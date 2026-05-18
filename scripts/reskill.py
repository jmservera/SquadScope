#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import track_quality

DEFAULT_PROMPT_TEMPLATE = ROOT / "prompts" / "reskill.md"
DEFAULT_ANALYZED_DIR = ROOT / "data" / "analyzed"
DEFAULT_SNAPSHOTS_DIR = ROOT / "data" / "snapshots"
DEFAULT_WISDOM_FILE = ROOT / ".squad" / "identity" / "wisdom.md"
DEFAULT_SKILLS_DIR = ROOT / ".squad" / "skills"
DEFAULT_REPORT_DIR = ROOT / ".squad" / "reskill"
DEFAULT_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODELS_MODEL = "openai/gpt-4.1"
DEFAULT_MODELS_TIMEOUT = 30
DEFAULT_COPILOT_MODEL = "claude-sonnet-4"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SquadScope reskill retrospective.")
    parser.add_argument("--current-datetime", required=True, help="ISO-8601 timestamp for the reskill run.")
    parser.add_argument(
        "--prompt-template",
        type=Path,
        default=DEFAULT_PROMPT_TEMPLATE,
        help="Prompt template path (defaults to prompts/reskill.md).",
    )
    parser.add_argument(
        "--analyzed-dir",
        type=Path,
        default=DEFAULT_ANALYZED_DIR,
        help="Directory containing analyzed weekly summaries.",
    )
    parser.add_argument(
        "--snapshots-dir",
        type=Path,
        default=DEFAULT_SNAPSHOTS_DIR,
        help="Directory containing weekly snapshot JSON files.",
    )
    parser.add_argument(
        "--wisdom-file",
        type=Path,
        default=DEFAULT_WISDOM_FILE,
        help="Path to the learned wisdom markdown file.",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=DEFAULT_SKILLS_DIR,
        help="Directory containing learned skill markdown files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write the reskill report. Defaults to .squad/reskill/YYYY-WNN.md.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of analyzed summaries to include.")
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Render the prompt to stdout without calling GitHub Models.",
    )
    return parser.parse_args(argv)


