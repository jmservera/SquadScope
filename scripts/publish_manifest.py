#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "publish_eligibility_v1"
AI_SOURCES = {"copilot-cli"}
RUN_MODES = {"normal", "dry-run", "restore", "force-replace", "candidate-only"}
SYNTHESIS_STATUSES = {"available", "missing", "empty", "failed"}
SOURCE_REFRESH_POLICIES = {"reuse-same-day", "refresh-missing-stale", "force-refresh"}
ALLOWED_PROMOTION_MANIFEST_ROOTS = {("data", "staging"), ("data", "candidates")}
PROMOTION_MANIFEST_ROOT_ERROR = (
    "Publish manifest must live under data/staging/ or data/candidates/."
)
NO_AI_SOURCE = "no-ai"
MIN_PUBLISH_QUALITY_SCORE = 60
FALLBACK_MIN_QUALITY_SCORE = 70
NO_AI_MARKERS = (
    "AI analysis was unavailable",
    "without AI-powered analysis",
    "Automated data-only summary",
    "generated without AI assistance",
)
FRONTMATTER_PATTERN = re.compile(r"^---\n(?P<frontmatter>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or validate a weekly publish eligibility manifest."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a publish eligibility manifest.")
    create.add_argument("--week", required=True)
    create.add_argument("--run-id", required=True)
    create.add_argument("--current-datetime", required=True)
    create.add_argument("--summary", required=True, type=Path)
    create.add_argument(
        "--content",
        type=Path,
        help="Rendered candidate content path. Defaults to --summary for legacy summary-only manifests.",
    )
    create.add_argument("--published-summary", required=True, type=Path)
    create.add_argument("--raw-json", required=True, type=Path)
    create.add_argument("--analysis-source", required=True)
    create.add_argument("--analysis-model", default="copilot-default")
    create.add_argument(
        "--preflight-report",
        type=Path,
        help="Analysis preflight report JSON used to decide whether Copilot output is normally promotable.",
    )
    create.add_argument("--validation-status", choices=["passed", "failed"], required=True)
    create.add_argument("--run-mode", choices=sorted(RUN_MODES), default="normal")
    create.add_argument(
        "--source-refresh-policy", choices=sorted(SOURCE_REFRESH_POLICIES), default="reuse-same-day"
    )
    create.add_argument(
        "--gate-report",
        type=Path,
        help="Structured analysis gate report emitted by analysis_gate.py.",
    )
    create.add_argument(
        "--synthesis-status",
        choices=sorted(SYNTHESIS_STATUSES),
        default="missing",
        help=(
            "Status of the required weekly synthesis narrative that feeds the Copilot "
            "analysis prompt. Defaults to 'missing' (fail closed) when not explicitly "
            "provided by the workflow. Only 'available' is publishable for normal-mode "
            "AI-authored publication."
        ),
    )
    create.add_argument(
        "--synthesis-file",
        type=Path,
        help="Path to the synthesis narrative file, when --synthesis-status is 'available'.",
    )
    create.add_argument("--output", required=True, type=Path)
    create.add_argument(
        "--artifact", action="append", default=[], help="Additional source artifact as role=path."
    )
    create.add_argument(
        "--fallback-reason",
        default="",
        help="Required reason when analysis-source is no-ai; records why AI output was unavailable.",
    )
    create.add_argument(
        "--attempted-ai-path",
        action="append",
        default=[],
        help="AI path attempted before this candidate, e.g. provider=copilot-cli,model=copilot-default,status=failed.",
    )
    create.add_argument(
        "--publish-policy",
        choices=["default", "allow-no-ai-first-publish", "force-replace"],
        default="default",
        help="Explicit operator policy for no-AI fallback publication.",
    )
    create.add_argument(
        "--force-reason", default="", help="Operator reason required for force-replace."
    )
    create.add_argument(
        "--actor",
        default="",
        help="Operator or automation actor requesting explicit fallback policy.",
    )

    check = subparsers.add_parser(
        "assert-eligible", help="Fail unless the manifest permits promotion."
    )
    check.add_argument("--manifest", required=True, type=Path)
    return parser.parse_args(argv)


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def week_slug(value: datetime) -> str:
    iso_year, iso_week, _ = value.astimezone(UTC).isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_preflight(
    path: Path | None, *, required: bool = False
) -> tuple[dict[str, Any] | None, list[str]]:
    if path is None:
        if required:
            return None, ["preflight report is required for Copilot CLI promotion"]
        return None, []
    payload = load_json(path)
    if payload is None:
        return None, [f"preflight report missing or malformed: {path}"]
    reasons: list[str] = []
    if payload.get("publish_eligible") is not True:
        reasons.append("preflight report marks candidate as publish-ineligible")
    return payload, reasons


def manifest_lives_under_allowed_promotion_root(
    manifest_path: Path, root: Path | None = None
) -> bool:
    workspace = (root or Path.cwd()).resolve()
    resolved_manifest = manifest_path if manifest_path.is_absolute() else workspace / manifest_path
    try:
        manifest_relative = resolved_manifest.resolve().relative_to(workspace)
    except ValueError:
        return False
    return manifest_relative.parts[:2] in ALLOWED_PROMOTION_MANIFEST_ROOTS


def _parse_scalar(value: str) -> Any:
    stripped = value.strip().strip("\"'")
    if re.fullmatch(r"-?\d+", stripped):
        return int(stripped)
    if re.fullmatch(r"-?\d+\.\d+", stripped):
        return float(stripped)
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False
    return stripped


def markdown_metadata(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {
            "exists": False,
            "path": path.as_posix(),
            "sha256": None,
            "quality_score": None,
            "week": None,
            "ai_status": "missing",
            "reasons": ["summary missing"],
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    match = FRONTMATTER_PATTERN.match(text)
    frontmatter: dict[str, Any] = {}
    reasons: list[str] = []
    if match:
        for line in match.group("frontmatter").splitlines():
            if ":" not in line or line.startswith((" ", "\t")):
                continue
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = _parse_scalar(value)
    else:
        reasons.append("summary lacks YAML frontmatter")

    quality = frontmatter.get("quality_score")
    if not isinstance(quality, (int, float)):
        quality = None
    ai_status = "no-ai" if any(marker in text for marker in NO_AI_MARKERS) else "unknown"
    source = str(frontmatter.get("analysis_source") or frontmatter.get("source") or "").strip()
    if source in AI_SOURCES:
        ai_status = "ai"
    elif source == "no-ai":
        ai_status = "no-ai"

    return {
        "exists": True,
        "path": path.as_posix(),
        "sha256": sha256_file(path),
        "quality_score": quality,
        "week": frontmatter.get("week"),
        "title": frontmatter.get("title"),
        "ai_status": ai_status,
        "reasons": reasons,
    }


def _published_manifest_paths(published_summary: Path, week: str) -> list[Path]:
    root = published_summary
    for parent in [published_summary, *published_summary.parents]:
        if (parent / "data").exists():
            root = parent
            break
    candidate_root = root / "data" / "candidates" / week
    return sorted(candidate_root.glob("*/publish-manifest.json")) if candidate_root.exists() else []


def _ai_status_from_manifest(payload: dict[str, Any]) -> str:
    analysis = payload.get("analysis")
    if isinstance(analysis, dict):
        ai_status = analysis.get("ai_status")
        if ai_status in {"ai", "no-ai"}:
            return ai_status
    ai_provenance = payload.get("ai_provenance")
    if isinstance(ai_provenance, dict):
        source = ai_provenance.get("source")
        if source in AI_SOURCES:
            return "ai"
        if source == "no-ai":
            return "no-ai"
    return "unknown"


def published_summary_status(path: Path, week: str) -> dict[str, Any]:
    status = markdown_metadata(path)
    if not status["exists"]:
        status.update({"good": False, "provenance_source": "missing"})
        return status

    matching_manifest: dict[str, Any] | None = None
    summary_sha = status.get("sha256")
    for manifest_path in _published_manifest_paths(path, week):
        payload = load_json(manifest_path)
        if not payload:
            continue
        candidate = payload.get("candidate")
        candidate_sha = candidate.get("summary_sha256") if isinstance(candidate, dict) else None
        if candidate_sha == summary_sha:
            matching_manifest = payload
            status["provenance_manifest_path"] = manifest_path.as_posix()
            break

    if matching_manifest:
        status["ai_status"] = _ai_status_from_manifest(matching_manifest)
        status["provenance_source"] = "publish-manifest"
    else:
        status["provenance_source"] = "summary"

    reasons = list(status.get("reasons", []))
    if status.get("week") != week:
        reasons.append(
            f"published summary week mismatch: expected {week}, found {status.get('week')!r}"
        )
    quality = status.get("quality_score")
    if quality is None:
        reasons.append("published summary lacks quality_score")
    elif quality < MIN_PUBLISH_QUALITY_SCORE:
        reasons.append(
            f"published summary quality_score below {MIN_PUBLISH_QUALITY_SCORE}: {quality}"
        )
    if status.get("ai_status") == "no-ai":
        reasons.append("published summary is no-AI fallback")

    status["reasons"] = reasons
    status["good"] = not reasons and status.get("ai_status") != "no-ai"
    return status


def fallback_quality_errors(summary: Path, validation_passed: bool) -> list[str]:
    errors: list[str] = []
    if not validation_passed:
        errors.append("no-AI fallback cannot publish because analysis validation did not pass")
    quality_score = markdown_metadata(summary).get("quality_score")
    if not isinstance(quality_score, (int, float)) or quality_score < FALLBACK_MIN_QUALITY_SCORE:
        errors.append(
            f"no-AI fallback quality_score must be at least {FALLBACK_MIN_QUALITY_SCORE} for explicit fallback publication"
        )
    return errors


def same_day_reuse_status(payload: dict[str, Any] | None) -> dict[str, Any]:
    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    explicit = metadata.get("same_day_reuse") or metadata.get("same_day_reuse_status")
    if isinstance(explicit, dict):
        return dict(explicit)
    if explicit:
        return {"status": str(explicit), "source": "artifact-metadata"}
    return {
        "status": "not_reused",
        "source": "default",
        "details": "No same-day reuse marker was present on this artifact.",
    }


def freshness_for_json_artifact(
    role: str,
    week: str,
    payload: dict[str, Any] | None,
    *,
    run_date: datetime | None = None,
    run_mode: str = "normal",
) -> dict[str, Any]:
    if payload is None:
        return {
            "status": "missing" if role == "raw_github" else "not_applicable",
            "reasons": ["artifact missing"],
        }

    reasons: list[str] = []
    artifact_week = payload.get("week")
    if artifact_week != week:
        reasons.append(f"week mismatch: expected {week}, found {artifact_week!r}")

    timestamp = payload.get("crawled_at") or payload.get("generated_at")
    parsed = parse_datetime(timestamp)
    if role in {"raw_github", "external_news", "techcrunch_news"}:
        if parsed is None:
            reasons.append("missing or invalid crawled_at/generated_at timestamp")
        elif week_slug(parsed) != week:
            reasons.append(f"timestamp week mismatch: expected {week}, found {week_slug(parsed)}")
        elif (
            run_date is not None
            and run_mode not in {"restore", "force-replace"}
            and parsed.astimezone(UTC).date() != run_date.astimezone(UTC).date()
        ):
            reasons.append("timestamp date is not the current UTC run date")

    crawl_window = payload.get("crawl_window")
    if role in {"external_news", "techcrunch_news"} and isinstance(crawl_window, dict):
        until = parse_datetime(crawl_window.get("until"))
        if until is not None and week_slug(until) != week:
            reasons.append(
                f"crawl_window.until week mismatch: expected {week}, found {week_slug(until)}"
            )

    return {"status": "fresh" if not reasons else "stale", "reasons": reasons}


def artifact_entry(
    role: str,
    path: Path,
    week: str,
    generated_at: str | None = None,
    *,
    run_date: datetime | None = None,
    run_mode: str = "normal",
) -> dict[str, Any]:
    payload = load_json(path) if path.suffix == ".json" else None
    metadata = (
        payload.get("metadata", {})
        if isinstance(payload, dict) and isinstance(payload.get("metadata"), dict)
        else {}
    )
    if isinstance(payload, dict):
        artifact_generated_at = (
            payload.get("generated_at") or payload.get("crawled_at") or generated_at
        )
    else:
        artifact_generated_at = generated_at
    reuse_status = same_day_reuse_status(payload)
    checksum = sha256_file(path)
    entry: dict[str, Any] = {
        "role": role,
        "path": path.as_posix(),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "sha256": checksum,
        "artifact_checksum": metadata.get("artifact_checksum"),
        "week": payload.get("week") if isinstance(payload, dict) else None,
        "crawled_at": payload.get("crawled_at") if isinstance(payload, dict) else None,
        "generated_at": artifact_generated_at,
        "same_day_reuse": reuse_status,
        "provenance": {
            "path": path.as_posix(),
            "sha256": checksum,
            "artifact_checksum": metadata.get("artifact_checksum"),
            "generated_at": artifact_generated_at,
            "same_day_reuse": reuse_status,
        },
        "freshness": freshness_for_json_artifact(
            role, week, payload, run_date=run_date, run_mode=run_mode
        )
        if path.suffix == ".json"
        else {"status": "not_applicable", "reasons": []},
    }
    if "source_status" in metadata:
        entry["source_status"] = metadata["source_status"]
    if "source_reuse_summary" in metadata:
        entry["source_reuse_summary"] = metadata["source_reuse_summary"]
    if "source_artifact_provenance" in metadata:
        entry["source_artifact_provenance"] = metadata["source_artifact_provenance"]
    if "source_config_checksum" in metadata:
        entry["source_config_checksum"] = metadata["source_config_checksum"]
    if "schema_checksum" in metadata:
        entry["schema_checksum"] = metadata["schema_checksum"]
    if "sources_requested" in metadata:
        entry["sources_requested"] = metadata["sources_requested"]
        entry["sources_succeeded"] = metadata.get("sources_succeeded", [])
        entry["sources_failed"] = metadata.get("sources_failed", [])
    return entry


def parse_artifacts(values: list[str]) -> list[tuple[str, Path]]:
    artifacts: list[tuple[str, Path]] = []
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --artifact value {value!r}; expected role=path")
        role, raw_path = value.split("=", 1)
        role = role.strip()
        if not role:
            raise SystemExit(f"Invalid --artifact value {value!r}; missing role")
        artifacts.append((role, Path(raw_path)))
    return artifacts


def load_gate_report(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "path": None,
            "present": False,
            "passed": False,
            "gates": {},
            "errors": ["structured analysis gate report was not provided"],
        }
    payload = load_json(path)
    if payload is None:
        return {
            "path": path.as_posix(),
            "present": False,
            "passed": False,
            "gates": {},
            "errors": ["structured analysis gate report is missing or malformed"],
        }
    gates = payload.get("gates")
    if not isinstance(gates, dict):
        gates = {}
    errors = payload.get("errors_after_repair")
    if not isinstance(errors, list):
        errors = []
    report = {
        "path": path.as_posix(),
        "present": True,
        "passed": payload.get("passed") is True,
        "failure_class": payload.get("failure_class"),
        "source": payload.get("source"),
        "model": payload.get("model"),
        "repair_actions": payload.get("repair_actions")
        if isinstance(payload.get("repair_actions"), list)
        else [],
        "errors": [str(error) for error in errors],
        "gates": gates,
        "sha256": sha256_file(path),
    }
    for gate_name in (
        "structural_schema",
        "ai_provenance",
        "evidence_citation",
        "editorial_quality",
    ):
        gate = gates.get(gate_name)
        if not isinstance(gate, dict) or gate.get("passed") is not True:
            report["passed"] = False
    return report


def gate_reasons(report: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not report.get("present"):
        return [
            str(error)
            for error in report.get("errors", ["structured analysis gate report missing"])
        ]
    gates = report.get("gates", {})
    if not isinstance(gates, dict):
        gates = {}
    for required_gate in (
        "structural_schema",
        "ai_provenance",
        "evidence_citation",
        "editorial_quality",
    ):
        if required_gate not in gates:
            reasons.append(f"{required_gate} gate missing from structured analysis gate report")
    for name, gate in gates.items():
        if isinstance(gate, dict) and gate.get("passed") is not True:
            gate_errors = gate.get("errors") if isinstance(gate.get("errors"), list) else []
            if gate_errors:
                reasons.extend(f"{name}: {error}" for error in gate_errors)
            else:
                reasons.append(f"{name} gate did not pass")
    for error in report.get("errors", []):
        if not any(str(error) in reason for reason in reasons):
            reasons.append(str(error))
    return reasons


def publishable_model_status(model: str) -> str:
    normalized = model.strip().lower()
    if normalized in {"", "unknown", "unavailable", "none", "no-ai"}:
        return "unavailable"
    return "available"


def create_manifest(args: argparse.Namespace) -> int:
    artifacts = [("raw_github", args.raw_json), *parse_artifacts(args.artifact)]
    run_date = parse_datetime(args.current_datetime)
    if run_date is None:
        raise SystemExit(f"Invalid --current-datetime value: {args.current_datetime!r}")
    source_artifacts = [
        artifact_entry(
            role, path, args.week, args.current_datetime, run_date=run_date, run_mode=args.run_mode
        )
        for role, path in artifacts
        if path.exists() or role == "raw_github"
    ]
    artifact_reasons = [
        f"{entry['role']}: {reason}"
        for entry in source_artifacts
        for reason in entry.get("freshness", {}).get("reasons", [])
    ]

    analysis_source = args.analysis_source.strip()
    ai_status = (
        "ai"
        if analysis_source in AI_SOURCES
        else "no-ai"
        if analysis_source == NO_AI_SOURCE
        else "unknown"
    )
    model_status = publishable_model_status(args.analysis_model)
    preflight, preflight_reasons = load_preflight(args.preflight_report, required=ai_status == "ai")
    gate_report = load_gate_report(args.gate_report)
    candidate_metadata = markdown_metadata(args.summary)
    published_status = published_summary_status(args.published_summary, args.week)
    candidate_exists = args.summary.exists()
    candidate_content = args.content or args.summary
    candidate_content_exists = candidate_content.exists()
    validation_passed = args.validation_status == "passed"
    mode_allows_promotion = args.run_mode not in {"dry-run", "candidate-only"}
    # Required synthesis only gates normal-mode AI-authored publication. Explicitly
    # documented non-normal/debug modes (dry-run, candidate-only, restore,
    # force-replace) are unaffected, matching their existing escape-hatch gates.
    synthesis_status = args.synthesis_status
    synthesis_required = args.run_mode == "normal" and ai_status == "ai"
    synthesis_reasons: list[str] = []
    # Fail closed: a claim of "available" is only trustworthy when it is backed by a
    # readable, non-empty synthesis file. If the provenance is absent or invalid we
    # downgrade the status to "missing" and drop the (unusable) file reference so the
    # manifest never advertises unbacked synthesis provenance.
    synthesis_file = args.synthesis_file
    synthesis_sha256 = sha256_file(synthesis_file) if synthesis_file else None
    if synthesis_status == "available":
        file_ok = (
            synthesis_file is not None
            and synthesis_file.is_file()
            and synthesis_file.stat().st_size > 0
            and synthesis_sha256 is not None
        )
        if not file_ok:
            synthesis_status = "missing"
            synthesis_file = None
            synthesis_sha256 = None
            if synthesis_required:
                synthesis_reasons.append(
                    "required synthesis claimed 'available' but no readable, non-empty "
                    "synthesis file was provided (downgraded to missing)"
                )
    if synthesis_required and synthesis_status != "available":
        if not synthesis_reasons:
            synthesis_reasons.append(
                f"required synthesis is {synthesis_status} for normal publication"
            )
    gates_passed = gate_report.get("present") is True and gate_report.get("passed") is True
    candidate_quality = candidate_metadata.get("quality_score")
    attempted_ai_paths = [path for path in args.attempted_ai_path if path.strip()]
    force_replacing_no_ai = ai_status == "no-ai" and args.publish_policy == "force-replace"
    comparison_reasons: list[str] = []
    if candidate_exists:
        if candidate_metadata.get("week") not in {None, args.week}:
            comparison_reasons.append(
                f"candidate summary week mismatch: expected {args.week}, found {candidate_metadata.get('week')!r}"
            )
        if candidate_quality is None:
            comparison_reasons.append("candidate summary lacks quality_score")
        elif candidate_quality < MIN_PUBLISH_QUALITY_SCORE:
            comparison_reasons.append(
                f"candidate quality_score below {MIN_PUBLISH_QUALITY_SCORE}: {candidate_quality}"
            )
        if (
            published_status.get("good")
            and isinstance(candidate_quality, (int, float))
            and not force_replacing_no_ai
        ):
            published_quality = published_status.get("quality_score")
            if (
                isinstance(published_quality, (int, float))
                and candidate_quality < published_quality
            ):
                comparison_reasons.append(
                    f"candidate quality_score {candidate_quality} is lower than published good quality_score {published_quality}"
                )

    reasons: list[str] = []
    fallback_errors: list[str] = []
    if ai_status == "no-ai":
        if not args.fallback_reason.strip():
            reasons.append("fallback_reason is required for no-AI fallback candidates")
        if not attempted_ai_paths:
            reasons.append(
                "attempted_ai_paths must record attempted AI paths for no-AI fallback candidates"
            )
        if args.publish_policy == "default":
            if published_status.get("good"):
                reasons.append(
                    "no-AI fallback is ineligible to replace an existing good AI-authored article by default"
                )
            else:
                reasons.append(
                    "no-AI fallback requires explicit allow-no-ai-first-publish or force-replace policy"
                )
        elif args.publish_policy == "allow-no-ai-first-publish":
            if published_status.get("good"):
                reasons.append(
                    "allow-no-ai-first-publish cannot replace an existing good AI-authored article"
                )
            fallback_errors = fallback_quality_errors(args.summary, validation_passed)
        elif args.publish_policy == "force-replace":
            if not args.force_reason.strip():
                reasons.append("force-replace requires force_reason")
            if not args.actor.strip():
                reasons.append("force-replace requires actor")
            fallback_errors = fallback_quality_errors(args.summary, validation_passed)
        reasons.extend(fallback_errors)

    if not candidate_exists:
        reasons.append(f"candidate summary missing: {args.summary}")
    if not candidate_content_exists:
        reasons.append(f"candidate content missing: {candidate_content}")
    if not validation_passed:
        reasons.append("analysis validation did not pass")
    if ai_status not in {"ai", "no-ai"}:
        reasons.append(f"analysis source is not AI-publishable: {analysis_source or 'unknown'}")
    reasons.extend(preflight_reasons)
    if not mode_allows_promotion:
        reasons.append(f"run mode {args.run_mode} is non-publishing")
    if ai_status == "ai" and model_status != "available":
        reasons.append(f"analysis model is not AI-publishable: {args.analysis_model or 'unknown'}")
    if not gates_passed:
        reasons.extend(gate_reasons(gate_report))
    reasons.extend(artifact_reasons)
    reasons.extend(comparison_reasons)
    reasons.extend(synthesis_reasons)

    eligible = (
        candidate_exists
        and candidate_content_exists
        and validation_passed
        and gates_passed
        and not artifact_reasons
        and not comparison_reasons
        and not preflight_reasons
        and not synthesis_reasons
        and mode_allows_promotion
        and not reasons
        and (
            (ai_status == "ai" and model_status == "available")
            or (
                ai_status == "no-ai"
                and args.publish_policy in {"allow-no-ai-first-publish", "force-replace"}
            )
        )
    )
    preserve_existing = bool(published_status.get("good") and not eligible)
    decision = "promote" if eligible else "preserve" if preserve_existing else "block"

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "week": args.week,
        "generated_at": args.current_datetime,
        "run_mode": args.run_mode,
        "source_refresh_policy": args.source_refresh_policy,
        "run_started_at": args.current_datetime,
        "candidate_summary_path": args.summary.as_posix(),
        "candidate_content_path": candidate_content.as_posix(),
        "promotion_eligible": eligible,
        "candidate": {
            "summary_path": args.summary.as_posix(),
            "content_path": candidate_content.as_posix(),
            "published_summary_path": args.published_summary.as_posix(),
            "summary_sha256": sha256_file(args.summary),
            "quality_score": candidate_quality,
            "ai_status": ai_status,
        },
        "published": published_status,
        "source_artifacts": source_artifacts,
        "synthesis": {
            "required": synthesis_required,
            "status": synthesis_status,
            "available": synthesis_status == "available",
            "path": synthesis_file.as_posix() if synthesis_file else None,
            "sha256": synthesis_sha256,
            "reasons": synthesis_reasons,
        },
        "analysis": {
            "ai_status": ai_status,
            "source": analysis_source,
            "model": args.analysis_model,
            "model_status": model_status,
            "provider": analysis_source,
            "preflight": {
                "path": args.preflight_report.as_posix() if args.preflight_report else None,
                "degraded": preflight.get("degraded") if preflight else None,
                "publish_eligible": preflight.get("publish_eligible") if preflight else None,
                "prompt_tokens": preflight.get("prompt_tokens") if preflight else None,
                "prompt_token_budget": preflight.get("prompt_token_budget") if preflight else None,
                "prompt_checksum_sha256": preflight.get("prompt_checksum_sha256")
                if preflight
                else None,
                "promotion_policy": preflight.get("promotion_policy") if preflight else None,
                "degradation_reason": preflight.get("degradation_reason") if preflight else None,
            },
            "provenance": {
                "run_id": args.run_id,
                "current_datetime": args.current_datetime,
                "authorship": "ai-authored"
                if ai_status == "ai"
                else "no-ai-fallback"
                if ai_status == "no-ai"
                else "unknown",
                "provider": analysis_source,
                "model": args.analysis_model,
                "degraded": preflight.get("degraded") if preflight else None,
                "fallback_reason": args.fallback_reason.strip() or None,
                "attempted_ai_paths": attempted_ai_paths,
            },
        },
        "ai_provenance": {
            "source": analysis_source,
            "model": args.analysis_model,
            "degraded": ai_status != "ai" or model_status != "available",
            "authorship": "ai-authored"
            if ai_status == "ai"
            else "no-ai-fallback"
            if ai_status == "no-ai"
            else "unknown",
            "fallback_reason": args.fallback_reason.strip() or None,
            "attempted_ai_paths": attempted_ai_paths,
        },
        "gate_results": {
            name: isinstance(gate, dict) and gate.get("passed") is True
            for name, gate in (
                gate_report.get("gates") if isinstance(gate_report.get("gates"), dict) else {}
            ).items()
        },
        "existing_article": {
            "exists": published_status["exists"],
            "path": published_status["path"],
            "quality_score": published_status.get("quality_score"),
            "provenance": (
                "no-ai-fallback"
                if published_status.get("ai_status") == "no-ai"
                else "ai-authored-assumed"
                if published_status["exists"]
                else "none"
            ),
            "good_ai_authored": bool(published_status.get("good")),
        },
        "validation": {
            "status": args.validation_status,
            "gate_report": gate_report,
            "quality_gates": [
                {
                    "name": "analysis_gate",
                    "status": "passed" if gates_passed else "failed",
                    "source": analysis_source,
                    "report": gate_report.get("path"),
                }
            ],
        },
        "promotion": {
            "eligible": eligible,
            "decision": decision,
            "mode": args.run_mode,
            "source_refresh_policy": args.source_refresh_policy,
            "policy": args.publish_policy,
            "reasons": reasons,
        },
        "audit": {
            "mode": args.publish_policy,
            "actor": args.actor.strip() or None,
            "reason": args.force_reason.strip() or None,
            "source_artifact_count": len(source_artifacts),
            "source_artifacts": source_artifacts,
        },
        "preservation": {
            "preserve_existing": preserve_existing,
            "preserved_summary_path": args.published_summary.as_posix()
            if preserve_existing
            else None,
            "rejected_candidate_path": args.summary.as_posix()
            if not eligible and candidate_exists
            else None,
            "reasons": reasons if preserve_existing else [],
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Publish manifest decision={manifest['promotion']['decision']} path={args.output}")
    if preserve_existing:
        print(f"Preserving published summary: {args.published_summary}")
        if candidate_exists:
            print(f"Rejected candidate summary: {args.summary}")
    if reasons:
        for reason in reasons:
            print(f"- {reason}")
    return 0


def assert_eligible(args: argparse.Namespace) -> int:
    payload = load_json(args.manifest)
    if payload is None:
        raise SystemExit(f"Publish manifest is missing or malformed: {args.manifest}")
    if not manifest_lives_under_allowed_promotion_root(args.manifest):
        raise SystemExit(PROMOTION_MANIFEST_ROOT_ERROR)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(f"Unsupported publish manifest schema: {payload.get('schema_version')!r}")
    analysis = payload.get("analysis")
    if not isinstance(analysis, dict):
        raise SystemExit("Manifest lacks publishable AI provenance.")
    ai_status = analysis.get("ai_status")
    if ai_status == "ai" and analysis.get("model_status") != "available":
        raise SystemExit("Manifest lacks an available AI model.")
    if ai_status == "ai":
        preflight = analysis.get("preflight")
        if not isinstance(preflight, dict) or preflight.get("publish_eligible") is not True:
            raise SystemExit("Manifest lacks a publish-eligible Copilot preflight report.")
    synthesis = payload.get("synthesis")
    if ai_status == "ai" and payload.get("run_mode") == "normal":
        if not isinstance(synthesis, dict) or synthesis.get("required") is not True:
            raise SystemExit(
                "Manifest lacks required synthesis provenance for normal-mode publication."
            )
        if synthesis.get("status") != "available":
            raise SystemExit(
                "Manifest blocks promotion: required synthesis is "
                f"{synthesis.get('status')!r} (missing/empty/failed), not available."
            )
        synthesis_path = synthesis.get("path")
        synthesis_sha256 = synthesis.get("sha256")
        if not (isinstance(synthesis_path, str) and synthesis_path.strip()) or not (
            isinstance(synthesis_sha256, str) and synthesis_sha256.strip()
        ):
            raise SystemExit(
                "Manifest claims synthesis is available but lacks authoritative "
                "provenance (path and sha256)."
            )
    validation = payload.get("validation")
    gate_report = validation.get("gate_report") if isinstance(validation, dict) else None
    if (
        not isinstance(gate_report, dict)
        or gate_report.get("present") is not True
        or gate_report.get("passed") is not True
    ):
        raise SystemExit("Manifest lacks a passing structured analysis gate report.")
    for gate_name in (
        "structural_schema",
        "ai_provenance",
        "evidence_citation",
        "editorial_quality",
    ):
        gate = (
            gate_report.get("gates", {}).get(gate_name)
            if isinstance(gate_report.get("gates"), dict)
            else None
        )
        if not isinstance(gate, dict) or gate.get("passed") is not True:
            raise SystemExit(f"Manifest analysis gate did not pass: {gate_name}")
    promotion_policy = (
        (payload.get("promotion") or {}).get("policy")
        if isinstance(payload.get("promotion"), dict)
        else None
    )
    if ai_status == "no-ai":
        provenance = analysis.get("provenance") if isinstance(analysis, dict) else {}
        if not isinstance(provenance, dict) or provenance.get("authorship") != "no-ai-fallback":
            raise SystemExit("Manifest lacks no-AI fallback provenance.")
        if not provenance.get("fallback_reason"):
            raise SystemExit("Manifest lacks no-AI fallback reason.")
        if not provenance.get("attempted_ai_paths"):
            raise SystemExit("Manifest lacks attempted AI path audit.")
        if promotion_policy == "force-replace":
            audit = payload.get("audit")
            if not isinstance(audit, dict) or not audit.get("actor") or not audit.get("reason"):
                raise SystemExit("Force replacement requires actor and reason in manifest audit.")
    elif ai_status != "ai":
        raise SystemExit("Manifest lacks publishable AI provenance.")
    promotion = payload.get("promotion")
    if (
        not isinstance(promotion, dict)
        or promotion.get("eligible") is not True
        or promotion.get("decision") != "promote"
    ):
        reasons = (
            promotion.get("reasons") if isinstance(promotion, dict) else ["missing promotion block"]
        )
        raise SystemExit(
            f"Manifest blocks promotion: {', '.join(str(reason) for reason in reasons)}"
        )
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict) or not candidate.get("summary_sha256"):
        raise SystemExit("Manifest lacks candidate summary checksum.")
    source_artifacts = payload.get("source_artifacts")
    if not isinstance(source_artifacts, list) or not source_artifacts:
        raise SystemExit("Manifest lacks source artifact provenance.")
    for entry in source_artifacts:
        if not isinstance(entry, dict) or not entry.get("sha256"):
            raise SystemExit("Manifest source artifact is missing a checksum.")
        provenance = entry.get("provenance")
        if not isinstance(provenance, dict) or provenance.get("sha256") != entry.get("sha256"):
            raise SystemExit("Manifest source artifact is missing auditable provenance.")
        if not isinstance(provenance.get("same_day_reuse"), dict):
            raise SystemExit("Manifest source artifact reuse provenance is missing.")
        freshness = entry.get("freshness", {})
        if isinstance(freshness, dict) and freshness.get("status") == "stale":
            raise SystemExit(f"Manifest source artifact is stale: {entry.get('path')}")
    print(f"Manifest permits promotion: {args.manifest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "create":
        return create_manifest(args)
    if args.command == "assert-eligible":
        return assert_eligible(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
