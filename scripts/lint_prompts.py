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

# Variables that are allowed without fencing because they come from local
# squad-controlled files (wisdom, skills).  They still need the closing
# security constraint to be present in the template.
SEMI_TRUSTED_VARIABLES = frozenset(
    {
        "{{WISDOM}}",
        "{{SKILLS}}",
        "{{WISDOM_CONTENT}}",
        "{{TOPIC_NAME}}",
        "{{TOPIC_DESCRIPTION}}",
    }
)

# Variables that MUST be inside <untrusted-content> blocks.
UNTRUSTED_VARIABLES = frozenset(
    {
        "{{RAW_JSON_CONTENT}}",
        "{{PREVIOUS_SUMMARY_CONTENT_OR_EMPTY}}",
        "{{RECENT_ANALYSES}}",
        "{{SNAPSHOT_CONTEXT}}",
        "{{SCORECARD}}",
    }
)

CLOSING_CONSTRAINT_PATTERN = re.compile(
    r"##\s+closing\s+security\s+constraint", re.IGNORECASE
)

UNTRUSTED_OPEN = "<untrusted-content>"
UNTRUSTED_CLOSE = "</untrusted-content>"


def _find_unfenced_variables(content: str) -> list[str]:
    """Return untrusted variables that appear outside <untrusted-content> blocks."""
    unfenced: list[str] = []

    # Find all untrusted-content blocks
    fenced_ranges: list[tuple[int, int]] = []
    open_pattern = re.compile(re.escape(UNTRUSTED_OPEN))
    close_pattern = re.compile(re.escape(UNTRUSTED_CLOSE))

    for m in open_pattern.finditer(content):
        start = m.start()
        close_match = close_pattern.search(content, m.end())
        if close_match:
            fenced_ranges.append((start, close_match.end()))

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

    # Check untrusted variables are inside fenced blocks
    unfenced = _find_unfenced_variables(content)
    for var in unfenced:
        errors.append(
            f"{path}: untrusted variable {var} is not inside "
            f"<untrusted-content> boundary tags"
        )

    # Check that {format_style} variables (single-brace) in press-context are fenced
    if "press-context" in path.name:
        for var_match in re.finditer(r"\{(articles_list|correlations_list)\}", content):
            # These should be inside untrusted-content blocks
            pos = var_match.start()
            fenced_ranges: list[tuple[int, int]] = []
            for m in re.finditer(re.escape(UNTRUSTED_OPEN), content):
                close_match = re.search(
                    re.escape(UNTRUSTED_CLOSE), content[m.end() :]
                )
                if close_match:
                    fenced_ranges.append((m.start(), m.end() + close_match.end()))
            if not any(start <= pos <= end for start, end in fenced_ranges):
                errors.append(
                    f"{path}: untrusted variable {{{var_match.group(1)}}} "
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
