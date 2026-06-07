import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib import error

import scripts.podcaster_handoff as podcaster_handoff


class _FakeHTTPResponse(io.BytesIO):
    status = 202

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def getcode(self):
        return self.status


class PodcasterHandoffTests(unittest.TestCase):
    def _write_manifest(self, base: Path, *, run_mode: str = "normal", ai_status: str = "ai") -> Path:
        manifest = base / "publish-manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "week": "2026-W23",
                    "run_id": "123456789",
                    "run_mode": run_mode,
                    "candidate": {"content_sha256": "a" * 64},
                    "analysis": {"ai_status": ai_status},
                    "promotion": {"eligible": True, "decision": "promote"},
                    "source_artifacts": [
                        {"role": "raw", "path": "data/raw/2026-W23.json", "sha256": "b" * 64},
                        {"role": "blob", "url": "https://example.blob.core.windows.net/artifacts/source.json"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def test_build_payload_uses_required_fields_and_real_optional_values(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            manifest = self._write_manifest(Path(tmpdir))

            payload = podcaster_handoff.build_payload(
                week="2026-W23",
                article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                article_path="content/weekly/2026/W23.md",
                publish_run_id="123456789",
                publish_mode="normal",
                manifest_path=manifest,
            )

        self.assertEqual(payload["week"], "2026-W23")
        self.assertEqual(payload["article_url"], "https://jmservera.github.io/SquadScope/weekly/2026/w23/")
        self.assertEqual(payload["article_path"], "content/weekly/2026/W23.md")
        self.assertEqual(payload["publish_run_id"], "123456789")
        self.assertEqual(payload["publish_mode"], "normal")
        self.assertEqual(payload["article_sha256"], "a" * 64)
        self.assertEqual(
            payload["source_artifacts"],
            [
                {"role": "raw", "path": "data/raw/2026-W23.json", "sha256": "b" * 64},
                {"role": "blob", "url": "https://example.blob.core.windows.net/artifacts/source.json"},
            ],
        )
        self.assertNotIn("force", payload)
        self.assertNotIn("dry_run", payload)

    def test_missing_config_skips_without_calling_podcaster(self) -> None:
        with mock.patch.object(podcaster_handoff.request, "urlopen") as urlopen_mock, mock.patch.dict(
            podcaster_handoff.os.environ, {"PODCASTER_API_KEY": ""}
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            exit_code = podcaster_handoff.main(
                [
                    "--week",
                    "2026-W23",
                    "--article-url",
                    "https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                    "--article-path",
                    "content/weekly/2026/W23.md",
                    "--publish-run-id",
                    "123456789",
                    "--endpoint",
                    "",
                ]
            )

        self.assertEqual(exit_code, 0)
        urlopen_mock.assert_not_called()
        self.assertIn("Podcaster handoff skipped", stdout.getvalue())

    def test_post_handoff_sends_auth_header_without_logging_value(self) -> None:
        response = _FakeHTTPResponse(json.dumps({"job_id": "podcast-2026-W23-abc12345", "status": "accepted", "errors": []}).encode())
        with mock.patch.object(podcaster_handoff.request, "urlopen", return_value=response) as urlopen_mock, mock.patch.dict(
            podcaster_handoff.os.environ, {"PODCASTER_API_KEY": "super-secret-value"}
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            exit_code = podcaster_handoff.main(
                [
                    "--week",
                    "2026-W23",
                    "--article-url",
                    "https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                    "--article-path",
                    "content/weekly/2026/W23.md",
                    "--publish-run-id",
                    "123456789",
                    "--endpoint",
                    "http://localhost:7071/api/generate",
                ]
            )

        self.assertEqual(exit_code, 0)
        req = urlopen_mock.call_args.args[0]
        self.assertEqual(req.get_header("X-podcaster-api-key"), "super-secret-value")
        self.assertEqual(req.get_header("Content-type"), "application/json")
        sent_payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(
            sent_payload,
            {
                "week": "2026-W23",
                "article_url": "https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                "article_path": "content/weekly/2026/W23.md",
                "publish_run_id": "123456789",
                "publish_mode": "normal",
            },
        )
        self.assertNotIn("super-secret-value", stdout.getvalue())

    def test_non_normal_publish_mode_skips_without_calling_podcaster(self) -> None:
        with mock.patch.object(podcaster_handoff.request, "urlopen") as urlopen_mock, mock.patch.dict(
            podcaster_handoff.os.environ, {"PODCASTER_API_KEY": "super-secret-value"}
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            exit_code = podcaster_handoff.main(
                [
                    "--week",
                    "2026-W23",
                    "--article-url",
                    "https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                    "--article-path",
                    "content/weekly/2026/W23.md",
                    "--publish-run-id",
                    "123456789",
                    "--publish-mode",
                    "restore",
                    "--endpoint",
                    "http://localhost:7071/api/generate",
                ]
            )

        self.assertEqual(exit_code, 0)
        urlopen_mock.assert_not_called()
        self.assertIn("skipped for publish mode restore", stdout.getvalue())
        self.assertNotIn("super-secret-value", stdout.getvalue())

    def test_manifest_blocks_restore_and_no_ai_handoffs(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            restore_manifest = self._write_manifest(base, run_mode="restore")
            with self.assertRaisesRegex(podcaster_handoff.PodcasterHandoffError, "not eligible"):
                podcaster_handoff.build_payload(
                    week="2026-W23",
                    article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                    article_path="content/weekly/2026/W23.md",
                    publish_run_id="123456789",
                    publish_mode="normal",
                    manifest_path=restore_manifest,
                )
            no_ai_manifest = self._write_manifest(base, ai_status="no-ai")
            with self.assertRaisesRegex(podcaster_handoff.PodcasterHandoffError, "not eligible"):
                podcaster_handoff.build_payload(
                    week="2026-W23",
                    article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                    article_path="content/weekly/2026/W23.md",
                    publish_run_id="123456789",
                    publish_mode="normal",
                    manifest_path=no_ai_manifest,
                )

    def test_validate_response_rejects_failed_status_or_errors(self) -> None:
        with self.assertRaises(podcaster_handoff.PodcasterHandoffError):
            podcaster_handoff.validate_response({"job_id": "podcast-1", "status": "failed", "errors": []})
        with self.assertRaises(podcaster_handoff.PodcasterHandoffError):
            podcaster_handoff.validate_response({"job_id": "podcast-1", "status": "accepted", "errors": ["bad"]})

    def test_non_2xx_response_fails_handoff(self) -> None:
        http_err = error.HTTPError(
            url="http://localhost:7071/api/generate",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=io.BytesIO(b'{"errors":["boom"]}'),
        )
        with mock.patch.object(podcaster_handoff.request, "urlopen", side_effect=http_err):
            with self.assertRaisesRegex(podcaster_handoff.PodcasterHandoffError, "HTTP 500"):
                podcaster_handoff.post_handoff(
                    "http://localhost:7071/api/generate",
                    "super-secret-value",
                    {
                        "week": "2026-W23",
                        "article_url": "https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                        "article_path": "content/weekly/2026/W23.md",
                        "publish_run_id": "123456789",
                        "publish_mode": "normal",
                    },
                )

    def test_article_url_from_page_path_matches_hugo_weekly_permalink(self) -> None:
        self.assertEqual(
            podcaster_handoff.article_url_from_page_path(
                "https://jmservera.github.io/SquadScope/",
                "content/weekly/2026/W23.md",
            ),
            "https://jmservera.github.io/SquadScope/weekly/2026/w23/",
        )


if __name__ == "__main__":
    unittest.main()
