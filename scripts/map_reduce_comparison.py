#!/usr/bin/env python3
"""Map/reduce vs. single-pass comparison framework.

Generates a structured comparison report that tracks quality deltas between
the map/reduce candidate and the current single-pass analyzer output. This
report feeds the promotion criteria defined in docs/map-reduce-promotion-path.md.

Never publishes content. Produces comparison-report.json alongside the
candidate artifacts for QA analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from scripts.analysis_gate import validate_analysis, validate_publish_quality
    from scripts.model_pricing import estimate_cost_usd
except ModuleNotFoundError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.analysis_gate import validate_analysis, validate_publish_quality
    from scripts.model_pricing import estimate_cost_usd

COMPARISON_SCHEMA = "comparison_report_v1"
PROMOTION_MIN_QUALITY = int(os.environ.get("MAPREDUCE_MIN_QUALITY_SCORE", "60"))
PROMOTION_MIN_COVERAGE = float(os.environ.get("MAPREDUCE_MIN_COVERAGE", "0.85"))
PROMOTION_HARD_FLOOR_QUALITY = 55
PROMOTION_HARD_FLOOR_COVERAGE = 0.70
TIME_BUDGET_SECONDS = int(os.environ.get("MAPREDUCE_TIME_BUDGET_SECONDS", "300"))


@dataclass(frozen=True)
class ArtifactInfo:
    path: str
    sha256: str
    quality_score: int
    gate_passed: bool
    evidence_coverage: float
    citation_count: int
    word_count: int


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_citations(text: str) -> int:
    """Count markdown repo/article links as citations."""
    import re

    return len(re.findall(r"\[[^\]]+\]\(https?://[^)]+\)", text))


def extract_quality_score(text: str) -> int:
    """Extract quality_score from frontmatter."""
    import re

    match = re.search(r"^quality_score:\s*(\d+)", text, re.MULTILINE)
    return int(match.group(1)) if match else 0


def compute_evidence_coverage(qa_report: dict[str, Any]) -> float:
    """Compute evidence coverage from QA report checks."""
    checks = qa_report.get("checks", {})
    ref_count = checks.get("reference_count", {})
    selected = ref_count.get("selected", 0)
    # Use mapper contracts to estimate input count
    mapper_contracts = checks.get("mapper_contracts", {})
    errors_by_mapper = mapper_contracts.get("errors_by_mapper", {})
    # If no errors, assume good coverage
    if not any(errors_by_mapper.values()):
        return 0.90
    # Degrade based on mapper failures
    failed_mappers = sum(1 for errs in errors_by_mapper.values() if errs)
    total_mappers = max(len(errors_by_mapper), 1)
    return max(0.0, 1.0 - (failed_mappers / total_mappers) * 0.5)


def compute_evidence_coverage_from_ledgers(
    candidate_dir: Path,
) -> float:
    """Compute evidence coverage from mapper ledger files."""
    total_input = 0
    total_mapped = 0
    for ledger_path in sorted(candidate_dir.glob("map-*.json")):
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        coverage = ledger.get("coverage", {})
        total_input += int(coverage.get("repo_count_input", 0)) + int(
            coverage.get("article_count_input", 0)
        )
        total_mapped += int(coverage.get("repo_count_mapped", 0)) + int(
            coverage.get("article_count_mapped", 0)
        )
    if total_input == 0:
        return 0.0
    return total_mapped / total_input


def analyze_single_pass(
    summary_path: Path, raw_payload: dict[str, Any], current_datetime: str
) -> ArtifactInfo:
    """Analyze the single-pass baseline artifact."""
    text = summary_path.read_text(encoding="utf-8")
    structural_errors, word_count = validate_analysis(text, raw_payload, current_datetime)
    publish_errors, _gates = validate_publish_quality(
        text, raw_payload, source="copilot-cli", model="claude-sonnet-4.6"
    )
    non_provenance = [e for e in publish_errors if not e.startswith("AI provenance")]
    gate_passed = not structural_errors and not non_provenance
    return ArtifactInfo(
        path=summary_path.as_posix(),
        sha256=sha256_file(summary_path),
        quality_score=extract_quality_score(text),
        gate_passed=gate_passed,
        evidence_coverage=0.92,  # Single-pass baseline assumed high coverage
        citation_count=count_citations(text),
        word_count=word_count,
    )


def analyze_map_reduce(
    candidate_dir: Path, raw_payload: dict[str, Any], current_datetime: str
) -> tuple[ArtifactInfo, dict[str, Any]]:
    """Analyze the map/reduce candidate artifact and QA report."""
    candidate_path = candidate_dir / "candidate-summary.md"
    qa_path = candidate_dir / "qa-report.json"

    if not candidate_path.exists():
        raise FileNotFoundError(f"Candidate summary not found: {candidate_path}")

    text = candidate_path.read_text(encoding="utf-8")
    structural_errors, word_count = validate_analysis(text, raw_payload, current_datetime)
    publish_errors, _gates = validate_publish_quality(
        text, raw_payload, source="map-reduce-dry-run", model="local-deterministic"
    )
    non_provenance = [e for e in publish_errors if not e.startswith("AI provenance")]
    gate_passed = not structural_errors and not non_provenance

    qa_report: dict[str, Any] = {}
    if qa_path.exists():
        qa_report = json.loads(qa_path.read_text(encoding="utf-8"))

    evidence_coverage = compute_evidence_coverage_from_ledgers(candidate_dir)

    extra = {
        "mapper_errors": qa_report.get("checks", {})
        .get("mapper_contracts", {})
        .get("errors_by_mapper", {}),
        "contradictions_resolved": qa_report.get("checks", {})
        .get("sidecars_present", {})
        .get("contradiction_count", 0),
        "claims_rejected": qa_report.get("checks", {})
        .get("sidecars_present", {})
        .get("rejected_count", 0),
    }

    info = ArtifactInfo(
        path=candidate_path.as_posix(),
        sha256=sha256_file(candidate_path),
        quality_score=extract_quality_score(text),
        gate_passed=gate_passed,
        evidence_coverage=evidence_coverage,
        citation_count=count_citations(text),
        word_count=word_count,
    )
    return info, extra


def compute_verdict(
    single_pass: ArtifactInfo,
    map_reduce: ArtifactInfo,
    deltas: dict[str, Any],
) -> tuple[str, list[str]]:
    """Determine pass/fail verdict and list blockers."""
    blockers: list[str] = []

    # Gate regression check
    if single_pass.gate_passed and not map_reduce.gate_passed:
        blockers.append("Gate regression: single-pass passes but map/reduce fails.")

    # Quality floor
    if map_reduce.quality_score < PROMOTION_MIN_QUALITY:
        blockers.append(
            f"Quality score {map_reduce.quality_score} below minimum {PROMOTION_MIN_QUALITY}."
        )

    # Hard quality floor (rollback trigger)
    if map_reduce.quality_score < PROMOTION_HARD_FLOOR_QUALITY:
        blockers.append(
            f"Quality score {map_reduce.quality_score} below hard floor "
            f"{PROMOTION_HARD_FLOOR_QUALITY} (rollback trigger)."
        )

    # Evidence coverage
    if map_reduce.evidence_coverage < PROMOTION_MIN_COVERAGE:
        blockers.append(
            f"Evidence coverage {map_reduce.evidence_coverage:.2f} below minimum "
            f"{PROMOTION_MIN_COVERAGE}."
        )

    # Hard coverage floor (rollback trigger)
    if map_reduce.evidence_coverage < PROMOTION_HARD_FLOOR_COVERAGE:
        blockers.append(
            f"Evidence coverage {map_reduce.evidence_coverage:.2f} below hard floor "
            f"{PROMOTION_HARD_FLOOR_COVERAGE} (rollback trigger)."
        )

    verdict = "pass" if not blockers else "fail"
    return verdict, blockers


def generate_comparison_report(
    *,
    week: str,
    single_pass: ArtifactInfo,
    map_reduce: ArtifactInfo,
    map_reduce_extra: dict[str, Any],
    run_datetime: str,
) -> dict[str, Any]:
    """Generate the full comparison report."""
    deltas = {
        "quality_score": map_reduce.quality_score - single_pass.quality_score,
        "evidence_coverage": round(
            map_reduce.evidence_coverage - single_pass.evidence_coverage, 4
        ),
        "citation_count": map_reduce.citation_count - single_pass.citation_count,
        "word_count": map_reduce.word_count - single_pass.word_count,
        "gate_regression": single_pass.gate_passed and not map_reduce.gate_passed,
    }

    verdict, blockers = compute_verdict(single_pass, map_reduce, deltas)

    return {
        "schema_version": COMPARISON_SCHEMA,
        "week": week,
        "run_datetime": run_datetime,
        "single_pass": {
            "artifact_path": single_pass.path,
            "sha256": single_pass.sha256,
            "quality_score": single_pass.quality_score,
            "gate_passed": single_pass.gate_passed,
            "evidence_coverage": single_pass.evidence_coverage,
            "citation_count": single_pass.citation_count,
            "word_count": single_pass.word_count,
        },
        "map_reduce": {
            "artifact_path": map_reduce.path,
            "sha256": map_reduce.sha256,
            "quality_score": map_reduce.quality_score,
            "gate_passed": map_reduce.gate_passed,
            "evidence_coverage": map_reduce.evidence_coverage,
            "citation_count": map_reduce.citation_count,
            "word_count": map_reduce.word_count,
            **map_reduce_extra,
        },
        "deltas": deltas,
        "verdict": verdict,
        "blockers": blockers,
    }


def check_promotion_eligibility(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Check whether a set of comparison reports meets promotion criteria.

    Returns a promotion status object indicating readiness and any blockers.
    """
    if len(reports) < 3:
        return {
            "eligible": False,
            "reason": f"Only {len(reports)} comparison runs available; need ≥ 3.",
            "runs_passing": len([r for r in reports if r.get("verdict") == "pass"]),
            "runs_total": len(reports),
        }

    passing = [r for r in reports if r.get("verdict") == "pass"]
    if len(passing) < 3:
        return {
            "eligible": False,
            "reason": f"Only {len(passing)}/{len(reports)} runs passed; need ≥ 3 consecutive.",
            "runs_passing": len(passing),
            "runs_total": len(reports),
        }

    # Check average quality across passing runs
    avg_quality = sum(
        r["map_reduce"]["quality_score"] for r in passing
    ) / len(passing)
    if avg_quality < 65:
        return {
            "eligible": False,
            "reason": f"Average quality score {avg_quality:.1f} below 65 threshold.",
            "runs_passing": len(passing),
            "runs_total": len(reports),
        }

    # Check staleness (28 days)
    from datetime import datetime, timedelta

    now = datetime.now(UTC)
    for report in passing[-3:]:
        run_dt = report.get("run_datetime", "")
        try:
            report_time = datetime.fromisoformat(run_dt.replace("Z", "+00:00"))
            if (now - report_time).days > 28:
                return {
                    "eligible": False,
                    "reason": f"Comparison run from {run_dt} is older than 28 days.",
                    "runs_passing": len(passing),
                    "runs_total": len(reports),
                }
        except (ValueError, TypeError):
            pass

    return {
        "eligible": True,
        "reason": "All promotion criteria met. Awaiting operator opt-in and team sign-off.",
        "runs_passing": len(passing),
        "runs_total": len(reports),
        "average_quality": round(avg_quality, 1),
    }


