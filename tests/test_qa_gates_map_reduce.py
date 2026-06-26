"""Automated QA gates for matrix crawl and map/reduce acceptance criteria.

Covers:
- Reducer correctness: deterministic fan-in, citation preservation, contradiction handling
- End-to-end dry-run: full pipeline on representative fixtures with gate validation
- Cost/token guardrails: budget accounting, bounds enforcement
- Failure handling: mapper/reducer failure paths and fallback behavior

These gates run as part of the existing pytest CI path (issue #438).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import map_reduce_dry_run as dry_run
from scripts.model_pricing import MODEL_RATES, estimate_cost_usd
from scripts.preflight_cost_check import estimate_input_tokens
from scripts.preflight_cost_check import main as preflight_main

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_repo(owner: str, name: str, stars: int, gained: int = 0, **extra) -> dict:
    base = {
        "name": name,
        "owner": owner,
        "full_name": f"{owner}/{name}",
        "description": f"{name} delivers evidence-backed developer tooling for the open-source ecosystem.",
        "language": "Python",
        "stars": stars,
        "stars_gained": gained,
        "created_at": "2026-05-18T10:00:00Z",
        "topics": ["ai", "developer-tools"],
        "url": f"https://github.com/{owner}/{name}",
    }
    base.update(extra)
    return base


def valid_finding(claim_id: str = "claim-1", repo: str = "org/repo", **overrides) -> dict:
    base = {
        "claim_id": claim_id,
        "claim": f"{repo} is supported by repository evidence.",
        "category": "trend",
        "source_type": "github",
        "evidence_refs": [{"type": "repo", "ref": repo, "url": f"https://github.com/{repo}"}],
        "repo_full_name": repo,
        "news_url": None,
        "confidence": 0.78,
        "contra_refs": [],
        "uncertainties": [],
    }
    base.update(overrides)
    return base


def valid_ledger(findings=None, shard_id="signal-type:test") -> dict:
    if findings is None:
        findings = [valid_finding()]
    return {
        "schema_version": "analysis_map_v1",
        "run_id": "local",
        "week": "2026-W21",
        "shard_id": shard_id,
        "slice": {},
        "coverage": {
            "repo_ids_seen": ["org/repo"],
            "article_urls_seen": [],
            "repo_count_input": 1,
            "repo_count_mapped": 1,
            "article_count_input": 0,
            "article_count_mapped": 0,
            "excluded_reason_counts": {},
        },
        "findings": findings,
        "citations": [],
        "reference_candidates": {"notable_projects": ["org/repo"], "press_articles": []},
        "provenance": {},
    }


RAW_PAYLOAD = {
    "week": "2026-W21",
    "crawled_at": "2026-05-20T12:00:00Z",
    "new_repos": [make_repo("octo", "alpha", 1200, 50), make_repo("octo", "beta", 900, 30)],
    "trending_repos": [
        make_repo("tools", "gamma", 5000, 450),
        make_repo("tools", "delta", 3000, 250),
    ],
    "signals": {"top_topics": ["ai", "developer-tools", "testing"]},
}

PRESS_CONTEXT = (
    "### Correlation Summary\n"
    "- Industry article: https://example.com/ai-tooling links repo momentum to developer tools.\n"
    "- Industry article: https://example.com/oss-growth shows OSS ecosystem expansion.\n"
)


# ===========================================================================
# Section 1: Reducer correctness
# ===========================================================================


class TestReducerDeterministicFanIn:
    """Validates deterministic fan-in assumptions needed by dry-run map/reduce."""

    def test_identical_ledgers_produce_stable_output(self):
        """Running reduce_ledgers twice with same input produces identical plan."""
        ledger = valid_ledger()
        plan1, rej1, con1 = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)
        plan2, rej2, con2 = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        assert plan1 == plan2
        assert rej1 == rej2
        assert con1 == con2

    def test_ledger_ordering_is_deterministic(self):
        """Reducer produces same output regardless of ledger insertion order."""
        ledger_a = valid_ledger(
            [valid_finding("a1", "org/alpha")],
            shard_id="signal-type:new_repos",
        )
        ledger_b = valid_ledger(
            [valid_finding("b1", "org/beta")],
            shard_id="signal-type:trending_repos",
        )

        plan_ab, _, _ = dry_run.reduce_ledgers([ledger_a, ledger_b], raw_payload=RAW_PAYLOAD)
        plan_ba, _, _ = dry_run.reduce_ledgers([ledger_b, ledger_a], raw_payload=RAW_PAYLOAD)

        # Selected claims sorted by section/confidence, so order should be stable
        assert [c["claim_id"] for c in plan_ab["selected_claims"]] == [
            c["claim_id"] for c in plan_ba["selected_claims"]
        ]

    def test_duplicate_claims_collapsed(self):
        """Claims with the same normalized key are deduplicated by the reducer."""
        finding = valid_finding("dup-1", "org/repo")
        finding_dup = valid_finding("dup-2", "org/repo")
        ledger = valid_ledger([finding, finding_dup])

        plan, rejected, _ = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        selected_ids = [c["claim_id"] for c in plan["selected_claims"]]
        assert len(selected_ids) == 1
        dup_rejects = [r for r in rejected if r["reason"] == "duplicate"]
        assert len(dup_rejects) == 1


class TestReducerCitationPreservation:
    """Validates citation preservation for mapper/reducer outputs."""

    def test_selected_claims_retain_citation_bindings(self):
        """Selected claims keep repo and article citation bindings through reduce."""
        finding = valid_finding("cit-1", "org/cited")
        finding["evidence_refs"].append(
            {
                "type": "article",
                "ref": "https://news.example.com/1",
                "url": "https://news.example.com/1",
            }
        )
        ledger = valid_ledger([finding])

        plan, _, _ = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        assert len(plan["selected_claims"]) == 1
        bindings = plan["selected_claims"][0]["citation_bindings"]
        assert "org/cited" in bindings["repos"]
        assert "https://news.example.com/1" in bindings["articles"]

    def test_merged_claims_combine_citations(self):
        """When claims merge, citation bindings from both are combined."""
        f1 = valid_finding("merge-1", "org/repo")
        f1["evidence_refs"] = [
            {"type": "repo", "ref": "org/repo", "url": "https://github.com/org/repo"}
        ]

        # Second ledger with same normalized key but different citation
        f2 = valid_finding("merge-2", "org/repo")
        f2["evidence_refs"] = [
            {"type": "repo", "ref": "org/repo", "url": "https://github.com/org/repo"},
            {
                "type": "article",
                "ref": "https://news.example.com/x",
                "url": "https://news.example.com/x",
            },
        ]
        ledger1 = valid_ledger([f1], shard_id="signal-type:shard1")
        ledger2 = valid_ledger([f2], shard_id="signal-type:shard2")

        plan, _, _ = dry_run.reduce_ledgers([ledger1, ledger2], raw_payload=RAW_PAYLOAD)

        assert len(plan["selected_claims"]) == 1
        bindings = plan["selected_claims"][0]["citation_bindings"]
        assert "org/repo" in bindings["repos"]
        assert "https://news.example.com/x" in bindings["articles"]

    def test_weak_citation_claims_rejected(self):
        """Findings without evidence refs are rejected as weak_citation."""
        finding = valid_finding("weak-1", "org/empty")
        finding["evidence_refs"] = []
        ledger = valid_ledger([finding])

        plan, rejected, _ = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        assert plan["selected_claims"] == []
        weak = [r for r in rejected if r["reason"] == "weak_citation"]
        assert len(weak) == 1
        assert weak[0]["claim_id"] == "weak-1"


class TestReducerContradictionHandling:
    """Validates contradiction detection and rejection behavior."""

    def test_mutual_contradiction_rejects_both(self):
        """Claims that reference each other's contra_refs are both rejected."""
        f1 = valid_finding("contra-1", "org/a")
        f1["contra_refs"] = ["contra-2"]
        f2 = valid_finding("contra-2", "org/b")
        f2["contra_refs"] = ["contra-1"]
        ledger = valid_ledger([f1, f2])

        plan, rejected, contradictions = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        assert plan["selected_claims"] == []
        contra_ids = {c["claim_id"] for c in contradictions}
        assert contra_ids == {"contra-1", "contra-2"}
        reject_ids = {r["claim_id"] for r in rejected if r["reason"] == "unresolved_contradiction"}
        assert reject_ids == {"contra-1", "contra-2"}

    def test_one_sided_contradiction_rejects_contradicted_claim(self):
        """A claim that contradicts another is rejected along with its target."""
        f1 = valid_finding("target-1", "org/target")
        f2 = valid_finding("attacker-1", "org/attacker")
        f2["contra_refs"] = ["target-1"]
        ledger = valid_ledger([f1, f2])

        plan, rejected, contradictions = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        # The attacker has contra_refs, so it's contradicted
        # The target is contradicted_by the attacker
        contra_ids = {c["claim_id"] for c in contradictions}
        assert "attacker-1" in contra_ids
        assert "target-1" in contra_ids

    def test_contradictions_sidecar_populated(self):
        """Contradictions list is preserved in the plan for audit."""
        f1 = valid_finding("sc-1", "org/x")
        f1["contra_refs"] = ["sc-2"]
        f2 = valid_finding("sc-2", "org/y")
        ledger = valid_ledger([f1, f2])

        plan, _, contradictions = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        assert plan["contradictions"] == contradictions
        assert len(contradictions) > 0
        for c in contradictions:
            assert "claim_id" in c
            assert "resolution" in c
            assert c["resolution"] == "rejected_unresolved"


