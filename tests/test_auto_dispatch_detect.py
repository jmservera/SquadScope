"""Tests for scripts/auto_dispatch_detect.py.

Public API tested:
  - find_manifest_for_article(article_path: str, repo_root: Path) -> dict
    Reads article from repo_root/article_path; scans
    repo_root/data/candidates/<week>/*/publish-manifest.json on disk.
    Returns: {eligible, week, run_id, manifest_path, article_sha256,
              manifest_sha256, reason}
  - extract_week(article_path: str) -> str | None
    Extracts ISO week string (e.g. "2026-W37") or None for invalid paths.
  - check_paused() -> bool
    Returns True iff PODCAST_AUTO_DISPATCH_PAUSED env var is 'true' (case-insensitive).
  - check_duplicate_result(week, run_id, article_sha256, gh_token, repo) -> DuplicateCheckResult
    Returns structured duplicate status using exact identity, canonical receipts,
    and compatibility logic for legacy runs.
"""

import hashlib
import io
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import scripts.auto_dispatch_detect as detect

# ---------------------------------------------------------------------------
# Constants shared across tests
# ---------------------------------------------------------------------------

KNOWN_ARTICLE_CONTENT = b"# W37 AI Weekly\n\nContent for week 37 of 2026.\n"
KNOWN_SHA256 = hashlib.sha256(KNOWN_ARTICLE_CONTENT).hexdigest()
WEEK = "2026-W37"
RUN_ID = "34082521901"
TEST_WORKSPACES_ROOT = Path(__file__).resolve().parents[1] / ".test-workspaces"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manifest(
    *,
    sha256: str = KNOWN_SHA256,
    week: str = WEEK,
    run_id: str = RUN_ID,
    publish_eligible: bool = True,
) -> dict:
    return {
        "week": week,
        "run_id": run_id,
        "run_mode": "normal",
        "promotion_eligible": publish_eligible,
        "analysis": {"preflight": {"publish_eligible": publish_eligible}},
        "candidate": {
            "content_sha256": sha256,
            "content_path": f"data/candidates/{week}/{run_id}/{week}-content.md",
        },
    }


class _FakeHTTPResponse(io.BytesIO):
    """Minimal urllib response stub used to mock GitHub API calls."""

    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def getcode(self):
        return self.status


def _gh_runs_response(runs: list) -> _FakeHTTPResponse:
    payload = json.dumps({"workflow_runs": runs}).encode()
    return _FakeHTTPResponse(payload)


def _gh_jobs_response(jobs: list) -> _FakeHTTPResponse:
    payload = json.dumps({"jobs": jobs}).encode()
    return _FakeHTTPResponse(payload)


def _gh_logs_response(*contents: str) -> _FakeHTTPResponse:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for index, content in enumerate(contents, start=1):
            archive.writestr(f"job-{index}.txt", content)
    return _FakeHTTPResponse(buffer.getvalue())


class _TempGitRepo:
    """Real git repository fixture rooted under the repo-local test workspace."""

    def __init__(self) -> None:
        TEST_WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)
        self._tmp = tempfile.TemporaryDirectory(
            prefix="auto-dispatch-detect-",
            dir=TEST_WORKSPACES_ROOT,
        )
        self.root = Path(self._tmp.name)
        self._run("git", "init", "-q", "-b", "main")
        self._run("git", "config", "user.name", "Fry Tester")
        self._run("git", "config", "user.email", "fry@example.com")

    def cleanup(self) -> None:
        self._tmp.cleanup()

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args),
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self, message: str, updates: dict[str, str]) -> str:
        for relative_path, content in updates.items():
            self.write(relative_path, content)
        self._run("git", "add", "-A")
        self._run("git", "commit", "-q", "-m", message)
        return self._run("git", "rev-parse", "HEAD").stdout.strip()


# ---------------------------------------------------------------------------
# TestFindManifest
# ---------------------------------------------------------------------------


