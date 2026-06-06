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

try:
    from scripts.sanitize_repo_content import sanitize_repo_payload
except ModuleNotFoundError:  # pragma: no cover - script execution path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.sanitize_repo_content import sanitize_repo_payload

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT_TEMPLATE = ROOT / "prompts" / "analyze-weekly.md"
DEFAULT_ANALYZED_DIR = ROOT / "data" / "analyzed"
DEFAULT_WISDOM_FILE = ROOT / ".squad" / "identity" / "wisdom.md"
DEFAULT_SKILLS_DIR = ROOT / ".squad" / "skills"
DEFAULT_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODELS_MODEL = "openai/gpt-4o"
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
        "--press-context",
        type=Path,
        default=None,
        help="Path to rendered press context markdown (appended to prompt).",
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
    press_context_path: Path | None = None,
) -> str:
    payload = load_json(raw_json_path)
    sanitized_payload = sanitize_repo_payload(payload)
    current_week = sanitized_payload["week"]
    previous_summary_path = find_previous_summary(current_week, analyzed_dir)
    previous_summary_content = previous_summary_path.read_text(encoding="utf-8") if previous_summary_path else ""
    raw_json_content = json.dumps(sanitized_payload, indent=2, ensure_ascii=False)
    current_year, _, week_number = current_week.partition("-W")
    generic_title_example = f"Week {int(week_number)}, {current_year} Analysis" if week_number.isdigit() else "Week NN, YYYY Analysis"

    prompt = prompt_template_path.read_text(encoding="utf-8")
    replacements = {
        "{{CURRENT_DATETIME}}": current_datetime,
        "{{CURRENT_WEEK}}": current_week,
        "{{CURRENT_YEAR}}": current_year,
        "{{TITLE_TEMPLATE_HINT}}": (
            f"Specific editorial headline about {current_week}'s dominant themes "
            f"(not \"{generic_title_example}\")"
        ),
        "{{RAW_JSON_PATH}}": str(raw_json_path),
        "{{OUTPUT_PATH}}": str(output_path),
        "{{PREVIOUS_SUMMARY_PATH_OR_NONE}}": str(previous_summary_path) if previous_summary_path else "None",
        "{{RAW_JSON_CONTENT}}": raw_json_content,
        "{{PREVIOUS_SUMMARY_CONTENT_OR_EMPTY}}": previous_summary_content.strip(),
        "{{WISDOM}}": render_wisdom(wisdom_file),
        "{{SKILLS}}": render_skills(skills_dir),
    }
    for needle, value in replacements.items():
        prompt = prompt.replace(needle, value)

    # Append press context if available
    if press_context_path and press_context_path.exists() and press_context_path.stat().st_size > 0:
        press_content = press_context_path.read_text(encoding="utf-8").strip()
        prompt += f"\n\n---\n## Press Context\n\n{press_content}\n"

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
NON_RETRYABLE_STATUS_CLASSES = {400, 401, 403, 404}
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
                retry_class = (
                    "non-retryable"
                    if exc.code in NON_RETRYABLE_STATUS_CLASSES or exc.code not in RETRYABLE_STATUS_CODES
                    else "retry-exhausted"
                )
                access_hint = " GitHub Models access is unavailable for this model." if exc.code == 403 else ""
                raise RuntimeError(
                    f"GitHub Models API request failed ({exc.code}, {retry_class}): {detail}{access_hint}"
                ) from exc
            # Determine delay: respect Retry-After header on 429
            retry_after = exc.headers.get("Retry-After") if exc.code == 429 and exc.headers is not None else None
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


