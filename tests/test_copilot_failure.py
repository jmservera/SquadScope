from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

from scripts import copilot_failure


def test_classifies_copilot_token_failure_as_actionable_non_retryable() -> None:
    report = copilot_failure.classify_log("Authentication failed: Bad credentials", exit_code=1)

    assert report.failure_class == "copilot_token_failure"
    assert report.retryable is False
    assert report.actionable is True
    assert "renew COPILOT_GH_TOKEN" in report.diagnostic
    assert copilot_failure.classify_log("HTTP 403 from Copilot").failure_class == "copilot_inaccessible"
    assert copilot_failure.classify_log("HTTP 401 from Copilot").failure_class == "copilot_inaccessible"
    assert copilot_failure.classify_log("HTTP 403 invalid token").failure_class == "copilot_token_failure"


def test_classifies_context_timeout_and_transient_failures() -> None:
    assert copilot_failure.classify_log("maximum context length exceeded").failure_class == "context_too_large"
    assert copilot_failure.classify_log("request timed out").failure_class == "timeout"
    assert copilot_failure.classify_log("HTTP 503 temporarily unavailable").failure_class == "transient_error"


def test_main_writes_report_without_creating_issue_for_transient(tmp_path: Path) -> None:
    log_path = tmp_path / "copilot.log"
    report_path = tmp_path / "report.json"
    log_path.write_text("HTTP 429 rate limit", encoding="utf-8")

    with mock.patch.object(copilot_failure, "create_or_update_token_issue") as issue_mock:
        exit_code = copilot_failure.main(
            [
                "--log",
                str(log_path),
                "--exit-code",
                "1",
                "--report-json",
                str(report_path),
                "--create-token-issue",
                "--repo",
                "jmservera/SquadScope",
            ]
        )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["failure_class"] == "transient_error"
    assert payload["retryable"] is True
    issue_mock.assert_not_called()


def test_main_creates_or_updates_issue_for_token_failure(tmp_path: Path) -> None:
    log_path = tmp_path / "copilot.log"
    report_path = tmp_path / "report.json"
    log_path.write_text("COPILOT_GITHUB_TOKEN invalid token", encoding="utf-8")

    with mock.patch.object(
        copilot_failure,
        "create_or_update_token_issue",
        return_value="https://github.com/jmservera/SquadScope/issues/123",
    ) as issue_mock:
        exit_code = copilot_failure.main(
            [
                "--log",
                str(log_path),
                "--exit-code",
                "1",
                "--report-json",
                str(report_path),
                "--create-token-issue",
                "--repo",
                "jmservera/SquadScope",
                "--week",
                "2026-W23",
                "--run-id",
                "27055543722",
            ]
        )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["failure_class"] == "copilot_token_failure"
    assert payload["issue"] == "https://github.com/jmservera/SquadScope/issues/123"
    issue_mock.assert_called_once()


def test_main_creates_or_updates_issue_for_copilot_inaccessible(tmp_path: Path) -> None:
    log_path = tmp_path / "copilot.log"
    report_path = tmp_path / "report.json"
    log_path.write_text("copilot is not available: command not found", encoding="utf-8")

    with mock.patch.object(
        copilot_failure,
        "create_or_update_token_issue",
        return_value="https://github.com/jmservera/SquadScope/issues/123",
    ) as issue_mock:
        exit_code = copilot_failure.main(
            [
                "--log",
                str(log_path),
                "--exit-code",
                "127",
                "--report-json",
                str(report_path),
                "--create-token-issue",
                "--repo",
                "jmservera/SquadScope",
                "--week",
                "2026-W23",
                "--run-id",
                "27055543722",
            ]
        )

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["failure_class"] == "copilot_inaccessible"
    assert payload["issue"] == "https://github.com/jmservera/SquadScope/issues/123"
    issue_mock.assert_called_once()


def test_create_or_update_token_issue_returns_consistent_url_for_existing_issue() -> None:
    report = copilot_failure.classify_log("invalid token")
    responses = [
        mock.Mock(returncode=0, stdout='[{"number": 123, "title": "Renew GitHub Copilot token for weekly analysis workflow"}]', stderr=""),
        mock.Mock(returncode=0, stdout="", stderr=""),
    ]

    with mock.patch.object(copilot_failure, "run_gh", side_effect=responses):
        result = copilot_failure.create_or_update_token_issue(
            report,
            repo="jmservera/SquadScope",
            assignee="jmservera",
            week="2026-W23",
            run_id="27055543722",
        )

    assert result == "https://github.com/jmservera/SquadScope/issues/123"


def test_create_or_update_token_issue_returns_consistent_url_for_created_issue() -> None:
    report = copilot_failure.classify_log("invalid token")
    responses = [
        mock.Mock(returncode=0, stdout="[]", stderr=""),
        mock.Mock(returncode=0, stdout="https://github.com/jmservera/SquadScope/issues/124\n", stderr=""),
    ]

    with mock.patch.object(copilot_failure, "run_gh", side_effect=responses):
        result = copilot_failure.create_or_update_token_issue(
            report,
            repo="jmservera/SquadScope",
            assignee="jmservera",
            week="2026-W23",
            run_id="27055543722",
        )

    assert result == "https://github.com/jmservera/SquadScope/issues/124"
