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
deletion_confirmed_at = "2026-06-15"
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
        assert deleted["lifecycle"]["retained_until"] == "2029-06-15"
        assert "last seen week 2026-W24" in deleted_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("lifecycle_fields", "error_match"),
    [
        ("", "requires deletion_confirmed_at"),
        ('deletion_confirmed_at = "not-a-date"', "invalid deletion_confirmed_at"),
        ('deletion_confirmed_at = "2026-07-02"', "future deletion_confirmed_at"),
        (
            'deletion_confirmed_at = "2026-07-01"\nretained_until = "2029-06-30"',
            "shortens configured retention",
        ),
    ],
)
def test_deleted_override_fails_closed_without_valid_retention(
    lifecycle_fields: str, error_match: str
) -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2024-W01", [repo_record("octo/deleted", 30, github_id=789)])
        config_dir = root / "config"
        config_dir.mkdir()
        config_path = config_dir / "observatory.toml"
        config_path.write_text(
            f"""
[repo_pages]
enabled = true
retention_years = 3

[repo_pages.lifecycle."octo/deleted"]
status = "deleted"
{lifecycle_fields}
""".strip(),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match=error_match):
            observatory_repos.generate(root, as_of=observatory_repos.date(2026, 7, 1))

        assert not (root / "content").exists()
        assert not (root / "data/derived").exists()
        assert not (root / "data/taxonomy").exists()


def test_deletion_retention_uses_confirmation_not_old_last_seen() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2024-W01", [repo_record("octo/deleted", 30, github_id=789)])
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            """
[repo_pages]
enabled = true
retention_years = 3

[repo_pages.lifecycle."octo/deleted"]
status = "deleted"
deletion_confirmed_at = "2026-07-01"
retained_until = "2030-01-01"
""".strip(),
            encoding="utf-8",
        )

        observatory_repos.generate(root, as_of=observatory_repos.date(2026, 7, 1))

        ledger = json.loads(
            (root / "data/derived/observatory/repository-lifecycle.json").read_text()
        )
        assert ledger["repositories"]["789"]["lifecycle"]["retained_until"] == "2029-07-01"


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


def test_seed_lifecycle_writes_only_ledger_and_is_byte_stable() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(
                root,
                week,
                [
                    repo_record("octo/qualified", 30 + index),
                    repo_record("octo/unqualified", 10 + index) if index == 0 else {},
                ],
            )
        config_dir = root / "config"
        config_dir.mkdir()
        config_path = config_dir / "observatory.toml"
        config_path.write_text("[repo_pages]\nenabled = true\n", encoding="utf-8")
        observatory_repos.generate(root)
        ledger_path = root / "data/derived/observatory/repository-lifecycle.json"
        ledger_path.unlink()
        config_path.write_text("[repo_pages]\nenabled = false\n", encoding="utf-8")
        page_path = root / "content/repo/octo-qualified/index.md"
        derived_path = root / "data/derived/observatory/repositories.json"
        unchanged_before = {path: path.read_bytes() for path in (page_path, derived_path)}

        counts = observatory_repos.seed_lifecycle(root)
        first_ledger = ledger_path.read_bytes()
        observatory_repos.seed_lifecycle(root)

        assert counts == {
            "fallback_histories": 2,
            "stable_id_histories": 0,
            "qualified_histories": 1,
            "existing_pages": 1,
            "mismatches": 0,
        }
        assert ledger_path.read_bytes() == first_ledger
        assert {path: path.read_bytes() for path in (page_path, derived_path)} == unchanged_before


def test_seed_lifecycle_rejects_page_parity_mismatch_without_writing() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(root, week, [repo_record("octo/qualified", 30 + index)])
        config_dir = root / "config"
        config_dir.mkdir()
        config_path = config_dir / "observatory.toml"
        config_path.write_text("[repo_pages]\nenabled = true\n", encoding="utf-8")
        observatory_repos.generate(root)
        ledger_path = root / "data/derived/observatory/repository-lifecycle.json"
        original_ledger = ledger_path.read_bytes()
        (root / "content/repo/octo-qualified/index.md").unlink()
        config_path.write_text("[repo_pages]\nenabled = false\n", encoding="utf-8")

        with pytest.raises(ValueError, match="Lifecycle seed parity mismatch"):
            observatory_repos.seed_lifecycle(root)

        assert ledger_path.read_bytes() == original_ledger


