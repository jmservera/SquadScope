#!/usr/bin/env python3
"""Create durable Hugo topic hubs from recurring analysis signals.

The lifecycle is intentionally additive: a quiet week never deletes an existing
hub. The weekly crawl/analysis pipeline remains read-only input for this step.
"""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "observatory.toml"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
WEEK_RE = re.compile(r"(?P<year>\d{4})-W(?P<week>\d{2})")
SLUG_RE = re.compile(r"[^a-z0-9]+")
SEED_TOPIC_TITLES = {
    "AI Coding Agents",
    "MCP Ecosystem",
    "Open-Source LLMs",
    "Developer Tools",
    "AI Agents in Healthcare",
}


@dataclass(frozen=True)
class HubCreationConfig:
    enabled: bool
    min_weekly_issues: int
    lookback_days: int
    log_path: Path
    ignore_topics: frozenset[str]
    source_globs: tuple[str, ...]


@dataclass
class CandidateSignal:
    title: str
    weeks: set[str]
    sources: set[str]


def slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.strip().lower()).strip("-")
    return slug[:80].strip("-")


def normalized_key(value: str) -> str:
    return slugify(value)


def load_config(path: Path = DEFAULT_CONFIG) -> HubCreationConfig:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    dynamic = raw.get("topic_hubs", {}).get("dynamic_creation", {})
    config_root = path.parent.parent if path.parent.name == "config" else path.parent
    return HubCreationConfig(
        enabled=bool(dynamic.get("enabled", True)),
        min_weekly_issues=int(dynamic["min_weekly_issues"]),
        lookback_days=int(dynamic["lookback_days"]),
        log_path=config_root / str(dynamic["log_path"]),
        ignore_topics=frozenset(
            normalized_key(str(item)) for item in dynamic.get("ignore_topics", [])
        ),
        source_globs=tuple(str(item) for item in dynamic.get("source_globs", [])),
    )


def parse_week_date(week: str) -> date:
    match = WEEK_RE.fullmatch(week)
    if not match:
        raise ValueError(f"Invalid ISO week: {week}")
    return date.fromisocalendar(int(match.group("year")), int(match.group("week")), 1)


def parse_current_date(value: str | None) -> date:
    if value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    return datetime.now(UTC).date()


def read_frontmatter(path: Path) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    parsed = yaml.safe_load(match.group(1))
    return parsed if isinstance(parsed, dict) else {}


