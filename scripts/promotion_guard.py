from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


class PromotionBlocked(ValueError):
    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


WEEK_PATTERN = re.compile(r"^(?P<year>\d{4})-W(?P<week>\d{2})$")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote an eligible weekly analysis candidate.")
    parser.add_argument("--manifest", required=True, type=Path, help="Publish eligibility manifest path.")
    parser.add_argument("--root", default=".", type=Path, help="Repository/workspace root.")
    return parser.parse_args(argv)


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PromotionBlocked([f"Missing publish eligibility manifest: {path}"]) from exc
    except json.JSONDecodeError as exc:
        raise PromotionBlocked([f"Malformed publish eligibility manifest: {exc.msg}"]) from exc

    if not isinstance(manifest, dict):
        raise PromotionBlocked(["Publish eligibility manifest must be a JSON object."])
    return manifest


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    try:
        return datetime.fromisoformat(candidate).astimezone(UTC).date()
    except ValueError:
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None


def _resolve_under_root(root: Path, value: Any, field: str, reasons: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        reasons.append(f"{field} is required.")
        return None
    path = Path(value)
    if path.is_absolute():
        reasons.append(f"{field} must be relative to the repository root.")
        return None
    resolved_root = root.resolve()
    resolved_path = (resolved_root / path).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        reasons.append(f"{field} must stay under the repository root.")
        return None
    return resolved_path


def _manifest_candidate_path(manifest: dict[str, Any], legacy_key: str, nested_key: str) -> Any:
    candidate = manifest.get("candidate")
    if isinstance(candidate, dict) and nested_key in candidate:
        return candidate.get(nested_key)
    return manifest.get(legacy_key)


def _manifest_promotion_eligible(manifest: dict[str, Any]) -> bool:
    promotion = manifest.get("promotion")
    if isinstance(promotion, dict):
        return promotion.get("eligible") is True and promotion.get("decision") == "promote"
    return manifest.get("promotion_eligible") is True


def _manifest_ai_provenance(manifest: dict[str, Any]) -> dict[str, Any] | None:
    analysis = manifest.get("analysis")
    if isinstance(analysis, dict):
        return {
            "source": analysis.get("source"),
            "model": analysis.get("model"),
            "degraded": analysis.get("ai_status") != "ai" or analysis.get("model_status") != "available",
        }
    ai_provenance = manifest.get("ai_provenance")
    return ai_provenance if isinstance(ai_provenance, dict) else None


def _manifest_gate_results(manifest: dict[str, Any]) -> dict[str, bool] | None:
    gate_results = manifest.get("gate_results")
    if isinstance(gate_results, dict):
        return {str(key): value is True for key, value in gate_results.items()}
    validation = manifest.get("validation")
    gate_report = validation.get("gate_report") if isinstance(validation, dict) else None
    gates = gate_report.get("gates") if isinstance(gate_report, dict) else None
    if isinstance(gates, dict):
        return {str(key): isinstance(value, dict) and value.get("passed") is True for key, value in gates.items()}
    return None


def _manifest_gate_report(manifest: dict[str, Any]) -> dict[str, Any] | None:
    validation = manifest.get("validation")
    gate_report = validation.get("gate_report") if isinstance(validation, dict) else None
    return gate_report if isinstance(gate_report, dict) else None


def _manifest_source_artifacts(manifest: dict[str, Any]) -> list[Any] | None:
    artifacts = manifest.get("source_artifacts")
    return artifacts if isinstance(artifacts, list) else None


def _validate_manifest(manifest: dict[str, Any], root: Path, manifest_path: Path) -> tuple[str, Path, Path, list[str]]:
    reasons: list[str] = []

    if manifest.get("schema_version") != "publish_eligibility_v1":
        reasons.append("schema_version must be publish_eligibility_v1.")

    week = manifest.get("week")
    if not isinstance(week, str) or not week.strip():
        reasons.append("week is required.")
        week = "unknown-week"
    elif not WEEK_PATTERN.fullmatch(week):
        reasons.append("week must use YYYY-WNN format.")

    if not _manifest_promotion_eligible(manifest):
        reasons.append("promotion_eligible must be true.")

    candidate_summary = _resolve_under_root(root, _manifest_candidate_path(manifest, "candidate_summary_path", "summary_path"), "candidate_summary_path", reasons)
    candidate_content = _resolve_under_root(root, _manifest_candidate_path(manifest, "candidate_content_path", "content_path"), "candidate_content_path", reasons)

    ai_provenance = _manifest_ai_provenance(manifest)
    if not isinstance(ai_provenance, dict):
        reasons.append("ai_provenance is required.")
    else:
        source = ai_provenance.get("source")
        if source in {None, "", "no-ai"}:
            reasons.append("AI-authored provenance is required for normal promotion.")
        if ai_provenance.get("degraded") is True:
            reasons.append("degraded AI provenance is not eligible for normal promotion.")

    gate_report = _manifest_gate_report(manifest)
    if gate_report is not None and gate_report.get("passed") is not True:
        reasons.append("validation.gate_report.passed must be true.")

    gate_results = _manifest_gate_results(manifest)
    if not isinstance(gate_results, dict):
        reasons.append("gate_results is required.")
    else:
        for gate in ("structural_schema", "ai_provenance", "evidence_citation", "editorial_quality"):
            if gate not in gate_results:
                reasons.append(f"gate_results must include passing {gate}.")
            elif gate_results.get(gate) is not True:
                reasons.append(f"{gate} must pass.")
        legacy_gates = ("analysis_gate", "editorial_quality_gate", "evidence_freshness_gate")
        if any(gate in gate_results for gate in legacy_gates):
            for gate in legacy_gates:
                if gate_results.get(gate) is not True:
                    reasons.append(f"{gate} must pass.")

    run_date = _parse_date(manifest.get("run_started_at"))
    if run_date is None:
        reasons.append("run_started_at must be an ISO date or timestamp.")

    source_artifacts = _manifest_source_artifacts(manifest)
    if not isinstance(source_artifacts, list) or not source_artifacts:
        reasons.append("source_artifacts must include at least one artifact.")
    else:
        for index, artifact in enumerate(source_artifacts, start=1):
            prefix = f"source_artifacts[{index}]"
            if not isinstance(artifact, dict):
                reasons.append(f"{prefix} must be an object.")
                continue
            freshness = artifact.get("freshness")
            if artifact.get("stale") is True or (isinstance(freshness, dict) and freshness.get("status") == "stale"):
                reasons.append(f"{prefix} is stale.")
            generated_date = _parse_date(artifact.get("generated_at") or artifact.get("crawled_at"))
            if generated_date is None:
                reasons.append(f"{prefix}.generated_at must be an ISO date or timestamp.")
            elif run_date is not None and generated_date != run_date and artifact.get("reused_same_day") is not True:
                reasons.append(f"{prefix} is not from the current run date or marked as same-day reuse.")
            artifact_path = _resolve_under_root(root, artifact.get("path"), f"{prefix}.path", reasons)
            if artifact_path is not None and not artifact_path.exists():
                reasons.append(f"{prefix}.path does not exist: {artifact.get('path')}")

    if candidate_summary is not None and not candidate_summary.exists():
        reasons.append(f"candidate_summary_path does not exist: {manifest.get('candidate_summary_path')}")
    if candidate_content is not None and not candidate_content.exists():
        reasons.append(f"candidate_content_path does not exist: {manifest.get('candidate_content_path')}")

    try:
        manifest_relative = manifest_path.resolve().relative_to(root.resolve())
    except ValueError:
        reasons.append("Publish manifest must be under the repository root.")
        manifest_relative = Path()
    if manifest_relative.parts[:2] != ("data", "staging"):
        reasons.append("Publish manifest must live under data/staging/.")

    return str(week), candidate_summary or root, candidate_content or root, reasons


def _write_diagnostic(root: Path, week: str, manifest: dict[str, Any] | None, reasons: list[str]) -> Path:
    diagnostic_dir = root / "data" / "diagnostics" / "promotion"
    diagnostic_dir.mkdir(parents=True, exist_ok=True)
    diagnostic_path = diagnostic_dir / f"{week}-blocked.json"
    diagnostic_path.write_text(
        json.dumps({"week": week, "promotion": "blocked", "reasons": reasons, "manifest": manifest}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return diagnostic_path


def promote_candidate(manifest_path: Path, *, root: Path | None = None) -> tuple[Path, Path]:
    workspace = (root or Path.cwd()).resolve()
    resolved_manifest_path = manifest_path if manifest_path.is_absolute() else workspace / manifest_path
    manifest: dict[str, Any] | None = None
    week = "unknown-week"

    try:
        manifest = _load_manifest(resolved_manifest_path)
        week, candidate_summary, candidate_content, reasons = _validate_manifest(manifest, workspace, resolved_manifest_path)
        if reasons:
            raise PromotionBlocked(reasons)
    except PromotionBlocked as exc:
        _write_diagnostic(workspace, week, manifest, exc.reasons)
        raise

    canonical_summary = workspace / "data" / "analyzed" / f"{week}-summary.md"
    match = WEEK_PATTERN.fullmatch(week)
    if match is None:
        raise PromotionBlocked(["week must use YYYY-WNN format."])
    year, week_number = match.group("year"), match.group("week")
    canonical_content = workspace / "content" / "weekly" / year / f"W{week_number}.md"
    canonical_summary.parent.mkdir(parents=True, exist_ok=True)
    canonical_content.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(candidate_summary, canonical_summary)
    shutil.copyfile(candidate_content, canonical_content)
    return canonical_summary, canonical_content


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary_path, content_path = promote_candidate(args.manifest, root=args.root)
    except PromotionBlocked as exc:
        for reason in exc.reasons:
            print(f"::error::{reason}")
        return 1
    print(f"Promoted {summary_path} and {content_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
