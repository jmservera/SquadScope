"""Tests for topic-config-driven query loading in crawl.py."""

import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

import scripts.crawl as crawl

SAMPLE_CONFIG = """\
topic:
  id: ai-ml
  name: "AI & Machine Learning"

queries:
  primary:
    - "topic:machine-learning stars:>50 pushed:>{last_week}"
    - "topic:artificial-intelligence stars:>50 pushed:>{last_week}"
  secondary:
    - "topic:transformers stars:>100 pushed:>{last_week}"

quality:
  min_repos_per_week: 5
"""

TESTS_ROOT = Path(__file__).resolve().parent


class LoadTopicQueriesTests(unittest.TestCase):
    def test_resolves_template_variables(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", dir=TESTS_ROOT, delete=False
        ) as f:
            f.write(SAMPLE_CONFIG)
            f.flush()
            config_path = f.name

        try:
            result = crawl.load_topic_queries(
                config_path, {"last_week": "2026-05-11", "today": "2026-05-18"}
            )
            self.assertEqual(
                result["primary"],
                [
                    "topic:machine-learning stars:>50 pushed:>2026-05-11",
                    "topic:artificial-intelligence stars:>50 pushed:>2026-05-11",
                ],
            )
            self.assertEqual(
                result["secondary"],
                ["topic:transformers stars:>100 pushed:>2026-05-11"],
            )
            self.assertEqual(result["min_repos_per_week"], 5)
        finally:
            os.unlink(config_path)

    def test_raises_on_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            crawl.load_topic_queries("/nonexistent.yml", {})


class MainWithConfigTests(unittest.TestCase):
    def _make_fake_client_class(self, queries: list[str], results_per_query: int = 0):
        """Return a FakeClient class that records queries and returns N fake repos."""

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
                return [
                    {"full_name": f"org/repo-{i}", "stargazers_count": 100}
                    for i in range(results_per_query)
                ]

            def has_readme(self, full_name: str) -> bool:
                return True

        return FakeClient

    def test_config_uses_primary_queries_only_when_enough_repos(self) -> None:
        queries: list[str] = []
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", dir=TESTS_ROOT, delete=False
        ) as f:
            f.write(SAMPLE_CONFIG)
            f.flush()
            config_path = f.name

        try:
            FakeClient = self._make_fake_client_class(queries, results_per_query=5)
            args = Namespace(
                since="2026-05-11",
                as_of=None,
                max_results=25,
                output="data/raw/test-config.json",
                topic=None,
                config=config_path,
            )
            with (
                mock.patch.object(crawl, "parse_args", return_value=args),
                mock.patch.dict("os.environ", {"GITHUB_TOKEN": "token"}, clear=False),
                mock.patch.object(crawl, "GitHubClient", FakeClient),
                mock.patch.object(crawl, "load_previous_star_snapshot", return_value={}),
                mock.patch.object(crawl, "write_payload"),
                mock.patch.object(crawl, "print"),
            ):
                exit_code = crawl.main()

            self.assertEqual(exit_code, 0)
            # Only primary queries run (2 primaries), secondary not needed
            self.assertEqual(len(queries), 2)
            self.assertIn("topic:machine-learning", queries[0])
            self.assertIn("topic:artificial-intelligence", queries[1])
            self.assertIn("pushed:>2026-05-11", queries[0])
        finally:
            os.unlink(config_path)

    def test_config_runs_secondary_when_primary_insufficient(self) -> None:
        queries: list[str] = []
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", dir=TESTS_ROOT, delete=False
        ) as f:
            f.write(SAMPLE_CONFIG)
            f.flush()
            config_path = f.name

        try:
            # Return only 1 repo per query → 2 total from primaries < min_repos_per_week=5
            FakeClient = self._make_fake_client_class(queries, results_per_query=1)
            args = Namespace(
                since="2026-05-11",
                as_of=None,
                max_results=25,
                output="data/raw/test-config-secondary.json",
                topic=None,
                config=config_path,
            )
            with (
                mock.patch.object(crawl, "parse_args", return_value=args),
                mock.patch.dict("os.environ", {"GITHUB_TOKEN": "token"}, clear=False),
                mock.patch.object(crawl, "GitHubClient", FakeClient),
                mock.patch.object(crawl, "load_previous_star_snapshot", return_value={}),
                mock.patch.object(crawl, "write_payload"),
                mock.patch.object(crawl, "print"),
            ):
                exit_code = crawl.main()

            self.assertEqual(exit_code, 0)
            # 2 primary + 1 secondary = 3 queries
            self.assertEqual(len(queries), 3)
            self.assertIn("topic:transformers", queries[2])
        finally:
            os.unlink(config_path)

    def test_no_config_preserves_existing_behavior(self) -> None:
        """Without --config, queries use the hardcoded stars:>50 pattern."""
        queries: list[str] = []
        FakeClient = self._make_fake_client_class(queries, results_per_query=0)
        args = Namespace(
            since="2026-05-11",
            as_of=None,
            max_results=25,
            output="data/raw/test-noconfig.json",
            topic=None,
            config=None,
        )
        with (
            mock.patch.object(crawl, "parse_args", return_value=args),
            mock.patch.dict("os.environ", {"GITHUB_TOKEN": "token"}, clear=False),
            mock.patch.object(crawl, "GitHubClient", FakeClient),
            mock.patch.object(crawl, "load_previous_star_snapshot", return_value={}),
            mock.patch.object(crawl, "write_payload"),
            mock.patch.object(crawl, "print"),
        ):
            exit_code = crawl.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(queries, ["created:>2026-05-11 stars:>50", "pushed:>2026-05-11 stars:>50"])


if __name__ == "__main__":
    unittest.main()
