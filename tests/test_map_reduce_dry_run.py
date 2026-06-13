from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts import map_reduce_dry_run as dry_run
from scripts.observability_metrics import validate_ledger


def make_repo(owner: str, name: str, stars: int, gained: int = 0) -> dict[str, object]:
    return {
        "name": name,
        "owner": owner,
        "full_name": f"{owner}/{name}",
        "description": f"{name} provides evidence-backed developer infrastructure for testing map reduce analysis contracts.",
        "language": "Python",
        "stars": stars,
        "stars_gained": gained,
        "created_at": "2026-05-18T10:00:00Z",
        "topics": ["ai", "developer-tools"],
        "url": f"https://github.com/{owner}/{name}",
    }


def test_dry_run_emits_valid_contract_artifacts() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        base = Path(tmpdir)
        raw_path = base / "data" / "raw" / "2026-W21.json"
        press_path = base / "data" / "analyzed" / "2026-W21-press-context.md"
        output_dir = base / "data" / "candidates" / "2026-W21" / "local" / "map-reduce"
        raw_path.parent.mkdir(parents=True)
        press_path.parent.mkdir(parents=True)
        raw_payload = {
            "week": "2026-W21",
            "crawled_at": "2026-05-20T12:00:00Z",
            "new_repos": [make_repo("octo", "alpha", 1200), make_repo("octo", "beta", 900)],
            "trending_repos": [make_repo("tools", "gamma", 5000, 450), make_repo("tools", "delta", 3000, 250)],
            "signals": {"top_topics": ["ai", "developer-tools", "testing"]},
        }
        raw_path.write_text(json.dumps(raw_payload), encoding="utf-8")
        press_path.write_text(
            "### Correlation Summary\n- Industry article: https://example.com/ai-tooling links repo momentum to developer tools.\n",
            encoding="utf-8",
        )

        rc = dry_run.main(
            [
                "--raw-json",
                raw_path.as_posix(),
                "--press-context",
                press_path.as_posix(),
                "--output-dir",
                output_dir.as_posix(),
                "--current-datetime",
                "2026-05-20T12:00:00Z",
                "--run-id",
                "local",
            ]
        )

        assert rc == 0
        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["publish_eligible"] is False
        assert manifest["candidate_only"] is True
        rendered_estimate = manifest["component_estimates"]["rendered_prompt_estimate"]
        assert set(rendered_estimate) == {"bytes", "tokens", "checksum_sha256"}
        assert rendered_estimate["tokens"] > 0
        assert rendered_estimate["checksum_sha256"]
        for mapper in dry_run.MAPPER_IDS:
            ledger = json.loads((output_dir / "maps" / f"{mapper}.json").read_text(encoding="utf-8"))
            assert ledger["schema_version"] == "analysis_map_v1"
            assert ledger["coverage"]["excluded_reason_counts"] == {}
            assert dry_run.validate_map(ledger) == []
        plan = json.loads((output_dir / "editorial-plan.json").read_text(encoding="utf-8"))
        assert plan["schema_version"] == "analysis_editorial_plan_v1"
        assert (output_dir / "sidecars" / "rejected-claims.json").exists()
        assert (output_dir / "sidecars" / "contradictions.json").exists()
        candidate = (output_dir / "2026-W21-map-reduce-candidate.md").read_text(encoding="utf-8")
        assert "Map/reduce dry-run candidate only" in candidate
        assert "[tools/gamma](https://github.com/tools/gamma)" in candidate
        qa = json.loads((output_dir / "qa-comparison-report.json").read_text(encoding="utf-8"))
        assert qa["status"] == "passed"
        assert qa["publish_eligible"] is False
        assert qa["checks"]["structural_analysis_gate"]["passed"] is True
        assert qa["checks"]["evidence_and_editorial_gates"]["passed"] is True
        assert qa["checks"]["publish_provenance_gate"]["expected_failure"] is True
        observability_path = dry_run.DEFAULT_OBSERVABILITY_DIR / "2026-W21-map-reduce.json"
        observability = json.loads(observability_path.read_text(encoding="utf-8"))
        assert validate_ledger(observability) == []
        assert observability["analysis_metrics"]["reduce_stage"]["status"] == "pass"
        assert observability["environment"]["pass_fail_counts"]["map_pass"] == 4


