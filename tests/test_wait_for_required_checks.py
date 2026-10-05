import subprocess

from scripts import wait_for_required_checks as w

ACTIONS = 15368
HEAD = "a" * 40


def check_run(
    name, status="COMPLETED", conclusion="SUCCESS", started="2026-10-05T10:00:00Z", app=ACTIONS
):
    return {
        "__typename": "CheckRun",
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
            subprocess.CalledProcessError(1, ["gh"]),
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
