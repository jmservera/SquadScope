import subprocess

from scripts import wait_for_required_checks as w

ACTIONS = 15368
HEAD = "a" * 40


def check_run(
    name,
    status="COMPLETED",
    conclusion="SUCCESS",
    started="2026-10-05T10:00:00Z",
    app=ACTIONS,
    database_id=1,
):
    return {
        "__typename": "CheckRun",
        "databaseId": database_id,
        "name": name,
        "status": status,
        "conclusion": conclusion,
        "startedAt": started,
        "checkSuite": {"app": {"databaseId": app}},
    }


def payload(nodes, state="OPEN", head=HEAD, commit_oid=None, has_next=False):
    return {
        "data": {
            "repository": {
                "pullRequest": {
                    "state": state,
                    "headRefOid": head,
                    "commits": {
                        "nodes": [
                            {
                                "commit": {
                                    "oid": commit_oid or head,
                                    "statusCheckRollup": {
                                        "contexts": {
                                            "pageInfo": {"hasNextPage": has_next},
                                            "nodes": nodes,
                                        }
                                    },
                                }
                            }
                        ]
                    },
                }
            }
        }
    }


REQUIRED = [w.RequiredCheck("Python", ACTIONS), w.RequiredCheck("Ruff", ACTIONS)]


def run_wait(payloads, timeout=100.0):
    remaining = list(payloads)

    def fetch():
        return remaining.pop(0) if len(remaining) > 1 else remaining[0]

    now = [0.0]
    logs = []

    def sleep(seconds):
        now[0] += seconds

    code = w.wait_for_checks(
        required=REQUIRED,
        head_sha=HEAD,
        fetch=fetch,
        timeout=timeout,
        interval=10.0,
        clock=lambda: now[0],
        sleep=sleep,
        log=logs.append,
    )
    return code, logs


def test_parse_required_checks_reads_ruleset_contexts_and_integration_ids():
    rules = [
        {"type": "pull_request", "parameters": {}},
        {
            "type": "required_status_checks",
            "parameters": {
                "required_status_checks": [
                    {"context": "Python", "integration_id": ACTIONS},
                    {"context": "Ruff"},
                    {"context": "Python", "integration_id": ACTIONS},
                ]
            },
        },
    ]
    assert w.parse_required_checks(rules) == [
        w.RequiredCheck("Python", ACTIONS),
        w.RequiredCheck("Ruff", None),
    ]


def test_waits_until_late_required_check_registers_and_completes():
    """`gh pr checks --watch` exits once visible checks finish (#826); this must not."""
    code, logs = run_wait(
        [
            payload([check_run("Ruff")]),
            payload(
                [check_run("Ruff"), check_run("Python", status="IN_PROGRESS", conclusion=None)]
            ),
            payload([check_run("Ruff"), check_run("Python")]),
        ]
    )
    assert code == 0
    assert any("Python (not registered)" in line for line in logs)
    assert any("Python (in_progress)" in line for line in logs)


def test_checks_from_another_app_do_not_satisfy_required_check():
    code, logs = run_wait([payload([check_run("Ruff"), check_run("Python", app=1)])], timeout=5)
    assert code == 1
    assert any("Timed out" in line for line in logs)


def test_failed_required_check_fails_fast():
    code, logs = run_wait([payload([check_run("Ruff"), check_run("Python", conclusion="FAILURE")])])
    assert code == 1
    assert any("Python (failure)" in line for line in logs)


def test_latest_rerun_wins_over_older_failure():
    nodes = [
        check_run("Ruff"),
        check_run("Python", conclusion="FAILURE", started="2026-10-05T10:00:00Z"),
        check_run("Python", started="2026-10-05T11:00:00Z"),
    ]
    assert run_wait([payload(nodes)])[0] == 0


def test_skipped_and_neutral_count_as_passing():
    nodes = [check_run("Ruff", conclusion="SKIPPED"), check_run("Python", conclusion="NEUTRAL")]
    assert run_wait([payload(nodes)])[0] == 0


def test_head_moved_or_closed_pr_refuses_to_merge():
    assert run_wait([payload([], head="b" * 40)])[0] == 1
    assert run_wait([payload([], state="CLOSED")])[0] == 1


def test_already_merged_pr_succeeds():
    assert run_wait([payload([], state="MERGED")])[0] == 0