def _strip_ai_instructions(content: str) -> str:
    """Remove AI-facing instruction blocks from a rendered press context string.

    Strips:
    - The "### Instructions" section (from that heading to the next "###" or EOF)
    - The "#### Divergence Instructions" block (heading + bullet items)
    - Truncates the "### Correlation Summary" list to the first 10 entries,
      appending a "…and N more" summary line when truncation occurs.
    """
    import re  # noqa: PLC0415

    # Strip ### Instructions section (to next ### heading or EOF)
    content = re.sub(
        r"\n### Instructions\n.*?(?=\n###|\Z)",
        "",
        content,
        flags=re.DOTALL,
    )

    # Strip #### Divergence Instructions block (to next #### / ### heading or EOF)
    content = re.sub(
        r"\n#### Divergence Instructions\n.*?(?=\n####|\n###|\Z)",
        "",
        content,
        flags=re.DOTALL,
    )

    # Truncate correlations list to top 10
    corr_match = re.search(
        r"(### Correlation Summary\n[^\n]*\n)((?:- [^\n]*\n?)+)",
        content,
    )
    if corr_match:
        header = corr_match.group(1)
        list_block = corr_match.group(2)
        list_lines = [ln for ln in list_block.splitlines() if ln.startswith("- ")]
        total = len(list_lines)
        if total > 10:
            omitted = total - 10
            truncated = "\n".join(list_lines[:10])
            truncated += f"\n…and {omitted} more repos with press correlation\n"
            content = (
                content[: corr_match.start()]
                + header
                + truncated
                + content[corr_match.end() :]
            )

    # Truncate divergence lists to top 10 items each
    for section_header in (
        r"#### 🔍 Tech Trends Without Dev Activity",
        r"#### 🚀 Dev Activity Without Press Coverage",
    ):
        div_match = re.search(
            rf"({re.escape(section_header)}\n[^\n]*\n\n?)((?:- [^\n]*\n?)+)",
            content,
        )
        if div_match:
            header = div_match.group(1)
            list_block = div_match.group(2)
            list_lines = [ln for ln in list_block.splitlines() if ln.startswith("- ")]
            total = len(list_lines)
            if total > 10:
                omitted = total - 10
                truncated = "\n".join(list_lines[:10])
                truncated += f"\n- …and {omitted} more topics\n"
                content = (
                    content[: div_match.start()]
                    + header
                    + truncated
                    + content[div_match.end() :]
                )

    # Add reader-friendly conclusion if divergences exist but instructions were stripped
    if "### Divergence Analysis" in content and "Divergence Instructions" not in content:
        if "These divergences highlight" not in content:
            content = content.rstrip()
            content += (
                "\n\nThese divergences highlight gaps between what the tech industry "
                "is reporting and what developers are actually building.\n"
            )

    return content.strip()


def _render_press_section_no_ai(press_context_path: Path | None) -> str:
    """Render press context data for the no-AI summary (reader-facing)."""
    if not press_context_path or not press_context_path.exists() or press_context_path.stat().st_size == 0:
        return (
            "No industry press data was available for this week's analysis. "
            "Future runs with TechCrunch integration enabled will provide "
            "correlation analysis between developer activity and industry coverage, "
            "highlighting press-driven hype versus organic growth patterns."
        )

    # Try to re-render from raw data using reader_mode=True so the narrative
    # divergence format (from PR #136) is used instead of the AI-prompt format.
    stem = press_context_path.stem  # e.g. "2026-W21-press-context"
    week = stem.replace("-press-context", "")  # e.g. "2026-W21"
    data_dir = press_context_path.parent.parent  # data/analyzed/ -> data/
    external_path = data_dir / "raw" / f"{week}-external-news.json"
    legacy_path = data_dir / "raw" / f"{week}-techcrunch.json"
    tc_path = external_path if external_path.exists() else legacy_path
    corr_path = data_dir / "analyzed" / f"{week}-correlations.json"

    if tc_path.exists():
        from scripts.render_press_context import render_press_context, load_json as rpc_load_json
        tc_data = rpc_load_json(tc_path)
        corr_data = rpc_load_json(corr_path) if corr_path.exists() else {}
        if tc_data is not None:
            return render_press_context(tc_data, corr_data or {}, week, reader_mode=True)

    # Fallback: strip AI instructions from the pre-rendered file.
    content = press_context_path.read_text(encoding="utf-8").strip()
    return _strip_ai_instructions(content)


