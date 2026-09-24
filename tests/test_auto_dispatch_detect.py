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
  - article_url_from_article_path(article_path: str) -> str | None
    Returns the canonical lowercase public weekly URL.
  - check_duplicate_result(
        week, run_id, article_sha256, gh_token, repo, manifest_sha256=...
    ) -> DuplicateCheckResult
    Returns structured duplicate status using the four-field publication
    identity, canonical receipts, and compatibility logic for legacy runs.
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
from scripts import podcast_dispatch_state as state

# ---------------------------------------------------------------------------
# Constants shared across tests
# ---------------------------------------------------------------------------

KNOWN_ARTICLE_CONTENT = b"# W37 AI Weekly\n\nContent for week 37 of 2026.\n"
KNOWN_SHA256 = hashlib.sha256(KNOWN_ARTICLE_CONTENT).hexdigest()
KNOWN_MANIFEST_SHA256 = "b" * 64
WEEK = "2026-W37"
RUN_ID = "34082521901"
TEST_WORKSPACES_ROOT = Path(__file__).resolve().parents[1] / ".test-workspaces"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_duplicate_result(*args, **kwargs):
    kwargs.setdefault("manifest_sha256", KNOWN_MANIFEST_SHA256)
    return detect.check_duplicate_result(*args, **kwargs)


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
            "run_attempt": 1,
            "path": workflow_path,
            "name": f"run-{run_id}",
            "display_title": f"run-{run_id}",
            "head_sha": head_sha,
            "html_url": f"https://github.com/example/squadscope/actions/runs/{run_id}",
        }

    def _receipt_log(
        self,
        *,
        state: str,
        week: str = WEEK,
        run_id: str = RUN_ID,
        sha: str = KNOWN_SHA256,
        manifest_sha: str = KNOWN_MANIFEST_SHA256,
    ) -> str:
        payload = {
            "schema_version": detect.RECEIPT_SCHEMA_VERSION,
            "receipt_state": state,
            "week": week,
            "publish_run_id": run_id,
            "article_sha256": sha,
            "manifest_sha256": manifest_sha,
        }
        return (
            f"{detect.RECEIPT_PREFIX}{json.dumps(payload, sort_keys=True, separators=(',', ':'))}\n"
        )

    def _v2_receipt_log(
        self,
        *,
        state: str,
        manifest_sha: str = "b" * 64,
        api_status_category: str | None = None,
    ) -> str:
        payload = {
            "schema_version": "podcast_dispatch_receipt_v2",
            "receipt_id": "receipt-1",
            "created_at": "2026-09-21T21:00:00Z",
            "dispatch_run_id": str(self._AUTO_RUN_ID),
            "attempt_id": f"{self._AUTO_RUN_ID}-1",
            "identity": {
                "week": WEEK,
                "publish_run_id": RUN_ID,
                "article_sha256": KNOWN_SHA256,
                "manifest_sha256": manifest_sha,
            },
            "receipt_state": state,
        }
        if api_status_category is not None:
            payload["api_status_category"] = api_status_category
        return (
            f"{detect.RECEIPT_PREFIX}{json.dumps(payload, sort_keys=True, separators=(',', ':'))}\n"
        )

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

    def test_run_metadata_association_matches_delimited_identifiers(self):
        identity = detect.DispatchIdentity(
            week=WEEK,
            publish_run_id="123",
            article_sha256="a" * 64,
            manifest_sha256="b" * 64,
        )

        for field, identifier in (
            ("name", identity.publish_run_id),
            ("display_title", identity.article_sha256),
            ("head_branch", identity.manifest_sha256),
        ):
            with self.subTest(field=field):
                self.assertTrue(
                    detect._run_metadata_associates_identity(
                        {field: f"dispatch/{identifier}-retry"},
                        identity,
                    )
                )

    def test_run_metadata_association_rejects_identifier_prefix_collisions(self):
        identity = detect.DispatchIdentity(
            week=WEEK,
            publish_run_id="123",
            article_sha256="a" * 64,
            manifest_sha256="b" * 64,
        )

        for identifier in (
            identity.publish_run_id,
            identity.article_sha256,
            identity.manifest_sha256,
        ):
            with self.subTest(identifier=identifier):
                self.assertFalse(
                    detect._run_metadata_associates_identity(
                        {"display_title": f"publish run {identifier}4"},
                        identity,
                    )
                )

    def test_run_metadata_association_rejects_identifier_suffix_collisions(self):
        identity = detect.DispatchIdentity(
            week=WEEK,
            publish_run_id="123",
            article_sha256="a" * 64,
            manifest_sha256="b" * 64,
        )

        for identifier in (
            identity.publish_run_id,
            identity.article_sha256,
            identity.manifest_sha256,
        ):
            with self.subTest(identifier=identifier):
                self.assertFalse(
                    detect._run_metadata_associates_identity(
                        {"display_title": f"publish run 9{identifier}"},
                        identity,
                    )
                )

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

    def _auto_pre_submit_jobs(self, *, detect_conclusion: str = "failure") -> list[dict]:
        return [
            {
                "name": "Detect eligible weekly publication",
                "conclusion": detect_conclusion,
                "steps": [
                    {
                        "name": "Detect eligible manifest",
                        "conclusion": detect_conclusion,
                    },
                    {
                        "name": "Check for duplicate dispatch",
                        "conclusion": "skipped",
                    },
                ],
            },
            {
                "name": "Protected podcast dispatch",
                "conclusion": "skipped",
                "steps": [],
            },
            {
                "name": "Observe-only summary",
                "conclusion": "skipped",
                "steps": [],
            },
        ]

    def _legacy_identity_log(
        self,
        *,
        week: str = WEEK,
        run_id: str = RUN_ID,
        sha: str = KNOWN_SHA256,
    ) -> str:
        return "\n".join(
            (
                f"  output: week={week}",
                f"  output: publish_run_id={run_id}",
                f"  output: article_sha256={sha}",
            )
        )

    def _router(
        self,
        *,
        auto_runs: list[dict] | None = None,
        trigger_runs: list[dict] | None = None,
        jobs: dict[int, list[dict]] | None = None,
        logs: dict[int, str] | None = None,
    ):
        routes = {
            (
                f"https://api.github.com/repos/{self._REPO}/issues?state=all&per_page=100&page=1"
            ): _FakeHTTPResponse(b"[]"),
            self._workflow_runs_url(detect.AUTO_DISPATCH_WORKFLOW): _gh_runs_response(
                auto_runs or []
            ),
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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_missing_requested_manifest_digest_fails_closed(self):
        result = detect.check_duplicate_result(
            WEEK,
            RUN_ID,
            KNOWN_SHA256,
            self._GH_TOKEN,
            self._REPO,
        )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.reason, "missing_requested_manifest_sha256")

    def test_missing_requested_manifest_digest_fails_closed_without_credentials(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            result = detect.check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertEqual(result.reason, "missing_requested_manifest_sha256")

    def test_invalid_requested_manifest_digest_rejected_without_repository(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "canonical formats"):
                detect.check_duplicate_result(
                    WEEK,
                    RUN_ID,
                    KNOWN_SHA256,
                    self._GH_TOKEN,
                    manifest_sha256="not-a-digest",
                )

    def test_compatibility_wrapper_fails_closed_without_credentials(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            duplicate, prior_url = detect.check_duplicate(WEEK, RUN_ID, KNOWN_SHA256, "")

        self.assertTrue(duplicate)
        self.assertIsNone(prior_url)

    def test_complete_identity_without_credentials_fails_closed(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            result = detect.check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.reason, "trusted_evidence_configuration_unavailable")

    def test_compatibility_wrapper_preserves_positional_token_and_repo_order(self):
        duplicate, prior_url = detect.check_duplicate(
            WEEK,
            RUN_ID,
            KNOWN_SHA256,
            "",
            "",
            manifest_sha256=KNOWN_MANIFEST_SHA256,
        )

        self.assertTrue(duplicate)
        self.assertIsNone(prior_url)

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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "duplicate")
        self.assertTrue(result.is_duplicate)
        self.assertEqual(result.prior_run_url, run["html_url"])

    def test_conflicting_manifest_digest_fails_closed(self):
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
                            manifest_sha="c" * 64,
                        )
                    },
                ),
            ),
        ):
            result = _check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.reason, "conflicting_manifest_sha256")

    def test_exact_four_field_receipt_blocks_duplicate_dispatch(self):
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
            result = _check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "duplicate")
        self.assertTrue(result.is_duplicate)

    def test_missing_manifest_digest_on_submitted_receipt_fails_closed(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        receipt = json.loads(
            self._receipt_log(state="submitted").split(detect.RECEIPT_PREFIX, 1)[1]
        )
        receipt.pop("manifest_sha256")
        log_text = (
            f"{detect.RECEIPT_PREFIX}{json.dumps(receipt, sort_keys=True, separators=(',', ':'))}\n"
        )
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: log_text},
                ),
            ),
        ):
            result = _check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertEqual(result.reason, "missing_manifest_sha256")

    def test_conflicting_pre_submit_receipt_still_fails_closed(self):
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
                            state="pre_submit_failed",
                            manifest_sha="c" * 64,
                        )
                    },
                ),
            ),
        ):
            result = _check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertEqual(result.reason, "conflicting_manifest_sha256")

    def test_duplicate_prevented_receipt_preserves_prior_submission_proof(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="duplicate_prevented")},
                ),
            ),
        ):
            result = _check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "duplicate")
        self.assertEqual(result.reason, "duplicate_prevented")

    def test_unknown_exact_receipt_state_fails_closed(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="future_state")},
                ),
            ),
        ):
            result = _check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertEqual(result.reason, "unknown_receipt_state")

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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.prior_run_url, run["html_url"])

    def test_legacy_submission_rejection_remains_ambiguous(self):
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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_v2_pre_acceptance_rejection_allows_retry(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={
                        self._AUTO_RUN_ID: self._v2_receipt_log(
                            state="submission_rejected",
                            api_status_category="http_rejected_pre_acceptance",
                        )
                    },
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_v2_unclassified_ledger_rejection_fails_closed(self):
        receipt = detect.parse_receipt(
            self._v2_receipt_log(state="submission_rejected").removeprefix(detect.RECEIPT_PREFIX)
        )
        self.assertIsInstance(receipt, detect.DispatchReceipt)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch.object(detect, "list_ledger_receipts", return_value=[receipt]),
            mock.patch.object(detect, "_list_workflow_runs", return_value=[]),
        ):
            result = detect.check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256="b" * 64,
            )

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_v2_manifest_digest_is_part_of_identity(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._v2_receipt_log(state="accepted")},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256="c" * 64,
            )
        self.assertEqual(result.status, "clear")

    def test_v2_exact_handoff_entry_is_fail_closed(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: self._v2_receipt_log(state="handoff_entered")},
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256="b" * 64,
            )
        self.assertEqual(result.status, "ambiguous_prior_submission")

    def test_cancelled_empty_run_is_unrelated(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        run["conclusion"] = "cancelled"
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run], jobs={self._AUTO_RUN_ID: []}, logs={self._AUTO_RUN_ID: ""}
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256="b" * 64,
            )
        self.assertEqual(result.status, "clear")

    def test_cancelled_run_with_exact_output_identity_is_ambiguous(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        outputs = "\n".join(
            (
                f"output: week={WEEK}",
                f"output: publish_run_id={RUN_ID}",
                f"output: article_sha256={KNOWN_SHA256}",
                f"output: manifest_sha256={'b' * 64}",
            )
        )
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run], jobs={self._AUTO_RUN_ID: []}, logs={self._AUTO_RUN_ID: outputs}
                ),
            ),
        ):
            result = detect.check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256="b" * 64,
            )
        self.assertEqual(result.status, "ambiguous_prior_submission")

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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_cancelled_empty_run_with_related_metadata_is_ambiguous(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        run["conclusion"] = "cancelled"
        run["display_title"] = f"Auto-dispatch for publish run {RUN_ID}"
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: []},
                    logs={self._AUTO_RUN_ID: ""},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_w38_ignores_unrelated_legacy_no_anchor_pre_submit_run(self):
        w38_week = "2026-W38"
        w38_run_id = "34806779896"
        w38_sha = "c935702d6887c2a9f88fc919ba74acbbc874278436b24d0872388f2e0322e1ef"
        legacy_run_id = 34255052607
        run = self._run(
            legacy_run_id,
            workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH,
        )
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={legacy_run_id: self._auto_pre_submit_jobs()},
                    logs={legacy_run_id: ""},
                ),
            ),
        ):
            result = _check_duplicate_result(
                w38_week,
                w38_run_id,
                w38_sha,
                self._GH_TOKEN,
                self._REPO,
            )

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_rerun_with_latest_skipped_protected_job_remains_ambiguous(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        run["run_attempt"] = 2
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: self._auto_pre_submit_jobs()},
                    logs={self._AUTO_RUN_ID: ""},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_pre_boundary_persistence_failure_allows_safe_retry(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        jobs = [
            {
                "name": "Protected podcast dispatch",
                "conclusion": "failure",
                "steps": [
                    {
                        "name": "Persist prepared receipt",
                        "conclusion": "failure",
                    },
                    {
                        "name": "Persist handoff-entered boundary",
                        "conclusion": "skipped",
                    },
                    {
                        "name": "Trigger podcast generation",
                        "conclusion": "skipped",
                    },
                ],
            }
        ]
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: jobs},
                    logs={self._AUTO_RUN_ID: self._legacy_identity_log()},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_same_identity_legacy_uncertain_submission_still_blocks(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        jobs = [
            {
                "name": "Protected podcast dispatch",
                "conclusion": "failure",
                "steps": [
                    {
                        "name": "Trigger podcast generation",
                        "conclusion": "failure",
                    }
                ],
            }
        ]
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: jobs},
                    logs={self._AUTO_RUN_ID: self._legacy_identity_log()},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.prior_run_url, run["html_url"])

    def test_exact_identity_canonical_duplicate_still_blocks(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: self._auto_pre_submit_jobs()},
                    logs={self._AUTO_RUN_ID: self._receipt_log(state="submitted")},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "duplicate")
        self.assertTrue(result.is_duplicate)
        self.assertEqual(result.reason, "submitted")

    def test_unclassified_authoritative_rejection_remains_ambiguous(self):
        receipt = state.DispatchReceipt(
            receipt_id="receipt-1",
            created_at="2026-09-21T21:00:00Z",
            dispatch_run_id=str(self._AUTO_RUN_ID),
            attempt_id=f"{self._AUTO_RUN_ID}-1",
            identity=state.CanonicalPublicationIdentity(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                KNOWN_MANIFEST_SHA256,
            ),
            receipt_state="submission_rejected",
            actions_run_url=f"https://github.com/{self._REPO}/actions/runs/{self._AUTO_RUN_ID}",
        )
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch.object(detect, "list_ledger_receipts", return_value=[receipt]),
            mock.patch.object(detect, "_list_workflow_runs", return_value=[]),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.reason, "exact_identity_uncertain")

    def test_different_complete_legacy_identity_is_ignored(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        jobs = [
            {
                "name": "Protected podcast dispatch",
                "conclusion": "failure",
                "steps": [
                    {
                        "name": "Trigger podcast generation",
                        "conclusion": "failure",
                    }
                ],
            }
        ]
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    auto_runs=[run],
                    jobs={self._AUTO_RUN_ID: jobs},
                    logs={
                        self._AUTO_RUN_ID: self._legacy_identity_log(
                            week="2026-W39",
                            run_id="34999999999",
                            sha="a" * 64,
                        )
                    },
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_legacy_manual_real_dispatch_with_conflicting_manifest_is_ambiguous(self):
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
                mock.patch.object(
                    detect, "read_manifest_from_publish", return_value=_make_manifest()
                ),
                mock.patch.object(
                    detect,
                    "read_manifest_bytes_from_publish",
                    return_value=b'{"manifest":"conflicting"}',
                ),
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
                result = _check_duplicate_result(
                    WEEK,
                    RUN_ID,
                    KNOWN_SHA256,
                    self._GH_TOKEN,
                    self._REPO,
                    repo_root=repo.root,
                    manifest_sha256=hashlib.sha256(
                        json.dumps(_make_manifest(), sort_keys=True).encode()
                    ).hexdigest(),
                )

            self.assertEqual(result.status, "ambiguous_prior_submission")
            self.assertFalse(result.is_duplicate)
            self.assertEqual(result.prior_run_url, run["html_url"])
            self.assertEqual(result.reason, "conflicting_manifest_sha256")
        finally:
            repo.cleanup()

    def test_legacy_manual_real_dispatch_uses_reconstructed_manifest_digest(self):
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
            manifest_bytes = json.dumps(_make_manifest(), separators=(",", ":")).encode()
            manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
            with (
                mock.patch.object(detect, "fetch_publish_branch"),
                mock.patch.object(
                    detect, "read_manifest_from_publish", return_value=_make_manifest()
                ),
                mock.patch.object(
                    detect, "read_manifest_bytes_from_publish", return_value=manifest_bytes
                ),
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
                result = _check_duplicate_result(
                    WEEK,
                    RUN_ID,
                    KNOWN_SHA256,
                    self._GH_TOKEN,
                    self._REPO,
                    repo_root=repo.root,
                    manifest_sha256=manifest_sha256,
                )

            self.assertEqual(result.status, "duplicate")
            self.assertTrue(result.is_duplicate)
        finally:
            repo.cleanup()

    def test_legacy_manual_real_dispatch_without_manifest_digest_fails_closed(self):
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
                mock.patch.object(
                    detect, "read_manifest_from_publish", return_value=_make_manifest()
                ),
                mock.patch.object(
                    detect,
                    "read_manifest_bytes_from_publish",
                    side_effect=ValueError("unavailable"),
                ),
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
                result = _check_duplicate_result(
                    WEEK,
                    RUN_ID,
                    KNOWN_SHA256,
                    self._GH_TOKEN,
                    self._REPO,
                    repo_root=repo.root,
                    manifest_sha256=KNOWN_MANIFEST_SHA256,
                )

            self.assertEqual(result.status, "ambiguous_prior_submission")
            self.assertEqual(result.reason, "missing_manifest_sha256")
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
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_successful_manual_run_with_related_metadata_and_missing_marker_is_ambiguous(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
        )
        run["display_title"] = f"Manual podcast dispatch for publish run {RUN_ID}"
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    trigger_runs=[run],
                    jobs={self._TRIGGER_RUN_ID: self._trigger_jobs("success")},
                    logs={self._TRIGGER_RUN_ID: ""},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_legacy_manual_success_with_related_metadata_and_no_marker_fails_closed(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
            head_sha="not-a-sync",
        )
        run["display_title"] = f"Manual podcast dispatch for publish run {RUN_ID}"
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    trigger_runs=[run],
                    jobs={self._TRIGGER_RUN_ID: self._trigger_jobs("success")},
                    logs={self._TRIGGER_RUN_ID: "handoff completed without legacy marker"},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_readable_manual_rerun_with_skipped_handoff_remains_ambiguous(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
        )
        run["run_attempt"] = 2
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    trigger_runs=[run],
                    jobs={self._TRIGGER_RUN_ID: self._trigger_jobs("skipped")},
                    logs={self._TRIGGER_RUN_ID: ""},
                ),
            ),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_readable_single_attempt_manual_skipped_handoff_is_pre_submit(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
        )
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=self._router(
                    trigger_runs=[run],
                    jobs={self._TRIGGER_RUN_ID: self._trigger_jobs("skipped")},
                    logs={self._TRIGGER_RUN_ID: ""},
                ),
            ),
        ):
            result = _check_duplicate_result(
                WEEK,
                RUN_ID,
                KNOWN_SHA256,
                self._GH_TOKEN,
                self._REPO,
                manifest_sha256=KNOWN_MANIFEST_SHA256,
            )

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_complete_evidence_outage_fails_closed(self):
        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=OSError("network error")),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.reason, "trusted_evidence_unavailable")

    def test_missing_evidence_configuration_fails_closed(self):
        with mock.patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "ambient-token", "GITHUB_REPOSITORY": "ambient/repo"},
            clear=True,
        ):
            for token, repository in ((None, self._REPO), (self._GH_TOKEN, "")):
                with self.subTest(token=bool(token), repository=bool(repository)):
                    result = detect.check_duplicate_result(
                        WEEK,
                        RUN_ID,
                        KNOWN_SHA256,
                        token,
                        repository,
                        manifest_sha256=KNOWN_MANIFEST_SHA256,
                    )
                    self.assertEqual(result.status, "ambiguous_prior_submission")
                    self.assertFalse(result.is_duplicate)
                    self.assertEqual(
                        result.reason,
                        "trusted_evidence_configuration_unavailable",
                    )

    def test_unreadable_related_run_evidence_returns_ambiguous(self):
        run = self._run(self._AUTO_RUN_ID, workflow_path=detect.AUTO_DISPATCH_WORKFLOW_PATH)
        run["name"] = f"Auto-dispatch: {WEEK} publish-run {RUN_ID}"
        run["display_title"] = run["name"]
        run["conclusion"] = "success"

        def _open(req, timeout=20):
            url = req.full_url
            if url == (
                f"https://api.github.com/repos/{self._REPO}/issues?state=all&per_page=100&page=1"
            ):
                return _FakeHTTPResponse(b"[]")
            if url == self._workflow_runs_url(detect.AUTO_DISPATCH_WORKFLOW):
                return _gh_runs_response([run])
            if url == self._workflow_runs_url(detect.TRIGGER_PODCAST_WORKFLOW):
                return _gh_runs_response([])
            if url in {self._jobs_url(self._AUTO_RUN_ID), self._logs_url(self._AUTO_RUN_ID)}:
                raise OSError("network error")
            raise AssertionError(f"Unexpected URL fetched: {url}")

        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=_open),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)

    def test_unreadable_unrelated_manual_failure_is_nonblocking(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
        )

        def _open(req, timeout=20):
            url = req.full_url
            if url == (
                f"https://api.github.com/repos/{self._REPO}/issues?state=all&per_page=100&page=1"
            ):
                return _FakeHTTPResponse(b"[]")
            if url == self._workflow_runs_url(detect.AUTO_DISPATCH_WORKFLOW):
                return _gh_runs_response([])
            if url == self._workflow_runs_url(detect.TRIGGER_PODCAST_WORKFLOW):
                return _gh_runs_response([run])
            if url == self._jobs_url(self._TRIGGER_RUN_ID):
                return _gh_jobs_response(self._trigger_jobs("failure"))
            if url == self._logs_url(self._TRIGGER_RUN_ID):
                raise OSError("network error")
            raise AssertionError(f"Unexpected URL fetched: {url}")

        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=_open),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)

    def test_unreadable_related_manual_failure_remains_ambiguous(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
        )
        run["display_title"] = f"Manual podcast dispatch for publish run {RUN_ID}"

        def _open(req, timeout=20):
            url = req.full_url
            if url == (
                f"https://api.github.com/repos/{self._REPO}/issues?state=all&per_page=100&page=1"
            ):
                return _FakeHTTPResponse(b"[]")
            if url == self._workflow_runs_url(detect.AUTO_DISPATCH_WORKFLOW):
                return _gh_runs_response([])
            if url == self._workflow_runs_url(detect.TRIGGER_PODCAST_WORKFLOW):
                return _gh_runs_response([run])
            if url == self._jobs_url(self._TRIGGER_RUN_ID):
                return _gh_jobs_response(self._trigger_jobs("failure"))
            if url == self._logs_url(self._TRIGGER_RUN_ID):
                raise OSError("network error")
            raise AssertionError(f"Unexpected URL fetched: {url}")

        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=_open),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.reason, "related_history_evidence_unavailable")

    def test_unreadable_manual_skipped_handoff_is_pre_submit(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
        )

        def _open(req, timeout=20):
            url = req.full_url
            if url == (
                f"https://api.github.com/repos/{self._REPO}/issues?state=all&per_page=100&page=1"
            ):
                return _FakeHTTPResponse(b"[]")
            if url == self._workflow_runs_url(detect.AUTO_DISPATCH_WORKFLOW):
                return _gh_runs_response([])
            if url == self._workflow_runs_url(detect.TRIGGER_PODCAST_WORKFLOW):
                return _gh_runs_response([run])
            if url == self._jobs_url(self._TRIGGER_RUN_ID):
                return _gh_jobs_response(self._trigger_jobs("skipped"))
            if url == self._logs_url(self._TRIGGER_RUN_ID):
                raise OSError("network error")
            raise AssertionError(f"Unexpected URL fetched: {url}")

        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=_open),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)
        self.assertIsNone(result.reason)

    def test_unreadable_manual_rerun_with_skipped_job_remains_ambiguous(self):
        run = self._run(
            self._TRIGGER_RUN_ID,
            workflow_path=detect.TRIGGER_PODCAST_WORKFLOW_PATH,
        )
        run["run_attempt"] = 2
        skipped_job = [{"name": "trigger-podcast", "conclusion": "skipped", "steps": []}]

        def _open(req, timeout=20):
            url = req.full_url
            if url == self._workflow_runs_url(detect.AUTO_DISPATCH_WORKFLOW):
                return _gh_runs_response([])
            if url == self._workflow_runs_url(detect.TRIGGER_PODCAST_WORKFLOW):
                return _gh_runs_response([run])
            if url == self._jobs_url(self._TRIGGER_RUN_ID):
                return _gh_jobs_response(skipped_job)
            if url == self._logs_url(self._TRIGGER_RUN_ID):
                raise OSError("network error")
            raise AssertionError(f"Unexpected URL fetched: {url}")

        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=_open),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)

        self.assertEqual(result.status, "ambiguous_prior_submission")
        self.assertFalse(result.is_duplicate)


