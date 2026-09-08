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

Sync-correlation mode:
    python3 scripts/auto_dispatch_detect.py \
        --find-sync-commit <pre-sync-sha>

Outputs written to $GITHUB_OUTPUT (when set) and printed to stdout.

Security notes:
- No untrusted text (commit messages, PR titles, article content) is used
  in correlation logic. Correlation is exclusively by SHA-256 of article bytes.
- PODCAST_AUTO_DISPATCH_PAUSED env var controls pause; 'true' is case-insensitive.
- Fails closed on any missing, ambiguous, or invalid manifest evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess  # nosec B404
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib import request

if TYPE_CHECKING:
    from collections.abc import Callable

WEEK_RE = re.compile(r"^[0-9]{4}-W[0-9]{2}$")
RUN_ID_RE = re.compile(r"^[0-9]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_PATH_RE = re.compile(
    r"^data/candidates/([0-9]{4}-W[0-9]{2})/([0-9]+)/publish-manifest\.json$"
)
ARTICLE_PATH_RE = re.compile(r"^content/weekly/(\d{4})/(W\d{2})\.md$")
NULL_SHA = "0" * 40
RECEIPT_PREFIX = "PODCAST_DISPATCH_RECEIPT::"
RECEIPT_SCHEMA_VERSION = "podcast_dispatch_receipt_v1"
AUTO_DISPATCH_WORKFLOW = "auto-podcast-dispatch.yml"
TRIGGER_PODCAST_WORKFLOW = "trigger-podcast.yml"
AUTO_DISPATCH_WORKFLOW_PATH = f".github/workflows/{AUTO_DISPATCH_WORKFLOW}"
TRIGGER_PODCAST_WORKFLOW_PATH = f".github/workflows/{TRIGGER_PODCAST_WORKFLOW}"
WORKFLOW_LOOKBACK_RUNS = 50
BLOCKING_RECEIPT_STATES = frozenset({"submitted", "submission_rejected"})
AMBIGUOUS_RECEIPT_STATES = frozenset({"ambiguous_prior_submission", "submission_unknown"})
NON_BLOCKING_RECEIPT_STATES = frozenset(
    {
        "ambiguous_prior_submission",
        "duplicate_prevented",
        "no_anchor",
        "no_matching_manifest",
        "no_new_article",
        "observe_only",
        "paused",
        "pre_submit_failed",
    }
)


@dataclass(frozen=True)
class DispatchIdentity:
    week: str
    publish_run_id: str
    article_sha256: str


