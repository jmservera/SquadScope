import json
import tempfile
import unittest
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from unittest import mock

import scripts.crawl as crawl


class CrawlTests(unittest.TestCase):
    def test_significance_skip_reason_allows_common_description_terms(self) -> None:
        repo = {
            "name": "awesome-tool",
            "description": "Includes sample data and a live demo for deployment.",
            "topics": ["ai", "demo"],
            "fork": False,
            "is_template": False,
        }

        self.assertIsNone(crawl.significance_skip_reason(repo))

    def test_significance_skip_reason_still_flags_name_tokens(self) -> None:
        repo = {
            "name": "starter-kit",
            "description": "Production-ready auth service.",
            "topics": ["ai"],
            "fork": False,
            "is_template": False,
        }

        self.assertEqual(crawl.significance_skip_reason(repo), "low_signal_keyword")

    def test_get_json_preserves_payload_contract(self) -> None:
        client = crawl.GitHubClient("token")
        entry = crawl.CacheEntry(status=200, payload={"ok": True}, headers={}, fetched_at=crawl.utc_now())

        with mock.patch.object(client, "get_json_entry", return_value=entry):
            self.assertEqual(client.get_json("https://example.com"), {"ok": True})

    def test_load_previous_star_snapshot_checks_all_raw_dirs_and_logs_failures(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            snapshot_dir = base / "snapshots"
            raw_default_dir = base / "raw-default"
            custom_output_dir = base / "custom-output"
            snapshot_dir.mkdir()
            raw_default_dir.mkdir()
            custom_output_dir.mkdir()

            (snapshot_dir / "2026-W21-stars.json").write_text(
                '{"week": "2026-W21", "stars": {"owner/current": 1}}\n', encoding="utf-8"
            )
            (raw_default_dir / "2026-W20.json").write_text("{not-json}\n", encoding="utf-8")
            (raw_default_dir / "2026-W19.json").write_text(
                '{"week": "2026-W19", "stars": {"owner/older": 42}}\n', encoding="utf-8"
            )

            with mock.patch.object(crawl, "log") as log_mock:
                stars = crawl.load_previous_star_snapshot(snapshot_dir, "2026-W21", custom_output_dir, raw_default_dir)

            self.assertEqual(stars, {"owner/older": 42})
            logged = "\n".join(call.args[0] for call in log_mock.call_args_list)
            self.assertIn("invalid JSON", logged)

    def test_validate_payload_accepts_rate_limit_metadata_schema(self) -> None:
        payload = {
            "week": "2026-W21",
            "crawled_at": "2026-05-18T10:00:00Z",
            "new_repos": [],
            "trending_repos": [],
            "signals": {"top_topics": []},
            "metadata": {
                "api_calls_used": 1,
                "cache_hits": 2,
                "stale_cache_hits": 3,
                "rate_limit_limit": 5000,
                "rate_limit_remaining": 4990,
                "rate_limit_reset": 1747562400,
                "rate_limit_resource": "search",
                "partial_failures": [],
                "snapshot_path": "data/snapshots/2026-W21-stars.json",
            },
        }

        crawl.validate_payload(payload)

    def test_pause_for_rate_limit_cools_down_without_reset_hint(self) -> None:
        client = crawl.GitHubClient("token")
        client.rate_limit_limit = 5000
        client.rate_limit_remaining = 0
        client.rate_limit_resource = "core"

        with mock.patch("scripts.crawl.time.sleep") as sleep_mock:
            client._pause_for_rate_limit("https://example.com")

        sleep_mock.assert_called_once()

    def test_main_uses_open_ended_queries_for_live_runs(self) -> None:
        queries: list[str] = []

        class FakeClient:
            def __init__(self, token: str, **kwargs) -> None:
                self.token = token
                self.api_calls_used = 0
                self.cache_hits = 0
                self.stale_cache_hits = 0
                self.rate_limit_limit = None
                self.rate_limit_remaining = None
                self.rate_limit_reset = None
                self.rate_limit_resource = None
                self.errors = []

            def search_repositories(self, query: str, *, max_results: int = 1000):
                queries.append(query)
                return []

            def has_readme(self, full_name: str) -> bool:
                return True

        args = Namespace(since="2026-05-11", as_of=None, max_results=25, output="data/raw/test-live.json", topic=None, config=None)
        with mock.patch.object(crawl, "parse_args", return_value=args), mock.patch.dict(
            "os.environ", {"GITHUB_TOKEN": "token"}, clear=False
        ), mock.patch.object(crawl, "GitHubClient", FakeClient), mock.patch.object(
            crawl, "load_previous_star_snapshot", return_value={}
        ), mock.patch.object(crawl, "write_payload"), mock.patch.object(crawl, "print"):
            exit_code = crawl.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(queries, ["created:>2026-05-11 stars:>50", "pushed:>2026-05-11 stars:>50"])

    def test_main_uses_bounded_queries_for_backfills_and_fails_on_partial_errors(self) -> None:
        queries: list[str] = []

        class FakeClient:
            def __init__(self, token: str, **kwargs) -> None:
                self.token = token
                self.api_calls_used = 0
                self.cache_hits = 0
                self.stale_cache_hits = 0
                self.rate_limit_limit = None
                self.rate_limit_remaining = None
                self.rate_limit_reset = None
                self.rate_limit_resource = None
                self.errors = ["README lookup failed"]

            def search_repositories(self, query: str, *, max_results: int = 1000):
                queries.append(query)
                return []

            def has_readme(self, full_name: str) -> bool:
                return True

        args = Namespace(since="2026-05-11", as_of="2026-05-18", max_results=25, output="data/raw/test-backfill.json", topic=None, config=None)
        with mock.patch.object(crawl, "parse_args", return_value=args), mock.patch.dict(
            "os.environ", {"GITHUB_TOKEN": "token"}, clear=False
        ), mock.patch.object(crawl, "GitHubClient", FakeClient), mock.patch.object(
            crawl, "load_previous_star_snapshot", return_value={}
        ), mock.patch.object(crawl, "write_payload"), mock.patch.object(crawl, "print"):
            exit_code = crawl.main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            queries,
            [
                "created:2026-05-11..2026-05-18 stars:>50",
                "pushed:2026-05-11..2026-05-18 stars:>50",
            ],
        )

    def test_load_reusable_github_payload_accepts_same_day_matching_artifact(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            output = base / "data/raw/2026-W21.json"
            args = Namespace(since="2026-05-12", as_of="2026-05-19", max_results=25, output=str(output), topic=None, config=None)
            since = datetime(2026, 5, 12, tzinfo=crawl.UTC)
            window_end = datetime(2026, 5, 19, tzinfo=crawl.UTC)
            crawled_at = datetime(2026, 5, 19, 8, 0, tzinfo=crawl.UTC)
            checksum = crawl.github_crawl_config_checksum(args, since, window_end, 25)
            payload = {
                "week": "2026-W21",
                "crawled_at": crawl.iso_timestamp(crawled_at),
                "new_repos": [],
                "trending_repos": [],
                "signals": {"top_topics": []},
                "metadata": {
                    "api_calls_used": 1,
                    "cache_hits": 0,
                    "stale_cache_hits": 0,
                    "rate_limit_limit": None,
                    "rate_limit_remaining": None,
                    "rate_limit_reset": None,
                    "rate_limit_resource": None,
                    "partial_failures": [],
                    "snapshot_path": "data/snapshots/2026-W21-stars.json",
                    "crawl_window": {"since": "2026-05-12", "until": "2026-05-19"},
                    "crawl_config_checksum": checksum,
                    "schema_checksum": crawl.github_schema_checksum(),
                    "same_day_reuse": {"status": "not_reused", "source": "github"},
                },
            }
            payload["metadata"]["artifact_checksum"] = crawl.github_artifact_checksum(payload)
            crawl.write_payload(output, payload)

            reused = crawl.load_reusable_github_payload(
                output,
                week="2026-W21",
                crawled_at=datetime(2026, 5, 19, 10, 0, tzinfo=crawl.UTC),
                since=since,
                window_end=window_end,
                config_checksum=checksum,
            )

            self.assertIsNotNone(reused)
            self.assertEqual(reused["metadata"]["same_day_reuse"]["status"], "reused")
            self.assertEqual(reused["metadata"]["same_day_reuse"]["source_id"], "github-search")

    def test_main_reuses_valid_same_day_raw_artifact_without_github_token(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            existing = base / "reuse/raw-data/2026-W21.json"
            output = base / "data/raw/2026-W21.json"
            args = Namespace(
                since="2026-05-12",
                as_of="2026-05-19",
                max_results=25,
                output=str(output),
                topic=None,
                config=None,
                reuse_artifact=str(existing),
                source_refresh_policy="reuse-same-day",
                run_started_at="2026-05-19T10:00:00Z",
                current_code_sha="sha",
            )
            since = datetime(2026, 5, 12, tzinfo=crawl.UTC)
            window_end = datetime(2026, 5, 19, tzinfo=crawl.UTC)
            checksum = crawl.github_crawl_config_checksum(args, since, window_end, 25)
            payload = {
                "week": "2026-W21",
                "crawled_at": "2026-05-19T08:00:00Z",
                "new_repos": [],
                "trending_repos": [],
                "signals": {"top_topics": []},
                "metadata": {
                    "api_calls_used": 1,
                    "cache_hits": 0,
                    "stale_cache_hits": 0,
                    "rate_limit_limit": None,
                    "rate_limit_remaining": None,
                    "rate_limit_reset": None,
                    "rate_limit_resource": None,
                    "partial_failures": [],
                    "run_id": "111111",
                    "snapshot_path": "data/snapshots/2026-W21-stars.json",
                    "crawl_window": {"since": "2026-05-12", "until": "2026-05-19"},
                    "crawl_config_checksum": checksum,
                    "schema_checksum": crawl.github_schema_checksum(),
                    "same_day_reuse": {"status": "not_reused", "source": "github", "source_id": crawl.GITHUB_SOURCE_ID},
                    "crawler_code_sha": "sha",
                },
            }
            payload["metadata"]["artifact_checksum"] = crawl.github_artifact_checksum(payload)
            crawl.write_payload(existing, payload)

            with mock.patch.object(crawl, "parse_args", return_value=args), mock.patch.dict(
                "os.environ", {}, clear=True
            ), mock.patch.object(crawl, "utc_now", return_value=datetime(2026, 5, 19, 10, 0, tzinfo=crawl.UTC)):
                exit_code = crawl.main()

            self.assertEqual(exit_code, 0)
            reused = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(reused["metadata"]["same_day_reuse"]["status"], "reused")
            self.assertEqual(reused["metadata"]["source_refresh_policy"], "reuse-same-day")

    def test_main_emits_github_source_id_in_same_day_reuse_metadata(self) -> None:
        class FakeClient:
            def __init__(self, token: str, **kwargs) -> None:
                self.token = token
                self.api_calls_used = 0
                self.cache_hits = 0
                self.stale_cache_hits = 0
                self.rate_limit_limit = None
                self.rate_limit_remaining = None
                self.rate_limit_reset = None
                self.rate_limit_resource = None
                self.errors = []

            def search_repositories(self, query: str, *, max_results: int = 1000):
                return []

            def has_readme(self, full_name: str) -> bool:
                return True

        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            output = Path(tmpdir) / "data/raw/2026-W21.json"
            args = Namespace(
                since="2026-05-12",
                as_of="2026-05-19",
                max_results=25,
                output=str(output),
                topic=None,
                config=None,
                force_refresh=True,
            )

            with mock.patch.object(crawl, "parse_args", return_value=args), mock.patch.dict(
                "os.environ", {"GITHUB_TOKEN": "token"}, clear=False
            ), mock.patch.object(crawl, "GitHubClient", FakeClient), mock.patch.object(
                crawl, "load_previous_star_snapshot", return_value={}
            ), mock.patch.object(
                crawl, "snapshots_dir", return_value=Path(tmpdir) / "data/snapshots"
            ), mock.patch.object(
                crawl, "utc_now", return_value=datetime(2026, 5, 19, 10, 0, tzinfo=crawl.UTC)
            ):
                exit_code = crawl.main()

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["metadata"]["same_day_reuse"]["status"], "not_reused")
            self.assertEqual(payload["metadata"]["same_day_reuse"]["source"], "github")
            self.assertEqual(payload["metadata"]["same_day_reuse"]["source_id"], "github-search")

    def test_load_reusable_github_payload_rejects_config_mismatch(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            output = base / "data/raw/2026-W21.json"
            payload = {
                "week": "2026-W21",
                "crawled_at": "2026-05-19T08:00:00Z",
                "new_repos": [],
                "trending_repos": [],
                "signals": {"top_topics": []},
                "metadata": {
                    "api_calls_used": 1,
                    "cache_hits": 0,
                    "stale_cache_hits": 0,
                    "rate_limit_limit": None,
                    "rate_limit_remaining": None,
                    "rate_limit_reset": None,
                    "rate_limit_resource": None,
                    "partial_failures": [],
                    "snapshot_path": "data/snapshots/2026-W21-stars.json",
                    "crawl_window": {"since": "2026-05-12", "until": "2026-05-19"},
                    "crawl_config_checksum": "old",
                    "schema_checksum": crawl.github_schema_checksum(),
                    "same_day_reuse": {"status": "not_reused", "source": "github"},
                },
            }
            payload["metadata"]["artifact_checksum"] = crawl.github_artifact_checksum(payload)
            crawl.write_payload(output, payload)

            reused = crawl.load_reusable_github_payload(
                output,
                week="2026-W21",
                crawled_at=datetime(2026, 5, 19, 10, 0, tzinfo=crawl.UTC),
                since=datetime(2026, 5, 12, tzinfo=crawl.UTC),
                window_end=datetime(2026, 5, 19, tzinfo=crawl.UTC),
                config_checksum="new",
            )

            self.assertIsNone(reused)


if __name__ == "__main__":
    unittest.main()