# ===========================================================================
# Section 2: End-to-end dry-run tests
# ===========================================================================


class TestEndToEndDryRun:
    """Exercises full map/reduce scaffolding on fixtures and validates gate outcomes."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create representative fixture workspace."""
        raw_path = tmp_path / "data" / "raw" / "2026-W21.json"
        press_path = tmp_path / "data" / "analyzed" / "2026-W21-press-context.md"
        output_dir = tmp_path / "data" / "candidates" / "2026-W21" / "local" / "map-reduce"
        raw_path.parent.mkdir(parents=True)
        press_path.parent.mkdir(parents=True)
        raw_path.write_text(json.dumps(RAW_PAYLOAD), encoding="utf-8")
        press_path.write_text(PRESS_CONTEXT, encoding="utf-8")
        return raw_path, press_path, output_dir

    def test_full_pipeline_produces_passing_qa(self, workspace):
        """End-to-end run produces qa-comparison-report with status=passed."""
        raw_path, press_path, output_dir = workspace

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
                "qa-gate-test",
            ]
        )

        assert rc == 0
        qa = json.loads((output_dir / "qa-comparison-report.json").read_text(encoding="utf-8"))
        assert qa["status"] == "passed"
        assert qa["publish_eligible"] is False

    def test_all_mapper_contracts_valid(self, workspace):
        """Each mapper ledger passes validate_map with zero errors."""
        raw_path, press_path, output_dir = workspace
        dry_run.main(
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
                "qa-gate-test",
            ]
        )

        for mapper in dry_run.MAPPER_IDS:
            ledger = json.loads(
                (output_dir / "maps" / f"{mapper}.json").read_text(encoding="utf-8")
            )
            errors = dry_run.validate_map(ledger)
            assert errors == [], f"Mapper {mapper} contract errors: {errors}"

    def test_sidecars_always_present(self, workspace):
        """rejected-claims.json and contradictions.json are always emitted."""
        raw_path, press_path, output_dir = workspace
        dry_run.main(
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
                "qa-gate-test",
            ]
        )

        rejected = json.loads(
            (output_dir / "sidecars" / "rejected-claims.json").read_text(encoding="utf-8")
        )
        contras = json.loads(
            (output_dir / "sidecars" / "contradictions.json").read_text(encoding="utf-8")
        )
        assert rejected["schema_version"] == "analysis_rejected_claims_v1"
        assert contras["schema_version"] == "analysis_contradictions_v1"
        assert isinstance(rejected["rejected_claims"], list)
        assert isinstance(contras["contradictions"], list)

    def test_manifest_is_never_publish_eligible(self, workspace):
        """Dry-run manifest always marks candidate_only=True, publish_eligible=False."""
        raw_path, press_path, output_dir = workspace
        dry_run.main(
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
                "qa-gate-test",
            ]
        )

        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["publish_eligible"] is False
        assert manifest["candidate_only"] is True

    def test_qa_report_documents_expected_provenance_failure(self, workspace):
        """The provenance gate fails as expected (dry-run is not publishable AI)."""
        raw_path, press_path, output_dir = workspace
        dry_run.main(
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
                "qa-gate-test",
            ]
        )

        qa = json.loads((output_dir / "qa-comparison-report.json").read_text(encoding="utf-8"))
        provenance = qa["checks"]["publish_provenance_gate"]
        assert provenance["passed"] is False
        assert provenance["expected_failure"] is True

    def test_candidate_markdown_contains_repo_links(self, workspace):
        """Candidate markdown includes hyperlinks to featured repositories."""
        raw_path, press_path, output_dir = workspace
        dry_run.main(
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
                "qa-gate-test",
            ]
        )

        candidate = (output_dir / "2026-W21-map-reduce-candidate.md").read_text(encoding="utf-8")
        assert "[tools/gamma](https://github.com/tools/gamma)" in candidate
        assert "Map/reduce dry-run candidate only" in candidate


