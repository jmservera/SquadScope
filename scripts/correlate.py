#!/usr/bin/env python3
"""Cross-source correlation engine for SquadScope.

Matches TechCrunch articles to GitHub repo activity using fuzzy matching
heuristics to identify press-correlated repositories.

Usage:
    python scripts/correlate.py [--raw data/raw/ai-ml/2026-W21.json] \
        [--techcrunch data/raw/ai-ml/2026-W21-techcrunch.json] \
        [--output data/analyzed/ai-ml/2026-W21-correlations.json] \
        [--topic ai-ml]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from scripts.topic_paths import analyzed_dir, raw_dir


def log(message: str) -> None:
    print(f"[correlate] {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Heuristic matchers
# ---------------------------------------------------------------------------


def match_direct_link(repo: dict[str, Any], articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match articles that contain a direct GitHub link to the repo."""
    repo_url = (repo.get("url") or "").rstrip("/").lower()
    full_name = (repo.get("full_name") or "").lower()
    if not repo_url and not full_name:
        return []

    matches = []
    for article in articles:
        for link in article.get("github_links", []):
            normalized = link.rstrip("/").lower()
            if normalized == repo_url or normalized.endswith(f"/{full_name}"):
                matches.append(article)
                break
    return matches


def match_org_name(repo: dict[str, Any], articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match articles whose entities contain the repo owner name."""
    owner = (repo.get("owner") or "").lower()
    if not owner or len(owner) < 2:
        return []

    matches = []
    for article in articles:
        entities = [e.lower() for e in article.get("entities", [])]
        if owner in entities:
            matches.append(article)
    return matches


def _token_overlap_ratio(a: str, b: str) -> float:
    """Compute token overlap ratio between two strings."""
    tokens_a = set(re.split(r"[\s\-_]+", a.lower()))
    tokens_b = set(re.split(r"[\s\-_]+", b.lower()))
    tokens_a.discard("")
    tokens_b.discard("")
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    return len(intersection) / min(len(tokens_a), len(tokens_b))


def fuzzy_name_score(repo_name: str, text: str) -> float:
    """Compute fuzzy match score between repo name and text."""
    if not repo_name or not text:
        return 0.0
    # SequenceMatcher ratio
    seq_score = SequenceMatcher(None, repo_name.lower(), text.lower()).ratio()
    # Token overlap
    token_score = _token_overlap_ratio(repo_name, text)
    return max(seq_score, token_score)


def match_project_name(repo: dict[str, Any], articles: list[dict[str, Any]], threshold: float = 0.6) -> list[dict[str, Any]]:
    """Match articles by fuzzy matching repo name against title/entities."""
    repo_name = repo.get("name") or ""
    if not repo_name or len(repo_name) < 3:
        return []

    matches = []
    for article in articles:
        title = article.get("title") or ""
        entities = article.get("entities", [])

        # Check title
        if fuzzy_name_score(repo_name, title) >= threshold:
            matches.append(article)
            continue

        # Check individual entities
        for entity in entities:
            if fuzzy_name_score(repo_name, entity) >= threshold:
                matches.append(article)
                break
    return matches


def match_category(repo: dict[str, Any], articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match articles whose categories overlap with repo topics."""
    topics = {t.lower() for t in (repo.get("topics") or [])}
    if not topics:
        return []

    matches = []
    for article in articles:
        categories = {c.lower() for c in (article.get("categories") or [])}
        if topics & categories:
            matches.append(article)
    return matches


def has_temporal_spike(repo: dict[str, Any], stars_threshold: int = 10) -> bool:
    """Check if repo had a stars_gained spike in the same week."""
    stars_gained = repo.get("stars_gained")
    if stars_gained is None:
        return False
    return stars_gained >= stars_threshold


# ---------------------------------------------------------------------------
# Hype risk assessment
# ---------------------------------------------------------------------------


def assess_hype_risk(confidence: float, stars_gained: int | None) -> str:
    """Assess hype risk based on correlation confidence and star velocity."""
    if confidence >= 0.8:
        if stars_gained is not None and stars_gained > 100:
            return "high"
        return "medium"
    if confidence >= 0.6:
        return "medium"
    if confidence >= 0.4:
        return "low"
    return "none"


# ---------------------------------------------------------------------------
# Main correlation logic
# ---------------------------------------------------------------------------


def correlate_repo(repo: dict[str, Any], articles: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Correlate a single repo against all articles. Returns correlation or None."""
    best_confidence = 0.0
    best_type = ""
    matched_articles: list[str] = []

    # Priority 1: Direct link match (confidence 1.0)
    direct = match_direct_link(repo, articles)
    if direct:
        best_confidence = 1.0
        best_type = "direct_link"
        matched_articles = [a["url"] for a in direct]

    # Priority 2: Org name match (confidence 0.8)
    if not matched_articles:
        org = match_org_name(repo, articles)
        if org:
            best_confidence = 0.8
            best_type = "org_name"
            matched_articles = [a["url"] for a in org]

    # Priority 3: Project name fuzzy match (confidence 0.6)
    if not matched_articles:
        fuzzy = match_project_name(repo, articles)
        if fuzzy:
            best_confidence = 0.6
            best_type = "project_name"
            matched_articles = [a["url"] for a in fuzzy]

    # Priority 4: Category correlation (confidence 0.4)
    if not matched_articles:
        cat = match_category(repo, articles)
        if cat:
            best_confidence = 0.4
            best_type = "category"
            matched_articles = [a["url"] for a in cat]

    if not matched_articles:
        return None

    # Priority 5: Temporal lag bonus
    press_correlated = True
    if has_temporal_spike(repo):
        best_confidence = min(best_confidence + 0.2, 1.0)
        press_correlated = True

    return {
        "repo": repo.get("full_name") or f"{repo.get('owner')}/{repo.get('name')}",
        "press_correlated": press_correlated,
        "correlation_confidence": round(best_confidence, 2),
        "matched_articles": matched_articles,
        "match_type": best_type,
        "hype_risk": assess_hype_risk(best_confidence, repo.get("stars_gained")),
    }


def correlate_all(repos: list[dict[str, Any]], articles: list[dict[str, Any]], week: str) -> dict[str, Any]:
    """Run correlation engine across all repos and articles."""
    correlations: list[dict[str, Any]] = []
    uncorrelated: list[str] = []

    for repo in repos:
        result = correlate_repo(repo, articles)
        if result:
            correlations.append(result)
        else:
            name = repo.get("full_name") or f"{repo.get('owner')}/{repo.get('name')}"
            uncorrelated.append(name)

    # Sort by confidence descending
    correlations.sort(key=lambda c: c["correlation_confidence"], reverse=True)

    articles_matched = len({url for c in correlations for url in c["matched_articles"]})

    return {
        "week": week,
        "correlations": correlations,
        "uncorrelated_repos": uncorrelated,
        "metadata": {
            "repos_analyzed": len(repos),
            "correlations_found": len(correlations),
            "articles_matched": articles_matched,
        },
    }


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def find_latest_file(directory: Path, pattern: str) -> Path | None:
    """Find the latest file matching a glob pattern in directory."""
    if not directory.exists():
        return None
    files = sorted(directory.glob(pattern), reverse=True)
    return files[0] if files else None


def load_json(path: Path) -> dict[str, Any]:
    """Load and return parsed JSON from a file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_week_from_filename(path: Path) -> str:
    """Extract week slug from filename like '2026-W21.json'."""
    match = re.search(r"(\d{4}-W\d{2})", path.name)
    return match.group(1) if match else "unknown"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-source correlation engine for SquadScope"
    )
    parser.add_argument(
        "--raw", default=None,
        help="Path to raw GitHub repos JSON file",
    )
    parser.add_argument(
        "--techcrunch", default=None,
        help="Path to TechCrunch articles JSON file",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path for correlations",
    )
    parser.add_argument(
        "--topic", default="general",
        help="Topic ID for path resolution (default: general)",
    )

    args = parser.parse_args(argv)
    topic = args.topic

    # Resolve raw repos file
    if args.raw:
        raw_path = Path(args.raw)
    else:
        raw_path = find_latest_file(raw_dir(topic), "[0-9]*-W[0-9]*.json")
        if raw_path is None:
            log(f"No raw data found in {raw_dir(topic)}")
            return 1

    if not raw_path.exists():
        log(f"Raw file not found: {raw_path}")
        return 1

    # Resolve TechCrunch file
    if args.techcrunch:
        tc_path = Path(args.techcrunch)
    else:
        tc_path = find_latest_file(raw_dir(topic), "*-techcrunch.json")

    # Load repos
    raw_data = load_json(raw_path)
    if isinstance(raw_data, list):
        repos = raw_data
    else:
        # The crawl output stores repos under "new_repos" and "trending_repos"
        repos = raw_data.get("repos", raw_data.get("repositories", []))
        if not repos:
            new_repos = raw_data.get("new_repos", [])
            trending_repos = raw_data.get("trending_repos", [])
            repos = new_repos + trending_repos

    # Load articles (graceful if missing)
    articles: list[dict[str, Any]] = []
    if tc_path and tc_path.exists():
        tc_data = load_json(tc_path)
        articles = tc_data if isinstance(tc_data, list) else tc_data.get("articles", [])
    else:
        log("No TechCrunch data found; producing empty correlations")

    # Determine week
    week = extract_week_from_filename(raw_path)

    # Run correlation
    result = correlate_all(repos, articles, week)

    # Write output
    if args.output:
        output_path = Path(args.output)
    else:
        out_dir = analyzed_dir(topic)
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{week}-correlations.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log(f"Wrote {output_path}: {result['metadata']['correlations_found']} correlations from {result['metadata']['repos_analyzed']} repos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
