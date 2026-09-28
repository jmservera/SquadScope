from pathlib import Path


def test_checkov_workflow_filters_accepted_sarif_suppressions_before_upload() -> None:
    workflow = Path(".github/workflows/checkov.yml").read_text(encoding="utf-8")

    assert "\n            --soft-fail" not in workflow
    assert "continue-on-error: true" not in workflow
    assert "python scripts/filter_checkov_sarif.py checkov-results.sarif" in workflow
    assert workflow.index("Filter accepted Checkov SARIF suppressions") < workflow.index(
        "Upload SARIF to GitHub Code Scanning"
    )
    assert "sarif_file: checkov-results.sarif" in workflow