# ===========================================================================
# Section 3: Cost/token guardrails
# ===========================================================================


class TestCostTokenGuardrails:
    """Enforces PRD guardrails for token usage and budget accounting."""

    def test_preflight_rejects_over_budget(self, tmp_path):
        """Cost check fails when token budget exceeds hard cap."""
        big_file = tmp_path / "big.json"
        big_file.write_text("x" * 2_000_000, encoding="utf-8")

        rc = preflight_main(["--context-files", str(big_file)])
        assert rc == 1

    def test_preflight_passes_under_budget(self, tmp_path):
        """Cost check passes when under hard cap."""
        small_file = tmp_path / "small.json"
        small_file.write_text("x" * 400, encoding="utf-8")

        rc = preflight_main(["--context-files", str(small_file)])
        assert rc == 0

    def test_preflight_custom_cap_enforcement(self, tmp_path):
        """Custom hard cap correctly triggers failure."""
        medium_file = tmp_path / "medium.json"
        medium_file.write_text("x" * 40_000, encoding="utf-8")

        rc = preflight_main(["--context-files", str(medium_file), "--hard-cap", "0.001"])
        assert rc == 1

    def test_unknown_model_always_fails(self, tmp_path):
        """Unknown model name causes preflight to fail rather than pass silently."""
        f = tmp_path / "a.json"
        f.write_text("content", encoding="utf-8")

        rc = preflight_main(["--context-files", str(f), "--model", "no-such-model-xyz"])
        assert rc == 1

    def test_token_estimate_deterministic(self, tmp_path):
        """Token estimation is deterministic for the same input."""
        f = tmp_path / "stable.json"
        f.write_text("hello world " * 100, encoding="utf-8")

        t1 = estimate_input_tokens([f])
        t2 = estimate_input_tokens([f])
        assert t1 == t2
        assert t1 > 0

    def test_missing_file_yields_zero_tokens(self):
        """Missing files contribute zero tokens, don't crash."""
        tokens = estimate_input_tokens([Path("/nonexistent/file.json")])
        assert tokens == 0

    def test_manifest_token_estimate_is_positive(self, tmp_path):
        """Dry-run manifest includes positive rendered_prompt_estimate tokens."""
        raw_path = tmp_path / "raw.json"
        press_path = tmp_path / "press.md"
        output_dir = tmp_path / "out"
        raw_path.write_text(json.dumps(RAW_PAYLOAD), encoding="utf-8")
        press_path.write_text(PRESS_CONTEXT, encoding="utf-8")

        dry_run.main(
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
                "cost-test",
            ]
        )

        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        est = manifest["component_estimates"]["rendered_prompt_estimate"]
        assert est["tokens"] > 0
        assert est["bytes"] > 0
        assert len(est["checksum_sha256"]) == 64

    def test_known_models_have_rates(self):
        """All known models in MODEL_RATES produce non-None cost estimates."""
        for model_name in MODEL_RATES:
            cost = estimate_cost_usd(model_name, 1000, 500)
            assert cost is not None, f"Model {model_name} returned None cost"
            assert cost >= 0


