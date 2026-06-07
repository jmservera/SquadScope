# PRD: Cost Estimation and Optimization for Token-Based Copilot Billing

**Author:** Leela (Lead/Architect)  
**Date:** 2026-05-19  
**Status:** Draft  
**Relates to:** docs/PRD.md, .squad/decisions.md (CI Architecture Decision)

---

## Executive Summary

SquadScope runs automated AI analysis weekly using GitHub Copilot CLI inside GitHub Actions; analysis is Copilot-only and has no GitHub Models/OpenAI operational fallback. With GitHub Copilot's shift to token-based consumption billing (AI Credits at $0.01/credit), every pipeline run has a measurable cost. This PRD quantifies per-run and annual costs, projects context growth over 6–12 months, and defines optimization strategies and budget controls to keep SquadScope economically sustainable as a zero-revenue open-source project.

**Key finding:** A weekly analysis run costs approximately **$0.27–$0.35** in AI credits. The annual projection table totals **$16.18/year** at current configuration. Accounting for context growth (5–10% over 12 months), diagnostic no-AI candidate runs after Copilot failures, and variance in weekly token counts, the realistic annual range is **$16–$20/year** — comparable to a cheap newsletter service, and orders of magnitude cheaper than a human analyst.

---

## Problem Statement

### Why Cost Matters for Automated Copilot Usage

1. **Predictability:** Unlike interactive Copilot chat (included in subscription), automated CI invocations consume tokens that count against plan allowances and incur overage charges.
2. **Context growth:** SquadScope's wisdom, skills, and history accumulate over time, making each run progressively more expensive unless managed.
3. **Budget transparency:** As a personal open-source project, jmservera needs clear visibility into the marginal cost of each published page.
4. **Plan selection:** Understanding token consumption informs whether Copilot Pro ($10/month, 300 credits included) or Copilot Pro+ ($39/month, 1500 credits) is the right tier.
5. **Graceful degradation:** If token budgets are exhausted, the pipeline must degrade gracefully (use cheaper models, skip optional enrichment) rather than fail silently.

---

## Token Pricing Model Summary

*(Source: [GitHub Copilot Models and Pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing), fetched 2026-06-06. Prices must be reviewed every two months.)*

The notification-only `.github/workflows/copilot-pricing-review.yml` workflow runs every two months and opens or updates a GitHub issue when pricing data is due for manual review. It must not mutate pricing tables directly; changes go through code/docs/tests and PR review.

### Core Concepts

- **1 AI Credit = $0.01 USD**
- Tokens are consumed for: input (prompt + context), cached input (reused context), and output (generated text)
- Plans include monthly credit allowances; overage billed at per-token rates
- Code completions remain unlimited on paid plans (not relevant to SquadScope CI)

### Relevant Model Pricing (per 1M tokens)

| Model | Category | Input | Cached Input | Output | Cache Write |
|-------|----------|------:|-------------:|-------:|------------:|
| GPT-5 mini | OpenAI | $0.25 | $0.025 | $2.00 | — |
| GPT-5.3-Codex | OpenAI | $1.75 | $0.175 | $14.00 | — |
| GPT-5.4 (≤272K input) | OpenAI | $2.50 | $0.25 | $15.00 | — |
| GPT-5.4 (>272K input) | OpenAI | $5.00 | $0.50 | $22.50 | — |
| GPT-5.4 mini | OpenAI | $0.75 | $0.075 | $4.50 | — |
| GPT-5.4 nano | OpenAI | $0.20 | $0.02 | $1.25 | — |
| GPT-5.5 (≤272K input) | OpenAI | $5.00 | $0.50 | $30.00 | — |
| GPT-5.5 (>272K input) | OpenAI | $10.00 | $1.00 | $45.00 | — |
| Claude Haiku 4.5 | Anthropic | $1.00 | $0.10 | $5.00 | $1.25 |
| **Claude Sonnet 4 / 4.5 / 4.6** (primary) | Anthropic | $3.00 | $0.30 | $15.00 | $3.75 |
| Claude Opus 4.5 / 4.6 / 4.7 / 4.8 | Anthropic | $5.00 | $0.50 | $25.00 | $6.25 |
| Gemini 2.5 Pro | Google | $1.25 | $0.125 | $10.00 | — |
| Gemini 3 Flash | Google | $0.50 | $0.05 | $3.00 | — |
| Gemini 3.1 Pro (≤200K input) | Google | $2.00 | $0.20 | $12.00 | — |
| Gemini 3.1 Pro (>200K input) | Google | $4.00 | $0.40 | $18.00 | — |
| Gemini 3.5 Flash | Google | $1.50 | $0.15 | $9.00 | — |
| Raptor mini | Fine-tuned/GitHub | $0.25 | $0.025 | $2.00 | — |
| MAI-Code-1-Flash | Microsoft | $0.75 | $0.075 | $4.50 | — |

