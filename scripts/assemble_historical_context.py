#!/usr/bin/env python3
"""Assemble bounded historical context for weekly analysis prompts."""

# NOTE: This module coexists with scripts/context_budget.py (the older CLI-oriented
# budget engine). This module is canonical for pipeline-integrated historical context
# assembly used by analyze_fallback.py. The older module remains for standalone CLI use.

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTENT_ROOT = ROOT / "content"
DEFAULT_MAX_WORDS = 1_500
DEFAULT_PROMPT_BUDGET_FRACTION = 0.15

SECTION_PRIORITY = ("rolling", "previous_week", "monthly", "yearly")

SECTION_SPECS = {
    "rolling": {"label": "Rolling Last 4 Weeks", "target_words": 500, "min_words": 250},
    "previous_week": {"label": "Previous Week Takeaways", "target_words": 200, "min_words": 100},
    "monthly": {"label": "Month In Progress", "target_words": 200, "min_words": 100},
    "yearly": {"label": "Yearly Narrative", "target_words": 500, "min_words": 150},
}

FRONTMATTER_PATTERN = re.compile(r"^---\n(?P<frontmatter>.*?)\n---\n?(?P<body>.*)\Z", re.DOTALL)


@dataclass(frozen=True)
class HistoricalContextSection:
    key: str
    label: str
    source_path: str | None
    words: int
    token_estimate: int
    content: str


@dataclass(frozen=True)
class HistoricalContextResult:
    markdown: str
    sections: tuple[HistoricalContextSection, ...]
    max_words: int
    max_tokens: int
    word_count: int
    token_estimate: int


@dataclass
class _SectionPlan:
    key: str
    label: str
    source_path: Path | None
    raw_content: str
    target_words: int
    min_words: int
    current_words: int


def estimate_tokens(text: str) -> int:
    return (len(text.encode("utf-8")) + 3) // 4


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def compress_to_budget(text: str, max_words: int) -> str:
    if not text or max_words <= 0:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text.strip()

    lines = text.strip().splitlines()
    result_lines: list[str] = []
    total_words = 0
    for line in lines:
        line_words = len(line.split())
        if total_words + line_words > max_words:
            remaining = max_words - total_words
            if remaining > 0:
                partial = " ".join(line.split()[:remaining])
                result_lines.append(partial + "…")
            elif not result_lines:
                result_lines.append(" ".join(words[:max_words]) + "…")
            break
        result_lines.append(line)
        total_words += line_words
    return "\n".join(result_lines)


def _read_text(path: Path | None) -> str:
    if path is None or not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _strip_frontmatter(markdown: str) -> str:
    match = FRONTMATTER_PATTERN.match(markdown.strip())
    return match.group("body").strip() if match else markdown.strip()


def _frontmatter_value(markdown: str, key: str) -> str:
    match = FRONTMATTER_PATTERN.match(markdown.strip())
    if not match:
        return ""
    for line in match.group("frontmatter").splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        raw_key, value = line.split(":", 1)
        if raw_key.strip() == key:
            return value.strip().strip('"').strip("'")
    return ""


def _extract_markdown_section(markdown: str, heading: str) -> str:
    content = _strip_frontmatter(markdown)
    lines = content.splitlines()
    capture = False
    result: list[str] = []
    heading_pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE)
    next_section_pattern = re.compile(r"^##\s+")

    for line in lines:
        if heading_pattern.match(line):
            capture = True
            result.append(line)
            continue
        if capture and next_section_pattern.match(line):
            break
        if capture:
            result.append(line)
    return "\n".join(result).strip()


def _join_nonempty(parts: Iterable[str]) -> str:
    return "\n\n".join(part.strip() for part in parts if part and part.strip())


def _extract_previous_week_takeaways(markdown: str) -> str:
    summary = _frontmatter_value(markdown, "summary")
    parts: list[str] = []
    if summary:
        parts.append(f"- Prior weekly thesis: {summary}")
    parts.extend(
        section
        for section in (
            _extract_markdown_section(markdown, "Signal & Noise"),
            _extract_markdown_section(markdown, "Blind Spots"),
            _extract_markdown_section(markdown, "The Week Ahead"),
        )
        if section
    )
    return _join_nonempty(parts) or _strip_frontmatter(markdown)


