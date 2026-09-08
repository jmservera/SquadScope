#!/usr/bin/env python3
"""
Auto-dispatch detection script for podcast generation.

Detects a newly published weekly article on main, correlates it with a
publish manifest on origin/publish, and emits structured outputs for the
auto-podcast-dispatch workflow.

Detection mode (push event):
    python3 scripts/auto_dispatch_detect.py \
        --article-path content/weekly/2026/W37.md \
        --before-sha <sha> \
        --current-sha <sha>

Manual-override mode (week recovery):
    python3 scripts/auto_dispatch_detect.py \
        --article-path content/weekly/2026/W37.md \
        --current-sha <sha> \
        --observe-only

Duplicate-check mode:
    python3 scripts/auto_dispatch_detect.py \
        --check-duplicate \
        --week 2026-W37 \
        --publish-run-id 34082521901

Outputs written to $GITHUB_OUTPUT (when set) and printed to stdout.

Security notes:
- No untrusted text (commit messages, PR titles, article content) is used
  in correlation logic. Correlation is exclusively by SHA-256 of article bytes.
- PODCAST_AUTO_DISPATCH_PAUSED env var controls pause; must be literal 'true'.
- Fails closed on any missing, ambiguous, or invalid manifest evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

WEEK_RE = re.compile(r"^[0-9]{4}-W[0-9]{2}$")
RUN_ID_RE = re.compile(r"^[0-9]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_PATH_RE = re.compile(
    r"^data/candidates/([^/]+)/([^/]+)/publish-manifest\.json$"
)
ARTICLE_PATH_RE = re.compile(r"^content/weekly/(\d{4})/(W\d{2})\.md$")
NULL_SHA = "0" * 40


def set_output(key: str, value: str) -> None:
    """Write key=value to $GITHUB_OUTPUT and echo to stdout."""
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")
    print(f"  output: {key}={value}")


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
    )


def fetch_publish_branch() -> None:
    result = git("fetch", "origin", "publish", "--no-tags", check=False)
    if result.returncode != 0:
        msg = result.stderr.strip()
        print(f"::error::Could not fetch origin/publish: {msg}", file=sys.stderr)
        sys.exit(1)


def read_manifest_from_publish(path: str) -> dict:
    """Read and parse a manifest JSON from origin/publish without checkout."""
    result = subprocess.run(
        ["git", "show", f"origin/publish:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Cannot read {path!r} from origin/publish")
    return json.loads(result.stdout)


def read_manifest_bytes_from_publish(path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"origin/publish:{path}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Cannot read bytes of {path!r} from origin/publish")
    return result.stdout


def list_manifests_for_week(week: str) -> list[str]:
    """List publish-manifest.json paths under data/candidates/<week>/ on origin/publish."""
    result = git("ls-tree", "-r", "origin/publish", "--name-only", check=False)
    if result.returncode != 0:
        return []
    prefix = f"data/candidates/{week}/"
    suffix = "/publish-manifest.json"
    return [
        line
        for line in result.stdout.splitlines()
        if line.startswith(prefix) and line.endswith(suffix) and MANIFEST_PATH_RE.match(line)
    ]


def extract_week_from_article_path(article_path: str) -> tuple[str | None, str | None, str | None]:
    """
    Extract (week_slug, year, short) from article path like content/weekly/2026/W37.md.
    Returns (None, None, None) if path does not match expected format.
    """
    m = ARTICLE_PATH_RE.match(article_path)
    if not m:
        return None, None, None
    year, short = m.group(1), m.group(2)
    return f"{year}-{short}", year, short


def validate_manifest(
    manifest: dict, week: str, run_id: str, article_sha256: str
) -> tuple[bool, str]:
    """
    Validate manifest fields for eligibility.
    Fails closed: any missing/mismatched/invalid field → (False, reason).
    """
    if manifest.get("week") != week:
        return False, f"manifest.week={manifest.get('week')!r} != {week!r}"
    if str(manifest.get("run_id")) != run_id:
        return False, f"manifest.run_id={manifest.get('run_id')!r} != {run_id!r}"

    # run_mode must be 'normal'
    run_mode = manifest.get("run_mode")
    if run_mode != "normal":
        return False, f"manifest.run_mode={run_mode!r} is not 'normal'"

    # analysis.preflight.publish_eligible must be truthy
    analysis = manifest.get("analysis") or {}
    preflight = analysis.get("preflight") or {}
    if not preflight.get("publish_eligible"):
        return False, "analysis.preflight.publish_eligible is not true"

    # promotion_eligible must be truthy
    if not manifest.get("promotion_eligible"):
        return False, "promotion_eligible is not true"

    # candidate.content_sha256 must be a valid SHA-256 matching the article
    candidate = manifest.get("candidate") or {}
    content_sha256 = candidate.get("content_sha256")
    if not isinstance(content_sha256, str) or not SHA256_RE.match(content_sha256):
        return False, "candidate.content_sha256 is missing or invalid"
    if content_sha256 != article_sha256:
        return False, (
            f"SHA-256 mismatch: manifest={content_sha256!r} article={article_sha256!r}"
        )

    return True, "ok"


def detect(args: argparse.Namespace) -> None:
    """Detection flow: find eligible manifest for a newly merged weekly article."""
    print("## Auto-dispatch detection")

    # Respect pause flag (owner-controlled via repo variable)
    paused = os.environ.get("PODCAST_AUTO_DISPATCH_PAUSED", "").strip().lower()
    if paused == "true":
        print("::notice::PODCAST_AUTO_DISPATCH_PAUSED=true — dispatch deferred.")
        set_output("eligible", "false")
        set_output("status", "paused")
        return

    article_path = args.article_path
    if not article_path:
        print("::error::--article-path is required.", file=sys.stderr)
        set_output("eligible", "false")
        set_output("reason", "missing_article_path")
        sys.exit(1)

    # Validate article path format
    week, year, short = extract_week_from_article_path(article_path)
    if not week:
        print(
            f"::error::article-path must match content/weekly/YYYY/WNN.md (got: {article_path!r})",
            file=sys.stderr,
        )
        set_output("eligible", "false")
        set_output("reason", "invalid_article_path")
        sys.exit(1)

    # Article must exist on main (fail closed if not merged)
    article_path_obj = Path(article_path)
    if not article_path_obj.exists():
        print(f"::error::Article not found on main: {article_path!r}", file=sys.stderr)
        set_output("eligible", "false")
        set_output("reason", "article_not_on_main")
        sys.exit(1)

    # Compute article SHA-256 (machine-readable — not user-controlled text)
    article_sha256 = compute_sha256(article_path_obj)
    print(f"  article_path: {article_path}")
    print(f"  article_sha256: {article_sha256}")
    print(f"  week: {week}")

    # Log before_sha to help diagnose first-push edge case (all-zeros SHA)
    if args.before_sha == NULL_SHA:
        print("  before_sha is all-zeros (first push to branch); diff-filter was handled upstream.")

    # Fetch origin/publish (read-only; does not alter working tree)
    fetch_publish_branch()

    # Find candidate manifests for this week
    manifests = list_manifests_for_week(week)
    print(f"  manifests found for {week}: {len(manifests)}")

    if not manifests:
        print(f"::notice::No publish manifests found for week {week}.")
        set_output("eligible", "false")
        set_output("reason", "no_matching_manifest")
        return

    matched: list[tuple[str, str, dict]] = []
    for manifest_path in manifests:
        m = MANIFEST_PATH_RE.match(manifest_path)
        if not m:
            continue
        run_id_from_path = m.group(2)
        try:
            manifest = read_manifest_from_publish(manifest_path)
        except (ValueError, json.JSONDecodeError, KeyError) as exc:
            print(f"::warning::Could not parse {manifest_path!r}: {exc}", file=sys.stderr)
            continue

        valid, reason = validate_manifest(manifest, week, run_id_from_path, article_sha256)
        if valid:
            matched.append((manifest_path, run_id_from_path, manifest))
            print(f"  MATCHED: {manifest_path}")
        else:
            print(f"  skip {manifest_path}: {reason}")

    if len(matched) == 0:
        print(f"::notice::No manifest matched article SHA-256={article_sha256} for week {week}.")
        set_output("eligible", "false")
        set_output("reason", "no_matching_manifest")
        return

    if len(matched) > 1:
        paths = ", ".join(p for p, _, _ in matched)
        print(
            f"::error::Ambiguous: {len(matched)} manifests matched for week {week}: {paths}. "
            f"Failing closed.",
            file=sys.stderr,
        )
        set_output("eligible", "false")
        set_output("reason", "ambiguous_manifest")
        sys.exit(1)

    manifest_path, run_id, manifest = matched[0]

    # Compute manifest SHA-256 from publish branch bytes (for evidence record)
    manifest_bytes = read_manifest_bytes_from_publish(manifest_path)
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()

    # Derive article URL deterministically from article path (preserve case: W37 not w37)
    article_url = f"https://claracle.com/weekly/{year}/{short}/"

    status = "observe_only" if args.observe_only else "eligible"

    set_output("eligible", "true")
    set_output("status", status)
    set_output("week", week)
    set_output("publish_run_id", run_id)
    set_output("manifest_path", manifest_path)
    set_output("article_path", article_path)
    set_output("article_url", article_url)
    set_output("article_sha256", article_sha256)
    set_output("manifest_sha256", manifest_sha256)

    print(f"  status: {status}")
    print(f"  publish_run_id: {run_id}")
    print(f"  manifest_sha256: {manifest_sha256}")


def check_duplicate(args: argparse.Namespace) -> None:
    """
    Check GitHub Actions for prior auto-dispatch runs of the same week.

    Limitation: trigger-podcast.yml workflow_dispatch inputs (week, publish_run_id)
    are not surfaced by the GitHub runs API, so manual legacy dispatches (e.g. W37)
    cannot be detected here. Safety for those runs relies on:
      - Podcaster idempotency (primary)
      - Human-gated environment approval (secondary)
      - Concurrency group preventing parallel auto-dispatch runs (tertiary)

    This check only covers auto-podcast-dispatch.yml runs.
    """
    week = args.week
    publish_run_id = args.publish_run_id

    if not week or not WEEK_RE.match(week):
        print(f"::error::--week must match YYYY-WNN (got: {week!r})", file=sys.stderr)
        sys.exit(1)
    if not publish_run_id or not RUN_ID_RE.match(publish_run_id):
        print(
            f"::error::--publish-run-id must be numeric (got: {publish_run_id!r})",
            file=sys.stderr,
        )
        sys.exit(1)

    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        print("::warning::GH_TOKEN/GITHUB_TOKEN not set; skipping duplicate check.")
        print("  Relying on concurrency group and Podcaster idempotency.")
        set_output("is_duplicate", "false")
        set_output("prior_run_url", "")
        return

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        print("::warning::GITHUB_REPOSITORY not set; skipping duplicate check.")
        set_output("is_duplicate", "false")
        set_output("prior_run_url", "")
        return

    env = os.environ.copy()
    env["GH_TOKEN"] = gh_token

    # Query recent successful runs of auto-podcast-dispatch.yml.
    # Match by display_title (push commit message may contain week slug) or run name.
    # This is best-effort; Podcaster idempotency is the final safety net.
    for field in ("display_title", "name"):
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo}/actions/workflows/auto-podcast-dispatch.yml/runs",
                "--method",
                "GET",
                "-F",
                "status=success",
                "-F",
                "per_page=20",
                "--jq",
                f'.workflow_runs[] | select(.{field} | contains("{week}")) | .html_url',
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            prior_url = result.stdout.strip().splitlines()[0]
            print(f"::warning::Possible prior auto-dispatch for {week} found: {prior_url}")
            set_output("is_duplicate", "true")
            set_output("prior_run_url", prior_url)
            return

    print(f"  No prior successful auto-dispatch runs found for week={week}.")
    print(
        "  Note: trigger-podcast.yml manual dispatches are not detectable via runs API."
    )
    print(
        "  Deduplication for legacy manual runs relies on Podcaster idempotency + environment gate."
    )
    set_output("is_duplicate", "false")
    set_output("prior_run_url", "")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect eligible podcast auto-dispatch after weekly article publish.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--check-duplicate",
        action="store_true",
        help="Run in duplicate-check mode (requires --week and --publish-run-id).",
    )
    parser.add_argument(
        "--article-path",
        default="",
        help="Repo-relative path to the newly merged weekly article.",
    )
    parser.add_argument(
        "--before-sha",
        default="",
        help="Git SHA before the push (GITHUB_EVENT_BEFORE).",
    )
    parser.add_argument(
        "--current-sha",
        default="",
        help="Git SHA of the push (GITHUB_SHA / HEAD).",
    )
    parser.add_argument(
        "--observe-only",
        action="store_true",
        help="Mark output status as 'observe_only' (validate but do not dispatch).",
    )
    parser.add_argument(
        "--week",
        default="",
        help="Week slug, e.g. 2026-W37 (required for --check-duplicate).",
    )
    parser.add_argument(
        "--publish-run-id",
        default="",
        help="Exact publish workflow run ID (required for --check-duplicate).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Populate from env vars when CLI args not supplied (Actions compatibility)
    if not args.before_sha:
        args.before_sha = os.environ.get("GITHUB_EVENT_BEFORE", "")
    if not args.current_sha:
        args.current_sha = os.environ.get("GITHUB_SHA", "")

    # Manual override via WEEK_OVERRIDE env (for workflow_dispatch recovery path)
    if not args.article_path:
        week_override = os.environ.get("WEEK_OVERRIDE", "").strip()
        if week_override and WEEK_RE.match(week_override):
            year, short = week_override.split("-")
            args.article_path = f"content/weekly/{year}/{short}.md"

    if args.check_duplicate:
        check_duplicate(args)
    else:
        detect(args)


if __name__ == "__main__":
    main()