def safe_candidate_title(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    title = " ".join(value.strip().split())
    if len(title) < 3 or len(title) > 80:
        return None
    lowered = title.lower()
    if lowered.startswith(("http://", "https://")):
        return None
    if any(
        phrase in lowered for phrase in ("ignore previous", "system prompt", "developer message")
    ):
        return None
    if not re.search(r"[a-zA-Z]", title):
        return None
    return title


def week_from_path(path: Path) -> str | None:
    match = WEEK_RE.search(str(path))
    return match.group(0) if match else None


def collect_weekly_markdown_signals(path: Path) -> tuple[str | None, set[str]]:
    frontmatter = read_frontmatter(path)
    week = str(frontmatter.get("week") or week_from_path(path) or "")
    if not WEEK_RE.fullmatch(week):
        return None, set()
    values: set[str] = set()
    for key in ("candidate_topics", "topics", "tags"):
        raw = frontmatter.get(key)
        if isinstance(raw, list):
            for item in raw:
                title = safe_candidate_title(item)
                if title:
                    values.add(title)
    return week, values


def collect_correlation_signals(path: Path) -> tuple[str | None, set[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    week = str(payload.get("week") or week_from_path(path) or "")
    if not WEEK_RE.fullmatch(week):
        return None, set()
    values: set[str] = set()
    for item in payload.get("uncovered_tech_trends") or []:
        if isinstance(item, dict):
            title = safe_candidate_title(item.get("topic"))
            if title:
                values.add(title)
    return week, values


def existing_hub_keys(content_root: Path) -> set[str]:
    keys = {normalized_key(title) for title in SEED_TOPIC_TITLES}
    topics_root = content_root / "topics"
    for index_path in topics_root.glob("*/_index.md"):
        keys.add(index_path.parent.name)
        frontmatter = read_frontmatter(index_path)
        title = safe_candidate_title(frontmatter.get("title"))
        if title:
            keys.add(normalized_key(title))
    return keys


def collect_candidates(root: Path, config: HubCreationConfig) -> dict[str, CandidateSignal]:
    signals: dict[str, CandidateSignal] = {}
    for pattern in config.source_globs:
        for path in root.glob(pattern):
            if path.suffix == ".md":
                week, titles = collect_weekly_markdown_signals(path)
            elif path.suffix == ".json":
                week, titles = collect_correlation_signals(path)
            else:
                continue
            if not week:
                continue
            for title in titles:
                key = normalized_key(title)
                if not key:
                    continue
                signal = signals.setdefault(
                    key, CandidateSignal(title=title, weeks=set(), sources=set())
                )
                signal.weeks.add(week)
                signal.sources.add(str(path.relative_to(root)))
    return signals


def candidate_is_recent(signal: CandidateSignal, current: date, lookback_days: int) -> bool:
    cutoff = current - timedelta(days=lookback_days)
    return any(parse_week_date(week) >= cutoff for week in signal.weeks)


def render_hub(signal: CandidateSignal, slug: str, config: HubCreationConfig) -> str:
    weeks = sorted(signal.weeks)
    description = (
        f"Evergreen Claracle hub for {signal.title}, created after the topic appeared in "
        f"{len(weeks)} weekly issues within the configured {config.lookback_days}-day window."
    )
    return f'''---
title: "{signal.title.replace('"', '\\"')}"
description: "{description.replace('"', '\\"')}"
summary: "Dynamic topic hub for recurring Claracle coverage of {signal.title.replace('"', '\\"')}."
params:
  dynamic_topic: true
  editorial_stance: "This hub was created by the additive dynamic-topic lifecycle after recurring analysis signals crossed the configured threshold. It persists through quiet weeks."
  discovery:
    min_weekly_issues: {config.min_weekly_issues}
    lookback_days: {config.lookback_days}
    observed_weeks: [{", ".join('"' + week + '"' for week in weeks)}]
---

This hub was created automatically because **{signal.title}** appeared in at least {config.min_weekly_issues} weekly issues within the configured {config.lookback_days}-day lookback window.

It is durable: a quiet week will not delete this page. Future weekly issues join the hub automatically when they include the matching canonical topic frontmatter.
'''


def append_log(config: HubCreationConfig, message: str) -> None:
    config.log_path.parent.mkdir(parents=True, exist_ok=True)
    with config.log_path.open("a", encoding="utf-8") as handle:
        handle.write(message.rstrip() + "\n")


def create_dynamic_hubs(
    *,
    root: Path = PROJECT_ROOT,
    config_path: Path = DEFAULT_CONFIG,
    current_date: str | None = None,
    dry_run: bool = False,
) -> list[Path]:
    config = load_config(config_path)
    now = parse_current_date(current_date)
    append_log(
        config,
        f"dynamic-topic-check enabled={config.enabled} threshold={config.min_weekly_issues} "
        f"lookback_days={config.lookback_days} current_date={now.isoformat()}",
    )
    if not config.enabled:
        return []

    candidates = collect_candidates(root, config)
    existing = existing_hub_keys(root / "content")
    created: list[Path] = []
    skipped: dict[str, str] = defaultdict(str)
    for key, signal in sorted(candidates.items()):
        recent_weeks = {
            week
            for week in signal.weeks
            if parse_week_date(week) >= now - timedelta(days=config.lookback_days)
        }
        if key in existing or key in config.ignore_topics:
            skipped[key] = "existing-or-ignored"
            continue
        if len(recent_weeks) < config.min_weekly_issues or not candidate_is_recent(
            signal, now, config.lookback_days
        ):
            skipped[key] = "below-threshold"
            continue
        target = root / "content" / "topics" / key / "_index.md"
        append_log(
            config,
            f"create topic={signal.title!r} slug={key} weeks={','.join(sorted(recent_weeks))} "
            f"threshold={config.min_weekly_issues}/{config.lookback_days}d",
        )
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_hub(signal, key, config), encoding="utf-8")
        created.append(target)

    append_log(config, f"dynamic-topic-summary created={len(created)} skipped={len(skipped)}")
    return created


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create durable topic hubs from recurring signals."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    created = create_dynamic_hubs(
        config_path=args.config,
        current_date=args.current_date,
        dry_run=args.dry_run,
    )
    for path in created:
        print(path.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