def _extract_month_notes(markdown: str) -> str:
    return _join_nonempty(
        section
        for section in (
            _extract_markdown_section(markdown, "Month Overview"),
            _extract_markdown_section(markdown, "Trends Observed"),
            _extract_markdown_section(markdown, "Key Takeaways"),
        )
        if section
    ) or _strip_frontmatter(markdown)


def _extract_yearly_narrative(markdown: str) -> str:
    narrative = _extract_markdown_section(markdown, "Narrative")
    if narrative:
        arc = _extract_markdown_section(markdown, "Arc")
        return _join_nonempty(section for section in (narrative, arc) if section)
    return _join_nonempty(
        section
        for section in (
            _extract_markdown_section(markdown, "Year in Review"),
            _extract_markdown_section(markdown, "Biggest Trends"),
            _extract_markdown_section(markdown, "Predictions Review"),
        )
        if section
    ) or _strip_frontmatter(markdown)


def _parse_current_datetime(value: str) -> datetime | None:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _resolve_month_path(content_root: Path, current_datetime: str) -> Path | None:
    monthly_dir = content_root / "monthly"
    if not monthly_dir.exists():
        return None

    dt = _parse_current_datetime(current_datetime)
    target_year = dt.year if dt else None
    target_month = dt.month if dt else None

    candidates: list[tuple[int, int, Path]] = []
    for path in sorted(monthly_dir.glob("*/*.md")):
        try:
            year = int(path.parent.name)
            month = int(path.stem)
        except ValueError:
            continue
        candidates.append((year, month, path))

    if not candidates:
        return None

    if target_year is not None and target_month is not None:
        eligible = [item for item in candidates if (item[0], item[1]) <= (target_year, target_month)]
        if eligible:
            return eligible[-1][2]
    return candidates[-1][2]


def _resolve_year_path(content_root: Path, current_datetime: str) -> Path | None:
    yearly_dir = content_root / "yearly"
    if not yearly_dir.exists():
        return None
    dt = _parse_current_datetime(current_datetime)
    if dt:
        exact = yearly_dir / f"{dt.year}.md"
        if exact.exists():
            return exact
    candidates = sorted(path for path in yearly_dir.glob("*.md") if path.stem.isdigit())
    return candidates[-1] if candidates else None


def _build_plans(
    *,
    current_datetime: str,
    previous_summary_path: Path | None,
    content_root: Path,
) -> list[_SectionPlan]:
    rolling_path = content_root / "rolling" / "last-month.md"
    monthly_path = _resolve_month_path(content_root, current_datetime)
    yearly_path = _resolve_year_path(content_root, current_datetime)

    extracted = {
        "rolling": _strip_frontmatter(_read_text(rolling_path)),
        "previous_week": _extract_previous_week_takeaways(_read_text(previous_summary_path)),
        "monthly": _extract_month_notes(_read_text(monthly_path)),
        "yearly": _extract_yearly_narrative(_read_text(yearly_path)),
    }
    source_paths = {
        "rolling": rolling_path if rolling_path.exists() else None,
        "previous_week": previous_summary_path if previous_summary_path and previous_summary_path.exists() else None,
        "monthly": monthly_path if monthly_path and monthly_path.exists() else None,
        "yearly": yearly_path if yearly_path and yearly_path.exists() else None,
    }

    plans: list[_SectionPlan] = []
    for key in SECTION_PRIORITY:
        raw_content = extracted[key].strip()
        if not raw_content:
            continue
        spec = SECTION_SPECS[key]
        plans.append(
            _SectionPlan(
                key=key,
                label=str(spec["label"]),
                source_path=source_paths[key],
                raw_content=raw_content,
                target_words=int(spec["target_words"]),
                min_words=int(spec["min_words"]),
                current_words=min(word_count(raw_content), int(spec["target_words"])),
            )
        )
    return plans


