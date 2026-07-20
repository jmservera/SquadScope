#!/usr/bin/env python3
"""Render the press context prompt section with TechCrunch and correlation data.

Reads crawl data and correlation data, then renders the press context
prompt template with real values. Output can be piped into the analyzer.

Usage:
    python scripts/render_press_context.py [--topic ai-ml] [--week 2026-W21]
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Allow imports when run from repo root or scripts/
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from topic_paths import analyzed_dir, raw_dir  # noqa: E402

PRESS_CONTEXT_TOKEN_BUDGET = 8000
PRESS_CONTEXT_CHAR_BUDGET = PRESS_CONTEXT_TOKEN_BUDGET * 4
MAX_RENDERED_ARTICLES = 40
MAX_RENDERED_CORRELATIONS = 20
GITHUB_REPO_FULL_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

# Single source of truth for the "no press this week" sentinel. This is a
# NON-EMPTY string, so downstream code must use NO_PRESS_SENTINEL_MARKER to
# detect it rather than treating any non-empty press_content as real press.
NO_PRESS_SENTINEL = (
    "No press data available for this week. Analyze repos based on GitHub signals only."
)
NO_PRESS_SENTINEL_MARKER = re.compile(r"no press data available for this week", re.IGNORECASE)


def validate_https_url(url: str, *, label: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError(f"{label} must use HTTPS: {url}")
    if parsed.username or parsed.password:
        raise ValueError(f"{label} must not include credentials: {url}")
    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        raise ValueError(f"{label} must include a hostname: {url}")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{label} has an invalid port: {url}") from exc
    if port not in (None, 443):
        raise ValueError(f"{label} must not use unexpected ports: {url}")


def _escape_markdown_url(url: str) -> str:
    """Escape parentheses in URLs used inside markdown link syntax [text](url).

    A bare ')' in the URL would prematurely close the markdown link, potentially
    allowing content injection in the rendered prompt.
    """
    return url.replace("(", "%28").replace(")", "%29")


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
    from sanitize_repo_content import sanitize_text

    if not articles:
        return "- (none)"
    lines = []
    for article in articles[:MAX_RENDERED_ARTICLES]:
        title = sanitize_text(
            article.get("title", "Untitled"),
            max_length=200,
            label="article_title",
        )
        url = sanitize_text(
            article.get("url", ""),
            max_length=300,
            label="article_url",
        )
        categories = [
            sanitize_text(c, max_length=50, label="article_category")
            for c in article.get("categories", [])
            if isinstance(c, str)
        ]
        source = sanitize_text(
            article.get("source", "unknown"),
            max_length=100,
            label="article_source",
        )
        published_at = sanitize_text(
            article.get("published_at", ""),
            max_length=20,
            label="article_published_at",
        )
        cat_str = f" [{', '.join(categories)}]" if categories else ""
        source_str = f" — {source}"
        if published_at:
            source_str += f", {published_at[:10]}"
        if url:
            lines.append(f"- [{title}]({_escape_markdown_url(url)}){cat_str}{source_str}")
        else:
            lines.append(f"- {title}{cat_str}{source_str}")
    omitted = len(articles) - MAX_RENDERED_ARTICLES
    if omitted > 0:
        lines.append(f"…and {omitted} more relevant articles within budget")
    return "\n".join(lines)


_HYPE_RISK_SEVERITY: dict[str, int] = {"high": 3, "medium": 2, "low": 1, "none": 0}


def _fetch_readme_snippet(full_name: str, max_chars: int = 500) -> str:
    """Fetch the first max_chars of a repo README from raw.githubusercontent.com.

    Returns an empty string on any failure (network error, 404, timeout).
    Should only be called in reader_mode=True paths.
    """
    if not GITHUB_REPO_FULL_NAME_RE.fullmatch(full_name):
        return ""
    url = f"https://raw.githubusercontent.com/{full_name}/HEAD/README.md"
    try:
        validate_https_url(url, label="README URL")
        req = urllib.request.Request(url, headers={"User-Agent": "SquadScope/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310
            raw = resp.read(max_chars * 3)
            return raw.decode("utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def _extract_readme_description(snippet: str) -> str:
    """Return the first readable descriptive line from a README snippet.

    Skips headings, badge lines, image tags, and blank lines.
    Trims each candidate line to the last complete sentence boundary
    (.  !  ?) so truncated snippets never show a broken mid-sentence tail.
    If no sentence boundary is found within a line, that line is skipped.
    Returns an empty string if nothing usable is found.
    """
    for line in snippet.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("#", "!", "<", "|", "[")):
            continue
        # Strip markdown formatting: links → text, remove bold/italic/code, strip HTML
        line = re.sub(r"!\[.*?\]\(.*?\)", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"[*_`>]", "", line)
        line = line.strip()
        if not line:
            continue
        # Trim to the last complete sentence boundary (. ! ? followed by space or end)
        last_boundary = -1
        for i in range(len(line) - 1, -1, -1):
            if line[i] in ".!?" and (i + 1 >= len(line) or line[i + 1] == " "):
                last_boundary = i
                break
        if last_boundary < 0:
            # No sentence boundary — drop this line to avoid broken sentences
            continue
        line = line[: last_boundary + 1].strip(" .,;:")
        if len(line) >= 20:
            return line
    return ""


def _format_correlations_narrative(correlations: list[dict], articles: list[dict]) -> str:
    """Generate narrative paragraphs explaining press-to-code correlations.

    Groups correlations by GitHub org, fetches README snippets for top repos,
    and produces 1–3 prose paragraphs with inline links to repos and articles.
    Only called in reader_mode=True — README network fetches happen here.
    """
    if not correlations:
        return "(No significant press correlations this week.)"

    # URL → title lookup for inline article links
    url_to_title: dict[str, str] = {
        a["url"]: a["title"] for a in articles if a.get("url") and a.get("title")
    }

    # Sort correlations by confidence desc, hype_risk severity desc
    sorted_corrs = sorted(
        correlations,
        key=lambda c: (
            -c.get("correlation_confidence", 0.0),
            -_HYPE_RISK_SEVERITY.get(c.get("hype_risk", "none"), 0),
        ),
    )

    # Group by org (first segment of "owner/repo")
    org_groups: dict[str, list[dict]] = {}
    for corr in sorted_corrs:
        repo = corr.get("repo", "")
        if not repo:
            continue
        org = repo.split("/")[0]
        org_groups.setdefault(org, []).append(corr)

    def _group_score(corrs: list[dict]) -> float:
        return sum(c.get("correlation_confidence", 0.0) for c in corrs)

    top_groups = sorted(
        org_groups.items(),
        key=lambda kv: _group_score(kv[1]),
        reverse=True,
    )[:4]

    # Fetch README snippets for the top repos across groups (max 6 total)
    repos_to_fetch: list[str] = []
    for _, group_corrs in top_groups:
        for corr in group_corrs[:2]:
            repo = corr.get("repo", "")
            if repo and repo not in repos_to_fetch and len(repos_to_fetch) < 6:
                repos_to_fetch.append(repo)

    readme_snippets: dict[str, str] = {}
    for repo in repos_to_fetch:
        snippet = _fetch_readme_snippet(repo)
        if snippet:
            readme_snippets[repo] = snippet

    total = len(correlations)
    paragraphs: list[str] = []

    for idx, (org, group_corrs) in enumerate(top_groups[:3]):
        # Collect up to 2 article links for this group
        article_links: list[str] = []
        seen_article_urls: set[str] = set()
        for corr in group_corrs:
            for url in corr.get("matched_articles", []):
                if url not in seen_article_urls and len(article_links) < 2:
                    seen_article_urls.add(url)
                    title = url_to_title.get(url, "")
                    if title:
                        article_links.append(f"[{title}]({_escape_markdown_url(url)})")

        # Collect up to 3 repo links with optional README description
        repo_parts: list[str] = []
        for corr in group_corrs[:3]:
            repo = corr.get("repo", "")
            if not repo:
                continue
            link = _repo_link(repo)
            desc = _extract_readme_description(readme_snippets.get(repo, ""))
            repo_parts.append(f"{link} — {desc}" if desc else link)

        if not repo_parts:
            continue

        repos_str = _join_links(repo_parts)

        if article_links:
            arts_str = _join_links(article_links)
            if idx == 0:
                para = (
                    f"This week's external press coverage closely tracks developer activity "
                    f"across {total} repos. {org.capitalize()} featured prominently: "
                    f"coverage of {arts_str} aligns with activity in {repos_str}."
                )
            else:
                para = (
                    f"{org.capitalize()}'s press footprint also intersects with GitHub: "
                    f"coverage of {arts_str} tracks activity in {repos_str}."
                )
        else:
            if idx == 0:
                para = (
                    f"This week's external press coverage closely tracks developer activity "
                    f"across {total} repos. {org.capitalize()} shows the strongest signal, "
                    f"with {repos_str} seeing notable GitHub traction."
                )
            else:
                para = (
                    f"{org.capitalize()} also shows strong press-to-code correlation, "
                    f"with activity in {repos_str}."
                )

        paragraphs.append(para)

    return (
        "\n\n".join(paragraphs) if paragraphs else "(No significant press correlations this week.)"
    )


def format_correlations_list(
    correlations: list[dict],
    *,
    top_n: int | None = None,
    reader_mode: bool = False,
    articles: list[dict] | None = None,
) -> str:
    """Format correlations into a markdown list or narrative prose.

    Args:
        correlations: List of correlation dicts.
        top_n: When set (and reader_mode=False), show only the top N entries
               (sorted by confidence desc, then hype_risk severity desc) and
               append a "…and N more" summary line.
        reader_mode: When True, delegate to _format_correlations_narrative()
                     which produces prose paragraphs with inline links. top_n
                     is ignored in this mode.
        articles: Article list used by the narrative formatter for URL→title
                  lookup. Ignored when reader_mode=False.
    """
    if not correlations:
        return "- (none)"

    if reader_mode:
        return _format_correlations_narrative(correlations, articles or [])

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

    from sanitize_repo_content import sanitize_text as _sanitize

    lines = []
    for corr in display:
        repo = corr.get("repo", "unknown")
        match_type = corr.get("match_type", "unknown")
        confidence = corr.get("correlation_confidence", 0.0)
        strength = corr.get("correlation_strength", corr.get("confidence_label", "unknown"))
        hype_risk = corr.get("hype_risk", "none")
        details = corr.get("matched_article_details", [])
        sources = sorted(
            {
                source
                for detail in details
                for source in detail.get("sources", [detail.get("source", "unknown")])
            }
        )
        citation = ""
        if details:
            first = details[0]
            title = _sanitize(
                first.get("title", "article"),
                max_length=200,
                label="correlation_article_title",
            )
            url = _sanitize(
                first.get("url", ""),
                max_length=300,
                label="correlation_article_url",
            )
            citation = (
                f", cited: [{title}]({_escape_markdown_url(url)})" if url else f", cited: {title}"
            )
        lines.append(
            f"- {repo} — match: {match_type}, "
            f"strength: {strength}, confidence: {confidence:.1f}, "
            f"sources: {', '.join(sources) if sources else 'unknown'}, "
            f"hype_risk: {hype_risk}{citation}"
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
    fragments = [f"{topic} saw activity with {_join_links(links)}" for topic, links in first_batch]
    para1 = (
        "Developer activity this week shows momentum in areas the tech press isn't covering. "
        + "; ".join(fragments)
        + "."
    )

    paragraphs = [para1]

    # Second paragraph for remaining topics
    if len(topic_parts) > 3:
        second_batch = topic_parts[3:]
        fragments2 = [f"{topic} with {_join_links(links)}" for topic, links in second_batch]
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
        for a in item.get("news_articles", item.get("techcrunch_articles", []))[:1]:
            title = a.get("title", "article")
            url = a.get("url", "")
            if url:
                article_links.append(f"[{title}]({_escape_markdown_url(url)})")
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
            article_str = f"Articles like {article_links[0]} and {article_links[1]} generated buzz"
    else:
        article_str = "Press articles generated buzz"

    return (
        f"External press heavily covered {topics_str} this week, but GitHub shows minimal "
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
            lines.append(
                "Topics heavily covered by external press with no matching GitHub repos:\n"
            )
            for item in uncovered:
                topic = item.get("topic", "unknown")
                articles = item.get("news_articles", item.get("techcrunch_articles", []))
                article_refs = ", ".join(
                    f"[{a.get('title', 'article')}]({_escape_markdown_url(a.get('url', ''))})"
                    for a in articles[:3]
                )
                lines.append(f"- **{topic}**: {article_refs}")
            lines.append("")

        if unpublicized:
            lines.append("#### 🚀 Dev Activity Without Press Coverage")
            lines.append("GitHub repos/trends with no matching external press coverage:\n")
            for item in unpublicized:
                topic = item.get("topic", "unknown")
                repos = item.get("github_repos", [])
                repo_refs = ", ".join(
                    f"{r.get('full_name', '?')} (⭐{r.get('stars', 0)})" for r in repos[:3]
                )
                lines.append(f"- **{topic}**: {repo_refs}")
            lines.append("")

        lines.append("#### Divergence Instructions")
        lines.append("Use divergences to identify:")
        lines.append("- 🔮 Where industry is moving but devs haven't caught up")
        lines.append("- 💡 Where devs are innovating ahead of media attention")
        lines.append("- 📊 Opportunity gaps between narrative and reality")

    return "\n".join(lines)


def _source_caveats(techcrunch_data: dict | None, correlation_data: dict | None) -> str:
    """Render concise partial-failure caveats from crawl/correlation metadata."""
    metadata: dict = {}
    if techcrunch_data:
        metadata = techcrunch_data.get("metadata", {})
    corr_sources = {}
    if correlation_data:
        corr_sources = correlation_data.get("metadata", {}).get("news_sources", {})

    requested = metadata.get("sources_requested") or corr_sources.get("sources_requested") or []
    succeeded = metadata.get("sources_succeeded") or corr_sources.get("sources_succeeded") or []
    failed = metadata.get("sources_failed") or corr_sources.get("sources_failed") or []
    errors = metadata.get("errors") or corr_sources.get("errors") or []
    if not requested and not failed:
        return ""
    lines = [
        "### Source Coverage",
        f"- Sources requested: {', '.join(requested) if requested else 'unknown'}",
        f"- Sources succeeded: {', '.join(succeeded) if succeeded else 'none'}",
    ]
    if failed:
        lines.append(f"- Partial crawl caveat: failed sources: {', '.join(failed)}")
        for error in errors[:3]:
            lines.append(
                f"  - {error.get('source', 'unknown')}: "
                f"{error.get('error_class', 'error')} {error.get('error', '')}".strip()
            )
    return "\n".join(lines)


def _source_coverage(
    techcrunch_data: dict | None, correlation_data: dict | None
) -> dict[str, list[str]]:
    metadata = techcrunch_data.get("metadata", {}) if techcrunch_data else {}
    corr_sources = (
        correlation_data.get("metadata", {}).get("news_sources", {}) if correlation_data else {}
    )
    requested = metadata.get("sources_requested") or corr_sources.get("sources_requested") or []
    succeeded = metadata.get("sources_succeeded") or corr_sources.get("sources_succeeded") or []
    failed = metadata.get("sources_failed") or corr_sources.get("sources_failed") or []
    return {
        "requested": [str(item) for item in requested],
        "succeeded": [str(item) for item in succeeded],
        "failed": [str(item) for item in failed],
    }


def estimate_tokens(markdown: str) -> int:
    """Return a rough token estimate used for telemetry and hard budget checks."""
    return max(1, (len(markdown) + 3) // 4)


def press_token_estimate(content: str) -> int:
    """Return 0 for empty content or no-press sentinel so gate fallback matches path logic."""
    stripped = content.strip()
    if not stripped or NO_PRESS_SENTINEL_MARKER.search(stripped):
        return 0
    return estimate_tokens(stripped)


def enforce_press_context_budget(markdown: str) -> str:
    """Keep press context below the documented token budget."""
    if estimate_tokens(markdown) <= PRESS_CONTEXT_TOKEN_BUDGET:
        return markdown
    budget_note = (
        "\n\n### Budget Notice\n"
        f"Press context truncated to ~{PRESS_CONTEXT_TOKEN_BUDGET} tokens; "
        "citations and source caveats above are prioritized.\n"
    )
    keep_chars = max(0, PRESS_CONTEXT_CHAR_BUDGET - len(budget_note))
    truncated = markdown[:keep_chars].rsplit("\n", 1)[0]
    return truncated + budget_note


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
        return NO_PRESS_SENTINEL

    template_path = _REPO_ROOT / "prompts" / "analyze-press-context.md"
    template = template_path.read_text(encoding="utf-8")

    # Extract articles (filter to relevant ones)
    articles = []
    if techcrunch_data:
        all_articles = techcrunch_data.get("articles", [])
        articles = [a for a in all_articles if a.get("relevance_score", 0) >= 0.4]

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

    top_n = MAX_RENDERED_CORRELATIONS if reader_mode else None

    # Render template
    source_label = "External news"
    rendered = template.replace("TechCrunch", source_label)
    rendered = rendered.replace("{date}", week)
    rendered = rendered.replace("{article_count}", str(article_count))
    rendered = rendered.replace("{articles_list}", format_articles_list(articles))
    rendered = rendered.replace("{correlation_count}", str(correlation_count))
    rendered = rendered.replace(
        "{correlations_list}",
        format_correlations_list(
            correlations,
            top_n=top_n,
            reader_mode=reader_mode,
            articles=articles,
        ),
    )

    # Strip the AI-only ### Instructions block in reader mode
    if reader_mode:
        instructions_marker = "\n### Instructions\n"
        if instructions_marker in rendered:
            rendered = rendered[: rendered.index(instructions_marker)]
        # Remove the count header "N repos have press correlation:" — narrative
        # paragraphs are self-contained; the raw count line is noise in reader mode.
        rendered = re.sub(r"\d+ repos have press correlation:\n", "", rendered)

    # Append divergences section
    divergence_section = format_divergences(divergences, reader_mode=reader_mode)
    if divergence_section:
        rendered += "\n" + divergence_section

    caveats = _source_caveats(techcrunch_data, correlation_data)
    if caveats:
        rendered += "\n\n" + caveats

    rendered += (
        "\n\n### Press Context Telemetry\n"
        f"- token_estimate: {estimate_tokens(rendered)}\n"
        f"- token_budget: {PRESS_CONTEXT_TOKEN_BUDGET}\n"
        f"- article_limit: {MAX_RENDERED_ARTICLES}\n"
        f"- articles_retained: {min(article_count, MAX_RENDERED_ARTICLES)}\n"
        f"- articles_dropped: {max(0, article_count - MAX_RENDERED_ARTICLES)}\n"
        f"- correlation_limit: {MAX_RENDERED_CORRELATIONS if reader_mode else 'unbounded-input'}\n"
        f"- correlations_retained: {min(correlation_count, MAX_RENDERED_CORRELATIONS) if reader_mode else correlation_count}\n"
        f"- correlations_dropped: {max(0, correlation_count - MAX_RENDERED_CORRELATIONS) if reader_mode else 0}\n"
    )
    coverage = _source_coverage(techcrunch_data, correlation_data)
    rendered += (
        f"- sources_requested: {', '.join(coverage['requested']) if coverage['requested'] else 'unknown'}\n"
        f"- sources_succeeded: {', '.join(coverage['succeeded']) if coverage['succeeded'] else 'unknown'}\n"
        f"- sources_failed: {', '.join(coverage['failed']) if coverage['failed'] else 'none'}\n"
    )

    return enforce_press_context_budget(rendered)


def resolve_paths(topic: str | None, week: str) -> tuple[Path, Path]:
    """Resolve file paths for external news and correlation data."""
    raw_path = raw_dir(topic)
    external_path = raw_path / f"{week}-external-news.json"
    legacy_path = raw_path / f"{week}-techcrunch.json"
    tc_path = legacy_path if legacy_path.exists() and not external_path.exists() else external_path
    corr_path = analyzed_dir(topic) / f"{week}-correlations.json"
    return tc_path, corr_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render press context prompt section")
    parser.add_argument("--topic", default=None, help="Topic ID (e.g., ai-ml)")
    parser.add_argument("--week", default=None, help="Week in YYYY-WNN format (default: current)")
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
