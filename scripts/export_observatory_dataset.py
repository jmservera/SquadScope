#!/usr/bin/env python3
"""Export the first public Claracle Observatory dataset from local crawl artifacts.

The export is intentionally read-only: it consumes checked-in files under data/
and never calls external APIs. The published CSV contains public GitHub aggregate
metadata only, derived from weekly crawl records.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_SLUG = "open-source-ai-github-projects-2026"
DATASET_VERSION = "2026-W31"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "static" / "datasets" / DATASET_SLUG
PREFERRED_RAW_WEEKS = ("2026-W21", "2026-W22", "2026-W29", "2026-W30", "2026-W31")
RECOVERED_WEEKS = ("2026-W23", "2026-W24", "2026-W25", "2026-W26", "2026-W27", "2026-W28")
CSV_COLUMNS = [
    "rank_by_latest_stars",
    "repository",
    "url",
    "primary_language",
    "latest_license",
    "first_seen_week",
    "last_seen_week",
    "weeks_observed",
    "latest_stars",
    "first_observed_stars",
    "observed_star_change",
    "max_forks_observed",
    "seen_in_trending",
    "seen_in_new",
    "top_topics",
]
AI_KEYWORDS = {
    "agent",
    "agents",
    "ai",
    "ai-agent",
    "ai-agents",
    "ai-assistant",
    "ai-coding",
    "ai-engineering",
    "ai-tools",
    "artificial-intelligence",
    "autonomous-agent",
    "chatbot",
    "claude",
    "claude-code",
    "codex",
    "computer-vision",
    "deep-learning",
    "diffusion",
    "generative-ai",
    "gpt",
    "huggingface",
    "langchain",
    "large-language-models",
    "llm",
    "llms",
    "machine-learning",
    "mcp",
    "model-context-protocol",
    "multi-agent",
    "openai",
    "rag",
    "semantic-search",
    "stable-diffusion",
    "transformer",
    "vibe-coding",
}


@dataclass
class RepoAggregate:
    repository: str
    url: str = ""
    first_seen_week: str = ""
    last_seen_week: str = ""
    weeks_observed: set[str] = field(default_factory=set)
    stars_by_week: dict[str, int] = field(default_factory=dict)
    max_forks_observed: int = 0
    languages: Counter[str] = field(default_factory=Counter)
    licenses: Counter[str] = field(default_factory=Counter)
    topics: Counter[str] = field(default_factory=Counter)
    buckets: set[str] = field(default_factory=set)

    def add(self, week: str, bucket: str, record: dict[str, Any]) -> None:
        self.weeks_observed.add(week)
        self.buckets.add(bucket)
        self.first_seen_week = min(self.first_seen_week or week, week)
        self.last_seen_week = max(self.last_seen_week or week, week)
        self.url = str(record.get("url") or self.url)

        stars = record.get("stars")
        if isinstance(stars, int):
            self.stars_by_week[week] = max(stars, self.stars_by_week.get(week, stars))

        forks = record.get("forks")
        if isinstance(forks, int):
            self.max_forks_observed = max(self.max_forks_observed, forks)

        language = record.get("language")
        if isinstance(language, str) and language.strip():
            self.languages[language.strip()] += 1

        license_name = record.get("license")
        if isinstance(license_name, str) and license_name.strip():
            self.licenses[license_name.strip()] += 1

        for topic in record.get("topics") or []:
            if isinstance(topic, str) and topic.strip():
                self.topics[topic.strip().lower()] += 1

    @property
    def latest_stars(self) -> int:
        return self.stars_by_week.get(self.last_seen_week, 0)

    @property
    def first_stars(self) -> int:
        return self.stars_by_week.get(self.first_seen_week, 0)

    @property
    def observed_star_change(self) -> int:
        if not self.stars_by_week:
            return 0
        return self.latest_stars - self.first_stars

    def row(self, rank: int) -> dict[str, str | int]:
        return {
            "rank_by_latest_stars": rank,
            "repository": self.repository,
            "url": self.url,
            "primary_language": self.languages.most_common(1)[0][0] if self.languages else "",
            "latest_license": self.licenses.most_common(1)[0][0] if self.licenses else "",
            "first_seen_week": self.first_seen_week,
            "last_seen_week": self.last_seen_week,
            "weeks_observed": len(self.weeks_observed),
            "latest_stars": self.latest_stars,
            "first_observed_stars": self.first_stars,
            "observed_star_change": self.observed_star_change,
            "max_forks_observed": self.max_forks_observed,
            "seen_in_trending": "true" if "trending_repos" in self.buckets else "false",
            "seen_in_new": "true" if "new_repos" in self.buckets else "false",
            "top_topics": "|".join(topic for topic, _count in self.topics.most_common(8)),
        }


def discover_source_paths(data_root: Path) -> list[Path]:
    paths: list[Path] = []
    for week in PREFERRED_RAW_WEEKS:
        paths.append(data_root / "raw" / f"{week}.json")
    for week in RECOVERED_WEEKS:
        paths.append(data_root / "archive" / "recovered-W23-W29" / week / f"{week}.json")
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing expected source files: " + ", ".join(missing))
    return sorted(paths, key=lambda path: json.loads(path.read_text(encoding="utf-8"))["week"])


def is_ai_adjacent(record: dict[str, Any]) -> bool:
    text_parts = [
        str(record.get("full_name") or ""),
        str(record.get("name") or ""),
        str(record.get("description") or ""),
    ]
    text_parts.extend(str(topic) for topic in record.get("topics") or [])
    normalized = " ".join(text_parts).lower().replace("_", "-").replace("/", " ").replace(".", " ")
    tokens = set(normalized.replace(",", " ").replace(":", " ").split())
    return bool(tokens & AI_KEYWORDS) or any(
        phrase in normalized
        for phrase in (
            "artificial intelligence",
            "machine learning",
            "large language model",
            "model context protocol",
            "prompt engineering",
        )
    )


def load_aggregates(
    source_paths: list[Path],
) -> tuple[dict[str, RepoAggregate], dict[str, int], int]:
    aggregates: dict[str, RepoAggregate] = {}
    observation_counts: dict[str, int] = {}
    total_source_observations = 0
    for source_path in source_paths:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        week = str(payload["week"])
        observation_counts[week] = 0
        for bucket in ("trending_repos", "new_repos"):
            for record in payload.get(bucket, []):
                total_source_observations += 1
                if not is_ai_adjacent(record):
                    continue
                full_name = record.get("full_name")
                if not isinstance(full_name, str) or "/" not in full_name:
                    continue
                key = full_name.lower()
                aggregate = aggregates.setdefault(key, RepoAggregate(repository=full_name))
                aggregate.add(week, bucket, record)
                observation_counts[week] += 1
    return aggregates, observation_counts, total_source_observations


def sorted_aggregates(aggregates: dict[str, RepoAggregate]) -> list[RepoAggregate]:
    return sorted(
        aggregates.values(),
        key=lambda repo: (-repo.latest_stars, repo.repository.lower()),
    )


def build_summary(
    repos: list[RepoAggregate],
    source_paths: list[Path],
    observation_counts: dict[str, int],
    total_source_observations: int,
) -> dict[str, Any]:
    language_counts: Counter[str] = Counter()
    license_counts: Counter[str] = Counter()
    topic_counts: Counter[str] = Counter()
    recurring = 0
    trending_seen = 0
    new_seen = 0
    for repo in repos:
        if len(repo.weeks_observed) >= 4:
            recurring += 1
        if "trending_repos" in repo.buckets:
            trending_seen += 1
        if "new_repos" in repo.buckets:
            new_seen += 1
        if repo.languages:
            language_counts[repo.languages.most_common(1)[0][0]] += 1
        if repo.licenses:
            license_counts[repo.licenses.most_common(1)[0][0]] += 1
        topic_counts.update(dict(repo.topics.most_common(5)))

    return {
        "dataset": DATASET_SLUG,
        "version": DATASET_VERSION,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "Read-only export from checked-in Claracle weekly GitHub crawl artifacts.",
        "selection_rule": (
            "Repository records are included when public name, description, or topics contain "
            "AI-adjacent terms such as AI, LLM, agent, MCP, RAG, machine learning, or model "
            "context protocol."
        ),
        "license": "MIT",
        "row_count": len(repos),
        "weeks": sorted(observation_counts),
        "weekly_observation_counts": observation_counts,
        "exported_repo_observations": sum(observation_counts.values()),
        "total_source_repo_observations_screened": total_source_observations,
        "recurring_repository_count_min_4_weeks": recurring,
        "repositories_seen_in_trending": trending_seen,
        "repositories_seen_in_new": new_seen,
        "top_languages_by_repository_count": language_counts.most_common(12),
        "top_licenses_by_repository_count": license_counts.most_common(12),
        "top_topics_by_repository_mentions": topic_counts.most_common(20),
        "top_repositories_by_latest_stars": [
            {
                "repository": repo.repository,
                "latest_stars": repo.latest_stars,
                "observed_star_change": repo.observed_star_change,
                "weeks_observed": len(repo.weeks_observed),
                "url": repo.url,
            }
            for repo in repos[:25]
        ],
        "fields": CSV_COLUMNS,
        "source_files": [str(path.relative_to(PROJECT_ROOT)) for path in source_paths],
        "public_exposure_review": (
            "PASS: exported fields are repository names, GitHub URLs, public language/license/topic "
            "metadata, public star/fork counts, and derived weekly aggregates from public GitHub crawl records. "
            "No tokens, private repo data, cache payloads, user account data, or unpublished crawl calls are included."
        ),
    }


def write_csv(path: Path, repos: list[RepoAggregate]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for rank, repo in enumerate(repos, start=1):
            writer.writerow(repo.row(rank))


def write_license(path: Path) -> None:
    path.write_text(
        """MIT License

