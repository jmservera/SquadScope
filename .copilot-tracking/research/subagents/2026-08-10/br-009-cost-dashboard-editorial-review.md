# Subagent Research: BR-009 Cost Dashboard — Farnsworth Editorial/Content Acceptance Review

## Topic / Questions

- Persona: Farnsworth (Analyst/Content Curator), charter at `.squad/agents/farnsworth/charter.md`.
- Task: read-only editorial acceptance review of BR-009 cost dashboard (commit 9af3026d, squash-merge of PR #697), scoped to `layouts/partials/cost-dashboard.html` user-facing copy, assessed against `docs/editorial-style-guide.md`.
- Sub-questions:
  1. Is the copy clear, accurate, honest about limitations, consistent with site voice?
  2. Does this change fall within Farnsworth's routed domain at all?
  3. Verdict: ACCEPT / ACCEPT WITH FOLLOW-UPS / BLOCK / NOT APPLICABLE.

## Findings

### 1. Charter boundaries (`.squad/agents/farnsworth/charter.md`)

- **I own:** weekly analysis markdown, editorial framing (hot/important/trending/missing), tagging/narrative structure for trend reports.
- **I don't handle:** data collection, **frontend implementation**, or architecture decisions.
- `layouts/partials/cost-dashboard.html` is a Hugo partial template — frontend implementation — explicitly listed as out of scope in the charter.

### 2. `docs/editorial-style-guide.md` scope

- Title: "Signal Check: Editorial Prompt & Safety Style Guide". Applies to: "SquadScope: Signal Check podcast script generation" only.
- Entire document is about the two-host podcast script (segment order, claim-ledger sourcing, AI voice disclosure, word counts, prohibited content for podcast scripts).
- Contains zero guidance applicable to Hugo template/UI chrome copy, dashboard labels, or transparency-panel prose. There is no general site-wide voice/tone guide in `docs/` for non-podcast UI copy — the closest analog is the "Editorial Lens" / tone table in `docs/analysis-spec.md` (§ "Tone: Analytical and opinionated... not a GitHub trending page"), but that governs weekly analysis narrative content, not dashboard chrome.
- Conclusion: there is no applicable editorial style guide for this specific artifact type in the repo today.

### 3. Copy inventory from `layouts/partials/cost-dashboard.html`

Rendered user-facing strings (static/prose only, template logic omitted):

- Topline: "Pipeline transparency"
- Heading: "AI pipeline cost"
- Intro sentence: "Reconciled token-usage cost for the automated analysis pipeline. Only the accepted workflow attempt for each stage is counted; retries and no-AI runs are excluded."
- Labels: "Total reconciled spend", "Covers {start} to {end}", "Input tokens", "Output tokens", "Accepted runs", "Generated", "Pricing basis", "Source ledger", "Freshness threshold"
- Details disclosure sentence: "{n} ledger records reconciled to {n} accepted attempts ({n} billable). Excluded: {n} legacy rows without workflow identity, {n} superseded retries, {n} no-AI runs."
- Unavailable-state message: "Cost data is not currently available. The reconciled pipeline cost is generated from accepted, workflow-identified ledger runs and republishes automatically once fresh data clears the freshness and reconciliation checks."

Qualitative read (informal, not against a governing style doc since none applies):
- Tone is plain, factual, non-promotional — consistent with the site's general non-hype posture described elsewhere in `docs/analysis-spec.md` ("Analytical... not a GitHub trending page").
- Honest about limitations: the unavailable-state message explains *why* data may be missing (freshness/reconciliation checks) rather than silently hiding the section or showing a fabricated number — this matches the template's own documented design intent (see the Hugo comment at top of the file: never fall back to an independently maintained total; fail closed on missing/stale/malformed data).
- Some domain jargon ("reconciled", "workflow attempt", "billable", "no-AI runs", "legacy rows without workflow identity") is present but appropriate for a self-described "Pipeline transparency" / provenance panel aimed at readers who want operational detail; the `<details>` disclosure closure (reconciliation/exclusions) is appropriately tucked behind a `<summary>` toggle rather than surfaced by default, which is good progressive-disclosure practice for a niche audience.
- No sentence overclaims accuracy, no marketing language, no unsupported trend/editorial claims (this is operational/provenance copy, not analysis).

### 4. PR/commit context

- Commit 9af3026d referenced as squash-merge of PR #697 (BR-009). Not independently re-fetched via GitHub tools since the task is read-only editorial review of already-known file contents, and the file content read directly reflects the merged state on `main`.

## Follow-on Questions (not pursued — out of original scope)

- None required for this review; the applicability question was the deciding factor and is fully answered by the charter + style-guide scope check.

## Clarifying Questions

- None. The routing question is unambiguous from the charter document.
