# Historical Context Injection for Weekly Analysis (#401)

## Goal

Add a bounded `HISTORICAL CONTEXT` preamble to the weekly analysis prompt so Farnsworth can:

- maintain continuity across weeks,
- recognize multi-week patterns,
- revisit open predictions and blind spots,
- do all of that without diluting the primacy of the current week's raw JSON.

## Architecture

### New module

Add `scripts/assemble_historical_context.py`.

Responsibilities:

1. Read historical source artifacts from `content/`.
2. Extract the most analysis-relevant slices from each source.
3. Compress each slice to a per-source target.
4. Enforce a global historical-context budget:
   - target: ~1500 words,
   - hard ceiling: never more than 15% of the total prompt-token budget.
5. Return one assembled markdown string ready for prompt injection.

### Source inputs

The assembler reads these sources in priority order:

1. `content/rolling/last-month.md`
   - rolling 4-week continuity
   - target: 500 words
2. Previous week's summary
   - derived from the prior analyzed weekly markdown already resolved by `find_previous_summary()`
   - target: 200 words
3. `content/monthly/YYYY/MM.md`
   - month-in-progress notes
   - target: 200 words
4. `content/yearly/YYYY.md` (optional)
   - longer narrative arc
   - target: 500 words

The module extracts focused sections instead of dumping whole files:

- previous week: frontmatter `summary` + `Signal & Noise` + `Blind Spots` + `The Week Ahead`
- monthly: `Month Overview` + `Trends Observed` + `Key Takeaways`
- yearly: `Year in Review` + `Biggest Trends` + `Predictions Review`
- rolling: whole rolling report body

## Integration point

Historical context is assembled inside `scripts/analyze_fallback.py` during prompt rendering, before preflight budget evaluation and before any LLM invocation.

Flow:

1. Load/sanitize raw weekly JSON.
2. Resolve previous summary with `find_previous_summary()`.
3. Call `assemble_historical_context(...)`.
4. Inject the returned markdown into `{{HISTORICAL_CONTEXT}}`.
5. Run existing prompt preflight / compaction logic.

This keeps the feature inside the current weekly analysis pipeline without changing the workflow contract.

## Prompt preamble format

`prompts/analyze-weekly.md` gains a new preamble block under `## Inputs`:

```md
### Historical context

Treat this as low-priority continuity scaffolding, not as the evidence base for this week's call. It is a bounded digest of recent rollups and prior takeaways. If it conflicts with the current raw JSON, the current raw JSON wins.

<untrusted-content>
{{HISTORICAL_CONTEXT}}
</untrusted-content>
```

Important prompt behavior:

- historical context is explicitly lower-weight than current data,
- it is fenced as untrusted content,
- it is continuity guidance, not permission to override present-week evidence.

## Budget management

Two limits apply:

1. **Word target:** ~1500 words total across all historical sections.
2. **Prompt-share cap:** historical context may consume at most **15%** of the configured prompt-token budget.

Implementation detail:

- each section is first compressed to its nominal word budget,
- the assembled result is then iteratively reduced until it fits both:
  - the word cap,
  - and the token cap derived from `prompt_token_budget * 0.15`.

This makes the feature safe for both the default 90k-token preflight and smaller future prompt budgets.

## Source priority and compression policy

Recency wins when over budget.

Priority retained longest:

1. rolling last 4 weeks
2. previous week takeaways
3. current month notes
4. yearly narrative

When over budget:

1. compress yearly first,
2. then monthly,
3. then previous week,
4. rolling is reduced last.

If the prompt budget is extremely tight, lower-priority sections can be dropped entirely before the rolling context is removed.

## Files changed

### Prompt / security

- `prompts/analyze-weekly.md`
  - add `{{HISTORICAL_CONTEXT}}` preamble section
- `scripts/lint_prompts.py`
  - classify `{{HISTORICAL_CONTEXT}}` as untrusted

### Pipeline

- `scripts/assemble_historical_context.py`
  - new bounded historical-context assembler
- `scripts/analyze_fallback.py`
  - call the assembler during prompt construction
  - expose `--content-root`
  - include the assembled context in prompt preflight components

### Tests

- `tests/test_assemble_historical_context.py`
- `tests/test_analyze_fallback.py`

## Draft implementation notes

This draft intentionally avoids generating new rollups inside the assembler. It assumes:

- rolling context is produced by `scripts/generate_rollups.py --rolling`,
- monthly/yearly artifacts already exist when available.

If a source is missing, the assembler skips it cleanly; the weekly prompt still renders.