### Plan Allowances

| Plan | Monthly Credits | Equivalent $ | Notes |
|------|----------------|--------------|-------|
| Copilot Free | ~13.33 | $0.13 | Very limited |
| Copilot Pro | 300 | $3.00 | Likely sufficient for SquadScope alone |
| Copilot Pro+ | 1500 | $15.00 | Generous headroom |
| Copilot Business | 200/user pooled | $2.00/user | Org billing |

---

## Cost Breakdown per Pipeline Stage

### Tokenization Assumptions

- Average ~4 characters per token (English text/markdown)
- JSON is less efficient: ~3.5 characters per token due to structural characters
- 1 KB of prose ≈ 250 tokens; 1 KB of JSON ≈ 285 tokens

### Stage 1: Weekly Analysis (Copilot CLI — Claude Sonnet 4)

| Component | Size | Estimated Tokens |
|-----------|------|-----------------|
| Analyze prompt template | 6.5 KB | ~1,625 |
| Raw weekly JSON (`data/raw/2026-W21.json`) | 301 KB | ~86,000 |
| Wisdom file (`.squad/identity/wisdom.md`) | 3.2 KB | ~800 |
| Skills directory (currently empty) | 0 KB | 0 |
| Previous week summary | ~5 KB | ~1,250 |
| System/tool overhead (Copilot CLI framing) | ~2 KB | ~500 |
| **Total input tokens** | **~318 KB** | **~90,175** |

| Output Component | Size | Estimated Tokens |
|------------------|------|-----------------|
| Analyzed summary markdown | ~5 KB | ~1,250 |
| Tool calls/internal reasoning overhead | ~3 KB | ~750 |
| **Total output tokens** | **~8 KB** | **~2,000** |

**Weekly analysis cost (Claude Sonnet 4):**

```
Input:  90,175 tokens × $3.00/1M = $0.2705
Output:  2,000 tokens × $15.00/1M = $0.0300
─────────────────────────────────────────────
Total per weekly run:              ≈ $0.30
```

**In AI Credits: ~30 credits per weekly run.**

### Stage 2: Reskill (Every 5th Week — Copilot CLI — copilot-default)

The reskill run is larger because it reads 5 weeks of history plus snapshot data.

| Component | Size | Estimated Tokens |
|-----------|------|-----------------|
| Reskill prompt template | 2.9 KB | ~725 |
| Last 5 analyzed summaries (5 × ~5 KB) | ~25 KB | ~6,250 |
| Wisdom file | 3.2 KB | ~800 |
| Skills directory (growing) | ~2 KB (month 6) | ~500 |
| Star snapshot context (5 weeks) | ~15 KB | ~4,285 |
| Quality trend report | ~2 KB | ~500 |
| **Total input tokens** | **~50 KB** | **~13,060** |

| Output Component | Size | Estimated Tokens |
|------------------|------|-----------------|
| Reskill report | ~4 KB | ~1,000 |
| Wisdom updates | ~1 KB | ~250 |
| **Total output tokens** | **~5 KB** | **~1,250** |

**Reskill cost (copilot-default at Claude Sonnet 4 rates):**

```
Input:  13,060 tokens × $3.00/1M = $0.0392
Output:  1,250 tokens × $15.00/1M = $0.0188
─────────────────────────────────────────────
Total per reskill run:             ≈ $0.058
```

**In AI Credits: ~6 credits per reskill run.**

### Stage 3: Copilot Failure Diagnosis (No GitHub Models/OpenAI fallback)

When Copilot CLI fails, weekly analysis must fail closed or produce a diagnostic no-AI candidate artifact that is publish-ineligible. There is no GitHub Models/OpenAI analysis fallback configured, so cost tooling may estimate alternate Copilot model choices but must not present GitHub Models as an operational recovery path.

```
Publishable AI output: none
AI token cost for diagnostic no-AI artifact: $0.00
Operator action: inspect Copilot failure classification, token/auth issue, and workflow logs
```

### Stage 4: GitHub Actions Compute

