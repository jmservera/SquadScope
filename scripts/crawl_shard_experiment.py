#!/usr/bin/env python3
"""Run a local no-publish GitHub crawl sharding experiment for issue #435."""

from __future__ import annotations

import argparse
import json
import math
import os
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from queue import Empty, Queue
from typing import Any

from scripts.crawl import (
    GitHubClient,
    RAW_ROOT,
    build_signals,
    build_star_snapshot,
    collect_repositories,
    github_artifact_checksum,
    github_crawl_config_checksum,
    github_schema_checksum,
    iso_timestamp,
    load_previous_star_snapshot,
    load_topic_queries,
    log,
    significance_skip_reason,
    to_repo_record,
    utc_now,
    validate_payload,
    week_slug,
    write_payload,
)
from scripts.topic_paths import cache_dir, raw_dir, snapshots_dir

EXPERIMENT_ROOT = Path("data/experiments/shard-435")
DEFAULT_WALL_CLOCK_BUDGET = 120
DEFAULT_API_BUDGET_MULTIPLIER = 1.1


class ExperimentAbort(RuntimeError):
    """Abort the shard experiment immediately."""


class ShardBudgetExceeded(RuntimeError):
    """Stop a shard gracefully once its wall-clock budget is exhausted."""


@dataclass(slots=True)
class GuardrailEvent:
    kind: str
    shard: str
    message: str
    at: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = {"kind": self.kind, "shard": self.shard, "message": self.message, "at": self.at}
        if self.details:
            payload["details"] = self.details
        return payload


@dataclass(slots=True)
class SearchPlan:
    shard_name: str
    repo_group: str
    primary_queries: list[str]
    secondary_queries: list[str] = field(default_factory=list)
    min_repos_per_week: int = 0


@dataclass(slots=True)
class ValidationItem:
    repo_group: str
    sequence: int
    repo: dict[str, Any]


@dataclass(slots=True)
class ValidatedRecord:
    repo_group: str
    sequence: int
    record: dict[str, Any]


@dataclass(slots=True)
class CrawlContext:
    args: argparse.Namespace
    topic_id: str | None
    topic_raw: Path
    topic_snapshots: Path
    topic_cache: Path
    crawled_at: datetime
    run_started_at: datetime
    since: datetime
    window_end: datetime
    week: str
    max_results: int
    config_checksum: str
    current_code_sha: str
    source_refresh_policy: str
    baseline_output_path: Path
    baseline_snapshot_path: Path
    shard_output_path: Path
    shard_snapshot_path: Path


@dataclass(slots=True)
class RunResult:
    name: str
    payload: dict[str, Any]
    snapshot_payload: dict[str, Any]
    api_calls: int
    cache_hits: int
    stale_cache_hits: int
    rate_limit_events: int
    secondary_rate_limit_events: int
    partial_failures: list[str]
    wall_clock_s: float
    shards_used: int
    completed: bool
    guardrail_events: list[dict[str, Any]]


@dataclass(slots=True)
class ShardResult:
    shard_id: str
    repos_found: list[dict[str, Any]]
    api_calls: int
    errors: list[str]
    wall_clock_s: float
    rate_limit_detected: bool = False
    rate_limit_events: int = 0


@dataclass(slots=True)
class ExperimentReport:
    speedup_pct: float | None
    api_growth_pct: float | None
    rate_limit_regression: bool
    output_stable: bool
    partial_data: bool
    baseline_complete: bool
    shard_complete: bool
    verdict: str

    @classmethod
    def from_comparison(cls, comparison: dict[str, Any]) -> "ExperimentReport":
        speedup_pct = comparison.get("speedup_pct")
        api_growth_pct = comparison.get("api_growth_pct")
        rate_limit_regression = bool(
            comparison.get("rate_limit_regression", comparison.get("secondary_rate_limit_regression", False))
        )
        output_stable = bool(comparison.get("output_stable", False))
        partial_data = bool(comparison.get("partial_data", False))
        baseline_complete = bool(comparison.get("baseline_complete", True))
        shard_complete = bool(comparison.get("shard_complete", True))
        if partial_data or not baseline_complete or not shard_complete:
            verdict = "inconclusive"
        elif (
            speedup_pct is not None
            and api_growth_pct is not None
            and output_stable
            and not rate_limit_regression
            and float(speedup_pct) >= 25.0
            and float(api_growth_pct) <= 10.0
        ):
            verdict = "pass"
        else:
            verdict = "fail"
        return cls(
            speedup_pct=speedup_pct,
            api_growth_pct=api_growth_pct,
            rate_limit_regression=rate_limit_regression,
            output_stable=output_stable,
            partial_data=partial_data,
            baseline_complete=baseline_complete,
            shard_complete=shard_complete,
            verdict=verdict,
        )


class SharedQuotaTracker:
    def __init__(self, cap: int) -> None:
        self.cap = max(0, int(cap))
        self.count = 0
        self._lock = threading.Lock()

    def increment(self) -> bool:
        with self._lock:
            if self.count >= self.cap:
                return False
            self.count += 1
            return True

    def reset(self) -> None:
        with self._lock:
            self.count = 0


