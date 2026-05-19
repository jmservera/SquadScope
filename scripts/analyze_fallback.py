#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT_TEMPLATE = ROOT / "prompts" / "analyze-weekly.md"
DEFAULT_ANALYZED_DIR = ROOT / "data" / "analyzed"
DEFAULT_WISDOM_FILE = ROOT / ".squad" / "identity" / "wisdom.md"
DEFAULT_SKILLS_DIR = ROOT / ".squad" / "skills"
DEFAULT_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODELS_MODEL = "openai/gpt-4.1"
DEFAULT_MODELS_TIMEOUT = 30


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
        "--print-prompt",
        action="store_true",
        help="Render the prompt to stdout without calling GitHub Models.",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Generate a data-only summary without calling any AI API.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_previous_summary(current_week: str, analyzed_dir: Path) -> Path | None:
    if not analyzed_dir.exists():
        return None

    candidates = []
    for path in analyzed_dir.glob("*-summary.md"):
        week = path.name.removesuffix("-summary.md")
        if week < current_week:
            candidates.append(path)
    return max(candidates, default=None)


def render_wisdom(wisdom_file: Path) -> str:
    if not wisdom_file.exists():
        return "_No learned wisdom has been recorded yet._"

    content = wisdom_file.read_text(encoding="utf-8").strip()
    return content or "_No learned wisdom has been recorded yet._"


def iter_skill_files(skills_dir: Path) -> list[Path]:
    if not skills_dir.exists():
        return []
    return sorted(path for path in skills_dir.rglob("*.md") if path.is_file())


def render_skills(skills_dir: Path) -> str:
    skill_files = iter_skill_files(skills_dir)
    if not skill_files:
        return "_No learned skills have been extracted yet._"

    blocks = []
    for path in skill_files:
        relative_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        blocks.append(f"--- Skill Source: {relative_path} ---\n{content}")
    return "\n\n".join(blocks) if blocks else "_No learned skills have been extracted yet._"


def render_prompt(
    *,
    prompt_template_path: Path,
    raw_json_path: Path,
    output_path: Path,
    current_datetime: str,
    analyzed_dir: Path,
    wisdom_file: Path = DEFAULT_WISDOM_FILE,
    skills_dir: Path = DEFAULT_SKILLS_DIR,
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
        "{{WISDOM}}": render_wisdom(wisdom_file),
        "{{SKILLS}}": render_skills(skills_dir),
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


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BASE_DELAY = 2  # seconds


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
        "temperature": 0.3,
    }
    body = json.dumps(payload).encode("utf-8")

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
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
            return extract_markdown(response_payload)
        except error.HTTPError as exc:
            if exc.code not in RETRYABLE_STATUS_CODES or attempt == MAX_RETRIES:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"GitHub Models API request failed ({exc.code}): {detail}"
                ) from exc
            # Determine delay: respect Retry-After header on 429
            retry_after = exc.headers.get("Retry-After") if exc.code == 429 else None
            if retry_after is not None:
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = BASE_DELAY ** (attempt + 1)
            else:
                delay = BASE_DELAY ** (attempt + 1)
            jitter = random.uniform(0, 1)  # noqa: S311
            total_delay = delay + jitter
            print(
                f"[retry] GitHub Models API returned {exc.code}, "
                f"retrying in {total_delay:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})",
                file=sys.stderr,
            )
            last_exc = exc
            time.sleep(total_delay)
        except error.URLError as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"GitHub Models API request failed: {exc.reason}"
                ) from exc
            delay = BASE_DELAY ** (attempt + 1) + random.uniform(0, 1)  # noqa: S311
            print(
                f"[retry] GitHub Models API network error: {exc.reason}, "
                f"retrying in {delay:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})",
                file=sys.stderr,
            )
            last_exc = exc
            time.sleep(delay)

    # Should not be reached, but satisfy type checkers
    raise RuntimeError("GitHub Models API request failed after retries") from last_exc


