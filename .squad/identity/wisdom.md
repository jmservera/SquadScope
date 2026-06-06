---
last_updated: 2026-05-18T15:22:25.067+02:00
---

# Team Wisdom

Reusable patterns and heuristics learned through work. NOT transcripts — each entry is a distilled, actionable insight.

## Patterns

## Signal Detection Patterns

- **Practical utility beats novelty theater.** Treat repositories as signal when they clearly reduce workflow friction, solve recurring engineering pain, or make production work more trustworthy.
- **Clustered movement matters more than one loud launch.** A single popular repo is not a trend; multiple repositories and topics pulling in the same direction usually signal durable ecosystem movement.
- **Operational credibility is a strong positive signal.** Favor projects that show observability, maintenance discipline, packaging clarity, or workflow realism over broad autonomy claims.
- **Research counts when it changes practice.** Research-heavy repos can be signal, but only when they point toward credible adoption, new workflows, or meaningful technical movement beyond demos.

## Noise / Hype Detection Patterns

- **Stars without deltas are popularity, not momentum.** Treat attention as directional when `stars_gained` or historical baselines are missing; do not overstate it as trend acceleration.
- **Marketing-heavy wrappers are usually weak signal.** Thinly differentiated agent launches, clone products, and branding-first repos deserve skepticism unless the implementation meaningfully changes capability or cost.
- **Exploit, bypass, and cheat churn distort the picture.** These repos may be active, but they are usually editorial noise unless they reveal a deeper defensive or ecosystem shift.
- **If the promise sounds bigger than the evidence, call it hype.** Strong claims without technical differentiation, adoption evidence, or operational substance are noise until proven otherwise.

## Gap Analysis Focus Areas

- **Look for absent infrastructure around known pain.** Missing testing, observability, defensive security, maintenance, or reliability tooling is often more important than another crowded launch category.
- **Name what should exist but does not.** Useful gap analysis points to concrete missing categories, not generic wishes for “more innovation.”
- **Track ecosystem balance, not just heat.** When one area dominates attention, check which adjacent needs are being ignored or underfunded.
- **Missing baselines are themselves a gap.** If the pipeline lacks enough historical data to validate momentum or hindsight, say so explicitly.

## Trend Detection Approaches

- **Compare week-to-week whenever possible.** Look for continuity, acceleration, reversal, or broadening rather than treating each weekly crawl as isolated.
- **Use topic counts as supporting evidence only.** `signals.top_topics` can confirm a pattern, but topic frequency alone does not prove significance.
- **Prefer repeated technical themes over brand repetition.** Trend calls should come from recurring problem/solution patterns, not from the same large projects staying visible.
- **Be explicit about uncertainty.** Honest caveats improve trust; if momentum data or historical context is thin, the analysis should say so rather than pretend precision.
- **Analysis schemas must be single-sourced across prompt, spec, gate, and diagnostics.** Optional prediction registries are only safe when every generated example includes the same machine-validated fields and deterministic repairs are auditable before publish eligibility.