class TestFindManifest(unittest.TestCase):
    """Tests for find_manifest_for_article()."""

    # -- setup helpers -------------------------------------------------------

    def _setup_article(self, tmp: Path, content: bytes = KNOWN_ARTICLE_CONTENT) -> None:
        article = tmp / "content" / "weekly" / "2026" / "W37.md"
        article.parent.mkdir(parents=True, exist_ok=True)
        article.write_bytes(content)

    def _write_manifest(
        self,
        tmp: Path,
        data: dict,
        run_id: str = RUN_ID,
        week: str = WEEK,
    ) -> Path:
        manifest_dir = tmp / "data" / "candidates" / week / run_id
        manifest_dir.mkdir(parents=True, exist_ok=True)
        path = manifest_dir / "publish-manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    # -- tests ---------------------------------------------------------------

    def test_happy_path(self):
        """Article + matching manifest → eligible=True, correct week/run_id."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            self._write_manifest(tmp, _make_manifest())

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertTrue(result["eligible"])
            self.assertEqual(result["week"], WEEK)
            self.assertEqual(result["run_id"], RUN_ID)
            self.assertEqual(result["article_sha256"], KNOWN_SHA256)

    def test_no_manifest_for_week(self):
        """No manifest on disk → eligible=False, reason contains no_matching_manifest."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])
            self.assertIn("no_matching_manifest", result["reason"])

    def test_sha256_mismatch(self):
        """Manifest SHA256 ≠ article SHA256 → eligible=False, reason contains sha256_mismatch."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            self._write_manifest(tmp, _make_manifest(sha256="a" * 64))

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])
            self.assertIn("sha256_mismatch", result["reason"])

    def test_multiple_candidates_correct_one_found(self):
        """Two manifests for same week — only one SHA matches → eligible=True, correct run_id."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            self._write_manifest(tmp, _make_manifest(sha256="b" * 64), run_id="11111111111")
            self._write_manifest(tmp, _make_manifest(sha256=KNOWN_SHA256), run_id=RUN_ID)

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertTrue(result["eligible"])
            self.assertEqual(result["run_id"], RUN_ID)

    def test_multiple_candidates_no_match(self):
        """Two manifests, neither SHA matches → eligible=False."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            self._write_manifest(tmp, _make_manifest(sha256="a" * 64), run_id="11111111111")
            self._write_manifest(tmp, _make_manifest(sha256="b" * 64), run_id="22222222222")

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])
            self.assertIn("no_matching_manifest", result["reason"])

    def test_manifest_week_field_mismatch(self):
        """manifest.week ≠ expected week → fail closed (eligible=False)."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            # manifest.week deliberately wrong; directory week is correct
            self._write_manifest(tmp, _make_manifest(week="2026-W36"))

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])

    def test_manifest_run_id_field_mismatch(self):
        """manifest.run_id ≠ directory run_id → fail closed (eligible=False)."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            # directory run_id = RUN_ID, but manifest.run_id = different
            self._write_manifest(tmp, _make_manifest(run_id="99999999999"), run_id=RUN_ID)

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])

    def test_ineligible_manifest(self):
        """publish_eligible=false in manifest → eligible=False."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            self._write_manifest(tmp, _make_manifest(publish_eligible=False))

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])

    def test_malformed_manifest_json(self):
        """Invalid JSON in manifest → fail closed (eligible=False)."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            manifest_dir = tmp / "data" / "candidates" / WEEK / RUN_ID
            manifest_dir.mkdir(parents=True, exist_ok=True)
            (manifest_dir / "publish-manifest.json").write_text("{invalid", encoding="utf-8")

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])

    def test_missing_candidate_sha256(self):
        """Manifest has no candidate.content_sha256 → fail closed (eligible=False)."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._setup_article(tmp)
            data = _make_manifest()
            del data["candidate"]["content_sha256"]
            self._write_manifest(tmp, data)

            result = detect.find_manifest_for_article("content/weekly/2026/W37.md", tmp)

            self.assertFalse(result["eligible"])

    def test_invalid_article_path_format(self):
        """Path not matching content/weekly/<year>/<WNN>.md → ValueError or eligible=False."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            article = tmp / "not" / "a" / "weekly" / "path.md"
            article.parent.mkdir(parents=True, exist_ok=True)
            article.write_bytes(b"irrelevant content")

            try:
                result = detect.find_manifest_for_article("not/a/weekly/path.md", tmp)
                # Either return is acceptable as long as it's not eligible
                self.assertFalse(
                    result["eligible"],
                    "Expected eligible=False for an invalid article path",
                )
            except (ValueError, KeyError):
                pass  # raising an error is also an acceptable response


# ---------------------------------------------------------------------------
# TestPausedCheck
# ---------------------------------------------------------------------------


class TestPausedCheck(unittest.TestCase):
    """Tests for check_paused()."""

    def test_paused_when_var_true(self):
        with mock.patch.dict(os.environ, {"PODCAST_AUTO_DISPATCH_PAUSED": "true"}):
            self.assertTrue(detect.check_paused())

    def test_paused_when_var_TRUE(self):
        with mock.patch.dict(os.environ, {"PODCAST_AUTO_DISPATCH_PAUSED": "TRUE"}):
            self.assertTrue(detect.check_paused())

    def test_not_paused_when_var_false(self):
        with mock.patch.dict(os.environ, {"PODCAST_AUTO_DISPATCH_PAUSED": "false"}):
            self.assertFalse(detect.check_paused())

    def test_not_paused_when_var_empty(self):
        with mock.patch.dict(os.environ, {"PODCAST_AUTO_DISPATCH_PAUSED": ""}):
            self.assertFalse(detect.check_paused())

    def test_not_paused_when_var_absent(self):
        env = {k: v for k, v in os.environ.items() if k != "PODCAST_AUTO_DISPATCH_PAUSED"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(detect.check_paused())


# ---------------------------------------------------------------------------
# TestDuplicateCheck
# ---------------------------------------------------------------------------


class TestDuplicateCheck(unittest.TestCase):
    """Tests for exact duplicate detection across auto and manual workflows."""

    _GH_TOKEN = "ghp_faketoken"
    _REPO = "example/squadscope"
    _AUTO_RUN_ID = 22222
    _TRIGGER_RUN_ID = 33333

    def _workflow_runs_url(self, workflow: str) -> str:
        return (
            f"https://api.github.com/repos/{self._REPO}/actions/workflows/{workflow}/runs"
            f"?per_page={detect.WORKFLOW_LOOKBACK_RUNS}"
        )

    def _jobs_url(self, run_id: int) -> str:
        return f"https://api.github.com/repos/{self._REPO}/actions/runs/{run_id}/jobs?per_page=100"

    def _logs_url(self, run_id: int) -> str:
        return f"https://api.github.com/repos/{self._REPO}/actions/runs/{run_id}/logs"

    def _run(self, run_id: int, *, workflow_path: str, head_sha: str = "abc123") -> dict:
        return {
            "id": run_id,
            "path": workflow_path,
            "name": f"run-{run_id}",
            "display_title": f"run-{run_id}",
            "head_sha": head_sha,
            "html_url": f"https://github.com/example/squadscope/actions/runs/{run_id}",
        }

    def _receipt_log(self, *, state: str, week: str = WEEK, run_id: str = RUN_ID, sha: str = KNOWN_SHA256) -> str:
        payload = {
            "schema_version": detect.RECEIPT_SCHEMA_VERSION,
            "receipt_state": state,
            "week": week,
            "publish_run_id": run_id,
            "article_sha256": sha,
        }
        return f"{detect.RECEIPT_PREFIX}{json.dumps(payload, sort_keys=True, separators=(',', ':'))}\n"

    def _trigger_jobs(self, handoff_conclusion: str) -> list[dict]:
        return [
            {
                "name": "trigger-podcast",
                "steps": [
                    {
                        "name": "Trigger podcast generation with existing manifest",
                        "conclusion": handoff_conclusion,
                    }
                ],
            }
        ]

    def _auto_observe_jobs(self) -> list[dict]:
        return [
            {
                "name": "Observe-only summary",
                "conclusion": "success",
                "steps": [{"name": "Record observe-only result", "conclusion": "success"}],
            },
            {
                "name": "Protected podcast dispatch",
                "conclusion": "skipped",
                "steps": [],
            },
        ]

    def _router(
        self,
        *,
        auto_runs: list[dict] | None = None,
        trigger_runs: list[dict] | None = None,
        jobs: dict[int, list[dict]] | None = None,
        logs: dict[int, str] | None = None,
    ):
        routes = {
            self._workflow_runs_url(detect.AUTO_DISPATCH_WORKFLOW): _gh_runs_response(auto_runs or []),
            self._workflow_runs_url(detect.TRIGGER_PODCAST_WORKFLOW): _gh_runs_response(
                trigger_runs or []
            ),
        }
        for run_id, run_jobs in (jobs or {}).items():
            routes[self._jobs_url(run_id)] = _gh_jobs_response(run_jobs)
        for run_id, log_text in (logs or {}).items():
            routes[self._logs_url(run_id)] = _gh_logs_response(log_text)

        def _open(req, timeout=20):
            url = req.full_url
            response = routes.get(url)
            if response is None:
                raise AssertionError(f"Unexpected URL fetched: {url}")
            return response

        return _open

    def test_dry_run_receipt_allows_first_real_dispatch(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="observe_only")},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_real_receipt_blocks_duplicate_dispatch(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="submitted")},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "duplicate")
        self.assertTrue(result.is_duplicate)
        self.assertEqual(result.prior_run_url, run["html_url"])

    def test_pre_submit_failure_allows_retry(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="pre_submit_failed")},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_unknown_submission_fails_closed(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="submission_unknown")},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.prior_run_url, run["html_url"])

    def test_submission_rejected_blocks_retry(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="submission_rejected")},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "duplicate")
        self.assertTrue(result.is_duplicate)

    def test_same_week_different_identity_is_not_conflated(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={
                        self._AUTO_RUN_ID: self._receipt_log(
                            state="submitted",
                            run_id=RUN_ID,
                            sha="a" * 64,
                        )
                    },
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_legacy_unmarked_observe_only_run_is_ignored(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: self._auto_observe_jobs()},
                    logs={self._AUTO_RUN_ID: ""},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_legacy_manual_real_dispatch_blocks_auto_duplicate(self):
        repo = _TempGitRepo()
        try:
            repo.commit("chore: baseline", {"README.md": "base\n"})
            sync_sha = repo.commit(
                "sync: publish data → main (#1)",
                {"content/weekly/2026/W37.md": "# W37\n"},
            )
            run = self._run(
                self._TRIGGER_RUN_ID,
                workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
                head_sha=sync_sha,
            )
            with (
                mock.patch.object(detect, "fetch_publish_branch"),
                mock.patch.object(detect, "read_manifest_from_publish", return_value=_make_manifest()),
                mock.patch(
                    "urllib.request.urlopen",
                    side_effect=self._router(
                        trigger_runs=[run],
                        jobs={self._TRIGGER_RUN_ID: self._trigger_jobs("success")},
                        logs={
                            self._TRIGGER_RUN_ID: (
                                "##[notice]Using manifest from crawl-and-publish run "
                                f"{RUN_ID} (2026-09-08 13:30:14)\n"
                            )
                        },
                    ),
                ),
            ):
                result = detect.check_duplicate_result(
                    WEEK,
                    RUN_ID,
                    KNOWN_SHA256,
                    self._GH_TOKEN,
                    self._REPO,
                    repo_root=repo.root,
                )

            self.assertEqual(result.status, "duplicate")
            self.assertTrue(result.is_duplicate)
            self.assertEqual(result.prior_run_url, run["html_url"])
        finally:
            repo.cleanup()

    def test_legacy_manual_same_publish_run_without_identity_fails_closed(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
            head_sha="not-a-sync",
        )
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    trigger_runs=[run],
                    jobs={self._TRIGGER_RUN_ID: self._trigger_jobs("success")},
                    logs={
                        self._TRIGGER_RUN_ID: (
                            "##[notice]Using manifest from crawl-and-publish run "
                            f"{RUN_ID} (2026-09-08 13:30:14)\n"
                        )
                    },
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_api_failure_non_blocking(self):
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=OSError("network error")),
        ):
            result = detect.check_duplicate_result(
                WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO
            )

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)


# ---------------------------------------------------------------------------
# TestWeekExtraction
# ---------------------------------------------------------------------------


class TestWeekExtraction(unittest.TestCase):
    """Tests for the week-extraction helper (e.g. extract_week()).

    NOTE: If Bender makes this a private helper (_extract_week) rather than
    a public function, these tests should be updated to match the actual name.
    """

    def test_week_extraction_normal(self):
        """content/weekly/2026/W37.md → 2026-W37."""
        result = detect.extract_week("content/weekly/2026/W37.md")
        self.assertEqual(result, "2026-W37")

    def test_week_extraction_single_digit(self):
        """content/weekly/2026/W05.md → 2026-W05 (zero-padded)."""
        result = detect.extract_week("content/weekly/2026/W05.md")
        self.assertEqual(result, "2026-W05")

    def test_invalid_path(self):
        """Non-weekly path → extract_week returns None (no ValueError; fails closed downstream)."""
        result = detect.extract_week("content/blog/2026/some-post.md")
        self.assertIsNone(result)


class TestFindSyncCommitRegression(unittest.TestCase):
    """Regression tests for sync-commit correlation anchored to pre_sync_sha."""

    def _new_repo(self) -> _TempGitRepo:
        return _TempGitRepo()

    def test_find_sync_commit_finds_correct_commit(self):
        repo = self._new_repo()
        try:
            sha_a = repo.commit("chore: baseline", {"README.md": "baseline\n"})
            sha_b = repo.commit(
                "sync: publish data → main (#1)",
                {"content/weekly/2026/W37.md": "# W37\n"},
            )
            repo.commit("chore: pricing update", {"data/pricing.json": '{"usd": 42}\n'})

            result = detect.find_sync_commit(sha_a, repo.root)

            self.assertEqual(result, sha_b)
        finally:
            repo.cleanup()

    def test_find_sync_commit_ignores_later_sync(self):
        repo = self._new_repo()
        try:
            sha_a = repo.commit("chore: baseline", {"README.md": "baseline\n"})
            sha_b = repo.commit(
                "sync: publish data → main (#1)",
                {"content/weekly/2026/W37.md": "# W37\n"},
            )
            repo.commit(
                "sync: publish data → main (#2)",
                {"data/metrics/w37.json": '{"articles": 1}\n'},
            )

            result = detect.find_sync_commit(sha_a, repo.root)

            self.assertEqual(result, sha_b)
        finally:
            repo.cleanup()

    def test_data_only_sync_has_no_article(self):
        repo = self._new_repo()
        try:
            repo.commit(
                "chore: seed prior article",
                {"content/weekly/2026/W36.md": "# W36\n"},
            )
            sha_a = repo.commit("chore: baseline", {"README.md": "baseline\n"})
            sha_b = repo.commit(
                "sync: publish data → main (#2)",
                {"data/metrics/w37.json": '{"articles": 0}\n'},
            )

            result = detect.find_sync_commit(sha_a, repo.root)

            self.assertEqual(result, sha_b)
            diff = subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-only",
                    "--diff-filter=A",
                    f"{sha_b}^1",
                    sha_b,
                    "--",
                    "content/weekly/**/*.md",
                ],
                cwd=repo.root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(diff.stdout.strip(), "")
        finally:
            repo.cleanup()

    def test_find_sync_commit_absent_when_no_sync_after_anchor(self):
        repo = self._new_repo()
        try:
            repo.commit("chore: baseline", {"README.md": "baseline\n"})
            sha_head = repo.commit("chore: later change", {"notes.txt": "no sync yet\n"})

            result = detect.find_sync_commit(sha_head, repo.root)

            self.assertIsNone(result)
        finally:
            repo.cleanup()

    def test_find_sync_commit_absent_anchor_fails_closed(self):
        repo = self._new_repo()
        try:
            repo.commit("chore: baseline", {"README.md": "baseline\n"})
            repo.commit(
                "sync: publish data → main (#1)",
                {"content/weekly/2026/W37.md": "# W37\n"},
            )

            for pre_sync_sha in ("", None):
                with self.subTest(pre_sync_sha=pre_sync_sha):
                    try:
                        result = detect.find_sync_commit(pre_sync_sha, repo.root)
                    except ValueError:
                        continue
                    self.assertIsNone(result)
        finally:
            repo.cleanup()


# ---------------------------------------------------------------------------
# Specification gaps (for Bender)
# ---------------------------------------------------------------------------
# 1. extract_week: spec doesn't confirm the function is public. If private,
#    rename TestWeekExtraction calls to _extract_week or test via
#    find_manifest_for_article instead.
#
# 2. check_duplicate HTTP library: tests mock urllib.request.urlopen. If
#    Bender uses `requests`, change the mock target to
#    `requests.get` (and adjust response structure).
#
# 3. check_duplicate run matching: tests assume the function matches on
#    inputs["week"] + inputs["run_id"] OR on the run name. Bender must pick
#    one and this test may need a narrowing adjustment.
#
# 4. manifest_sha256 in result: spec mentions manifest_sha256 in the return
#    dict; test_happy_path doesn't assert on it. Bender should confirm
#    this field is populated from hashlib.sha256(manifest_bytes).hexdigest().
#
# 5. test_manifest_run_id_field_mismatch uses directory run_id=RUN_ID but
#    manifest.run_id="99999999999". The script may check the directory name
#    against manifest.run_id — confirm this is the intended validation.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