| Job | Runner | Duration (est.) | Cost |
|-----|--------|-----------------|------|
| Crawl | ubuntu-latest | ~3 min | Free (public repo) |
| Analyze | ubuntu-latest | ~2 min | Free (public repo) |
| Generate | ubuntu-latest | ~1 min | Free (public repo) |
| Deploy | ubuntu-latest | ~2 min | Free (public repo) |
| Reskill | ubuntu-latest | ~2 min | Free (public repo) |

**GitHub Actions is free for public repositories.** If the repo becomes private, estimate ~10 minutes/run × $0.008/min = $0.08/run.

---

## Context Growth Projections

### Growth Vectors

| Component | Current Size | Growth Rate | 6-Month Projection | 12-Month Projection |
|-----------|-------------|-------------|--------------------|--------------------|
| Wisdom.md | 3.2 KB | +0.5 KB per reskill (~every 5 weeks) | 5.8 KB | 8.4 KB |
| Skills directory | 0 KB | +1 KB per reskill (new skill files) | 5.2 KB | 10.4 KB |
| Raw JSON (per file) | 301 KB | Stable (weekly crawl scope fixed) | 301 KB | 301 KB |
| Star snapshots (per file) | ~3 KB | Stable per file, linear file count | 78 KB total | 156 KB total |
| Previous summary | 5 KB | Stable (only last week sent) | 5 KB | 5 KB |
| Analyzed archive | 5 KB × weeks | Linear growth | 130 KB (26 files) | 260 KB (52 files) |

### Token Cost Trajectory

| Timeframe | Weekly Input Tokens | Weekly Cost | Reskill Input Tokens | Monthly Cost (4.3 weeks + 0.86 reskill amortized) |
|-----------|--------------------:|------------:|---------------------:|---:|
| Month 1 (now) | 90,175 | $0.30 | 13,060 | $1.32 |
| Month 6 | 92,300 (+2.4%) | $0.31 | 16,200 (+24%) | $1.36 |
| Month 12 | 94,500 (+4.8%) | $0.32 | 19,500 (+49%) | $1.40 |

**Key insight:** Context growth is modest because the dominant cost driver (raw JSON at 86K tokens) is stable. Wisdom and skills growth adds only ~2-5% annually to weekly runs. Reskill grows faster (24-49%) because it accumulates more historical context, but it runs infrequently.

---

## Cost per Page Calculation

### Annual Cost Projection (Year 1)

| Line Item | Frequency | Unit Cost | Annual Cost |
|-----------|-----------|-----------|-------------|
| Weekly analysis (Claude Sonnet 4) | 52/year | $0.30 | $15.60 |
| Reskill (copilot-default / Claude Sonnet rates) | ~10/year | $0.058 | $0.58 |
| GitHub Actions compute | 52/year | $0.00 (public) | $0.00 |
| **Total annual AI cost** | | | **$16.18** |

### Cost per Published Page

```
Annual AI cost / 52 pages = $16.18 / 52 = $0.311 per page
```

Including amortized reskill:
```
($15.60 + $0.58) / 52 = $0.311 per page (reskill is small)
```

### Comparative Analysis

| Approach | Annual Cost | Cost per Page | Quality |
|----------|-------------|---------------|---------|
| **SquadScope (automated)** | **~$16/year** | **$0.311** | Consistent, opinionated, improving |
| Human analyst (freelance) | $5,200–$10,400/year | $100–$200 | High but variable |
| Newsletter service (Substack Pro) | $600/year | $11.50 | Platform cost only, still need writer |
| Manual GPT-4 chat (copy-paste) | ~$50/year | ~$1 | Inconsistent, no learning loop |

**SquadScope is 300× cheaper than a human analyst and offers compounding quality via reskill.**

---

## Cost Optimization Strategies

### Strategy 1: Model Selection by Task Criticality

| Task | Current Model | Optimized Model | Savings |
|------|---------------|-----------------|---------|
| Weekly analysis | Claude Sonnet 4 ($0.30) | GPT-5 mini ($0.023 input + $0.004 output) | **91%** |
| Reskill | copilot-default / Claude Sonnet rates ($0.058) | Keep Copilot-only; no GitHub Models fallback | 0% |
| Copilot failure diagnosis | No AI ($0.00) | Fail closed or produce publish-ineligible diagnostic artifact | N/A |

**Recommendation:** Start with Claude Sonnet 4 for quality. If quality_score consistently ≥ 75, experiment with GPT-5.4 mini, GPT-5 mini, or Claude Haiku 4.5 for weekly analysis. Reserve premium models for reskill where judgment quality matters most.