# ===========================================================================
# Section 4: Failure handling and fallback behavior
# ===========================================================================


class TestMapperFailureHandling:
    """Tests mapper and reducer failure paths."""

    def test_validate_map_catches_missing_required_fields(self):
        """validate_map returns errors for missing required mapper fields."""
        payload = {"schema_version": "analysis_map_v1"}
        errors = dry_run.validate_map(payload)
        missing_fields = {
            "run_id",
            "week",
            "shard_id",
            "slice",
            "coverage",
            "findings",
            "citations",
            "reference_candidates",
            "provenance",
        }
        for field in missing_fields:
            assert any(field in e for e in errors), f"Missing error for {field}"

    def test_validate_map_catches_wrong_schema_version(self):
        """Wrong schema version produces a validation error."""
        ledger = valid_ledger()
        ledger["schema_version"] = "wrong_version"
        errors = dry_run.validate_map(ledger)
        assert "mapper schema_version mismatch" in errors

    def test_validate_map_catches_failed_status(self):
        """A ledger with status=failed is flagged."""
        ledger = valid_ledger()
        ledger["status"] = "failed"
        errors = dry_run.validate_map(ledger)
        assert "mapper status failed" in errors

    def test_malformed_finding_in_reducer(self):
        """Non-dict findings are rejected as malformed."""
        ledger = valid_ledger()
        ledger["findings"] = ["not-a-dict", 42]

        plan, rejected, _ = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        malformed = [r for r in rejected if r["reason"] == "malformed_finding"]
        assert len(malformed) == 2

    def test_empty_ledger_list_produces_empty_plan(self):
        """Reducing zero ledgers produces an empty selected_claims list."""
        plan, rejected, contradictions = dry_run.reduce_ledgers([], raw_payload=RAW_PAYLOAD)
        assert plan["selected_claims"] == []
        assert rejected == []
        assert contradictions == []

    def test_partial_press_mapper_handles_no_urls(self, tmp_path):
        """Press mapper with no URLs emits partial status, not a crash."""
        press_path = tmp_path / "empty-press.md"
        press_path.write_text("No links here.\n", encoding="utf-8")
        raw_path = tmp_path / "raw.json"
        raw_path.write_text(json.dumps(RAW_PAYLOAD), encoding="utf-8")
        raw_ref = dry_run.file_ref(raw_path)

        result = dry_run.map_press(
            run_id="test",
            week="2026-W21",
            press_path=press_path,
            press_ref=dry_run.file_ref(press_path),
            raw_ref=raw_ref,
        )

        assert result["status"] == "partial"
        assert result["findings"] == []
        assert any("No press URLs" in e for e in result["errors"])

    def test_end_to_end_without_press_context(self, tmp_path):
        """Pipeline still runs when press context is unavailable."""
        raw_path = tmp_path / "raw.json"
        output_dir = tmp_path / "out"
        raw_path.write_text(json.dumps(RAW_PAYLOAD), encoding="utf-8")

        rc = dry_run.main(
            [
                "--raw-json",
                raw_path.as_posix(),
                "--output-dir",
                output_dir.as_posix(),
                "--current-datetime",
                "2026-05-20T12:00:00Z",
                "--run-id",
                "no-press",
            ]
        )

        assert rc == 0
        qa = json.loads((output_dir / "qa-comparison-report.json").read_text(encoding="utf-8"))
        # Should still pass structural checks even without press
        assert qa["checks"]["structural_analysis_gate"]["passed"] is True


