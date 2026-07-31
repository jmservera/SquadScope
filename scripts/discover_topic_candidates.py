#!/usr/bin/env python3
"""Build deterministic noncanonical topic evidence from weekly pipeline artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.manage_topic_hubs import safe_candidate_title, slugify

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "observatory.toml"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "taxonomy" / "topic-candidates.json"
WEEK_RE = re.compile(r"(?P<year>\d{4})-W(?P<week>\d{2})")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<frontmatter>.*?)\n---\n", re.DOTALL)
BOLD_HEADING_RE = re.compile(r"^\*\*(?P<title>[^*]+)\*\*", re.MULTILINE)


@dataclass
class CandidateEvidence:
    labels: set[str] = field(default_factory=set)
    weeks: set[str] = field(default_factory=set)
    sources: dict[tuple[str, str, str], dict[str, Any]] = field(default_factory=dict)
    support: dict[tuple[str, str, str], dict[str, Any]] = field(default_factory=dict)


def parse_week_date(week: str) -> date:
    """Return the Monday for an ISO week label."""
    match = WEEK_RE.fullmatch(week)
    if not match:
        raise ValueError(f"Invalid ISO week: {week}")
    return date.fromisocalendar(int(match.group("year")), int(match.group("week")), 1)


def week_from_path(path: Path) -> str | None:
    """Extract an ISO week from a source path."""
    match = WEEK_RE.search(path.name)
    return match.group(0) if match else None


def load_settings(config_path: Path) -> tuple[int, int, set[str], int]:
    """Load candidate and recurring-repository thresholds."""
    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    dynamic = raw.get("topic_hubs", {}).get("dynamic_creation", {})
    repo_pages = raw.get("repo_pages", {})
    return (
        int(dynamic["min_weekly_issues"]),
        int(dynamic["lookback_days"]),
        {slugify(str(value)) for value in dynamic.get("ignore_topics", [])},
        int(repo_pages.get("recurrence_threshold_distinct_weekly_issues", 3)) + 1,
    )


def canonical_keys(registry_path: Path) -> set[str]:
    """Return slugs for every canonical title and alias."""
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    terms = payload.get("terms", {}) if isinstance(payload, dict) else {}
    keys: set[str] = set()
    if not isinstance(terms, dict):
        return keys
    for slug, raw in terms.items():
        if not isinstance(raw, dict) or not (raw.get("is_hub") or raw.get("promoted")):
            continue
        keys.add(slugify(str(slug)))
        keys.add(slugify(str(raw.get("display_name") or "")))
        keys.update(slugify(str(alias)) for alias in raw.get("aliases", []))
    return keys


def _display_name(labels: set[str]) -> str:
    label = sorted(labels, key=lambda value: (len(value), value.lower()))[0]
    if "-" not in label and "_" not in label:
        return label
    words = re.split(r"[-_]+", label)
    abbreviations = {"ai": "AI", "llm": "LLM", "mcp": "MCP", "api": "API"}
    return " ".join(abbreviations.get(word.lower(), word.capitalize()) for word in words)


def _record(
    evidence: dict[str, CandidateEvidence],
    *,
    label: object,
    week: str,
    source_type: str,
    source_path: Path,
    canonical: set[str],
    ignored: set[str],
    count: int | None = None,
) -> str | None:
    title = safe_candidate_title(label)
    if not title:
        return None
    slug = slugify(title)
    if not slug or slug in canonical or slug in ignored:
        return None
    candidate = evidence[slug]
    candidate.labels.add(title)
    candidate.weeks.add(week)
    source = {
        "week": week,
        "source_type": source_type,
        "source_path": source_path.as_posix(),
        "signal": title,
    }
    if count is not None:
        source["count"] = count
    candidate.sources[(week, source_type, source_path.as_posix())] = source
    if source_type in {"summary_tag", "summary_heading"}:
        candidate.support[(week, "analysis-summary", source_path.as_posix())] = {
            "week": week,
            "support_type": "analysis-summary",
            "source_path": source_path.as_posix(),
            "detail": title,
        }
    return slug


def _frontmatter(path: Path) -> dict[str, Any]:
    document = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(document)
    if not match:
        return {}
    parsed = yaml.safe_load(match.group("frontmatter"))
    return parsed if isinstance(parsed, dict) else {}


def discover_candidates(
    *,
    root: Path = PROJECT_ROOT,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """Discover noncanonical candidates and return a byte-stable payload."""
    config = config_path or root / "config" / "observatory.toml"
    min_weeks, lookback_days, ignored, recurring_repo_weeks = load_settings(config)
    registry_path = root / "data" / "taxonomy" / "topics.json"
    canonical = canonical_keys(registry_path)
    evidence: dict[str, CandidateEvidence] = defaultdict(CandidateEvidence)
    raw_repos: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    raw_repo_topics: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    raw_paths: dict[str, Path] = {}

    source_paths = sorted((root / "content" / "weekly").glob("**/*.md"))
    summary_paths = sorted((root / "data" / "analyzed").glob("*-summary.md"))
    raw_paths_list = sorted((root / "data" / "raw").glob("*.json"))
    weeks = [
        week
        for path in [*source_paths, *summary_paths, *raw_paths_list]
        if (week := week_from_path(path))
    ]
    if not weeks:
        return {"schema_version": 1, "policy": {}, "candidates": {}}
    latest_week = max(weeks, key=parse_week_date)
    cutoff = parse_week_date(latest_week) - timedelta(days=lookback_days)

    def in_window(week: str) -> bool:
        return parse_week_date(week) >= cutoff

    for path in source_paths:
        week = week_from_path(path)
        if not week or not in_window(week):
            continue
        for tag in _frontmatter(path).get("tags", []):
            _record(
                evidence,
                label=tag,
                week=week,
                source_type="weekly_tag",
                source_path=path.relative_to(root),
                canonical=canonical,
                ignored=ignored,
            )

    for path in summary_paths:
        week = week_from_path(path)
        if not week or not in_window(week):
            continue
        relative = path.relative_to(root)
        for tag in _frontmatter(path).get("tags", []):
            _record(
                evidence,
                label=tag,
                week=week,
                source_type="summary_tag",
                source_path=relative,
                canonical=canonical,
                ignored=ignored,
            )
        document = path.read_text(encoding="utf-8")
        for heading in BOLD_HEADING_RE.findall(document):
            _record(
                evidence,
                label=heading.rstrip(".?!"),
                week=week,
                source_type="summary_heading",
                source_path=relative,
                canonical=canonical,
                ignored=ignored,
            )

    for path in raw_paths_list:
        week = week_from_path(path)
        if not week or not in_window(week) or path.name.endswith("-external-news.json"):
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(root)
        raw_paths[week] = relative
        signals = payload.get("signals", {}) if isinstance(payload, dict) else {}
        for item in signals.get("top_topics", []) if isinstance(signals, dict) else []:
            if isinstance(item, dict):
                _record(
                    evidence,
                    label=item.get("topic"),
                    week=week,
                    source_type="raw_top_topic",
                    source_path=relative,
                    canonical=canonical,
                    ignored=ignored,
                    count=int(item.get("count") or 0),
                )
        for bucket in ("new_repos", "trending_repos"):
            for repo in payload.get(bucket, []) if isinstance(payload, dict) else []:
                if not isinstance(repo, dict) or not isinstance(repo.get("topics"), list):
                    continue
                repo_name = str(repo.get("full_name") or "")
                for topic in repo["topics"]:
                    slug = _record(
                        evidence,
                        label=topic,
                        week=week,
                        source_type="raw_repo_topic",
                        source_path=relative,
                        canonical=canonical,
                        ignored=ignored,
                    )
                    if slug and repo_name:
                        raw_repos[slug][repo_name].add(week)
                        raw_repo_topics[week][repo_name].add(slug)

    for slug, repos in raw_repos.items():
        for repo_name, repo_weeks in sorted(repos.items()):
            if len(repo_weeks) < recurring_repo_weeks:
                continue
            candidate = evidence[slug]
            candidate.support[(min(repo_weeks), "recurring-repository-cluster", repo_name)] = {
                "week": max(repo_weeks),
                "support_type": "recurring-repository-cluster",
                "source_path": raw_paths[max(repo_weeks)].as_posix(),
                "detail": repo_name,
                "evidence_weeks": sorted(repo_weeks),
            }

    for path in sorted((root / "data" / "analyzed").glob("*-correlations.json")):
        week = week_from_path(path)
        if not week or not in_window(week):
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for correlation in payload.get("correlations", []) if isinstance(payload, dict) else []:
            if not isinstance(correlation, dict) or correlation.get("confidence_label") != "strong":
                continue
            repo_name = str(correlation.get("repo_key") or correlation.get("repo") or "")
            for slug in sorted(raw_repo_topics[week].get(repo_name, set())):
                evidence[slug].support[(week, "strong-press-correlation", repo_name)] = {
                    "week": week,
                    "support_type": "strong-press-correlation",
                    "source_path": path.relative_to(root).as_posix(),
                    "detail": repo_name,
                }

    candidates: dict[str, Any] = {}
    for slug, candidate in sorted(evidence.items()):
        supporting = sorted(
            candidate.support.values(),
            key=lambda item: (item["week"], item["support_type"], item["source_path"]),
        )
        display_name = _display_name(candidate.labels)
        if not safe_candidate_title(display_name):
            continue
        candidates[slug] = {
            "display_name": display_name,
            "slug": slug,
            "aliases": sorted(candidate.labels, key=str.lower),
            "first_seen_week": min(candidate.weeks),
            "last_seen_week": max(candidate.weeks),
            "weekly_issue_count": len(candidate.weeks),
            "evidence_weeks": sorted(candidate.weeks),
            "sources": sorted(
                candidate.sources.values(),
                key=lambda item: (item["week"], item["source_type"], item["source_path"]),
            ),
            "supporting_signals": supporting,
            "eligible": len(candidate.weeks) >= min_weeks and bool(supporting),
        }
    return {
        "schema_version": 1,
        "as_of_week": latest_week,
        "policy": {
            "min_weekly_issues": min_weeks,
            "lookback_days": lookback_days,
            "recurring_repository_weeks": recurring_repo_weeks,
        },
        "candidates": candidates,
    }


def render_registry(payload: dict[str, Any]) -> str:
    """Render candidate evidence as canonical JSON."""
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def update_candidate_registry(
    *,
    root: Path = PROJECT_ROOT,
    config_path: Path | None = None,
    output_path: Path | None = None,
    check: bool = False,
) -> bool:
    """Write candidate evidence and return whether the prior output was stale."""
    output = output_path or root / "data" / "taxonomy" / "topic-candidates.json"
    rendered = render_registry(discover_candidates(root=root, config_path=config_path))
    stale = not output.exists() or output.read_text(encoding="utf-8") != rendered
    if stale and not check:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return stale


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    return parser


def main() -> int:
    """Update or validate the candidate registry."""
    args = create_parser().parse_args()
    try:
        stale = update_candidate_registry(
            root=args.root,
            config_path=args.config,
            output_path=args.output,
            check=args.check,
        )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if args.check and stale:
        print("Topic candidate registry is stale.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
