import io
import json
import sys
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
                    "candidate": {"summary_sha256": "a" * 64},
                    "analysis": {"ai_status": ai_status},
                    "promotion": {"eligible": True, "decision": "promote"},
                    "source_artifacts": [
                        {
                            "role": "raw",
                            "path": "data/raw/2026-W23.json",
                            "sha256": "b" * 64,
                            "generated_at": "2026-06-08T10:15:00Z",
                            "freshness": {"status": "fresh", "reasons": []},
                            "provenance": {
                                "path": "data/raw/2026-W23.json",
                                "sha256": "b" * 64,
                            },
                        },
                        {
                            "role": "blob",
                            "artifact_url": "https://example.blob.core.windows.net/artifacts/source.json",
                            "exists": True,
                            "size_bytes": 1024,
                        },
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
            # Create article file so article_content is included
            article_dir = Path(tmpdir) / "content" / "weekly" / "2026"
            article_dir.mkdir(parents=True)
            article_file = article_dir / "W23.md"
            article_file.write_text(
                "---\ntitle: Week 23 Report\nsummary: Week 23 summary.\n---\n# Heading\nBody content here.\n",
                encoding="utf-8",
            )

            payload = podcaster_handoff.build_payload(
                week="2026-W23",
                article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                article_path="content/weekly/2026/W23.md",
                publish_run_id="123456789",
                publish_mode="normal",
                manifest_path=manifest,
                repo_root=Path(tmpdir),
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
                {
                    "role": "raw",
                    "path": "data/raw/2026-W23.json",
                    "sha256": "b" * 64,
                    "generated_at": "2026-06-08T10:15:00Z",
                    "freshness": {"status": "fresh", "reasons": []},
                    "provenance": {
                        "path": "data/raw/2026-W23.json",
                        "sha256": "b" * 64,
                    },
                },
                {
                    "role": "blob",
                    "url": "https://example.blob.core.windows.net/artifacts/source.json",
                    "exists": True,
                    "size_bytes": 1024,
                },
            ],
        )
        self.assertNotIn("artifact_url", payload["source_artifacts"][1])
        self.assertNotIn("freshness_status", payload["source_artifacts"][0])
        self.assertNotIn("force", payload)
        self.assertNotIn("dry_run", payload)
        # article_content and article_title from the article file
        self.assertIn("article_content", payload)
        self.assertIn("Week 23 Report", payload["article_title"])
        self.assertEqual(payload["article_summary"], "Week 23 summary.")
        self.assertIn("Body content here.", payload["article_content"])

    def test_smoke_payload_matches_real_weekly_handoff_shape(self) -> None:
        podcaster_root = Path(__file__).resolve().parents[2] / "SquadScope-Podcaster"
        if not podcaster_root.exists():
            self.skipTest("SquadScope-Podcaster checkout is not available for contract validation")

        sys.path.insert(0, str(podcaster_root))
        try:
            from podcaster.validation import validate_payload
        finally:
            sys.path.pop(0)

        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            manifest = self._write_manifest(Path(tmpdir))
            article_dir = Path(tmpdir) / "content" / "weekly" / "2026"
            article_dir.mkdir(parents=True)
            (article_dir / "W23.md").write_text(
                "---\ntitle: Week 23 Report\nsummary: Week 23 summary.\n---\n# Week 23 Report\nBody content here.\n",
                encoding="utf-8",
            )

            payload = podcaster_handoff.build_payload(
                week="2026-W23",
                article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                article_path="content/weekly/2026/W23.md",
                publish_run_id="123456789",
                publish_mode="normal",
                manifest_path=manifest,
                podcast_config_path=Path(__file__).resolve().parents[1] / "config" / "podcast.json",
                podcaster_dry_run=True,
                repo_root=Path(tmpdir),
            )

        self.assertEqual(validate_payload(payload), [])
        self.assertTrue(payload["dry_run"])
        self.assertIn("source_artifacts", payload)
        self.assertTrue(payload["source_artifacts"])
        self.assertIn("podcast_config", payload)
        self.assertIn("script_directions", payload)
        self.assertIn("spotify_publish", payload)
        self.assertEqual(payload["article_title"], "Week 23 Report")
        self.assertEqual(payload["article_summary"], "Week 23 summary.")

    def test_podcaster_dry_run_sets_payload_flag(self) -> None:
        payload = podcaster_handoff.build_payload(
            week="2026-W23",
            article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
            article_path="content/weekly/2026/W23.md",
            publish_run_id="123456789",
            publish_mode="normal",
            podcaster_dry_run=True,
        )

        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["publish_mode"], "normal")

    def test_build_payload_normalizes_absolute_article_path(self) -> None:
        payload = podcaster_handoff.build_payload(
            week="2026-W23",
            article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
            article_path="/home/runner/work/SquadScope/SquadScope/content/weekly/2026/W23.md",
            publish_run_id="123456789",
            publish_mode="normal",
        )

        self.assertEqual(payload["article_path"], "content/weekly/2026/W23.md")

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
        self.assertEqual(sent_payload["week"], "2026-W23")
        self.assertEqual(sent_payload["article_url"], "https://jmservera.github.io/SquadScope/weekly/2026/w23/")
        self.assertEqual(sent_payload["article_path"], "content/weekly/2026/W23.md")
        self.assertEqual(sent_payload["publish_run_id"], "123456789")
        self.assertEqual(sent_payload["publish_mode"], "normal")
        self.assertIn("podcast_config", sent_payload)
        self.assertEqual(sent_payload["podcast_config"]["name"], "Claracle")
        self.assertIn("script_directions", sent_payload)
        self.assertIn("music_mix", sent_payload["script_directions"])
        self.assertIn("spotify_publish", sent_payload)
        self.assertEqual(sent_payload["spotify_publish"]["publish_mode"], "draft")
        self.assertIsInstance(sent_payload["spotify_publish"]["season_number"], int)
        self.assertIsInstance(sent_payload["spotify_publish"]["episode_number"], int)
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

    def test_missing_manifest_path_raises_fail_closed(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            missing = Path(tmpdir) / "does-not-exist.json"
            with self.assertRaisesRegex(podcaster_handoff.PodcasterHandoffError, "does not exist"):
                podcaster_handoff.build_payload(
                    week="2026-W23",
                    article_url="https://jmservera.github.io/SquadScope/weekly/2026/w23/",
                    article_path="content/weekly/2026/W23.md",
                    publish_run_id="123456789",
                    publish_mode="normal",
                    manifest_path=missing,
                )

    def test_validate_response_rejects_failed_status_or_errors(self) -> None:
        with self.assertRaises(podcaster_handoff.PodcasterHandoffError):
            podcaster_handoff.validate_response({"job_id": "podcast-1", "status": "failed", "errors": []})
        with self.assertRaises(podcaster_handoff.PodcasterHandoffError):
            podcaster_handoff.validate_response({"job_id": "podcast-1", "status": "accepted", "errors": ["bad"]})

    def test_validate_response_rejects_unexpected_or_missing_status(self) -> None:
        for status in ("rejected", "queued", "pending", None):
            with self.assertRaisesRegex(
                podcaster_handoff.PodcasterHandoffError, "known success status"
            ):
                podcaster_handoff.validate_response({"job_id": "podcast-1", "status": status, "errors": []})
        with self.assertRaisesRegex(
            podcaster_handoff.PodcasterHandoffError, "known success status"
        ):
            podcaster_handoff.validate_response({"job_id": "podcast-1", "errors": []})

    def test_validate_response_accepts_known_success_status(self) -> None:
        result = podcaster_handoff.validate_response(
            {"job_id": "podcast-1", "status": "accepted", "errors": []}
        )
        self.assertEqual(result["status"], "accepted")

    def test_validate_response_accepts_dry_run_status(self) -> None:
        result = podcaster_handoff.validate_response(
            {"job_id": "podcast-1", "status": "dry_run", "errors": []}
        )
        self.assertEqual(result["status"], "dry_run")

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

    def test_article_url_from_page_path_normalizes_absolute_runner_path(self) -> None:
        self.assertEqual(
            podcaster_handoff.article_url_from_page_path(
                "https://jmservera.github.io/SquadScope/",
                "/home/runner/work/SquadScope/SquadScope/content/weekly/2026/W23.md",
            ),
            "https://jmservera.github.io/SquadScope/weekly/2026/w23/",
        )


    def test_build_payload_includes_article_content_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            article_dir = base / "content" / "weekly" / "2026"
            article_dir.mkdir(parents=True)
            article = article_dir / "W24.md"
            article.write_text(
                "---\ntitle: My Title\nsummary: My summary.\n---\n# Heading\nHello world.\n",
                encoding="utf-8",
            )

            payload = podcaster_handoff.build_payload(
                week="2026-W24",
                article_url="https://example.com/weekly/2026/w24/",
                article_path="content/weekly/2026/W24.md",
                publish_run_id="999",
                publish_mode="normal",
                podcaster_dry_run=True,
                repo_root=base,
            )

        self.assertEqual(payload["article_title"], "My Title")
        self.assertEqual(payload["article_summary"], "My summary.")
        self.assertIn("Hello world.", payload["article_content"])
        self.assertIn("---\ntitle: My Title\nsummary: My summary.\n---", payload["article_content"])

    def test_build_payload_resolves_spotify_publish_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            article_dir = base / "content" / "weekly" / "2026"
            article_dir.mkdir(parents=True)
            article = article_dir / "W24.md"
            article.write_text(
                "---\ntitle: Skills Go Vertical\nsummary: This week we explore agent skills.\n---\n# Heading\nHello world.\n",
                encoding="utf-8",
            )

            payload = podcaster_handoff.build_payload(
                week="2026-W24",
                article_url="https://example.com/weekly/2026/w24/",
                article_path="content/weekly/2026/W24.md",
                publish_run_id="999",
                publish_mode="normal",
                podcaster_dry_run=True,
                repo_root=base,
            )

        self.assertEqual(
            payload["spotify_publish"]["title"],
            "Why Skills Go Vertical Matters for AI, GitHub & Developer Trends | W24",
        )
        self.assertIn("This week we explore agent skills.", payload["spotify_publish"]["description"])
        self.assertEqual(payload["spotify_publish"]["season_number"], 2026)
        self.assertEqual(payload["spotify_publish"]["episode_number"], 24)

    def test_build_payload_truncates_resolved_spotify_publish_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            article_dir = base / "content" / "weekly" / "2026"
            article_dir.mkdir(parents=True)
            article = article_dir / "W24.md"
            article.write_text(
                f"---\ntitle: {'T' * 250}\nsummary: {'S' * 5000}\n---\n# Heading\nHello world.\n",
                encoding="utf-8",
            )

            payload = podcaster_handoff.build_payload(
                week="2026-W24",
                article_url="https://example.com/weekly/2026/w24/",
                article_path="content/weekly/2026/W24.md",
                publish_run_id="999",
                publish_mode="normal",
                podcaster_dry_run=True,
                repo_root=base,
            )

        self.assertLessEqual(len(payload["spotify_publish"]["title"]), 200)
        self.assertTrue(payload["spotify_publish"]["title"].startswith("Why "))
        desc = payload["spotify_publish"]["description"]
        self.assertLessEqual(len(desc), 4000)
        self.assertTrue(desc.startswith("<p>"))
        # Verify HTML is properly closed after truncation
        self.assertTrue(desc.endswith("</p>"), "Truncated description must end with a closed tag")

    def test_render_template_value_raises_on_malformed_format_string(self) -> None:
        context = {"year": 2026, "week": 24}
        with self.assertRaises(podcaster_handoff.PodcasterHandoffError) as cm:
            podcaster_handoff._render_template_value("{year}-W{week}: {unclosed", context)
        self.assertIn("invalid format syntax", str(cm.exception))

    def test_build_payload_extracts_title_from_heading_when_no_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            article_dir = base / "content" / "weekly" / "2026"
            article_dir.mkdir(parents=True)
            article = article_dir / "W24.md"
            article.write_text("# My Heading Title\nSome content.\n", encoding="utf-8")

            payload = podcaster_handoff.build_payload(
                week="2026-W24",
                article_url="https://example.com/weekly/2026/w24/",
                article_path="content/weekly/2026/W24.md",
                publish_run_id="999",
                publish_mode="normal",
                podcaster_dry_run=True,
                repo_root=base,
            )

        self.assertEqual(payload["article_title"], "My Heading Title")

    def test_build_payload_truncates_large_article_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            article_dir = base / "content" / "weekly" / "2026"
            article_dir.mkdir(parents=True)
            article = article_dir / "W24.md"
            large_content = "# Title\n" + "x" * 60_000
            article.write_text(large_content, encoding="utf-8")

            payload = podcaster_handoff.build_payload(
                week="2026-W24",
                article_url="https://example.com/weekly/2026/w24/",
                article_path="content/weekly/2026/W24.md",
                publish_run_id="999",
                publish_mode="normal",
                podcaster_dry_run=True,
                repo_root=base,
            )

        self.assertEqual(len(payload["article_content"]), 50_000)
        self.assertEqual(payload["article_title"], "Title")

    def test_build_payload_missing_article_file_omits_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            payload = podcaster_handoff.build_payload(
                week="2026-W24",
                article_url="https://example.com/weekly/2026/w24/",
                article_path="content/weekly/2026/W24.md",
                publish_run_id="999",
                publish_mode="normal",
                podcaster_dry_run=True,
                repo_root=base,
            )

        self.assertNotIn("article_content", payload)
        self.assertNotIn("article_title", payload)

    def test_read_article_content_path_traversal_raises(self) -> None:
       """Path traversal attempts must raise PodcasterHandoffError."""
       with tempfile.TemporaryDirectory() as tmpdir:
           base = Path(tmpdir)
           # Create a file outside repo_root
           outside = base.parent / "secret.txt"
           outside.write_text("secret data", encoding="utf-8")
           try:
               with self.assertRaises(podcaster_handoff.PodcasterHandoffError) as ctx:
                   podcaster_handoff._read_article_content("../secret.txt", repo_root=base)
               self.assertIn("outside the repository root", str(ctx.exception))
           finally:
               outside.unlink(missing_ok=True)

    def test_read_article_content_unreadable_file_raises(self) -> None:
       """An existing but unreadable file must raise, not silently omit content."""
       with tempfile.TemporaryDirectory() as tmpdir:
           base = Path(tmpdir)
           article_dir = base / "content" / "weekly"
           article_dir.mkdir(parents=True)
           article_file = article_dir / "W24.md"
           article_file.write_text("# Test", encoding="utf-8")
           # Make file unreadable
           article_file.chmod(0o000)
           try:
               with self.assertRaises(podcaster_handoff.PodcasterHandoffError) as ctx:
                   podcaster_handoff._read_article_content(
                       "content/weekly/W24.md", repo_root=base
                   )
               self.assertIn("could not be read", str(ctx.exception))
           finally:
               article_file.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