def test_frozen_corpus_lifecycle_seed_has_expected_parity() -> None:
    config = observatory_repos.load_config(REPO_ROOT)
    ledger_path = config["ledger_path"]
    ledger = observatory_repos.load_lifecycle_ledger(ledger_path)
    histories = observatory_repos.load_repository_histories(REPO_ROOT, config["lifecycle"], ledger)
    qualified_identities = {
        (history.display_name, history.slug) for history in histories.values() if history.qualified
    }
    page_identities, derived_identities = observatory_repos.existing_repository_identities(
        REPO_ROOT
    )
    assert config["enabled"] is False
    # Derived history retains every qualified repository, while BR-003 limits the
    # published profile surface to sponsor-approved canonical keeps.
    # After the identity backfill + rename-consolidation regeneration: 270 - 7 stale
    # + 3 consolidated-elsewhere = 266 qualified identities (some renames/ownership
    # transfers merged into an already-existing identity rather than needing a new one).
    assert len(qualified_identities) == 266
    assert qualified_identities == derived_identities
    approved = json.loads(
        (REPO_ROOT / "data/migrations/repository-approved-dispositions.json").read_text(
            encoding="utf-8"
        )
    )
    retained_slugs = {
        record["url"].removeprefix("/repo/").removesuffix("/")
        for record in approved["records"]
        if record["url_type"] == "canonical" and record["disposition"] == "keep"
    }
    retained_identities = {
        (history.display_name, history.slug)
        for history in histories.values()
        if history.slug in retained_slugs
    }
    assert page_identities == retained_identities

    # After Phase 1 fix (reverse index for full_name->key migration), the ledger
    # is idempotent across multiple passes. The loaded corpus includes the
    # committed ledger plus any migrations to numeric keys and any new repositories
    # discovered in raw weeks. Re-running load_repository_histories() without
    # identity_backfill still reconciles to the same qualified/page/derived parity,
    # even though it recreates transient fallback entries for prior names still
    # present in raw crawl data.
    assert all(isinstance(key, str) and key for key in histories)
    expected_schema = observatory_repos.lifecycle_ledger_payload({})["schema_version"]
    committed_ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert committed_ledger["schema_version"] == expected_schema
    committed_repositories = committed_ledger["repositories"]
    assert isinstance(committed_repositories, dict)
    # The persisted ledger reflects the identity-backfill-consolidated corpus (fewer
    # entries than the freshly-recomputed histories above, since the committed ledger
    # has already merged the renamed/consolidated identities into single entries).
    assert len(committed_repositories) == 2400
    assert set(committed_repositories).issubset(histories)
    assert all(isinstance(entry, dict) for entry in committed_repositories.values())


def test_stable_id_absorbs_seeded_fallback_history() -> None:
    observation = observatory_repos.RepoObservation(
        week="2026-W25",
        source_bucket="trending_repos",
        owner="new-owner",
        name="repo",
        full_name="new-owner/repo",
        url="https://github.com/new-owner/repo",
        description="renamed",
        language="Python",
        stars=20,
        forks=1,
        created_at="2026-01-01T00:00:00Z",
        topics=("ai-agents",),
        source_path="data/raw/2026-W25.json",
        github_id="123",
    )
    history = observatory_repos.RepositoryHistory(
        key="name:new-owner/repo",
        github_id=None,
        node_id=None,
        display_name="new-owner/repo",
        owner="new-owner",
        name="repo",
        slug="new-owner-repo",
        url="https://github.com/new-owner/repo",
        observations=[observation],
        lifecycle={"status": "active", "note": "seeded"},
        prior_full_names={"old-owner/repo"},
        prior_slugs={"old-owner-repo"},
        qualified=True,
    )
    ledger = observatory_repos.lifecycle_ledger_payload({history.key: history})
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2026-W26", [repo_record("new-owner/repo", 21, github_id=123)])

        histories = observatory_repos.load_repository_histories(root, ledger=ledger)

        migrated = histories["123"]
        assert "name:new-owner/repo" not in histories
        assert migrated.qualified is True
        assert migrated.lifecycle == {"status": "active", "note": "seeded"}
        assert migrated.prior_full_names == {"old-owner/repo"}
        assert migrated.prior_slugs == {"old-owner-repo"}
        assert migrated.node_id == "R_123"
        assert {item.week for item in migrated.observations} == {"2026-W25", "2026-W26"}