Copyright (c) 2026 Claracle contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this dataset and associated documentation files (the "Dataset"), to deal
in the Dataset without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Dataset, and to permit persons to whom the Dataset is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Dataset.

THE DATASET IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE DATASET OR THE USE OR OTHER DEALINGS IN THE
DATASET.
""",
        encoding="utf-8",
    )


def write_citation(path: Path, summary: dict[str, Any]) -> None:
    source_list = "\n".join(f"- `{source}`" for source in summary["source_files"])
    path.write_text(
        f"""# Citation and attribution

Dataset: **Claracle Open Source AI GitHub Projects 2026** (`{DATASET_SLUG}`)

License: MIT. See `LICENSE.txt`.

Suggested citation:

> Claracle contributors. "Claracle Open Source AI GitHub Projects 2026."
> Version {DATASET_VERSION}, generated from public GitHub crawl artifacts,
> {summary["generated_at"]}. https://claracle.com/datasets/{DATASET_SLUG}/top-github-projects.csv

## Sources

The dataset is a read-only aggregate of public GitHub repository metadata captured by Claracle's weekly crawl. The original public source for repository names, URLs, stars, forks, languages, licenses, and topics is GitHub repository search and public repository pages/API responses.

Checked-in Claracle artifacts used for this release:

{source_list}

## Exposure review

{summary["public_exposure_review"]}
""",
        encoding="utf-8",
    )


def export_dataset(
    output_dir: Path = DEFAULT_OUTPUT_DIR, data_root: Path = PROJECT_ROOT / "data"
) -> dict[str, Any]:
    source_paths = discover_source_paths(data_root)
    aggregates, observation_counts, total_source_observations = load_aggregates(source_paths)
    repos = sorted_aggregates(aggregates)
    summary = build_summary(repos, source_paths, observation_counts, total_source_observations)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "top-github-projects.csv", repos)
    (output_dir / "dataset-metadata.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_license(output_dir / "LICENSE.txt")
    write_citation(output_dir / "CITATION.md", summary)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--data-root", type=Path, default=PROJECT_ROOT / "data")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = export_dataset(args.output_dir, args.data_root)
    print(
        f"Exported {summary['row_count']} repositories from "
        f"{summary['exported_repo_observations']} AI-adjacent observations to {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
