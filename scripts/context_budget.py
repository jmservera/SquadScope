#!/usr/bin/env python3
"""Context-budget compression engine for historical summaries.

Assembles rolling, yearly, previous-week, and monthly context into a single
markdown string suitable for LLM prompt injection, respecting a total word
budget with per-section allocations.

Pruning rules:
  - Predictions unconfirmed after 8 weeks → drop
  - Trends with 0 signal for 4 weeks → compress to one sentence
  - Noise patterns → keep only top 3

CLI:
    python scripts/context_budget.py --rolling path --yearly path [--prev-week path] [--max-words 1500]
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


# Default budget allocations (words)
BUDGET_ROLLING = 500
BUDGET_PREV_WEEK = 200
BUDGET_YEARLY = 500
BUDGET_MONTH = 300

STALE_PREDICTION_WEEKS = 8
STALE_TREND_WEEKS = 4
MAX_NOISE_PATTERNS = 3


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def compress_to_budget(text: str, max_words: int) -> str:
    """Truncate/summarize text to fit within a word budget.

    Preserves complete lines where possible, trimming from the end.
    Returns the compressed text ending with '...' if truncated.
    """
    if not text or not text.strip():
        return ""
    if max_words <= 0:
        return ""

    words = text.split()
    if len(words) <= max_words:
        return text.strip()

    # Preserve line structure: keep complete lines until budget
    lines = text.strip().splitlines()
    result_lines: list[str] = []
    total_words = 0
    for line in lines:
        line_words = len(line.split())
        if total_words + line_words > max_words:
            # Partial last line if we have room
            remaining = max_words - total_words
            if remaining > 0:
                partial = " ".join(line.split()[:remaining])
                result_lines.append(partial + "...")
            elif not result_lines:
                # Edge case: first line exceeds budget
                result_lines.append(" ".join(words[:max_words]) + "...")
            break
        result_lines.append(line)
        total_words += line_words

    return "\n".join(result_lines)


def _parse_date_from_line(line: str) -> Optional[datetime]:
    """Try to extract a date from a line like '- [2026-01-15] ...'."""
    match = re.search(r"\[(\d{4}-\d{2}-\d{2})\]", line)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return None
    return None


def prune_stale_predictions(text: str, now: Optional[datetime] = None) -> str:
    """Drop predictions unconfirmed after 8 weeks."""
    if not text:
        return ""
    if now is None:
        now = datetime.now(timezone.utc)

    cutoff = now - timedelta(weeks=STALE_PREDICTION_WEEKS)
    lines = text.splitlines()
    result: list[str] = []

    for line in lines:
        # Predictions are bullet lines with dates and no confirmation marker
        if re.match(r"\s*[-*]\s*\[", line):
            date = _parse_date_from_line(line)
            if date and date < cutoff:
                # Check for confirmation markers
                lower = line.lower()
                if "confirmed" not in lower and "✓" not in line and "✅" not in line:
                    continue  # Drop stale unconfirmed prediction
        result.append(line)

    return "\n".join(result)


def compress_stale_trends(text: str, now: Optional[datetime] = None) -> str:
    """Compress trends with 0 signal for 4+ weeks to one sentence."""
    if not text:
        return ""
    if now is None:
        now = datetime.now(timezone.utc)

    cutoff = now - timedelta(weeks=STALE_TREND_WEEKS)
    lines = text.splitlines()
    result: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # Detect trend blocks: "### Trend: <name>" or "## Trend: <name>"
        trend_match = re.match(r"(#{2,3})\s+[Tt]rend:\s*(.+)", line)
        if trend_match:
            heading_level = trend_match.group(1)
            trend_name = trend_match.group(2).strip()
            # Collect the trend block
            block_lines = [line]
            i += 1
            has_recent_signal = False
            while i < len(lines) and not re.match(r"#{2,3}\s+", lines[i]):
                block_lines.append(lines[i])
                # Check for recent signals
                date = _parse_date_from_line(lines[i])
                if date and date >= cutoff:
                    has_recent_signal = True
                # Non-dated content counts as signal
                if lines[i].strip() and not lines[i].startswith("#"):
                    if "no signal" in lines[i].lower() or "0 signal" in lines[i].lower():
                        pass
                    elif date is None and lines[i].strip().startswith(("-", "*")):
                        has_recent_signal = True
                i += 1

            if has_recent_signal:
                result.extend(block_lines)
            else:
                # Compress to one sentence
                result.append(f"- {trend_name}: no recent signal (stale)")
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def keep_top_noise_patterns(text: str, max_patterns: int = MAX_NOISE_PATTERNS) -> str:
    """Keep only the top N noise patterns from a noise section."""
    if not text:
        return ""

    lines = text.splitlines()
    result: list[str] = []
    in_noise_section = False
    noise_count = 0

    for line in lines:
        # Detect noise section headers
        if re.match(r"#{2,3}\s+[Nn]oise", line):
            in_noise_section = True
            noise_count = 0
            result.append(line)
            continue

        if in_noise_section:
            # New section starts
            if re.match(r"#{2,3}\s+", line) and not re.match(r"#{2,3}\s+[Nn]oise", line):
                in_noise_section = False
                result.append(line)
                continue

            # Count bullet items
            if re.match(r"\s*[-*]\s+", line):
                noise_count += 1
                if noise_count <= max_patterns:
                    result.append(line)
                continue

            result.append(line)
        else:
            result.append(line)

    return "\n".join(result)


def _read_file_safe(path: Optional[Path]) -> str:
    """Read a file, returning empty string if missing or unreadable."""
    if path is None:
        return ""
    try:
        return Path(path).read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, OSError):
        return ""


def assemble_historical_context(
    rolling_path: Optional[str] = None,
    yearly_path: Optional[str] = None,
    prev_week_path: Optional[str] = None,
    month_path: Optional[str] = None,
    max_total_words: int = 1500,
    now: Optional[datetime] = None,
) -> str:
    """Assemble context from multiple sources within budget.

    Budget allocation:
      - rolling: 500 words
      - prev_week: 200 words
      - yearly: 500 words
      - month: 300 words

    Total is capped at max_total_words (default 1500).
    Returns a single markdown string for LLM prompt injection.
    """
    # Scale budgets if max_total_words differs from default
    default_total = BUDGET_ROLLING + BUDGET_PREV_WEEK + BUDGET_YEARLY + BUDGET_MONTH
    scale = max_total_words / default_total if default_total > 0 else 1.0

    budget_rolling = int(BUDGET_ROLLING * scale)
    budget_prev_week = int(BUDGET_PREV_WEEK * scale)
    budget_yearly = int(BUDGET_YEARLY * scale)
    budget_month = int(BUDGET_MONTH * scale)

    # Read sources
    rolling_raw = _read_file_safe(Path(rolling_path) if rolling_path else None)
    yearly_raw = _read_file_safe(Path(yearly_path) if yearly_path else None)
    prev_week_raw = _read_file_safe(Path(prev_week_path) if prev_week_path else None)
    month_raw = _read_file_safe(Path(month_path) if month_path else None)

    # Apply pruning rules
    rolling_pruned = keep_top_noise_patterns(
        compress_stale_trends(prune_stale_predictions(rolling_raw, now=now), now=now)
    )
    yearly_pruned = prune_stale_predictions(yearly_raw, now=now)
    prev_week_pruned = prev_week_raw
    month_pruned = compress_stale_trends(
        prune_stale_predictions(month_raw, now=now), now=now
    )

    # Compress each section to its budget
    rolling_compressed = compress_to_budget(rolling_pruned, budget_rolling)
    prev_week_compressed = compress_to_budget(prev_week_pruned, budget_prev_week)
    yearly_compressed = compress_to_budget(yearly_pruned, budget_yearly)
    month_compressed = compress_to_budget(month_pruned, budget_month)

    # Assemble final markdown
    sections: list[str] = []

    if rolling_compressed:
        sections.append(f"## Rolling Context\n\n{rolling_compressed}")
    if prev_week_compressed:
        sections.append(f"## Previous Week\n\n{prev_week_compressed}")
    if yearly_compressed:
        sections.append(f"## Yearly Context\n\n{yearly_compressed}")
    if month_compressed:
        sections.append(f"## Monthly Context\n\n{month_compressed}")

    assembled = "\n\n".join(sections)

    # Final enforcement: ensure total stays within max_total_words
    if word_count(assembled) > max_total_words:
        assembled = compress_to_budget(assembled, max_total_words)

    return assembled


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble historical context within a word budget."
    )
    parser.add_argument("--rolling", type=str, help="Path to rolling context file")
    parser.add_argument("--yearly", type=str, help="Path to yearly context file")
    parser.add_argument("--prev-week", type=str, help="Path to previous week file")
    parser.add_argument("--month", type=str, help="Path to monthly context file")
    parser.add_argument(
        "--max-words", type=int, default=1500, help="Maximum total words (default: 1500)"
    )

    args = parser.parse_args(argv)

    result = assemble_historical_context(
        rolling_path=args.rolling,
        yearly_path=args.yearly,
        prev_week_path=args.prev_week,
        month_path=args.month,
        max_total_words=args.max_words,
    )

    if result:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
