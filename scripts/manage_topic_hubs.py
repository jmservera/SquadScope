#!/usr/bin/env python3
"""Create durable Hugo topic hubs from recurring weekly topic taxonomy terms.

The lifecycle is intentionally additive: a quiet week never deletes an existing
hub. The weekly crawl/analysis pipeline remains read-only input for this step;
promotion updates the shared topic registry used by generation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.sanitize_repo_content import INJECTION_PHRASES, sanitize_text
from scripts.taxonomy_registry import update_taxonomy_registries

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "observatory.toml"
DEFAULT_TOPICS_REGISTRY = PROJECT_ROOT / "data" / "taxonomy" / "topics.json"
DEFAULT_CANDIDATES_REGISTRY = PROJECT_ROOT / "data" / "taxonomy" / "topic-candidates.json"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
TOPICS_LINE_RE = re.compile(r"^topics:.*$", re.MULTILINE)
CATEGORIES_LINE_RE = re.compile(r"^categories:.*$", re.MULTILINE)
BOLD_HEADING_RE = re.compile(r"^\*\*(?P<title>[^*]+)\*\*", re.MULTILINE)
WEEK_RE = re.compile(r"(?P<year>\d{4})-W(?P<week>\d{2})")
SLUG_RE = re.compile(r"[^a-z0-9]+")
TITLE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9 .&+(),/-]*")


@dataclass(frozen=True)
class HubCreationConfig:
    enabled: bool
    min_weekly_issues: int
    lookback_days: int
    log_path: Path
    ignore_topics: frozenset[str]
    registry_path: Path
    candidates_path: Path


@dataclass
class CandidateSignal:
    title: str
    weeks: set[str]
    sources: set[str]
    aliases: set[str]
    supporting_signals: list[dict[str, Any]]
    eligible: bool
    weekly_issue_count: int = 0
    last_used: str = ""


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
        enabled=bool(dynamic.get("enabled", False)),
        min_weekly_issues=int(dynamic["min_weekly_issues"]),
        lookback_days=int(dynamic["lookback_days"]),
        log_path=config_root / str(dynamic["log_path"]),
        ignore_topics=frozenset(
            normalized_key(str(item)) for item in dynamic.get("ignore_topics", [])
        ),
        registry_path=config_root / "data" / "taxonomy" / "topics.json",
        candidates_path=config_root / "data" / "taxonomy" / "topic-candidates.json",
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
    stripped = value.strip()
    sanitized = sanitize_text(stripped, max_length=80, label="candidate title")
    if sanitized != stripped or any(character in value for character in "\r\n"):
        return None
    title = " ".join(stripped.split())
    if len(title) < 3 or len(title) > 80:
        return None
    lowered = title.lower()
    if lowered.startswith(("http://", "https://")):
        return None
    if any(phrase in lowered for phrase in INJECTION_PHRASES):
        return None
    if "developer message" in lowered or "---" in title or not TITLE_RE.fullmatch(title):
        return None
    if not re.search(r"[a-zA-Z]", title):
        return None
    return title


def week_from_path(path: Path) -> str | None:
    match = WEEK_RE.search(str(path))
    return match.group(0) if match else None


def existing_hub_keys(content_root: Path) -> set[str]:
    keys: set[str] = set()
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
    if not config.candidates_path.exists():
        return signals
    payload = json.loads(config.candidates_path.read_text(encoding="utf-8"))
    candidates = payload.get("candidates", {}) if isinstance(payload, dict) else {}
    if not isinstance(candidates, dict):
        return signals
    for slug, raw in candidates.items():
        if not isinstance(raw, dict):
            continue
        title = safe_candidate_title(raw.get("display_name"))
        if not title:
            raise ValueError(f"Rejected unsafe candidate title for {slug!r}")
        expected_slug = normalized_key(title)
        if slug != expected_slug:
            raise ValueError(f"Rejected candidate slug {slug!r}; expected {expected_slug!r}")
        weekly_count = int(raw.get("weekly_issue_count") or 0)
        weeks = {
            str(week)
            for week in raw.get("evidence_weeks", [])
            if isinstance(week, str) and WEEK_RE.fullmatch(week)
        }
        signal = CandidateSignal(
            title=title,
            weeks=weeks,
            sources={
                str(source.get("source_path"))
                for source in raw.get("sources", [])
                if isinstance(source, dict) and source.get("source_path")
            },
            aliases={
                str(alias) for alias in raw.get("aliases", []) if isinstance(alias, str) and alias
            },
            supporting_signals=[
                support
                for support in raw.get("supporting_signals", [])
                if isinstance(support, dict)
            ],
            eligible=bool(raw.get("eligible", False)),
            weekly_issue_count=weekly_count,
            last_used=parse_week_date(max(weeks)).isoformat() if weeks else "",
        )
        signals[slug] = signal
    return signals


def candidate_is_recent(signal: CandidateSignal, current: date, lookback_days: int) -> bool:
    if signal.last_used:
        return datetime.fromisoformat(signal.last_used).date() >= current - timedelta(
            days=lookback_days
        )
    if signal.weekly_issue_count:
        return False
    cutoff = current - timedelta(days=lookback_days)
    return any(parse_week_date(week) >= cutoff for week in signal.weeks)


def render_hub(signal: CandidateSignal, slug: str, config: HubCreationConfig) -> str:
    weeks = sorted(signal.weeks)
    weekly_count = signal.weekly_issue_count or len(weeks)
    description = (
        f"Evergreen Claracle hub for {signal.title}, created after the topic appeared in "
        f"{weekly_count} weekly issues within the configured {config.lookback_days}-day window."
    )
    frontmatter = {
        "title": signal.title,
        "description": description,
        "summary": f"Dynamic topic hub for recurring Claracle coverage of {signal.title}.",
        "params": {
            "dynamic_topic": True,
            "editorial_stance": (
                "This hub was created by the additive dynamic-topic lifecycle after recurring "
                "analysis signals crossed the configured threshold. It persists through quiet weeks."
            ),
            "discovery": {
                "min_weekly_issues": config.min_weekly_issues,
                "lookback_days": config.lookback_days,
                "observed_weeks": weeks,
            },
        },
    }
    serialized = yaml.safe_dump(
        frontmatter, sort_keys=False, allow_unicode=True, width=1000
    ).rstrip()
    return (
        f"---\n{serialized}\n---\n\n"
        f"This hub was created automatically because **{signal.title}** appeared in at least "
        f"{config.min_weekly_issues} weekly issues within the configured "
        f"{config.lookback_days}-day lookback window.\n\n"
        "It is durable: a quiet week will not delete this page. Future weekly issues join the "
        "hub automatically when they include the matching canonical topic frontmatter.\n"
    )


def promote_topic_in_registry(registry_path: Path, slug: str) -> None:
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    terms = payload.get("terms", {}) if isinstance(payload, dict) else {}
    if isinstance(terms, dict) and slug in terms and isinstance(terms[slug], dict):
        terms[slug]["is_hub"] = True
        terms[slug]["promoted"] = True
        registry_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def add_topic_to_registry(registry_path: Path, slug: str, signal: CandidateSignal) -> None:
    """Create or promote a canonical registry term from candidate evidence."""
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    terms = payload.setdefault("terms", {})
    if not isinstance(terms, dict):
        raise ValueError(f"{registry_path}: terms must be a mapping")
    term = terms.setdefault(slug, {})
    if not isinstance(term, dict):
        raise ValueError(f"{registry_path}: invalid term {slug}")
    term.update(
        {
            "display_name": signal.title,
            "slug": slug,
            "first_seen": parse_week_date(min(signal.weeks)).isoformat(),
            "last_used": parse_week_date(max(signal.weeks)).isoformat(),
            "count": int(term.get("count") or 0),
            "times_used": int(term.get("times_used") or 0),
            "weekly_issue_count": int(term.get("weekly_issue_count") or 0),
            "is_hub": True,
            "promoted": True,
            "aliases": sorted(signal.aliases, key=str.lower),
        }
    )
    registry_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def proposed_weekly_assignments(root: Path, signal: CandidateSignal) -> list[Path]:
    """Return weekly issue paths that would gain signal.title, without writing."""
    proposed: list[Path] = []
    for week in sorted(signal.weeks):
        year, number = week.split("-W", maxsplit=1)
        path = root / "content" / "weekly" / year / f"W{number}.md"
        if not path.exists():
            continue
        document = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(document)
        if not match:
            raise ValueError(f"{path}: missing YAML frontmatter")
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            raise ValueError(f"{path}: frontmatter must be a mapping")
        topics = frontmatter.get("topics", [])
        if not isinstance(topics, list) or any(not isinstance(topic, str) for topic in topics):
            raise ValueError(f"{path}: topics must be a list of strings")
        if signal.title in topics:
            continue
        proposed.append(path)
    return proposed


def assign_topic_to_weeks(root: Path, signal: CandidateSignal) -> list[Path]:
    """Add a promoted canonical topic to every evidenced weekly issue."""
    changed: list[Path] = []
    for path in proposed_weekly_assignments(root, signal):
        document = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(document)
        if not match:
            raise ValueError(f"{path}: missing YAML frontmatter")
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            raise ValueError(f"{path}: frontmatter must be a mapping")
        topics = frontmatter.get("topics", [])
        if not isinstance(topics, list) or any(not isinstance(topic, str) for topic in topics):
            raise ValueError(f"{path}: topics must be a list of strings")
        topics_line = (
            "topics: [" + ", ".join(json.dumps(topic) for topic in [*topics, signal.title]) + "]"
        )
        frontmatter_text = match.group(1)
        if TOPICS_LINE_RE.search(frontmatter_text):
            updated_frontmatter = TOPICS_LINE_RE.sub(topics_line, frontmatter_text, count=1)
        else:
            categories = CATEGORIES_LINE_RE.search(frontmatter_text)
            if not categories:
                raise ValueError(f"{path}: categories field is required before topics")
            updated_frontmatter = (
                frontmatter_text[: categories.end()]
                + "\n"
                + topics_line
                + frontmatter_text[categories.end() :]
            )
        updated = document[: match.start(1)] + updated_frontmatter + document[match.end(1) :]
        path.write_text(updated, encoding="utf-8")
        changed.append(path)
    return changed


def assign_promoted_topics_from_sources(root: Path, registry_path: Path) -> list[Path]:
    """Assign dynamic canonical topics when their aliases recur in current sources."""
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    terms = payload.get("terms", {}) if isinstance(payload, dict) else {}
    aliases: dict[str, str] = {}
    if not isinstance(terms, dict):
        return []
    for slug, raw in terms.items():
        if (
            not isinstance(raw, dict)
            or not raw.get("promoted")
            or not raw.get("is_hub")
            or isinstance(raw.get("order"), int)
        ):
            continue
        title = safe_candidate_title(raw.get("display_name"))
        if not title:
            continue
        aliases[normalized_key(str(slug))] = title
        aliases[normalized_key(title)] = title
        for alias in raw.get("aliases", []):
            if isinstance(alias, str):
                aliases[normalized_key(alias)] = title

    weeks_by_title: dict[str, set[str]] = defaultdict(set)

    def record(week: str | None, values: list[object]) -> None:
        if not week:
            return
        for value in values:
            if isinstance(value, str) and (title := aliases.get(normalized_key(value))):
                weeks_by_title[title].add(week)

    for path in sorted((root / "content" / "weekly").glob("**/W[0-9][0-9].md")):
        values = read_frontmatter(path).get("tags", [])
        record(week_from_path(path), values if isinstance(values, list) else [])
    for path in sorted((root / "data" / "analyzed").glob("*-summary.md")):
        values = read_frontmatter(path).get("tags", [])
        record(week_from_path(path), values if isinstance(values, list) else [])
        headings = BOLD_HEADING_RE.findall(path.read_text(encoding="utf-8"))
        record(week_from_path(path), [heading.rstrip(".?!") for heading in headings])
    for path in sorted((root / "data" / "raw").glob("*.json")):
        week = week_from_path(path)
        if not week or path.name.endswith("-external-news.json"):
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        signals = raw.get("signals", {}) if isinstance(raw, dict) else {}
        top_topics = signals.get("top_topics", []) if isinstance(signals, dict) else []
        record(week, [item.get("topic") for item in top_topics if isinstance(item, dict)])
        for bucket in ("new_repos", "trending_repos"):
            for repo in raw.get(bucket, []) if isinstance(raw, dict) else []:
                if isinstance(repo, dict) and isinstance(repo.get("topics"), list):
                    record(week, repo["topics"])

    changed: list[Path] = []
    for title, weeks in sorted(weeks_by_title.items()):
        changed.extend(
            assign_topic_to_weeks(
                root,
                CandidateSignal(
                    title=title,
                    weeks=weeks,
                    sources=set(),
                    aliases=set(),
                    supporting_signals=[],
                    eligible=True,
                ),
            )
        )
    return sorted(set(changed))


def append_log(config: HubCreationConfig, message: str) -> None:
    config.log_path.parent.mkdir(parents=True, exist_ok=True)
    with config.log_path.open("a", encoding="utf-8") as handle:
        handle.write(message.rstrip() + "\n")


def preview_dynamic_hubs(
    *,
    root: Path = PROJECT_ROOT,
    config_path: Path = DEFAULT_CONFIG,
    current_date: str | None = None,
) -> list[dict[str, Any]]:
    """Report proposed topic-hub promotions without writing any file.

    Evaluates every candidate through the same eligibility path as
    create_dynamic_hubs(), but never creates a hub, updates the registry,
    assigns weekly frontmatter, or appends to the log.
    """
    config = load_config(config_path)
    now = parse_current_date(current_date)
    candidates = collect_candidates(root, config)
    existing = existing_hub_keys(root / "content")
    registry_terms: dict[str, Any] = {}
    if config.registry_path.exists():
        payload = json.loads(config.registry_path.read_text(encoding="utf-8"))
        terms = payload.get("terms") if isinstance(payload, dict) else None
        registry_terms = terms if isinstance(terms, dict) else {}

    report: list[dict[str, Any]] = []
    for key, signal in sorted(candidates.items()):
        weekly_count = signal.weekly_issue_count or len(signal.weeks)
        entry: dict[str, Any] = {
            "slug": key,
            "title": signal.title,
            "evidence_weeks": sorted(signal.weeks),
            "supporting_sources": sorted(signal.sources),
            "weekly_issue_count": weekly_count,
            "action": "skip",
            "skip_reason": None,
            "proposed_hub_path": None,
            "proposed_weekly_assignments": [],
            "registry_effect": None,
        }
        if key in existing or key in config.ignore_topics:
            entry["skip_reason"] = "existing-or-ignored"
        elif not signal.eligible or not signal.supporting_signals:
            entry["skip_reason"] = "missing-supporting-evidence"
        elif weekly_count < config.min_weekly_issues or not candidate_is_recent(
            signal, now, config.lookback_days
        ):
            entry["skip_reason"] = "below-threshold"
        else:
            entry["action"] = "promote"
            entry["proposed_hub_path"] = (
                (root / "content" / "topics" / key / "_index.md").relative_to(root).as_posix()
            )
            entry["proposed_weekly_assignments"] = [
                path.relative_to(root).as_posix()
                for path in proposed_weekly_assignments(root, signal)
            ]
            entry["registry_effect"] = (
                "promote-existing-term" if key in registry_terms else "create-new-term"
            )
        report.append(entry)
    return report


def create_dynamic_hubs(
    *,
    root: Path = PROJECT_ROOT,
    config_path: Path = DEFAULT_CONFIG,
    current_date: str | None = None,
    dry_run: bool = False,
) -> list[Path]:
    config = load_config(config_path)
    now = parse_current_date(current_date)
    if dry_run:
        # The preview reads candidates and reports proposed changes without writing
        # anything, so it is safe to run regardless of the enabled flag - this is
        # exactly how a reviewer evaluates candidates before flipping the flag on.
        report = preview_dynamic_hubs(root=root, config_path=config_path, current_date=current_date)
        print(json.dumps({"schema_version": 1, "candidates": report}, indent=2, sort_keys=True))
        return []
    if not config.enabled:
        print("dynamic-topic-decision enabled=false action=skip reason=disabled", file=sys.stderr)
        return []

    candidates = collect_candidates(root, config)
    append_log(
        config,
        f"dynamic-topic-check enabled=true threshold={config.min_weekly_issues} "
        f"lookback_days={config.lookback_days} current_date={now.isoformat()}",
    )
    existing = existing_hub_keys(root / "content")
    created: list[Path] = []
    skipped: dict[str, str] = defaultdict(str)
    for key, signal in sorted(candidates.items()):
        weekly_count = signal.weekly_issue_count or len(signal.weeks)
        if key in existing or key in config.ignore_topics:
            skipped[key] = "existing-or-ignored"
            continue
        if not signal.eligible or not signal.supporting_signals:
            skipped[key] = "missing-supporting-evidence"
            continue
        if weekly_count < config.min_weekly_issues or not candidate_is_recent(
            signal, now, config.lookback_days
        ):
            skipped[key] = "below-threshold"
            continue
        target = root / "content" / "topics" / key / "_index.md"
        append_log(
            config,
            f"create topic={signal.title!r} slug={key} weekly_issue_count={weekly_count} "
            f"threshold={config.min_weekly_issues}/{config.lookback_days}d",
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_hub(signal, key, config), encoding="utf-8")
        add_topic_to_registry(config.registry_path, key, signal)
        assigned = assign_topic_to_weeks(root, signal)
        append_log(
            config,
            json.dumps(
                {
                    "event": "promote-topic",
                    "topic": signal.title,
                    "slug": key,
                    "evidence_weeks": sorted(signal.weeks),
                    "sources": sorted(signal.sources),
                    "supporting_signals": signal.supporting_signals,
                    "assigned_paths": [path.relative_to(root).as_posix() for path in assigned],
                },
                sort_keys=True,
            ),
        )
        created.append(target)

    current_assignments = assign_promoted_topics_from_sources(root, config.registry_path)
    if current_assignments:
        append_log(
            config,
            json.dumps(
                {
                    "event": "assign-promoted-topics",
                    "assigned_paths": [
                        path.relative_to(root).as_posix() for path in current_assignments
                    ],
                },
                sort_keys=True,
            ),
        )
    if created or current_assignments:
        update_taxonomy_registries(root=root, config_path=config_path)
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