def test_stale_rollup_commit_is_ignored():
    stale = payload([check_run("Ruff"), check_run("Python")], commit_oid="c" * 40)
    code, _ = run_wait([stale, payload([check_run("Ruff"), check_run("Python")])])
    assert code == 0


def test_partial_rollup_is_a_configuration_error():
    try:
        w.parse_rollup(payload([], has_next=True))
    except w.ConfigurationError:
        pass
    else:
        raise AssertionError("expected ConfigurationError")


def test_no_required_checks_fails_closed():
    code = w.wait_for_checks(
        required=[], head_sha=HEAD, fetch=dict, timeout=1, interval=1, log=lambda _: None
    )
    assert code == 2


def test_transient_api_error_is_retried():
    calls = iter(
        [
            w.GhCommandError("gh api graphql exited 1: boom"),
            payload([check_run("Ruff"), check_run("Python")]),
        ]
    )

    def fetch():
        item = next(calls)
        if isinstance(item, Exception):
            raise item
        return item

    code = w.wait_for_checks(
        required=REQUIRED,
        head_sha=HEAD,
        fetch=fetch,
        timeout=100,
        interval=1,
        clock=lambda: 0.0,
        sleep=lambda _: None,
        log=lambda _: None,
    )
    assert code == 0


def test_unexpected_rules_response_is_a_configuration_error(monkeypatch):
    monkeypatch.setattr(w, "gh_json", lambda args: {"message": "Not Found"})
    try:
        w.fetch_required_checks("o/r", "main")
    except w.ConfigurationError as exc:
        assert "Not Found" in str(exc)
    else:
        raise AssertionError("expected ConfigurationError")


def test_invalid_integration_id_is_reported():
    rules = [
        {
            "type": "required_status_checks",
            "parameters": {"required_status_checks": [{"context": "x", "integration_id": "1"}]},
        }
    ]
    try:
        w.parse_required_checks(rules)
    except w.ConfigurationError as exc:
        assert "'1'" in str(exc)
    else:
        raise AssertionError("expected ConfigurationError")


def test_gh_failures_become_gh_command_errors(monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["gh"], stderr="HTTP 403")

    monkeypatch.setattr(w.subprocess, "run", fail)
    try:
        w.gh_json(["api", "x"])
    except w.GhCommandError as exc:
        assert "HTTP 403" in str(exc)
    else:
        raise AssertionError("expected GhCommandError")

    monkeypatch.setattr(
        w.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="not json", stderr=""),
    )
    try:
        w.gh_json(["api", "x"])
    except w.GhCommandError as exc:
        assert "non-JSON" in str(exc)
    else:
        raise AssertionError("expected GhCommandError")


def test_main_returns_2_when_rules_cannot_be_read(monkeypatch):
    def boom(repo, branch):
        raise w.GhCommandError("gh api repos/o/r/rules/branches/main exited 1: HTTP 404")

    monkeypatch.setattr(w, "fetch_required_checks", boom)
    assert w.main(["--repo", "o/r", "--pr", "1", "--head-sha", HEAD]) == 2


def test_same_start_time_prefers_higher_database_id():
    nodes = [
        check_run("Ruff"),
        check_run("Python", conclusion="FAILURE", database_id=5),
        check_run("Python", database_id=9),
    ]
    assert run_wait([payload(nodes)])[0] == 0
    nodes = [
        check_run("Ruff"),
        check_run("Python", database_id=5),
        check_run("Python", conclusion="FAILURE", database_id=9),
    ]
    assert run_wait([payload(nodes)])[0] == 1


def test_queued_rerun_without_start_time_is_pending_not_hidden():
    old_failure = check_run("Python", conclusion="FAILURE", database_id=5)
    queued = check_run("Python", status="QUEUED", conclusion=None, started=None, database_id=9)
    code, logs = run_wait(
        [
            payload([check_run("Ruff"), old_failure, queued]),
            payload([check_run("Ruff"), old_failure, check_run("Python", database_id=9)]),
        ]
    )
    assert code == 0
    assert any("Python (queued)" in line for line in logs)


def test_malformed_pull_request_payload_is_a_configuration_error():
    bad = {"data": {"repository": {"pullRequest": {"state": "OPEN"}}}}
    try:
        w.parse_rollup(bad)
    except w.ConfigurationError as exc:
        assert "KeyError" in str(exc)
    else:
        raise AssertionError("expected ConfigurationError")
