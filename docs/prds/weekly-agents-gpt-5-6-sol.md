---
title: Upgrade Weekly Agents to GPT-5.6-Sol Product Requirements Document
description: PRD proposing a model upgrade for the weekly-analysis and weekly-synthesis Copilot CLI agents from gpt-5.5 to gpt-5.6-sol, with evidence, acceptance criteria, and rollback plan
author: Leela (Lead/Architect)
ms.date: 2026-09-08
ms.topic: reference
---
<!-- markdownlint-disable-file -->

Version 1.2 | Status Draft — **editorial quality confirmed; cost validation required before upgrade** | Owner jmservera | Team SquadScope Squad | Lifecycle Definition

> **PRD-only. No production changes in this PR.** This document proposes a future
> change. No agent files, `tier_selector.py`, workflows, pricing code, or tests are
> modified here. Implementation does not begin until jmservera approves this PRD.

## 1. Problem and Context

SquadScope runs a two-step Copilot CLI analysis every week:

- `weekly-synthesis` (`.github/agents/weekly-synthesis.agent.md`, currently `model: gpt-5.5`)
- `weekly-analysis` (`.github/agents/weekly-analysis.agent.md`, currently `model: gpt-5.5`)

Analysis is Copilot-only with no GitHub Models/OpenAI operational fallback, so each
weekly run consumes AI Credits at a measurable, recurring cost. `gpt-5.6-sol` is now
GA on the Copilot CLI. This PRD records the evidence from a model comparison study
(Livingston QA, 2026-09-08) and gates the upgrade decision on sufficient evidence.

**Current evidence verdict: editorial quality confirmed, cost validation required.**
A blinded editorial review (6 articles, W33+W34, random A–F labels) found sol and
astra both outperform gpt-5.5 by a consistent ~1.2-point margin (sol avg 8.60,
astra avg 8.65, baseline avg 7.45/10). The same failure modes appeared in BOTH
baseline weeks independently. Cost evidence across 2 runs is inconclusive (sol
averages +1.2% more expensive than baseline, with high variance). Latency penalty
of +50% for sol is confirmed (W34 serial run: 64s vs 42s). Upgrade path for sol
is supported by editorial evidence; ≥3 additional cost runs needed to confirm
cost neutrality before jmservera approves production change.

## 2. Evidence Summary

Source evidence (Livingston QA model comparison, 2026-09-08), full report:
`/home/azureuser/.copilot/session-state/e1686c39-fa20-4e79-bd06-f50706616fd3/files/model-comparison/comparison-report-v2.md`

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
| W34 (serial) | 42s | 64s | +52% | 99s | +136% |
| W33 (concurrent) | 80s | 119s | +49% | 101s | +26% |
| **Average** | **61s** | **92s** | **+50%** | **100s** | **+64%** |

⚠️ W33 runs were parallel (concurrent processes) — latency values are confounded by
simultaneous machine load. W34 runs were serial and are more reliable.

### Blinded editorial review (6 articles, W33+W34, complete 2026-09-08)

| Model | W33 score | W34 score | Average | vs. baseline |
|-------|-----------|-----------|---------|--------------|
| gpt-5.5 (current) | 7.3 | 7.6 | 7.45 | — |
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

Full verdict: `blinded-review/editorial-verdict.md` in session files.

Pricing source: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing (fetched 2026-09-08).
These are Copilot CLI billing rates, NOT direct Azure/OpenAI API prices.

| Dimension | gpt-5.5 (current) | gpt-5.6-sol (proposed) | gpt-6-astra (rejected) |
|-----------|-------------------|------------------------|------------------------|
| Availability | GA | GA, Copilot CLI | GA, Copilot CLI |
| Avg cost / weekly run | $0.456 | $0.462 (+1.2%) | $1.094 (+140%) |
| Est. annual cost | ~$23.7/yr | ~$24.0/yr | ~$56.9/yr |
| Quality gate (both weeks) | 85/85 | 85/85 | 85/85 |
| Avg latency | 61s | 92s (+50%) | 100s (+64%) |
| Editorial quality | baseline | **inconclusive** | inconclusive |

## 3. Goals and Non-Goals

### Goals

- Confirm cost parity for sol over ≥3 additional runs, then upgrade weekly agents.
- Adopt a GA model that is a drop-in `model:` declaration change for the two weekly
  agents; editorial quality improvement is now evidenced.
- Keep the change auditable and reversible.

### Non-Goals

- No change to `gpt-6-astra` adoption (average +140% cost, no measured quality lift — rejected).
- No change to `tier_selector.py` tier definitions, `docs/model-routing-policy.md`,
  or any non-weekly agent.
