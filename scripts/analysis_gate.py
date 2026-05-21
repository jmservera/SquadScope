#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency on runners
    import yaml
except ImportError:  # pragma: no cover - exercised via fallback parser
    yaml = None

REQUIRED_FIELDS = [
    "title",
    "date",
    "week",
    "year",
    "tags",
    "categories",
    "repos_featured",
    "stars_tracked",
    "top_repo",
    "quality_score",
    "summary",
]
REQUIRED_HEADINGS = [
    "## This Week's Trends",
    "## Where Industry Meets Code",
    "## Signal & Noise",
    "## Blind Spots",
    "## The Week Ahead",
    "## Key References",
    "### Notable Projects",
    "### Press & Industry",
]
RAW_MARKERS = [
    "```json",
    '"week":',
    '"new_repos"',
    '"trending_repos"',
    "traceback (most recent call last)",
]
PLACEHOLDER_PATTERNS = [
    (re.compile(r"(?mi)^\s*(?:[-*]\s*)?todo\s*[:\-]"), "TODO placeholder marker"),
    (re.compile(r"(?mi)^\s*(?:[-*]\s*)?tbd\s*[:\-]"), "TBD placeholder marker"),
    (re.compile(r"(?i)\bplaceholder text\b"), "placeholder text"),
    (re.compile(r"(?i)\byour analysis here\b"), "placeholder instruction"),
]
WEEK_PATTERN = re.compile(r"^(?P<year>\d{4})-W(?P<week>\d{2})$")
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
HEADING_PATTERN = re.compile(r"(?m)^(#{2,3})\s+(.+?)\s*$")
WORD_PATTERN = re.compile(r"\b[\w'-]+\b")
TOP_REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")
GENERIC_TITLE_PATTERNS = [
    re.compile(r"^Week\s+\d+.*Analysis$", re.IGNORECASE),
    re.compile(r"^Week\s+\d+,\s*\d{4}$", re.IGNORECASE),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate weekly analysis output against the analysis spec.")
    parser.add_argument("--analysis-file", required=True, type=Path, help="Path to the rendered markdown summary.")
    parser.add_argument("--raw-json", required=True, type=Path, help="Path to the raw weekly payload.")
    parser.add_argument("--current-datetime", required=True, help="Current run timestamp in ISO 8601 format.")
    parser.add_argument("--source", default="unknown", help="Analysis source label for summaries.")
    return parser.parse_args(argv)


def parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        candidate = value.strip()
        if candidate.endswith("Z"):
            candidate = f"{candidate[:-1]}+00:00"
        parsed = datetime.fromisoformat(candidate)
    else:  # pragma: no cover - guarded by callers
        raise TypeError(f"Unsupported datetime value: {value!r}")
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def week_slug(value: datetime) -> str:
    year, week, _ = value.astimezone(UTC).isocalendar()
    return f"{year}-W{week:02d}"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Raw payload must be an object: {path}")
    return payload


def strip_quotes(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {'"', "'"}:
        return stripped[1:-1]
    return stripped


def parse_inline_list(value: str) -> list[str]:
    inner = value.strip()[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    for part in inner.split(","):
        item = strip_quotes(part)
        if not item:
            raise ValueError(f"Malformed YAML list entry: {value}")
        items.append(item)
    return items


def parse_frontmatter_fallback(text: str) -> dict[str, Any]:
    frontmatter: dict[str, Any] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith((" ", "\t")):
            raise ValueError(f"Unexpected indentation in frontmatter: {line}")
        if ":" not in line:
            raise ValueError(f"Malformed frontmatter line: {line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            raise ValueError(f"Malformed frontmatter key: {line}")
        if value == "":
            items: list[str] = []
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if not candidate.strip():
                    index += 1
                    continue
                if not candidate.startswith((" ", "\t")):
                    break
                stripped = candidate.strip()
                if not stripped.startswith("- "):
                    raise ValueError(f"Unsupported multiline frontmatter value for {key}: {candidate}")
                items.append(strip_quotes(stripped[2:]))
                index += 1
            frontmatter[key] = items
            continue
        if value.startswith("[") and value.endswith("]"):
            frontmatter[key] = parse_inline_list(value)
        else:
            scalar = strip_quotes(value)
            frontmatter[key] = int(scalar) if re.fullmatch(r"-?\d+", scalar) else scalar
        index += 1
    return frontmatter


def parse_frontmatter(text: str) -> dict[str, Any]:
    if yaml is not None:
        try:
            data = yaml.safe_load(text) or {}
        except Exception:
            data = parse_frontmatter_fallback(text)
        else:
            if not isinstance(data, dict):
                raise ValueError("YAML frontmatter must be a mapping.")
            return data
    return parse_frontmatter_fallback(text)


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        raise ValueError("Analysis output is missing YAML frontmatter.")
    frontmatter_text, body = match.groups()
    return parse_frontmatter(frontmatter_text), body


def validate_string_field(frontmatter: dict[str, Any], field: str, errors: list[str]) -> None:
    value = frontmatter.get(field)
    if value is None:
        return
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string.")


def validate_integer_field(frontmatter: dict[str, Any], field: str, errors: list[str], *, minimum: int = 0) -> None:
    value = frontmatter.get(field)
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{field} must be an integer.")
        return
    if value < minimum:
        errors.append(f"{field} must be at least {minimum}.")


def validate_string_list(
    frontmatter: dict[str, Any],
    field: str,
    errors: list[str],
    *,
    minimum: int | None = None,
    maximum: int | None = None,
    includes: str | None = None,
) -> None:
    value = frontmatter.get(field)
    if value is None:
        return
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{field} must be an array of strings.")
        return
    if minimum is not None and len(value) < minimum:
        errors.append(f"{field} must contain at least {minimum} items.")
    if maximum is not None and len(value) > maximum:
        errors.append(f"{field} must contain at most {maximum} items.")
    if includes is not None and includes not in value:
        errors.append(f"{field} must include {includes!r}.")


def find_missing_headings(body: str) -> list[str]:
    headings = [f"{level} {title.strip()}" for level, title in HEADING_PATTERN.findall(body)]
    missing: list[str] = []
    position = -1
    for required in REQUIRED_HEADINGS:
        try:
            position = headings.index(required, position + 1)
        except ValueError:
            missing.append(required)
    return missing


def validate_analysis(text: str, raw_payload: dict[str, Any], current_datetime: str) -> tuple[list[str], int]:
    errors: list[str] = []
    try:
        frontmatter, body = extract_frontmatter(text)
    except ValueError as exc:
        return [str(exc)], 0

    missing_fields = [field for field in REQUIRED_FIELDS if field not in frontmatter]
    if missing_fields:
        errors.append(f"Missing frontmatter fields: {', '.join(missing_fields)}")

    extra_fields = sorted(set(frontmatter) - set(REQUIRED_FIELDS))
    if extra_fields:
        errors.append(f"Unexpected frontmatter fields: {', '.join(extra_fields)}")

    validate_string_field(frontmatter, "title", errors)
    title = frontmatter.get("title")
    if isinstance(title, str) and title.strip():
        if any(pattern.fullmatch(title.strip()) for pattern in GENERIC_TITLE_PATTERNS):
            errors.append("title must not use a generic week/year placeholder format.")
    validate_string_field(frontmatter, "week", errors)
    validate_string_field(frontmatter, "top_repo", errors)
    validate_string_field(frontmatter, "summary", errors)
    validate_string_list(frontmatter, "tags", errors, minimum=3, maximum=8)
    validate_string_list(frontmatter, "categories", errors, includes="weekly")
    validate_integer_field(frontmatter, "year", errors)
    validate_integer_field(frontmatter, "repos_featured", errors)
    validate_integer_field(frontmatter, "stars_tracked", errors)
    validate_integer_field(frontmatter, "quality_score", errors)

    quality_score = frontmatter.get("quality_score")
    if isinstance(quality_score, int) and quality_score < 60:
        errors.append("quality_score must be at least 60.")

    expected_week = raw_payload.get("week")
    week_match = WEEK_PATTERN.fullmatch(expected_week) if isinstance(expected_week, str) else None
    expected_year = int(week_match.group("year")) if week_match else None
    if frontmatter.get("week") != expected_week:
        errors.append(f"week must match raw payload week {expected_week!r}.")
    if expected_year is not None and frontmatter.get("year") != expected_year:
        errors.append(f"year must match the raw payload week year ({expected_year}).")

    date_value = frontmatter.get("date")
    if date_value is None:
        pass
    else:
        try:
            analysis_datetime = parse_datetime(date_value)
            run_datetime = parse_datetime(current_datetime)
        except (TypeError, ValueError) as exc:
            errors.append(f"date must be a valid ISO 8601 timestamp: {exc}")
        else:
            if analysis_datetime.astimezone(UTC) != run_datetime.astimezone(UTC):
                errors.append("date must match the current run timestamp.")
            if isinstance(expected_week, str) and week_slug(analysis_datetime) != expected_week:
                errors.append(f"date must fall within raw payload week {expected_week}.")

    top_repo = frontmatter.get("top_repo")
    if isinstance(top_repo, str) and top_repo and not TOP_REPO_PATTERN.fullmatch(top_repo):
        errors.append("top_repo must use owner/repo format.")

    missing_headings = find_missing_headings(body)
    if missing_headings:
        for heading in missing_headings:
            errors.append(f"Missing required section heading: {heading}")

    word_count = len(WORD_PATTERN.findall(body))
    if word_count < 200:
        errors.append(f"Analysis body must be at least 200 words; found {word_count}.")

    lower_body = body.lower()
    for marker in RAW_MARKERS:
        if marker in lower_body:
            errors.append(f"Analysis body contains prohibited marker: {marker}")
    for pattern, description in PLACEHOLDER_PATTERNS:
        if pattern.search(body):
            errors.append(f"Analysis body contains prohibited placeholder marker: {description}")

    return errors, word_count


def fail(errors: list[str], summary_path: str | None) -> None:
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("## Analysis quality gate failed\n")
            for error in errors:
                handle.write(f"- {error}\n")
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)


def report_success(path: Path, source: str, word_count: int, summary_path: str | None) -> None:
    message = f"✅ Analysis quality gate passed for {path.name} via {source} ({word_count} words)."
    print(message)
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("## Analysis quality gate passed\n")
            handle.write(f"- File: `{path}`\n")
            handle.write(f"- Source: `{source}`\n")
            handle.write(f"- Word count: `{word_count}`\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")

    if not args.analysis_file.exists():
        fail([f"Missing analysis output: {args.analysis_file}"], summary_path)

    text = args.analysis_file.read_text(encoding="utf-8")
    raw_payload = load_json(args.raw_json)
    errors, word_count = validate_analysis(text, raw_payload, args.current_datetime)
    if errors:
        fail(errors, summary_path)

    report_success(args.analysis_file, args.source, word_count, summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