def _render_sections(plans: Iterable[_SectionPlan]) -> tuple[str, tuple[HistoricalContextSection, ...]]:
    rendered_sections: list[str] = []
    metadata: list[HistoricalContextSection] = []
    for plan in plans:
        if plan.current_words <= 0:
            continue
        content = compress_to_budget(plan.raw_content, plan.current_words)
        if not content:
            continue
        rendered_sections.append(f"### {plan.label}\n\n{content}")
        metadata.append(
            HistoricalContextSection(
                key=plan.key,
                label=plan.label,
                source_path=plan.source_path.as_posix() if plan.source_path else None,
                words=word_count(content),
                token_estimate=estimate_tokens(content),
                content=content,
            )
        )
    return "\n\n".join(rendered_sections).strip(), tuple(metadata)


def _reduce_plans(
    plans: list[_SectionPlan],
    *,
    max_words: int,
    max_tokens: int,
) -> tuple[str, tuple[HistoricalContextSection, ...]]:
    if not plans:
        return "", ()

    for _ in range(400):
        rendered, metadata = _render_sections(plans)
        if not rendered:
            return "", ()
        if word_count(rendered) <= max_words and estimate_tokens(rendered) <= max_tokens:
            return rendered, metadata

        reduced = False
        for key in reversed(SECTION_PRIORITY):
            for plan in plans:
                if plan.key != key or plan.current_words <= 0:
                    continue
                floor = 0 if plan.current_words <= plan.min_words else plan.min_words
                step = 50 if plan.current_words - floor > 100 else 25
                next_words = max(floor, plan.current_words - step)
                if next_words == plan.current_words and floor == 0:
                    next_words = 0
                if next_words < plan.current_words:
                    plan.current_words = next_words
                    reduced = True
                    break
            if reduced:
                break
        if not reduced:
            break

    return _render_sections(plans)


def build_historical_context(
    *,
    current_datetime: str,
    previous_summary_path: Path | None,
    content_root: Path = DEFAULT_CONTENT_ROOT,
    max_words: int = DEFAULT_MAX_WORDS,
    prompt_token_budget: int = 90_000,
    prompt_budget_fraction: float = DEFAULT_PROMPT_BUDGET_FRACTION,
) -> HistoricalContextResult:
    max_tokens = max(0, int(prompt_token_budget * prompt_budget_fraction))
    if max_words <= 0 or max_tokens <= 0:
        return HistoricalContextResult("", (), max_words, max_tokens, 0, 0)

    plans = _build_plans(
        current_datetime=current_datetime,
        previous_summary_path=previous_summary_path,
        content_root=content_root,
    )
    rendered, sections = _reduce_plans(plans, max_words=max_words, max_tokens=max_tokens)
    return HistoricalContextResult(
        markdown=rendered,
        sections=sections,
        max_words=max_words,
        max_tokens=max_tokens,
        word_count=word_count(rendered),
        token_estimate=estimate_tokens(rendered),
    )


def assemble_historical_context(
    *,
    current_datetime: str,
    previous_summary_path: Path | None,
    content_root: Path = DEFAULT_CONTENT_ROOT,
    max_words: int = DEFAULT_MAX_WORDS,
    prompt_token_budget: int = 90_000,
    prompt_budget_fraction: float = DEFAULT_PROMPT_BUDGET_FRACTION,
) -> str:
    return build_historical_context(
        current_datetime=current_datetime,
        previous_summary_path=previous_summary_path,
        content_root=content_root,
        max_words=max_words,
        prompt_token_budget=prompt_token_budget,
        prompt_budget_fraction=prompt_budget_fraction,
    ).markdown


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble bounded historical context for weekly analysis prompts.")
    parser.add_argument("--current-datetime", required=True, help="ISO-8601 timestamp for the current analysis run.")
    parser.add_argument("--previous-summary", type=Path, default=None, help="Path to the previous week's markdown summary.")
    parser.add_argument("--content-root", type=Path, default=DEFAULT_CONTENT_ROOT, help="Path to the content/ root.")
    parser.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS, help="Maximum total historical-context words.")
    parser.add_argument(
        "--prompt-token-budget",
        type=int,
        default=90_000,
        help="Total prompt-token budget used to derive the 15%% historical-context ceiling.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_historical_context(
        current_datetime=args.current_datetime,
        previous_summary_path=args.previous_summary,
        content_root=args.content_root,
        max_words=args.max_words,
        prompt_token_budget=args.prompt_token_budget,
    )
    if result.markdown:
        print(result.markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
