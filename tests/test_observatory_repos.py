from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

import scripts.observatory_repos as observatory_repos

REPO_ROOT = Path(__file__).resolve().parent.parent


def write_week(root: Path, week: str, repos: list[dict[str, object]]) -> None:
    raw_dir = root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    payload = {"week": week, "trending_repos": repos, "new_repos": []}
    (raw_dir / f"{week}.json").write_text(json.dumps(payload), encoding="utf-8")


def repo_record(
    full_name: str,
    stars: int,
    topics: list[str] | None = None,
    *,
    github_id: int | None = None,
    archived: bool = False,
    disabled: bool = False,
) -> dict[str, object]:
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
        "topics": topics or ["ai-agents"],
        "license": None,
        "url": f"https://github.com/{full_name}",
        "id": github_id,
        "node_id": f"R_{github_id}" if github_id is not None else None,
        "archived": archived,
        "disabled": disabled,
        "updated_at": "2026-07-29T00:00:00Z",
        "pushed_at": "2026-07-28T00:00:00Z",
        "api_url": f"https://api.github.com/repos/{full_name}",
    }


def read_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    return yaml.safe_load(frontmatter)


def test_slug_scheme_uses_normalized_owner_and_name() -> None:
    assert observatory_repos.repo_slug("OpenHands/OpenHands") == "openhands-openhands"
    assert observatory_repos.repo_slug("n8n-io/n8n") == "n8n-io-n8n"
    assert observatory_repos.repo_slug("Owner.Name/Repo_Name") == "owner-name-repo-name"


def test_generates_only_repositories_above_configured_threshold() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            repos = [repo_record("octo/recurring", 100 + index)]
            if index < 3:
                repos.append(repo_record("octo/oneoff", 50 + index))
            write_week(root, week, repos)
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            """
[repo_pages]
enabled = true
recurrence_threshold_distinct_weekly_issues = 3
recurrence_threshold_operator = ">"
retention_years = 3
[repo_pages.lifecycle]
""".strip(),
            encoding="utf-8",
        )

        written = observatory_repos.generate(root)

        assert len(written) == 1
        page = root / "content" / "repo" / "octo-recurring" / "index.md"
        assert page.exists()
        assert not (root / "content" / "repo" / "octo-oneoff" / "index.md").exists()
        frontmatter = read_frontmatter(page)
        assert frontmatter["distinct_weekly_issues"] == 4
        assert frontmatter["recurrence_threshold"]["minimum_weeks"] == 4
        assert [entry["delta"] for entry in frontmatter["star_history"]] == [None, 1, 1, 1]
        assert frontmatter["weekly_appearances"][0]["url"] == "/weekly/2026/w21/"


def test_repo_github_topics_route_to_tags_not_curated_topics() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(
                root,
                week,
                [
                    repo_record(
                        "octo/recurring",
                        100 + index,
                        topics=["Raw Repo Topic", "llm", "AI Agents"],
                    )
                ],
            )

        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            "[repo_pages]\nenabled = true\n", encoding="utf-8"
        )
        topics_path = root / "data" / "taxonomy" / "topics.json"
        topics_path.parent.mkdir(parents=True)
        topics_path.write_text(
            json.dumps(
                {
                    "terms": {
                        "open-source-llms": {
                            "slug": "open-source-llms",
                            "display_name": "Open-Source LLMs",
                            "promoted": True,
                            "aliases": ["llm"],
                        },
                        "unpromoted": {
                            "slug": "unpromoted",
                            "display_name": "Unpromoted",
                            "promoted": False,
                            "aliases": ["raw-repo-topic"],
                        },
                    }
                }
            ),
            encoding="utf-8",
        )

        observatory_repos.generate(root)

        page_path = root / "content" / "repo" / "octo-recurring" / "index.md"
        page = page_path.read_text(encoding="utf-8")
        frontmatter = read_frontmatter(page_path)
        assert "topics" not in frontmatter
        assert frontmatter["tags"] == ["AI Agents", "llm", "Raw Repo Topic"]
        assert frontmatter["tag_links"] == [
            {"name": "AI Agents", "url": "/tags/ai-agents/"},
            {"name": "llm", "url": "/tags/llm/"},
            {"name": "Raw Repo Topic", "url": "/tags/raw-repo-topic/"},
        ]
        assert frontmatter["topic_links"] == [
            {
                "name": "Open-Source LLMs",
                "slug": "open-source-llms",
                "url": "/topics/open-source-llms/",
            }
        ]
        assert "/topics/raw-repo-topic/" not in page

        tags_registry = json.loads((root / "data" / "taxonomy" / "tags.json").read_text())
        raw_topic = tags_registry["terms"]["raw-repo-topic"]
        assert raw_topic["display_name"] == "Raw Repo Topic"
        assert raw_topic["count"] == 4
        assert raw_topic["times_used"] == 4
        assert raw_topic["weekly_issue_count"] == 4
        assert raw_topic["first_seen"] == "2026-05-18"
        assert raw_topic["last_used"] == "2026-06-08"


