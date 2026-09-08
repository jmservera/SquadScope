---
title: Upgrade Weekly Agents to GPT-5.6-Sol Product Requirements Document
description: PRD proposing a model upgrade for the weekly-analysis and weekly-synthesis Copilot CLI agents from gpt-5.5 to gpt-5.6-sol, with evidence, acceptance criteria, and rollback plan
author: Leela (Lead/Architect)
ms.date: 2026-09-08
ms.topic: reference
---
<!-- markdownlint-disable-file -->

Version 1.0 | Status Draft — approval pending | Owner jmservera | Team SquadScope Squad | Lifecycle Definition

> **PRD-only. No production changes in this PR.** This document proposes a future
> change. No agent files, `tier_selector.py`, workflows, pricing code, or tests are
> modified here. Implementation does not begin until jmservera approves this PRD.

## 1. Problem and Context

SquadScope runs a two-step Copilot CLI analysis every week:

- `weekly-synthesis` (`.github/agents/weekly-synthesis.agent.md`, currently `model: gpt-5.5`)
- `weekly-analysis` (`.github/agents/weekly-analysis.agent.md`, currently `model: gpt-5.5`)

Analysis is Copilot-only with no GitHub Models/OpenAI operational fallback, so each
weekly run consumes AI Credits at a measurable, recurring cost. `gpt-5.6-sol` is now
GA on the Copilot CLI and is cheaper than `gpt-5.5` while delivering comparable
quality in a controlled comparison. This PRD asks whether the two weekly agents should
move from `gpt-5.5` to `gpt-5.6-sol`.

This aligns with the "cost first, unless code is being produced" governing principle in
`docs/model-routing-policy.md`: the weekly agents produce editorial analysis, not code,
so a cheaper model of comparable quality is preferred if quality gates hold.

## 2. Evidence Summary

Source evidence (Livingston QA model comparison, 2026-09-08), full report:
`/home/azureuser/.copilot/session-state/e1686c39-fa20-4e79-bd06-f50706616fd3/files/model-comparison/comparison-report.md`
(single-run comparison on input week 2026-W35; CLI AI-credit billing, not direct API).

| Dimension | gpt-5.5 (current) | gpt-5.6-sol (proposed) |
|-----------|-------------------|------------------------|
| Availability | GA | GA, accessible via Copilot CLI |
| First-call cost / weekly run | $0.224 | $0.192 (−14%) |
| Retry cost (cache hit) | $0.224 | $0.072 (−68%) |
| Est. annual pipeline cost | ~$14.00 | ~$11.00 (−21%) |
| Quality gate | Passed (score 85) | Passed (score 82) |
| Output size | 12,885 bytes | 13,112 bytes |
| Duration | 53s | 52s |

Pricing verified against GitHub Copilot billing docs (fetched 2026-09-08) and now
present in `scripts/model_pricing.py` via PR #739 (Sol default rates
input $4 / cached $0.40 / cache_write $5 / output $20 per 1M tokens). The Sol
cache-write rate was confirmed live: 22.5K tokens × $5/M = $0.1125.

Both models passed all structural, schema, editorial, and provenance gates. No
hallucinated repositories were detected in any run.

## 3. Goals and Non-Goals

### Goals

- Reduce recurring weekly analysis cost (−14% first call, −68% retries, ~−21% annual)
  without regressing quality gates.
- Adopt a GA model that is a drop-in `model:` declaration change for the two weekly
  agents.
- Keep the change auditable and reversible.

### Non-Goals

- No change to `gpt-6-astra` adoption (2.1× cost, no measured quality lift — rejected).
- No change to `tier_selector.py` tier definitions, `docs/model-routing-policy.md`,
  or any non-weekly agent.
- No fix in this PRD to the separately reported cost-tracking bug (analysis logged as
  `copilot-default` instead of the actual agent model). That is tracked independently.
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

- **Single-run evidence.** The comparison is one run per model on one week; stochastic
  model variance means quality deltas (85 vs 82) are within editorial noise, not a
  statistically significant ranking. Gate pass/fail is the reliable signal, and both
  passed.
- **Editorial variance.** In the single run, Sol omitted a "gap" prediction and chose an
  anchor repo (`deepseek-harness`) as top repo rather than the sharper W35-specific
  signal. This is within normal editorial variance but should be watched over the first
  few live weeks.
- **CLI billing basis.** Costs are Copilot CLI AI credits, not direct Azure/OpenAI API
  billing; absolute figures could differ if the pipeline ever migrates providers.
- **Cache assumptions.** Retry savings assume cache hits on the stable prompt prefix;
  real savings depend on cache warmth.
- **Model lifecycle.** A GA model can still change price or availability; the pricing
  review cadence (`.github/workflows/copilot-pricing-review.yml`, every two months)
  mitigates drift.

## 8. Approval Gate

This is a PRD-first proposal. No production agent files, `tier_selector.py`, workflows,
pricing code, or tests are modified by this PR. Implementation (Section 4) begins only
after **jmservera explicitly approves this PRD**. On approval, the change proceeds on a
dedicated branch and PR per the repository Branch and Pull Request Workflow, with the
weekly quality gate as the blocking acceptance check.

## 9. Source Evidence Reference

- Livingston model comparison report (primary evidence):
  `/home/azureuser/.copilot/session-state/e1686c39-fa20-4e79-bd06-f50706616fd3/files/model-comparison/comparison-report.md`
- Pricing data (Sol/Astra/Terra/Luna) landed by PR jmservera/SquadScope#739 in
  `scripts/model_pricing.py`.
- Routing principles: `docs/model-routing-policy.md`.
- Cost model context: `docs/processed/PRD-cost-estimation.md`.
