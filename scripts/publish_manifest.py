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
AI_SOURCES = {"copilot-cli", "github-models"}
NO_AI_SOURCE = "no-ai"
FALLBACK_MIN_QUALITY_SCORE = 70
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or validate a weekly publish eligibility manifest.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a publish eligibility manifest.")
    create.add_argument("--week", required=True)
    create.add_argument("--run-id", required=True)
    create.add_argument("--current-datetime", required=True)
    create.add_argument("--summary", required=True, type=Path)
    create.add_argument("--published-summary", required=True, type=Path)
    create.add_argument("--raw-json", required=True, type=Path)
    create.add_argument("--analysis-source", required=True)
    create.add_argument("--analysis-model", required=True)
    create.add_argument("--validation-status", choices=["passed", "failed"], required=True)
    create.add_argument("--output", required=True, type=Path)
    create.add_argument("--artifact", action="append", default=[], help="Additional source artifact as role=path.")
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
    create.add_argument("--force-reason", default="", help="Operator reason required for force-replace.")
    create.add_argument("--actor", default="", help="Operator or automation actor requesting explicit fallback policy.")

    check = subparsers.add_parser("assert-eligible", help="Fail unless the manifest permits promotion.")
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


def load_frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    match = FRONTMATTER_PATTERN.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    frontmatter: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, raw_value = line.split(":", 1)
        value = raw_value.strip().strip('"').strip("'")
        if value.isdigit():
            frontmatter[key.strip()] = int(value)
        else:
            frontmatter[key.strip()] = value
    return frontmatter


def classify_summary(path: Path) -> dict[str, Any]:
    exists = path.exists() and path.is_file()
    frontmatter = load_frontmatter(path) if exists else {}
    text = path.read_text(encoding="utf-8") if exists else ""
    lowered = text.lower()
    quality_score = frontmatter.get("quality_score")
    is_no_ai = any(
        marker in lowered
        for marker in (
            "source: no-ai",
            "model: none",
            "without ai-powered analysis",
            "generated without ai assistance",
            "automated data-only summary",
        )
    )
    good = isinstance(quality_score, int) and quality_score >= 60
    return {
        "exists": exists,
        "path": path.as_posix(),
        "quality_score": quality_score,
        "provenance": "no-ai-fallback" if is_no_ai else "ai-authored-assumed" if exists else "none",
        "good_ai_authored": bool(exists and good and not is_no_ai),
    }


def fallback_quality_errors(summary: Path, validation_passed: bool) -> list[str]:
    errors: list[str] = []
    if not validation_passed:
        errors.append("no-AI fallback cannot publish because analysis validation did not pass")
    quality_score = load_frontmatter(summary).get("quality_score")
    if not isinstance(quality_score, int) or quality_score < FALLBACK_MIN_QUALITY_SCORE:
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


