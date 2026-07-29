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


def repo_record(full_name: str, stars: int, topics: list[str] | None = None) -> dict[str, object]:
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