class WallClockBudget:
    def __init__(self, budget_s: float) -> None:
        self.budget_s = float(budget_s)
        self.started_at = time.monotonic()

    def elapsed_s(self) -> float:
        return time.monotonic() - self.started_at

    def is_exceeded(self) -> bool:
        return self.elapsed_s() > self.budget_s


class SharedQuotaCoordinator:
    def __init__(self, api_hard_cap: int | None) -> None:
        self.api_hard_cap = api_hard_cap
        self.total_api_calls = 0
        self.global_backoff_until = 0.0
        self.secondary_rate_limit_hit = False
        self.abort_reason: str | None = None
        self._guardrail_events: list[GuardrailEvent] = []
        self._lock = threading.Lock()

    def before_request(self, shard_name: str, query: str, deadline: float | None) -> None:
        self._raise_if_aborted()
        self._raise_if_budget_exceeded(shard_name, deadline)
        while True:
            with self._lock:
                resume_at = self.global_backoff_until
            now = time.monotonic()
            if resume_at <= now:
                break
            time.sleep(min(resume_at - now, 1.0))
            self._raise_if_aborted()
            self._raise_if_budget_exceeded(shard_name, deadline)
        with self._lock:
            if self.api_hard_cap is not None and self.total_api_calls >= self.api_hard_cap:
                if self.abort_reason is None:
                    self.abort_reason = (
                        f"API budget cap reached before {shard_name} requested {query} "
                        f"({self.total_api_calls}/{self.api_hard_cap})."
                    )
                    self._guardrail_events.append(
                        GuardrailEvent(
                            kind="api_budget_cap",
                            shard=shard_name,
                            message=self.abort_reason,
                            at=iso_timestamp(utc_now()),
                            details={"api_calls_used": self.total_api_calls, "api_hard_cap": self.api_hard_cap},
                        )
                    )
                raise ExperimentAbort(self.abort_reason)

    def register_api_calls(self, delta: int, shard_name: str) -> None:
        if delta <= 0:
            return
        with self._lock:
            self.total_api_calls += delta
            if self.api_hard_cap is not None and self.total_api_calls > self.api_hard_cap and self.abort_reason is None:
                self.abort_reason = (
                    f"API budget cap exceeded by {shard_name} "
                    f"({self.total_api_calls}/{self.api_hard_cap})."
                )
                self._guardrail_events.append(
                    GuardrailEvent(
                        kind="api_budget_cap",
                        shard=shard_name,
                        message=self.abort_reason,
                        at=iso_timestamp(utc_now()),
                        details={"api_calls_used": self.total_api_calls, "api_hard_cap": self.api_hard_cap},
                    )
                )

    def register_backoff(self, shard_name: str, delay: float, reason: str, *, secondary: bool = False) -> None:
        delay = max(delay, 1.0)
        with self._lock:
            self.global_backoff_until = max(self.global_backoff_until, time.monotonic() + delay)
            self._guardrail_events.append(
                GuardrailEvent(
                    kind="secondary_rate_limit" if secondary else "rate_limit_backoff",
                    shard=shard_name,
                    message=reason,
                    at=iso_timestamp(utc_now()),
                    details={"delay_seconds": round(delay, 2)},
                )
            )
            if secondary:
                self.secondary_rate_limit_hit = True
                self.abort_reason = reason

    def record_budget_exceeded(self, shard_name: str, budget_seconds: int) -> None:
        with self._lock:
            self._guardrail_events.append(
                GuardrailEvent(
                    kind="wall_clock_budget",
                    shard=shard_name,
                    message=f"{shard_name} exhausted its {budget_seconds}s wall-clock budget.",
                    at=iso_timestamp(utc_now()),
                    details={"budget_seconds": budget_seconds},
                )
            )

    def record_redistribution(self, shard_name: str, repo_count: int) -> None:
        if repo_count <= 0:
            return
        with self._lock:
            self._guardrail_events.append(
                GuardrailEvent(
                    kind="work_redistributed",
                    shard=shard_name,
                    message=f"Redistributed {repo_count} remaining repositories from {shard_name}.",
                    at=iso_timestamp(utc_now()),
                    details={"repo_count": repo_count},
                )
            )

    def guardrail_events(self) -> list[dict[str, Any]]:
        with self._lock:
            return [event.to_dict() for event in self._guardrail_events]

    def _raise_if_aborted(self) -> None:
        with self._lock:
            if self.abort_reason is not None:
                raise ExperimentAbort(self.abort_reason)

    def _raise_if_budget_exceeded(self, shard_name: str, deadline: float | None) -> None:
        if deadline is not None and time.monotonic() >= deadline:
            raise ShardBudgetExceeded(f"{shard_name} exceeded its wall-clock budget.")


