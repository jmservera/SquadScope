from pathlib import Path

WORKFLOW = Path(".github/workflows/sync-publish-to-main.yml")
RESTORE_WORKFLOW = Path(".github/workflows/restore-publish-backup.yml")
CRAWL_WORKFLOW = Path(".github/workflows/crawl-and-publish.yml")


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
    assert "data/raw-store/" not in workflow


def test_publish_sync_refuses_staged_squad_changes() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "Refusing to sync .squad state from publish to main" in workflow
    assert "git diff --cached --name-only | grep -E '^\\.squad/'" in workflow
    assert "data/raw/" in workflow
    assert ".squad/**" in workflow


def test_restore_publish_backup_workflow_uses_immutable_backup_manifest() -> None:
    workflow = RESTORE_WORKFLOW.read_text(encoding="utf-8")

    assert "backup_manifest" in workflow
    assert "python3 ../workflow-source/scripts/publish_safety.py restore-backup" in workflow
    assert "--force-with-lease" in workflow
    assert "ref: publish" in workflow


def test_restore_publish_backup_workflow_keeps_helper_available_after_publish_checkout() -> None:
    workflow = RESTORE_WORKFLOW.read_text(encoding="utf-8")

    assert "path: workflow-source" in workflow
    assert "ref: ${{ github.sha }}" in workflow
    assert "path: publish" in workflow
    assert "cd publish" in workflow
    assert "python3 scripts/publish_safety.py restore-backup" not in workflow
    assert "python3 ../workflow-source/scripts/publish_safety.py restore-backup" in workflow


def test_publish_sync_stages_before_cached_diff_evaluation() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert workflow.index("git add -A") < workflow.index("if git diff --cached --quiet; then")


def test_crawl_workflow_stores_and_restores_source_bound_raw_evidence() -> None:
    workflow = CRAWL_WORKFLOW.read_text(encoding="utf-8")

    assert "source_run_id:" in workflow
    assert "run_mode=restore and source_run_id" in workflow
    assert workflow.count("python3 scripts/publish_safety.py restore-raw") == 2
    assert "python3 publish-safety-tool.py store-raw" in workflow
    assert 'RAW_STORE_DIR="data/raw-store/${REBUILD_WEEK}/${SOURCE_RUN_ID}"' in workflow
    assert (
        '--raw-store-manifest "data/raw-store/${WEEK}/${SOURCE_RUN_ID}/manifest.json"' in workflow
    )
    assert 'source-artifact-id "$RAW_ARTIFACT_ID"' in workflow
    assert "retention-days: 90" in workflow


def test_crawl_workflow_stages_raw_store_before_cached_diff_evaluation() -> None:
    workflow = CRAWL_WORKFLOW.read_text(encoding="utf-8")

    stage = workflow.index("git add data/raw/ data/snapshots/ data/raw-store/")
    cached_diff = workflow.index("if git diff --cached --quiet; then", stage)
    assert stage < cached_diff
