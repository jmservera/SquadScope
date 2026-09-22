---
title: Upgrade Weekly Agents to GPT-5.6-Sol Product Requirements Document
description: PRD proposing a model upgrade for the weekly-analysis and weekly-synthesis Copilot CLI agents from gpt-5.5 to gpt-5.6-sol, with evidence, acceptance criteria, and rollback plan
author: Leela (Lead/Architect)
ms.date: 2026-09-22
ms.topic: reference
---
<!-- markdownlint-disable-file -->

> **ACTIVE — IMPLEMENTATION SHIPPED; POST-UPGRADE VALIDATION BLOCKED**
> The model upgrade shipped in
> [#745](https://github.com/jmservera/SquadScope/pull/745), but the post-upgrade
> lifecycle criteria are not complete. PR
> [#774](https://github.com/jmservera/SquadScope/pull/774) archived this PRD
> before issue [#779](https://github.com/jmservera/SquadScope/issues/779)
> completed acceptance. This document is restored to `docs/prds/` pending an
> explicit owner decision and/or comparable instrumented telemetry.

Version 1.3 | Status **Implemented; validation incomplete/blocked** | Owner jmservera | Team SquadScope Squad | Lifecycle Definition

> **Approval boundary.** The 2026-09-08 owner approval authorized implementing
> Sol while cost evidence was still preliminary. No explicit owner-approved
> exception has been found that waives the post-upgrade acceptance criteria or
> authorizes lifecycle closure with incomplete or invalid comparison evidence.

## 1. Problem and Context

At the time of this proposal, SquadScope ran a two-step Copilot CLI analysis
with the following baseline:

- `weekly-synthesis` (`.github/agents/weekly-synthesis.agent.md`, then `model: gpt-5.5`)
- `weekly-analysis` (`.github/agents/weekly-analysis.agent.md`, then `model: gpt-5.5`)

Analysis is Copilot-only with no GitHub Models/OpenAI operational fallback, so each
weekly run consumes AI Credits at a measurable, recurring cost. `gpt-5.6-sol` is now
GA on the Copilot CLI. This PRD records the evidence from a model comparison study
(Livingston QA, 2026-09-08) and gates the upgrade decision on sufficient evidence.

**Current lifecycle verdict: qualified editorial acceptance; measurement
acceptance blocked.**
A blinded editorial review (6 articles, W33+W34, separate-context Squad child agent,
label-blinded) found sol and astra both score higher than gpt-5.5 in a subjective
2-packet assessment (sol avg 8.60, astra avg 8.65, baseline avg 7.45/10). This is
not a confirmed population improvement — one reviewer, 2 source weeks, coordinator-
authored brief. Cost evidence across 2 runs is inconclusive (sol averages +1.2% more
expensive). All latency measurements are confounded (all W33 and W34 runs ran as
concurrent parallel processes).

Post-upgrade W38/W39 evidence confirms that publication gates passed and finds
no immediate editorial rollback trigger. It does not provide the required
per-agent usage, cache, cost, runtime-model, or isolated provider-latency
measurements. The owner must decide whether to retain Sol provisionally while
collecting comparable evidence or execute the documented rollback.

## 2. Evidence Summary

The Livingston QA model comparison (2026-09-08) supplied the historical
proposal evidence summarized below. Its original machine-local session
artifacts are not retained in the repository and are historical context only;
they are not the canonical source trail for the current lifecycle disposition.
The repository-retained Fry and Farnsworth reports and linked GitHub records
in Section 9 are the durable current evidence.

⚠️ **W35 comparison voided**: the original W35 runs were invalid — `--model` CLI flag
does not override an agent's `model:` field; all three W35 runs used gpt-5.5.
Valid data is W33 + W34 (two runs per model, worktree isolation, confirmed by
`--usage-output-file` → `currentModel` field).

### Measured per-run costs (Copilot CLI AI credits; 1 credit = $0.01 USD)

| Week | gpt-5.5 | gpt-5.6-sol | delta | gpt-6-astra | delta |
|------|---------|-------------|-------|-------------|-------|
| W34 | $0.396 | $0.338 | −15% | $1.075 | +171% |
| W33 | $0.516 | $0.585 | +13% | $1.112 | +115% |
| **Average** | **$0.456** | **$0.462** | **+1.2%** | **$1.094** | **+140%** |

⚠️ High output-token variance (3.9k–11k) drives cost swings. Sol was cheaper in
W34 but more expensive in W33. With only 2 samples, cost comparison is inconclusive.

### Latency

| Week | gpt-5.5 | gpt-5.6-sol | delta | gpt-6-astra | delta |
|------|---------|-------------|-------|-------------|-------|
| W34 (concurrent) | 42s | 64s | +52% | 99s | +136% |
| W33 (concurrent) | 80s | 119s | +49% | 101s | +26% |
| **Average** | **61s** | **92s** | **+50%** | **100s** | **+64%** |

⚠️ **All latency measurements confounded** — all W33 and W34 runs used concurrent
parallel processes. No latency figure is a reliable serial measurement.

### Blinded editorial review (6 articles, W33+W34, complete 2026-09-08)

| Model | W33 score | W34 score | Average | vs. baseline |
|-------|-----------|-----------|---------|--------------|
| gpt-5.5 (proposal baseline) | 7.3 | 7.6 | 7.45 | — |
| gpt-5.6-sol | 8.2 | 9.0 | 8.60 | **+1.15 points** |
| gpt-6-astra | 8.7 | 8.6 | 8.65 | +1.20 points |

Key findings (reviewer had no model/cost knowledge during review):
- gpt-5.5 ranked last in both weeks; same failure modes reproduced in both: "blind
  spot missing own exhibit" (both W33 and W34 baseline articles), unsupported
  predictions (both), provenance conflation (both), near-zero metric specificity.
- sol and astra effectively tied; sol is the better editor (narrative coherence,
  contrastive citation); astra is the better fact-checker (most verified exact metrics).
- Astra has a fixable schema bug: missing `predictions` block in both articles.
- All 3 models miss non-agent top repos (pipeline/prompt selection bias, not model-specific).
- Zero hallucinated repositories across 116 citations.

The blinded editorial review completed on 2026-09-08. Its historical verdict
is summarized above; the original machine-local session file is not
repository-resolvable.

Pricing source: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing (fetched 2026-09-08).
These are Copilot CLI billing rates, NOT direct Azure/OpenAI API prices.

| Dimension | gpt-5.5 (proposal baseline) | gpt-5.6-sol (proposed) | gpt-6-astra (rejected) |
|-----------|-------------------|------------------------|------------------------|
| Availability | GA | GA, Copilot CLI | GA, Copilot CLI |
| Avg cost / weekly run | $0.456 | $0.462 (+1.2%) | $1.094 (+140%) |
| Est. annual cost | ~$23.7/yr | ~$24.0/yr | ~$56.9/yr |
| Quality gate (both weeks) | 85/85 | 85/85 | 85/85 |
| Avg latency | 61s | 92s (+50%) | 100s (+64%) |
| Editorial quality | baseline | **inconclusive** | inconclusive |

### Post-upgrade scheduled-run evidence (W37–W39)

Issue [#779](https://github.com/jmservera/SquadScope/issues/779) evaluates:

- W37 baseline run
  [34082521901](https://github.com/jmservera/SquadScope/actions/runs/34082521901)
- W38 Sol run
  [34806779896](https://github.com/jmservera/SquadScope/actions/runs/34806779896)
- W39 Sol run
  [35561779454](https://github.com/jmservera/SquadScope/actions/runs/35561779454)

All three final and per-attempt `analysis_gate` reports passed with zero
structural/schema, editorial, evidence-citation, or AI-provenance errors and no
repair actions. W38 and W39 declarations, gate metadata, manifests, and ledger
rows identify `gpt-5.6-sol`; however, the retained logs contain no
`currentModel` or equivalent runtime usage field independently confirming the
executed model.

The retained ledger contains one estimated analysis row per run:

| Week | Recorded model | Estimated input | Estimated output | Retained estimated cost |
|------|----------------|----------------:|-----------------:|------------------------:|
| W37 | `copilot-default` | 25,210 | 3,055 | $0.121455 |
| W38 | `gpt-5.6-sol` | 24,966 | 3,009 | $0.160044 |
| W39 | `gpt-5.6-sol` | 24,884 | 3,013 | $0.159796 |

These values require three distinct interpretations:

1. **Retained ledger comparison:** W39 is 31.57% more expensive than the
   retained W37 row despite 1.30% fewer estimated total tokens (W38 is 31.77%
   more expensive with 1.03% fewer tokens). This arithmetic is correct for the
   stored rows.
2. **Attribution defect:** W37's two agent declarations were `gpt-5.5`, while
   its ledger and gate attribution used `copilot-default` pricing. PR
   [#740](https://github.com/jmservera/SquadScope/pull/740) documented this
   defect. Therefore the retained W37 cost is not a valid model-normalized
   GPT-5.5 baseline.
3. **Corrected pricing reconstruction:** Repricing W37's same estimated tokens
   at the repository's GPT-5.5 rates produces $0.217700. Against that
   reconstructed estimate, W38 is 26.48% cheaper and W39 is 26.60% cheaper.
   This is analysis-only reconstruction, not measured billing. It still omits
   synthesis usage, cached-input and cache-write counts, and provider-measured
   per-call cost.

The scheduled evidence has no separate synthesis ledger row, no per-agent
input/output/cache measurements, no cache counts, no measured provider charge,
and no isolated provider latency. Analysis-path and GitHub Actions step
durations include local preparation, CLI handling, gates, and ledger work and
must not be represented as provider latency.

### Post-upgrade editorial evidence

W38 and W39 support **qualified editorial acceptance**:

- no material provenance conflation was found;
- reader-facing analysis is evidence-aware and materially specific;
- all four gate families passed, and both reports received
  `quality_score: 100`;
- no immediate editorial rollback trigger was found.

Bounded weaknesses remain:

- each retained candidate includes unsupported `up`, `down`, or `flat`
  directional predictions even though the evidence is a single snapshot and
  all reviewed records have `stars_gained: null`;
- several material press-side claims lack reader-visible references even
  though sources exist in retained artifacts;
- some claims use vague magnitude language where exact values were available.

The score of 100 proves structural, citation-presence, section-depth, and basic
judgment-language checks passed. It does **not** prove claim-level correctness,
evidence for prediction direction, support in retained press summaries, or
reference completeness.

## 3. Goals and Non-Goals

### Goals

- Obtain an explicit owner decision on provisional retention versus rollback.
- If Sol is retained provisionally, collect comparable instrumented telemetry
  for both weekly agent calls, including runtime model identity, input/output
  and cache tokens, measured cost, input size, and isolated provider latency.
- Keep the shipped change auditable and reversible.

### Non-Goals

- No change to `gpt-6-astra` adoption (average +140% cost, no measured quality lift — rejected).
- No change to `tier_selector.py` tier definitions, `docs/model-routing-policy.md`,
  or any non-weekly agent.
- No fix in this PRD to the separately reported cost-tracking bug (tracked in PR #740).
- No change to prompts, gates, retry logic, or workflow orchestration.

## 4. Implemented Scope

- `.github/agents/weekly-analysis.agent.md`: `model: gpt-5.5` → `model: gpt-5.6-sol`
- `.github/agents/weekly-synthesis.agent.md`: `model: gpt-5.5` → `model: gpt-5.6-sol`

PR #745 also aligned `.github/workflows/crawl-and-publish.yml` attribution
literals and `tests/test_pipeline.py` expectations.

## 5. Acceptance Criteria

1. Both weekly agent files declare `model: gpt-5.6-sol`, with workflow and test
   consistency surfaces aligned. **Satisfied by PR #745.**
2. A weekly analysis run on a representative week passes `scripts/analysis_gate.py`
   (`--source copilot-cli --model gpt-5.6-sol`) with no structural, schema,
   editorial, or provenance failures. **Satisfied for W38 and W39.**
3. `gpt-5.6-sol` and `openai/gpt-5.6-sol` remain priced in `scripts/model_pricing.py`
   (delivered by PR #739) so budget/alerting uses correct rates. **Satisfied.**
4. Existing Python and content gates (`ruff check .`, `ruff format --check .`,
   `pytest tests/`) pass for the implementation change. **Satisfied for the
   implementation PR's applicable checks; this does not substitute for
   post-upgrade measurement.**
5. Measured first-call cost of a post-upgrade run is at or below the gpt-5.5 baseline
   for a comparable input size. **Blocked/not proven.** The retained rows are
   estimated and aggregate only the analysis stage; W37 is misattributed, and
   the reconstructed GPT-5.5 comparison is not measured billing.
6. Record per-agent runtime model, input/output/cache tokens, measured cost,
   input size, and isolated provider latency. **Blocked.** Scheduled artifacts
   do not retain these measurements.

## 6. Validation and Rollback Plan

### Validation status

- End-to-end W38 and W39 scheduled runs passed the publication gates.
- Editorial review supports qualified acceptance, with unresolved prediction
  evidence and reference-completeness weaknesses.
- Comparable cost and per-agent telemetry remain unavailable. Lifecycle
  closure is blocked pending an owner decision and/or instrumented evidence.

### Rollback

- Effective model selection is reverted by changing the two agent declarations
  to `model: gpt-5.5`.
- A consistent focused rollback PR must also align
  `.github/workflows/crawl-and-publish.yml` gate/ledger attribution literals
  and `tests/test_pipeline.py` expectations. This is the same four-file shape
  used by PR #745.
- No data migration, schema change, prompt change, or interface change is
  required.
- Existing triggers remain any quality-gate regression, owner-reported
  editorial regression, or Sol availability/GA change. The current lifecycle
  decision additionally requires the owner to choose whether incomplete
  comparable telemetry warrants provisional retention or rollback.

## 7. Risks and Limitations

- **Blinded editorial review: complete.** The historical verdict is summarized
  in Section 2; its original machine-local session file is not
  repository-resolvable. Baseline is consistently last; sol and astra tied.
  Upgrade path is supported.
- **Post-upgrade cost remains unproven.** The retained W37 row makes W38/W39
  about 31.6% more expensive, but W37 was incorrectly attributed and priced as
  `copilot-default`. Correcting only the pricing makes Sol about 26.5% cheaper,
  but that reconstruction still uses estimated tokens and omits
  synthesis/cache/provider billing.
- **Measurement granularity is insufficient.** Scheduled evidence lacks
  per-agent usage and cost, runtime `currentModel`, cache counts, and isolated
  provider latency.
- **Editorial acceptance is qualified.** Gate and reviewer findings support
  retaining the output on editorial grounds, but unsupported directional
  predictions and incomplete reader-visible references remain bounded
  weaknesses.
- **Latency penalty.** Sol averages +50% in observed measurements, but all runs were concurrent parallel processes — these figures are not reliable serial measurements. Dedicated serial latency benchmarks required before pipeline timeout assessment.
- **Concurrent run confound.** All W33 and W34 latency measurements used parallel processes —
  values are not independent. No latency figure from this study is reliable for pipeline planning.
- **CLI billing basis.** Costs are Copilot CLI AI credits, not direct Azure/OpenAI API
  billing; absolute figures could differ if the pipeline ever migrates providers.
- **Model lifecycle.** GA status can still change; the pricing review cadence
  (`.github/workflows/copilot-pricing-review.yml`, every two months) mitigates drift.

## 8. Approval Gate

**IMPLEMENTATION APPROVED by jmservera, 2026-09-08T14:29:49Z.**
("approve Sol for now on")

Scope: SquadScope weekly-analysis and weekly-synthesis agents only. Not all CLI agents or
unrelated repos. Implementation branch: `feat/weekly-agents-gpt-5-6-sol`.

This approval permitted implementation before sufficient cost evidence was
available. It is not recorded as an exception approving post-upgrade lifecycle
closure with incomplete or invalid measurement evidence.

**Current owner decision required:** choose either:

1. retain Sol provisionally while comparable instrumented evidence is
   collected for both weekly calls; or
2. execute the four-file consistent rollback described in Section 6.

## 9. Source Evidence Reference

The durable, canonical source trail for the current issue-779 lifecycle
disposition is:

- Fry measurement and gate evidence:
  `.copilot-tracking/research/2026-09-22/issue-779-fry-measurement-evidence.md`.
- Farnsworth editorial evidence:
  `.copilot-tracking/research/2026-09-22/issue-779-farnsworth-editorial-evidence.md`.
- Post-upgrade disposition:
  [issue jmservera/SquadScope#779](https://github.com/jmservera/SquadScope/issues/779).
- Owner decision request:
  [issue jmservera/SquadScope#780](https://github.com/jmservera/SquadScope/issues/780).
- W37, W38, and W39 scheduled runs:
  [34082521901](https://github.com/jmservera/SquadScope/actions/runs/34082521901),
  [34806779896](https://github.com/jmservera/SquadScope/actions/runs/34806779896),
  and
  [35561779454](https://github.com/jmservera/SquadScope/actions/runs/35561779454).
- Pricing data:
  [PR jmservera/SquadScope#739](https://github.com/jmservera/SquadScope/pull/739)
  and `scripts/model_pricing.py`.
- Cost attribution defect:
  [PR jmservera/SquadScope#740](https://github.com/jmservera/SquadScope/pull/740).
- Implementation:
  [PR jmservera/SquadScope#745](https://github.com/jmservera/SquadScope/pull/745).
- Premature archival:
  [PR jmservera/SquadScope#774](https://github.com/jmservera/SquadScope/pull/774).
- Routing principles: `docs/model-routing-policy.md`.

The corrected Livingston comparison report and completed blinded editorial
verdict were created as machine-local session artifacts during the original
proposal work. They are not retained in this repository and cannot be resolved
by repository readers. Their historical results remain summarized in Section
2, but they are not the auditable source of the current lifecycle verdict.