@dataclass(frozen=True)
class DuplicateCheckResult:
    status: str
    is_duplicate: bool
    prior_run_url: str | None = None
    reason: str | None = None


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
    return subprocess.run(  # nosec B603 B607 - fixed argv, no shell, git is a controlled tool
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


def _github_api_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _github_api_json(url: str, token: str) -> dict[str, Any]:
    req = request.Request(url, headers=_github_api_headers(token))
    with request.urlopen(req, timeout=20) as resp:  # nosec B310 - trusted GitHub API endpoint
        payload = json.loads(resp.read())
    if not isinstance(payload, dict):
        raise ValueError(f"GitHub API response was not a JSON object for {url}")
    return payload


def _github_api_bytes(url: str, token: str) -> bytes:
    req = request.Request(url, headers=_github_api_headers(token))
    with request.urlopen(req, timeout=20) as resp:  # nosec B310 - trusted GitHub API endpoint
        return resp.read()


def _step_conclusion(jobs: list[dict[str, Any]], job_name: str, step_name: str) -> str:
    for job in jobs:
        if job.get("name") != job_name:
            continue
        for step in job.get("steps", []):
            if step.get("name") == step_name:
                return str(step.get("conclusion") or "")
    return ""


def _run_url(run: dict[str, Any]) -> str:
    value = run.get("html_url")
    return value if isinstance(value, str) else ""


def _parse_dispatch_receipts(log_text: str) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for line in log_text.splitlines():
        if RECEIPT_PREFIX not in line:
            continue
        _, payload = line.split(RECEIPT_PREFIX, 1)
        try:
            parsed = json.loads(payload.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and parsed.get("schema_version") == RECEIPT_SCHEMA_VERSION:
            receipts.append(parsed)
    return receipts


def _receipt_identity_matches(receipt: dict[str, Any], identity: DispatchIdentity) -> bool:
    return (
        receipt.get("week") == identity.week
        and str(receipt.get("publish_run_id") or "") == identity.publish_run_id
        and receipt.get("article_sha256") == identity.article_sha256
    )


def _extract_dispatch_identity_from_log_outputs(log_text: str) -> DispatchIdentity | None:
    values: dict[str, str] = {}
    for line in log_text.splitlines():
        marker = "output: "
        if marker not in line:
            continue
        key_value = line.split(marker, 1)[1].strip()
        if "=" not in key_value:
            continue
        key, value = key_value.split("=", 1)
        values[key.strip()] = value.strip()
    week = values.get("week", "")
    publish_run_id = values.get("publish_run_id", "")
    article_sha256 = values.get("article_sha256", "")
    if (
        WEEK_RE.match(week)
        and RUN_ID_RE.match(publish_run_id)
        and SHA256_RE.match(article_sha256)
    ):
        return DispatchIdentity(
            week=week,
            publish_run_id=publish_run_id,
            article_sha256=article_sha256,
        )
    return None


def _extract_publish_run_id_from_log_text(log_text: str) -> str | None:
    match = re.search(r"Using manifest from crawl-and-publish run (\d+)", log_text)
    if not match:
        return None
    publish_run_id = match.group(1)
    return publish_run_id if RUN_ID_RE.match(publish_run_id) else None


def _identity_from_sync_commit(
    *,
    head_sha: str,
    publish_run_id: str,
    repo_root: Path | str,
) -> DispatchIdentity | None:
    if not head_sha:
        return None
    result = subprocess.run(  # nosec B603 B607 - fixed argv, no shell, git is a controlled tool
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=A",
            f"{head_sha}^1",
            head_sha,
            "--",
            "content/weekly/**/*.md",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    article_paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(article_paths) != 1:
        return None
    week, _, _ = extract_week_from_article_path(article_paths[0])
    if not week:
        return None
    try:
        manifest = read_manifest_from_publish(
            f"data/candidates/{week}/{publish_run_id}/publish-manifest.json"
        )
    except (ValueError, json.JSONDecodeError, KeyError):
        return None
    candidate = manifest.get("candidate") or {}
    article_sha256 = candidate.get("content_sha256")
    if not isinstance(article_sha256, str) or not SHA256_RE.match(article_sha256):
        return None
    return DispatchIdentity(
        week=week,
        publish_run_id=publish_run_id,
        article_sha256=article_sha256,
    )


def _legacy_auto_observe_only(jobs: list[dict[str, Any]]) -> bool:
    return (
        _step_conclusion(jobs, "Observe-only summary", "Record observe-only result") == "success"
        and any(
            job.get("name") == "Protected podcast dispatch"
            and str(job.get("conclusion") or "") == "skipped"
            for job in jobs
        )
    )


def _compat_identity_for_run(
    run: dict[str, Any],
    jobs: list[dict[str, Any]],
    log_text: str,
    requested_identity: DispatchIdentity,
    repo_root: Path | str,
) -> tuple[str, DispatchIdentity | None]:
    path = str(run.get("path") or "")

    if path == AUTO_DISPATCH_WORKFLOW_PATH:
        if _legacy_auto_observe_only(jobs):
            return "ignore", None
        identity = _extract_dispatch_identity_from_log_outputs(log_text)
        if identity is None:
            return "ambiguous", None
        if _step_conclusion(jobs, "Protected podcast dispatch", "Trigger podcast generation") == "success":
            return "blocking" if identity == requested_identity else "ignore", identity
        return "ambiguous", identity if identity.publish_run_id == requested_identity.publish_run_id else None

    if path != TRIGGER_PODCAST_WORKFLOW_PATH:
        return "ignore", None

    if _step_conclusion(jobs, "trigger-podcast", "Trigger podcast generation with existing manifest") != "success":
        return "ignore", None

    publish_run_id = _extract_publish_run_id_from_log_text(log_text)
    if publish_run_id is None:
        return "ambiguous", None
    if publish_run_id != requested_identity.publish_run_id:
        return "ignore", None

    identity = _identity_from_sync_commit(
        head_sha=str(run.get("head_sha") or ""),
        publish_run_id=publish_run_id,
        repo_root=repo_root,
    )
    if identity is None:
        return "ambiguous", None
    return ("blocking" if identity == requested_identity else "ignore"), identity


def _list_workflow_runs(repo: str, token: str, workflow_file: str) -> list[dict[str, Any]]:
    url = (
        f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_file}/runs"
        f"?per_page={WORKFLOW_LOOKBACK_RUNS}"
    )
    payload = _github_api_json(url, token)
    runs = payload.get("workflow_runs", [])
    return runs if isinstance(runs, list) else []


def _run_jobs(repo: str, token: str, run_id: int) -> list[dict[str, Any]]:
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"
    payload = _github_api_json(url, token)
    jobs = payload.get("jobs", [])
    return jobs if isinstance(jobs, list) else []


def _run_logs(repo: str, token: str, run_id: int) -> str:
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    raw = _github_api_bytes(url, token)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            parts: list[str] = []
            for name in sorted(archive.namelist()):
                with archive.open(name) as fh:
                    parts.append(fh.read().decode("utf-8", errors="replace"))
            return "\n".join(parts)
    except zipfile.BadZipFile as exc:
        raise ValueError(f"Run logs were not a readable zip archive for run {run_id}") from exc


def find_sync_commit(pre_sync_sha: str | None, repo_root: Path | str) -> str | None:
    """Return the first matching sync commit after pre_sync_sha, if any."""
    if not pre_sync_sha:
        raise ValueError("pre_sync_sha must be a non-empty commit SHA")

    result = subprocess.run(  # nosec B603 B607 - fixed argv, no shell, git is a controlled tool
        [
            "git",
            "log",
            "--grep=^sync: publish data",
            "--ancestry-path",
            "--format=%H",
            f"{pre_sync_sha}..HEAD",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git log failed (exit {result.returncode}): {result.stderr.strip()[:200]}"
        )
    lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    if not lines:
        return None
    return lines[-1]


def read_manifest_from_publish(path: str) -> dict:
    """Read and parse a manifest JSON from origin/publish without checkout."""
    result = subprocess.run(  # nosec B603 B607 - fixed argv, no shell; path validated by MANIFEST_PATH_RE
        ["git", "show", f"origin/publish:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Cannot read {path!r} from origin/publish")
    return json.loads(result.stdout)


def read_manifest_bytes_from_publish(path: str) -> bytes:
    result = subprocess.run(  # nosec B603 B607 - fixed argv, no shell; path validated by MANIFEST_PATH_RE
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
        return False, (f"SHA-256 mismatch: manifest={content_sha256!r} article={article_sha256!r}")

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

    manifest_path, run_id, _manifest = matched[0]

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


def _check_duplicate_cli(args: argparse.Namespace) -> None:
    """Check GitHub Actions for prior real dispatches of the same publication."""
    week = args.week
    publish_run_id = args.publish_run_id
    article_sha256 = args.article_sha256

    if not week or not WEEK_RE.match(week):
        print(f"::error::--week must match YYYY-WNN (got: {week!r})", file=sys.stderr)
        sys.exit(1)
    if not publish_run_id or not RUN_ID_RE.match(publish_run_id):
        print(
            f"::error::--publish-run-id must be numeric (got: {publish_run_id!r})",
            file=sys.stderr,
        )
        sys.exit(1)
    if not article_sha256 or not SHA256_RE.match(article_sha256):
        print(
            f"::error::--article-sha256 must be lowercase 64-char hex (got: {article_sha256!r})",
            file=sys.stderr,
        )
        sys.exit(1)

    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        print("::warning::GH_TOKEN/GITHUB_TOKEN not set; skipping duplicate check.")
        print("  Relying on concurrency group and Podcaster idempotency.")
        set_output("is_duplicate", "false")
        set_output("prior_run_url", "")
        set_output("dedup_status", "skipped_missing_token")
        return

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        print("::warning::GITHUB_REPOSITORY not set; skipping duplicate check.")
        set_output("is_duplicate", "false")
        set_output("prior_run_url", "")
        set_output("dedup_status", "skipped_missing_repository")
        return

    result = check_duplicate_result(
        week,
        publish_run_id,
        article_sha256,
        gh_token,
        repo,
    )

    if result.status == "duplicate":
        prior_url = result.prior_run_url or ""
        print(
            f"::warning::Prior real podcast dispatch for {week}/{publish_run_id} found: {prior_url}"
        )
        set_output("is_duplicate", "true")
        set_output("prior_run_url", prior_url)
        set_output("dedup_status", result.status)
        return
    if result.status == "ambiguous_prior_submission":
        prior_url = result.prior_run_url or ""
        reason = result.reason or "ambiguous_prior_submission"
        print(
            "::error::Prior podcast dispatch evidence is ambiguous; refusing to assume retry safety. "
            f"run={prior_url or '<unknown>'} reason={reason}",
            file=sys.stderr,
        )
        set_output("is_duplicate", "false")
        set_output("prior_run_url", prior_url)
        set_output("dedup_status", result.status)
        sys.exit(1)

    print(
        f"  No prior real podcast dispatch found for identity "
        f"week={week} publish_run_id={publish_run_id} article_sha256={article_sha256}."
    )
    set_output("is_duplicate", "false")
    set_output("prior_run_url", "")
    set_output("dedup_status", result.status)


def _find_sync_commit_cli(args: argparse.Namespace) -> None:
    sync_sha = find_sync_commit(args.find_sync_commit, Path("."))
    print(sync_sha or "")


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
        "--find-sync-commit",
        default="",
        help="Print the first sync: publish data commit descending from the given anchor SHA.",
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
    parser.add_argument(
        "--article-sha256",
        default="",
        help="Exact article SHA-256 (required for --check-duplicate).",
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

    if args.find_sync_commit:
        _find_sync_commit_cli(args)
    elif args.check_duplicate:
        _check_duplicate_cli(args)
    else:
        detect(args)


# ---------------------------------------------------------------------------
# Public test-friendly API — thin wrappers over internal functions
# ---------------------------------------------------------------------------


def extract_week(article_path: str) -> str | None:
    """Return week slug (e.g. '2026-W37') from article path, or None if invalid."""
    week, _, _ = extract_week_from_article_path(article_path)
    return week


def check_paused() -> bool:
    """Return True iff PODCAST_AUTO_DISPATCH_PAUSED env var is 'true' (case-insensitive)."""
    return os.environ.get("PODCAST_AUTO_DISPATCH_PAUSED", "").strip().lower() == "true"


def find_manifest_for_article(
    article_path: str,
    repo_root: "Path",
    *,
    manifest_reader: "Callable[[Path], dict] | None" = None,
) -> dict:
    """Scan repo_root for a matching publish manifest (test-friendly, no git I/O).

    Returns a dict with keys: eligible, week, run_id, manifest_path,
    article_sha256, manifest_sha256, reason.
    """
    week, _year, _short = extract_week_from_article_path(article_path)
    if not week:
        return {"eligible": False, "reason": "invalid_article_path"}

    article_file = Path(repo_root) / article_path
    if not article_file.exists():
        return {"eligible": False, "reason": "article_not_on_main", "week": week}
    article_sha256 = compute_sha256(article_file)

    candidates_dir = Path(repo_root) / "data" / "candidates" / week
    manifest_files: list[Path] = (
        sorted(candidates_dir.glob("*/publish-manifest.json")) if candidates_dir.exists() else []
    )

    matched: list[tuple[str, str, dict]] = []
    failures: list[tuple[str, str]] = []  # (manifest_path, reason)
    for mf in manifest_files:
        run_id_from_path = mf.parent.name
        try:
            if manifest_reader is not None:
                manifest = manifest_reader(mf)
            else:
                manifest = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            failures.append((str(mf), "malformed_json"))
            continue
        valid, reason = validate_manifest(manifest, week, run_id_from_path, article_sha256)
        if valid:
            rel = str(mf.relative_to(repo_root))
            matched.append((rel, run_id_from_path, manifest))
        else:
            # Normalize validate_manifest reason to test-friendly key
            if "SHA-256 mismatch" in reason:
                norm_reason = "sha256_mismatch"
            elif "run_mode" in reason:
                norm_reason = "ineligible_run_mode"
            elif "publish_eligible" in reason:
                norm_reason = "ineligible_manifest"
            elif "manifest.week" in reason:
                norm_reason = "manifest_week_mismatch"
            elif "manifest.run_id" in reason:
                norm_reason = "manifest_run_id_mismatch"
            else:
                norm_reason = reason
            failures.append((str(mf), norm_reason))

    if len(matched) == 0:
        # Surface specific reason when exactly one manifest failed
        specific_reason = failures[0][1] if len(failures) == 1 else "no_matching_manifest"
        return {
            "eligible": False,
            "reason": specific_reason,
            "week": week,
            "article_sha256": article_sha256,
        }
    if len(matched) > 1:
        return {
            "eligible": False,
            "reason": "ambiguous_manifest",
            "week": week,
            "article_sha256": article_sha256,
        }

    manifest_path, run_id, _manifest = matched[0]
    manifest_sha256 = hashlib.sha256((Path(repo_root) / manifest_path).read_bytes()).hexdigest()
    return {
        "eligible": True,
        "week": week,
        "run_id": run_id,
        "manifest_path": manifest_path,
        "article_path": article_path,
        "article_sha256": article_sha256,
        "manifest_sha256": manifest_sha256,
        "reason": "ok",
    }


def check_duplicate_api(
    week: str,
    run_id: str,
    gh_token: "str | None" = None,
    repo: "str | None" = None,
) -> "tuple[bool, str | None]":
    """Check GitHub API for a prior successful auto-dispatch run (test-friendly).

    Returns (is_duplicate, prior_run_url | None).
    On API failure, returns (False, None) — fail-open; Podcaster idempotency
    is the fallback safety net.
    """
    token = gh_token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repository = repo or os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repository:
        return False, None

    try:
        url = f"https://api.github.com/repos/{repository}/actions/workflows/auto-podcast-dispatch.yml/runs?status=success&per_page=20"
        req = request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with request.urlopen(req, timeout=15) as resp:  # nosec B310 - URL is constructed from trusted API endpoint
            data = json.loads(resp.read())
    except Exception:
        return False, None

    for run in data.get("workflow_runs", []):
        name = run.get("name", "") or ""
        if week not in name:
            continue
        if "observe" in name.lower():
            continue
        return True, run.get("html_url")
    return False, None


def check_duplicate_result(
    week: str,
    run_id: str,
    article_sha256: str,
    gh_token: "str | None" = None,
    repo: "str | None" = None,
    *,
    repo_root: "Path | str" = Path("."),
) -> DuplicateCheckResult:
    """Check GitHub history for an existing real or ambiguous prior submission."""
    token = gh_token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repository = repo or os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repository:
        return DuplicateCheckResult(status="clear", is_duplicate=False)
    if not WEEK_RE.match(week) or not RUN_ID_RE.match(run_id) or not SHA256_RE.match(article_sha256):
        raise ValueError("week, run_id, and article_sha256 must be valid exact identity fields")

    identity = DispatchIdentity(
        week=week,
        publish_run_id=run_id,
        article_sha256=article_sha256,
    )

    try:
        fetch_publish_branch()
        candidate_runs: list[dict[str, Any]] = []
        for workflow_file in (AUTO_DISPATCH_WORKFLOW, TRIGGER_PODCAST_WORKFLOW):
            candidate_runs.extend(_list_workflow_runs(repository, token, workflow_file))
    except Exception:
        return DuplicateCheckResult(status="clear", is_duplicate=False)

    for run in candidate_runs:
        run_id_value = run.get("id")
        if not isinstance(run_id_value, int):
            continue

        try:
            jobs = _run_jobs(repository, token, run_id_value)
            log_text = _run_logs(repository, token, run_id_value)
        except Exception:
            continue

        receipts = _parse_dispatch_receipts(log_text)
        matched_receipt = False
        for receipt in receipts:
            if not _receipt_identity_matches(receipt, identity):
                continue
            matched_receipt = True
            state = str(receipt.get("receipt_state") or "")
            if state in BLOCKING_RECEIPT_STATES:
                return DuplicateCheckResult(
                    status="duplicate",
                    is_duplicate=True,
                    prior_run_url=_run_url(run) or None,
                    reason=state,
                )
            if state in AMBIGUOUS_RECEIPT_STATES:
                return DuplicateCheckResult(
                    status="ambiguous_prior_submission",
                    is_duplicate=False,
                    prior_run_url=_run_url(run) or None,
                    reason=state,
                )
            if state in NON_BLOCKING_RECEIPT_STATES:
                break
        if matched_receipt or receipts:
            continue

        compatibility, compat_identity = _compat_identity_for_run(
            run,
            jobs,
            log_text,
            identity,
            repo_root,
        )
        if compatibility == "blocking" and compat_identity == identity:
            return DuplicateCheckResult(
                status="duplicate",
                is_duplicate=True,
                prior_run_url=_run_url(run) or None,
                reason="legacy_real_submission",
            )
        if compatibility == "ambiguous":
            return DuplicateCheckResult(
                status="ambiguous_prior_submission",
                is_duplicate=False,
                prior_run_url=_run_url(run) or None,
                reason="legacy_submission_without_canonical_receipt",
            )

    return DuplicateCheckResult(status="clear", is_duplicate=False)


def check_duplicate(
    week: str,
    run_id: str,
    article_sha256: str,
    gh_token: "str | None" = None,
    repo: "str | None" = None,
    *,
    repo_root: "Path | str" = Path("."),
) -> "tuple[bool, str | None]":
    result = check_duplicate_result(
        week,
        run_id,
        article_sha256,
        gh_token,
        repo,
        repo_root=repo_root,
    )
    return result.is_duplicate, result.prior_run_url


# Expose the test-friendly signature as the public name.
if __name__ == "__main__":
    main()
