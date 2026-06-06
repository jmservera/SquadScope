#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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
OPTIONAL_FIELDS = ["predictions"]
PREDICTION_DIRECTIONS = {"up", "flat", "down"}
PREDICTION_CLAIM_TYPES = {"signal", "noise", "gap"}
PREDICTION_FIELDS = {"repo", "claim_type", "direction", "confidence"}
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
PUBLISHABLE_AI_SOURCES = {"copilot-cli", "github-models"}
UNPUBLISHABLE_MODEL_VALUES = {"", "unknown", "unavailable", "none", "no-ai"}
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
REPO_LINK_PATTERN = re.compile(r"\[([^/\]\s]+/[^/\]\s]+)\]\(https://github\.com/\1\)")
SECTION_MIN_WORDS = {
    "## This Week's Trends": 60,
    "## Where Industry Meets Code": 40,
    "## Signal & Noise": 50,
    "## Blind Spots": 30,
    "## The Week Ahead": 30,
}
EDITORIAL_TERMS = {
    "signal",
    "noise",
    "gap",
    "gaps",
    "durable",
    "hype",
    "matters",
    "evidence",
    "trend",
    "trends",
    "blind",
    "missing",
    "practitioners",
    "ecosystem",
}
EXPLANATORY_PATTERN = re.compile(r"\b(because|why|matters|signals|reveals|driven|shows|suggests)\b", re.IGNORECASE)
CONTRADICTION_PATTERNS = [
    (
        re.compile(r"no press data was provided", re.IGNORECASE),
        re.compile(r"\b(press|media|article|coverage|reported|techcrunch)\b", re.IGNORECASE),
        "claims no press data was provided while also describing press coverage.",
    ),
    (
        re.compile(r"no meaningful developer activity", re.IGNORECASE),
        REPO_LINK_PATTERN,
        "claims no meaningful developer activity while citing active repositories.",
    ),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate weekly analysis output against the analysis spec.")
    parser.add_argument("--analysis-file", required=True, type=Path, help="Path to the rendered markdown summary.")
    parser.add_argument("--raw-json", required=True, type=Path, help="Path to the raw weekly payload.")
    parser.add_argument("--current-datetime", required=True, help="Current run timestamp in ISO 8601 format.")
    parser.add_argument("--source", default="unknown", help="Analysis source label for summaries.")
    parser.add_argument("--model", default="unknown", help="AI model label for provenance validation.")
    parser.add_argument(
        "--repair-safe",
        action="store_true",
        help="Apply deterministic frontmatter/schema repairs before final validation.",
    )
    parser.add_argument("--report-json", type=Path, help="Write a machine-readable gate report.")
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


def parse_scalar(value: str) -> Any:
    scalar = strip_quotes(value)
    if re.fullmatch(r"-?\d+", scalar):
        return int(scalar)
    if re.fullmatch(r"-?\d+\.\d+", scalar):
        return float(scalar)
    return scalar


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
            items: list[Any] = []
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if not candidate.strip():
                    index += 1
                    continue
                candidate_indent = len(candidate) - len(candidate.lstrip(" \t"))
                if candidate_indent == 0:
                    break
                stripped = candidate.strip()
                if not stripped.startswith("- "):
                    raise ValueError(f"Unsupported multiline frontmatter value for {key}: {candidate}")
                item_value = stripped[2:].strip()
                if ":" in item_value:
                    item: dict[str, Any] = {}
                    item_key, item_raw_value = item_value.split(":", 1)
                    item[item_key.strip()] = parse_scalar(item_raw_value.strip())
                    index += 1
                    while index < len(lines):
                        nested = lines[index]
                        if not nested.strip():
                            index += 1
                            continue
                        nested_indent = len(nested) - len(nested.lstrip(" \t"))
                        if nested_indent <= candidate_indent:
                            break
                        if ":" not in nested:
                            raise ValueError(f"Unsupported multiline frontmatter value for {key}: {nested}")
                        nested_key, nested_raw_value = nested.strip().split(":", 1)
                        item[nested_key.strip()] = parse_scalar(nested_raw_value.strip())
                        index += 1
                    items.append(item)
                    continue
                items.append(parse_scalar(item_value))
                index += 1
            frontmatter[key] = items
            continue
        if value.startswith("[") and value.endswith("]"):
            frontmatter[key] = parse_inline_list(value)
        else:
            frontmatter[key] = parse_scalar(value)
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


def dump_frontmatter(data: dict[str, Any]) -> str:
    if yaml is not None:
        dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
        return re.sub(r"^(date): '([^']+)'$", r"\1: \2", dumped, flags=re.MULTILINE)

    def format_scalar(value: Any) -> str:
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, (int, float)):
            return str(value)
        raise TypeError(f"Unsupported frontmatter value for fallback dump: {value!r}")

    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
                continue
            lines.append(f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    if not item:
                        lines.append("  - {}")
                        continue
                    item_fields = list(item.items())
                    first_key, first_value = item_fields[0]
                    lines.append(f"  - {first_key}: {format_scalar(first_value)}")
                    for nested_key, nested_value in item_fields[1:]:
                        lines.append(f"    {nested_key}: {format_scalar(nested_value)}")
                else:
                    lines.append(f"  - {format_scalar(item)}")
        else:
            lines.append(f"{key}: {format_scalar(value)}")
    return "\n".join(lines)


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        raise ValueError("Analysis output is missing YAML frontmatter.")
    frontmatter_text, body = match.groups()
    return parse_frontmatter(frontmatter_text), body


def render_analysis(frontmatter: dict[str, Any], body: str) -> str:
    return f"---\n{dump_frontmatter(frontmatter)}\n---\n{body}"


def expected_repo_counts(raw_payload: dict[str, Any]) -> tuple[int, int]:
    repos: list[dict[str, Any]] = []
    for field in ("new_repos", "trending_repos"):
        value = raw_payload.get(field)
        if isinstance(value, list):
            repos.extend(item for item in value if isinstance(item, dict))
    stars = sum(star for repo in repos if isinstance((star := repo.get("stars")), int) and not isinstance(star, bool))
    return len(repos), stars


def repair_analysis(
    text: str,
    raw_payload: dict[str, Any],
    current_datetime: str,
) -> tuple[str, list[str]]:
    frontmatter, body = extract_frontmatter(text)
    repaired = dict(frontmatter)
    actions: list[str] = []

    expected_week = raw_payload.get("week")
    week_match = WEEK_PATTERN.fullmatch(expected_week) if isinstance(expected_week, str) else None
    if isinstance(expected_week, str) and repaired.get("week") != expected_week:
        repaired["week"] = expected_week
        actions.append(f"set week from raw payload ({expected_week})")
    if week_match:
        expected_year = int(week_match.group("year"))
        if repaired.get("year") != expected_year:
            repaired["year"] = expected_year
            actions.append(f"set year from raw payload week ({expected_year})")
    if repaired.get("date") != current_datetime:
        repaired["date"] = current_datetime
        actions.append("set date from current run timestamp")

    repos_featured, stars_tracked = expected_repo_counts(raw_payload)
    if repaired.get("repos_featured") != repos_featured:
        repaired["repos_featured"] = repos_featured
        actions.append(f"set repos_featured from raw repo counts ({repos_featured})")
    if repaired.get("stars_tracked") != stars_tracked:
        repaired["stars_tracked"] = stars_tracked
        actions.append(f"set stars_tracked from raw repo stars ({stars_tracked})")

    predictions = repaired.get("predictions")
    if isinstance(predictions, list):
        repaired_predictions = []
        changed_predictions = False
        for index, prediction in enumerate(predictions, start=1):
            if not isinstance(prediction, dict):
                repaired_predictions.append(prediction)
                continue
            repaired_prediction = dict(prediction)
            if "claim_type" not in repaired_prediction:
                for alias in ("claim", "claimType", "type", "kind"):
                    alias_value = repaired_prediction.get(alias)
                    if isinstance(alias_value, str) and alias_value.strip().lower() in PREDICTION_CLAIM_TYPES:
                        repaired_prediction["claim_type"] = alias_value.strip().lower()
                        del repaired_prediction[alias]
                        changed_predictions = True
                        actions.append(f"set predictions[{index}].claim_type from {alias}")
                        break
            claim_type = repaired_prediction.get("claim_type")
            if isinstance(claim_type, str) and claim_type.strip().lower() in PREDICTION_CLAIM_TYPES and claim_type != claim_type.strip().lower():
                repaired_prediction["claim_type"] = claim_type.strip().lower()
                changed_predictions = True
                actions.append(f"normalized predictions[{index}].claim_type")
            direction = repaired_prediction.get("direction")
            if isinstance(direction, str) and direction.strip().lower() in PREDICTION_DIRECTIONS and direction != direction.strip().lower():
                repaired_prediction["direction"] = direction.strip().lower()
                changed_predictions = True
                actions.append(f"normalized predictions[{index}].direction")
            repaired_predictions.append(repaired_prediction)
        if changed_predictions:
            repaired["predictions"] = repaired_predictions

    if not actions:
        return text, actions
    return render_analysis(repaired, body), actions


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


def validate_predictions(frontmatter: dict[str, Any], errors: list[str]) -> None:
    predictions = frontmatter.get("predictions")
    if predictions is None:
        return
    if not isinstance(predictions, list):
        errors.append("predictions must be an array.")
        return
    for index, prediction in enumerate(predictions, start=1):
        if not isinstance(prediction, dict):
            errors.append(f"predictions[{index}] must be an object.")
            continue
        repo = prediction.get("repo")
        claim_type = prediction.get("claim_type")
        direction = prediction.get("direction")
        confidence = prediction.get("confidence")
        if not isinstance(repo, str) or not TOP_REPO_PATTERN.fullmatch(repo.strip()):
            errors.append(f"predictions[{index}].repo must use owner/repo format.")
        if not isinstance(claim_type, str) or claim_type.strip().lower() not in PREDICTION_CLAIM_TYPES:
            errors.append(f"predictions[{index}].claim_type must be one of signal, noise, gap.")
        if not isinstance(direction, str) or direction.strip().lower() not in PREDICTION_DIRECTIONS:
            errors.append(f"predictions[{index}].direction must be one of up, flat, down.")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            errors.append(f"predictions[{index}].confidence must be numeric.")
        elif not 0 <= float(confidence) <= 1:
            errors.append(f"predictions[{index}].confidence must be between 0 and 1.")
        extra_fields = sorted(set(prediction) - PREDICTION_FIELDS)
        if extra_fields:
            errors.append(f"predictions[{index}] has unexpected fields: {', '.join(extra_fields)}")


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


def section_text(body: str, heading: str) -> str:
    heading_match = re.search(rf"(?m)^{re.escape(heading)}\s*$", body)
    if heading_match is None:
        return ""
    next_heading = re.search(r"(?m)^##\s+", body[heading_match.end() :])
    end = heading_match.end() + next_heading.start() if next_heading else len(body)
    return body[heading_match.end() : end].strip()


def raw_repo_names(raw_payload: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for field in ("new_repos", "trending_repos"):
        repos = raw_payload.get(field)
        if not isinstance(repos, list):
            continue
        for repo in repos:
            if isinstance(repo, dict) and isinstance(repo.get("full_name"), str):
                names.add(repo["full_name"].strip())
    return {name for name in names if TOP_REPO_PATTERN.fullmatch(name)}


def raw_artifact_week_errors(raw_payload: dict[str, Any], expected_week: Any) -> list[str]:
    if not isinstance(expected_week, str):
        return []
    timestamp = raw_payload.get("crawled_at") or raw_payload.get("generated_at")
    if not isinstance(timestamp, str) or not timestamp.strip():
        return []
    try:
        parsed = parse_datetime(timestamp)
    except (TypeError, ValueError) as exc:
        return [f"raw evidence timestamp is invalid: {exc}"]
    artifact_week = week_slug(parsed)
    if artifact_week != expected_week:
        return [f"raw evidence timestamp week mismatch: expected {expected_week}, found {artifact_week}."]
    return []


def evidence_citation_errors(body: str, raw_payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    repos = raw_repo_names(raw_payload)
    linked_repos = set(REPO_LINK_PATTERN.findall(body))
    if repos and not linked_repos.intersection(repos):
        errors.append("evidence citations must include at least one repository link from the raw payload.")
    if repos and "## Key References" in body:
        notable = section_text(body, "## Key References")
        notable_links = set(REPO_LINK_PATTERN.findall(notable))
        if not notable_links.intersection(repos):
            errors.append("Key References must cite at least one raw-payload repository link.")
    errors.extend(raw_artifact_week_errors(raw_payload, raw_payload.get("week")))
    return errors


def editorial_quality_errors(body: str) -> list[str]:
    errors: list[str] = []
    prose = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("#"))
    lower_body = prose.lower()
    terms_found = {term for term in EDITORIAL_TERMS if re.search(rf"\b{re.escape(term)}\b", lower_body)}
    if len(terms_found) < 3:
        errors.append("editorial analysis must use trend/evidence judgment language, not generic summary prose.")
    for heading, minimum in SECTION_MIN_WORDS.items():
        text = section_text(body, heading)
        if not text:
            continue
        count = len(WORD_PATTERN.findall(text))
        if count < minimum:
            errors.append(f"{heading} section is too thin for publish-quality analysis; found {count} words, expected at least {minimum}.")
    for heading in ("## This Week's Trends", "## Signal & Noise", "## Blind Spots"):
        text = section_text(body, heading)
        if text and not EXPLANATORY_PATTERN.search(text):
            errors.append(f"{heading} must explain why the pattern matters, not only name it.")
    return errors


def contradiction_errors(body: str) -> list[str]:
    errors: list[str] = []
    for negative_pattern, positive_pattern, message in CONTRADICTION_PATTERNS:
        for match in negative_pattern.finditer(body):
            window_start = max(0, match.start() - 300)
            window_end = min(len(body), match.end() + 300)
            window = body[window_start:window_end]
            if positive_pattern.search(window.replace(match.group(0), "", 1)):
                errors.append(f"contradictory claim: {message}")
                break
    return errors


def ai_provenance_errors(source: str, model: str) -> list[str]:
    errors: list[str] = []
    normalized_source = source.strip()
    normalized_model = model.strip()
    if normalized_source not in PUBLISHABLE_AI_SOURCES:
        errors.append(f"AI provenance source is not publishable: {normalized_source or 'unknown'}.")
    if normalized_model.lower() in UNPUBLISHABLE_MODEL_VALUES:
        errors.append(f"AI provenance model is not publishable: {normalized_model or 'unknown'}.")
    return errors


def categorize_gate_error(error: str) -> str:
    if error.startswith("AI provenance"):
        return "ai_provenance"
    if error.startswith(("evidence citations", "Key References", "raw evidence")):
        return "evidence_citation"
    if error.startswith(("editorial analysis", "contradictory claim")) or "section is too thin" in error or "must explain why" in error:
        return "editorial_quality"
    if "quality_score" in error or "generic week/year" in error or "placeholder" in error:
        return "editorial_quality"
    return "structural_schema"


def build_gate_results(errors: list[str]) -> dict[str, dict[str, Any]]:
    gates = {
        "structural_schema": {"passed": True, "errors": []},
        "ai_provenance": {"passed": True, "errors": []},
        "evidence_citation": {"passed": True, "errors": []},
        "editorial_quality": {"passed": True, "errors": []},
    }
    for error in errors:
        category = categorize_gate_error(error)
        gates[category]["passed"] = False
        gates[category]["errors"].append(error)
    return gates


def validate_publish_quality(
    text: str,
    raw_payload: dict[str, Any],
    *,
    source: str,
    model: str,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    try:
        _, body = extract_frontmatter(text)
    except ValueError:
        body = ""
    errors: list[str] = []
    errors.extend(ai_provenance_errors(source, model))
    if body:
        errors.extend(evidence_citation_errors(body, raw_payload))
        errors.extend(editorial_quality_errors(body))
        errors.extend(contradiction_errors(body))
    return errors, build_gate_results(errors)


def validate_analysis(text: str, raw_payload: dict[str, Any], current_datetime: str) -> tuple[list[str], int]:
    errors: list[str] = []
    try:
        frontmatter, body = extract_frontmatter(text)
    except ValueError as exc:
        return [str(exc)], 0

    missing_fields = [field for field in REQUIRED_FIELDS if field not in frontmatter]
    if missing_fields:
        errors.append(f"Missing frontmatter fields: {', '.join(missing_fields)}")

    extra_fields = sorted(set(frontmatter) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS))
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
    validate_predictions(frontmatter, errors)

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


def write_gate_report(
    path: Path | None,
    *,
    analysis_file: Path,
    source: str,
    model: str,
    errors_before: list[str],
    errors_after: list[str],
    repair_actions: list[str],
    word_count: int,
    gate_results: dict[str, dict[str, Any]],
) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "analysis_file": analysis_file.as_posix(),
        "source": source,
        "model": model,
        "passed": not errors_after,
        "word_count": word_count,
        "gates": gate_results,
        "errors_before_repair": errors_before,
        "repair_actions": repair_actions,
        "errors_after_repair": errors_after,
        "failure_class": classify_gate_errors(errors_after),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def classify_gate_errors(errors: list[str]) -> str:
    if not errors:
        return "passed"
    categories = {categorize_gate_error(error) for error in errors}
    if len(categories) == 1:
        return next(iter(categories))
    if all(
        error.startswith(("date must", "week must", "year must", "repos_featured must", "stars_tracked must"))
        or ".claim_type must" in error
        for error in errors
    ):
        return "metadata_schema"
    if any(error.startswith("Missing required section heading") or "body" in error for error in errors):
        return "content_structure"
    return "quality_gate"


def gate_report_fingerprint(path: Path) -> str:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(report, dict):
        return ""
    errors = report.get("errors_after_repair") or report.get("errors_before_repair") or []
    if not isinstance(errors, list):
        return ""
    return hashlib.sha256(json.dumps(errors, sort_keys=True).encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")

    if not args.analysis_file.exists():
        fail([f"Missing analysis output: {args.analysis_file}"], summary_path)

    text = args.analysis_file.read_text(encoding="utf-8")
    raw_payload = load_json(args.raw_json)
    errors_before, word_count = validate_analysis(text, raw_payload, args.current_datetime)
    errors = errors_before
    repair_actions: list[str] = []
    if errors and args.repair_safe:
        try:
            repaired_text, repair_actions = repair_analysis(text, raw_payload, args.current_datetime)
        except Exception as exc:  # noqa: BLE001 - repair is best-effort; validation/reporting must continue.
            repair_actions = [f"repair skipped: {exc}"]
        else:
            if repair_actions and repaired_text != text:
                args.analysis_file.write_text(repaired_text, encoding="utf-8")
                text = repaired_text
                errors, word_count = validate_analysis(text, raw_payload, args.current_datetime)
                print(
                    f"::notice::Analysis gate applied safe repairs: {', '.join(repair_actions)}",
                    file=sys.stderr,
                )
    publish_errors_before, _ = validate_publish_quality(text, raw_payload, source=args.source, model=args.model)
    combined_errors_before = errors_before + [error for error in publish_errors_before if error not in errors_before]
    publish_errors, _ = validate_publish_quality(text, raw_payload, source=args.source, model=args.model)
    errors = errors + [error for error in publish_errors if error not in errors]
    gate_results = build_gate_results(errors)
    write_gate_report(
        args.report_json,
        analysis_file=args.analysis_file,
        source=args.source,
        model=args.model,
        errors_before=combined_errors_before,
        errors_after=errors,
        repair_actions=repair_actions,
        word_count=word_count,
        gate_results=gate_results,
    )
    if errors:
        fail(errors, summary_path)

    report_success(args.analysis_file, args.source, word_count, summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
