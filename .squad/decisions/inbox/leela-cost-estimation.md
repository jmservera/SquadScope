# Decision Proposal: Cost Estimation Framework for SquadScope

**Date:** 2026-05-19T05:17:53.102+02:00  
**Author:** Leela (Lead/Architect)  
**Status:** Proposed  
**PRD:** docs/PRD-cost-estimation.md

## Summary

SquadScope's automated Copilot CLI and GitHub Models API usage has a quantifiable cost under token-based billing. At current configuration (~$0.30/week), annual cost is ~$16 — well within Copilot Pro's 300 credits/month allowance. However, proactive monitoring and budget controls are needed before context growth or model upgrades change the picture.

## Decisions Proposed

1. **Accept current cost profile as sustainable** — $16/year is economically trivial; no immediate action required on model downgrade.
2. **Implement token usage tracking (Phase A)** — Add `scripts/track_token_usage.py` and `data/metrics/token-usage.jsonl` to establish baselines before optimizing.
3. **Set budget alert thresholds** — Warn at $0.50/run, fail at $1.00/run, email alert at $5/month cumulative, auto-switch to cheaper model at $10/month cumulative (aligned with PRD budget alerts table).
4. **Defer raw JSON pre-processing** — The 40-60% savings is significant but adds pipeline complexity; implement only if costs grow beyond $30/year.
5. **Wisdom.md cap at 5 KB** — Reskill should retire obsolete heuristics, not only append.

## Rationale

The dominant cost driver (raw JSON at 86K tokens) is stable and bounded by crawl scope. Growth comes from wisdom/skills/history accumulation, which is slow. Premature optimization would add complexity without meaningful savings at current scale.

## Risks

- OQ5/OQ6: Billing mechanics for Copilot CLI vs Models API may differ in ways not yet visible
- Credit exhaustion mid-month would disrupt the weekly pipeline if no degradation path exists

## Next Steps

- Create implementation issues per PRD Phase A (tracking)
- Validate actual token counts against estimates after 4 weeks of data