### Strategy 2: Context Window Management

1. **Summarize raw JSON before sending:** Instead of sending 301 KB of raw JSON, pre-process to extract only the fields used by the prompt (~50 KB, saving ~60% of input tokens).
2. **Cap wisdom.md:** Establish a 5 KB soft limit. During reskill, retire obsolete heuristics rather than only appending.
3. **Compress star snapshots:** For reskill, send only delta summaries rather than full snapshot JSON.

**Potential savings:** 40-60% reduction in input tokens = ~$0.12–$0.18 savings per weekly run.

### Strategy 3: Skip-If-Unchanged (Caching)

If the crawled data has fewer than N significant changes from the prior week (e.g., <5 new repos, <10% topic shift), skip analysis and republish last week's summary with an "unchanged" note.

**Potential savings:** 5-15% of annual runs skipped = $0.80–$2.40/year.

**Risk:** Breaks the "every week has a page" contract. Implement as opt-in only.

### Strategy 4: Token Budget per Run

Set a hard cap on total tokens per invocation:

```yaml
env:
  SQUADSCOPE_TOKEN_BUDGET: 150000  # tokens
  SQUADSCOPE_COST_CAP: 0.50       # USD per run
```

If pre-calculated token estimate exceeds budget:
1. Truncate raw JSON to top 50 repos by stars_gained
2. Omit skills context
3. Shorten previous summary to frontmatter-only

### Strategy 5: Prompt Optimization

| Optimization | Token Savings | Effort |
|--------------|---------------|--------|
| Remove output template (model knows format) | ~500 tokens | Low |
| Shorten editorial stance to bullet points | ~200 tokens | Low |
| Inline wisdom into prompt (skip file read) | ~100 tokens | Medium |
| Use structured JSON output instead of markdown | ~300 output tokens | Medium |

**Combined prompt optimization: ~1,100 tokens saved = ~$0.004/run (marginal).**

Prompt optimization has low ROI because the raw JSON dominates input cost. Focus on Strategy 2 (context window management) first.

### Strategy 6: Cached Input Optimization

If the Copilot CLI supports prompt caching (reusing context across calls), the 86K raw JSON tokens could be served at cached rates:

```
Cached: 86,000 × $0.30/1M = $0.026 (vs $0.258 uncached)
Savings: $0.232 per run = 77% reduction on the JSON portion
```

**Status:** Copilot CLI caching behavior is not yet documented for CI invocations. Monitor for updates.

---

## Monitoring & Alerting Design

### Per-Run Token Tracking

1. **Copilot CLI transcript:** The `--share=PATH` flag exports a session transcript. Parse it post-run to extract actual token counts.
2. **API-compatible response metadata (general tooling only):** The cost ledger can parse OpenAI-compatible `usage` JSON for non-analysis experiments, but weekly analysis remains Copilot-only and does not use GitHub Models/OpenAI fallback.
3. **Workflow annotations:** Log token estimates and actuals as workflow summary annotations.

### Implementation

```yaml
- name: Log token usage
  if: always()
  run: |
    # Parse Copilot CLI transcript for usage data
    if [ -f copilot-session.md ]; then
      python3 scripts/track_token_usage.py \
        --transcript copilot-session.md \
        --stage analysis \
        --week "$WEEK"
    fi
```

### Usage Dashboard

Store per-run metrics in `data/metrics/token-usage.jsonl`:

```json
{"week": "2026-W21", "stage": "analysis", "model": "claude-sonnet-4", "input_tokens": 90175, "output_tokens": 2000, "cost_usd": 0.30, "timestamp": "2026-05-19T08:00:00Z"}
```

Render a simple chart on the SquadScope site (Hugo shortcode or static SVG) showing:
- Weekly cost trend
- Cumulative annual spend
- Context size growth

### Budget Alerts

| Threshold | Action |
|-----------|--------|
| Single run > $0.50 | Warning annotation in workflow summary |
| Single run > $1.00 | Fail the run, open issue |
| Monthly cumulative > $5.00 | Email alert via GitHub Actions notification |
| Monthly cumulative > $10.00 | Auto-switch to GPT-5 mini for remaining month |

---

## Budget Controls (Hard Limits, Graceful Degradation)

### Tiered Degradation Strategy

