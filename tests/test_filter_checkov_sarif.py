import json
import subprocess
import sys
from pathlib import Path

from scripts.filter_checkov_sarif import filter_in_source_suppressions


def _result(rule_id: str, *, suppressed: bool = False) -> dict:
    result = {
        "ruleId": rule_id,
        "level": "warning",
        "message": {"text": "finding"},
    }
    if suppressed:
        result["suppressions"] = [{"kind": "inSource", "justification": "accepted inline skip"}]
    return result


def test_filter_removes_only_in_source_suppressed_results() -> None:
    sarif = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Checkov"}},
                "results": [
                    _result("CKV_GHA_7", suppressed=True),
                    _result("CKV_GHA_7"),
                    _result("CKV_GHA_3"),
                    {"ruleId": "CKV_GHA_4", "suppressions": [{"kind": "external"}]},
                ],
            }
        ],
    }

    removed = filter_in_source_suppressions(sarif)

    assert removed == 1
    assert [result["ruleId"] for result in sarif["runs"][0]["results"]] == [
        "CKV_GHA_7",
        "CKV_GHA_3",
        "CKV_GHA_4",
    ]


def test_cli_updates_sarif_in_place(tmp_path: Path) -> None:
    path = tmp_path / "checkov-results.sarif"
    path.write_text(
        json.dumps(
            {
                "version": "2.1.0",
                "runs": [{"results": [_result("CKV_GHA_7", suppressed=True)]}],
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "scripts/filter_checkov_sarif.py", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Removed 1" in completed.stdout
    assert json.loads(path.read_text(encoding="utf-8"))["runs"][0]["results"] == []
