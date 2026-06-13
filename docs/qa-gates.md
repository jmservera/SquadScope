# QA Gates: Map/Reduce Acceptance Criteria

This document describes the automated QA gates that validate matrix crawl and
map/reduce changes before rollout (see issue #438).

## Gate Structure

The gates live in `tests/test_qa_gates_map_reduce.py` and run as part of the
standard `python -m pytest` CI step. No additional workflow configuration is
needed.

### 1. Reducer Correctness (`TestReducerDeterministicFanIn`, `TestReducerCitationPreservation`, `TestReducerContradictionHandling`)

| Gate | What it checks | Failure meaning |
|------|---------------|-----------------|
| Deterministic fan-in | Same input → same output, order-independent | Reducer has non-deterministic behavior |
| Duplicate collapse | Same normalized key is deduplicated | Duplicate claims leak to editorial plan |
| Citation preservation | Repo/article bindings survive reduce | Published claims would lack evidence links |
| Weak citation rejection | Findings without evidence_refs rejected | Unsupported claims reach output |
| Contradiction handling | Mutual/one-sided contradictions rejected | Conflicting claims not caught |

### 2. End-to-End Dry-Run (`TestEndToEndDryRun`)

| Gate | What it checks | Failure meaning |
|------|---------------|-----------------|
| Full pipeline QA pass | Complete run produces `status: passed` | Pipeline broke a contract |
| Mapper contracts valid | Every mapper ledger passes `validate_map` | Schema/coverage violation in mapper |
| Sidecars present | rejected-claims.json & contradictions.json exist | Audit trail missing |
| Never publish eligible | manifest.publish_eligible is always False | Dry-run could accidentally publish |
| Provenance expected failure | Provenance gate fails as expected | Dry-run wrongly claims AI provenance |
| Candidate has links | Output markdown contains repo hyperlinks | Citation rendering broken |

### 3. Cost/Token Guardrails (`TestCostTokenGuardrails`)

| Gate | What it checks | Failure meaning |
|------|---------------|-----------------|
| Over-budget rejection | 2M char file → preflight fails | Cost guard is disabled |
| Under-budget pass | Small file → preflight passes | False positive blocking pipeline |
| Custom cap | Tighter cap triggers failure | Cap override broken |
| Unknown model fails | Unrecognized model → exit 1 | Silent pass on unknown pricing |
| Token determinism | Same file → same estimate | Non-deterministic budget |
| Missing file → 0 tokens | Missing path doesn't crash | Pipeline crash on optional inputs |
| Manifest token estimate | rendered_prompt_estimate > 0 | Token accounting missing from artifacts |
| All models have rates | Every MODEL_RATES entry yields cost | Pricing table incomplete |

### 4. Failure Handling (`TestMapperFailureHandling`)

| Gate | What it checks | Failure meaning |
|------|---------------|-----------------|
| Missing required fields | validate_map catches all missing fields | Schema violation undetected |
| Wrong schema version | Version mismatch flagged | Version drift undetected |
| Failed status flagged | status=failed → error | Silent failure |
| Malformed findings | Non-dict findings rejected | Crash on bad data |
| Empty ledger list | Zero ledgers → empty plan | Crash on empty input |
| No-URL press mapper | Partial status, no crash | Press mapper crash |
| No press context | Pipeline completes without press | Hard dependency on optional input |

### 5. Gate Output Clarity (`TestGateOutputClarity`)

| Gate | What it checks | Failure meaning |
|------|---------------|-----------------|
| Descriptive errors | Each error > 10 chars, actionable | CI errors too terse to debug |
| Gate identification | QA report has `passed` key per gate | CI can't determine which gate failed |
| Rejection reasons | Every rejected claim has a reason | No diagnosis path for rejections |

## Running Locally

```bash
python -m pytest tests/test_qa_gates_map_reduce.py -v
```

## CI Integration

These tests run in the existing CI workflow (`.github/workflows/ci.yml`) under
the `python -m pytest` step. No additional configuration required — pytest
autodiscovers the test file.

## Interpreting Failures

When a gate fails in CI:

1. The test name tells you which category failed (e.g., `TestCostTokenGuardrails::test_preflight_rejects_over_budget`)
2. The assertion message identifies the specific contract violation
3. The QA report JSON (`qa-comparison-report.json`) provides structured gate-by-gate results with error lists

If `test_full_pipeline_produces_passing_qa` fails, inspect the QA report's
`checks` object carefully. The schema varies by gate:

- `mapper_contracts` includes `passed` plus `errors_by_mapper`
- `structural_analysis_gate` and `evidence_and_editorial_gates` include `passed`
  plus `errors`
- `publish_provenance_gate` includes `passed`, `expected_failure`, and `errors`
- `sidecars_present` includes `passed` plus emitted object counts
- `reference_count` is informational only and reports `selected`,
  `notable_projects`, and `press_articles`
