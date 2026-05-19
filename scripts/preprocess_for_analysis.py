#!/usr/bin/env python3
"""Pre-process raw crawl JSON to reduce token count for analysis prompts.

Extracts only fields needed by the analysis prompt, truncates descriptions,
and computes basic signals to produce a compact JSON suitable for LLM input.

CLI:
    python scripts/preprocess_for_analysis.py \
        --input data/raw/2026-W21.json \
        --output data/raw/2026-W21-compact.json \
        --max-desc-length 200
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def estimate_tokens(text: str) -> int:
    """Rough token estimate: characters / 4."""
    return len(text) // 4


def compute_age_days(created_at: str | None, reference: datetime | None = None) -> int | None:
    """Compute age in days from created_at ISO timestamp."""
    if not created_at:
        return None
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        ref = reference or datetime.now(timezone.utc)
        return max(0, (ref - created).days)
    except (ValueError, TypeError):
        return None


def compact_repo(repo: dict, max_desc: int, reference_date: datetime | None = None) -> dict:
    """Extract and compact a single repo entry."""
    desc = (repo.get("description") or "")[:max_desc]
    return {
        "name": repo.get("name", ""),
        "desc": desc,
        "stars": repo.get("stars", 0),
        "gained": repo.get("stars_gained", repo.get("gained", 0)),
        "topics": repo.get("topics", []),
        "lang": repo.get("language"),
        "age_days": compute_age_days(repo.get("created_at"), reference_date),
    }


def compute_signals(repos: list[dict]) -> dict:
    """Compute aggregate signals from the compacted repo list."""
    topic_counts: dict[str, int] = {}
    for r in repos:
        for t in r.get("topics", []):
            topic_counts[t] = topic_counts.get(t, 0) + 1
    top_topics = sorted(topic_counts.items(), key=lambda x: -x[1])[:10]
    return {"top_topics": [t for t, _ in top_topics]}


def preprocess(data: dict, max_desc: int = 200, reference_date: datetime | None = None) -> dict:
    """Transform raw crawl JSON into compact analysis format."""
    original_text = json.dumps(data)
    original_tokens = estimate_tokens(original_text)

    # Combine new_repos and trending_repos
    all_repos = data.get("new_repos", []) + data.get("trending_repos", [])

    # Deduplicate by name
    seen = set()
    unique_repos = []
    for r in all_repos:
        name = r.get("name", "")
        if name not in seen:
            seen.add(name)
            unique_repos.append(r)

    compacted = [compact_repo(r, max_desc, reference_date) for r in unique_repos]
    signals = compute_signals(compacted)

    result = {
        "week": data.get("week", ""),
        "repos": compacted,
        "signals": signals,
    }

    compact_text = json.dumps(result)
    compact_tokens = estimate_tokens(compact_text)
    reduction_pct = round((1 - compact_tokens / original_tokens) * 100) if original_tokens > 0 else 0

    result["stats"] = {
        "original_tokens_est": original_tokens,
        "compact_tokens_est": compact_tokens,
        "reduction_pct": reduction_pct,
    }

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-process raw JSON for analysis")
    parser.add_argument("--input", required=True, help="Path to raw crawl JSON")
    parser.add_argument("--output", help="Output path (default: input with -compact suffix)")
    parser.add_argument("--max-desc-length", type=int, default=200, help="Max description length")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + "-compact")

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    result = preprocess(data, max_desc=args.max_desc_length)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    stats = result["stats"]
    print(f"Preprocessed: {input_path} -> {output_path}")
    print(f"  Tokens: {stats['original_tokens_est']} -> {stats['compact_tokens_est']} ({stats['reduction_pct']}% reduction)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
