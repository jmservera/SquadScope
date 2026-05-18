#!/usr/bin/env python3
"""Collect weekly GitHub repository signals for SquadScope."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable
from urllib import error, parse, request

API_ROOT = "https://api.github.com"
SEARCH_REPOSITORIES = f"{API_ROOT}/search/repositories"
README_KEYWORDS = {
    "homework",
    "assignment",
    "tutorial",
    "course",
    "bootcamp",
    "workshop",
    "exercise",
    "lab",
    "lesson",
    "leetcode",
    "kata",
    "template",
    "starter",
    "example",
    "cheatsheet",
    "guide",
    "demo",
    "sample",
}
EXCLUDED_TOPICS = {
    "tutorial",
    "tutorials",
    "homework",
    "assignment",
    "assignments",
    "course",
    "courses",
    "bootcamp",
    "workshop",
    "workshops",
    "example",
    "examples",
    "template",
    "templates",
    "starter",
    "starter-template",
}
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json, application/vnd.github.mercy-preview+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "SquadScope-Crawler/1.0",
}


class GitHubClient:
    def __init__(self, token: str, *, timeout: int = 30, max_retries: int = 6) -> None:
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_calls_used = 0
        self.rate_limit_remaining: int | None = None
        self.rate_limit_reset: int | None = None
        self._readme_cache: dict[str, bool] = {}

    def _headers(self) -> dict[str, str]:
        headers = dict(DEFAULT_HEADERS)
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        query = f"{url}?{parse.urlencode(params)}" if params else url
        attempt = 0
        while True:
            req = request.Request(query, headers=self._headers())
            try:
                with request.urlopen(req, timeout=self.timeout) as response:
                    self.api_calls_used += 1
                    self._update_rate_limit(response.headers)
                    payload = response.read().decode("utf-8")
                    return json.loads(payload)
            except error.HTTPError as exc:
                self.api_calls_used += 1
                self._update_rate_limit(exc.headers)
                body = exc.read().decode("utf-8", errors="replace")
                if attempt >= self.max_retries or not self._should_retry(exc.code, body):
                    raise RuntimeError(
                        f"GitHub API request failed with status {exc.code}: {body.strip() or exc.reason}"
                    ) from exc
                self._sleep_before_retry(attempt, exc.headers, body)
                attempt += 1
            except error.URLError as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"GitHub API request failed: {exc}") from exc
                self._sleep_before_retry(attempt, None, str(exc))
                attempt += 1

    def search_repositories(self, query: str, *, max_results: int = 1000) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        per_page = 100
        max_pages = min((max_results + per_page - 1) // per_page, 10)
        for page in range(1, max_pages + 1):
            payload = self.get_json(
                SEARCH_REPOSITORIES,
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": per_page,
                    "page": page,
                },
            )
            items = payload.get("items", [])
            if not items:
                break
            results.extend(items)
            if len(items) < per_page or len(results) >= min(payload.get("total_count", 0), max_results, 1000):
                break
        return results[:max_results]

    def has_readme(self, full_name: str) -> bool:
        if full_name in self._readme_cache:
            return self._readme_cache[full_name]
        url = f"{API_ROOT}/repos/{full_name}/readme"
        try:
            self.get_json(url)
            self._readme_cache[full_name] = True
        except RuntimeError as exc:
            message = str(exc)
            if "status 404" in message or "SAML enforcement" in message:
                self._readme_cache[full_name] = False
            else:
                raise
        return self._readme_cache[full_name]

    def _should_retry(self, status: int, body: str) -> bool:
        lowered = body.lower()
        return status in {403, 429, 500, 502, 503, 504} or "secondary rate limit" in lowered

    def _sleep_before_retry(self, attempt: int, headers: Any, body: str) -> None:
        reset_at = None
        if headers is not None:
            remaining = headers.get("X-RateLimit-Remaining")
            reset = headers.get("X-RateLimit-Reset")
            if remaining == "0" and reset:
                try:
                    reset_at = max(int(reset) - int(time.time()), 1)
                except ValueError:
                    reset_at = None
        if reset_at is not None:
            delay = reset_at + random.uniform(0.0, 1.0)
        else:
            delay = min(2**attempt, 60) + random.uniform(0.0, 1.0)
            if "secondary rate limit" in body.lower():
                delay = max(delay, 5.0 + random.uniform(0.0, 3.0))
        time.sleep(delay)

    def _update_rate_limit(self, headers: Any) -> None:
        remaining = headers.get("X-RateLimit-Remaining") if headers else None
        reset = headers.get("X-RateLimit-Reset") if headers else None
        if remaining is not None:
            try:
                self.rate_limit_remaining = int(remaining)
            except ValueError:
                self.rate_limit_remaining = None
        if reset is not None:
            try:
                self.rate_limit_reset = int(reset)
            except ValueError:
                self.rate_limit_reset = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--since",
        help="UTC date cutoff for repository queries (YYYY-MM-DD). Defaults to 7 days before --as-of/current time.",
    )
    parser.add_argument(
        "--as-of",
        help="Anchor date for the crawl window and output week (YYYY-MM-DD). Defaults to now in UTC.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=250,
        help="Maximum repositories to fetch per search query (default: 250, capped at 1000).",
    )
    parser.add_argument(
        "--output",
        help="Optional explicit output path. Defaults to data/raw/YYYY-WNN.json.",
    )
    return parser.parse_args()


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def iso_timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def week_slug(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def previous_snapshot(data_dir: Path, current_week: str) -> dict[str, int]:
    snapshots = sorted(data_dir.glob("*.json"), reverse=True)
    for snapshot in snapshots:
        try:
            payload = json.loads(snapshot.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("week") == current_week:
            continue
        mapping: dict[str, int] = {}
        for section in ("new_repos", "trending_repos"):
            for repo in payload.get(section, []):
                full_name = repo.get("full_name") or ""
                stars = repo.get("stars")
                if full_name and isinstance(stars, int):
                    mapping[full_name] = stars
        if mapping:
            return mapping
    return {}


def looks_insignificant(repo: dict[str, Any]) -> bool:
    if repo.get("fork"):
        return True
    description = (repo.get("description") or "").strip()
    if not description:
        return True
    lowered_description = description.lower()
    lowered_name = str(repo.get("name") or "").lower()
    topics = {topic.lower() for topic in repo.get("topics") or []}
    combined = " ".join([lowered_name, lowered_description, " ".join(sorted(topics))])
    if topics & EXCLUDED_TOPICS:
        return True
    return any(keyword in combined for keyword in README_KEYWORDS)


def to_repo_record(repo: dict[str, Any], *, stars_gained: int | None = None) -> dict[str, Any]:
    license_info = repo.get("license") or {}
    record = {
        "name": repo.get("name"),
        "owner": (repo.get("owner") or {}).get("login"),
        "full_name": repo.get("full_name"),
        "description": repo.get("description"),
        "language": repo.get("language"),
        "stars": repo.get("stargazers_count"),
        "forks": repo.get("forks_count"),
        "created_at": repo.get("created_at"),
        "topics": sorted(repo.get("topics") or []),
        "license": license_info.get("spdx_id") or license_info.get("name"),
        "url": repo.get("html_url"),
    }
    if stars_gained is not None:
        record["stars_gained"] = stars_gained
    return record


def collect_repositories(
    client: GitHubClient,
    repositories: Iterable[dict[str, Any]],
    *,
    previous_stars: dict[str, int] | None = None,
    trending_cutoff: datetime | None = None,
) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    seen: set[str] = set()
    has_prior_snapshot = bool(previous_stars)
    for repo in repositories:
        full_name = repo.get("full_name")
        if not full_name or full_name in seen or looks_insignificant(repo):
            continue
        if not client.has_readme(full_name):
            continue
        seen.add(full_name)
        stars_gained: int | None = None
        if previous_stars is not None:
            previous_value = previous_stars.get(full_name)
            current_stars = int(repo.get("stargazers_count") or 0)
            if previous_value is not None:
                stars_gained = max(current_stars - previous_value, 0)
            elif has_prior_snapshot and trending_cutoff is not None:
                created_at = repo.get("created_at")
                if isinstance(created_at, str):
                    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if created >= trending_cutoff:
                        stars_gained = current_stars
        collected.append(to_repo_record(repo, stars_gained=stars_gained))
    if previous_stars is not None and has_prior_snapshot:
        collected.sort(key=lambda item: (item.get("stars_gained", -1), item["stars"]), reverse=True)
    else:
        collected.sort(key=lambda item: item["stars"], reverse=True)
    return collected


def build_signals(*repo_groups: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    topic_counter: Counter[str] = Counter()
    for group in repo_groups:
        for repo in group:
            topic_counter.update(topic.lower() for topic in repo.get("topics") or [])
    top_topics = [
        {"topic": topic, "count": count}
        for topic, count in topic_counter.most_common(15)
    ]
    return {"top_topics": top_topics}


def validate_payload(payload: dict[str, Any]) -> None:
    required_top_level = {"week", "crawled_at", "new_repos", "trending_repos", "signals", "metadata"}
    missing = required_top_level - payload.keys()
    if missing:
        raise ValueError(f"Missing top-level keys: {sorted(missing)}")
    if not isinstance(payload["new_repos"], list) or not isinstance(payload["trending_repos"], list):
        raise ValueError("new_repos and trending_repos must be lists")
    if not isinstance(payload["signals"], dict) or not isinstance(payload["metadata"], dict):
        raise ValueError("signals and metadata must be objects")
    repo_fields = {
        "name",
        "owner",
        "full_name",
        "description",
        "language",
        "stars",
        "forks",
        "created_at",
        "topics",
        "license",
        "url",
    }
    for section in ("new_repos", "trending_repos"):
        for repo in payload[section]:
            missing_fields = repo_fields - repo.keys()
            if missing_fields:
                raise ValueError(f"Repository in {section} missing fields: {sorted(missing_fields)}")
    metadata = payload["metadata"]
    if not isinstance(metadata.get("api_calls_used"), int):
        raise ValueError("metadata.api_calls_used must be an integer")
    if metadata.get("rate_limit_remaining") is not None and not isinstance(metadata.get("rate_limit_remaining"), int):
        raise ValueError("metadata.rate_limit_remaining must be an integer or null")


def write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return 1

    crawled_at = utc_now()
    window_end = (
        datetime.strptime(args.as_of, "%Y-%m-%d").replace(tzinfo=UTC)
        if args.as_of
        else crawled_at
    )
    since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=UTC) if args.since else window_end - timedelta(days=7)
    week = week_slug(window_end)
    output_path = Path(args.output) if args.output else Path("data/raw") / f"{week}.json"
    client = GitHubClient(github_token)
    max_results = max(1, min(args.max_results, 1000))

    new_query = f"created:>{since.date().isoformat()} stars:>50"
    trending_query = f"pushed:>{since.date().isoformat()} stars:>50"

    new_candidates = client.search_repositories(new_query, max_results=max_results)
    previous_stars = previous_snapshot(output_path.parent, week)
    trending_candidates = client.search_repositories(trending_query, max_results=max_results)

    new_repos = collect_repositories(client, new_candidates)
    trending_repos = collect_repositories(
        client,
        trending_candidates,
        previous_stars=previous_stars,
        trending_cutoff=since,
    )

    payload = {
        "week": week,
        "crawled_at": iso_timestamp(crawled_at),
        "new_repos": new_repos,
        "trending_repos": trending_repos,
        "signals": build_signals(new_repos, trending_repos),
        "metadata": {
            "api_calls_used": client.api_calls_used,
            "rate_limit_remaining": client.rate_limit_remaining,
        },
    }
    validate_payload(payload)
    write_payload(output_path, payload)

    print(
        f"Wrote {output_path} with {len(new_repos)} new repos and {len(trending_repos)} trending repos "
        f"using {client.api_calls_used} API calls."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
