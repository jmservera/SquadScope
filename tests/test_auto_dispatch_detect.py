"""Tests for scripts/auto_dispatch_detect.py.

Written test-first (P03). The script does not exist yet; these tests will
show as errors/failures until Bender completes P01. That is expected.

Design assumptions about the script interface:
  - find_manifest_for_article(article_path: str, repo_root: Path) -> dict
    Reads article from repo_root/article_path; scans
    repo_root/data/candidates/<week>/*/publish-manifest.json on disk.
    Returns: {eligible, week, run_id, manifest_path, article_sha256,
              manifest_sha256, reason}
  - extract_week(article_path: str) -> str
    Extracts ISO week string (e.g. "2026-W37") from a weekly article path.
  - check_paused() -> bool
    Returns True iff PODCAST_AUTO_DISPATCH_PAUSED env var is truthy.
  - check_duplicate(week, run_id, gh_token, repo) -> (bool, str | None)
    Returns (is_duplicate, prior_run_url).

Specification gaps noted at bottom of this file.
"""

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
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
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "auto_dispatch"


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
            self._write_manifest(
                tmp, _make_manifest(run_id="99999999999"), run_id=RUN_ID
            )

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
            (manifest_dir / "publish-manifest.json").write_text(
                "{invalid", encoding="utf-8"
            )

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
    """Tests for check_duplicate().

    GitHub API calls are mocked at the urllib.request.urlopen level so no
    real network traffic is made.
    """

    _GH_TOKEN = "ghp_faketoken"
    _REPO = "example/squadscope"

    def _matching_run(self) -> dict:
        return {
            "id": 99999,
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/squadscope/actions/runs/99999",
            "inputs": {"week": WEEK, "run_id": RUN_ID},
            "name": f"podcast-dispatch-{WEEK}-{RUN_ID}",
        }

    def _other_run(self) -> dict:
        return {
            "id": 88888,
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/squadscope/actions/runs/88888",
            "inputs": {"week": "2026-W36", "run_id": "11111111111"},
            "name": "podcast-dispatch-2026-W36-11111111111",
        }

    def test_duplicate_detected(self):
        """GitHub API returns a matching successful run → is_duplicate=True."""
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = _gh_runs_response([self._matching_run()])

            is_dup, url = detect.check_duplicate(
                WEEK, RUN_ID, self._GH_TOKEN, self._REPO
            )

        self.assertTrue(is_dup)
        self.assertIsNotNone(url)

    def test_no_duplicate(self):
        """GitHub API returns runs for a different week → is_duplicate=False."""
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = _gh_runs_response([self._other_run()])

            is_dup, url = detect.check_duplicate(
                WEEK, RUN_ID, self._GH_TOKEN, self._REPO
            )

        self.assertFalse(is_dup)

    def test_api_failure_non_blocking(self):
        """GitHub API call fails → is_duplicate=False (fail open; rely on Podcaster idempotency)."""
        with mock.patch("urllib.request.urlopen", side_effect=OSError("network error")):
            is_dup, url = detect.check_duplicate(
                WEEK, RUN_ID, self._GH_TOKEN, self._REPO
            )

        self.assertFalse(is_dup)


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