def freshness_for_json_artifact(role: str, week: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {"status": "missing" if role == "raw_github" else "not_applicable", "reasons": ["artifact missing"]}

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

    crawl_window = payload.get("crawl_window")
    if role in {"external_news", "techcrunch_news"} and isinstance(crawl_window, dict):
        until = parse_datetime(crawl_window.get("until"))
        if until is not None and week_slug(until) != week:
            reasons.append(f"crawl_window.until week mismatch: expected {week}, found {week_slug(until)}")

    return {"status": "fresh" if not reasons else "stale", "reasons": reasons}


def artifact_entry(role: str, path: Path, week: str) -> dict[str, Any]:
    payload = load_json(path) if path.suffix == ".json" else None
    metadata = payload.get("metadata", {}) if isinstance(payload, dict) and isinstance(payload.get("metadata"), dict) else {}
    entry: dict[str, Any] = {
        "role": role,
        "path": path.as_posix(),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "sha256": sha256_file(path),
        "artifact_checksum": metadata.get("artifact_checksum"),
        "week": payload.get("week") if isinstance(payload, dict) else None,
        "crawled_at": payload.get("crawled_at") if isinstance(payload, dict) else None,
        "same_day_reuse": same_day_reuse_status(payload),
        "freshness": freshness_for_json_artifact(role, week, payload) if path.suffix == ".json" else {"status": "not_applicable", "reasons": []},
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


def create_manifest(args: argparse.Namespace) -> int:
    artifacts = [("raw_github", args.raw_json), *parse_artifacts(args.artifact)]
    source_artifacts = [artifact_entry(role, path, args.week) for role, path in artifacts if path.exists() or role == "raw_github"]
    artifact_reasons = [
        f"{entry['role']}: {reason}"
        for entry in source_artifacts
        for reason in entry.get("freshness", {}).get("reasons", [])
    ]

    analysis_source = args.analysis_source.strip()
    ai_status = "ai" if analysis_source in AI_SOURCES else "no-ai" if analysis_source == NO_AI_SOURCE else "unknown"
    candidate_exists = args.summary.exists()
    validation_passed = args.validation_status == "passed"
    existing_article = classify_summary(args.published_summary)
    attempted_ai_paths = [path for path in args.attempted_ai_path if path.strip()]

    reasons: list[str] = []
    fallback_errors: list[str] = []
    if ai_status == "no-ai":
        if not args.fallback_reason.strip():
            reasons.append("fallback_reason is required for no-AI fallback candidates")
        if not attempted_ai_paths:
            reasons.append("attempted_ai_paths must record attempted AI paths for no-AI fallback candidates")
        if args.publish_policy == "default":
            if existing_article["good_ai_authored"]:
                reasons.append("no-AI fallback is ineligible to replace an existing good AI-authored article by default")
            else:
                reasons.append("no-AI fallback requires explicit allow-no-ai-first-publish or force-replace policy")
        elif args.publish_policy == "allow-no-ai-first-publish":
            if existing_article["good_ai_authored"]:
                reasons.append("allow-no-ai-first-publish cannot replace an existing good AI-authored article")
            fallback_errors = fallback_quality_errors(args.summary, validation_passed)
        elif args.publish_policy == "force-replace":
            if not args.force_reason.strip():
                reasons.append("force-replace requires force_reason")
            if not args.actor.strip():
                reasons.append("force-replace requires actor")
            fallback_errors = fallback_quality_errors(args.summary, validation_passed)
        reasons.extend(fallback_errors)

    eligible = (
        candidate_exists
        and validation_passed
        and not artifact_reasons
        and (
            ai_status == "ai"
            or (ai_status == "no-ai" and args.publish_policy in {"allow-no-ai-first-publish", "force-replace"} and not reasons)
        )
    )

    if not candidate_exists:
        reasons.append(f"candidate summary missing: {args.summary}")
    if not validation_passed:
        reasons.append("analysis validation did not pass")
    if ai_status not in {"ai", "no-ai"}:
        reasons.append(f"analysis source is not AI-publishable: {analysis_source or 'unknown'}")
    reasons.extend(artifact_reasons)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "week": args.week,
        "generated_at": args.current_datetime,
        "candidate": {
            "summary_path": args.summary.as_posix(),
            "published_summary_path": args.published_summary.as_posix(),
            "summary_sha256": sha256_file(args.summary),
        },
        "source_artifacts": source_artifacts,
        "analysis": {
            "ai_status": ai_status,
            "source": analysis_source,
            "model": args.analysis_model,
            "provider": analysis_source,
            "provenance": {
                "run_id": args.run_id,
                "current_datetime": args.current_datetime,
                "authorship": "ai-authored" if ai_status == "ai" else "no-ai-fallback" if ai_status == "no-ai" else "unknown",
                "provider": analysis_source,
                "model": args.analysis_model,
                "fallback_reason": args.fallback_reason.strip() or None,
                "attempted_ai_paths": attempted_ai_paths,
            },
        },
        "existing_article": existing_article,
        "validation": {
            "status": args.validation_status,
            "quality_gates": [
                {
                    "name": "analysis_gate",
                    "status": args.validation_status,
                    "source": analysis_source,
                }
            ],
        },
        "promotion": {
            "eligible": eligible,
            "decision": "promote" if eligible else "block",
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
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Publish manifest decision={manifest['promotion']['decision']} path={args.output}")
    if reasons:
        for reason in reasons:
            print(f"- {reason}")
    return 0


def assert_eligible(args: argparse.Namespace) -> int:
    payload = load_json(args.manifest)
    if payload is None:
        raise SystemExit(f"Publish manifest is missing or malformed: {args.manifest}")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(f"Unsupported publish manifest schema: {payload.get('schema_version')!r}")
    analysis = payload.get("analysis")
    ai_status = analysis.get("ai_status") if isinstance(analysis, dict) else None
    promotion_policy = (payload.get("promotion") or {}).get("policy") if isinstance(payload.get("promotion"), dict) else None
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
    promotion = payload.get("promotion")
    if not isinstance(promotion, dict) or promotion.get("eligible") is not True or promotion.get("decision") != "promote":
        reasons = promotion.get("reasons") if isinstance(promotion, dict) else ["missing promotion block"]
        raise SystemExit(f"Manifest blocks promotion: {', '.join(str(reason) for reason in reasons)}")
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict) or not candidate.get("summary_sha256"):
        raise SystemExit("Manifest lacks candidate summary checksum.")
    source_artifacts = payload.get("source_artifacts")
    if not isinstance(source_artifacts, list) or not source_artifacts:
        raise SystemExit("Manifest lacks source artifact provenance.")
    for entry in source_artifacts:
        if not isinstance(entry, dict) or not entry.get("sha256"):
            raise SystemExit("Manifest source artifact is missing a checksum.")
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
