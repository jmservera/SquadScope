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


_HYPE_RISK_SEVERITY: dict[str, int] = {"high": 3, "medium": 2, "low": 1, "none": 0}


def format_correlations_list(correlations: list[dict], *, top_n: int | None = None) -> str:
    """Format correlations into a markdown list.

    Args:
        correlations: List of correlation dicts.
        top_n: When set, show only the top N entries (sorted by confidence desc,
               then hype_risk severity desc) and append a "…and N more" summary line.
    """
    if not correlations:
        return "- (none)"

    if top_n is not None:
        sorted_corrs = sorted(
            correlations,
            key=lambda c: (
                -c.get("correlation_confidence", 0.0),
                -_HYPE_RISK_SEVERITY.get(c.get("hype_risk", "none"), 0),
            ),
        )
        omitted = max(0, len(sorted_corrs) - top_n)
        display = sorted_corrs[:top_n]
    else:
        display = correlations
        omitted = 0

    lines = []
    for corr in display:
        repo = corr.get("repo", "unknown")
        match_type = corr.get("match_type", "unknown")
        confidence = corr.get("correlation_confidence", 0.0)
        hype_risk = corr.get("hype_risk", "none")
        lines.append(
            f"- {repo} — match: {match_type}, "
            f"confidence: {confidence:.1f}, hype_risk: {hype_risk}"
        )

    if omitted > 0:
        lines.append(f"…and {omitted} more repos with press correlation")

    return "\n".join(lines)


def _repo_link(full_name: str) -> str:
    """Format a repo as a markdown link using only the repo name (after the slash)."""
    repo_name = full_name.split("/")[-1]
    return f"[{repo_name}](https://github.com/{full_name})"


def _join_links(links: list[str]) -> str:
    """Join a list of markdown links into a readable phrase."""
    if len(links) == 1:
        return links[0]
    if len(links) == 2:
        return f"{links[0]} and {links[1]}"
    return f"{', '.join(links[:-1])}, and {links[-1]}"


def _format_unpublicized_narrative(items: list[dict]) -> str:
    """Generate narrative paragraph(s) for dev activity without press coverage."""
    if not items:
        return ""

    # Sort topics by total stars, cap at 6
    sorted_items = sorted(
        items,
        key=lambda x: sum(r.get("stars", 0) for r in x.get("github_repos", [])),
        reverse=True,
    )[:6]

    topic_parts: list[tuple[str, list[str]]] = []
    for item in sorted_items:
        topic = item.get("topic", "unknown")
        repos = sorted(
            item.get("github_repos", []),
            key=lambda r: r.get("stars", 0),
            reverse=True,
        )
        links = [_repo_link(r["full_name"]) for r in repos[:3] if r.get("full_name")]
        if links:
            topic_parts.append((topic, links))

    if not topic_parts:
        return ""

    # First paragraph: intro + first three topics
    first_batch = topic_parts[:3]
    fragments = [
        f"{topic} saw activity with {_join_links(links)}"
        for topic, links in first_batch
    ]
    para1 = (
        "Developer activity this week shows momentum in areas the tech press isn't covering. "
        + "; ".join(fragments)
        + "."
    )

    paragraphs = [para1]

    # Second paragraph for remaining topics
    if len(topic_parts) > 3:
        second_batch = topic_parts[3:]
        fragments2 = [
            f"{topic} with {_join_links(links)}" for topic, links in second_batch
        ]
        paragraphs.append("Additional activity surfaced in " + ", ".join(fragments2) + ".")

    paragraphs.append(
        "These gaps suggest that foundational developer tooling — the infrastructure "
        "that powers daily workflows — grows through community word-of-mouth rather than press cycles."
    )

    return "\n\n".join(paragraphs)


