#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CopilotFailure:
    failure_class: str
    retryable: bool
    actionable: bool
    diagnostic: str
    exit_code: int | None = None


TOKEN_PATTERNS = (
    "bad credentials",
    "invalid token",
    "expired token",
    "token expired",
    "authentication failed",
    "unauthorized",
    "copilot_github_token",
)
INACCESSIBLE_PATTERNS = (
    "401",
    "403",
    "copilot is not available",
    "copilot unavailable",
    "permission",
    "not subscribed",
    "subscription",
    "access to copilot",
    "forbidden",
)
CONTEXT_PATTERNS = (
    "context length",
    "context too large",
    "maximum context",
    "token limit",
    "too many tokens",
    "prompt is too long",
)
TIMEOUT_PATTERNS = ("timed out", "timeout", "deadline exceeded")
TRANSIENT_PATTERNS = (
    "rate limit",
    "429",
    "500",
    "502",
    "503",
    "504",
    "econnreset",
    "network",
    "temporarily unavailable",
    "temporary failure",
)


def classify_log(log_text: str, exit_code: int | None = None) -> CopilotFailure:
    normalized = log_text.lower()
    if any(pattern in normalized for pattern in TOKEN_PATTERNS):
        return CopilotFailure(
            "copilot_token_failure",
            retryable=False,
            actionable=True,
            diagnostic="Copilot authentication/token failure; renew COPILOT_GH_TOKEN.",
            exit_code=exit_code,
        )
    if any(pattern in normalized for pattern in CONTEXT_PATTERNS):
        return CopilotFailure(
            "context_too_large",
            retryable=False,
            actionable=True,
            diagnostic="Copilot prompt/context exceeded supported size; reduce analysis context before rerun.",
            exit_code=exit_code,
        )
    if any(pattern in normalized for pattern in TIMEOUT_PATTERNS):
        return CopilotFailure(
            "timeout",
            retryable=True,
            actionable=False,
            diagnostic="Copilot analysis timed out; retry is allowed.",
            exit_code=exit_code,
        )
    if any(pattern in normalized for pattern in TRANSIENT_PATTERNS):
        return CopilotFailure(
            "transient_error",
            retryable=True,
            actionable=False,
            diagnostic="Copilot analysis hit a transient service/network failure; retry is allowed.",
            exit_code=exit_code,
        )
    if any(pattern in normalized for pattern in INACCESSIBLE_PATTERNS):
        return CopilotFailure(
            "copilot_token_failure",
            retryable=False,
            actionable=True,
            diagnostic="Copilot authentication/access failure; renew COPILOT_GH_TOKEN or verify Copilot permissions.",
            exit_code=exit_code,
        )
    return CopilotFailure(
        "other",
        retryable=True,
        actionable=False,
        diagnostic="Copilot analysis failed with an unclassified error; retry is allowed before failing the run.",
        exit_code=exit_code,
    )


def issue_title() -> str:
    return "Renew GitHub Copilot token for weekly analysis workflow"


def issue_body(report: CopilotFailure, *, week: str, run_id: str) -> str:
    return "\n".join(
        [
            "The weekly analysis workflow cannot run because GitHub Copilot authentication failed.",
            "",
            f"- Week: `{week}`",
            f"- Run ID: `{run_id}`",
            f"- Failure class: `{report.failure_class}`",
            f"- Diagnostic: {report.diagnostic}",
            "",
            "Please renew or replace the `COPILOT_GH_TOKEN` secret, then rerun the workflow.",
        ]
    )


def run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], check=False, capture_output=True, text=True)


def issue_url(repo: str, number: str) -> str:
    return f"https://github.com/{repo}/issues/{number}"


def create_or_update_token_issue(report: CopilotFailure, *, repo: str, assignee: str, week: str, run_id: str) -> str:
    title = issue_title()
    body = issue_body(report, week=week, run_id=run_id)
    search = run_gh(
        [
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--search",
            title,
            "--json",
            "number,title",
            "--limit",
            "10",
        ]
    )
    if search.returncode == 0:
        try:
            issues = json.loads(search.stdout)
        except json.JSONDecodeError:
            issues = []
        for issue in issues:
            if issue.get("title") == title and issue.get("number"):
                number = str(issue["number"])
                comment = run_gh(["issue", "comment", number, "--repo", repo, "--body", body])
                if comment.returncode != 0:
                    raise RuntimeError(comment.stderr.strip() or "failed to update Copilot token issue")
                return issue_url(repo, number)

    created = run_gh(
        [
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            title,
            "--body",
            body,
            "--assignee",
            assignee,
            "--label",
            "type:bug",
        ]
    )
    if created.returncode != 0:
        raise RuntimeError(created.stderr.strip() or "failed to create Copilot token issue")
    created_output = created.stdout.strip()
    if created_output.startswith("https://"):
        return created_output
    return created_output or issue_url(repo, "unknown")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify Copilot CLI analysis failures.")
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--create-token-issue", action="store_true")
    parser.add_argument("--repo", default="")
    parser.add_argument("--assignee", default="jmservera")
    parser.add_argument("--week", default="")
    parser.add_argument("--run-id", default="")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    log_text = args.log.read_text(encoding="utf-8", errors="replace") if args.log.exists() else ""
    report = classify_log(log_text, args.exit_code)
    payload = asdict(report)
    payload["log_path"] = args.log.as_posix()

    if args.create_token_issue and report.failure_class == "copilot_token_failure":
        payload["issue"] = create_or_update_token_issue(
            report,
            repo=args.repo,
            assignee=args.assignee,
            week=args.week,
            run_id=args.run_id,
        )

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(report.failure_class)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
