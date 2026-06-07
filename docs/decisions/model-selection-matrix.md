# Model Selection Decision Matrix

Pricing source: [GitHub Copilot Models and Pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing), fetched 2026-06-06. Review prices every two months.

Scheduled reminder: `.github/workflows/copilot-pricing-review.yml` checks this cadence every two months and opens/updates a review issue; pricing changes still require a normal PR.

## Current Configuration

| Task | Model | Cost/Run | Quality Req | Notes |
|------|-------|----------|-------------|-------|
| Weekly Analysis | Claude Sonnet 4 | ~$0.35 | quality_score ≥ 60 | Primary, full context |
| Reskill | Claude Sonnet 4 | ~$0.10 | N/A (advisory) | Lower token count |
| Copilot Failure Diagnosis | No AI | $0.00 | N/A | Copilot failures fail closed or produce publish-ineligible diagnostics; no GitHub Models/OpenAI fallback |
| Budget Mode | Copilot GPT-5.4 mini | ~$0.08 | quality_score ≥ 50 | Truncated context, still through Copilot |
| Minimal Mode | GPT-5 mini | ~$0.05 | quality_score ≥ 40 | Top 30 repos only |
| Scoring | Local (no AI) | $0.00 | N/A | Heuristic-based |
| Pre-flight | Local (no AI) | $0.00 | N/A | Token counting only |

## Decision Criteria

1. Monthly budget remaining > 50%: use Claude Sonnet 4
2. Monthly budget 20-50%: switch Copilot model to GPT-5.4 mini
3. Monthly budget < 20%: switch to GPT-5 mini
4. Monthly budget exhausted: diagnostic no-AI mode only (raw stats are publish-ineligible; no AI fallback)

## Quality Thresholds

- Below quality_score 40: reject and retry with better model
- Below quality_score 50: acceptable for budget mode only
- Above quality_score 60: production quality

## Evolution Plan

- Review model pricing every two months and quality data monthly
- Adjust thresholds if model pricing changes
- Consider direct Anthropic API if caching becomes critical