- No fix in this PRD to the separately reported cost-tracking bug (tracked in PR #740).
- No change to prompts, gates, retry logic, or workflow orchestration.

## 4. Proposed Future Scope (post-approval)

If approved, implementation is limited to the model declaration in exactly two files:

- `.github/agents/weekly-analysis.agent.md`: `model: gpt-5.5` → `model: gpt-5.6-sol`
- `.github/agents/weekly-synthesis.agent.md`: `model: gpt-5.5` → `model: gpt-5.6-sol`

Optional, only if jmservera expands scope during approval: update model-reference
comments/annotations in `architecture.md`, `docs/model-routing-policy.md`, and
`.github/workflows/crawl-and-publish.yml` to reflect the new weekly model. These are
documentation-only follow-ups and are out of scope unless explicitly approved.

## 5. Acceptance Criteria

1. Both weekly agent files declare `model: gpt-5.6-sol`; no other production file
   changes ship in the implementation PR (unless doc-comment scope is expanded on
   approval).
2. A weekly analysis run on a representative week passes `scripts/analysis_gate.py`
   (`--source copilot-cli --model gpt-5.6-sol`) with no structural, schema, editorial,
   or provenance failures.
3. `gpt-5.6-sol` and `openai/gpt-5.6-sol` remain priced in `scripts/model_pricing.py`
   (delivered by PR #739) so budget/alerting uses correct rates.
4. Existing Python and content gates (`ruff check .`, `ruff format --check .`,
   `pytest tests/`) pass for the implementation change.
5. Measured first-call cost of a post-upgrade run is at or below the gpt-5.5 baseline
   for a comparable input size.

## 6. Validation and Rollback Plan

### Validation

- Run the two-step pipeline on one week end-to-end and confirm the quality gate passes.
- Confirm the produced `data/analyzed/YYYY-WNN-summary.md` meets editorial and schema
  expectations before publish.
- Observe at least one real weekly run (or a manual dispatch) to confirm cost tracks the
  projected −14% first-call reduction.

### Rollback

- Revert the two-line model declarations to `model: gpt-5.5`. The change is a pure
  configuration flip with no schema, data, or interface impact, so rollback is a single
  focused revert PR with no data migration.
- Trigger condition for rollback: any quality-gate regression, editorial-quality
  complaint from jmservera, or Sol availability/GA change.

## 7. Risks and Limitations

- **Blinded editorial review: blinded review complete.** Full verdict in session files.
  Baseline is consistently last; sol and astra tied. Upgrade path is supported.
- **Inconclusive cost evidence.** 2 runs per model with high output-token variance (3.9k–11k
  output tokens). Sol averaged +1.2% more expensive than baseline. ≥3 runs needed.
- **Latency penalty.** Sol averages +50% slower (W34 serial: 64s vs 42s). For pipeline timeout
  budgets, this must be evaluated before upgrade.
- **Concurrent run confound.** W33 latency measurements used parallel processes —
  values are not independent. Only W34 (serial) latency is reliable for pipeline planning.
- **CLI billing basis.** Costs are Copilot CLI AI credits, not direct Azure/OpenAI API
  billing; absolute figures could differ if the pipeline ever migrates providers.
- **Model lifecycle.** GA status can still change; the pricing review cadence
  (`.github/workflows/copilot-pricing-review.yml`, every two months) mitigates drift.

## 8. Approval Gate

This is a PRD-first proposal. **Editorial quality advantage for sol is confirmed (blinded review, 2 weeks). Cost evidence requires ≥3 additional valid runs.** No implementation begins until:

1. At least 3 total cost runs per model (with `--usage-output-file`) show sol ≤ baseline
   average cost on diverse week data.
2. **jmservera explicitly approves this PRD** after reviewing the combined evidence.

On approval, the change is limited to the two agent `model:` declarations per Section 4,
on a dedicated branch/PR, with the weekly quality gate as the blocking acceptance check.

## 9. Source Evidence Reference

- Livingston model comparison report v2 (corrected, primary evidence):
  `/home/azureuser/.copilot/session-state/e1686c39-fa20-4e79-bd06-f50706616fd3/files/model-comparison/comparison-report-v2.md`
- Blinded editorial review (pending):
  `/home/azureuser/.copilot/session-state/e1686c39-fa20-4e79-bd06-f50706616fd3/files/model-comparison/blinded-review/editorial-verdict.md`
- Pricing data (Sol/Astra/Terra/Luna) landed by PR jmservera/SquadScope#739 in
  `scripts/model_pricing.py`.
- Cost tracking bug fix: PR jmservera/SquadScope#740.
- Routing principles: `docs/model-routing-policy.md`.