class InstrumentedGitHubClient(GitHubClient):
    def __init__(
        self,
        token: str,
        *,
        cache_dir: Path,
        shard_name: str,
        coordinator: SharedQuotaCoordinator | None = None,
        deadline: float | None = None,
        timeout: int = 30,
        max_retries: int = 6,
    ) -> None:
        self._api_calls_used = 0
        self.shard_name = shard_name
        self.coordinator = coordinator
        self.deadline = deadline
        self.rate_limit_events = 0
        self.secondary_rate_limit_events = 0
        super().__init__(token, cache_dir=cache_dir, timeout=timeout, max_retries=max_retries)

    @property
    def api_calls_used(self) -> int:
        return self._api_calls_used

    @api_calls_used.setter
    def api_calls_used(self, value: int) -> None:
        prior = getattr(self, "_api_calls_used", 0)
        self._api_calls_used = value
        delta = value - prior
        if self.coordinator is not None and delta > 0:
            self.coordinator.register_api_calls(delta, self.shard_name)

    def _pause_for_rate_limit(self, query: str) -> None:
        if self.coordinator is not None:
            self.coordinator.before_request(self.shard_name, query, self.deadline)
        elif self.deadline is not None and time.monotonic() >= self.deadline:
            raise ShardBudgetExceeded(f"{self.shard_name} exceeded its wall-clock budget.")
        super()._pause_for_rate_limit(query)

    def _respect_min_interval(self, url: str) -> None:
        if self.deadline is not None and time.monotonic() >= self.deadline:
            raise ShardBudgetExceeded(f"{self.shard_name} exceeded its wall-clock budget.")
        super()._respect_min_interval(url)

    def _sleep_before_retry(
        self,
        attempt: int,
        headers: dict[str, str] | None,
        body: str,
        query: str,
        retry_limit: int,
        max_delay_seconds: float,
    ) -> None:
        lowered = body.lower()
        retry_after = None
        if headers and headers.get("Retry-After"):
            try:
                retry_after = max(float(headers["Retry-After"]), 1.0)
            except ValueError:
                retry_after = None
        reset_delay = self._reset_delay(headers)
        delay = retry_after or reset_delay or min(2**attempt, max_delay_seconds)
        if "secondary rate limit" in lowered:
            self.rate_limit_events += 1
            self.secondary_rate_limit_events += 1
            reason = f"{self.shard_name} hit a secondary rate limit while requesting {query}."
            if self.coordinator is not None:
                self.coordinator.register_backoff(self.shard_name, max(delay, 8.0), reason, secondary=True)
            raise ExperimentAbort(reason)
        if headers and (
            headers.get("Retry-After") is not None
            or headers.get("X-RateLimit-Remaining") == "0"
            or (self.rate_limit_remaining is not None and self.rate_limit_remaining <= 0)
        ):
            self.rate_limit_events += 1
            if self.coordinator is not None:
                self.coordinator.register_backoff(
                    self.shard_name,
                    max(delay, 1.0),
                    f"{self.shard_name} backing off before retrying {query}.",
                )
        super()._sleep_before_retry(attempt, headers, body, query, retry_limit, max_delay_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", required=True, help="UTC crawl window start date (YYYY-MM-DD).")
    parser.add_argument("--as-of", required=True, help="UTC crawl window end date (YYYY-MM-DD).")
    parser.add_argument("--max-results", type=int, default=250, help="Maximum repositories per query.")
    parser.add_argument("--topic", default=None, help="Optional topic id.")
    parser.add_argument("--config", default=None, help="Optional crawl topic config file.")
    parser.add_argument("--shards", type=int, default=3, help="Total shards including search shards.")
    parser.add_argument("--wall-clock-budget", type=int, default=DEFAULT_WALL_CLOCK_BUDGET)
    parser.add_argument("--api-budget-multiplier", type=float, default=DEFAULT_API_BUDGET_MULTIPLIER)
    parser.add_argument("--output-dir", default=str(EXPERIMENT_ROOT))
    parser.add_argument("--experiment-id", default=None)
    return parser.parse_args()


def build_context(args: argparse.Namespace, experiment_dir: Path) -> CrawlContext:
    crawled_at = utc_now()
    since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=UTC)
    window_end = datetime.strptime(args.as_of, "%Y-%m-%d").replace(tzinfo=UTC)
    topic_id = args.topic
    max_results = max(1, min(int(args.max_results), 1000))
    config_args = argparse.Namespace(
        since=args.since,
        as_of=args.as_of,
        max_results=max_results,
        output=str(experiment_dir / "baseline-raw.json"),
        topic=topic_id,
        config=args.config,
    )
    return CrawlContext(
        args=args,
        topic_id=topic_id,
        topic_raw=raw_dir(topic_id),
        topic_snapshots=snapshots_dir(topic_id),
        topic_cache=cache_dir(topic_id),
        crawled_at=crawled_at,
        run_started_at=crawled_at,
        since=since,
        window_end=window_end,
        week=week_slug(window_end),
        max_results=max_results,
        config_checksum=github_crawl_config_checksum(config_args, since, window_end, max_results),
        current_code_sha=os.environ.get("CRAWLER_CODE_SHA", ""),
        source_refresh_policy="force-refresh",
        baseline_output_path=experiment_dir / "baseline-raw.json",
        baseline_snapshot_path=experiment_dir / "baseline-stars.json",
        shard_output_path=experiment_dir / "shard-raw.json",
        shard_snapshot_path=experiment_dir / "shard-stars.json",
    )


