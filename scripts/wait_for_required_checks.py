"""Wait until a pull request's ruleset-required checks have all completed.

The publish-sync workflow uses this instead of ``gh pr checks --watch``. That
command exits as soon as the checks it can currently see have finished, so it
can return before slower required checks have even registered
(jmservera/SquadScope#826).

The required check names and app ids come from the branch rules API, so they
always match what the ruleset enforces. Each required check is resolved from
the pull request's ``statusCheckRollup``, which is the same view the merge box
uses. Check runs that are not associated with the pull request, such as those
from ``workflow_dispatch`` suites, are not part of that rollup and never count.

Exit codes: 0 when every required check passed (or the PR is already merged),
1 when a required check failed, the head moved, the PR closed, or the wait
timed out, and 2 for usage or configuration errors.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # nosec B404
import sys
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass

PASSING_CONCLUSIONS = frozenset({"SUCCESS", "NEUTRAL", "SKIPPED"})

ROLLUP_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      state
      headRefOid
      commits(last: 1) {
        nodes {
          commit {
            oid
            statusCheckRollup {
              contexts(first: 100) {
                pageInfo { hasNextPage }
                nodes {
                  __typename
                  ... on CheckRun {
                    name
                    status
                    conclusion
                    databaseId
                    startedAt
                    checkSuite { app { databaseId } }
                  }
                  ... on StatusContext {
                    context
                    state
                    createdAt
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


class ConfigurationError(Exception):
    """The inputs or GitHub responses cannot be evaluated safely."""


class GhCommandError(Exception):
    """A ``gh`` invocation failed, timed out, or returned non-JSON output."""


@dataclass(frozen=True)
class RequiredCheck:
    context: str
    integration_id: int | None


@dataclass(frozen=True)
class CheckResult:
    name: str
    app_id: int | None
    completed: bool
    passed: bool
    order_key: tuple[str, int]
    detail: str


@dataclass(frozen=True)
class Evaluation:
    state: str  # "passed", "failed", or "pending"
    passed: tuple[str, ...]
    failed: tuple[str, ...]
    pending: tuple[str, ...]


def parse_required_checks(rules: Iterable[dict]) -> list[RequiredCheck]:
    """Return the unique required status checks from branch rules."""
    found: dict[tuple[str, int | None], RequiredCheck] = {}
    for rule in rules:
        if rule.get("type") != "required_status_checks":
            continue
        for entry in (rule.get("parameters") or {}).get("required_status_checks") or []:
            context = entry.get("context")
            if not isinstance(context, str) or not context:
                raise ConfigurationError(f"required status check without a context: {entry!r}")
            integration_id = entry.get("integration_id")
            if integration_id is not None and not isinstance(integration_id, int):
                raise ConfigurationError(
                    f"invalid integration_id {integration_id!r} for {context!r}: {entry!r}"
                )
            check = RequiredCheck(context, integration_id)
            found[(check.context, check.integration_id)] = check
    return sorted(found.values(), key=lambda c: (c.context, c.integration_id or 0))


# A check run that has not started yet (a queued re-run) sorts after every
# started run, so a pending re-run is never hidden behind an older result.
NOT_STARTED = "\uffff"


def parse_rollup(payload: dict) -> tuple[str, str, list[CheckResult]]:
    """Return ``(pr_state, head_sha, contexts)`` from the GraphQL payload."""
    try:
        return _parse_rollup(payload)
    except (KeyError, TypeError, AttributeError) as exc:
        raise ConfigurationError(
            f"unexpected GraphQL response ({type(exc).__name__}: {exc}): {str(payload)[:300]}"
        ) from exc


def _parse_rollup(payload: dict) -> tuple[str, str, list[CheckResult]]:
    pull_request = payload["data"]["repository"]["pullRequest"]
    if pull_request is None:
        raise ConfigurationError("pull request not found")

    state = pull_request["state"]
    head_sha = pull_request["headRefOid"]
    commits = pull_request["commits"]["nodes"]
    if not commits:
        return state, head_sha, []
    commit = commits[0]["commit"]
    if commit["oid"] != head_sha:
        # The rollup belongs to a different commit than the PR head; treat as
        # not yet registered rather than trusting stale results.
        return state, head_sha, []
    rollup = commit.get("statusCheckRollup")
    if not rollup:
        return state, head_sha, []
    contexts = rollup["contexts"]
    if contexts["pageInfo"]["hasNextPage"]:
        raise ConfigurationError(
            "more than 100 status contexts; refusing to evaluate a partial set"
        )

    results: list[CheckResult] = []
    for node in contexts["nodes"]:
        if node.get("__typename") == "CheckRun":
            app = (node.get("checkSuite") or {}).get("app") or {}
            completed = node.get("status") == "COMPLETED"
            conclusion = node.get("conclusion") or ""
            results.append(
                CheckResult(
                    name=node["name"],
                    app_id=app.get("databaseId"),
                    completed=completed,
                    passed=completed and conclusion in PASSING_CONCLUSIONS,
                    order_key=(node.get("startedAt") or NOT_STARTED, node.get("databaseId") or 0),
                    detail=(conclusion or node.get("status") or "UNKNOWN").lower(),
                )
            )
        elif node.get("__typename") == "StatusContext":
            status_state = node.get("state") or ""
            results.append(
                CheckResult(
                    name=node["context"],
                    app_id=None,
                    completed=status_state not in {"PENDING", "EXPECTED"},
                    passed=status_state == "SUCCESS",
                    order_key=(node.get("createdAt") or NOT_STARTED, 0),
                    detail=status_state.lower(),
                )
            )
    return state, head_sha, results


def evaluate(required: list[RequiredCheck], contexts: list[CheckResult]) -> Evaluation:
    """Classify each required check using its most recent matching context."""
    passed: list[str] = []
    failed: list[str] = []
    pending: list[str] = []
    for check in required:
        matches = [
            ctx
            for ctx in contexts
            if ctx.name == check.context
            and (check.integration_id is None or ctx.app_id == check.integration_id)
        ]
        if not matches:
            pending.append(f"{check.context} (not registered)")
            continue
        latest = max(matches, key=lambda ctx: ctx.order_key)
        if not latest.completed:
            pending.append(f"{check.context} ({latest.detail})")
        elif latest.passed:
            passed.append(check.context)
        else:
            failed.append(f"{check.context} ({latest.detail})")

    if failed:
        state = "failed"
    elif pending:
        state = "pending"
    else:
        state = "passed"
    return Evaluation(state, tuple(passed), tuple(failed), tuple(pending))


def gh_json(args: list[str]) -> object:
    command = " ".join(args[:2])
    try:
        completed = subprocess.run(  # nosec B603 B607 - fixed gh argv, no shell, gh is a controlled tool
            ["gh", *args], check=True, capture_output=True, text=True, timeout=120
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()[:300]
        raise GhCommandError(f"gh {command} exited {exc.returncode}: {stderr}") from exc
    except subprocess.TimeoutExpired as exc:
        raise GhCommandError(f"gh {command} timed out") from exc
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise GhCommandError(
            f"gh {command} returned non-JSON output: {completed.stdout[:300]!r}"
        ) from exc


def fetch_required_checks(repo: str, branch: str) -> list[RequiredCheck]:
    rules = gh_json(["api", f"repos/{repo}/rules/branches/{branch}", "--paginate", "--slurp"])
    if not isinstance(rules, list) or not all(isinstance(page, list) for page in rules):
        raise ConfigurationError(
            f"unexpected branch rules response for {repo}@{branch}: {type(rules).__name__} "
            f"{str(rules)[:300]}"
        )
    return parse_required_checks([rule for page in rules for rule in page])


def fetch_rollup(repo: str, number: int) -> dict:
    owner, name = repo.split("/", 1)
    payload = gh_json(
        [
            "api",
            "graphql",
            "-f",
            f"query={ROLLUP_QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={number}",
        ]
    )
    if not isinstance(payload, dict):
        raise ConfigurationError("unexpected GraphQL response type")
    return payload


def wait_for_checks(
    *,
    required: list[RequiredCheck],
    head_sha: str,
    fetch: Callable[[], dict],
    timeout: float,
    interval: float,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    log: Callable[[str], None] = print,
) -> int:
    if not required:
        log("::error::No required status checks found for the base branch; refusing to merge.")
        return 2

    deadline = clock() + timeout
    last_pending: tuple[str, ...] = ()
    while True:
        try:
            pr_state, pr_head, contexts = parse_rollup(fetch())
        except GhCommandError as exc:
            log(f"::warning::Could not read PR checks ({exc}); retrying.")
            pr_state, pr_head, contexts = "OPEN", head_sha, None

        if pr_state == "MERGED":
            log("::notice::Pull request is already merged.")
            return 0
        if pr_state != "OPEN":
            log(f"::error::Pull request is {pr_state}; refusing to continue.")
            return 1
        if pr_head != head_sha:
            log(f"::error::Pull request head moved to {pr_head}; expected {head_sha}.")
            return 1

        if contexts is not None:
            result = evaluate(required, contexts)
            if result.state == "failed":
                log("::error::Required checks failed:")
                for item in result.failed:
                    log(f"  - {item}")
                return 1
            if result.state == "passed":
                log(f"All {len(result.passed)} required checks passed on {head_sha}.")
                return 0
            last_pending = result.pending

        if clock() >= deadline:
            log(f"::error::Timed out after {int(timeout)}s waiting for required checks:")
            for item in last_pending:
                log(f"  - {item}")
            return 1
        if last_pending:
            log(f"Waiting for {len(last_pending)} required check(s): " + "; ".join(last_pending))
        sleep(interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--pr", required=True, type=int, help="pull request number")
    parser.add_argument("--head-sha", required=True, help="expected PR head commit")
    parser.add_argument("--base", default="main", help="base branch whose rules apply")
    parser.add_argument("--timeout", type=float, default=2700.0, help="seconds to wait")
    parser.add_argument("--interval", type=float, default=20.0, help="seconds between polls")
    args = parser.parse_args(argv)

    if "/" not in args.repo:
        print("::error::--repo must be owner/name", file=sys.stderr)
        return 2

    try:
        required = fetch_required_checks(args.repo, args.base)
        print(f"Required checks for {args.base}: " + ", ".join(check.context for check in required))
        return wait_for_checks(
            required=required,
            head_sha=args.head_sha,
            fetch=lambda: fetch_rollup(args.repo, args.pr),
            timeout=args.timeout,
            interval=args.interval,
        )
    except (ConfigurationError, GhCommandError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
