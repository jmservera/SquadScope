# Design: Synthesized month summaries

**Issue:** #398  
**Status:** Proposed  
**Branch:** `design/398-month-synthesis`

## Goal

Replace the current month page opening, which is effectively a week-by-week ledger, with a generated narrative summary of the completed month. The summary should compress 4-5 weekly reports into ~300 words of editorial insight while preserving links to the underlying weekly pages.

## Current state

`scripts/generate_rollups.py` already:

- loads weekly summaries from `data/analyzed/*-summary.md`
- groups them by `(year, month)`
- renders monthly Hugo pages with four append-only sections:
  - `Month Overview`
  - `Top Repos This Month`
  - `Trends Observed`
  - `Key Takeaways`

It also has a lightweight rolling synthesis path (`--rolling`) that proves the script is already the right place to assemble multi-week context.

## Proposal

Add a synthesized month artifact and inject it into monthly rollups when a month is complete.

### New artifact

Generate and cache one markdown file per completed month:

`data/analyzed/YYYY-MM-month-synthesis.md`

This keeps the LLM output versioned alongside weekly analyses and gives yearly rollups a stable source instead of reparsing monthly Hugo pages.

## Architecture

### New data flow

1. `generate_rollups()` loads all weekly summaries.
2. `build_monthly_pages()` groups summaries by month.
3. For each month, call `ensure_month_synthesis(...)` **before** building `RollupPage.sections`.
4. `ensure_month_synthesis(...)`:
   - checks whether the month is closed
   - builds a compressed month input pack from the month’s weekly summaries
   - reuses an existing synthesis artifact when `weeks_covered` still matches
   - otherwise invokes the LLM path
   - falls back cleanly if generation fails
5. `build_monthly_pages()` inserts the synthesized narrative at the top of the monthly page, then keeps the existing weekly detail sections.
6. `build_yearly_pages()` prefers month synthesis artifacts for yearly narrative sections; if missing, it falls back to the current weekly-derived text.

### Integration point in `generate_rollups.py`

The LLM call should not happen in `main()`. It should happen inside the monthly builder path, immediately after `items = sorted(...)` in `build_monthly_pages()`, because that is where:

- the full set of weekly inputs for the month is available
- the script knows whether the month is complete
- the resulting synthesis can be attached to the correct `RollupPage`

Recommended helper split:

- `is_completed_month(month_key, all_month_keys) -> bool`
- `build_month_synthesis_pack(items) -> str`
- `ensure_month_synthesis(items, analyzed_dir, content_root, now) -> MonthSynthesis | None`
- `load_month_synthesis(path) -> MonthSynthesis`

The actual model invocation should live in a new helper module (for example `scripts/month_synthesis.py`) patterned after `scripts/analyze_fallback.py`, so `generate_rollups.py` stays focused on rollup assembly.

## Prompt template

Create `prompts/synthesize-month.md`.

The prompt should ask for one coherent narrative, not bullets, and should explicitly cover:

- what defined the month overall
- which trends emerged, accelerated, peaked, or faded
- surprises vs. confirmed patterns
- which weekly predictions held up or weakened

The model should write a cached month-synthesis markdown artifact with:

- YAML frontmatter
- a one-sentence `summary`
- a ~300 word narrative body

## Input format

The LLM should not receive 4-5 raw weekly pages verbatim unless needed. Instead it should receive a compressed month pack rendered from parsed weekly fields already available in `WeeklySummary`.

### Compression pipeline

For each weekly summary, extract:

- `week`
- `title`
- `summary`
- `top_repo`
- `tags`
- `signal`
- `noise`
- `gaps`
- `conclusion`
- `featured_repos` (cap at top 5)
- `predictions` from frontmatter when present

Then render a deterministic digest for the prompt:

```md
### 2026-W23
- Thesis: ...
- Top repo: owner/repo
- Tags: ...
- Signal: ...
- Noise: ...
- Gaps: ...
- Week-ahead prediction: ...
- Referenced repos: ...
```