def generate_no_ai_summary(raw_json_path: Path, current_datetime: str) -> str:
    """Generate a valid summary from raw JSON without any AI API calls."""
    payload = load_json(raw_json_path)
    week = payload["week"]
    new_repos = payload.get("new_repos", [])
    trending_repos = payload.get("trending_repos", [])
    signals = payload.get("signals", {})
    raw_topics = signals.get("top_topics", [])
    top_topics = [t["topic"] if isinstance(t, dict) else str(t) for t in raw_topics]

    total_stars = sum(r.get("stars", 0) for r in new_repos + trending_repos)
    repos_featured = len(new_repos) + len(trending_repos)

    all_repos = sorted(new_repos + trending_repos, key=lambda r: r.get("stars", 0), reverse=True)
    top_repo = all_repos[0]["full_name"] if all_repos else "unknown/unknown"

    tags = top_topics[:5] if len(top_topics) >= 3 else ["open-source", "developer-tools", "automation"]

    # Notable new repos
    notable_new = sorted(new_repos, key=lambda r: r.get("stars", 0), reverse=True)[:10]
    notable_lines = []
    for repo in notable_new:
        desc = repo.get("description") or "No description provided"
        lang = repo.get("language") or "Unknown"
        notable_lines.append(
            f"- [{repo['full_name']}]({repo.get('url', '#')}) ({lang}, "
            f"{repo.get('stars', 0):,} stars): {desc}"
        )
    notable_section = "\n".join(notable_lines) if notable_lines else "No new repositories were captured this week."

    # Trending repos
    top_trending = sorted(trending_repos, key=lambda r: r.get("stars", 0), reverse=True)[:10]
    trending_lines = []
    for repo in top_trending:
        desc = repo.get("description") or "No description provided"
        lang = repo.get("language") or "Unknown"
        trending_lines.append(
            f"- [{repo['full_name']}]({repo.get('url', '#')}) ({lang}, "
            f"{repo.get('stars', 0):,} stars): {desc}"
        )
    trending_section = "\n".join(trending_lines) if trending_lines else "No trending repositories were captured this week."

    # Language breakdown
    lang_counts: dict[str, int] = {}
    for repo in all_repos:
        lang = repo.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    top_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    lang_summary = ", ".join(f"{lang} ({count})" for lang, count in top_langs) if top_langs else "diverse mix of languages"

    year_str = week.split("-W")[0]
    week_num = week.split("-W")[1]
    topics_str = ", ".join(top_topics[:8]) if top_topics else "not available from this crawl"

    markdown = f'''---
title: "Week {week_num}, {year_str} Analysis"
date: {current_datetime}
week: "{week}"
year: {int(year_str)}
tags: [{", ".join(tags)}]
categories: [weekly]
repos_featured: {repos_featured}
stars_tracked: {total_stars}
top_repo: "{top_repo}"
quality_score: 62
summary: "Automated data-only summary for {week}. AI analysis was unavailable; this report presents raw crawl statistics and top repositories without editorial commentary."
---

## Notable New Repositories

This week the crawler captured {len(new_repos)} new repositories. The following are the highest-starred new entries, representing emerging projects and fresh launches that attracted early attention from the community.

{notable_section}

These repositories reflect the current interests of the developer community. The concentration of activity around {lang_summary} suggests continued investment in these technology areas. Without AI-powered analysis, editorial interpretation of these signals is deferred to the next available run.

## Trending This Week

The trending set includes {len(trending_repos)} repositories that were active during the crawl window. The following top entries by cumulative star count represent sustained community interest.

{trending_section}

The presence of established projects alongside newer entries indicates both sustained momentum in foundational tools and growing interest in emerging categories.

## Trend Analysis

### Signal

The primary signal this week comes from language and topic distribution. The top languages are {lang_summary}. The top community topics are {topics_str}. These patterns indicate where developer attention is concentrating and what categories are gaining traction relative to prior weeks.

### Noise

Without AI-powered filtering, distinguishing signal from noise requires manual review. Some repositories in the crawl may represent low-quality forks, exploit tools, or promotional projects that inflate topic counts without contributing meaningful innovation. Future AI-enabled runs will provide better noise filtering.

## What's Missing

### Gaps

This automated summary lacks editorial judgment that AI analysis would normally provide. Specific gaps include: comparative trend analysis against prior weeks, qualitative assessment of repository significance, identification of emerging ecosystem patterns, and filtering of low-signal entries. The raw data is preserved for future re-analysis when AI capabilities become available.

## Conclusion

Week {week_num} of {year_str} captured {repos_featured} repositories with {total_stars:,} cumulative stars tracked. The top repository by star count is [{top_repo}](https://github.com/{top_repo}). This summary was generated without AI assistance and presents factual crawl statistics only. A full analytical run should be attempted when AI model access is restored.
'''
    return markdown.strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    prompt = render_prompt(
        prompt_template_path=args.prompt_template,
        raw_json_path=args.raw_json,
        output_path=args.output,
        current_datetime=args.current_datetime,
        analyzed_dir=args.analyzed_dir,
        wisdom_file=args.wisdom_file,
        skills_dir=args.skills_dir,
    )

    if args.print_prompt:
        print(prompt)
        return 0

    if args.no_ai:
        markdown = generate_no_ai_summary(args.raw_json, args.current_datetime)
    else:
        markdown = call_github_models(prompt)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