def test_consolidates_ledger_preloaded_duplicate_after_rename_settles_display_name() -> None:
    """Reproduces the pewdiepie-archdaemon/odysseus -> odysseus-dev/odysseus corpus bug.

    A "name:"-keyed ledger entry recorded before a repository's github_id was known can
    coexist with a stable-ID ledger entry for the same repository under an earlier name.
    The stable-ID history's display_name only settles to match the fallback entry's name
    once a later raw-week observation updates it, so the two must still be reconciled
    after that happens rather than only during raw-week reverse-index migration.
    """
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2026-W40", [repo_record("new-owner/repo", 10, github_id=555)])

        stable = observatory_repos.RepositoryHistory(
            key="555",
            github_id="555",
            node_id="R_555",
            display_name="old-owner/repo",
            owner="old-owner",
            name="repo",
            slug="old-owner-repo",
            url="https://github.com/old-owner/repo",
            observations=[
                observatory_repos.RepoObservation(
                    week="2026-W38",
                    source_bucket="trending_repos",
                    owner="old-owner",
                    name="repo",
                    full_name="old-owner/repo",
                    url="https://github.com/old-owner/repo",
                    description=None,
                    language=None,
                    stars=5,
                    forks=0,
                    created_at="2026-01-01T00:00:00Z",
                    topics=(),
                    source_path="data/raw/2026-W38.json",
                    github_id="555",
                )
            ],
        )
        fallback = observatory_repos.RepositoryHistory(
            key="name:new-owner/repo",
            github_id=None,
            node_id=None,
            display_name="new-owner/repo",
            owner="new-owner",
            name="repo",
            slug="new-owner-repo",
            url="https://github.com/new-owner/repo",
            observations=[
                observatory_repos.RepoObservation(
                    week="2026-W39",
                    source_bucket="trending_repos",
                    owner="new-owner",
                    name="repo",
                    full_name="new-owner/repo",
                    url="https://github.com/new-owner/repo",
                    description=None,
                    language=None,
                    stars=6,
                    forks=0,
                    created_at="2026-01-01T00:00:00Z",
                    topics=(),
                    source_path="data/raw/2026-W39.json",
                    github_id=None,
                )
            ],
        )
        ledger = observatory_repos.lifecycle_ledger_payload(
            {stable.key: stable, fallback.key: fallback}
        )

        histories = observatory_repos.load_repository_histories(root, ledger=ledger)

        assert set(histories) == {"555"}
        merged = histories["555"]
        assert merged.display_name == "new-owner/repo"
        assert merged.prior_full_names == {"old-owner/repo"}
        assert {item.week for item in merged.observations} == {"2026-W38", "2026-W39", "2026-W40"}


