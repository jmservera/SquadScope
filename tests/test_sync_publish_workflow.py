from pathlib import Path


WORKFLOW = Path(".github/workflows/sync-publish-to-main.yml")


def test_publish_sync_only_checks_out_generated_content_paths() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    for path in (
        "data/raw/",
        "data/analyzed/",
        "data/metrics/",
        "content/weekly/",
        "content/monthly/",
        "content/yearly/",
    ):
        assert path in workflow

    assert "git checkout origin/publish -- .squad" not in workflow
    assert "git ls-tree -r --name-only origin/publish -- .squad" not in workflow
    assert "squad learnings" not in workflow.lower()
    assert "python3 scripts/generate_rollups.py" in workflow


def test_publish_sync_refuses_staged_squad_changes() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "Refusing to sync .squad state from publish to main" in workflow
    assert "git diff --cached --name-only | grep -E '^\\.squad/'" in workflow
    assert "data/raw/" in workflow
    assert ".squad/**" in workflow
