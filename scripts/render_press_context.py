#!/usr/bin/env python3
"""Render the press context prompt section with TechCrunch and correlation data.

Reads crawl data and correlation data, then renders the press context
prompt template with real values. Output can be piped into the analyzer.

Usage:
    python scripts/render_press_context.py [--topic ai-ml] [--week 2026-W21]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Allow imports when run from repo root or scripts/
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from topic_paths import raw_dir, analyzed_dir  # noqa: E402


def current_week() -> str:
    """Return the current ISO week as YYYY-WNN."""
    now = datetime.now()
    iso = now.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def load_json(path: Path) -> dict | None:
    """Load a JSON file, returning None if it doesn't exist."""
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_articles_list(articles: list[dict]) -> str:
    """Format articles into a markdown list."""
    if not articles:
        return "- (none)"
    lines = []
    for article in articles:
        title = article.get("title", "Untitled")
        url = article.get("url", "")
        categories = article.get("categories", [])
        cat_str = f" [{', '.join(categories)}]" if categories else ""
        if url:
            lines.append(f"- [{title}]({url}){cat_str}")
        else:
            lines.append(f"- {title}{cat_str}")
    return "\n".join(lines)


def format_correlations_list(correlations: list[dict]) -> str:
    """Format correlations into a markdown list."""
    if not correlations:
        return "- (none)"
    lines = []
    for corr in correlations:
        repo = corr.get("repo", "unknown")
        match_type = corr.get("match_type", "unknown")
        confidence = corr.get("correlation_confidence", 0.0)
        hype_risk = corr.get("hype_risk", "none")
        lines.append(
            f"- {repo} — match: {match_type}, "
            f"confidence: {confidence:.1f}, hype_risk: {hype_risk}"
        )
    return "\n".join(lines)


def format_divergences(divergences: dict) -> str:
    """Format divergences section into markdown."""
    if not divergences:
        return ""

    uncovered = divergences.get("uncovered_tech_trends", [])
    unpublicized = divergences.get("unpublicized_dev_activity", [])

    if not uncovered and not unpublicized:
        return ""

    lines = ["\n### Divergence Analysis\n"]

    if uncovered:
        lines.append("#### 🔍 Tech Trends Without Dev Activity")
        lines.append("Topics heavily covered by TechCrunch with no matching GitHub repos:\n")
        for item in uncovered:
            topic = item.get("topic", "unknown")
            articles = item.get("techcrunch_articles", [])
            article_refs = ", ".join(
                f"[{a.get('title', 'article')}]({a.get('url', '')})"
                for a in articles[:3]
            )
            lines.append(f"- **{topic}**: {article_refs}")
        lines.append("")

    if unpublicized:
        lines.append("#### 🚀 Dev Activity Without Press Coverage")
        lines.append("GitHub repos/trends with no matching TechCrunch coverage:\n")
        for item in unpublicized:
            topic = item.get("topic", "unknown")
            repos = item.get("github_repos", [])
            repo_refs = ", ".join(
                f"{r.get('full_name', '?')} (⭐{r.get('stars', 0)})"
                for r in repos[:3]
            )
            lines.append(f"- **{topic}**: {repo_refs}")
        lines.append("")

    lines.append("#### Divergence Instructions")
    lines.append("Use divergences to identify:")
    lines.append("- 🔮 Where industry is moving but devs haven't caught up")
    lines.append("- 💡 Where devs are innovating ahead of media attention")
    lines.append("- 📊 Opportunity gaps between narrative and reality")

    return "\n".join(lines)


def render_press_context(
    techcrunch_data: dict | None, correlation_data: dict | None, week: str
) -> str:
    """Render the press context prompt section.

    Args:
        techcrunch_data: Parsed TechCrunch crawl JSON or None.
        correlation_data: Parsed correlation JSON or None.
        week: The week string (YYYY-WNN).

    Returns:
        Rendered markdown prompt section.
    """
    if techcrunch_data is None and correlation_data is None:
        return (
            "No press data available for this week. "
            "Analyze repos based on GitHub signals only."
        )

    template_path = _REPO_ROOT / "prompts" / "analyze-press-context.md"
    template = template_path.read_text(encoding="utf-8")

    # Extract articles (filter to relevant ones)
    articles = []
    if techcrunch_data:
        all_articles = techcrunch_data.get("articles", [])
        articles = [
            a for a in all_articles if a.get("relevance_score", 0) >= 0.4
        ]

    # Extract correlations
    correlations = []
    if correlation_data:
        correlations = correlation_data.get("correlations", [])

    article_count = len(articles)
    correlation_count = len(correlations)

    # Extract divergences
    divergences = {}
    if correlation_data:
        divergences = correlation_data.get("divergences", {})

    # Render template
    rendered = template.replace("{date}", week)
    rendered = rendered.replace("{article_count}", str(article_count))
    rendered = rendered.replace("{articles_list}", format_articles_list(articles))
    rendered = rendered.replace("{correlation_count}", str(correlation_count))
    rendered = rendered.replace("{correlations_list}", format_correlations_list(correlations))

    # Append divergences section
    divergence_section = format_divergences(divergences)
    if divergence_section:
        rendered += "\n" + divergence_section

    return rendered


def resolve_paths(topic: str | None, week: str) -> tuple[Path, Path]:
    """Resolve file paths for TechCrunch and correlation data."""
    tc_path = raw_dir(topic) / f"{week}-techcrunch.json"
    corr_path = analyzed_dir(topic) / f"{week}-correlations.json"
    return tc_path, corr_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render press context prompt section"
    )
    parser.add_argument(
        "--topic", default=None, help="Topic ID (e.g., ai-ml)"
    )
    parser.add_argument(
        "--week", default=None, help="Week in YYYY-WNN format (default: current)"
    )
    args = parser.parse_args()

    week = args.week or current_week()
    topic = args.topic

    tc_path, corr_path = resolve_paths(topic, week)
    techcrunch_data = load_json(tc_path)
    correlation_data = load_json(corr_path)

    output = render_press_context(techcrunch_data, correlation_data, week)
    print(output)


if __name__ == "__main__":
    main()