def test_validate_map_rejects_citationless_findings() -> None:
    payload = {
        "schema_version": "analysis_map_v1",
        "run_id": "local",
        "week": "2026-W21",
        "shard_id": "signal-type:new_repos",
        "slice": {},
        "coverage": {"repo_ids_seen": [], "article_urls_seen": [], "excluded_reason_counts": {}},
        "findings": [
            {
                "claim_id": "bad",
                "claim": "unsupported",
                "category": "trend",
                "source_type": "github",
                "evidence_refs": [],
                "confidence": 0.5,
                "contra_refs": [],
                "uncertainties": [],
            }
        ],
        "citations": [],
        "reference_candidates": {"notable_projects": [], "press_articles": []},
        "provenance": {},
    }

    assert "finding 0 has no evidence refs" in dry_run.validate_map(payload)


def valid_ledger(findings: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "schema_version": "analysis_map_v1",
        "run_id": "local",
        "week": "2026-W21",
        "shard_id": "signal-type:test",
        "slice": {},
        "coverage": {
            "repo_ids_seen": ["octo/alpha"],
            "article_urls_seen": [],
            "repo_count_input": 1,
            "repo_count_mapped": 1,
            "article_count_input": 0,
            "article_count_mapped": 0,
            "excluded_reason_counts": {},
        },
        "findings": findings
        if findings is not None
        else [
            {
                "claim_id": "claim-a",
                "claim": "octo/alpha is supported by direct repository evidence.",
                "category": "trend",
                "source_type": "github",
                "evidence_refs": [{"type": "repo", "ref": "octo/alpha", "url": "https://github.com/octo/alpha"}],
                "repo_full_name": "octo/alpha",
                "news_url": None,
                "confidence": 0.8,
                "contra_refs": [],
                "uncertainties": [],
            }
        ],
        "citations": [],
        "reference_candidates": {"notable_projects": ["octo/alpha"], "press_articles": []},
        "provenance": {},
    }


def test_validate_map_rejects_malformed_ledger() -> None:
    payload = valid_ledger()
    payload.pop("coverage")
    payload["findings"] = "not-a-list"

    errors = dry_run.validate_map(payload)

    assert "mapper missing coverage" in errors
    assert "findings must be a list" in errors
    assert "coverage must be an object" in errors


def test_validate_map_rejects_failed_or_low_coverage() -> None:
    payload = valid_ledger()
    payload["coverage"] = {
        "repo_ids_seen": ["octo/alpha"],
        "article_urls_seen": [],
        "repo_count_input": 3,
        "repo_count_mapped": 1,
        "article_count_input": 0,
        "article_count_mapped": 1,
        "excluded_reason_counts": {},
    }
    payload["status"] = "failed"

    errors = dry_run.validate_map(payload)

    assert "coverage repo_count_mapped below repo_count_input without excluded reasons" in errors
    assert "coverage article_count_mapped exceeds article_count_input" in errors
    assert "mapper status failed" in errors


def test_reduce_rejects_and_preserves_contradictory_claims() -> None:
    supported = valid_ledger()["findings"][0]
    contradictory = {
        **supported,
        "claim_id": "claim-b",
        "claim": "octo/alpha evidence is contradicted by another retained source.",
        "contra_refs": ["claim-a"],
        "confidence": 0.9,
    }
    ledger = valid_ledger([supported, contradictory])

    plan, rejected, contradictions = dry_run.reduce_ledgers([ledger], raw_payload={"week": "2026-W21", "new_repos": [make_repo("octo", "alpha", 1200)], "trending_repos": []})

    assert plan["selected_claims"] == []
    assert [item["claim_id"] for item in contradictions] == ["claim-a", "claim-b"]
    assert {item["claim_id"] for item in rejected if item["reason"] == "unresolved_contradiction"} == {"claim-a", "claim-b"}
    assert plan["contradictions"] == contradictions
