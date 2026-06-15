#!/usr/bin/env python3
"""Lint prompt templates for missing untrusted-content guardrails.

Checks that every template variable injecting external text is fenced with
<untrusted-content> boundary markers and that a closing security constraint
is present at the end of each prompt.

Usage:
    python scripts/lint_prompts.py [--prompts-dir prompts/]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Template variables that carry controlled/trusted values (no fencing required).
TRUSTED_VARIABLES = frozenset(
    {
        "{{CURRENT_DATETIME}}",
        "{{CURRENT_WEEK}}",
        "{{CURRENT_YEAR}}",
        "{{OUTPUT_PATH}}",
        "{{RAW_JSON_PATH}}",
        "{{PREVIOUS_SUMMARY_PATH_OR_NONE}}",
        "{{TITLE_TEMPLATE_HINT}}",
        "{{TOPIC_ID}}",
    }
)

# Variables that carry locally-controlled short identifiers (e.g. topic name
# from the config file).  No fencing required, but the closing security
# constraint must still be present in the template.
SEMI_TRUSTED_VARIABLES = frozenset(
    {
        "{{TOPIC_NAME}}",
    }
)

# Variables that MUST be inside <untrusted-content> blocks.
UNTRUSTED_VARIABLES = frozenset(
    {
        "{{RAW_JSON_CONTENT}}",
        "{{HISTORICAL_CONTEXT}}",
        "{{PREVIOUS_SUMMARY_CONTENT_OR_EMPTY}}",
        "{{RECENT_ANALYSES}}",
        "{{SNAPSHOT_CONTEXT}}",
        "{{SCORECARD}}",
        "{{QUALITY_TREND}}",
        "{{WISDOM}}",
        "{{SKILLS}}",
        "{{CONTINUITY}}",
        "{{ARCHIVE_CONTEXT}}",
        "{{WISDOM_CONTENT}}",
        "{{TOPIC_DESCRIPTION}}",
    }
)

# Single-brace format variables that carry trusted/template-controlled values.
TRUSTED_FORMAT_VARIABLES = frozenset(
    {
        "article_count",
        "correlation_count",
        "date",
        "level",
        "topic_name",
    }
)

# Single-brace format variables that carry untrusted external content and MUST
# be inside <untrusted-content> blocks regardless of which template they appear in.
UNTRUSTED_FORMAT_VARIABLES = frozenset(
    {
        "articles_list",
        "correlations_list",
        "scorecard_summary",
    }
)

# All known variables for the unknown-variable check.
ALL_KNOWN_VARIABLES = TRUSTED_VARIABLES | SEMI_TRUSTED_VARIABLES | UNTRUSTED_VARIABLES
ALL_KNOWN_FORMAT_VARIABLES = TRUSTED_FORMAT_VARIABLES | UNTRUSTED_FORMAT_VARIABLES

CLOSING_CONSTRAINT_PATTERN = re.compile(
    r"##\s+closing\s+security\s+constraint", re.IGNORECASE
)

UNTRUSTED_OPEN = "<untrusted-content>"
UNTRUSTED_CLOSE = "</untrusted-content>"


def _find_fenced_ranges(content: str) -> list[tuple[int, int]]:
    fenced_ranges: list[tuple[int, int]] = []
    open_pattern = re.compile(re.escape(UNTRUSTED_OPEN))
    close_pattern = re.compile(re.escape(UNTRUSTED_CLOSE))

    for match in open_pattern.finditer(content):
        close_match = close_pattern.search(content, match.end())
        if close_match:
            fenced_ranges.append((match.start(), close_match.end()))

    return fenced_ranges


def _find_unfenced_variables(content: str) -> list[str]:
    """Return untrusted variables that appear outside <untrusted-content> blocks."""
    unfenced: list[str] = []

    fenced_ranges = _find_fenced_ranges(content)

    def _is_fenced(pos: int) -> bool:
        return any(start <= pos <= end for start, end in fenced_ranges)

    # Check each untrusted variable
    for var in UNTRUSTED_VARIABLES:
        for m in re.finditer(re.escape(var), content):
            if not _is_fenced(m.start()):
                unfenced.append(var)
                break  # report each variable only once

    return unfenced


def lint_prompt(path: Path) -> list[str]:
    """Lint a single prompt file. Returns list of error messages."""
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []

    # Check for closing security constraint
    if not CLOSING_CONSTRAINT_PATTERN.search(content):
        errors.append(f"{path}: missing '## Closing security constraint' section")

    # Check for unknown/unclassified template variables
    all_vars = set(re.findall(r"\{\{[A-Z][A-Z_]*\}\}", content))
    unknown_vars = all_vars - ALL_KNOWN_VARIABLES
    # Exclude conditional block markers like {{#IF_TOPIC}} / {{/IF_TOPIC}}
    for var in sorted(unknown_vars):
        errors.append(
            f"{path}: unknown variable {var} is not classified as "
            f"trusted/semi-trusted/untrusted in lint_prompts.py"
        )

    fenced_ranges = _find_fenced_ranges(content)

    def _is_fenced(pos: int) -> bool:
        return any(start <= pos <= end for start, end in fenced_ranges)

    # Check untrusted variables are inside fenced blocks
    unfenced = _find_unfenced_variables(content)
    for var in unfenced:
        errors.append(
            f"{path}: untrusted variable {var} is not inside "
            f"<untrusted-content> boundary tags"
        )

    # Check for unknown single-brace format variables and ensure untrusted ones are fenced.
    for var_match in re.finditer(r"\{([a-z_]+)\}", content):
        var_name = var_match.group(1)
        pos = var_match.start()
        if var_name not in ALL_KNOWN_FORMAT_VARIABLES:
            errors.append(
                f"{path}: unknown format variable {{{var_name}}} is not classified as "
                f"trusted/untrusted in lint_prompts.py"
            )
            continue
        if var_name in UNTRUSTED_FORMAT_VARIABLES and not _is_fenced(pos):
            errors.append(
                f"{path}: untrusted variable {{{var_name}}} "
                f"is not inside <untrusted-content> boundary tags"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint prompt templates for security guardrails")
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=Path("prompts"),
        help="Directory containing prompt templates",
    )
    args = parser.parse_args(argv)

    prompts_dir: Path = args.prompts_dir
    if not prompts_dir.exists():
        print(f"ERROR: prompts directory not found: {prompts_dir}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for prompt_file in sorted(prompts_dir.glob("*.md")):
        all_errors.extend(lint_prompt(prompt_file))

    if all_errors:
        for err in all_errors:
            print(f"FAIL: {err}", file=sys.stderr)
        print(f"\n{len(all_errors)} prompt security issue(s) found.", file=sys.stderr)
        return 1

    print("All prompt templates pass security lint checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
