from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts import map_reduce_dry_run as dry_run


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