def parse_datetime(value: str) -> datetime:
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    parsed = datetime.fromisoformat(candidate)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def week_slug(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def default_output_path(current_datetime: str) -> Path:
    return DEFAULT_REPORT_DIR / f"{week_slug(parse_datetime(current_datetime))}.md"


def render_wisdom(wisdom_file: Path) -> str:
    if not wisdom_file.exists():
        return "_No learned wisdom has been recorded yet._"
    content = wisdom_file.read_text(encoding="utf-8").strip()
    return content or "_No learned wisdom has been recorded yet._"


def render_skills(skills_dir: Path) -> str:
    if not skills_dir.exists():
        return "_No learned skills have been extracted yet._"

    skill_files = sorted(path for path in skills_dir.rglob("*.md") if path.is_file())
    if not skill_files:
        return "_No learned skills have been extracted yet._"

    blocks = []
    for path in skill_files:
        relative_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        content = path.read_text(encoding="utf-8").strip()
        if content:
            blocks.append(f"--- Skill Source: {relative_path} ---\n{content}")
    return "\n\n".join(blocks) if blocks else "_No learned skills have been extracted yet._"


def find_recent_summaries(analyzed_dir: Path, limit: int) -> list[Path]:
    summaries = sorted(analyzed_dir.glob("*-summary.md")) if analyzed_dir.exists() else []
    if limit <= 0:
        return summaries
    return summaries[-limit:]


def render_recent_analyses(analyzed_dir: Path, limit: int) -> str:
    summaries = find_recent_summaries(analyzed_dir, limit)
    if not summaries:
        return "_No analyzed summaries are available yet._"

    blocks = []
    for path in summaries:
        relative_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        blocks.append(f"--- Analysis Source: {relative_path} ---\n{path.read_text(encoding='utf-8').strip()}")
    return "\n\n".join(blocks)


def snapshot_candidates(week: str, snapshots_dir: Path) -> list[Path]:
    if not snapshots_dir.exists():
        return []
    patterns = [f"{week}.json", f"{week}-*.json"]
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(sorted(path for path in snapshots_dir.glob(pattern) if path.is_file()))
    deduped = []
    seen: set[Path] = set()
    for path in matches:
        if path not in seen:
            deduped.append(path)
            seen.add(path)
    return deduped


def render_snapshot_context(analyzed_dir: Path, snapshots_dir: Path, limit: int) -> str:
    summaries = find_recent_summaries(analyzed_dir, limit)
    if not summaries:
        return "_No analyzed summaries are available, so no snapshot hindsight can be matched yet._"

    blocks = []
    for summary_path in summaries:
        week = summary_path.name.removesuffix("-summary.md")
        matches = snapshot_candidates(week, snapshots_dir)
        if not matches:
            blocks.append(f"--- Snapshot Context: {week} ---\nNo snapshot data available for hindsight validation.")
            continue
        rendered_matches = []
        for snapshot_path in matches:
            relative_path = snapshot_path.relative_to(ROOT) if snapshot_path.is_relative_to(ROOT) else snapshot_path
            rendered_matches.append(f"File: {relative_path}\n{snapshot_path.read_text(encoding='utf-8').strip()}")
        blocks.append(f"--- Snapshot Context: {week} ---\n" + "\n\n".join(rendered_matches))
    return "\n\n".join(blocks)


def render_prompt(
    *,
    prompt_template_path: Path,
    current_datetime: str,
    output_path: Path,
    analyzed_dir: Path,
    snapshots_dir: Path,
    wisdom_file: Path,
    skills_dir: Path,
    limit: int,
) -> str:
    prompt = prompt_template_path.read_text(encoding="utf-8")
    replacements = {
        "{{CURRENT_DATETIME}}": current_datetime,
        "{{OUTPUT_PATH}}": str(output_path),
        "{{WISDOM}}": render_wisdom(wisdom_file),
        "{{SKILLS}}": render_skills(skills_dir),
        "{{QUALITY_TREND}}": track_quality.build_quality_report(analyzed_dir).strip(),
        "{{RECENT_ANALYSES}}": render_recent_analyses(analyzed_dir, limit),
        "{{SNAPSHOT_CONTEXT}}": render_snapshot_context(analyzed_dir, snapshots_dir, limit),
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


def call_copilot_cli(prompt: str) -> str:
    copilot_path = shutil.which("copilot")
    if not copilot_path:
        raise RuntimeError("GitHub Copilot CLI is not installed.")

    result = subprocess.run(
        [
            copilot_path,
            "-p",
            prompt,
            "-s",
            "--no-ask-user",
            "--model",
            os.environ.get("COPILOT_MODEL", DEFAULT_COPILOT_MODEL),
            "--allow-tool=read",
            "--allow-tool=write",
            "--allow-tool=glob",
            "--allow-tool=grep",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
        raise RuntimeError(f"GitHub Copilot CLI failed: {detail}")

    output = result.stdout.strip()
    if not output:
        raise RuntimeError("GitHub Copilot CLI returned empty output.")
    return output + "\n"


def heading_body(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    start_index: int | None = None
    target_level: int | None = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == heading and stripped.startswith("#"):
            target_level = len(stripped.split(" ", 1)[0])
            start_index = index + 1
            break

    if start_index is None or target_level is None:
        return ""

    body_lines: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped.split(" ", 1)[0])
            if level <= target_level:
                break
        body_lines.append(line)
    return "\n".join(body_lines).strip()


def section_bullets(markdown: str, heading: str) -> list[str]:
    body = heading_body(markdown, heading)
    if not body:
        return []

    bullets: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^[-*+]\s+(.*)$", stripped)
        if match:
            bullets.append(match.group(1).strip())
            continue
        match = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if match:
            bullets.append(match.group(1).strip())
    if bullets:
        return bullets
    return [body.replace("\n", " ").strip()]


def skill_slug(output_path: Path) -> str:
    return f"reskill-{output_path.stem.lower()}"


def write_skill_artifact(markdown: str, output_path: Path, skills_dir: Path = DEFAULT_SKILLS_DIR) -> Path:
    summary = heading_body(markdown, "## Retrospective Summary") or (
        "Retrospective lessons distilled from the latest SquadScope reskill cycle."
    )
    blind_spots = section_bullets(markdown, "## Recurring Blind Spots")
    skill_candidates = section_bullets(markdown, "## Skill Candidates")
    next_cycle = section_bullets(markdown, "## Next-Cycle Adjustments")
    patterns = skill_candidates or next_cycle or [summary]
    anti_patterns = blind_spots or [
        "Do not ignore hindsight evidence or repeat unsupported signal, noise, or gap calls.",
    ]

    report_reference = output_path.relative_to(ROOT) if output_path.is_relative_to(ROOT) else output_path
    skill_path = skills_dir / skill_slug(output_path) / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(
        "\n".join(
            [
                "---",
                f'name: "{skill_slug(output_path)}"',
                f'description: "Lessons extracted from {output_path.stem} retrospective"',
                'domain: "analysis-calibration"',
                'confidence: "medium"',
                f'source: "{report_reference.as_posix()}"',
                "---",
                "",
                "## Context",
                summary,
                "",
                "## Patterns",
                *(f"- {item}" for item in patterns),
                "",
                "## Examples",
                f"- Source report: `{report_reference.as_posix()}`",
                *(f"- Next-cycle adjustment: {item}" for item in next_cycle),
                "",
                "## Anti-Patterns",
                *(f"- {item}" for item in anti_patterns),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return skill_path


def generate_report(prompt: str) -> str:
    try:
        return call_copilot_cli(prompt)
    except RuntimeError as exc:
        print(f"Copilot CLI unavailable or failed; falling back to GitHub Models API: {exc}", file=sys.stderr)
        return call_github_models(prompt)


def call_github_models(prompt: str) -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required for GitHub Models fallback.")

    endpoint = os.environ.get("GITHUB_MODELS_ENDPOINT", DEFAULT_MODELS_ENDPOINT)
    model = os.environ.get("GITHUB_MODELS_MODEL", DEFAULT_MODELS_MODEL)
    timeout = int(os.environ.get("GITHUB_MODELS_TIMEOUT", str(DEFAULT_MODELS_TIMEOUT)))
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
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
        with request.urlopen(req, timeout=timeout) as response:
            response_payload = json.load(response)
    except error.HTTPError as exc:  # pragma: no cover - exercised via message formatting
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub Models API request failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:  # pragma: no cover - network failures are environment-specific
        raise RuntimeError(f"GitHub Models API request failed: {exc.reason}") from exc

    return extract_markdown(response_payload)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_path = args.output or default_output_path(args.current_datetime)
    prompt = render_prompt(
        prompt_template_path=args.prompt_template,
        current_datetime=args.current_datetime,
        output_path=output_path,
        analyzed_dir=args.analyzed_dir,
        snapshots_dir=args.snapshots_dir,
        wisdom_file=args.wisdom_file,
        skills_dir=args.skills_dir,
        limit=args.limit,
    )

    if args.print_prompt:
        print(prompt)
        return 0

    markdown = generate_report(prompt)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    write_skill_artifact(markdown, output_path, args.skills_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