# ---------------------------------------------------------------------------
# TestSelfBlockedPreHandoffRetry — W39 run 35562322880 regression
# ---------------------------------------------------------------------------


class TestSelfBlockedPreHandoffRetry(unittest.TestCase):
    """A week's own provably pre-handoff dedup failure must not block its retry."""

    _GH_TOKEN = "ghp_faketoken"
    _REPO = "example/squadscope"
    _SELF_RUN_ID = 35562322880
    _SOURCE_RUN_ID = 32730109166
    _API = "https://api.github.com/repos/example/squadscope"

    def _url(self, run_id: int) -> str:
        return f"https://github.com/{self._REPO}/actions/runs/{run_id}"

    def _auto_run(self, run_id: int = _SELF_RUN_ID, **overrides) -> dict:
        run = {
            "id": run_id,
            "run_attempt": 1,
            "path": detect.AUTO_DISPATCH_WORKFLOW_PATH,
            "name": "Auto-dispatch: main",
            "display_title": "Auto-dispatch: main",
            "head_branch": "main",
            "event": "workflow_run",
            "status": "completed",
            "conclusion": "failure",
            "head_sha": "1a3d888f7a430721935d597c168a7c25aadf4672",
            "html_url": self._url(run_id),
        }
        run.update(overrides)
        return run

    def _source_run(self, run_id: int = _SOURCE_RUN_ID, **overrides) -> dict:
        run = {
            "id": run_id,
            "run_attempt": 1,
            "path": detect.TRIGGER_PODCAST_WORKFLOW_PATH,
            "name": "Trigger podcast generation",
            "display_title": "Trigger podcast generation",
            "head_branch": "main",
            "event": "workflow_dispatch",
            "status": "completed",
            "conclusion": "cancelled",
            "head_sha": "def456",
            "html_url": self._url(run_id),
        }
        run.update(overrides)
        return run

    def _w39_jobs(self, *, dispatch_conclusion: str = "skipped", dispatch_steps=None) -> list:
        """Job shape observed for W39 run 35562322880."""
        return [
            {
                "name": "Detect eligible weekly publication",
                "conclusion": "failure",
                "steps": [
                    {"name": "Detect eligible manifest", "conclusion": "success"},
                    {"name": "Check for duplicate dispatch", "conclusion": "failure"},
                    {"name": "Emit detect receipt", "conclusion": "success"},
                    {"name": "Record ambiguous prior dispatch notice", "conclusion": "success"},
                ],
            },
            {
                "name": "Protected podcast dispatch",
                "conclusion": dispatch_conclusion,
                "steps": dispatch_steps or [],
            },
            {"name": "Observe-only summary", "conclusion": "skipped", "steps": []},
        ]

    def _source_jobs(self, **overrides) -> list:
        """Job shape observed for cancelled trigger-podcast run 32730109166."""
        job = {
            "name": "trigger-podcast",
            "status": "completed",
            "conclusion": "cancelled",
            "runner_id": 0,
            "runner_name": "",
            "steps": [],
        }
        job.update(overrides)
        return [job]

    def _receipt(self, state: str, *, run_id: int = _SELF_RUN_ID, **overrides) -> str:
        payload = {
            "schema_version": detect.RECEIPT_SCHEMA_VERSION,
            "workflow": "auto-podcast-dispatch",
            "receipt_state": state,
            "week": WEEK,
            "publish_run_id": RUN_ID,
            "article_sha256": KNOWN_SHA256,
            "manifest_sha256": KNOWN_MANIFEST_SHA256,
            "prior_run_url": self._url(self._SOURCE_RUN_ID),
            "actions_run_url": self._url(run_id),
        }
        payload.update(overrides)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return f"{detect.RECEIPT_PREFIX}{encoded}\n"

    def _check(
        self,
        *,
        auto_runs: list,
        trigger_runs: list | None = None,
        jobs: dict | None = None,
        logs: dict | None = None,
        runs_by_id: dict | None = None,
    ):
        routes = {
            f"{self._API}/issues?state=all&per_page=100&page=1": lambda: b"[]",
            (
                f"{self._API}/actions/workflows/{detect.AUTO_DISPATCH_WORKFLOW}/runs"
                f"?per_page={detect.WORKFLOW_LOOKBACK_RUNS}"
            ): lambda: json.dumps({"workflow_runs": auto_runs}).encode(),
            (
                f"{self._API}/actions/workflows/{detect.TRIGGER_PODCAST_WORKFLOW}/runs"
                f"?per_page={detect.WORKFLOW_LOOKBACK_RUNS}"
            ): lambda: json.dumps({"workflow_runs": trigger_runs or []}).encode(),
        }
        for run_id, run_jobs in (jobs or {}).items():
            routes[f"{self._API}/actions/runs/{run_id}/jobs?per_page=100"] = (
                lambda run_jobs=run_jobs: json.dumps({"jobs": run_jobs}).encode()
            )
        for run_id, log_text in (logs or {}).items():
            routes[f"{self._API}/actions/runs/{run_id}/logs"] = lambda log_text=log_text: (
                _gh_logs_response(log_text).getvalue()
            )
        for run_id, run in (runs_by_id or {}).items():
            routes[f"{self._API}/actions/runs/{run_id}"] = lambda run=run: json.dumps(run).encode()
        fetched: list[str] = []

        def _open(req, timeout=20):
            fetched.append(req.full_url)
            body = routes.get(req.full_url)
            if body is None:
                raise OSError(f"unavailable in fixture: {req.full_url}")
            return _FakeHTTPResponse(body())

        with (
            mock.patch.object(detect, "fetch_publish_branch"),
            mock.patch("urllib.request.urlopen", side_effect=_open),
        ):
            result = _check_duplicate_result(WEEK, RUN_ID, KNOWN_SHA256, self._GH_TOKEN, self._REPO)
        return result, fetched

    def _w39_history(self, **run_overrides) -> dict:
        return {
            "auto_runs": [self._auto_run(**run_overrides)],
            "trigger_runs": [self._source_run()],
            "jobs": {
                self._SELF_RUN_ID: self._w39_jobs(),
                self._SOURCE_RUN_ID: self._source_jobs(),
            },
            "logs": {
                self._SELF_RUN_ID: self._receipt("ambiguous_prior_submission"),
                self._SOURCE_RUN_ID: "",
            },
        }

    def assertBlocked(self, result, reason: str | None = None) -> None:
        self.assertNotEqual(result.status, "clear")
        if reason is not None:
            self.assertEqual(result.reason, reason)

    # -- R1: provable pre-handoff failure does not block ---------------------

    def test_w39_own_pre_handoff_verdict_does_not_block_retry(self):
        result, _ = self._check(**self._w39_history())

        self.assertEqual(result.status, "clear")
        self.assertFalse(result.is_duplicate)
        self.assertEqual(result.ignored_pre_handoff_runs, (self._url(self._SELF_RUN_ID),))

    def test_verdict_without_source_does_not_block_retry(self):
        history = self._w39_history()
        history["logs"][self._SELF_RUN_ID] = self._receipt(
            "ambiguous_prior_submission", prior_run_url=""
        )

        result, _ = self._check(**history)

        self.assertEqual(result.status, "clear")

    def test_verdict_source_outside_lookback_is_fetched_and_reproven(self):
        history = self._w39_history()
        history["trigger_runs"] = []
        history["runs_by_id"] = {self._SOURCE_RUN_ID: self._source_run()}

        result, fetched = self._check(**history)

        self.assertEqual(result.status, "clear")
        self.assertIn(f"{self._API}/actions/runs/{self._SOURCE_RUN_ID}", fetched)

    def test_budget_allows_two_ignored_self_blocked_attempts(self):
        history = self._w39_history()
        second = self._SELF_RUN_ID + 1
        history["auto_runs"].insert(0, self._auto_run(second))
        history["jobs"][second] = self._w39_jobs()
        history["logs"][second] = self._receipt("ambiguous_prior_submission", run_id=second)

        result, _ = self._check(**history)

        self.assertEqual(result.status, "clear")
        self.assertEqual(len(result.ignored_pre_handoff_runs), 2)

    # -- R4: bounded retries -------------------------------------------------

    def test_budget_blocks_after_three_ignored_self_blocked_attempts(self):
        history = self._w39_history()
        for offset in (1, 2):
            run_id = self._SELF_RUN_ID + offset
            history["auto_runs"].insert(0, self._auto_run(run_id))
            history["jobs"][run_id] = self._w39_jobs()
            history["logs"][run_id] = self._receipt("ambiguous_prior_submission", run_id=run_id)

        result, _ = self._check(**history)

        self.assertBlocked(result, "pre_handoff_retry_budget_exhausted")
        self.assertEqual(len(result.ignored_pre_handoff_runs), 3)

    # -- R2: handed off still blocks ------------------------------------------

    def test_handed_off_attempt_still_blocks(self):
        history = self._w39_history()
        history["jobs"][self._SELF_RUN_ID] = self._w39_jobs(
            dispatch_conclusion="success",
            dispatch_steps=[{"name": "Trigger podcast generation", "conclusion": "success"}],
        )

        result, _ = self._check(**history)

        self.assertBlocked(result, "ambiguous_prior_submission")
        self.assertEqual(result.ignored_pre_handoff_runs, ())

    def test_handoff_receipt_for_identity_in_later_run_still_blocks(self):
        history = self._w39_history()
        later = self._SELF_RUN_ID + 1
        history["auto_runs"].insert(0, self._auto_run(later, conclusion="success"))
        history["jobs"][later] = self._w39_jobs(dispatch_conclusion="success")
        history["logs"][later] = self._receipt("submitted", run_id=later)

        result, _ = self._check(**history)

        self.assertEqual(result.status, "duplicate")
        self.assertTrue(result.is_duplicate)

    def test_verdict_source_with_real_submission_still_blocks(self):
        history = self._w39_history()
        history["trigger_runs"] = []
        source = self._auto_run(self._SOURCE_RUN_ID, conclusion="success")
        history["auto_runs"].append(source)
        history["jobs"][self._SOURCE_RUN_ID] = self._w39_jobs(dispatch_conclusion="success")
        history["logs"][self._SOURCE_RUN_ID] = self._receipt(
            "handoff_entered", run_id=self._SOURCE_RUN_ID
        )

        result, _ = self._check(**history)

        self.assertBlocked(result, "handoff_entered")
        self.assertEqual(result.ignored_pre_handoff_runs, (self._url(self._SELF_RUN_ID),))

    # -- R2: unknown handoff outcome still blocks (UNKNOWN != FAILED) --------

    def test_unknown_outcome_variants_still_block(self):
        cases = {
            "rerun_attempt": {"run_attempt": 2},
            "in_progress": {"status": "in_progress", "conclusion": None},
            "succeeded": {"conclusion": "success"},
            "non_main_branch": {"head_branch": "feature"},
            "unexpected_event": {"event": "push"},
        }
        for name, overrides in cases.items():
            with self.subTest(case=name):
                result, _ = self._check(**self._w39_history(**overrides))
                self.assertBlocked(result, "ambiguous_prior_submission")
                self.assertEqual(result.ignored_pre_handoff_runs, ())

    def test_unreadable_or_incomplete_job_evidence_still_blocks(self):
        job_cases = {
            "jobs_unreadable": None,
            "dispatch_job_missing": [self._w39_jobs()[0]],
            "duplicate_dispatch_job": self._w39_jobs() + [self._w39_jobs()[1]],
            "dedup_step_not_failed": [
                {
                    **self._w39_jobs()[0],
                    "steps": [{"name": "Check for duplicate dispatch", "conclusion": "success"}],
                },
                *self._w39_jobs()[1:],
            ],
            "dispatch_steps_missing": [
                self._w39_jobs()[0],
                {"name": "Protected podcast dispatch", "conclusion": "skipped"},
                self._w39_jobs()[2],
            ],
            "dispatch_steps_null": [
                self._w39_jobs()[0],
                {"name": "Protected podcast dispatch", "conclusion": "skipped", "steps": None},
                self._w39_jobs()[2],
            ],
            "detect_steps_null": [
                {**self._w39_jobs()[0], "steps": None},
                *self._w39_jobs()[1:],
            ],
            "detect_step_not_object": [
                {**self._w39_jobs()[0], "steps": ["Check for duplicate dispatch"]},
                *self._w39_jobs()[1:],
            ],
            "job_not_object": [*self._w39_jobs(), "Protected podcast dispatch"],
            "dispatch_step_ran": self._w39_jobs(
                dispatch_steps=[{"name": "Set up job", "conclusion": "success"}]
            ),
        }
        for name, run_jobs in job_cases.items():
            with self.subTest(case=name):
                history = self._w39_history()
                if run_jobs is None:
                    del history["jobs"][self._SELF_RUN_ID]
                else:
                    history["jobs"][self._SELF_RUN_ID] = run_jobs
                result, _ = self._check(**history)
                self.assertBlocked(result, "ambiguous_prior_submission")

    def test_receipt_not_emitted_by_carrying_run_still_blocks(self):
        for name, overrides in {
            "foreign_actions_run_url": {"actions_run_url": self._url(99)},
            "missing_actions_run_url": {"actions_run_url": ""},
            "foreign_workflow": {"workflow": "trigger-podcast"},
        }.items():
            with self.subTest(case=name):
                history = self._w39_history()
                history["logs"][self._SELF_RUN_ID] = self._receipt(
                    "ambiguous_prior_submission", **overrides
                )
                result, _ = self._check(**history)
                self.assertBlocked(result, "ambiguous_prior_submission")

    def test_multiple_verdict_receipts_in_one_run_still_block(self):
        history = self._w39_history()
        receipt = self._receipt("ambiguous_prior_submission")
        history["logs"][self._SELF_RUN_ID] = receipt + receipt

        result, _ = self._check(**history)

        self.assertBlocked(result, "ambiguous_prior_submission")

    def test_unverifiable_verdict_source_still_blocks(self):
        cases = {
            "source_fetch_fails": {"trigger_runs": [], "runs_by_id": {}},
            "source_logs_expired_after_handoff": {"source_handoff_ran": True},
            "source_jobs_unreadable": {"drop_source_jobs": True},
            "source_in_progress": {
                "trigger_runs": [self._source_run(status="in_progress", conclusion=None)]
            },
            "source_jobs_empty": {"source_jobs": []},
            "source_jobs_unreadable_with_pre_submit_receipt": {
                "drop_source_jobs": True,
                "source_log": "PRE_SUBMIT",
            },
            "source_foreign_html_url": {
                "trigger_runs": [],
                "runs_by_id": {
                    self._SOURCE_RUN_ID: self._source_run(
                        html_url=f"https://github.com/other/repo/actions/runs/{self._SOURCE_RUN_ID}"
                    )
                },
            },
            "source_missing_html_url": {
                "trigger_runs": [],
                "runs_by_id": {self._SOURCE_RUN_ID: self._source_run(html_url=None)},
            },
            "source_foreign_workflow": {
                "trigger_runs": [],
                "runs_by_id": {
                    self._SOURCE_RUN_ID: self._source_run(path=".github/workflows/ci.yml")
                },
            },
        }
        for name, change in cases.items():
            with self.subTest(case=name):
                history = self._w39_history()
                if change.pop("source_handoff_ran", False):
                    del history["logs"][self._SOURCE_RUN_ID]
                    history["jobs"][self._SOURCE_RUN_ID] = self._source_jobs(
                        runner_id=7,
                        runner_name="GitHub Actions 7",
                        steps=[
                            {
                                "name": "Trigger podcast generation with existing manifest",
                                "conclusion": "success",
                            }
                        ],
                    )
                if change.pop("drop_source_jobs", False):
                    del history["jobs"][self._SOURCE_RUN_ID]
                if "source_jobs" in change:
                    history["jobs"][self._SOURCE_RUN_ID] = change.pop("source_jobs")
                if change.pop("source_log", None) == "PRE_SUBMIT":
                    history["logs"][self._SOURCE_RUN_ID] = self._receipt(
                        "pre_submit_failed", run_id=self._SOURCE_RUN_ID
                    )
                history.update(change)
                result, _ = self._check(**history)
                self.assertBlocked(result, "derived_verdict_source_unverifiable")

    def test_cancelled_source_job_that_got_a_runner_still_blocks(self):
        for name, overrides in {
            "runner_assigned": {"runner_id": 7, "runner_name": "GitHub Actions 7"},
            "runner_fields_missing": {"runner_id": None, "runner_name": None},
            "not_cancelled": {"conclusion": "failure"},
        }.items():
            with self.subTest(case=name):
                history = self._w39_history()
                history["jobs"][self._SOURCE_RUN_ID] = self._source_jobs(**overrides)
                result, _ = self._check(**history)
                self.assertBlocked(result, "legacy_submission_without_canonical_receipt")

    def test_unrelated_never_started_manual_run_does_not_block_first_dispatch(self):
        result, _ = self._check(
            auto_runs=[],
            trigger_runs=[self._source_run()],
            jobs={self._SOURCE_RUN_ID: self._source_jobs()},
            logs={self._SOURCE_RUN_ID: ""},
        )

        self.assertEqual(result.status, "clear")
        self.assertEqual(result.ignored_pre_handoff_runs, ())

    def test_manual_handoff_failure_is_scoped_to_its_publish_run(self):
        failed_handoff = self._source_jobs(
            conclusion="failure",
            runner_id=7,
            runner_name="GitHub Actions 7",
            steps=[
                {
                    "name": "Trigger podcast generation with existing manifest",
                    "conclusion": "failure",
                }
            ],
        )
        for name, log_text, expected in (
            (
                "other_publish_run",
                "::notice::Using manifest from crawl-and-publish run 29744859230 (x)\n",
                "clear",
            ),
            (
                "same_publish_run",
                f"::notice::Using manifest from crawl-and-publish run {RUN_ID} (x)\n",
                "ambiguous_prior_submission",
            ),
            ("publish_run_not_logged", "", "ambiguous_prior_submission"),
        ):
            with self.subTest(case=name):
                result, _ = self._check(
                    auto_runs=[],
                    trigger_runs=[self._source_run(conclusion="failure")],
                    jobs={self._SOURCE_RUN_ID: failed_handoff},
                    logs={self._SOURCE_RUN_ID: log_text},
                )
                self.assertEqual(result.status, expected)

    def test_w39_pre_recovery_history_replay_allows_retry(self):
        """Replay of the W39 history shape before the manual recovery dispatch."""
        unrelated_failed = 30162265246
        history = self._w39_history()
        history["trigger_runs"].append(self._source_run(unrelated_failed, conclusion="failure"))
        history["jobs"][unrelated_failed] = self._source_jobs(
            conclusion="failure",
            runner_id=1000091927,
            runner_name="GitHub Actions 1000091927",
            steps=[
                {
                    "name": "Trigger podcast generation with existing manifest",
                    "conclusion": "failure",
                }
            ],
        )
        history["logs"][unrelated_failed] = (
            "::notice::Using manifest from crawl-and-publish run 29744859230 (x)\n"
        )

        result, _ = self._check(**history)

        self.assertEqual(result.status, "clear")
        self.assertEqual(result.ignored_pre_handoff_runs, (self._url(self._SELF_RUN_ID),))

    def test_verdict_source_url_must_be_a_distinct_same_repo_run(self):
        for name, prior_run_url in {
            "self_reference": self._url(self._SELF_RUN_ID),
            "foreign_repo": f"https://github.com/other/repo/actions/runs/{self._SOURCE_RUN_ID}",
            "not_a_run_url": "https://example.com/runs/1",
        }.items():
            with self.subTest(case=name):
                history = self._w39_history()
                history["logs"][self._SELF_RUN_ID] = self._receipt(
                    "ambiguous_prior_submission", prior_run_url=prior_run_url
                )
                result, _ = self._check(**history)
                self.assertBlocked(result, "derived_verdict_source_unverifiable")

    def test_verdict_source_chain_is_bounded_and_cycle_safe(self):
        history = self._w39_history()
        history["trigger_runs"] = []
        chain = [
            self._SOURCE_RUN_ID + offset for offset in range(detect.MAX_VERDICT_SOURCE_FETCHES + 1)
        ]
        history["runs_by_id"] = {}
        previous = self._SELF_RUN_ID
        for run_id in chain:
            history["logs"][previous] = self._receipt(
                "ambiguous_prior_submission", run_id=previous, prior_run_url=self._url(run_id)
            )
            history["jobs"][run_id] = self._w39_jobs()
            history["runs_by_id"][run_id] = self._auto_run(run_id)
            previous = run_id
        history["logs"][previous] = self._receipt(
            "ambiguous_prior_submission", run_id=previous, prior_run_url=self._url(chain[0])
        )

        result, _ = self._check(**history)

        self.assertBlocked(result)

    # -- R3: identity scope ----------------------------------------------------

    def test_verdict_for_other_identity_is_not_counted(self):
        history = self._w39_history()
        other = self._SELF_RUN_ID + 1
        history["auto_runs"].insert(0, self._auto_run(other))
        history["jobs"][other] = self._w39_jobs()
        history["logs"][other] = self._receipt(
            "ambiguous_prior_submission", run_id=other, week="2026-W38"
        )

        result, _ = self._check(**history)

        self.assertEqual(result.status, "clear")
        self.assertEqual(result.ignored_pre_handoff_runs, (self._url(self._SELF_RUN_ID),))

    # -- R5: loud logs and summary --------------------------------------------

    def test_cli_summary_explains_proceed_decision_without_receipt_prefix(self):
        result = detect.DuplicateCheckResult(
            status="clear",
            is_duplicate=False,
            ignored_pre_handoff_runs=(self._url(self._SELF_RUN_ID),),
        )
        self._assert_cli_summary(result, ["✅ Dispatch may proceed", self._url(self._SELF_RUN_ID)])

    def test_cli_summary_explains_blocked_decision(self):
        result = detect.DuplicateCheckResult(
            status="ambiguous_prior_submission",
            is_duplicate=False,
            prior_run_url=self._url(self._SELF_RUN_ID),
            reason="pre_handoff_retry_budget_exhausted",
        )
        self._assert_cli_summary(
            result,
            ["⛔ Blocked", "pre_handoff_retry_budget_exhausted", "workflow_dispatch"],
            expect_exit=True,
        )

    def _assert_cli_summary(self, result, needles, *, expect_exit=False) -> None:
        TEST_WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_WORKSPACES_ROOT) as tmp:
            summary = Path(tmp) / "summary.md"
            output = Path(tmp) / "output.txt"
            env = {
                "GH_TOKEN": self._GH_TOKEN,
                "GITHUB_REPOSITORY": self._REPO,
                "GITHUB_STEP_SUMMARY": str(summary),
                "GITHUB_OUTPUT": str(output),
            }
            argv = [
                "--check-duplicate",
                "--week",
                WEEK,
                "--publish-run-id",
                RUN_ID,
                "--article-sha256",
                KNOWN_SHA256,
                "--manifest-sha256",
                KNOWN_MANIFEST_SHA256,
            ]
            stdout = io.StringIO()
            with (
                mock.patch.dict(os.environ, env),
                mock.patch.object(detect, "check_duplicate_result", return_value=result),
                mock.patch("sys.stdout", stdout),
                mock.patch("sys.stderr", io.StringIO()),
            ):
                if expect_exit:
                    with self.assertRaises(SystemExit):
                        detect.main(argv)
                else:
                    detect.main(argv)
            text = summary.read_text(encoding="utf-8")
        self.assertIn("## Podcast dispatch dedup decision", text)
        for needle in needles:
            self.assertIn(needle, text)
        self.assertNotIn(detect.RECEIPT_PREFIX, text)
        self.assertNotIn(detect.RECEIPT_PREFIX, stdout.getvalue())
        for run_url in result.ignored_pre_handoff_runs:
            self.assertIn("::notice::Ignoring own earlier auto-dispatch attempt", stdout.getvalue())
            self.assertIn(run_url, stdout.getvalue())


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

    def test_article_url_uses_canonical_lowercase_week_path(self):
        self.assertEqual(
            detect.article_url_from_article_path("content/weekly/2026/W38.md"),
            "https://claracle.com/weekly/2026/w38/",
        )


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
