#!/usr/bin/env python3
"""Collect weekly GitHub repository signals for SquadScope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable
from urllib import error, parse, request

from scripts.topic_paths import cache_dir, raw_dir, snapshots_dir

API_ROOT = "https://api.github.com"
SEARCH_REPOSITORIES = f"{API_ROOT}/search/repositories"
CACHE_ROOT = Path("data/cache")
RAW_ROOT = Path("data/raw")
SNAPSHOT_ROOT = Path("data/snapshots")
RETRYABLE_STATUSES = {403, 429, 500, 502, 503, 504}
LOW_SIGNAL_TOPICS = {
    "assignment",
    "assignments",
    "bootcamp",
    "course",
    "courses",
    "example",
    "examples",
    "exercise",
    "homework",
    "learning",
    "starter-template",
    "template",
    "templates",
    "tutorial",
    "tutorials",
    "workshop",
    "workshops",
}
LOW_SIGNAL_TOKENS = {
    "assignment",
    "assignments",
    "bootcamp",
    "cheatsheet",
    "course",
    "courses",
    "example",
    "examples",
    "exercise",
    "exercises",
    "homework",
    "leetcode",
    "template",
    "tutorial",
    "tutorials",
    "walkthrough",
    "workshop",
}
LOW_SIGNAL_NAME_TOKENS = {
    "demo",
    "kata",
    "lab",
    "labs",
    "lesson",
    "lessons",
    "practice",
    "sample",
    "starter",
}
LOW_SIGNAL_PHRASES = {
    "course project",
    "for beginners",
    "getting started tutorial",
    "my solution",
    "starter template",
    "step by step",
    "step-by-step",
    "study notes",
}
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json, application/vnd.github.mercy-preview+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "SquadScope-Crawler/1.0",
}
GITHUB_SOURCE_ID = "github-search"


def log(message: str) -> None:
    print(f"[crawl {iso_timestamp(utc_now())}] {message}", file=sys.stderr)


@dataclass(slots=True)
class CacheEntry:
    status: int
    payload: Any
    headers: dict[str, str]
    fetched_at: datetime
    stale: bool = False


class ResponseCache:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def load(self, key: str, ttl_seconds: int) -> CacheEntry | None:
        path = self._path_for(key)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            fetched_at = datetime.fromisoformat(payload["fetched_at"].replace("Z", "+00:00"))
            headers = payload.get("headers") or {}
            age = (utc_now() - fetched_at).total_seconds()
            return CacheEntry(
                status=int(payload["status"]),
                payload=payload.get("payload"),
                headers={str(name): str(value) for name, value in headers.items()},
                fetched_at=fetched_at,
                stale=age > ttl_seconds,
            )
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

    def store(self, key: str, *, status: int, payload: Any, headers: dict[str, str]) -> None:
        path = self._path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        cache_payload = {
            "status": status,
            "fetched_at": iso_timestamp(utc_now()),
            "headers": headers,
            "payload": payload,
        }
        path.write_text(json.dumps(cache_payload, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    def _path_for(self, key: str) -> Path:
        parsed = parse.urlparse(key)
        label = parsed.path.strip("/").replace("/", "-") or "root"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.root / f"{label}-{digest}.json"


class GitHubClient:
    def __init__(self, token: str, *, cache_dir: Path = CACHE_ROOT, timeout: int = 30, max_retries: int = 6) -> None:
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_calls_used = 0
        self.cache_hits = 0
        self.stale_cache_hits = 0
        self.rate_limit_limit: int | None = None
        self.rate_limit_remaining: int | None = None
        self.rate_limit_reset: int | None = None
        self.rate_limit_resource: str | None = None
        self._last_request_at = 0.0
        self._readme_cache: dict[str, bool] = {}
        self._cache = ResponseCache(cache_dir)
        self.errors: list[str] = []

    def _headers(self) -> dict[str, str]:
        headers = dict(DEFAULT_HEADERS)
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        *,
        acceptable_statuses: set[int] | None = None,
        ttl_seconds: int | None = None,
        allow_stale: bool = True,
        max_retries: int | None = None,
        max_delay_seconds: float = 300.0,
    ) -> Any:
        return self.get_json_entry(
            url,
            params,
            acceptable_statuses=acceptable_statuses,
            ttl_seconds=ttl_seconds,
            allow_stale=allow_stale,
            max_retries=max_retries,
            max_delay_seconds=max_delay_seconds,
        ).payload

    def get_json_entry(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        *,
        acceptable_statuses: set[int] | None = None,
        ttl_seconds: int | None = None,
        allow_stale: bool = True,
        max_retries: int | None = None,
        max_delay_seconds: float = 300.0,
    ) -> CacheEntry:
        query = f"{url}?{parse.urlencode(params)}" if params else url
        accepted = acceptable_statuses or set()
        retry_limit = self.max_retries if max_retries is None else max_retries
        ttl = ttl_seconds if ttl_seconds is not None else self._cache_ttl(url)
        cached = self._cache.load(query, ttl)
        if cached and not cached.stale and (cached.status == 200 or cached.status in accepted):
            self.cache_hits += 1
            return cached

        stale_fallback = None
        if cached and allow_stale and (cached.status == 200 or cached.status in accepted):
            stale_fallback = CacheEntry(
                status=cached.status,
                payload=cached.payload,
                headers=cached.headers,
                fetched_at=cached.fetched_at,
                stale=True,
            )

        attempt = 0
        while True:
            self._pause_for_rate_limit(query)
            self._respect_min_interval(url)
            req = request.Request(query, headers=self._headers())
            try:
                with request.urlopen(req, timeout=self.timeout) as response:
                    self.api_calls_used += 1
                    headers = {name: value for name, value in response.headers.items()}
                    self._update_rate_limit(headers)
                    body = response.read().decode("utf-8", errors="replace")
                    self._last_request_at = time.monotonic()
                    try:
                        payload = json.loads(body)
                    except json.JSONDecodeError as exc:
                        if stale_fallback is not None:
                            self.stale_cache_hits += 1
                            log(f"Using stale cache for {query} after malformed JSON response: {exc}")
                            return stale_fallback
                        raise RuntimeError(f"GitHub API returned malformed JSON for {query}: {exc}") from exc
                    self._cache.store(query, status=response.status, payload=payload, headers=self._cache_headers(headers))
                    self._log_rate_limit(query)
                    return CacheEntry(response.status, payload, headers, utc_now())
            except error.HTTPError as exc:
                self.api_calls_used += 1
                headers = {name: value for name, value in (exc.headers.items() if exc.headers else [])}
                self._update_rate_limit(headers)
                body = exc.read().decode("utf-8", errors="replace")
                self._last_request_at = time.monotonic()
                payload = decode_json_body(body)
                if exc.code in accepted:
                    self._cache.store(query, status=exc.code, payload=payload, headers=self._cache_headers(headers))
                    self._log_rate_limit(query)
                    return CacheEntry(exc.code, payload, headers, utc_now())
                if attempt >= retry_limit or not self._should_retry(exc.code, body):
                    if stale_fallback is not None:
                        self.stale_cache_hits += 1
                        log(f"Using stale cache for {query} after HTTP {exc.code}.")
                        return stale_fallback
                    raise RuntimeError(
                        f"GitHub API request failed with status {exc.code}: {body.strip() or exc.reason}"
                    ) from exc
                self._sleep_before_retry(attempt, headers, body, query, retry_limit, max_delay_seconds)
                attempt += 1
            except (error.URLError, TimeoutError) as exc:
                if attempt >= retry_limit:
                    if stale_fallback is not None:
                        self.stale_cache_hits += 1
                        log(f"Using stale cache for {query} after network error: {exc}")
                        return stale_fallback
                    raise RuntimeError(f"GitHub API request failed: {exc}") from exc
                self._sleep_before_retry(attempt, None, str(exc), query, retry_limit, max_delay_seconds)
                attempt += 1

    def search_repositories(self, query: str, *, max_results: int = 1000) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        per_page = 100
        max_pages = min((max_results + per_page - 1) // per_page, 10)
        for page in range(1, max_pages + 1):
            try:
                response = self.get_json_entry(
                    SEARCH_REPOSITORIES,
                    params={
                        "q": query,
                        "sort": "stars",
                        "order": "desc",
                        "per_page": per_page,
                        "page": page,
                    },
                    ttl_seconds=6 * 60 * 60,
                )
            except RuntimeError as exc:
                self.record_error(f"Search failed for '{query}' page {page}: {exc}")
                break
            payload = response.payload if isinstance(response.payload, dict) else {}
            items = payload.get("items")
            if not isinstance(items, list):
                self.record_error(f"Malformed search payload for '{query}' page {page}: missing items list")
                break
            if payload.get("incomplete_results"):
                self.record_error(f"GitHub marked search results incomplete for '{query}' page {page}")
            results.extend(item for item in items if isinstance(item, dict))
            total_count = payload.get("total_count")
            if len(items) < per_page or len(results) >= min(int(total_count or 0), max_results, 1000):
                break
        return results[:max_results]

    def has_readme(self, full_name: str) -> bool:
        if full_name in self._readme_cache:
            return self._readme_cache[full_name]
        url = f"{API_ROOT}/repos/{full_name}/readme"
        try:
            response = self.get_json_entry(
                url,
                acceptable_statuses={404},
                ttl_seconds=24 * 60 * 60,
                max_retries=2,
                max_delay_seconds=60.0,
            )
        except RuntimeError as exc:
            message = str(exc)
            if "SAML enforcement" in message:
                self._readme_cache[full_name] = False
                return False
            raise
        has_readme = response.status != 404
        self._readme_cache[full_name] = has_readme
        return has_readme

    def record_error(self, message: str) -> None:
        self.errors.append(message)
        log(message)

    def _cache_ttl(self, url: str) -> int:
        if "/search/" in url:
            return 6 * 60 * 60
        if url.endswith("/readme"):
            return 24 * 60 * 60
        return 12 * 60 * 60

    def _should_retry(self, status: int, body: str) -> bool:
        lowered = body.lower()
        return status in RETRYABLE_STATUSES or "secondary rate limit" in lowered

    def _sleep_before_retry(
        self,
        attempt: int,
        headers: dict[str, str] | None,
        body: str,
        query: str,
        retry_limit: int,
        max_delay_seconds: float,
    ) -> None:
        reset_delay = self._reset_delay(headers)
        retry_after = None
        if headers and headers.get("Retry-After"):
            try:
                retry_after = max(float(headers["Retry-After"]), 1.0)
            except ValueError:
                retry_after = None
        if retry_after is not None and (self.rate_limit_reset is None or (self.rate_limit_remaining or 0) <= 0):
            self.rate_limit_reset = max(self.rate_limit_reset or 0, int(time.time() + retry_after))
        base_delay = min(2**attempt, 60)
        jitter = random.uniform(0.3, 1.7)
        delay = retry_after or reset_delay or (base_delay + jitter)
        if "secondary rate limit" in body.lower():
            delay = max(delay, 8.0 + random.uniform(0.0, 5.0))
        delay = min(delay, max_delay_seconds)
        log(f"Retrying {query} in {delay:.1f}s (attempt {attempt + 1}/{retry_limit}).")
        time.sleep(delay)

    def _respect_min_interval(self, url: str) -> None:
        minimum_interval = 0.35 if url.endswith("/readme") else 0.0
        if minimum_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < minimum_interval:
            time.sleep(minimum_interval - elapsed)

    def _pause_for_rate_limit(self, query: str) -> None:
        if self.rate_limit_remaining is None or self.rate_limit_limit is None:
            return
        low_threshold = max(5, min(25, int(self.rate_limit_limit * 0.1)))
        critical_threshold = max(3, min(10, int(self.rate_limit_limit * 0.03)))
        if self.rate_limit_remaining > low_threshold:
            return
        reset_headers = {"X-RateLimit-Reset": str(self.rate_limit_reset)} if self.rate_limit_reset is not None else None
        reset_delay = self._reset_delay(reset_headers)
        if reset_delay is None:
            if self.rate_limit_remaining <= critical_threshold:
                delay = 10.0 if self.rate_limit_remaining <= 0 else 3.0
                log(
                    f"Rate limit low ({self.rate_limit_remaining}/{self.rate_limit_limit} {self.rate_limit_resource or 'requests'}) "
                    f"without reset hint; cooling down {delay:.1f}s before {query}."
                )
                time.sleep(delay)
            return
        if self.rate_limit_remaining <= critical_threshold:
            delay = min(reset_delay + random.uniform(0.3, 1.5), 300.0)
            log(f"Rate limit nearly exhausted before {query}; pausing {delay:.1f}s until reset window.")
            time.sleep(delay)
            return
        delay = min(max(reset_delay / 10, 1.0), 30.0)
        log(
            f"Rate limit low ({self.rate_limit_remaining}/{self.rate_limit_limit} {self.rate_limit_resource or 'requests'}); "
            f"cooling down {delay:.1f}s before {query}."
        )
        time.sleep(delay)

    def _reset_delay(self, headers: dict[str, str] | None) -> float | None:
        if not headers:
            return None
        reset = headers.get("X-RateLimit-Reset")
        if not reset:
            return None
        try:
            return max(int(reset) - int(time.time()), 1)
        except ValueError:
            return None

    def _update_rate_limit(self, headers: dict[str, str] | None) -> None:
        limit = headers.get("X-RateLimit-Limit") if headers else None
        remaining = headers.get("X-RateLimit-Remaining") if headers else None
        reset = headers.get("X-RateLimit-Reset") if headers else None
        resource = headers.get("X-RateLimit-Resource") if headers else None
        if limit is not None:
            try:
                self.rate_limit_limit = int(limit)
            except ValueError:
                self.rate_limit_limit = None
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
        if resource is not None:
            self.rate_limit_resource = resource

    def _log_rate_limit(self, query: str) -> None:
        if self.rate_limit_remaining is None:
            return
        reset_text = rate_limit_reset_text(self.rate_limit_reset)
        limit_text = self.rate_limit_limit if self.rate_limit_limit is not None else "?"
        resource_text = self.rate_limit_resource or "unknown"
        log(
            f"Rate limit after {query}: remaining={self.rate_limit_remaining}/{limit_text} "
            f"({resource_text}), resets={reset_text}."
        )

    def _cache_headers(self, headers: dict[str, str]) -> dict[str, str]:
        names = {"Date", "Retry-After", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"}
        return {name: value for name, value in headers.items() if name in names}


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
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic ID for namespaced data directories. Defaults to 'general' (flat layout).",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a topic YAML config file (e.g. squadscope.topic.yml). "
        "When provided, queries are read from the config instead of using hardcoded defaults.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Refresh GitHub data even when a same-day raw artifact is reusable.",
    )
    parser.add_argument(
        "--reuse-artifact",
        default=None,
        help="Existing raw GitHub artifact to reuse when it is fresh for this run window.",
    )
    parser.add_argument(
        "--source-refresh-policy",
        choices=["reuse-same-day", "refresh-missing-stale", "force-refresh"],
        default="reuse-same-day",
        help="Source refresh policy for reruns (default: reuse eligible same-day artifacts).",
    )
    parser.add_argument(
        "--run-started-at",
        default=None,
        help="UTC run start timestamp used for same-day reuse checks (ISO 8601). Defaults to now.",
    )
    parser.add_argument(
        "--current-code-sha",
        default=None,
        help="Optional crawler/config fingerprint; reused artifacts with a conflicting fingerprint are stale.",
    )
    return parser.parse_args()


def load_topic_queries(config_path: str, template_vars: dict[str, str]) -> dict[str, Any]:
    """Load and resolve queries from a topic YAML config file.

    Returns a dict with keys: primary (list[str]), secondary (list[str]), min_repos_per_week (int).
    Template variables in queries (e.g. {last_week}, {today}) are replaced with values from template_vars.
    """
    import yaml

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Topic config not found: {config_path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    queries_section = data.get("queries", {})
    primary = queries_section.get("primary", [])
    secondary = queries_section.get("secondary", [])
    quality_section = data.get("quality", {})
    min_repos = quality_section.get("min_repos_per_week", 5)

    def resolve(q: str) -> str:
        for key, value in template_vars.items():
            q = q.replace(f"{{{key}}}", value)
        return q

    return {
        "primary": [resolve(q) for q in primary],
        "secondary": [resolve(q) for q in secondary],
        "min_repos_per_week": min_repos,
    }


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def iso_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def week_slug(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def rate_limit_reset_text(reset_timestamp: int | None) -> str | None:
    if reset_timestamp is None:
        return None
    return iso_timestamp(datetime.fromtimestamp(reset_timestamp, tz=UTC))


def decode_json_body(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"message": body.strip()}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def github_schema_checksum() -> str:
    contract = {
        "schema": "github_raw_v1",
        "top_level": ["week", "crawled_at", "new_repos", "trending_repos", "signals", "metadata"],
        "metadata": ["crawl_window", "crawl_config_checksum", "schema_checksum", "artifact_checksum", "same_day_reuse"],
    }
    return sha256_text(json.dumps(contract, sort_keys=True, separators=(",", ":")))


def github_crawl_config_checksum(args: argparse.Namespace, since: datetime, window_end: datetime, max_results: int) -> str:
    config_digest = sha256_file(Path(args.config)) if args.config else None
    payload = {
        "since": since.date().isoformat(),
        "until": window_end.date().isoformat(),
        "as_of": args.as_of,
        "max_results": max_results,
        "topic": args.topic,
        "config": args.config,
        "config_sha256": config_digest,
    }
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def github_artifact_checksum(payload: dict[str, Any]) -> str:
    candidate = dict(payload)
    candidate.pop("crawled_at", None)
    metadata = dict(candidate.get("metadata", {}))
    metadata.pop("artifact_checksum", None)
    metadata.pop("same_day_reuse", None)
    candidate["metadata"] = metadata
    return sha256_text(json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def load_json_artifact(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_reusable_github_payload(
    path: Path,
    *,
    week: str,
    crawled_at: datetime,
    since: datetime,
    window_end: datetime,
    config_checksum: str,
    policy: str = "reuse-same-day",
    current_code_sha: str | None = None,
) -> dict[str, Any] | None:
    if policy == "force-refresh":
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    try:
        validate_payload(payload)
    except ValueError:
        return None
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    parsed = None
    raw_crawled_at = payload.get("crawled_at")
    if isinstance(raw_crawled_at, str):
        try:
            parsed = datetime.fromisoformat(raw_crawled_at.replace("Z", "+00:00"))
        except ValueError:
            parsed = None
    window = metadata.get("crawl_window")
    if (
        payload.get("week") != week
        or parsed is None
        or parsed.astimezone(UTC).date() != crawled_at.astimezone(UTC).date()
        or not isinstance(window, dict)
        or window.get("since") != since.date().isoformat()
        or window.get("until") != window_end.date().isoformat()
        or metadata.get("crawl_config_checksum") != config_checksum
        or metadata.get("schema_checksum") != github_schema_checksum()
        or metadata.get("artifact_checksum") != github_artifact_checksum(payload)
    ):
        return None
    artifact_code_sha = metadata.get("crawler_code_sha")
    if current_code_sha and artifact_code_sha != current_code_sha:
        return None
    original_checksum = metadata.get("artifact_checksum")
    metadata["same_day_reuse"] = {
        "status": "reused",
        "source": "github",
        "source_id": GITHUB_SOURCE_ID,
        "original_run_id": metadata.get("run_id", ""),
        "original_crawled_at": payload.get("crawled_at"),
        "reused_at": iso_timestamp(crawled_at),
        "week": week,
        "crawl_window": window,
        "crawl_config_checksum": config_checksum,
        "schema_checksum": github_schema_checksum(),
        "content_checksum": original_checksum,
    }
    metadata["source_refresh_policy"] = policy
    if current_code_sha:
        metadata.setdefault("crawler_code_sha", current_code_sha)
    payload["metadata"] = metadata
    metadata["artifact_checksum"] = github_artifact_checksum(payload)
    return payload


def _safe_snapshot_destination(snapshot_path: str, expected_snapshot_dir: Path = SNAPSHOT_ROOT) -> Path | None:
    destination = Path(snapshot_path)
    expected_root = Path("data") / "snapshots"
    if destination.is_absolute() or ".." in destination.parts:
        return None
    if len(destination.parts) < 3 or destination.parts[:2] != expected_root.parts:
        return None
    expected_dir = expected_snapshot_dir.resolve()
    resolved_destination = destination.resolve()
    if expected_dir != resolved_destination.parent and expected_dir not in resolved_destination.parents:
        return None
    return destination


def restore_reused_snapshot(
    reuse_path: Path,
    metadata: dict[str, Any],
    *,
    expected_snapshot_dir: Path = SNAPSHOT_ROOT,
) -> None:
    snapshot_path = metadata.get("snapshot_path")
    if not isinstance(snapshot_path, str) or not snapshot_path:
        return
    destination = _safe_snapshot_destination(snapshot_path, expected_snapshot_dir)
    if destination is None:
        return
    source_snapshot = reuse_path.parent.parent / "snapshots" / Path(snapshot_path).name
    if not source_snapshot.exists():
        return
    snapshot_payload = load_json_artifact(source_snapshot)
    if snapshot_payload is not None:
        write_payload(destination, snapshot_payload)


def load_previous_star_snapshot(snapshot_dir: Path, current_week: str, *raw_dirs: Path) -> dict[str, int]:
    for snapshot in sorted(snapshot_dir.glob("*-stars.json"), reverse=True):
        stars, reason = load_star_mapping_details(snapshot, current_week)
        if stars:
            return stars
        if reason and reason != "same-week snapshot":
            log(f"Skipping star snapshot {snapshot}: {reason}.")
    seen_dirs: set[Path] = set()
    for raw_dir in raw_dirs:
        if raw_dir in seen_dirs:
            continue
        seen_dirs.add(raw_dir)
        for snapshot in sorted(raw_dir.glob("*.json"), reverse=True):
            stars, reason = load_star_mapping_details(snapshot, current_week)
            if stars:
                return stars
            if reason and reason != "same-week snapshot":
                log(f"Skipping star snapshot {snapshot}: {reason}.")
    return {}


def load_star_mapping(path: Path, current_week: str) -> dict[str, int]:
    return load_star_mapping_details(path, current_week)[0]


def load_star_mapping_details(path: Path, current_week: str) -> tuple[dict[str, int], str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return {}, f"read failed ({exc})"
    except json.JSONDecodeError as exc:
        return {}, f"invalid JSON ({exc})"
    if payload.get("week") == current_week:
        return {}, "same-week snapshot"
    stars = payload.get("stars")
    if isinstance(stars, dict):
        mapping = {name: int(value) for name, value in stars.items() if isinstance(value, int)}
        if mapping:
            return mapping, None
        return {}, "empty stars mapping"
    mapping: dict[str, int] = {}
    for section in ("new_repos", "trending_repos"):
        for repo in payload.get(section, []):
            full_name = repo.get("full_name") or ""
            stars_value = repo.get("stars")
            if full_name and isinstance(stars_value, int):
                mapping[full_name] = stars_value
    if mapping:
        return mapping, None
    return {}, "no star data"


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def significance_skip_reason(repo: dict[str, Any]) -> str | None:
    if repo.get("fork"):
        return "fork"
    if repo.get("is_template"):
        return "template_repo"
    description = (repo.get("description") or "").strip()
    if not description:
        return "missing_description"
    topics = {str(topic).lower() for topic in repo.get("topics") or []}
    if topics & LOW_SIGNAL_TOPICS:
        return "low_signal_topic"
    name = str(repo.get("name") or "")
    combined_text = " ".join([name, description]).lower()
    combined_tokens = tokenize(combined_text)
    if combined_tokens & LOW_SIGNAL_TOKENS:
        return "low_signal_keyword"
    if tokenize(name) & LOW_SIGNAL_NAME_TOKENS:
        return "low_signal_keyword"
    if any(phrase in combined_text for phrase in LOW_SIGNAL_PHRASES):
        return "low_signal_phrase"
    return None


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
        "topics": sorted(str(topic).lower() for topic in (repo.get("topics") or [])),
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
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    collected: list[dict[str, Any]] = []
    seen: set[str] = set()
    filter_stats: Counter[str] = Counter()
    has_prior_snapshot = bool(previous_stars)
    for repo in repositories:
        full_name = repo.get("full_name")
        if not full_name:
            filter_stats["missing_full_name"] += 1
            continue
        if full_name in seen:
            filter_stats["duplicate"] += 1
            continue
        seen.add(full_name)
        skip_reason = significance_skip_reason(repo)
        if skip_reason:
            filter_stats[skip_reason] += 1
            continue
        try:
            if not client.has_readme(full_name):
                filter_stats["missing_readme"] += 1
                continue
        except RuntimeError as exc:
            filter_stats["readme_lookup_failed"] += 1
            client.record_error(f"README lookup failed for {full_name}: {exc}")
            continue
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
    return collected, dict(filter_stats)


def build_signals(*repo_groups: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    topic_counter: Counter[str] = Counter()
    # A repo can appear in both search buckets; count its topics once to avoid inflating weekly signals.
    merged: dict[str, dict[str, Any]] = {}
    for group in repo_groups:
        for repo in group:
            full_name = repo.get("full_name")
            if full_name:
                merged[full_name] = repo
    for repo in merged.values():
        topic_counter.update(topic.lower() for topic in repo.get("topics") or [])
    top_topics = [{"topic": topic, "count": count} for topic, count in topic_counter.most_common(15)]
    return {"top_topics": top_topics}


def build_star_snapshot(*repo_groups: Iterable[dict[str, Any]]) -> dict[str, int]:
    stars: dict[str, int] = {}
    for group in repo_groups:
        for repo in group:
            full_name = repo.get("full_name")
            value = repo.get("stargazers_count")
            if full_name and isinstance(value, int):
                stars[full_name] = value
    return dict(sorted(stars.items()))


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
    if not isinstance(metadata.get("cache_hits"), int):
        raise ValueError("metadata.cache_hits must be an integer")
    if not isinstance(metadata.get("stale_cache_hits"), int):
        raise ValueError("metadata.stale_cache_hits must be an integer")
    if metadata.get("rate_limit_remaining") is not None and not isinstance(metadata.get("rate_limit_remaining"), int):
        raise ValueError("metadata.rate_limit_remaining must be an integer or null")
    if metadata.get("rate_limit_limit") is not None and not isinstance(metadata.get("rate_limit_limit"), int):
        raise ValueError("metadata.rate_limit_limit must be an integer or null")
    if metadata.get("rate_limit_reset") is not None and not isinstance(metadata.get("rate_limit_reset"), int):
        raise ValueError("metadata.rate_limit_reset must be an integer or null")
    if metadata.get("rate_limit_resource") is not None and not isinstance(metadata.get("rate_limit_resource"), str):
        raise ValueError("metadata.rate_limit_resource must be a string or null")
    if not isinstance(metadata.get("snapshot_path"), str):
        raise ValueError("metadata.snapshot_path must be a string")
    partial_failures = metadata.get("partial_failures")
    if partial_failures is not None and not isinstance(partial_failures, list):
        raise ValueError("metadata.partial_failures must be a list when present")


def write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()

    topic_id = args.topic
    topic_raw = raw_dir(topic_id)
    topic_snapshots = snapshots_dir(topic_id)
    topic_cache = cache_dir(topic_id)

    crawled_at = utc_now()
    run_started_at_arg = getattr(args, "run_started_at", None)
    run_started_at = parse_datetime(run_started_at_arg) if run_started_at_arg else crawled_at
    if run_started_at is None:
        print("--run-started-at must be an ISO 8601 timestamp", file=sys.stderr)
        return 1
    window_end = datetime.strptime(args.as_of, "%Y-%m-%d").replace(tzinfo=UTC) if args.as_of else crawled_at
    since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=UTC) if args.since else window_end - timedelta(days=7)
    week = week_slug(window_end)
    output_path = Path(args.output) if args.output else topic_raw / f"{week}.json"
    snapshot_path = topic_snapshots / f"{week}-stars.json"
    max_results = max(1, min(args.max_results, 1000))
    config_checksum = github_crawl_config_checksum(args, since, window_end, max_results)
    source_refresh_policy = (
        "force-refresh"
        if getattr(args, "force_refresh", False)
        else getattr(args, "source_refresh_policy", "reuse-same-day")
    )
    current_code_sha = getattr(args, "current_code_sha", None) or os.environ.get("CRAWLER_CODE_SHA")

    if source_refresh_policy != "force-refresh":
        reuse_path = Path(getattr(args, "reuse_artifact", "")) if getattr(args, "reuse_artifact", None) else output_path
        reusable = load_reusable_github_payload(
            reuse_path,
            week=week,
            crawled_at=run_started_at,
            since=since,
            window_end=window_end,
            config_checksum=config_checksum,
            policy=source_refresh_policy,
            current_code_sha=current_code_sha,
        )
        if reusable is not None:
            write_payload(output_path, reusable)
            restore_reused_snapshot(reuse_path, reusable.get("metadata", {}), expected_snapshot_dir=topic_snapshots)
            print(f"Reused same-day GitHub raw artifact {reuse_path} -> {output_path}; used 0 API calls.")
            return 0

    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return 1
    client = GitHubClient(github_token, cache_dir=topic_cache)

    if args.config:
        template_vars = {
            "last_week": since.date().isoformat(),
            "today": window_end.date().isoformat(),
        }
        topic_queries = load_topic_queries(args.config, template_vars)
        all_candidates: list[Any] = []
        for q in topic_queries["primary"]:
            all_candidates.extend(client.search_repositories(q, max_results=max_results))
        if len(all_candidates) < topic_queries["min_repos_per_week"]:
            for q in topic_queries["secondary"]:
                all_candidates.extend(client.search_repositories(q, max_results=max_results))
        new_candidates = all_candidates
        previous_stars = load_previous_star_snapshot(SNAPSHOT_ROOT, week, output_path.parent, RAW_ROOT)
        trending_candidates: list[Any] = []
    else:
        if args.as_of:
            created_filter = f"created:{since.date().isoformat()}..{window_end.date().isoformat()}"
            pushed_filter = f"pushed:{since.date().isoformat()}..{window_end.date().isoformat()}"
        else:
            created_filter = f"created:>{since.date().isoformat()}"
            pushed_filter = f"pushed:>{since.date().isoformat()}"
        new_query = f"{created_filter} stars:>50"
        trending_query = f"{pushed_filter} stars:>50"

        new_candidates = client.search_repositories(new_query, max_results=max_results)
        previous_stars = load_previous_star_snapshot(SNAPSHOT_ROOT, week, output_path.parent, RAW_ROOT)
        trending_candidates = client.search_repositories(trending_query, max_results=max_results)

    new_repos, new_filters = collect_repositories(client, new_candidates)
    trending_repos, trending_filters = collect_repositories(
        client,
        trending_candidates,
        previous_stars=previous_stars,
        trending_cutoff=since,
    )

    # Keep star snapshots broader than the filtered payload so future reruns can still compute deltas
    # even when a repo is later excluded as low-signal or missing a README.
    star_snapshot = build_star_snapshot(new_candidates, trending_candidates)
    snapshot_payload = {
        "week": week,
        "captured_at": iso_timestamp(crawled_at),
        "repository_count": len(star_snapshot),
        "stars": star_snapshot,
    }

    payload = {
        "week": week,
        "crawled_at": iso_timestamp(crawled_at),
        "new_repos": new_repos,
        "trending_repos": trending_repos,
        "signals": build_signals(new_repos, trending_repos),
        "metadata": {
            "api_calls_used": client.api_calls_used,
            "cache_hits": client.cache_hits,
            "stale_cache_hits": client.stale_cache_hits,
            "rate_limit_limit": client.rate_limit_limit,
            "rate_limit_remaining": client.rate_limit_remaining,
            "rate_limit_reset": client.rate_limit_reset,
            "rate_limit_resource": client.rate_limit_resource,
            "partial_failures": client.errors,
            "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
            "crawl_window": {
                "since": since.date().isoformat(),
                "until": window_end.date().isoformat(),
            },
            "crawl_config_checksum": config_checksum,
            "schema_checksum": github_schema_checksum(),
            "same_day_reuse": {"status": "not_reused", "source": "github", "source_id": GITHUB_SOURCE_ID},
            "filter_summary": {
                "new_repos": new_filters,
                "trending_repos": trending_filters,
            },
            "snapshot_path": snapshot_path.as_posix(),
            "source_refresh_policy": source_refresh_policy,
            "crawler_code_sha": current_code_sha or "",
        },
    }
    payload["metadata"]["artifact_checksum"] = github_artifact_checksum(payload)
    validate_payload(payload)
    write_payload(output_path, payload)
    write_payload(snapshot_path, snapshot_payload)

    if client.errors:
        log(f"Completed with {len(client.errors)} partial failure(s).")

    print(
        f"Wrote {output_path} with {len(new_repos)} new repos and {len(trending_repos)} trending repos, "
        f"saved {snapshot_path}, used {client.api_calls_used} API calls, and served {client.cache_hits} cache hits."
    )
    return 1 if client.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