Budget guidance:

- keep `summary` intact
- trim `signal`/`noise`/`gaps`/`conclusion` to sane character limits
- cap repo lists
- include only the previous month synthesis, not the entire yearly page, for continuity

This reduces prompt size while preserving the editorial signal needed for synthesis.

## Output format

Suggested cached artifact format:

```md
---
title: "June 2026 Month Synthesis"
date: "2026-07-07T06:53:00Z"
month: "2026-06"
weeks_covered: ["2026-W23", "2026-W24", "2026-W25", "2026-W26"]
categories: ["monthly-synthesis"]
summary: "June turned agent skills from novelty into distribution infrastructure while GitHub spam tactics kept mutating."
status: "generated"
source_checksum: "sha256:..."
---

## Month Synthesis

~300 words of narrative prose.
```

`source_checksum` should be computed from the compressed month pack so reruns can detect when a weekly source changed and invalidate the cached synthesis.

## Month boundary detection

The monthly synthesis should run only for **closed** months.

### Rule

A month is closed when at least one later weekly summary exists.

Examples:

- W24 is the latest week in June and no July week exists yet → June is **not** closed
- the first July weekly summary lands → June becomes **closed**
- rerunning the first July week is safe because the cached June synthesis is reused unless `source_checksum` changed

### Implementation sketch

```python
def is_completed_month(target: tuple[int, int], all_items: list[WeeklySummary]) -> bool:
    return any((item.year, item.month) > target for item in all_items)
```

This matches the workflow requirement: the first successful run after a month change synthesizes the previous month.

## Fallback behavior

If Copilot CLI / GitHub Models is unavailable, times out, or returns invalid output:

1. log a warning
2. do not write a broken synthesis artifact
3. generate the monthly page using the **current enumeration format**
4. set frontmatter metadata such as `synthesis_status: "fallback"` on the monthly page if desired
5. keep yearly rollups on the current weekly-derived fallback path

This preserves publishability and keeps the site generation path fail-open for the monthly summary enhancement while leaving weekly details intact.

## Hugo integration

### Monthly page

Keep the current page and links, but prepend a new section:

1. `Month Synthesis`
2. `Month Overview`
3. `Top Repos This Month`
4. `Trends Observed`
5. `Key Takeaways`

Recommended monthly frontmatter additions:

- `summary` — one-sentence thesis from the month synthesis artifact
- `synthesis_status` — `generated` or `fallback`
- `synthesis_weeks` — copied from the synthesis artifact

This gives Hugo list pages and social previews a usable summary while preserving the detailed weekly sections below.

### Yearly page

Change yearly rollups to consume month synthesis artifacts first:

- `Year in Review` and `What Changed` should summarize by month, not by week, when synthesis exists
- the existing weekly fallback remains for older months or failed syntheses

This satisfies the requirement that month summaries feed the yearly report.

## Operational notes

- Reuse the existing model/fallback pattern from `scripts/analyze_fallback.py`
- Keep prompt rendering fenced with `<untrusted-content>` because weekly summaries are prior LLM output
- Store the synthesis artifact in `data/analyzed/` so both publish and sync workflows already carry it forward
- Do not remove the existing monthly sections; they remain the audit trail and source links

## Testing plan

Add tests for:

1. completed-month detection
2. no synthesis for open/current month
3. synthesis artifact reuse when `weeks_covered` and checksum match
4. fallback to existing monthly page structure on model failure
5. yearly rollup preference for month synthesis artifacts
6. prompt lint passing for `prompts/synthesize-month.md`

## Implementation sequence

1. add `prompts/synthesize-month.md`
2. add month-synthesis helper module
3. extend `generate_rollups.py` to detect closed months and reuse/cache syntheses
4. update yearly rollup assembly to prefer month syntheses
5. add tests