def _format_uncovered_narrative(items: list[dict]) -> str:
    """Generate a narrative paragraph for tech trends without dev activity."""
    if not items:
        return ""

    display = items[:5]

    topic_names = [item.get("topic", "unknown") for item in display]

    # Collect up to two article links across all topics
    article_links: list[str] = []
    for item in display:
        for a in item.get("techcrunch_articles", [])[:1]:
            title = a.get("title", "article")
            url = a.get("url", "")
            if url:
                article_links.append(f"[{title}]({url})")
        if len(article_links) >= 2:
            break

    if len(topic_names) == 1:
        topics_str = topic_names[0]
    elif len(topic_names) == 2:
        topics_str = f"{topic_names[0]} and {topic_names[1]}"
    else:
        topics_str = f"{', '.join(topic_names[:-1])}, and {topic_names[-1]}"

    if article_links:
        if len(article_links) == 1:
            article_str = f"Articles like {article_links[0]} generated buzz"
        else:
            article_str = (
                f"Articles like {article_links[0]} and {article_links[1]} generated buzz"
            )
    else:
        article_str = "Press articles generated buzz"

    return (
        f"TechCrunch heavily covered {topics_str} this week, but GitHub shows minimal "
        f"matching developer activity. {article_str}, yet no significant new repositories "
        f"emerged in these spaces — suggesting these are still in the narrative or "
        f"announcement phase rather than implementation."
    )


def format_divergences(divergences: dict, *, reader_mode: bool = False) -> str:
    """Format divergences section into markdown.

    Args:
        divergences: Divergence data dict.
        reader_mode: When True, renders narrative paragraphs with inline repo/article
                     links instead of raw bullet lists. When False (AI prompt mode),
                     the original bullet-list format is preserved unchanged.
    """
    if not divergences:
        return ""

    uncovered = divergences.get("uncovered_tech_trends", [])
    unpublicized = divergences.get("unpublicized_dev_activity", [])

    if not uncovered and not unpublicized:
        return ""

    lines = ["\n### Divergence Analysis\n"]

    if reader_mode:
        # Narrative mode: flowing prose with inline links, no raw data dumps
        if uncovered:
            lines.append("#### 🔍 Tech Trends Without Dev Activity\n")
            lines.append(_format_uncovered_narrative(uncovered))
            lines.append("")

        if unpublicized:
            lines.append("#### 🚀 Dev Activity Without Press Coverage\n")
            lines.append(_format_unpublicized_narrative(unpublicized))
            lines.append("")
    else:
        # AI prompt mode: full raw data for model consumption — keep unchanged
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
    techcrunch_data: dict | None,
    correlation_data: dict | None,
    week: str,
    *,
    reader_mode: bool = False,
) -> str:
    """Render the press context prompt section.

    Args:
        techcrunch_data: Parsed TechCrunch crawl JSON or None.
        correlation_data: Parsed correlation JSON or None.
        week: The week string (YYYY-WNN).
        reader_mode: When True, produces reader-facing output: top-10 correlations
                     only, no AI instruction blocks, and a narrative divergence
                     conclusion instead of model directives.

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

    # In reader mode, sort correlations by confidence desc then hype_risk severity
    if reader_mode and correlations:
        correlations = sorted(
            correlations,
            key=lambda c: (
                -c.get("correlation_confidence", 0.0),
                -_HYPE_RISK_SEVERITY.get(c.get("hype_risk", "none"), 0),
            ),
        )

    top_n = 10 if reader_mode else None

    # Render template
    rendered = template.replace("{date}", week)
    rendered = rendered.replace("{article_count}", str(article_count))
    rendered = rendered.replace("{articles_list}", format_articles_list(articles))
    rendered = rendered.replace("{correlation_count}", str(correlation_count))
    rendered = rendered.replace(
        "{correlations_list}", format_correlations_list(correlations, top_n=top_n)
    )

    # Strip the AI-only ### Instructions block in reader mode
    if reader_mode:
        instructions_marker = "\n### Instructions\n"
        if instructions_marker in rendered:
            rendered = rendered[: rendered.index(instructions_marker)]

    # Append divergences section
    divergence_section = format_divergences(divergences, reader_mode=reader_mode)
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