def test_consolidation_never_leaves_final_identity_in_its_own_prior_names() -> None:
    """Reproduces a self-collision: the merged final display_name/slug must never also
    appear in prior_full_names/prior_slugs, or write_repository_pages() would delete the
    page it just wrote (its current slug is also treated as an obsolete prior one).
    """
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2026-W50", [repo_record("unrelated/other", 1, github_id=999)])

        stable = observatory_repos.RepositoryHistory(
            key="777",
            github_id="777",
            node_id="R_777",
            display_name="new-owner/repo",
            owner="new-owner",
            name="repo",
            slug="new-owner-repo",
            url="https://github.com/new-owner/repo",
            observations=[
                observatory_repos.RepoObservation(
                    week="2026-W38",
                    source_bucket="trending_repos",
                    owner="new-owner",
                    name="repo",
                    full_name="new-owner/repo",
                    url="https://github.com/new-owner/repo",
                    description=None,
                    language=None,
                    stars=5,
                    forks=0,
                    created_at="2026-01-01T00:00:00Z",
                    topics=(),
                    source_path="data/raw/2026-W38.json",
                    github_id="777",
                )
            ],
        )
        # This fallback's own prior_full_names/prior_slugs already list the exact
        # name/slug the merge settles on, simulating stale prior-identity data
        # recorded before the fallback entry was last updated.
        fallback = observatory_repos.RepositoryHistory(
            key="name:new-owner/repo",
            github_id=None,
            node_id=None,
            display_name="new-owner/repo",
            owner="new-owner",
            name="repo",
            slug="new-owner-repo",
            url="https://github.com/new-owner/repo",
            prior_full_names={"new-owner/repo"},
            prior_slugs={"new-owner-repo"},
            observations=[
                observatory_repos.RepoObservation(
                    week="2026-W39",
                    source_bucket="trending_repos",
                    owner="new-owner",
                    name="repo",
                    full_name="new-owner/repo",
                    url="https://github.com/new-owner/repo",
                    description=None,
                    language=None,
                    stars=6,
                    forks=0,
                    created_at="2026-01-01T00:00:00Z",
                    topics=(),
                    source_path="data/raw/2026-W39.json",
                    github_id=None,
                )
            ],
        )
        ledger = observatory_repos.lifecycle_ledger_payload(
            {stable.key: stable, fallback.key: fallback}
        )

        histories = observatory_repos.load_repository_histories(root, ledger=ledger)

        merged = histories["777"]
        assert merged.display_name == "new-owner/repo"
        assert merged.slug not in merged.prior_slugs
        assert merged.display_name not in merged.prior_full_names


def test_two_pass_duplicate_identity_regression() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        write_week(root, "2026-W30", [repo_record("test-owner/test-repo", 100, github_id=None)])
        write_week(root, "2026-W31", [repo_record("test-owner/test-repo", 101, github_id=456)])

        config = observatory_repos.load_config(root)
        first_histories = observatory_repos.load_repository_histories(root, config.get("lifecycle"))
        assert "name:test-owner/test-repo" not in first_histories
        assert set(first_histories) == {"456"}
        assert {item.week for item in first_histories["456"].observations} == {
            "2026-W30",
            "2026-W31",
        }
        first_ledger = observatory_repos.lifecycle_ledger_payload(first_histories)

        second_histories = observatory_repos.load_repository_histories(
            root, config.get("lifecycle"), first_ledger
        )
        matching = [
            history
            for history in second_histories.values()
            if history.display_name == "test-owner/test-repo"
        ]
        assert len(matching) == 1
        assert set(second_histories) == {"456"}
        migrated = second_histories["456"]
        assert migrated.distinct_weeks == {"2026-W30", "2026-W31"}
        assert len(migrated.observations) == 2
        assert {obs.week for obs in migrated.observations} == {"2026-W30", "2026-W31"}
        assert migrated.github_id == "456"
        assert migrated.display_name == "test-owner/test-repo"


