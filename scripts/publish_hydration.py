#!/usr/bin/env python3
"""Reproduce the deploy publish-hydration reference checks in CI (NFR-011).

`deploy-site.yml` hydrates the generated content set from the canonical `publish`
branch and then depends on cross-branch references that are never validated on
`main`:

* every `content/embeds/*` `source_page` must resolve to a data page (NFR-012,
  issue #627), and
* the newest promotion record must resolve to its article and its
  `source_manifest.path`, the exact evidence the blocking post-deploy Podcaster
  smoke verifies (issue #644).

Running these checks against the hydrated tree in CI reproduces the deploy's
publish-hydration, so `main`/`publish` divergence fails CI rather than the
production deploy (NFR-011).

Usage (run as a module so the ``scripts`` package resolves):

* ``python3 -m scripts.publish_hydration paths`` prints the generated paths the
  deploy hydrates, one per line, to drive the CI hydration loop.
* ``python3 -m scripts.publish_hydration check`` validates the hydrated tree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_embed_sources import check_embed_sources  # noqa: E402
from scripts.podcaster_handoff import (  # noqa: E402
    PodcasterHandoffError,
    verify_release_evidence,
)

# Canonical list of generated paths deploy-site.yml hydrates from `publish`.
# Kept in sync with the deploy workflow by tests/test_publish_hydration.py.
GENERATED_PATHS: list[str] = [
    "content/weekly/",
    "content/monthly/",
    "content/yearly/",
    "content/topics/",
    "content/data/",
    "data/analyzed/",
    "data/raw/",
    "data/metrics/",
    "data/snapshots/",
    "data/candidates/",
    "data/published/",
    "data/taxonomy/",
    "data/topic-hubs/",
    "data/derived/observatory/",
    "static/datasets/open-source-ai-github-projects-2026/",
    "static/tools/star-velocity-explorer.json",
]


def _newest_promotion_record(root: Path) -> Path | None:
    records = sorted((root / "data" / "published").glob("*/promotion-manifest.json"))
    return records[-1] if records else None


def check_publish_references(root: Path = ROOT) -> list[str]:
    """Return human-readable problems in the hydrated content set; empty when clean.

    Mirrors the reference checks the production deploy and the blocking Podcaster
    release smoke perform, so a `main`/`publish` divergence surfaces in CI.
    """
    root = Path(root)
    problems: list[str] = [f"embed: {problem}" for problem in check_embed_sources(root)]

    record_path = _newest_promotion_record(root)
    if record_path is None:
        # The deploy's release-resolution step raises when no promotion record is
        # retained, so a missing record is a real divergence, not a clean pass.
        problems.append("promotion: no retained promotion record under data/published/")
        return problems

    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        problems.append(f"promotion: {record_path} is not readable JSON: {exc}")
        return problems

    if record.get("schema_version") != "promotion_transaction_v1":
        problems.append(
            f"promotion: {record_path} has unsupported schema {record.get('schema_version')!r}"
        )
        return problems

    article = next(
        (
            artifact
            for artifact in record.get("published_artifacts", [])
            if isinstance(artifact, dict) and artifact.get("role") == "hugo_content"
        ),
        None,
    )
    if not isinstance(article, dict) or not article.get("path") or not article.get("sha256"):
        problems.append(f"promotion: {record_path} lacks a complete hugo_content artifact")
        return problems

    try:
        verify_release_evidence(
            week=str(record.get("week") or ""),
            article_path=str(article["path"]),
            article_sha256=str(article["sha256"]),
            promotion_reference=record_path.relative_to(root),
            repo_root=root,
        )
    except PodcasterHandoffError as exc:
        problems.append(f"promotion: {record_path.name}: {exc}")

    return problems


def _cmd_paths(_: argparse.Namespace) -> int:
    for path in GENERATED_PATHS:
        print(path)
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    problems = check_publish_references(Path(args.root))
    for problem in problems:
        print(f"::error::{problem}", file=sys.stderr)
    if problems:
        return 1
    print("Publish-hydration references resolve (embeds and promotion record).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=ROOT, type=Path, help="Repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("paths", help="Print the generated paths deploy hydrates from publish.")
    subparsers.add_parser("check", help="Validate the hydrated content set's references.")
    args = parser.parse_args(argv)

    if args.command == "paths":
        return _cmd_paths(args)
    return _cmd_check(args)


if __name__ == "__main__":
    raise SystemExit(main())
