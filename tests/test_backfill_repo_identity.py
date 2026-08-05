from __future__ import annotations

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.backfill_repo_identity as backfill
from scripts.crawl import API_ROOT


def write_week(root: Path, week: str, repos: list[dict[str, object]]) -> None:
    raw_dir = root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    payload = {"week": week, "trending_repos": repos, "new_repos": []}
    (raw_dir / f"{week}.json").write_text(json.dumps(payload), encoding="utf-8")


def repo_record(full_name: str, stars: int, *, github_id: int | None = None) -> dict[str, object]:
    owner, name = full_name.split("/", 1)
    return {
        "owner": owner,
        "name": name,
        "full_name": full_name,
        "description": f"{full_name} description",
        "language": "Python",
        "stars": stars,
        "forks": 1,
        "created_at": "2026-01-01T00:00:00Z",
        "topics": ["ai-agents"],
        "license": None,
        "url": f"https://github.com/{full_name}",
        "id": github_id,
        "node_id": f"R_{github_id}" if github_id is not None else None,
        "archived": False,
        "disabled": False,
        "updated_at": "2026-07-29T00:00:00Z",
        "pushed_at": "2026-07-28T00:00:00Z",
        "api_url": f"https://api.github.com/repos/{full_name}",
    }


def write_config(root: Path, extra: str = "") -> None:
    config_dir = root / "config"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "observatory.toml").write_text(
        f"[repo_pages]\nenabled = false\n{extra}", encoding="utf-8"
    )


class StubGitHubClient:
    """Fakes GitHubClient.get_json_entry() for repository identity lookups."""

    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requested_full_names: list[str] = []

    def get_json_entry(
        self,
        url: str,
        params: dict[str, object] | None = None,
        *,
        acceptable_statuses: set[int] | None = None,
        ttl_seconds: int | None = None,
        allow_stale: bool = True,
        max_retries: int | None = None,
        max_delay_seconds: float = 300.0,
    ) -> SimpleNamespace:
        full_name = url.removeprefix(f"{API_ROOT}/repos/")
        self.requested_full_names.append(full_name)
        outcome = self.responses[full_name]
        if outcome == "raise":
            raise RuntimeError("simulated transient failure")
        return outcome


def test_collect_pending_full_names_returns_repos_missing_stable_id() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(
            root,
            "2026-W30",
            [
                repo_record("octo/fallback", 10, github_id=None),
                repo_record("octo/stable", 20, github_id=123),
            ],
        )
        write_config(root)

        pending = backfill.collect_pending_full_names(root)

        assert pending == {"octo/fallback": "octo/fallback"}


def test_run_backfill_dry_run_reports_counts_without_calling_api() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2026-W30", [repo_record("octo/fallback", 10, github_id=None)])
        write_config(root)
        output_path = root / "data/derived/observatory/repo-identity-backfill.json"

        counts = backfill.run_backfill(root, output_path, dry_run=True)

        assert counts == {
            "pending_total": 1,
            "already_checked": 0,
            "to_check": 1,
            "found": 0,
            "not_found": 0,
            "error": 0,
        }
        assert not output_path.exists()


def test_run_backfill_records_found_not_found_and_error_outcomes() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(
            root,
            "2026-W30",
            [
                repo_record("octo/found", 10, github_id=None),
                repo_record("octo/missing", 20, github_id=None),
                repo_record("octo/flaky", 30, github_id=None),
            ],
        )
        write_config(root)
        output_path = root / "data/derived/observatory/repo-identity-backfill.json"
        client = StubGitHubClient(
            {
                "octo/found": SimpleNamespace(
                    status=200,
                    payload={"id": 987, "node_id": "R_987", "full_name": "octo/found"},
                ),
                "octo/missing": SimpleNamespace(status=404, payload=None),
                "octo/flaky": "raise",
            }
        )

        counts = backfill.run_backfill(root, output_path, client=client)

        assert counts["found"] == 1
        assert counts["not_found"] == 1
        assert counts["error"] == 1
        entries = json.loads(output_path.read_text())["entries"]
        assert entries["octo/found"]["status"] == "found"
        assert entries["octo/found"]["github_id"] == "987"
        assert entries["octo/found"]["node_id"] == "R_987"
        assert entries["octo/missing"]["status"] == "not_found"
        assert entries["octo/flaky"]["status"] == "error"
        assert "simulated transient failure" in entries["octo/flaky"]["detail"]


def test_run_backfill_skips_already_checked_entries_on_resume() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(
            root,
            "2026-W30",
            [
                repo_record("octo/already-checked", 10, github_id=None),
                repo_record("octo/new", 20, github_id=None),
            ],
        )
        write_config(root)
        output_path = root / "data/derived/observatory/repo-identity-backfill.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "entries": {
                        "octo/already-checked": {"status": "not_found", "checked_at": "2026-08-01"}
                    },
                }
            ),
            encoding="utf-8",
        )
        client = StubGitHubClient(
            {"octo/new": SimpleNamespace(status=200, payload={"id": 42, "node_id": "R_42"})}
        )

        counts = backfill.run_backfill(root, output_path, client=client)

        assert client.requested_full_names == ["octo/new"]
        assert counts["already_checked"] == 1
        assert counts["to_check"] == 1
        entries = json.loads(output_path.read_text())["entries"]
        assert entries["octo/already-checked"]["status"] == "not_found"
        assert entries["octo/new"]["status"] == "found"


def test_run_backfill_requires_token_when_client_not_provided() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2026-W30", [repo_record("octo/fallback", 10, github_id=None)])
        write_config(root)
        output_path = root / "data/derived/observatory/repo-identity-backfill.json"

        with pytest.raises(ValueError, match="GITHUB_TOKEN"):
            backfill.run_backfill(root, output_path)