def next_experiment_id(output_dir: Path) -> str:
    index = 0
    for candidate in output_dir.glob("shard-435-run-*"):
        suffix = candidate.name.removeprefix("shard-435-run-")
        if suffix.isdigit():
            index = max(index, int(suffix))
    return f"shard-435-run-{index + 1:03d}"


def build_search_plans(context: CrawlContext) -> list[SearchPlan]:
    if context.args.config:
        queries = load_topic_queries(
            context.args.config,
            {"last_week": context.since.date().isoformat(), "today": context.window_end.date().isoformat()},
        )
        return [
            SearchPlan(
                shard_name="new-search",
                repo_group="new",
                primary_queries=list(queries["primary"]),
                secondary_queries=list(queries["secondary"]),
                min_repos_per_week=int(queries["min_repos_per_week"]),
            )
        ]
    return [
        SearchPlan(
            shard_name="new-search",
            repo_group="new",
            primary_queries=[f"created:{context.since.date().isoformat()}..{context.window_end.date().isoformat()} stars:>50"],
        ),
        SearchPlan(
            shard_name="trending-search",
            repo_group="trending",
            primary_queries=[f"pushed:{context.since.date().isoformat()}..{context.window_end.date().isoformat()} stars:>50"],
        ),
    ]


def run_search_plan(
    plan: SearchPlan,
    client: InstrumentedGitHubClient,
    *,
    max_results: int,
    wall_clock_budget: int,
    coordinator: SharedQuotaCoordinator | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    errors: list[str] = []
    completed = True
    try:
        for query in plan.primary_queries:
            candidates.extend(client.search_repositories(query, max_results=max_results))
        if plan.secondary_queries and len(candidates) < plan.min_repos_per_week:
            for query in plan.secondary_queries:
                candidates.extend(client.search_repositories(query, max_results=max_results))
    except ShardBudgetExceeded as exc:
        completed = False
        errors.append(str(exc))
        if coordinator is not None:
            coordinator.record_budget_exceeded(plan.shard_name, wall_clock_budget)
    except ExperimentAbort:
        raise
    return candidates, {
        "completed": completed,
        "errors": errors + list(client.errors),
        "api_calls": client.api_calls_used,
        "cache_hits": client.cache_hits,
        "stale_cache_hits": client.stale_cache_hits,
        "rate_limit_events": client.rate_limit_events,
        "secondary_rate_limit_events": client.secondary_rate_limit_events,
    }


def chunk_validation_items(items: list[ValidationItem], worker_count: int) -> list[list[ValidationItem]]:
    if not items:
        return []
    chunk_size = max(1, math.ceil(len(items) / max(worker_count * 2, 1)))
    return [items[index : index + chunk_size] for index in range(0, len(items), chunk_size)]


def prepare_validation_items(
    new_candidates: list[dict[str, Any]],
    trending_candidates: list[dict[str, Any]],
    worker_count: int,
) -> tuple[Queue[list[ValidationItem]], dict[str, int]]:
    duplicate_counts = {"new": 0, "trending": 0}
    grouped_unique_items: list[ValidationItem] = []
    for repo_group, candidates in (("new", new_candidates), ("trending", trending_candidates)):
        seen: set[str] = set()
        for sequence, repo in enumerate(candidates):
            full_name = repo.get("full_name")
            if not full_name:
                grouped_unique_items.append(ValidationItem(repo_group=repo_group, sequence=sequence, repo=repo))
                continue
            if full_name in seen:
                duplicate_counts[repo_group] += 1
                continue
            seen.add(full_name)
            grouped_unique_items.append(ValidationItem(repo_group=repo_group, sequence=sequence, repo=repo))
    queue: Queue[list[ValidationItem]] = Queue()
    for chunk in chunk_validation_items(grouped_unique_items, worker_count):
        queue.put(chunk)
    return queue, duplicate_counts


def trending_stars_gained(
    repo: dict[str, Any],
    *,
    previous_stars: dict[str, int] | None,
    trending_cutoff: datetime | None,
) -> int | None:
    if previous_stars is None:
        return None
    previous_value = previous_stars.get(str(repo.get("full_name") or ""))
    current_stars = int(repo.get("stargazers_count") or 0)
    if previous_value is not None:
        return max(current_stars - previous_value, 0)
    if previous_stars and trending_cutoff is not None and isinstance(repo.get("created_at"), str):
        created = datetime.fromisoformat(str(repo["created_at"]).replace("Z", "+00:00"))
        if created >= trending_cutoff:
            return current_stars
    return None


def validate_item(
    client: InstrumentedGitHubClient,
    item: ValidationItem,
    *,
    previous_stars: dict[str, int] | None,
    trending_cutoff: datetime | None,
) -> tuple[ValidatedRecord | None, str | None]:
    full_name = item.repo.get("full_name")
    if not full_name:
        return None, "missing_full_name"
    skip_reason = significance_skip_reason(item.repo)
    if skip_reason:
        return None, skip_reason
    try:
        if not client.has_readme(full_name):
            return None, "missing_readme"
    except RuntimeError as exc:
        client.record_error(f"README lookup failed for {full_name}: {exc}")
        return None, "readme_lookup_failed"
    stars_gained = None
    if item.repo_group == "trending":
        stars_gained = trending_stars_gained(
            item.repo,
            previous_stars=previous_stars,
            trending_cutoff=trending_cutoff,
        )
    return ValidatedRecord(item.repo_group, item.sequence, to_repo_record(item.repo, stars_gained=stars_gained)), None


def sort_validated_records(
    records: list[ValidatedRecord],
    *,
    previous_stars: dict[str, int] | None,
) -> list[dict[str, Any]]:
    if records and records[0].repo_group == "trending" and previous_stars:
        ordered = sorted(
            records,
            key=lambda item: (
                -int(item.record.get("stars_gained", -1) if item.record.get("stars_gained") is not None else -1),
                -int(item.record.get("stars") or 0),
                item.sequence,
            ),
        )
    else:
        ordered = sorted(records, key=lambda item: (-int(item.record.get("stars") or 0), item.sequence))
    return [item.record for item in ordered]


def validation_worker(
    worker_index: int,
    queue: Queue[list[ValidationItem]],
    client: InstrumentedGitHubClient,
    *,
    previous_stars: dict[str, int] | None,
    trending_cutoff: datetime | None,
    wall_clock_budget: int,
    coordinator: SharedQuotaCoordinator,
) -> dict[str, Any]:
    shard_name = f"validate-{worker_index}"
    results = {"new": [], "trending": []}
    filters: dict[str, Counter[str]] = {"new": Counter(), "trending": Counter()}
    completed = True
    while True:
        try:
            chunk = queue.get_nowait()
        except Empty:
            break
        current_index = 0
        try:
            for current_index, item in enumerate(chunk):
                validated, skip_reason = validate_item(
                    client,
                    item,
                    previous_stars=previous_stars,
                    trending_cutoff=trending_cutoff,
                )
                if validated is not None:
                    results[item.repo_group].append(validated)
                elif skip_reason is not None:
                    filters[item.repo_group][skip_reason] += 1
        except ShardBudgetExceeded:
            completed = False
            coordinator.record_budget_exceeded(shard_name, wall_clock_budget)
            remaining_items = chunk[current_index:]
            if remaining_items:
                queue.put(remaining_items)
                coordinator.record_redistribution(shard_name, len(remaining_items))
            break
        except ExperimentAbort:
            raise
    return {
        "completed": completed,
        "results": results,
        "filters": {name: dict(counter) for name, counter in filters.items()},
        "errors": list(client.errors),
        "api_calls": client.api_calls_used,
        "cache_hits": client.cache_hits,
        "stale_cache_hits": client.stale_cache_hits,
        "rate_limit_events": client.rate_limit_events,
        "secondary_rate_limit_events": client.secondary_rate_limit_events,
    }


def build_payload(
    *,
    context: CrawlContext,
    output_path: Path,
    snapshot_path: Path,
    new_repos: list[dict[str, Any]],
    trending_repos: list[dict[str, Any]],
    new_candidates: list[dict[str, Any]],
    trending_candidates: list[dict[str, Any]],
    api_calls: int,
    cache_hits: int,
    stale_cache_hits: int,
    rate_limit_limit: int | None,
    rate_limit_remaining: int | None,
    rate_limit_reset: int | None,
    rate_limit_resource: str | None,
    partial_failures: list[str],
    filter_summary: dict[str, dict[str, int]],
    run_mode: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    star_snapshot = build_star_snapshot(new_candidates, trending_candidates)
    snapshot_payload = {
        "week": context.week,
        "captured_at": iso_timestamp(context.crawled_at),
        "repository_count": len(star_snapshot),
        "stars": star_snapshot,
    }
    payload = {
        "week": context.week,
        "crawled_at": iso_timestamp(context.crawled_at),
        "new_repos": new_repos,
        "trending_repos": trending_repos,
        "signals": build_signals(new_repos, trending_repos),
        "metadata": {
            "api_calls_used": api_calls,
            "cache_hits": cache_hits,
            "stale_cache_hits": stale_cache_hits,
            "rate_limit_limit": rate_limit_limit,
            "rate_limit_remaining": rate_limit_remaining,
            "rate_limit_reset": rate_limit_reset,
            "rate_limit_resource": rate_limit_resource,
            "partial_failures": partial_failures,
            "run_id": f"local-{run_mode}",
            "crawl_window": {
                "since": context.since.date().isoformat(),
                "until": context.window_end.date().isoformat(),
            },
            "crawl_config_checksum": context.config_checksum,
            "schema_checksum": github_schema_checksum(),
            "same_day_reuse": {"status": "not_reused", "source": "github", "source_id": "github-search"},
            "filter_summary": filter_summary,
            "snapshot_path": snapshot_path.as_posix(),
            "source_refresh_policy": context.source_refresh_policy,
            "crawler_code_sha": context.current_code_sha,
            "experiment_mode": run_mode,
            "output_path": output_path.as_posix(),
        },
    }
    payload["metadata"]["artifact_checksum"] = github_artifact_checksum(payload)
    validate_payload(payload)
    return payload, snapshot_payload


def run_baseline(context: CrawlContext, token: str) -> RunResult:
    started_at = time.monotonic()
    search_plans = build_search_plans(context)
    client = InstrumentedGitHubClient(token, cache_dir=context.topic_cache, shard_name="baseline")
    previous_stars = load_previous_star_snapshot(
        context.topic_snapshots,
        context.week,
        context.baseline_output_path.parent,
        context.topic_raw,
        RAW_ROOT,
    )
    new_candidates: list[dict[str, Any]] = []
    trending_candidates: list[dict[str, Any]] = []
    if context.args.config:
        new_candidates, _ = run_search_plan(
            search_plans[0],
            client,
            max_results=context.max_results,
            wall_clock_budget=context.args.wall_clock_budget,
            coordinator=None,
        )
    else:
        for plan in search_plans:
            candidates, _ = run_search_plan(
                plan,
                client,
                max_results=context.max_results,
                wall_clock_budget=context.args.wall_clock_budget,
                coordinator=None,
            )
            if plan.repo_group == "new":
                new_candidates = candidates
            else:
                trending_candidates = candidates
    new_repos, new_filters = collect_repositories(client, new_candidates)
    trending_repos, trending_filters = collect_repositories(
        client,
        trending_candidates,
        previous_stars=previous_stars,
        trending_cutoff=context.since,
    )
    payload, snapshot_payload = build_payload(
        context=context,
        output_path=context.baseline_output_path,
        snapshot_path=context.baseline_snapshot_path,
        new_repos=new_repos,
        trending_repos=trending_repos,
        new_candidates=new_candidates,
        trending_candidates=trending_candidates,
        api_calls=client.api_calls_used,
        cache_hits=client.cache_hits,
        stale_cache_hits=client.stale_cache_hits,
        rate_limit_limit=client.rate_limit_limit,
        rate_limit_remaining=client.rate_limit_remaining,
        rate_limit_reset=client.rate_limit_reset,
        rate_limit_resource=client.rate_limit_resource,
        partial_failures=list(client.errors),
        filter_summary={"new_repos": new_filters, "trending_repos": trending_filters},
        run_mode="baseline",
    )
    write_payload(context.baseline_output_path, payload)
    write_payload(context.baseline_snapshot_path, snapshot_payload)
    return RunResult(
        name="baseline",
        payload=payload,
        snapshot_payload=snapshot_payload,
        api_calls=client.api_calls_used,
        cache_hits=client.cache_hits,
        stale_cache_hits=client.stale_cache_hits,
        rate_limit_events=client.rate_limit_events,
        secondary_rate_limit_events=client.secondary_rate_limit_events,
        partial_failures=list(client.errors),
        wall_clock_s=round(time.monotonic() - started_at, 3),
        shards_used=1,
        completed=not bool(client.errors),
        guardrail_events=[],
    )


def run_sharded(context: CrawlContext, token: str, baseline_api_calls: int) -> RunResult:
    started_at = time.monotonic()
    search_plans = build_search_plans(context)
    validation_workers = max(1, int(context.args.shards) - len(search_plans))
    api_hard_cap = max(1, math.floor(baseline_api_calls * float(context.args.api_budget_multiplier)))
    coordinator = SharedQuotaCoordinator(api_hard_cap)
    previous_stars = load_previous_star_snapshot(
        context.topic_snapshots,
        context.week,
        context.shard_output_path.parent,
        context.topic_raw,
        RAW_ROOT,
    )
    aggregated_errors: list[str] = []
    aggregated_api_calls = 0
    aggregated_cache_hits = 0
    aggregated_stale_cache_hits = 0
    aggregated_rate_limit_events = 0
    aggregated_secondary_rate_limit_events = 0
    search_results: dict[str, list[dict[str, Any]]] = {"new": [], "trending": []}

    try:
        with ThreadPoolExecutor(max_workers=max(len(search_plans), 1)) as pool:
            futures = {
                pool.submit(
                    run_search_plan,
                    plan,
                    InstrumentedGitHubClient(
                        token,
                        cache_dir=context.topic_cache,
                        shard_name=plan.shard_name,
                        coordinator=coordinator,
                        deadline=time.monotonic() + int(context.args.wall_clock_budget),
                    ),
                    max_results=context.max_results,
                    wall_clock_budget=int(context.args.wall_clock_budget),
                    coordinator=coordinator,
                ): plan
                for plan in search_plans
            }
            for future in as_completed(futures):
                plan = futures[future]
                candidates, metrics = future.result()
                search_results[plan.repo_group] = candidates
                aggregated_errors.extend(metrics["errors"])
                aggregated_api_calls += metrics["api_calls"]
                aggregated_cache_hits += metrics["cache_hits"]
                aggregated_stale_cache_hits += metrics["stale_cache_hits"]
                aggregated_rate_limit_events += metrics["rate_limit_events"]
                aggregated_secondary_rate_limit_events += metrics["secondary_rate_limit_events"]
    except ExperimentAbort as exc:
        aggregated_errors.append(str(exc))

    validation_queue, duplicate_counts = prepare_validation_items(
        search_results["new"], search_results["trending"], validation_workers
    )
    validated_records: dict[str, list[ValidatedRecord]] = {"new": [], "trending": []}
    filter_summary: dict[str, Counter[str]] = {
        "new_repos": Counter({"duplicate": duplicate_counts["new"]}),
        "trending_repos": Counter({"duplicate": duplicate_counts["trending"]}),
    }
    if coordinator.abort_reason is None:
        try:
            with ThreadPoolExecutor(max_workers=validation_workers) as pool:
                futures = {
                    pool.submit(
                        validation_worker,
                        index + 1,
                        validation_queue,
                        InstrumentedGitHubClient(
                            token,
                            cache_dir=context.topic_cache,
                            shard_name=f"validate-{index + 1}",
                            coordinator=coordinator,
                            deadline=time.monotonic() + int(context.args.wall_clock_budget),
                        ),
                        previous_stars=previous_stars,
                        trending_cutoff=context.since,
                        wall_clock_budget=int(context.args.wall_clock_budget),
                        coordinator=coordinator,
                    ): index + 1
                    for index in range(validation_workers)
                }
                for future in as_completed(futures):
                    result = future.result()
                    validated_records["new"].extend(result["results"]["new"])
                    validated_records["trending"].extend(result["results"]["trending"])
                    filter_summary["new_repos"].update(result["filters"]["new"])
                    filter_summary["trending_repos"].update(result["filters"]["trending"])
                    aggregated_errors.extend(result["errors"])
                    aggregated_api_calls += result["api_calls"]
                    aggregated_cache_hits += result["cache_hits"]
                    aggregated_stale_cache_hits += result["stale_cache_hits"]
                    aggregated_rate_limit_events += result["rate_limit_events"]
                    aggregated_secondary_rate_limit_events += result["secondary_rate_limit_events"]
        except ExperimentAbort as exc:
            aggregated_errors.append(str(exc))

    new_repos = sort_validated_records(validated_records["new"], previous_stars=None)
    trending_repos = sort_validated_records(validated_records["trending"], previous_stars=previous_stars)
    payload, snapshot_payload = build_payload(
        context=context,
        output_path=context.shard_output_path,
        snapshot_path=context.shard_snapshot_path,
        new_repos=new_repos,
        trending_repos=trending_repos,
        new_candidates=search_results["new"],
        trending_candidates=search_results["trending"],
        api_calls=aggregated_api_calls,
        cache_hits=aggregated_cache_hits,
        stale_cache_hits=aggregated_stale_cache_hits,
        rate_limit_limit=None,
        rate_limit_remaining=None,
        rate_limit_reset=None,
        rate_limit_resource="mixed",
        partial_failures=aggregated_errors,
        filter_summary={name: dict(counter) for name, counter in filter_summary.items()},
        run_mode="shard",
    )
    write_payload(context.shard_output_path, payload)
    write_payload(context.shard_snapshot_path, snapshot_payload)
    return RunResult(
        name="shard",
        payload=payload,
        snapshot_payload=snapshot_payload,
        api_calls=aggregated_api_calls,
        cache_hits=aggregated_cache_hits,
        stale_cache_hits=aggregated_stale_cache_hits,
        rate_limit_events=aggregated_rate_limit_events,
        secondary_rate_limit_events=aggregated_secondary_rate_limit_events,
        partial_failures=aggregated_errors,
        wall_clock_s=round(time.monotonic() - started_at, 3),
        shards_used=len(search_plans) + validation_workers,
        completed=not aggregated_errors and validation_queue.empty() and not coordinator.secondary_rate_limit_hit,
        guardrail_events=coordinator.guardrail_events(),
    )


def canonicalize_payload(payload: dict[str, Any]) -> bytes:
    canonical = {
        "week": payload.get("week"),
        "new_repos": payload.get("new_repos", []),
        "trending_repos": payload.get("trending_repos", []),
        "signals": payload.get("signals", {}),
    }
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonicalize_snapshot(snapshot_payload: dict[str, Any]) -> bytes:
    canonical = {
        "week": snapshot_payload.get("week"),
        "repository_count": snapshot_payload.get("repository_count"),
        "stars": snapshot_payload.get("stars", {}),
    }
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _normalize_for_comparison(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalize_for_comparison(item)
            for key, item in sorted(value.items())
            if key not in {"crawled_at", "captured_at", "report_generated_at"}
        }
    if isinstance(value, list):
        return [_normalize_for_comparison(item) for item in value]
    return value


def deterministic_merge(shard_results: list[ShardResult]) -> dict[str, Any]:
    merged: dict[str, dict[str, Any]] = {}
    for result in shard_results:
        for repo in result.repos_found:
            full_name = str(repo.get("full_name") or "")
            if full_name and full_name not in merged:
                merged[full_name] = repo
    repos = sorted(
        merged.values(),
        key=lambda item: (
            -(int(item.get("stars_gained", -1) or -1)),
            -(int(item.get("stars") or 0)),
            str(item.get("full_name") or ""),
        ),
    )
    return {"repos": repos}


def compare_results(baseline: dict[str, Any], shard: dict[str, Any]) -> dict[str, Any]:
    baseline_wall = float(baseline.get("wall_clock_s", baseline.get("elapsed_s", 0.0)) or 0.0001)
    shard_wall = float(shard.get("wall_clock_s", shard.get("elapsed_s", 0.0)) or 0.0)
    baseline_api = int(baseline.get("api_calls", baseline.get("api_calls_used", 0)) or 0)
    shard_api = int(shard.get("api_calls", shard.get("api_calls_used", 0)) or 0)
    baseline_output = _normalize_for_comparison(baseline.get("canonical_output", baseline.get("output", {})))
    shard_output = _normalize_for_comparison(shard.get("canonical_output", shard.get("output", {})))
    return {
        "speedup_pct": round(((baseline_wall - shard_wall) / baseline_wall) * 100, 2),
        "api_growth_pct": round(((shard_api - baseline_api) / max(baseline_api, 1)) * 100, 2),
        "output_stable": baseline_output == shard_output,
        "rate_limit_regression": int(shard.get("rate_limit_events", 0) or 0)
        > int(baseline.get("rate_limit_events", 0) or 0),
        "partial_data": bool(shard.get("partial_data", False) or baseline.get("partial_data", False)),
        "baseline_complete": not bool(baseline.get("partial_data", False)),
        "shard_complete": not bool(shard.get("partial_data", False)),
    }


def build_report(experiment_id: str, baseline: RunResult, shard: RunResult) -> dict[str, Any]:
    baseline_wall = baseline.wall_clock_s or 0.0001
    speedup_pct = round(((baseline_wall - shard.wall_clock_s) / baseline_wall) * 100, 2)
    api_growth_pct = round(((shard.api_calls - baseline.api_calls) / max(baseline.api_calls, 1)) * 100, 2)
    output_stable = canonicalize_payload(baseline.payload) == canonicalize_payload(shard.payload) and canonicalize_snapshot(
        baseline.snapshot_payload
    ) == canonicalize_snapshot(shard.snapshot_payload)
    report_card = ExperimentReport.from_comparison(
        {
            "speedup_pct": speedup_pct,
            "api_growth_pct": api_growth_pct,
            "rate_limit_regression": shard.secondary_rate_limit_events > baseline.secondary_rate_limit_events,
            "output_stable": output_stable,
            "partial_data": bool(baseline.partial_failures) or bool(shard.partial_failures),
            "baseline_complete": not bool(baseline.partial_failures),
            "shard_complete": not bool(shard.partial_failures),
        }
    )
    verdict = report_card.verdict
    if report_card.partial_data and any(event["kind"] == "secondary_rate_limit" for event in shard.guardrail_events):
        verdict = "fail"
    return {
        "experiment_id": experiment_id,
        "baseline": {
            "wall_clock_s": baseline.wall_clock_s,
            "api_calls": baseline.api_calls,
            "rate_limit_events": baseline.rate_limit_events,
            "repos_new": len(baseline.payload.get("new_repos", [])),
            "repos_trending": len(baseline.payload.get("trending_repos", [])),
        },
        "shard": {
            "wall_clock_s": shard.wall_clock_s,
            "api_calls": shard.api_calls,
            "rate_limit_events": shard.rate_limit_events,
            "shards_used": shard.shards_used,
            "repos_new": len(shard.payload.get("new_repos", [])),
            "repos_trending": len(shard.payload.get("trending_repos", [])),
        },
        "comparison": {
            "speedup_pct": speedup_pct,
            "api_growth_pct": api_growth_pct,
            "output_stable": output_stable,
            "secondary_rate_limit_regression": shard.secondary_rate_limit_events > baseline.secondary_rate_limit_events,
        },
        "verdict": verdict,
        "guardrail_events": shard.guardrail_events,
    }


def main() -> int:
    args = parse_args()
    if args.shards < 3:
        print("--shards must be >= 3.", file=os.sys.stderr)
        return 1
    if args.wall_clock_budget <= 0:
        print("--wall-clock-budget must be positive.", file=os.sys.stderr)
        return 1
    if args.api_budget_multiplier < 1.0:
        print("--api-budget-multiplier must be >= 1.0.", file=os.sys.stderr)
        return 1
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is required", file=os.sys.stderr)
        return 1
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    experiment_id = args.experiment_id or next_experiment_id(output_dir)
    experiment_dir = output_dir / experiment_id
    experiment_dir.mkdir(parents=True, exist_ok=True)
    context = build_context(args, experiment_dir)
    baseline = run_baseline(context, token)
    shard = run_sharded(context, token, baseline.api_calls)
    report = build_report(experiment_id, baseline, shard)
    report_path = experiment_dir / "report.json"
    write_payload(report_path, report)
    print(
        json.dumps(
            {
                "experiment_id": experiment_id,
                "verdict": report["verdict"],
                "speedup_pct": report["comparison"]["speedup_pct"],
                "api_growth_pct": report["comparison"]["api_growth_pct"],
                "output_stable": report["comparison"]["output_stable"],
                "report_path": report_path.as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["verdict"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
