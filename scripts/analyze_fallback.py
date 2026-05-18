#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
WEEK_PATTERN = re.compile(r"^(?P<year>\d{4})-W(?P<week>\d{2})$")
SUMMARY_SUFFIX = "-summary.md"
DEFAULT_PROMPT_TEMPLATE = ROOT / "prompts" / "analyze-weekly.md"
DEFAULT_ANALYZED_DIR = ROOT / "data" / "analyzed"
DEFAULT_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODELS_MODEL = "openai/gpt-4.1"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fallback weekly analysis via GitHub Models API.")
    parser.add_argument("--raw-json", required=True, type=Path, help="Path to the weekly raw JSON payload.")
    parser.add_argument("--output", required=True, type=Path, help="Path to write the analyzed markdown output.")
    parser.add_argument("--current-datetime", required=True, help="ISO-8601 timestamp for the analysis run.")
    parser.add_argument(
        "--prompt-template",
        type=Path,
        default=DEFAULT_PROMPT_TEMPLATE,
        help="Prompt template path (defaults to prompts/analyze-weekly.md).",
    )
    parser.add_argument(
        "--analyzed-dir",
        type=Path,
        default=DEFAULT_ANALYZED_DIR,
        help="Directory containing prior weekly summaries.",
    )
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Render the prompt to stdout without calling GitHub Models.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_week(value: str) -> tuple[int, int]:
    match = WEEK_PATTERN.fullmatch(value)
    if not match:
        raise ValueError(f"Invalid week value: {value}")
    return int(match.group("year")), int(match.group("week"))


def find_previous_summary(current_week: str, analyzed_dir: Path) -> Path | None:
    if not analyzed_dir.exists():
        return None

    current_week_key = parse_week(current_week)
    previous_candidate: tuple[int, int] | None = None
    previous_path: Path | None = None

    for path in analyzed_dir.glob(f"*{SUMMARY_SUFFIX}"):
        try:
            week_key = parse_week(path.name.removesuffix(SUMMARY_SUFFIX))
        except ValueError:
            continue
        if week_key < current_week_key and (previous_candidate is None or week_key > previous_candidate):
            previous_candidate = week_key
            previous_path = path

    return previous_path


def render_prompt(
    *,
    prompt_template_path: Path,
    raw_json_path: Path,
    output_path: Path,
    current_datetime: str,
    analyzed_dir: Path,
) -> str:
    payload = load_json(raw_json_path)
    current_week = payload["week"]
    previous_summary_path = find_previous_summary(current_week, analyzed_dir)
    previous_summary_content = previous_summary_path.read_text(encoding="utf-8") if previous_summary_path else ""

    prompt = prompt_template_path.read_text(encoding="utf-8")
    replacements = {
        "{{CURRENT_DATETIME}}": current_datetime,
        "{{RAW_JSON_PATH}}": str(raw_json_path),
        "{{OUTPUT_PATH}}": str(output_path),
        "{{PREVIOUS_SUMMARY_PATH_OR_NONE}}": str(previous_summary_path) if previous_summary_path else "None",
        "{{RAW_JSON_CONTENT}}": raw_json_path.read_text(encoding="utf-8").strip(),
        "{{PREVIOUS_SUMMARY_CONTENT_OR_EMPTY}}": previous_summary_content.strip(),
    }
    for needle, value in replacements.items():
        prompt = prompt.replace(needle, value)
    return prompt


def extract_markdown(response_payload: dict[str, Any]) -> str:
    choices = response_payload.get("choices") or []
    if not choices:
        raise ValueError("GitHub Models response did not include any choices.")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content.strip() + "\n"

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("output_text")
                if text:
                    parts.append(text)
        if parts:
            return "\n".join(parts).strip() + "\n"

    text = choices[0].get("text")
    if isinstance(text, str) and text.strip():
        return text.strip() + "\n"

    raise ValueError("GitHub Models response did not contain markdown output.")


def call_github_models(prompt: str) -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required for GitHub Models fallback.")

    endpoint = os.environ.get("GITHUB_MODELS_ENDPOINT", DEFAULT_MODELS_ENDPOINT)
    model = os.environ.get("GITHUB_MODELS_MODEL", DEFAULT_MODELS_MODEL)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.3,
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req) as response:
            response_payload = json.load(response)
    except error.HTTPError as exc:  # pragma: no cover
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub Models API request failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:  # pragma: no cover
        raise RuntimeError(f"GitHub Models API request failed: {exc.reason}") from exc

    return extract_markdown(response_payload)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    prompt = render_prompt(
        prompt_template_path=args.prompt_template,
        raw_json_path=args.raw_json,
        output_path=args.output,
        current_datetime=args.current_datetime,
        analyzed_dir=args.analyzed_dir,
    )

    if args.print_prompt:
        print(prompt)
        return 0

    markdown = call_github_models(prompt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
