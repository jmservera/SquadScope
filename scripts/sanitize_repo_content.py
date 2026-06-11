#!/usr/bin/env python3
"""Sanitize user-controlled repository content before LLM prompt rendering."""

from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

MAX_DESCRIPTION_LENGTH = 500
SUSPICIOUS_DESCRIPTION_LENGTH = 200
BOUNDARY_CLOSE = "</untrusted-content>"
BOUNDARY_CLOSE_ESCAPED = "<\\/untrusted-content>"
INJECTION_PHRASES = (
    "ignore previous",
    "ignore all previous",
    "ignore the above",
    "ignore instructions",
    "ignore restrictions",
    "disregard",
    "you are now",
    "you are a",
    "pretend to be",
    "act as if",
    "roleplay",
    "new instructions",
    "system:",
    "system prompt",
    "user:",
    "assistant:",
    "</untrusted-content>",
    "<untrusted-content>",
    "do not follow",
    "override",
    BOUNDARY_CLOSE,
)


def _repo_label(repo: Mapping[str, Any] | None) -> str:
    if not repo:
        return "unknown repo"
    for key in ("full_name", "name", "url"):
        value = repo.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown repo"


def _truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 1].rstrip() + "…"


def _escape_untrusted_boundaries(value: str) -> str:
    result = value.replace(BOUNDARY_CLOSE, BOUNDARY_CLOSE_ESCAPED)
    result = result.replace("<untrusted-content>", "<\\/untrusted-content>")
    return result


def sanitize_text(
    text: Any,
    *,
    max_length: int = MAX_DESCRIPTION_LENGTH,
    label: str = "text",
) -> str:
    """Sanitize arbitrary untrusted text for safe prompt injection.

    Unlike sanitize_description (which targets repo description fields), this
    function works on any free-form text (article titles, topic descriptions,
    scorecard summaries, etc.).
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    sanitized = _escape_untrusted_boundaries(text.lstrip())
    lowered = sanitized.lower()
    suspicious_matches = [phrase for phrase in INJECTION_PHRASES if phrase in lowered]

    limit = min(SUSPICIOUS_DESCRIPTION_LENGTH, max_length) if suspicious_matches else max_length
    truncated = _truncate(sanitized, limit)

    if suspicious_matches:
        LOGGER.warning(
            "Suspicious %s contained possible prompt-injection phrase(s): %s",
            label,
            ", ".join(suspicious_matches),
        )
    return truncated


def sanitize_description(
    description: Any,
    *,
    repo: Mapping[str, Any] | None = None,
    max_length: int = MAX_DESCRIPTION_LENGTH,
    suspicious_length: int = SUSPICIOUS_DESCRIPTION_LENGTH,
) -> Any:
    """Return a prompt-safe repository description while preserving normal text."""
    if description is None or not isinstance(description, str):
        return description

    original = description
    sanitized = _escape_untrusted_boundaries(description.lstrip())
    lowered = sanitized.lower()
    suspicious_matches = [phrase for phrase in INJECTION_PHRASES if phrase in lowered]

    if original != sanitized:
        LOGGER.warning("Sanitized leading whitespace or boundary marker in description for %s", _repo_label(repo))

    limit = suspicious_length if suspicious_matches else max_length
    truncated = _truncate(sanitized, limit)

    if suspicious_matches:
        LOGGER.warning(
            "Suspicious repo description for %s contained possible prompt-injection phrase(s): %s",
            _repo_label(repo),
            ", ".join(suspicious_matches),
        )
    if truncated != sanitized:
        LOGGER.warning("Truncated repo description for %s to %d characters", _repo_label(repo), limit)

    return truncated


def sanitize_repo_payload(payload: Any) -> Any:
    """Recursively sanitize `description` fields in a raw crawl payload."""
    if isinstance(payload, Mapping):
        result: dict[str, Any] = {}
        for key, value in payload.items():
            if key == "description":
                result[key] = sanitize_description(value, repo=payload)
            else:
                result[key] = sanitize_repo_payload(value)
        return result
    if isinstance(payload, list):
        return [sanitize_repo_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(sanitize_repo_payload(item) for item in payload)
    return payload


def sanitize_json_file(input_path: Path, output_path: Path | None = None) -> Path:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    sanitized = sanitize_repo_payload(payload)
    destination = output_path or input_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(sanitized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sanitize repo descriptions in a raw crawl JSON payload.")
    parser.add_argument("--input", required=True, type=Path, help="Raw JSON payload to sanitize")
    parser.add_argument("--output", type=Path, help="Destination path; defaults to modifying input in place")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
    sanitize_json_file(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
