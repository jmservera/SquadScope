#!/usr/bin/env python3
"""Deterministic map/reduce analysis dry-run scaffolding.

This module intentionally performs no live AI calls and never writes to published
content paths. It emits candidate-only artifacts under an explicit output
folder so the contracts can be validated before any future promotion work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.analysis_gate import validate_analysis, validate_publish_quality
    from scripts.analyze_fallback import find_previous_summary
    from scripts.model_pricing import estimate_cost_usd
    from scripts.observability_metrics import (
        DEFAULT_OBSERVABILITY_DIR,
        METRICS_SCHEMA_VERSION,
        AnalysisMetrics,
        MapReduceMetrics,
        ObservabilityLedger,
        emit_ledger,
    )
    from scripts.render_press_context import estimate_tokens
    from scripts.sanitize_repo_content import sanitize_repo_payload
except ModuleNotFoundError:  # pragma: no cover - script execution path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.analysis_gate import validate_analysis, validate_publish_quality
    from scripts.analyze_fallback import find_previous_summary
    from scripts.model_pricing import estimate_cost_usd
    from scripts.observability_metrics import (
        DEFAULT_OBSERVABILITY_DIR,
        METRICS_SCHEMA_VERSION,
        AnalysisMetrics,
        MapReduceMetrics,
        ObservabilityLedger,
        emit_ledger,
    )
    from scripts.render_press_context import estimate_tokens
    from scripts.sanitize_repo_content import sanitize_repo_payload

ROOT = Path(__file__).resolve().parent.parent
MAP_SCHEMA = "analysis_map_v1"
PLAN_SCHEMA = "analysis_editorial_plan_v1"
QA_SCHEMA = "analysis_map_reduce_qa_v1"
CANDIDATE_DISCLAIMER = "Map/reduce dry-run candidate only; not publish eligible."
MAPPER_IDS = ("new_repos", "trending_repos", "press_correlations", "prior_continuity")
TOKEN_ESTIMATE_KEY = "_".join(("token", "estimate"))
SECTION_ORDER = [
    "This Week's Trends",
    "Where Industry Meets Code",
    "Signal & Noise",
    "Blind Spots",
    "The Week Ahead",
]


@dataclass(frozen=True)
class ArtifactRef:
    path: str
    sha256: str | None
    bytes: int


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create deterministic candidate-only map/reduce analysis artifacts."
    )
    parser.add_argument(
        "--raw-json", required=True, type=Path, help="Canonical weekly raw GitHub crawl payload."
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Candidate artifact output directory."
    )
    parser.add_argument(
        "--current-datetime", required=True, help="ISO-8601 timestamp for the dry run."
    )
    parser.add_argument("--run-id", default="local", help="Stable run id to include in contracts.")
    parser.add_argument(
        "--press-context", type=Path, help="Rendered press context markdown, if available."
    )
    parser.add_argument("--analyzed-dir", type=Path, default=ROOT / "data" / "analyzed")
    parser.add_argument(
        "--baseline-summary",
        type=Path,
        help="Optional current single-pass summary for QA comparison.",
    )
    parser.add_argument("--max-repos-per-ledger", type=int, default=10)
    parser.add_argument("--analysis-source", default="map-reduce-dry-run")
    parser.add_argument("--analysis-model", default="local-deterministic")
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload must be an object: {path}")
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(payload), encoding="utf-8")


def metric_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    return estimate_cost_usd(model, input_tokens, output_tokens) or 0.0


def file_ref(path: Path | None) -> ArtifactRef | None:
    if path is None or not path.exists() or not path.is_file():
        return None
    data = path.read_bytes()
    return ArtifactRef(path=path.as_posix(), sha256=sha256_bytes(data), bytes=len(data))


def collect_gate_failure_reasons(qa_report: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    checks = qa_report.get("checks", {}) if isinstance(qa_report.get("checks"), dict) else {}
    mapper_contracts = checks.get("mapper_contracts", {})
    if isinstance(mapper_contracts, dict):
        errors_by_mapper = mapper_contracts.get("errors_by_mapper", {})
        if isinstance(errors_by_mapper, dict):
            for mapper, errors in sorted(errors_by_mapper.items()):
                if isinstance(errors, list):
                    reasons.extend(f"{mapper}: {error}" for error in errors)
    for key in (
        "structural_analysis_gate",
        "evidence_and_editorial_gates",
        "publish_provenance_gate",
    ):
        check = checks.get(key, {})
        if (
            isinstance(check, dict)
            and check.get("expected_failure") is not True
            and isinstance(check.get("errors"), list)
        ):
            reasons.extend(str(error) for error in check["errors"] if error)
    if isinstance(qa_report.get("regressions"), list):
        reasons.extend(str(error) for error in qa_report["regressions"] if error)
    sidecars = checks.get("sidecars_present", {})
    if isinstance(sidecars, dict) and sidecars.get("passed") is False:
        reasons.append("sidecars_present failed")
    seen: set[str] = set()
    ordered: list[str] = []
    for reason in reasons:
        normalized = reason.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)
    return ordered


def normalize_repo_name(repo: dict[str, Any]) -> str:
    full_name = str(repo.get("full_name") or "").strip()
    if full_name:
        return full_name
    owner = str(repo.get("owner") or "").strip()
    name = str(repo.get("name") or "").strip()
    return f"{owner}/{name}" if owner and name else name


def repo_url(repo: dict[str, Any], full_name: str) -> str:
    return str(repo.get("url") or repo.get("html_url") or f"https://github.com/{full_name}")


def repo_description(repo: dict[str, Any]) -> str:
    desc = str(repo.get("description") or "No description provided").strip()
    return re.sub(r"\s+", " ", desc)[:220]


def repo_claim_key(repo: dict[str, Any], *, mapper: str) -> str:
    full_name = normalize_repo_name(repo)
    base = f"{mapper}:{full_name}:{repo.get('stars', 0)}:{repo.get('stars_gained', repo.get('gained', 0))}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]


def sorted_repos(repos: list[dict[str, Any]], *, mode: str) -> list[dict[str, Any]]:
    if mode == "trending":
        return sorted(
            repos,
            key=lambda r: (
                int(r.get("stars_gained") or r.get("gained") or 0),
                int(r.get("stars") or 0),
                normalize_repo_name(r),
            ),
            reverse=True,
        )
    return sorted(
        repos, key=lambda r: (int(r.get("stars") or 0), normalize_repo_name(r)), reverse=True
    )


def coverage_for_repos(
    repos: list[dict[str, Any]], input_count: int, *, omitted_reason: str
) -> dict[str, Any]:
    seen = [normalize_repo_name(repo) for repo in repos if normalize_repo_name(repo)]
    omitted = max(0, input_count - len(seen))
    return {
        "repo_ids_seen": seen,
        "article_urls_seen": [],
        "repo_count_input": input_count,
        "repo_count_mapped": len(seen),
        "article_count_input": 0,
        "article_count_mapped": 0,
        "excluded_reason_counts": {omitted_reason: omitted} if omitted else {},
    }


def make_repo_finding(
    repo: dict[str, Any], *, mapper: str, category: str, role: str
) -> dict[str, Any]:
    full_name = normalize_repo_name(repo)
    stars = int(repo.get("stars") or 0)
    gained = int(repo.get("stars_gained") or repo.get("gained") or 0)
    language = repo.get("language") or "unknown language"
    topics = repo.get("topics") if isinstance(repo.get("topics"), list) else []
    topic_note = f" with topics {', '.join(str(t) for t in topics[:3])}" if topics else ""
    metric_note = f"{stars:,} stars" + (f", {gained:,} gained" if gained else "")
    claim = f"{full_name} is a {role} {language} signal this week ({metric_note}){topic_note}: {repo_description(repo)}"
    confidence = 0.74 if mapper == "trending_repos" and gained else 0.68
    return {
        "claim_id": f"{mapper}-{repo_claim_key(repo, mapper=mapper)}",
        "claim": claim,
        "category": category,
        "source_type": "github",
        "evidence_refs": [
            {
                "type": "repo",
                "ref": full_name,
                "url": repo_url(repo, full_name),
                "full_name": full_name,
                "description": repo.get("description"),
                "language": repo.get("language"),
                "topics": topics,
                "stars": stars,
                "stars_gained": gained,
                "created_at": repo.get("created_at"),
                "role": "anchor",
                "evidence_note": f"Crawler metrics show {metric_note}.",
            }
        ],
        "repo_full_name": full_name,
        "news_url": None,
        "confidence": confidence,
        "contra_refs": [],
        "uncertainties": [] if gained else ["stars_gained unavailable or zero in raw payload"],
        "quality_flags": ["dry_run_local_mapper"],
    }


def base_map_payload(
    *,
    run_id: str,
    week: str,
    shard_id: str,
    input_refs: list[str],
    repo_count: int,
    article_count: int,
    token_estimate: int,
) -> dict[str, Any]:
    return {
        "schema_version": MAP_SCHEMA,
        "run_id": run_id,
        "week": week,
        "shard_id": f"signal-type:{shard_id}",
        "slice": {
            "strategy": "signal_type",
            "input_refs": input_refs,
            "input_token_estimate": token_estimate,
            "repo_count": repo_count,
            "article_count": article_count,
        },
        "coverage": {},
        "findings": [],
        "citations": [],
        "reference_candidates": {"notable_projects": [], "press_articles": []},
        TOKEN_ESTIMATE_KEY: 0,
        "model": "none",
        "status": "success",
        "errors": [],
        "provenance": {},
    }


def map_repositories(
    *,
    run_id: str,
    week: str,
    raw_path: Path,
    raw_ref: ArtifactRef,
    shard_id: str,
    repos: list[dict[str, Any]],
    mode: str,
    max_repos: int,
) -> dict[str, Any]:
    selected = sorted_repos(repos, mode=mode)[:max_repos]
    payload = base_map_payload(
        run_id=run_id,
        week=week,
        shard_id=shard_id,
        input_refs=[f"{raw_path.as_posix()}#{shard_id}[0:{len(repos)}]"],
        repo_count=len(repos),
        article_count=0,
        token_estimate=estimate_tokens(stable_json(repos)),
    )
    category = "trend" if shard_id == "new_repos" else "signal"
    role = "new-repository" if shard_id == "new_repos" else "momentum"
    findings = [
        make_repo_finding(repo, mapper=shard_id, category=category, role=role) for repo in selected
    ]
    payload["findings"] = findings
    payload["coverage"] = coverage_for_repos(
        selected, len(repos), omitted_reason="outside_dry_run_top_repo_limit"
    )
    payload["citations"] = [
        {"type": "repo", "url": item["evidence_refs"][0]["url"], "title": item["repo_full_name"]}
        for item in findings
    ]
    payload["reference_candidates"] = {
        "notable_projects": [item["repo_full_name"] for item in findings],
        "press_articles": [],
    }
    payload["token_estimate"] = estimate_tokens(stable_json(payload))
    payload["provenance"] = {"raw_json": asdict(raw_ref), "deterministic_mapper": True}
    return payload


def extract_press_articles(press_context: str) -> list[dict[str, str]]:
    urls = []
    for match in re.finditer(r"https?://[^\s)\]]+", press_context):
        url = match.group(0).rstrip(".,")
        if url not in urls:
            urls.append(url)
    articles: list[dict[str, str]] = []
    lines = [line.strip(" -*") for line in press_context.splitlines() if line.strip()]
    for url in urls[:10]:
        title = next((line[:120] for line in lines if url in line), url)
        articles.append({"url": url, "title": title})
    return articles


def map_press(
    *,
    run_id: str,
    week: str,
    press_path: Path | None,
    press_ref: ArtifactRef | None,
    raw_ref: ArtifactRef,
) -> dict[str, Any]:
    content = press_path.read_text(encoding="utf-8") if press_path and press_path.exists() else ""
    articles = extract_press_articles(content)
    payload = base_map_payload(
        run_id=run_id,
        week=week,
        shard_id="press_correlations",
        input_refs=[press_path.as_posix() if press_path else "press_context:none"],
        repo_count=0,
        article_count=len(articles),
        token_estimate=estimate_tokens(content),
    )
    findings = []
    for index, article in enumerate(articles[:5], start=1):
        claim_id = hashlib.sha256(f"press:{article['url']}".encode("utf-8")).hexdigest()[:12]
        findings.append(
            {
                "claim_id": f"press_correlations-{claim_id}",
                "claim": f"Retained press context cites {article['title']} as industry evidence to compare against repository activity.",
                "category": "press_correlation",
                "source_type": "news",
                "evidence_refs": [
                    {
                        "type": "article",
                        "ref": article["url"],
                        "url": article["url"],
                        "role": "supporting",
                        "evidence_note": "URL was retained in rendered press context.",
                    }
                ],
                "repo_full_name": None,
                "news_url": article["url"],
                "confidence": 0.66,
                "contra_refs": [],
                "uncertainties": ["dry-run mapper does not infer unstated press sentiment"],
                "quality_flags": ["dry_run_local_mapper"],
            }
        )
    if not findings:
        payload["status"] = "partial"
        payload["errors"] = ["No press URLs were available; mapper emitted coverage-only ledger."]
    payload["findings"] = findings
    payload["coverage"] = {
        "repo_ids_seen": [],
        "article_urls_seen": [article["url"] for article in articles],
        "repo_count_input": 0,
        "repo_count_mapped": 0,
        "article_count_input": len(articles),
        "article_count_mapped": len(articles[:5]),
        "excluded_reason_counts": {"outside_dry_run_article_limit": max(0, len(articles) - 5)}
        if len(articles) > 5
        else {},
    }
    payload["citations"] = [
        {"type": "article", "url": item["news_url"], "title": item["claim"][:80]}
        for item in findings
    ]
    payload["reference_candidates"] = {
        "notable_projects": [],
        "press_articles": [item["news_url"] for item in findings],
    }
    payload["token_estimate"] = estimate_tokens(stable_json(payload))
    payload["provenance"] = {
        "raw_json": asdict(raw_ref),
        "press_context": asdict(press_ref) if press_ref else None,
        "deterministic_mapper": True,
    }
    return payload


def map_prior(
    *,
    run_id: str,
    week: str,
    previous_summary: Path | None,
    previous_ref: ArtifactRef | None,
    raw_ref: ArtifactRef,
) -> dict[str, Any]:
    content = (
        previous_summary.read_text(encoding="utf-8")
        if previous_summary and previous_summary.exists()
        else ""
    )
    payload = base_map_payload(
        run_id=run_id,
        week=week,
        shard_id="prior_continuity",
        input_refs=[previous_summary.as_posix() if previous_summary else "prior_summary:none"],
        repo_count=0,
        article_count=0,
        token_estimate=estimate_tokens(content),
    )
    finding = {
        "claim_id": f"prior_continuity-{hashlib.sha256((previous_summary.as_posix() if previous_summary else 'none').encode()).hexdigest()[:12]}",
        "claim": (
            "Prior weekly analysis is available for continuity checks; reducer should compare carried-forward claims against this week's evidence."
            if content
            else "No prior weekly analysis was available, so continuity claims should be treated as open blind spots."
        ),
        "category": "continuity",
        "source_type": "prior_summary",
        "evidence_refs": [
            {
                "type": "prior_summary",
                "ref": previous_summary.as_posix() if previous_summary else "none",
                "url": previous_summary.as_posix() if previous_summary else "none",
                "role": "supporting",
                "evidence_note": "Deterministic local continuity marker.",
            }
        ],
        "repo_full_name": None,
        "news_url": None,
        "confidence": 0.55 if content else 0.35,
        "contra_refs": [],
        "uncertainties": [] if content else ["no prior summary artifact found"],
        "quality_flags": ["dry_run_local_mapper"],
    }
    payload["findings"] = [finding]
    payload["coverage"] = {
        "repo_ids_seen": [],
        "article_urls_seen": [],
        "repo_count_input": 0,
        "repo_count_mapped": 0,
        "article_count_input": 0,
        "article_count_mapped": 0,
        "excluded_reason_counts": {},
        "prior_summary_present": bool(content),
    }
    payload["citations"] = [
        {
            "type": "prior_summary",
            "url": finding["evidence_refs"][0]["url"],
            "title": "prior weekly summary",
        }
    ]
    payload["reference_candidates"] = {"notable_projects": [], "press_articles": []}
    payload["token_estimate"] = estimate_tokens(stable_json(payload))
    payload["provenance"] = {
        "raw_json": asdict(raw_ref),
        "prior_summary": asdict(previous_ref) if previous_ref else None,
        "deterministic_mapper": True,
    }
    return payload


def validate_map(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != MAP_SCHEMA:
        errors.append("mapper schema_version mismatch")
    for field in (
        "run_id",
        "week",
        "shard_id",
        "slice",
        "coverage",
        "findings",
        "citations",
        "reference_candidates",
        "provenance",
    ):
        if field not in payload:
            errors.append(f"mapper missing {field}")
    if "findings" in payload and not isinstance(payload.get("findings"), list):
        errors.append("findings must be a list")
    findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"finding {index} must be an object")
            continue
        for field in (
            "claim_id",
            "claim",
            "category",
            "source_type",
            "evidence_refs",
            "confidence",
            "contra_refs",
            "uncertainties",
        ):
            if field not in finding:
                errors.append(f"finding {index} missing {field}")
        refs = finding.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"finding {index} has no evidence refs")
        else:
            for ref in refs:
                if (
                    not isinstance(ref, dict)
                    or not ref.get("type")
                    or not ref.get("ref")
                    or not ref.get("url")
                ):
                    errors.append(f"finding {index} has malformed evidence ref")
        confidence = finding.get("confidence")
        if not isinstance(confidence, (int, float)) or not (0 <= float(confidence) <= 1):
            errors.append(f"finding {index} confidence out of range")
        if "contra_refs" in finding and not isinstance(finding.get("contra_refs"), list):
            errors.append(f"finding {index} contra_refs must be a list")
    coverage = payload.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage must be an object")
    else:
        for key in ("repo_ids_seen", "article_urls_seen", "excluded_reason_counts"):
            if key not in coverage:
                errors.append(f"coverage missing {key}")
        if "repo_ids_seen" in coverage and not isinstance(coverage.get("repo_ids_seen"), list):
            errors.append("coverage repo_ids_seen must be a list")
        if "article_urls_seen" in coverage and not isinstance(
            coverage.get("article_urls_seen"), list
        ):
            errors.append("coverage article_urls_seen must be a list")
        excluded = coverage.get("excluded_reason_counts")
        if "excluded_reason_counts" in coverage and not isinstance(excluded, dict):
            errors.append("coverage excluded_reason_counts must be an object")
        elif isinstance(excluded, dict):
            for reason, count in excluded.items():
                if not reason or not isinstance(count, int) or count < 0:
                    errors.append(
                        "coverage excluded_reason_counts must contain non-negative integer counts"
                    )
                    break
        for prefix in ("repo", "article"):
            input_key = f"{prefix}_count_input"
            mapped_key = f"{prefix}_count_mapped"
            if input_key in coverage or mapped_key in coverage:
                input_count = coverage.get(input_key)
                mapped_count = coverage.get(mapped_key)
                if (
                    not isinstance(input_count, int)
                    or not isinstance(mapped_count, int)
                    or input_count < 0
                    or mapped_count < 0
                ):
                    errors.append(f"coverage {prefix} counts must be non-negative integers")
                    continue
                if mapped_count > input_count:
                    errors.append(f"coverage {mapped_key} exceeds {input_key}")
                if mapped_count < input_count and not coverage.get("excluded_reason_counts"):
                    errors.append(
                        f"coverage {mapped_key} below {input_key} without excluded reasons"
                    )
        status = payload.get("status")
        if status == "failed":
            errors.append("mapper status failed")
    return errors


def normalized_claim_key(finding: dict[str, Any]) -> str:
    repo = finding.get("repo_full_name") or ""
    article = finding.get("news_url") or ""
    claim = str(finding.get("claim") or "").lower()
    words = "-".join(re.findall(r"[a-z0-9]+", claim)[:8])
    return f"{finding.get('category')}:{repo or article or words}"


def contra_ref_targets(contra_refs: Any) -> set[str]:
    targets: set[str] = set()
    if not isinstance(contra_refs, list):
        return targets
    for ref in contra_refs:
        if isinstance(ref, str) and ref:
            targets.add(ref)
        elif isinstance(ref, dict):
            for key in ("claim_id", "ref", "url"):
                value = ref.get(key)
                if value:
                    targets.add(str(value))
    return targets


def contradiction_record(
    finding: dict[str, Any],
    ledger: dict[str, Any],
    *,
    contradicted_by: list[str],
) -> dict[str, Any]:
    contra_refs = finding.get("contra_refs") if isinstance(finding.get("contra_refs"), list) else []
    return {
        "claim_id": finding.get("claim_id"),
        "claim": finding.get("claim"),
        "source_shard": ledger.get("shard_id"),
        "normalized_claim_key": normalized_claim_key(finding),
        "evidence_refs": finding.get("evidence_refs")
        if isinstance(finding.get("evidence_refs"), list)
        else [],
        "contra_refs": contra_refs,
        "contradicted_by": sorted(set(contradicted_by)),
        "resolution": "rejected_unresolved",
        "reason": "Unresolved contradiction refs are preserved for audit and excluded from selected editorial material.",
    }


def reduce_ledgers(
    ledgers: list[dict[str, Any]], *, raw_payload: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    contradictions: list[dict[str, Any]] = []
    seen_keys: dict[str, dict[str, Any]] = {}
    section_by_category = {
        "trend": "This Week's Trends",
        "signal": "Signal & Noise",
        "noise": "Signal & Noise",
        "gap": "Blind Spots",
        "press_correlation": "Where Industry Meets Code",
        "press_divergence": "Where Industry Meets Code",
        "continuity": "The Week Ahead",
    }
    inbound_contradictions: dict[str, list[str]] = {}
    for ledger in ledgers:
        for finding in (
            ledger.get("findings", []) if isinstance(ledger.get("findings"), list) else []
        ):
            if not isinstance(finding, dict):
                continue
            source_claim_id = finding.get("claim_id")
            for target in contra_ref_targets(finding.get("contra_refs")):
                inbound_contradictions.setdefault(target, []).append(str(source_claim_id))
    for ledger in ledgers:
        ledger_findings = (
            ledger.get("findings", []) if isinstance(ledger.get("findings"), list) else []
        )
        for finding in ledger_findings:
            if not isinstance(finding, dict):
                rejected.append(
                    {
                        "claim_id": None,
                        "reason": "malformed_finding",
                        "source_shard": ledger.get("shard_id"),
                    }
                )
                continue
            refs = (
                finding.get("evidence_refs")
                if isinstance(finding.get("evidence_refs"), list)
                else []
            )
            contra_refs = (
                finding.get("contra_refs") if isinstance(finding.get("contra_refs"), list) else []
            )
            contradicted_by = inbound_contradictions.get(str(finding.get("claim_id")), [])
            if contra_refs or contradicted_by:
                contradictions.append(
                    contradiction_record(finding, ledger, contradicted_by=contradicted_by)
                )
                rejected.append(
                    {
                        "claim_id": finding.get("claim_id"),
                        "reason": "unresolved_contradiction",
                        "source_shard": ledger.get("shard_id"),
                    }
                )
                continue
            if not refs:
                rejected.append(
                    {
                        "claim_id": finding.get("claim_id"),
                        "reason": "weak_citation",
                        "source_shard": ledger.get("shard_id"),
                    }
                )
                continue
            key = normalized_claim_key(finding)
            if key in seen_keys:
                existing = seen_keys[key]
                existing["merged_from"].append(finding["claim_id"])
                existing["citation_bindings"]["repos"].extend(
                    [r.get("ref") for r in refs if r.get("type") == "repo"]
                )
                existing["citation_bindings"]["articles"].extend(
                    [r.get("url") for r in refs if r.get("type") == "article"]
                )
                rejected.append(
                    {
                        "claim_id": finding.get("claim_id"),
                        "reason": "duplicate",
                        "source_shard": ledger.get("shard_id"),
                    }
                )
                continue
            reduced = {
                "claim_id": f"reduce-{hashlib.sha256(key.encode('utf-8')).hexdigest()[:12]}",
                "section": section_by_category.get(finding.get("category"), "Signal & Noise"),
                "merged_from": [finding["claim_id"]],
                "normalized_claim_key": key,
                "claim": finding["claim"],
                "citation_bindings": {
                    "repos": [r.get("ref") for r in refs if r.get("type") == "repo"],
                    "articles": [r.get("url") for r in refs if r.get("type") == "article"],
                },
                "confidence": finding.get("confidence", 0),
                "rationale": "Selected by deterministic dry-run reducer because it has explicit evidence references and unique normalized key.",
            }
            seen_keys[key] = reduced
            selected.append(reduced)
    for claim in selected:
        claim["citation_bindings"]["repos"] = sorted(
            set(filter(None, claim["citation_bindings"]["repos"]))
        )
        claim["citation_bindings"]["articles"] = sorted(
            set(filter(None, claim["citation_bindings"]["articles"]))
        )
    contradictions = sorted(
        contradictions, key=lambda c: (str(c.get("source_shard")), str(c.get("claim_id")))
    )
    selected = sorted(
        selected,
        key=lambda c: (
            SECTION_ORDER.index(c["section"]) if c["section"] in SECTION_ORDER else 99,
            -float(c["confidence"]),
            c["claim_id"],
        ),
    )[:16]
    all_repos = raw_payload.get("new_repos", []) + raw_payload.get("trending_repos", [])
    top_repo = (
        normalize_repo_name(sorted_repos(all_repos, mode="new")[:1][0])
        if all_repos
        else "unknown/unknown"
    )
    topics = (
        raw_payload.get("signals", {}).get("top_topics", [])
        if isinstance(raw_payload.get("signals"), dict)
        else []
    )
    tags = []
    for topic in topics:
        value = topic.get("topic") if isinstance(topic, dict) else topic
        if value:
            tags.append(str(value))
    tags = tags[:5] or ["open-source", "developer-tools", "automation"]
    notable = sorted({repo for claim in selected for repo in claim["citation_bindings"]["repos"]})
    articles = sorted({url for claim in selected for url in claim["citation_bindings"]["articles"]})
    plan = {
        "schema_version": PLAN_SCHEMA,
        "title": f"{top_repo.split('/')[-1]} and the Week's Candidate Repo Signals",
        "summary": "Deterministic map/reduce dry-run candidate built from validated claim ledgers; not publish eligible.",
        "top_repo": top_repo,
        "tags": tags,
        "selected_claims": selected,
        "key_references": {"notable_projects": notable[:10], "press_articles": articles[:10]},
        "rejected_claims": rejected,
        "contradictions": contradictions,
        "quality_notes": [
            CANDIDATE_DISCLAIMER,
            "Reducer consumed only validated analysis_map_v1 ledgers.",
        ],
    }
    return plan, rejected, contradictions


def section_claims(plan: dict[str, Any], section: str) -> list[dict[str, Any]]:
    return [claim for claim in plan.get("selected_claims", []) if claim.get("section") == section]


def repo_link(repo: str) -> str:
    return f"[{repo}](https://github.com/{repo})"


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_claim_sentence(claim: dict[str, Any]) -> str:
    repos = [repo_link(repo) for repo in claim.get("citation_bindings", {}).get("repos", [])]
    articles = claim.get("citation_bindings", {}).get("articles", [])
    evidence = ""
    if repos:
        evidence = f" Evidence anchor: {', '.join(repos[:3])}."
    if articles:
        evidence += f" Press reference: {articles[0]}."
    return f"{claim.get('claim')} {evidence} Confidence is {float(claim.get('confidence', 0)):.2f}; this remains a candidate signal because the dry-run reducer has not been promoted."


def render_section(plan: dict[str, Any], section: str, fallback: str) -> str:
    claims = section_claims(plan, section)
    sentences = [render_claim_sentence(claim) for claim in claims[:4]]
    if not sentences:
        sentences = [fallback]
    # Add deterministic editorial context so candidate exercises analysis_gate-like structural and evidence checks.
    context = {
        "This Week's Trends": "The durable trend test is whether repeated repository evidence points to reusable developer infrastructure rather than isolated launches. These candidate claims are useful for QA because each one is bound to ledger provenance, explicit confidence, and source coverage counts.",
        "Where Industry Meets Code": "The industry comparison stays cautious: retained press URLs can support context, but the reducer rejects unstated sentiment and keeps weak correlations out of the final plan. This matters because press excitement and repository adoption often move at different speeds.",
        "Signal & Noise": "The signal/noise split favors claims with direct repository citations, measurable stars or momentum, and clear uncertainty notes. Noise remains possible where descriptions are thin, stars are early, or a project resembles a promotional launch rather than durable ecosystem work.",
        "Blind Spots": "The main blind spots are deterministic: this dry run cannot make live model judgments, cannot infer sentiment beyond supplied artifacts, and cannot publish. Coverage ledgers expose omitted repositories and missing prior context so future QA can decide whether human review is required.",
        "The Week Ahead": "Future eligibility depends on the same candidate passing structural analysis gates, evidence gates, and comparison QA while still staying non-publishing until an explicit promotion policy exists. The next run should compare selected references, contradictions, and rejected claims against the current single-pass path.",
    }[section]
    return "\n\n".join(sentences + [context])


def render_candidate(
    plan: dict[str, Any], raw_payload: dict[str, Any], current_datetime: str
) -> str:
    week = raw_payload["week"]
    year = int(week.split("-W", 1)[0])
    repos_featured = len(raw_payload.get("new_repos", [])) + len(
        raw_payload.get("trending_repos", [])
    )
    stars_tracked = sum(
        int(repo.get("stars") or 0)
        for repo in raw_payload.get("new_repos", []) + raw_payload.get("trending_repos", [])
    )
    tags = ", ".join(yaml_quote(str(tag)) for tag in plan["tags"])
    frontmatter = f'''---
title: {yaml_quote(str(plan["title"]))}
date: {current_datetime}
week: "{week}"
year: {year}
tags: [{tags}]
categories: [weekly]
repos_featured: {repos_featured}
stars_tracked: {stars_tracked}
top_repo: {yaml_quote(str(plan["top_repo"]))}
quality_score: 60
summary: {yaml_quote(str(plan["summary"]))}
---'''
    notable = plan.get("key_references", {}).get("notable_projects", []) or [plan["top_repo"]]
    notable_lines = "\n".join(f"- {repo_link(repo)}" for repo in notable[:10])
    articles = plan.get("key_references", {}).get("press_articles", [])
    press_lines = (
        "\n".join(f"- {url}" for url in articles[:10])
        if articles
        else "- No retained press URLs were selected by the dry-run reducer."
    )
    return (
        frontmatter
        + f"\n\n> {CANDIDATE_DISCLAIMER}\n\n"
        + "## This Week's Trends\n\n"
        + render_section(
            plan,
            "This Week's Trends",
            f"The leading dry-run trend is anchored by {repo_link(plan['top_repo'])}, but the reducer requires future human/model QA before publication.",
        )
        + "\n\n## Where Industry Meets Code\n\n"
        + render_section(
            plan,
            "Where Industry Meets Code",
            "No strong press correlation survived this deterministic dry run; the absence is surfaced as uncertainty rather than converted into a publishable claim.",
        )
        + "\n\n## Signal & Noise\n\n"
        + render_section(
            plan,
            "Signal & Noise",
            f"The clearest candidate signal is repository-backed momentum around {repo_link(plan['top_repo'])}, while uncited or duplicate findings stay in rejected sidecars.",
        )
        + "\n\n## Blind Spots\n\n"
        + render_section(
            plan,
            "Blind Spots",
            "The reducer exposes blind spots instead of filling them with prose: omitted repos, missing press URLs, and absent prior continuity remain QA findings.",
        )
        + "\n\n## The Week Ahead\n\n"
        + render_section(
            plan,
            "The Week Ahead",
            "Before any promotion, QA must show no regression against the current single-pass path and the candidate must remain blocked from publish workflows.",
        )
        + "\n\n## Key References\n\n### Notable Projects\n\n"
        + notable_lines
        + "\n\n### Press & Industry\n\n"
        + press_lines
        + "\n"
    )


def build_qa_report(
    *,
    candidate_path: Path,
    candidate_text: str,
    raw_payload: dict[str, Any],
    current_datetime: str,
    plan: dict[str, Any],
    map_errors: dict[str, list[str]],
    baseline_summary: Path | None,
    source: str,
    model: str,
) -> dict[str, Any]:
    structural_errors, word_count = validate_analysis(candidate_text, raw_payload, current_datetime)
    publish_errors, gates = validate_publish_quality(
        candidate_text, raw_payload, source=source, model=model
    )
    non_provenance_errors = [
        error for error in publish_errors if not error.startswith("AI provenance")
    ]
    baseline_ref = file_ref(baseline_summary)
    selected_refs = set(plan.get("key_references", {}).get("notable_projects", [])) | set(
        plan.get("key_references", {}).get("press_articles", [])
    )
    report = {
        "schema_version": QA_SCHEMA,
        "candidate": asdict(file_ref(candidate_path)) if file_ref(candidate_path) else None,
        "baseline_summary": asdict(baseline_ref) if baseline_ref else None,
        "status": "passed"
        if not structural_errors and not non_provenance_errors and not any(map_errors.values())
        else "failed",
        "publish_eligible": False,
        "promotion_blockers": [
            CANDIDATE_DISCLAIMER,
            "analysis source/model are local deterministic dry-run values, not publishable AI provenance.",
            "No workflow path promotes map/reduce dry-run output to content/weekly or data/analyzed.",
        ],
        "regressions": [],
        "checks": {
            "mapper_contracts": {
                "passed": not any(map_errors.values()),
                "errors_by_mapper": map_errors,
            },
            "structural_analysis_gate": {
                "passed": not structural_errors,
                "errors": structural_errors,
                "word_count": word_count,
            },
            "evidence_and_editorial_gates": {
                "passed": not non_provenance_errors,
                "errors": non_provenance_errors,
                "gate_details": gates,
            },
            "publish_provenance_gate": {
                "passed": False,
                "expected_failure": True,
                "errors": [error for error in publish_errors if error.startswith("AI provenance")],
            },
            "sidecars_present": {
                "passed": isinstance(plan.get("rejected_claims"), list)
                and isinstance(plan.get("contradictions"), list),
                "rejected_count": len(plan.get("rejected_claims", [])),
                "contradiction_count": len(plan.get("contradictions", [])),
            },
            "reference_count": {
                "selected": len(selected_refs),
                "notable_projects": len(plan.get("key_references", {}).get("notable_projects", [])),
                "press_articles": len(plan.get("key_references", {}).get("press_articles", [])),
            },
        },
    }
    if baseline_summary and not baseline_summary.exists():
        report["regressions"].append(f"baseline summary not found: {baseline_summary}")
    return report


def run(args: argparse.Namespace) -> dict[str, Path]:
    analysis_started = time.monotonic()
    raw_payload = sanitize_repo_payload(load_json(args.raw_json))
    week = raw_payload["week"]
    raw_ref = file_ref(args.raw_json)
    if raw_ref is None:
        raise ValueError(f"raw JSON not found: {args.raw_json}")
    press_ref = file_ref(args.press_context)
    previous_summary = find_previous_summary(week, args.analyzed_dir)
    previous_ref = file_ref(previous_summary)

    map_stage_metrics: list[MapReduceMetrics] = []
    maps: dict[str, dict[str, Any]] = {}
    map_builders = {
        "new_repos": lambda: map_repositories(
            run_id=args.run_id,
            week=week,
            raw_path=args.raw_json,
            raw_ref=raw_ref,
            shard_id="new_repos",
            repos=raw_payload.get("new_repos", []),
            mode="new",
            max_repos=args.max_repos_per_ledger,
        ),
        "trending_repos": lambda: map_repositories(
            run_id=args.run_id,
            week=week,
            raw_path=args.raw_json,
            raw_ref=raw_ref,
            shard_id="trending_repos",
            repos=raw_payload.get("trending_repos", []),
            mode="trending",
            max_repos=args.max_repos_per_ledger,
        ),
        "press_correlations": lambda: map_press(
            run_id=args.run_id,
            week=week,
            press_path=args.press_context,
            press_ref=press_ref,
            raw_ref=raw_ref,
        ),
        "prior_continuity": lambda: map_prior(
            run_id=args.run_id,
            week=week,
            previous_summary=previous_summary,
            previous_ref=previous_ref,
            raw_ref=raw_ref,
        ),
    }
    for name in MAPPER_IDS:
        stage_started = time.monotonic()
        payload = map_builders[name]()
        maps[name] = payload
        stage_duration = round(time.monotonic() - stage_started, 3)
        input_tokens = int(payload.get("slice", {}).get("input_token_estimate") or 0)
        output_tokens = int(payload.get("token_estimate") or 0)
        map_stage_metrics.append(
            MapReduceMetrics(
                stage=name,
                duration_seconds=stage_duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=metric_cost_usd(args.analysis_model, input_tokens, output_tokens),
                status="pass",
                gate_failure_reasons=[],
            )
        )
    map_errors = {name: validate_map(payload) for name, payload in maps.items()}
    if any(map_errors.values()):
        for name, errors in map_errors.items():
            if errors:
                maps[name]["status"] = "failed"
                maps[name]["errors"] = errors
    map_metrics_by_stage = {metric.stage: metric for metric in map_stage_metrics}
    for name, errors in map_errors.items():
        if errors:
            metric = map_metrics_by_stage.get(name)
            if metric is not None:
                map_stage_metrics[map_stage_metrics.index(metric)] = MapReduceMetrics(
                    stage=metric.stage,
                    duration_seconds=metric.duration_seconds,
                    input_tokens=metric.input_tokens,
                    output_tokens=metric.output_tokens,
                    cost_usd=metric.cost_usd,
                    status="fail",
                    gate_failure_reasons=list(errors),
                )
    reduce_started = time.monotonic()
    plan, rejected, contradictions = reduce_ledgers(list(maps.values()), raw_payload=raw_payload)
    candidate_text = render_candidate(plan, raw_payload, args.current_datetime)

    out = args.output_dir
    maps_dir = out / "maps"
    sidecars_dir = out / "sidecars"
    evidence_slices_dir = sidecars_dir / "evidence-slices"
    evidence_slice_refs: dict[str, dict[str, Any]] = {}
    for name, payload in maps.items():
        map_path = maps_dir / f"{name}.json"
        write_json(map_path, payload)
        map_ref = file_ref(map_path)
        if map_ref:
            addressed_path = evidence_slices_dir / f"{name}-{map_ref.sha256[:12]}.json"
            write_json(addressed_path, payload)
            addressed_ref = file_ref(addressed_path)
            evidence_slice_refs[name] = asdict(addressed_ref) if addressed_ref else {}
    write_json(out / "editorial-plan.json", plan)
    write_json(
        sidecars_dir / "rejected-claims.json",
        {
            "schema_version": "analysis_rejected_claims_v1",
            "week": week,
            "rejected_claims": rejected,
        },
    )
    write_json(
        sidecars_dir / "contradictions.json",
        {
            "schema_version": "analysis_contradictions_v1",
            "week": week,
            "contradictions": contradictions,
        },
    )
    candidate_path = out / f"{week}-map-reduce-candidate.md"
    candidate_path.write_text(candidate_text, encoding="utf-8")
    qa = build_qa_report(
        candidate_path=candidate_path,
        candidate_text=candidate_text,
        raw_payload=raw_payload,
        current_datetime=args.current_datetime,
        plan=plan,
        map_errors=map_errors,
        baseline_summary=args.baseline_summary,
        source=args.analysis_source,
        model=args.analysis_model,
    )
    reduce_duration = round(time.monotonic() - reduce_started, 3)
    reduce_input_tokens = sum(metric.output_tokens for metric in map_stage_metrics)
    reduce_output_tokens = estimate_tokens(candidate_text)
    reduce_failure_reasons = collect_gate_failure_reasons(qa)
    reduce_stage_metric = MapReduceMetrics(
        stage="reduce",
        duration_seconds=reduce_duration,
        input_tokens=reduce_input_tokens,
        output_tokens=reduce_output_tokens,
        cost_usd=metric_cost_usd(args.analysis_model, reduce_input_tokens, reduce_output_tokens),
        status="pass" if qa.get("status") == "passed" else "fail",
        gate_failure_reasons=reduce_failure_reasons,
    )
    write_json(out / "qa-comparison-report.json", qa)
    raw_component = file_ref(args.raw_json)
    press_component = file_ref(args.press_context)
    template_component = file_ref(ROOT / "prompts" / "analyze-weekly.md")
    prior_component = file_ref(previous_summary)
    slice_components = {name: ref for name, ref in evidence_slice_refs.items()}
    manifest = {
        "schema_version": "analysis_map_reduce_dry_run_manifest_v1",
        "week": week,
        "run_id": args.run_id,
        "created_at": args.current_datetime,
        "publish_eligible": False,
        "candidate_only": True,
        "artifacts": {
            "maps": {name: (maps_dir / f"{name}.json").as_posix() for name in MAPPER_IDS},
            "evidence_slices": {name: ref.get("path") for name, ref in evidence_slice_refs.items()},
            "editorial_plan": (out / "editorial-plan.json").as_posix(),
            "rejected_claims": (sidecars_dir / "rejected-claims.json").as_posix(),
            "contradictions": (sidecars_dir / "contradictions.json").as_posix(),
            "candidate": candidate_path.as_posix(),
            "qa_report": (out / "qa-comparison-report.json").as_posix(),
        },
        "component_estimates": {
            "raw_json": asdict(raw_component) if raw_component else None,
            "press_context": asdict(press_component) if press_component else None,
            "prompt_template": asdict(template_component) if template_component else None,
            "prior_continuity": asdict(prior_component) if prior_component else None,
            "generated_evidence_slices": slice_components,
            "rendered_prompt_estimate": {
                "bytes": len(candidate_text.encode("utf-8")),
                "tokens": estimate_tokens(candidate_text),
                "checksum_sha256": sha256_bytes(candidate_text.encode("utf-8")),
            },
        },
        "citation_inventories": {
            "repos": sorted(
                {
                    ref.get("ref")
                    for payload in maps.values()
                    for finding in payload.get("findings", [])
                    for ref in finding.get("evidence_refs", [])
                    if isinstance(ref, dict) and ref.get("type") == "repo" and ref.get("ref")
                }
            ),
            "press_articles": sorted(
                {
                    ref.get("url")
                    for payload in maps.values()
                    for finding in payload.get("findings", [])
                    for ref in finding.get("evidence_refs", [])
                    if isinstance(ref, dict) and ref.get("type") == "article" and ref.get("url")
                }
            ),
        },
        "promotion_policy": "blocked: dry-run/candidate-only map/reduce output must not write data/analyzed, content/weekly, deploy, notify, or satisfy publish eligibility.",
    }
    write_json(out / "manifest.json", manifest)
    total_input_tokens = (
        sum(metric.input_tokens for metric in map_stage_metrics) + reduce_stage_metric.input_tokens
    )
    total_output_tokens = (
        sum(metric.output_tokens for metric in map_stage_metrics)
        + reduce_stage_metric.output_tokens
    )
    total_cost_usd = round(
        sum(metric.cost_usd for metric in map_stage_metrics) + reduce_stage_metric.cost_usd, 6
    )
    analysis_duration = round(time.monotonic() - analysis_started, 3)
    observability_path = DEFAULT_OBSERVABILITY_DIR / f"{week}-map-reduce.json"
    emit_ledger(
        ObservabilityLedger(
            schema_version=METRICS_SCHEMA_VERSION,
            run_id=args.run_id,
            week=week,
            timestamp=args.current_datetime,
            crawl_metrics=[],
            analysis_metrics=AnalysisMetrics(
                duration_seconds=analysis_duration,
                token_ledger={
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": total_input_tokens + total_output_tokens,
                    "cost_usd": total_cost_usd,
                },
                map_stages=map_stage_metrics,
                reduce_stage=reduce_stage_metric,
            ),
            environment={
                "pipeline": "map-reduce-dry-run",
                "analysis_source": args.analysis_source,
                "analysis_model": args.analysis_model,
                "output_dir": out.as_posix(),
                "qa_status": qa.get("status"),
                "publish_eligible": qa.get("publish_eligible"),
                "pass_fail_counts": {
                    "map_pass": sum(1 for metric in map_stage_metrics if metric.status == "pass"),
                    "map_fail": sum(1 for metric in map_stage_metrics if metric.status == "fail"),
                    "reduce_pass": 1 if reduce_stage_metric.status == "pass" else 0,
                    "reduce_fail": 1 if reduce_stage_metric.status == "fail" else 0,
                },
                "gate_failure_reasons": reduce_failure_reasons,
                "artifacts": {
                    "manifest": (out / "manifest.json").as_posix(),
                    "candidate": candidate_path.as_posix(),
                    "qa_report": (out / "qa-comparison-report.json").as_posix(),
                },
            },
        ),
        observability_path,
    )
    return {
        "manifest": out / "manifest.json",
        "qa_report": out / "qa-comparison-report.json",
        "candidate": candidate_path,
        "observability": observability_path,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        artifacts = run(args)
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"map/reduce dry-run failed: {exc}", file=sys.stderr)
        return 1
    print(f"Map/reduce dry-run artifacts written to {args.output_dir}")
    for name, path in artifacts.items():
        print(f"{name}={path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