def test_repo_generation_is_deterministic_and_sorts_related_repos() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(
                root,
                week,
                [
                    repo_record("Alpha/Foo", 100 + index, topics=["shared", "llm"]),
                    repo_record("Gamma/Baz", 90 + index, topics=["shared", "agent"]),
                    repo_record("Beta/Bar", 80 + index, topics=["shared", "agent"]),
                ],
            )

        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            "[repo_pages]\nenabled = true\n", encoding="utf-8"
        )

        observatory_repos.generate(root)
        first = {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted((root / "content" / "repo").glob("**/*.md"))
        }
        first["data/taxonomy/tags.json"] = (root / "data" / "taxonomy" / "tags.json").read_bytes()
        observatory_repos.generate(root)
        second = {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted((root / "content" / "repo").glob("**/*.md"))
        }
        second["data/taxonomy/tags.json"] = (root / "data" / "taxonomy" / "tags.json").read_bytes()

        assert first == second
        frontmatter = read_frontmatter(root / "content" / "repo" / "alpha-foo" / "index.md")
        assert frontmatter["date"] == "2026-06-08"
        assert [item["full_name"] for item in frontmatter["related_repos"]] == [
            "Beta/Bar",
            "Gamma/Baz",
        ]


def test_lifecycle_rename_archive_and_delete_handling() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        weeks = ("2026-W21", "2026-W22", "2026-W23", "2026-W24")
        for index, week in enumerate(weeks):
            repos = [
                repo_record("old-owner/old-name", 10 + index),
                repo_record("octo/archived", 30 + index),
                repo_record("octo/deleted", 40 + index),
            ]
            if week == "2026-W24":
                repos.append(repo_record("new-owner/new-name", 20 + index))
            write_week(
                root,
                week,
                repos,
            )
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            """
[repo_pages]
enabled = true
recurrence_threshold_distinct_weekly_issues = 3
recurrence_threshold_operator = ">"
retention_years = 3

[repo_pages.lifecycle."old-owner/old-name"]
status = "renamed"
renamed_to = "new-owner/new-name"

[repo_pages.lifecycle."octo/archived"]
status = "archived"

[repo_pages.lifecycle."octo/deleted"]
status = "deleted"
""".strip(),
            encoding="utf-8",
        )

        observatory_repos.generate(root)

        assert not (root / "content" / "repo" / "old-owner-old-name" / "index.md").exists()
        renamed = read_frontmatter(root / "content" / "repo" / "new-owner-new-name" / "index.md")
        assert renamed["aliases"] == ["/repo/old-owner-old-name/"]
        assert renamed["distinct_weekly_issues"] == 4
        assert renamed["lifecycle"]["renamed_from"] == "old-owner/old-name"
        archived = read_frontmatter(root / "content" / "repo" / "octo-archived" / "index.md")
        assert archived["lifecycle"]["status"] == "archived"
        deleted_path = root / "content" / "repo" / "octo-deleted" / "index.md"
        deleted = read_frontmatter(deleted_path)
        assert deleted["lifecycle"]["status"] == "deleted"
        assert deleted["lifecycle"]["retention_years"] == 3
        assert deleted["lifecycle"]["retained_until"] >= "2029-06-08"
        assert "last seen week 2026-W24" in deleted_path.read_text(encoding="utf-8")


def test_stable_id_rename_creates_alias_and_positive_archive_evidence() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(
                root,
                week,
                [repo_record("old-owner/repo", 10 + index, github_id=123)],
            )
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            "[repo_pages]\nenabled = true\n", encoding="utf-8"
        )

        observatory_repos.generate(root)
        old_page = root / "content/repo/old-owner-repo/index.md"
        assert old_page.exists()

        write_week(
            root,
            "2026-W25",
            [repo_record("new-owner/repo", 14, github_id=123, archived=True)],
        )
        observatory_repos.generate(root)

        page = read_frontmatter(root / "content/repo/new-owner-repo/index.md")
        assert not old_page.exists()
        assert page["aliases"] == ["/repo/old-owner-repo/"]
        assert page["lifecycle"]["status"] == "archived"
        assert page["lifecycle"]["status_evidence"] == "github_archived_field"
        ledger = json.loads(
            (root / "data/derived/observatory/repository-lifecycle.json").read_text()
        )
        assert ledger["schema_version"] == 1
        assert ledger["repositories"]["123"]["current_full_name"] == "new-owner/repo"
        assert ledger["repositories"]["123"]["prior_full_names"] == ["old-owner/repo"]


