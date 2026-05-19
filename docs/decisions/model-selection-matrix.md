# Model Selection Decision Matrix

## Current Configuration

| Task | Model | Cost/Run | Quality Req | Notes |
|------|-------|----------|-------------|-------|
| Weekly Analysis | Claude Sonnet 4 | ~$0.35 | quality_score ≥ 60 | Primary, full context |
| Reskill | Claude Sonnet 4 | ~$0.10 | N/A (advisory) | Lower token count |
| Fallback Analysis | GitHub Models GPT-4.1 | ~$0.25 | quality_score ≥ 50 | When Copilot CLI unavailable |
| Budget Mode | GPT-4.1 | ~$0.20 | quality_score ≥ 50 | Truncated context |
| Minimal Mode | GPT-5 mini | ~$0.05 | quality_score ≥ 40 | Top 30 repos only |
| Scoring | Local (no AI) | $0.00 | N/A | Heuristic-based |
| Pre-flight | Local (no AI) | $0.00 | N/A | Token counting only |

## Decision Criteria

1. Monthly budget remaining > 50%: use Claude Sonnet 4
2. Monthly budget 20-50%: switch to GPT-4.1
3. Monthly budget < 20%: switch to GPT-5 mini
4. Monthly budget exhausted: emergency mode (raw stats only)

## Quality Thresholds

- Below quality_score 40: reject and retry with better model
- Below quality_score 50: acceptable for budget mode only
- Above quality_score 60: production quality

## Evolution Plan

- Review monthly based on accumulated quality data
- Adjust thresholds if model pricing changes
- Consider direct Anthropic API if caching becomes critical