# ===========================================================================
# Section 5: Gate output clarity (CI-facing documentation)
# ===========================================================================


class TestGateOutputClarity:
    """Validates that gate failures produce clear, actionable output."""

    def test_validate_map_errors_are_descriptive(self):
        """Each validation error string identifies what failed and why."""
        payload = {
            "schema_version": "wrong",
            "findings": "not-a-list",
        }
        errors = dry_run.validate_map(payload)

        # Every error should be a non-empty string
        for error in errors:
            assert isinstance(error, str)
            assert len(error) > 10, f"Error too terse to be actionable: {error!r}"

    def test_qa_report_identifies_failing_gate(self, tmp_path):
        """QA report structure makes it clear which gate failed."""
        raw_path = tmp_path / "raw.json"
        press_path = tmp_path / "press.md"
        output_dir = tmp_path / "out"
        raw_path.write_text(json.dumps(RAW_PAYLOAD), encoding="utf-8")
        press_path.write_text(PRESS_CONTEXT, encoding="utf-8")

        dry_run.main(
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
                "clarity-test",
            ]
        )

        qa = json.loads((output_dir / "qa-comparison-report.json").read_text(encoding="utf-8"))
        # Each check section has "passed" bool and either "errors" or "expected_failure"
        for gate_name, gate_data in qa["checks"].items():
            assert "passed" in gate_data or "selected" in gate_data, (
                f"Gate {gate_name} missing 'passed' key — CI cannot determine outcome"
            )

    def test_rejected_claims_include_reason(self, tmp_path):
        """Every rejected claim has a reason field for diagnosis."""
        f1 = valid_finding("rej-1", "org/x")
        f1["evidence_refs"] = []  # will be rejected as weak_citation
        f2 = valid_finding("rej-2", "org/y")
        f2["contra_refs"] = ["rej-1"]  # will be rejected as contradiction
        ledger = valid_ledger([f1, f2])

        _, rejected, _ = dry_run.reduce_ledgers([ledger], raw_payload=RAW_PAYLOAD)

        for item in rejected:
            assert "reason" in item, f"Rejected claim missing reason: {item}"
            assert item["reason"] in {
                "weak_citation",
                "unresolved_contradiction",
                "duplicate",
                "malformed_finding",
            }, f"Unknown rejection reason: {item['reason']}"