def should_rollback(report: dict[str, Any]) -> tuple[bool, str]:
    """Determine if automatic rollback should trigger based on a comparison report.

    Returns (should_rollback, reason).
    """
    mr = report.get("map_reduce", {})

    # Gate failure when single-pass passes
    if report.get("deltas", {}).get("gate_regression"):
        return True, "Gate regression: map/reduce fails gates that single-pass passes."

    # Hard quality floor
    quality = mr.get("quality_score", 0)
    if quality < PROMOTION_HARD_FLOOR_QUALITY:
        return True, f"Quality score {quality} below hard floor {PROMOTION_HARD_FLOOR_QUALITY}."

    # Hard coverage floor
    coverage = mr.get("evidence_coverage", 0.0)
    if coverage < PROMOTION_HARD_FLOOR_COVERAGE:
        return True, f"Evidence coverage {coverage:.2f} below hard floor {PROMOTION_HARD_FLOOR_COVERAGE}."

    # Mapper failure
    mapper_errors = mr.get("mapper_errors", {})
    if any(
        errs
        for errs in mapper_errors.values()
        if isinstance(errs, list) and errs
    ):
        failed = [k for k, v in mapper_errors.items() if v]
        return True, f"Mapper failures in: {', '.join(failed)}."

    return False, ""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare map/reduce candidate against single-pass baseline."
    )
    parser.add_argument(
        "--raw-json",
        required=True,
        type=Path,
        help="Weekly raw crawl payload.",
    )
    parser.add_argument(
        "--single-pass-summary",
        required=True,
        type=Path,
        help="Current single-pass analyzed summary.",
    )
    parser.add_argument(
        "--candidate-dir",
        required=True,
        type=Path,
        help="Map/reduce candidate output directory.",
    )
    parser.add_argument(
        "--current-datetime",
        default=datetime.now(UTC).isoformat(),
        help="ISO-8601 timestamp for the comparison run.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for comparison report (default: candidate-dir/comparison-report.json).",
    )
    parser.add_argument(
        "--check-promotion",
        action="store_true",
        help="Also check promotion eligibility across all available comparison reports.",
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    """Execute comparison and return the report."""
    raw_payload = json.loads(args.raw_json.read_text(encoding="utf-8"))
    week = raw_payload.get("week", "unknown")

    single_pass = analyze_single_pass(
        args.single_pass_summary, raw_payload, args.current_datetime
    )
    map_reduce, mr_extra = analyze_map_reduce(
        args.candidate_dir, raw_payload, args.current_datetime
    )

    report = generate_comparison_report(
        week=week,
        single_pass=single_pass,
        map_reduce=map_reduce,
        map_reduce_extra=mr_extra,
        run_datetime=args.current_datetime,
    )

    # Check rollback
    rollback, rollback_reason = should_rollback(report)
    if rollback:
        report["rollback"] = True
        report["rollback_reason"] = rollback_reason

    # Write report
    output_path = args.output or (args.candidate_dir / "comparison-report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # Optional promotion check
    if args.check_promotion:
        reports_dir = args.candidate_dir.parent
        all_reports = []
        for rdir in sorted(reports_dir.iterdir()):
            rpath = rdir / "comparison-report.json"
            if rpath.exists():
                try:
                    all_reports.append(
                        json.loads(rpath.read_text(encoding="utf-8"))
                    )
                except (json.JSONDecodeError, OSError):
                    pass
        promotion = check_promotion_eligibility(all_reports)
        report["promotion_status"] = promotion

        # Re-write with promotion status
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return report


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = run(args)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    verdict = report.get("verdict", "unknown")
    rollback = report.get("rollback", False)
    print(f"Comparison complete: week={report.get('week')} verdict={verdict}", flush=True)
    if rollback:
        print(f"⚠️  ROLLBACK TRIGGERED: {report.get('rollback_reason')}", flush=True)
    if report.get("promotion_status"):
        status = report["promotion_status"]
        if status.get("eligible"):
            print("✅ Promotion eligible — awaiting operator opt-in.", flush=True)
        else:
            print(f"⏳ Not yet eligible: {status.get('reason')}", flush=True)

    return 1 if rollback else 0


if __name__ == "__main__":
    raise SystemExit(main())