def test_write_repository_pages_raises_on_slug_collision() -> None:
    """Unit test verifying the slug-collision guard in write_repository_pages().

    The slug-collision guard is a defensive check that ensures no two different
    repository history keys produce the same output slug/path. This should be
    unreachable after the identity-merge fix, but the guard catches any future
    regression before corrupt derived data reaches production.
    """
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)

        # Create a minimal config
        config = observatory_repos.load_config(root)

        # Construct two RepositoryHistory objects that will collide on slug
        # Both resolve to slug "owner-repo" from their display_name
        collision_slug = "owner-repo"

        # History 1: numeric key with display name "owner/repo"
        history1 = observatory_repos.RepositoryHistory(
            key="123",
            github_id="123",
            node_id="R_123",
            display_name="owner/repo",
            owner="owner",
            name="repo",
            slug=collision_slug,  # Explicitly set to collision slug
            url="https://github.com/owner/repo",
            description="First history",
        )

        # Add observations to make it eligible for page generation
        history1.observations.append(
            observatory_repos.RepoObservation(
                week="2026-W30",
                source_bucket="trending_repos",
                owner="owner",
                name="repo",
                full_name="owner/repo",
                url="https://github.com/owner/repo",
                description="First history",
                language="Python",
                stars=100,
                forks=10,
                created_at="2026-01-01T00:00:00Z",
                topics=("ai",),
                source_path="data/raw/2026-W30.json",
                github_id="123",
                node_id="R_123",
            )
        )

        # History 2: name-key variant with same slug (crafted to collide)
        history2 = observatory_repos.RepositoryHistory(
            key="name:owner/repo-variant",
            github_id=None,
            node_id=None,
            display_name="owner/repo-variant",  # Different display name
            owner="owner",
            name="repo-variant",
            slug=collision_slug,  # Same slug due to Unicode/normalization crafting
            url="https://github.com/owner/repo-variant",
            description="Second history (collision)",
        )

        # Add observations to make it eligible for page generation
        history2.observations.append(
            observatory_repos.RepoObservation(
                week="2026-W30",
                source_bucket="trending_repos",
                owner="owner",
                name="repo-variant",
                full_name="owner/repo-variant",
                url="https://github.com/owner/repo-variant",
                description="Second history",
                language="Python",
                stars=50,
                forks=5,
                created_at="2026-01-02T00:00:00Z",
                topics=("ai",),
                source_path="data/raw/2026-W30.json",
                github_id=None,
            )
        )

        # Mark both as qualified so they will be eligible
        history1.qualified = True
        history2.qualified = True

        # Create histories dict with both
        histories = {history1.key: history1, history2.key: history2}

        with pytest.raises(ValueError) as error:
            observatory_repos.write_repository_pages(root, histories, config, check=True)
        message = str(error.value)
        assert history1.key in message
        assert history2.key in message
        assert collision_slug in message


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
def test_enabled_fixture_is_idempotent_and_renders_lifecycle_contracts() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        shutil.copy2(REPO_ROOT / "hugo.toml", root / "hugo.toml")
        for directory in ("archetypes", "assets", "layouts", "static", "themes"):
            shutil.copytree(REPO_ROOT / directory, root / directory)
        for directory in ("data/raw", "data/snapshots", "data/metrics", "content"):
            (root / directory).mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / "data/cookieconsent.json", root / "data/cookieconsent.json")
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(
                root,
                week,
                [
                    repo_record(
                        "old-owner/old-name",
                        30 + index,
                        topics=["Raw Repo Topic", "llm"],
                    ),
                    repo_record("octo/deleted", 20 + index),
                ],
            )
            weekly_path = root / "content/weekly/2026" / f"{week.split('-')[1]}.md"
            weekly_path.parent.mkdir(parents=True, exist_ok=True)
            weekly_path.write_text(f"---\ntitle: {week}\n---\n", encoding="utf-8")
        (root / "content/_index.md").write_text("---\ntitle: Home\n---\n", encoding="utf-8")
        for path, title in (
            (root / "content/methodology/_index.md", "Methodology"),
            (root / "content/topics/open-source-llms/_index.md", "Open-Source LLMs"),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"---\ntitle: {title}\n---\n", encoding="utf-8")
        topics_path = root / "data/taxonomy/topics.json"
        topics_path.parent.mkdir(parents=True, exist_ok=True)
        topics_path.write_text(
            json.dumps(
                {
                    "terms": {
                        "open-source-llms": {
                            "slug": "open-source-llms",
                            "display_name": "Open-Source LLMs",
                            "promoted": True,
                            "aliases": ["llm"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            """
[repo_pages]
enabled = true
retention_years = 3

[repo_pages.lifecycle."old-owner/old-name"]
status = "renamed"
renamed_to = "new-owner/new-name"

[repo_pages.lifecycle."octo/deleted"]
status = "deleted"
deletion_confirmed_at = "2026-07-01"
""".strip(),
            encoding="utf-8",
        )

        observatory_repos.generate(root, as_of=observatory_repos.date(2026, 7, 1))
        generated_paths = sorted((root / "content/repo").glob("**/*.md")) + sorted(
            (root / "data/derived/observatory").glob("*.json")
        )
        generated_paths += [root / "data/taxonomy/tags.json"]
        first = {path.relative_to(root): path.read_bytes() for path in generated_paths}
        observatory_repos.generate(root, as_of=observatory_repos.date(2026, 7, 1))
        second = {path.relative_to(root): path.read_bytes() for path in generated_paths}

        assert second == first
        result = subprocess.run(
            ["hugo", "--minify", "--quiet"],
            cwd=root,
            check=False,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        canonical = root / "public/repo/new-owner-new-name/index.html"
        alias = root / "public/repo/old-owner-old-name/index.html"
        deleted = root / "public/repo/octo-deleted/index.html"
        canonical_html = canonical.read_text(encoding="utf-8")
        deleted_html = deleted.read_text(encoding="utf-8")
        assert canonical.exists()
        assert alias.exists()
        assert "/tags/raw-repo-topic/" in canonical_html
        assert "/topics/open-source-llms/" in canonical_html
        assert (root / "public/tags/raw-repo-topic/index.html").exists()
        assert (root / "public/topics/open-source-llms/index.html").exists()
        assert "Deleted or inaccessible repository" in deleted_html


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
    assert (REPO_ROOT / "public" / "repo" / "odysseus-dev-odysseus" / "index.html").exists()


def write_identity_backfill(root: Path, entries: dict[str, dict[str, object]]) -> Path:
    path = root / "data" / "derived" / "observatory" / "repo-identity-backfill.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": 1, "entries": entries}, indent=2),
        encoding="utf-8",
    )
    return path


def test_identity_backfill_resolves_stable_id_for_fallback_history() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(root, week, [repo_record("octo/fallback", 20 + index, github_id=None)])
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            "[repo_pages]\nenabled = true\n", encoding="utf-8"
        )
        write_identity_backfill(
            root,
            {
                "octo/fallback": {
                    "status": "found",
                    "github_id": "555",
                    "node_id": "R_555",
                    "checked_at": "2026-08-05",
                }
            },
        )

        observatory_repos.generate(root)

        page = root / "content/repo/octo-fallback/index.md"
        assert page.exists()
        ledger = json.loads(
            (root / "data/derived/observatory/repository-lifecycle.json").read_text()
        )
        assert "555" in ledger["repositories"]
        assert "name:octo/fallback" not in ledger["repositories"]


def test_identity_backfill_not_found_is_treated_as_deletion_evidence() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(root, week, [repo_record("octo/vanished", 20 + index, github_id=None)])
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            "[repo_pages]\nenabled = true\nretention_years = 3\n", encoding="utf-8"
        )
        write_identity_backfill(
            root,
            {"octo/vanished": {"status": "not_found", "checked_at": "2026-07-01"}},
        )

        observatory_repos.generate(root, as_of=observatory_repos.date(2026, 7, 2))

        page_path = root / "content/repo/octo-vanished/index.md"
        page = read_frontmatter(page_path)
        assert page["lifecycle"]["status"] == "deleted"
        assert page["lifecycle"]["status_evidence"] == "github_api_404_identity_backfill"
        assert page["lifecycle"]["retained_until"] == "2029-07-01"


def test_manual_lifecycle_override_wins_over_identity_backfill_not_found() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        root = Path(tmpdir)
        for index, week in enumerate(("2026-W21", "2026-W22", "2026-W23", "2026-W24")):
            write_week(root, week, [repo_record("octo/reviewed", 20 + index, github_id=None)])
        config_dir = root / "config"
        config_dir.mkdir()
        (config_dir / "observatory.toml").write_text(
            """
[repo_pages]
enabled = true
retention_years = 3

[repo_pages.lifecycle."octo/reviewed"]
status = "archived"
""".strip(),
            encoding="utf-8",
        )
        write_identity_backfill(
            root,
            {"octo/reviewed": {"status": "not_found", "checked_at": "2026-07-01"}},
        )

        observatory_repos.generate(root, as_of=observatory_repos.date(2026, 7, 2))

        page = read_frontmatter(root / "content/repo/octo-reviewed/index.md")
        assert page["lifecycle"]["status"] == "archived"