def test_absence_preserves_qualified_page_and_does_not_imply_deletion() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(root, week, [repo_record("octo/durable", 20 + index, github_id=456)])
        config_dir = root / "config"
        config_dir.mkdir()
        config_path = config_dir / "observatory.toml"
        config_path.write_text("[repo_pages]\nenabled = true\n", encoding="utf-8")
        observatory_repos.generate(root)
        page_path = root / "content/repo/octo-durable/index.md"

        shutil.rmtree(root / "data/raw")
        config_path.write_text(
            "[repo_pages]\nenabled = true\nrecurrence_threshold_distinct_weekly_issues = 10\n",
            encoding="utf-8",
        )
        observatory_repos.generate(root)

        assert page_path.exists()
        page = read_frontmatter(page_path)
        assert page["lifecycle"]["status"] == "active"
        ledger = json.loads(
            (root / "data/derived/observatory/repository-lifecycle.json").read_text()
        )
        assert ledger["repositories"]["456"]["qualified"] is True
        assert ledger["repositories"]["456"]["lifecycle"]["status"] == "active"


def test_confirmed_deletion_is_retained_then_removed_only_after_expiry(
    capsys: pytest.CaptureFixture[str],
) -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(root, week, [repo_record("octo/deleted", 30 + index, github_id=789)])
        config_dir = root / "config"
        config_dir.mkdir()
        config_path = config_dir / "observatory.toml"
        config_path.write_text(
            """
[repo_pages]
enabled = true
retention_years = 3

[repo_pages.lifecycle."octo/deleted"]
status = "deleted"
deletion_confirmed_at = "2026-07-01"
""".strip(),
            encoding="utf-8",
        )

        observatory_repos.generate(root, as_of=observatory_repos.date(2029, 7, 1))
        page_path = root / "content/repo/octo-deleted/index.md"
        assert page_path.exists()
        assert read_frontmatter(page_path)["lifecycle"]["retained_until"] == "2029-07-01"

        shutil.rmtree(root / "data/raw")
        config_path.write_text("[repo_pages]\nenabled = true\n", encoding="utf-8")
        observatory_repos.generate(root, as_of=observatory_repos.date(2029, 7, 2))

        assert not page_path.exists()
        ledger = json.loads(
            (root / "data/derived/observatory/repository-lifecycle.json").read_text()
        )
        assert "789" not in ledger["repositories"]
        assert "Removed expired repository tombstone octo/deleted" in capsys.readouterr().out


def test_check_mode_is_non_mutating_and_reports_stale_outputs() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(root, week, [repo_record("octo/check", 40 + index, github_id=999)])
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            "[repo_pages]\nenabled = true\n", encoding="utf-8"
        )
        observatory_repos.generate(root)
        tracked = [
            root / "content/repo/octo-check/index.md",
            root / "data/derived/observatory/repositories.json",
            root / "data/derived/observatory/repository-lifecycle.json",
        ]
        before = {path: path.read_bytes() for path in tracked}

        assert observatory_repos.generate(root, check=True) == []
        assert {path: path.read_bytes() for path in tracked} == before
        tracked[0].write_text("stale\n", encoding="utf-8")
        stale_before = tracked[0].read_bytes()

        assert tracked[0] in observatory_repos.generate(root, check=True)
        assert tracked[0].read_bytes() == stale_before


def test_disabled_repo_generation_preserves_durable_state(
    capsys: pytest.CaptureFixture[str],
) -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2026-W21", [repo_record("octo/new", 100)])
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            "[repo_pages]\nenabled = false\n", encoding="utf-8"
        )
        durable_page = root / "content" / "repo" / "octo-durable" / "index.md"
        durable_page.parent.mkdir(parents=True)
        durable_page.write_text(
            f"---\ngenerated_by: {observatory_repos.GENERATED_BY}\n---\n",
            encoding="utf-8",
        )
        page_before = durable_page.read_bytes()

        written = observatory_repos.generate(root)

        assert written == []
        assert durable_page.read_bytes() == page_before
        assert not (root / "content" / "repo" / "octo-new").exists()
        assert not (root / "data" / "derived" / "observatory" / "repositories.json").exists()
        assert (
            "repository-page-decision disabled; "
            "no repository pages created or durable pages deleted" in capsys.readouterr().out
        )


@pytest.mark.skipif(shutil.which("hugo") is None, reason="hugo binary is not installed")
def test_hugo_build_renders_generated_repo_pages() -> None:
    result = subprocess.run(
        ["hugo", "--minify"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert (REPO_ROOT / "public" / "repo" / "anthropics-claude-code" / "index.html").exists()
