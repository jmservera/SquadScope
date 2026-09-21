#!/usr/bin/env python3
"""Canonical podcast dispatch receipts, terminal monitoring, and incidents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib import error, parse, request

RECEIPT_SCHEMA_VERSION_V2 = "podcast_dispatch_receipt_v2"
STATUS_SCHEMA_VERSION_V1 = "podcast_publication_status_v1"
LEDGER_MARKER = "<!-- podcast-dispatch-ledger:v2 -->"
LEDGER_TITLE = "Podcast dispatch receipt ledger"
INCIDENT_MARKER_PREFIX = "<!-- podcast-dispatch-incident:v1:"
WEEK_RE = re.compile(r"^[0-9]{4}-W[0-9]{2}$")
RUN_ID_RE = re.compile(r"^[0-9]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,256}$")
RECEIPT_STATES = frozenset(
    {
        "attempt_prepared",
        "pre_submit_failed",
        "handoff_entered",
        "accepted",
        "submission_rejected",
        "submission_unknown",
        "observation_only",
    }
)
BLOCKING_STATES = frozenset({"handoff_entered", "accepted", "submission_unknown"})
RETRYABLE_STATES = frozenset(
    {"attempt_prepared", "pre_submit_failed", "submission_rejected", "observation_only"}
)
EVIDENCE_DEADLINE_SECONDS = 3480
TOTAL_MONITOR_BUDGET_SECONDS = 3600
POLL_INTERVAL_SECONDS = 30
REQUEST_TIMEOUT_SECONDS = 10
MAX_CONSECUTIVE_ERRORS = 5
SYNTHESIS_WARNING_SECONDS = 600


def _validate(value: str, pattern: re.Pattern[str], field: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"invalid {field}")
    return value


def _timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid created_at") from exc
    if parsed.tzinfo is None:
        raise ValueError("created_at must include timezone")
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class CanonicalPublicationIdentity:
    week: str
    publish_run_id: str
    article_sha256: str
    manifest_sha256: str

    def __post_init__(self) -> None:
        _validate(self.week, WEEK_RE, "week")
        _validate(str(self.publish_run_id), RUN_ID_RE, "publish_run_id")
        _validate(self.article_sha256, SHA256_RE, "article_sha256")
        _validate(self.manifest_sha256, SHA256_RE, "manifest_sha256")

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class DispatchReceipt:
    receipt_id: str
    created_at: str
    dispatch_run_id: str
    attempt_id: str
    identity: CanonicalPublicationIdentity
    receipt_state: str
    api_status: int | None = None
    api_status_category: str | None = None
    podcaster_job_id: str | None = None
    correlation_id: str | None = None
    actions_run_url: str | None = None
    stage: str | None = None
    state: str | None = None
    ledger_persisted: bool | None = None
    artifact_persisted: bool | None = None
    synthesis_latency_seconds: int | None = None

    def __post_init__(self) -> None:
        _validate(str(self.dispatch_run_id), RUN_ID_RE, "dispatch_run_id")
        _validate(self.attempt_id, SAFE_ID_RE, "attempt_id")
        _validate(self.receipt_id, SAFE_ID_RE, "receipt_id")
        _timestamp(self.created_at)
        if self.receipt_state not in RECEIPT_STATES:
            raise ValueError("invalid receipt_state")
        if self.api_status is not None and not 100 <= self.api_status <= 599:
            raise ValueError("invalid api_status")
        for field in (
            self.api_status_category,
            self.podcaster_job_id,
            self.correlation_id,
            self.stage,
            self.state,
        ):
            if field is not None:
                _validate(field, SAFE_ID_RE, "safe identifier")
        if self.actions_run_url is not None and not self.actions_run_url.startswith(
            ("https://github.com/", "https://api.github.com/")
        ):
            raise ValueError("invalid actions_run_url")
        if self.synthesis_latency_seconds is not None and self.synthesis_latency_seconds < 0:
            raise ValueError("invalid synthesis_latency_seconds")

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["schema_version"] = RECEIPT_SCHEMA_VERSION_V2
        return value


@dataclass(frozen=True)
class TerminalStatus:
    identity: CanonicalPublicationIdentity
    job_id: str
    correlation_id: str
    synthesis_state: str
    video_state: str
    provider_state: str
    external_verified: bool


@dataclass(frozen=True)
class MonitorResult:
    success: bool
    stage: str
    state: str
    synthesis_latency_seconds: int | None = None
    warning_emitted: bool = False
    detail: str = ""


def canonical_identity_key(identity: CanonicalPublicationIdentity) -> str:
    canonical = "\0".join(
        (
            identity.week,
            identity.publish_run_id,
            identity.article_sha256,
            identity.manifest_sha256,
        )
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def incident_key(identity: CanonicalPublicationIdentity, stage: str, state: str) -> str:
    canonical = json.dumps(identity.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(
        f"podcast-dispatch-incident-v1\0{canonical}\0{stage}\0{state}".encode()
    ).hexdigest()


def serialize_receipt(receipt: DispatchReceipt) -> str:
    return json.dumps(receipt.as_dict(), sort_keys=True, separators=(",", ":"))


def parse_receipt(value: str | bytes | dict[str, Any]) -> DispatchReceipt | dict[str, Any]:
    payload = json.loads(value) if isinstance(value, (str, bytes)) else value
    if not isinstance(payload, dict):
        raise ValueError("receipt must be an object")
    schema = payload.get("schema_version")
    if schema == "podcast_dispatch_receipt_v1":
        allowed = {
            "schema_version",
            "workflow",
            "dispatcher",
            "receipt_state",
            "week",
            "publish_run_id",
            "article_sha256",
            "manifest_sha256",
            "podcaster_status",
            "podcaster_job_id",
            "prior_run_url",
            "actions_run_url",
        }
        if set(payload) - allowed:
            raise ValueError("unsupported v1 receipt fields")
        return dict(payload)
    if schema != RECEIPT_SCHEMA_VERSION_V2:
        raise ValueError("unsupported receipt schema")
    allowed = {
        "schema_version",
        "receipt_id",
        "created_at",
        "dispatch_run_id",
        "attempt_id",
        "identity",
        "receipt_state",
        "api_status",
        "api_status_category",
        "podcaster_job_id",
        "correlation_id",
        "actions_run_url",
        "stage",
        "state",
        "ledger_persisted",
        "artifact_persisted",
        "synthesis_latency_seconds",
    }
    if set(payload) - allowed:
        raise ValueError("unsupported receipt fields")
    identity_payload = payload.get("identity")
    if not isinstance(identity_payload, dict) or set(identity_payload) != {
        "week",
        "publish_run_id",
        "article_sha256",
        "manifest_sha256",
    }:
        raise ValueError("invalid identity")
    identity = CanonicalPublicationIdentity(**identity_payload)
    kwargs = {
        key: value for key, value in payload.items() if key not in {"schema_version", "identity"}
    }
    return DispatchReceipt(identity=identity, **kwargs)


def receipt_retry_classification(receipts: Iterable[DispatchReceipt]) -> str:
    states = {receipt.receipt_state for receipt in receipts}
    if states & BLOCKING_STATES:
        return "blocking"
    if states <= RETRYABLE_STATES:
        return "retryable_non_mutation"
    return "ambiguous_exact"


def parse_artifact_json(data: bytes) -> list[DispatchReceipt]:
    payload = json.loads(data)
    values = payload if isinstance(payload, list) else [payload]
    receipts = [parse_receipt(value) for value in values]
    if not all(isinstance(value, DispatchReceipt) for value in receipts):
        raise ValueError("artifact contains legacy receipt")
    return [value for value in receipts if isinstance(value, DispatchReceipt)]


def _github_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "SquadScope-Podcast-Dispatch/2",
    }


def _github_json(
    url: str, token: str, *, method: str = "GET", payload: dict[str, Any] | None = None
) -> Any:
    body = None if payload is None else json.dumps(payload).encode()
    req = request.Request(url, data=body, method=method, headers=_github_headers(token))
    with request.urlopen(req, timeout=20) as response:  # nosec B310
        return json.loads(response.read())


def _iter_issue_pages(repo: str, token: str, state: str = "all") -> Iterable[dict[str, Any]]:
    for page in range(1, 101):
        url = f"https://api.github.com/repos/{repo}/issues?state={state}&per_page=100&page={page}"
        values = _github_json(url, token)
        if not isinstance(values, list):
            raise ValueError("issues response must be a list")
        yield from (value for value in values if isinstance(value, dict))
        if len(values) < 100:
            break


def _trusted_comment(comment: dict[str, Any], repo: str) -> bool:
    user = comment.get("user") or {}
    body = comment.get("body")
    url = str(comment.get("html_url") or "")
    return (
        user.get("login") == "github-actions[bot]"
        and isinstance(body, str)
        and f"github.com/{repo}/" in url
    )


def list_ledger_receipts(repo: str, token: str) -> list[DispatchReceipt]:
    ledger = next(
        (
            issue
            for issue in _iter_issue_pages(repo, token)
            if issue.get("title") == LEDGER_TITLE and LEDGER_MARKER in str(issue.get("body") or "")
        ),
        None,
    )
    if ledger is None:
        return []
    comments_url = str(ledger.get("comments_url") or "")
    if not comments_url.startswith(f"https://api.github.com/repos/{repo}/"):
        raise ValueError("untrusted ledger comments URL")
    receipts: list[DispatchReceipt] = []
    for page in range(1, 101):
        comments = _github_json(f"{comments_url}?per_page=100&page={page}", token)
        if not isinstance(comments, list):
            raise ValueError("comments response must be a list")
        for comment in comments:
            if not isinstance(comment, dict) or not _trusted_comment(comment, repo):
                continue
            body = str(comment["body"]).strip()
            try:
                parsed = parse_receipt(body)
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            if isinstance(parsed, DispatchReceipt):
                expected_run_url = (
                    f"https://github.com/{repo}/actions/runs/{parsed.dispatch_run_id}"
                )
                if parsed.actions_run_url != expected_run_url:
                    continue
                receipts.append(parsed)
        if len(comments) < 100:
            break
    return receipts


def _ledger_issue(repo: str, token: str) -> dict[str, Any]:
    issue = next(
        (
            value
            for value in _iter_issue_pages(repo, token)
            if value.get("title") == LEDGER_TITLE and LEDGER_MARKER in str(value.get("body") or "")
        ),
        None,
    )
    if issue is not None:
        return issue
    created = _github_json(
        f"https://api.github.com/repos/{repo}/issues",
        token,
        method="POST",
        payload={"title": LEDGER_TITLE, "body": f"{LEDGER_MARKER}\nAppend-only dispatch receipts."},
    )
    if not isinstance(created, dict):
        raise ValueError("invalid ledger issue response")
    return created


def append_ledger_receipt(repo: str, token: str, receipt: DispatchReceipt) -> None:
    issue = _ledger_issue(repo, token)
    number = issue.get("number")
    if not isinstance(number, int):
        raise ValueError("ledger issue number missing")
    _github_json(
        f"https://api.github.com/repos/{repo}/issues/{number}/comments",
        token,
        method="POST",
        payload={"body": serialize_receipt(receipt)},
    )


def validate_terminal_status(
    payload: Any, identity: CanonicalPublicationIdentity, job_id: str, correlation_id: str
) -> TerminalStatus:
    if not isinstance(payload, dict) or payload.get("schema_version") != STATUS_SCHEMA_VERSION_V1:
        raise ValueError("status schema unavailable")
    if payload.get("identity") != identity.as_dict():
        raise ValueError("status identity mismatch")
    if payload.get("job_id") != job_id or payload.get("correlation_id", job_id) != correlation_id:
        raise ValueError("status correlation mismatch")
    synthesis = payload.get("synthesis")
    video = payload.get("video")
    provider = payload.get("provider")
    if not all(isinstance(value, dict) for value in (synthesis, video, provider)):
        raise ValueError("status stages missing")
    synth_state = synthesis.get("state")
    video_state = video.get("state")
    provider_state = provider.get("state")
    if synth_state not in {"pending", "started", "succeeded", "failed", "unknown"}:
        raise ValueError("invalid synthesis state")
    if video_state not in {"pending", "succeeded", "failed", "unknown"}:
        raise ValueError("invalid video state")
    if provider_state not in {"pending", "published", "failed", "unknown"}:
        raise ValueError("invalid provider state")
    if not isinstance(provider.get("external_verified"), bool):
        raise ValueError("provider external_verified missing")
    return TerminalStatus(
        identity=identity,
        job_id=job_id,
        correlation_id=correlation_id,
        synthesis_state=synth_state,
        video_state=video_state,
        provider_state=provider_state,
        external_verified=provider["external_verified"],
    )


def evaluate_terminal_status(status: TerminalStatus) -> MonitorResult | None:
    for stage, state in (
        ("synthesis", status.synthesis_state),
        ("video", status.video_state),
        ("provider", status.provider_state),
    ):
        if state in {"failed", "unknown"}:
            return MonitorResult(False, stage, state)
    if (
        status.synthesis_state in {"started", "succeeded"}
        and status.video_state == "succeeded"
        and status.provider_state == "published"
        and status.external_verified
    ):
        return MonitorResult(True, "provider", "published")
    if status.provider_state == "published" and not status.external_verified:
        return MonitorResult(False, "provider", "unverified")
    return None


def fetch_terminal_status(
    endpoint: str,
    token: str,
    identity: CanonicalPublicationIdentity,
    job_id: str,
    correlation_id: str,
    timeout: float,
) -> TerminalStatus:
    query = parse.urlencode(
        {
            **identity.as_dict(),
            "job_id": job_id,
            "correlation_id": correlation_id,
        }
    )
    separator = "&" if "?" in endpoint else "?"
    req = request.Request(
        f"{endpoint}{separator}{query}",
        headers={"x-podcaster-api-key": token, "Accept": "application/json"},
    )
    with request.urlopen(req, timeout=timeout) as response:  # nosec B310
        payload = json.loads(response.read())
    return validate_terminal_status(payload, identity, job_id, correlation_id)


def monitor_terminal_outcome(
    receipt: DispatchReceipt,
    endpoint: str,
    token: str,
    *,
    fetch: Callable[..., TerminalStatus] = fetch_terminal_status,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    warning: Callable[[int], None] | None = None,
    evidence_deadline: int = EVIDENCE_DEADLINE_SECONDS,
    poll_interval: int = POLL_INTERVAL_SECONDS,
) -> MonitorResult:
    if receipt.receipt_state != "accepted" or not receipt.podcaster_job_id:
        return MonitorResult(False, "receipt", "not_accepted")
    if not endpoint:
        return MonitorResult(False, "status_contract", "unavailable")
    correlation_id = receipt.correlation_id or receipt.podcaster_job_id
    started = monotonic()
    accepted_at = datetime.fromisoformat(receipt.created_at.replace("Z", "+00:00")).timestamp()
    consecutive_errors = 0
    warning_emitted = False
    synthesis_latency: int | None = None
    latest: TerminalStatus | None = None
    while True:
        elapsed = monotonic() - started
        remaining = evidence_deadline - elapsed
        if remaining <= 0:
            break
        try:
            latest = fetch(
                endpoint,
                token,
                receipt.identity,
                receipt.podcaster_job_id,
                correlation_id,
                min(REQUEST_TIMEOUT_SECONDS, remaining),
            )
            consecutive_errors = 0
        except (OSError, ValueError, json.JSONDecodeError, error.URLError):
            consecutive_errors += 1
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                return MonitorResult(False, "evidence_unavailable", "error_budget_exhausted")
        else:
            if latest.synthesis_state in {"started", "succeeded"} and synthesis_latency is None:
                synthesis_latency = max(0, int(time.time() - accepted_at))
            result = evaluate_terminal_status(latest)
            if result is not None:
                return MonitorResult(
                    result.success,
                    result.stage,
                    result.state,
                    synthesis_latency,
                    warning_emitted,
                    result.detail,
                )
        elapsed = monotonic() - started
        if (
            synthesis_latency is None
            and elapsed >= SYNTHESIS_WARNING_SECONDS
            and not warning_emitted
        ):
            warning_emitted = True
            if warning:
                warning(int(elapsed))
        remaining = evidence_deadline - elapsed
        if remaining <= 0:
            break
        sleep(min(poll_interval, remaining))
    if latest is None or latest.synthesis_state == "pending":
        stage = "synthesis"
    elif latest.video_state == "pending":
        stage = "video"
    else:
        stage = "provider"
    return MonitorResult(False, stage, "timeout", synthesis_latency, warning_emitted)


def upsert_incident(
    repo: str,
    token: str,
    identity: CanonicalPublicationIdentity,
    stage: str,
    state: str,
    evidence: dict[str, str | int | bool | None],
) -> str:
    key = incident_key(identity, stage, state)
    marker = f"{INCIDENT_MARKER_PREFIX}{key} -->"
    body = (
        f"{marker}\n## Podcast dispatch reconciliation\n\n"
        f"* Identity key: `{canonical_identity_key(identity)}`\n"
        f"* Week: `{identity.week}`\n"
        f"* Publish run: `{identity.publish_run_id}`\n"
        f"* Article SHA-256: `{identity.article_sha256}`\n"
        f"* Manifest SHA-256: `{identity.manifest_sha256}`\n"
        f"* Stage/state: `{stage}/{state}`\n"
        f"* Evidence: `{json.dumps(evidence, sort_keys=True, separators=(',', ':'))}`\n\n"
        "Recovery: restore authoritative status evidence or reconcile manually; do not redispatch "
        "an identity with handoff-entered or unknown evidence."
    )
    existing = next(
        (
            issue
            for issue in _iter_issue_pages(repo, token, "open")
            if marker in str(issue.get("body") or "")
        ),
        None,
    )
    if existing is not None:
        number = existing.get("number")
        _github_json(
            f"https://api.github.com/repos/{repo}/issues/{number}/comments",
            token,
            method="POST",
            payload={"body": body},
        )
        return str(existing.get("html_url") or "")
    try:
        created = _github_json(
            f"https://api.github.com/repos/{repo}/issues",
            token,
            method="POST",
            payload={
                "title": f"Podcast dispatch incident: {identity.week} {stage}/{state}",
                "body": body,
                "labels": ["podcast-dispatch-incident"],
            },
        )
    except error.HTTPError:
        existing = next(
            (
                issue
                for issue in _iter_issue_pages(repo, token, "open")
                if marker in str(issue.get("body") or "")
            ),
            None,
        )
        if existing is None:
            raise
        return str(existing.get("html_url") or "")
    return str(created.get("html_url") or "") if isinstance(created, dict) else ""


def reconcile_identity_incidents(
    repo: str, token: str, identity: CanonicalPublicationIdentity
) -> None:
    identity_marker = f"* Identity key: `{canonical_identity_key(identity)}`"
    for issue in _iter_issue_pages(repo, token, "open"):
        if identity_marker not in str(issue.get("body") or ""):
            continue
        number = issue.get("number")
        if not isinstance(number, int):
            continue
        _github_json(
            f"https://api.github.com/repos/{repo}/issues/{number}/comments",
            token,
            method="POST",
            payload={"body": "Authoritative externally verified terminal publication succeeded."},
        )
        _github_json(
            f"https://api.github.com/repos/{repo}/issues/{number}",
            token,
            method="PATCH",
            payload={"state": "closed", "state_reason": "completed"},
        )


def _identity_from_args(args: argparse.Namespace) -> CanonicalPublicationIdentity:
    return CanonicalPublicationIdentity(
        args.week, args.publish_run_id, args.article_sha256, args.manifest_sha256
    )


def _build_receipt(args: argparse.Namespace) -> DispatchReceipt:
    created_at = args.created_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    attempt_id = args.attempt_id
    receipt_id = (
        args.receipt_id
        or hashlib.sha256(f"{attempt_id}\0{args.state}\0{created_at}".encode()).hexdigest()
    )
    return DispatchReceipt(
        receipt_id=receipt_id,
        created_at=created_at,
        dispatch_run_id=args.dispatch_run_id,
        attempt_id=attempt_id,
        identity=_identity_from_args(args),
        receipt_state=args.state,
        api_status=args.api_status,
        api_status_category=args.api_status_category,
        podcaster_job_id=args.job_id,
        correlation_id=args.correlation_id,
        actions_run_url=args.actions_run_url,
    )


def _add_identity_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--week", required=True)
    parser.add_argument("--publish-run-id", required=True)
    parser.add_argument("--article-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    writer = subparsers.add_parser("write-receipt")
    _add_identity_args(writer)
    writer.add_argument("--state", required=True, choices=sorted(RECEIPT_STATES))
    writer.add_argument("--dispatch-run-id", required=True)
    writer.add_argument("--attempt-id", required=True)
    writer.add_argument("--receipt-id", default="")
    writer.add_argument("--created-at", default="")
    writer.add_argument("--api-status", type=int)
    writer.add_argument("--api-status-category")
    writer.add_argument("--job-id")
    writer.add_argument("--correlation-id")
    writer.add_argument("--actions-run-url")
    writer.add_argument("--output", type=Path, required=True)
    writer.add_argument("--append-ledger", action="store_true")
    monitor = subparsers.add_parser("monitor")
    monitor.add_argument("--receipt", type=Path, required=True)
    monitor.add_argument("--endpoint", default="")
    monitor.add_argument("--api-key", default="")
    monitor.add_argument("--repo", default="")
    monitor.add_argument("--token", default="")
    monitor.add_argument("--summary", type=Path)
    incident = subparsers.add_parser("upsert-incident")
    _add_identity_args(incident)
    incident.add_argument("--stage", required=True)
    incident.add_argument("--state", required=True)
    incident.add_argument("--repo", required=True)
    incident.add_argument("--token", required=True)
    incident.add_argument("--dispatch-run-id", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "write-receipt":
        receipt = _build_receipt(args)
        args.output.write_text(serialize_receipt(receipt) + "\n", encoding="utf-8")
        if args.append_ledger:
            repo = os.environ.get("GITHUB_REPOSITORY", "")
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
            if not repo or not token:
                raise SystemExit("ledger persistence requires repository and token")
            append_ledger_receipt(repo, token, receipt)
        print(serialize_receipt(receipt))
        return 0
    if args.command == "upsert-incident":
        identity = _identity_from_args(args)
        url = upsert_incident(
            args.repo,
            args.token,
            identity,
            args.stage,
            args.state,
            {"dispatch_run_id": args.dispatch_run_id},
        )
        print(url)
        return 0
    parsed = parse_receipt(args.receipt.read_text(encoding="utf-8"))
    if not isinstance(parsed, DispatchReceipt):
        raise SystemExit("monitor requires v2 receipt")
    warning_urls: list[str] = []

    def warn(latency: int) -> None:
        if args.repo and args.token:
            warning_urls.append(
                upsert_incident(
                    args.repo,
                    args.token,
                    parsed.identity,
                    "synthesis_latency",
                    "warning",
                    {
                        "dispatch_run_id": parsed.dispatch_run_id,
                        "attempt_id": parsed.attempt_id,
                        "job_id": parsed.podcaster_job_id,
                        "correlation_id": parsed.correlation_id,
                        "synthesis_latency_seconds": latency,
                    },
                )
            )

    result = monitor_terminal_outcome(parsed, args.endpoint, args.api_key, warning=warn)
    summary = (
        f"## Podcast dispatch reconciliation\n\n"
        f"- Identity key: `{canonical_identity_key(parsed.identity)}`\n"
        f"- Result: `{result.stage}/{result.state}`\n"
        f"- Terminal success: `{str(result.success).lower()}`\n"
        f"- Synthesis latency seconds: `{result.synthesis_latency_seconds}`\n"
        f"- Synthesis warning incident: `{warning_urls[-1] if warning_urls else 'none'}`\n"
    )
    if args.summary:
        with args.summary.open("a", encoding="utf-8") as output:
            output.write(summary)
    if result.success:
        if args.repo and args.token:
            reconcile_identity_incidents(args.repo, args.token, parsed.identity)
        return 0
    if args.repo and args.token:
        upsert_incident(
            args.repo,
            args.token,
            parsed.identity,
            result.stage,
            result.state,
            {
                "dispatch_run_id": parsed.dispatch_run_id,
                "attempt_id": parsed.attempt_id,
                "job_id": parsed.podcaster_job_id,
                "correlation_id": parsed.correlation_id,
                "actions_run_url": parsed.actions_run_url,
                "synthesis_latency_seconds": result.synthesis_latency_seconds,
            },
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