def generate_no_ai_summary(raw_json_path: Path, current_datetime: str, press_context_path: Path | None = None) -> str:
    """Generate a valid summary from raw JSON without any AI API calls."""
    payload = sanitize_repo_payload(load_json(raw_json_path))
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
    title_topics = [topic.replace("-", " ").title() for topic in top_topics[:2] if topic]
    if len(title_topics) == 2:
        fallback_title = f"{title_topics[0]}, {title_topics[1]}, and This Week's Repo Signals"
    elif len(title_topics) == 1:
        fallback_title = f"{title_topics[0]} Leads This Week's Repo Signals"
    else:
        fallback_title = f"{top_repo.split('/')[-1]} Leads This Week's Repo Signals"

    markdown = f'''---
title: "{fallback_title}"
date: {current_datetime}
week: "{week}"
year: {int(year_str)}
tags: [{", ".join(tags)}]
categories: [weekly]
repos_featured: {repos_featured}
stars_tracked: {total_stars}
top_repo: "{top_repo}"
quality_score: 70
summary: "Automated data-only summary for {week}. AI analysis was unavailable; this report presents raw crawl statistics and top repositories without editorial commentary."
---

## This Week's Trends

Without AI-powered analysis, this section reports observed patterns from crawl data rather than synthesized editorial trends. The top community topics this week are {topics_str}, and the dominant languages are {lang_summary}. These signals point to where developer attention is concentrated, though qualitative interpretation of which patterns are durable versus incidental requires a full AI-enabled analysis run.

The crawler captured {repos_featured} repositories this week ({len(new_repos)} new, {len(trending_repos)} trending) with {total_stars:,} cumulative stars. The top repository by star count is [{top_repo}](https://github.com/{top_repo}). Raw patterns suggest continued investment in {lang_summary}, but without editorial judgment these should be treated as directional rather than conclusive.

## Where Industry Meets Code

{_render_press_section_no_ai(press_context_path)}

## Signal & Noise

The primary observable signal this week comes from language and topic distribution. The top languages are {lang_summary}. The top community topics are {topics_str}. These patterns indicate where developer attention is concentrating and what categories are gaining traction relative to prior weeks.

Without AI-powered filtering, distinguishing signal from noise requires manual review. Some repositories in the crawl may represent low-quality forks, exploit tools, or promotional projects that inflate topic counts without contributing meaningful innovation. Future AI-enabled runs will provide better noise filtering and critical editorial judgment.

## Blind Spots

This automated summary lacks the editorial judgment that AI analysis would normally provide. Specific blind spots in this report include: comparative trend analysis against prior weeks, qualitative assessment of repository significance, identification of emerging ecosystem patterns not visible from raw metrics, and filtering of low-signal entries that inflate topic counts. The raw data is preserved for future re-analysis when AI capabilities become available.

## The Week Ahead

Week {week_num} of {year_str} captured {repos_featured} repositories with {total_stars:,} cumulative stars tracked. The top repository is [{top_repo}](https://github.com/{top_repo}). This summary was generated without AI assistance and presents factual crawl statistics only. A full analytical run should be attempted when AI model access is restored to provide trend synthesis and editorial judgment.

## Key References

### Notable Projects

{notable_section}

### Press & Industry

{_render_press_section_no_ai(press_context_path) if press_context_path else "No press data was provided this week."}
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
        press_context_path=args.press_context,
    )

    if args.print_prompt:
        print(prompt)
        return 0

    if args.no_ai:
        markdown = generate_no_ai_summary(args.raw_json, args.current_datetime, args.press_context)
    else:
        markdown = call_github_models(prompt)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
