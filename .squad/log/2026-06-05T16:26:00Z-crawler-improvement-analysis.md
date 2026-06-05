# Session log: Crawler improvement analysis

Timestamp: 2026-06-05T16:26:00Z

## Brief overview

Squad completed analysis of multi-source external news crawler topology, LLM input strategy, and reliability architecture. Outcome: GitHub issue #237 created; next iteration keeps GitHub crawl monolithic with optional matrix RSS, defers matrix fan-out to triggered conditions, prioritizes bounded in-process parallelism and deterministic merge-before-analyze flow.

## Key decision

Lead decision: keep in-process bounded RSS parallelism for now; add schema versioning, per-source metrics, and deterministic merge before analysis. Defer matrix fan-out to when RSS stage exceeds 60s p95, source count exceeds ~10–15, or per-source credentials/quota becomes necessary.

## Deliverables

1. **Bender**: Crawler parallelism analysis — topology options (in-process A, matrix B, hybrid C); recommendation C (hybrid staged); acceptance criteria.
2. **Farnsworth**: LLM input strategy — options (raw dumps, merged, staged source-specific, compact); recommendation compact press-context; token budget <= 8k.
3. **Fry**: Reliability assessment — findings (GitHub dominates, in-process fast but poor isolation); recommendation matrix with fail-fast: false; tests and metrics.
4. **Leela**: Issue #237 created; routing to Bender (implementation), Fry (reliability), Farnsworth (quality).

## Output files

- `.squad/decisions.md`: Merged 4 inbox decisions; size after merge: 36240 bytes (was 25779).
- `.squad/orchestration-log/`: 4 agent logs (Bender, Farnsworth, Fry, Leela).
- `.squad/log/{timestamp}-crawler-improvement-analysis.md`: This file.

## Next session

Bender owns implementation of issue #237; focus on per-source metrics, schema versioning, merge/validate step, tests for partial failures and dedupe.
