"""Resolve stable GitHub repository IDs for the tracked repository corpus.

Historical crawl snapshots never captured GitHub's numeric repository `id`, so
`observatory_repos.repository_key()` falls back to a normalized full-name key for
every history built from them. That fallback key breaks identity continuity across
GitHub renames.

This script checks each repository lacking a stable ID against the live GitHub API
(read-only `GET /repos/{full_name}`) and records the result in a reviewable JSON
file consumed by `observatory_repos.load_identity_backfill()`:

* HTTP 200 -> the repository's current `id`/`node_id` are recorded as "found" and
  are threaded into identity resolution on the next run of `observatory_repos.py`.
* HTTP 404 -> recorded as "not_found", reviewed deletion evidence equivalent to a
  manual `[repo_pages.lifecycle]` override (folded in via
  `merge_identity_backfill_overrides()`).
* Any other outcome (rate limiting, network errors, unexpected status) is recorded
  as "error" and left for a later run; it never implies deletion.

Sponsor decision (jmservera, 2026-08-05): backfill stable IDs for the production
corpus; where a repository cannot be found, treat the confirmed absence as deletion
evidence rather than as an unresolved risk, since deleted repositories are an
expected outcome regardless of identity strategy.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import observatory_repos
from scripts.crawl import API_ROOT, GitHubClient

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_CONFIG_ERROR = 2

DEFAULT_OUTPUT = Path("data/derived/observatory/repo-identity-backfill.json")
PROGRESS_INTERVAL = 25


def collect_pending_full_names(root: Path) -> dict[str, str]:
    """Return normalized full_name -> current display full_name for repos missing a stable ID."""
    config = observatory_repos.load_config(root)
    ledger = observatory_repos.load_lifecycle_ledger(config["ledger_path"])
    histories = observatory_repos.load_repository_histories(root, config.get("lifecycle"), ledger)
    return {
        observatory_repos.normalize_full_name(history.display_name): history.display_name
        for history in histories.values()
        if not history.github_id
    }


def write_backfill_output(path: Path, entries: dict[str, dict[str, Any]]) -> None:
    payload = {
        "schema_version": 1,
        "source": "scripts/backfill_repo_identity.py",
        "entries": {key: entries[key] for key in sorted(entries)},
    }
    observatory_repos.write_json_atomically(path, payload)


def check_repository(client: GitHubClient, full_name: str, *, checked_at: str) -> dict[str, Any]:
    try:
        entry = client.get_json_entry(
            f"{API_ROOT}/repos/{full_name}",
            acceptable_statuses={404},
            ttl_seconds=0,
            allow_stale=False,
            # Bounded like has_readme(): a single flaky repo must not stall the run for
            # up to the client's default 6 retries * 300s; unresolved checks are recorded
            # as "error" (never inferred as deletion) and retried on the next run.
            max_retries=3,
            max_delay_seconds=60.0,
        )
    except RuntimeError as exc:
        return {"status": "error", "checked_at": checked_at, "detail": str(exc)}
    if entry.status == 404:
        return {"status": "not_found", "checked_at": checked_at}
    payload = entry.payload if isinstance(entry.payload, dict) else {}
    github_id = payload.get("id")
    if github_id is None:
        return {
            "status": "error",
            "checked_at": checked_at,
            "detail": "GitHub API returned 200 without a repository id",
        }
    return {
        "status": "found",
        "github_id": str(github_id),
        "node_id": str(payload["node_id"]) if payload.get("node_id") else None,
        "resolved_full_name": payload.get("full_name"),
        "checked_at": checked_at,
    }


def run_backfill(
    root: Path,
    output_path: Path,
    *,
    limit: int | None = None,
    dry_run: bool = False,
    token: str | None = None,
    client: GitHubClient | None = None,
) -> dict[str, int]:
    pending = collect_pending_full_names(root)
    existing = observatory_repos.load_identity_backfill(output_path)
    to_check = [name for name in sorted(pending) if name not in existing]
    if limit is not None:
        to_check = to_check[:limit]

    counts = {
        "pending_total": len(pending),
        "already_checked": len(existing),
        "to_check": len(to_check),
        "found": 0,
        "not_found": 0,
        "error": 0,
    }
    if dry_run or not to_check:
        return counts

    if client is None:
        if not token:
            raise ValueError("GITHUB_TOKEN is required to check live repository identity")
        client = GitHubClient(token, cache_dir=root / "data" / "cache" / "identity_backfill")
    results = dict(existing)
    checked_at = date.today().isoformat()
    for index, normalized_full_name in enumerate(to_check, start=1):
        display_full_name = pending[normalized_full_name]
        result = check_repository(client, display_full_name, checked_at=checked_at)
        results[normalized_full_name] = result
        counts[result["status"]] += 1
        if index % PROGRESS_INTERVAL == 0 or index == len(to_check):
            write_backfill_output(output_path, results)
            print(
                f"[backfill] {index}/{len(to_check)} checked "
                f"(found={counts['found']} not_found={counts['not_found']} error={counts['error']})",
                file=sys.stderr,
            )
    write_backfill_output(output_path, results)
    return counts


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None, help="Backfill JSON output path.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Check at most this many not-yet-resolved repositories, for smoke testing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report how many repositories are pending without calling the GitHub API.",
    )
    return parser


def main() -> int:
    args = create_parser().parse_args()
    root = args.root.resolve()
    output_path = (args.output or (root / DEFAULT_OUTPUT)).resolve()
    token = os.environ.get("GITHUB_TOKEN")
    if not args.dry_run and not token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    try:
        counts = run_backfill(
            root, output_path, limit=args.limit, dry_run=args.dry_run, token=token
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_FAILURE
    print(json.dumps(counts, indent=2, sort_keys=True))
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