```
Normal Mode (cost < $0.50/run)
  └─ Full analysis with Claude Sonnet 4
  └─ Full context (raw JSON + wisdom + skills + prior week)

Budget Mode (cost would exceed $0.50/run)
  └─ Switch to GPT-5.4 mini (saves ~74%)
  └─ Truncate raw JSON to top 100 repos
  └─ Omit skills context

Minimal Mode (monthly budget exhausted)
  └─ Switch to GPT-5 mini (saves ~91%)
  └─ Truncate raw JSON to top 30 repos
  └─ Omit all optional context
  └─ Quality gate threshold lowered to 50

Emergency Mode (all credits exhausted)
  └─ Skip AI analysis entirely
  └─ Produce diagnostic/staged no-AI artifact only; publish-ineligible
  └─ Open issue for manual intervention
```

### Pre-flight Cost Estimation

Before invoking the model, estimate cost:

```python
from scripts.model_pricing import estimate_cost_usd


def estimate_cost(input_tokens: int, output_estimate: int, model: str) -> float | None:
    # Centralized implementation lives in scripts/model_pricing.py.
    return estimate_cost_usd(
        model,
        input_tokens=input_tokens,
        output_tokens=output_estimate,
    )
```

---

## Implementation Plan

### Issues to Create

| # | Title | Priority | Effort | Dependencies |
|---|-------|----------|--------|--------------|
| 1 | Add pre-flight token estimation to analyze workflow | High | S | None |
| 2 | Implement `scripts/track_token_usage.py` for post-run metrics | High | M | None |
| 3 | Create `data/metrics/token-usage.jsonl` schema and writer | Medium | S | #2 |
| 4 | Add budget alerts to workflow (annotations + issue creation) | Medium | M | #2 |
| 5 | Implement tiered degradation (model downgrade on budget) | Medium | M | #1 |
| 6 | Pre-process raw JSON to reduce token count (Strategy 2) | Medium | M | None |
| 7 | Add wisdom.md size cap and retirement policy to reskill | Low | S | None |
| 8 | Create cost dashboard Hugo shortcode | Low | L | #3 |
| 9 | Investigate Copilot CLI caching for CI (Strategy 6) | Low | S | None |
| 10 | Document model selection decision matrix | Low | S | None |

### Phasing

- **Phase A (immediate):** Issues 1–3 — visibility into actual costs
- **Phase B (month 2):** Issues 4–6 — active cost management
- **Phase C (month 3+):** Issues 7–10 — optimization and documentation

---

## Open Questions

| # | Question | Impact | Proposed Resolution |
|---|----------|--------|---------------------|
| OQ1 | Does Copilot CLI expose actual token usage in transcript or exit metadata? | High — needed for accurate tracking | Spike: parse `--share` output for usage data |
| OQ2 | Does `copilot-requests: write` permission on GITHUB_TOKEN consume from org pool or personal allowance? | High — affects billing entity | Test in workflow with usage monitoring |
| OQ3 | Is prompt caching available for Copilot CLI in non-interactive mode? | Medium — could save 77% on JSON input | Monitor GitHub changelog |
| OQ4 | What's the actual token count for the raw JSON? (estimated 86K, need actuals) | Medium — calibration | Add tokenizer count in pre-flight step |
| OQ5 | How does GitHub bill for the Copilot CLI invocation itself vs. the underlying model tokens? | High — may have additional overhead | Review billing after first month |
| OQ6 | Can Copilot CLI expose more detailed actual token usage for cache/cached-input accounting? | Medium — affects estimate precision | Review Copilot CLI release notes and billing exports |
| OQ7 | What happens when the Copilot Pro credit allowance is consumed mid-month? | High — operational risk | Set up overage alerts, test degradation path |

---

## Appendix: Token Estimation Methodology

### Tokenization Rules of Thumb

- English prose: ~4 characters/token (or ~0.75 words/token)
- JSON with short keys: ~3.5 characters/token
- Markdown with formatting: ~3.8 characters/token
- Code: ~3.2 characters/token

### Validation Approach

Once `scripts/track_token_usage.py` is live, compare estimates against actuals for 4 weeks. Adjust multipliers if estimates deviate by >20%.

### Raw JSON Breakdown (2026-W21.json = 301 KB)

Estimated token distribution:
- Structural JSON characters (`{}[],:"`): ~20% = ~17K tokens
- Repository names, URLs, descriptions: ~50% = ~43K tokens  
- Numeric fields (stars, dates): ~15% = ~13K tokens
- Topic arrays: ~15% = ~13K tokens
- **Total: ~86K tokens** (at 3.5 chars/token)

---

*This PRD will be updated with actuals once token tracking is implemented (Phase A, Issues 1–3).*
