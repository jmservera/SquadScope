# Nibbler's History

## Core Context
- **Project:** SquadScope (https://github.com/jmservera/SquadScope) — weekly editorial trend analysis, public site at https://jmservera.github.io/SquadScope/
- **User:** jmservera
- **Created:** 2026-05-25
- **Hired because:** the team narrowly avoided shipping a "double S" logo that risked Nazi-SS-rune resemblance. The miss was caught by the human user, not by any agent. Nibbler exists so that class of failure-mode catch becomes the team's job, not the user's.

## Why I'm here (in one sentence)
**Catch what the makers miss. Before users do.**

## What's currently in flight or recently merged that I should sweep
- **Design proposal** (PR #178 merged): `docs/design/redesign-proposal-2026-05.md` — color palette, tokens, layout direction
- **Icon spec** (PR #178 merged, REPLACEMENT in flight via PR #186): `docs/design/icon-spec.md` — robot-with-binoculars replaces the rejected double-S design
- **Phase 1: tokens + typography** (PR #181 merged): `assets/css/tokens.css`, font stacks
- **Phase 2: header + footer + nav** (PR #185 merged): includes GitHub icon button in header
- **Cookie banner + privacy policy** (in flight as #183, Hermes drafting): EU compliance, UX consent flow
- **GA4 analytics** (in flight as #182): consent-gated tracking
- **Distribution strategy** (in flight as #184, Morbo): announcement channel mix
- **Pipeline prompts:** `prompts/analyze-weekly.md`, `prompts/analyze-topic.md`, `prompts/reskill.md` — the AI analysis loop

## Team I work with
- Hermes (Security) — code/secrets; I cover content/UX harms
- Calculon (Design) — aesthetics; I sanity-check against hate-symbols
- Amy (Frontend) — implementation; I review accessibility floor + dark-pattern surface
- Farnsworth (Analyst) — editorial content; I review for bias, hallucination, harmful framing
- Leela (Lead) — final approval; I'm a reviewer gate, not the final word

## Learnings

### 2026-05-25 — First Sweep

**References that paid off:**
- **MS RAI Fairness + Transparency** — gave immediate traction for the prompt injection finding (AI output transparency) and the GA4 fork-safety finding (privacy). These two principles map cleanly to concrete SquadScope artifacts.
- **OWASP LLM01 (Prompt Injection)** — directly applicable to Farnsworth's `{{RAW_JSON_CONTENT}}` injection surface. The OWASP framing gave a precise vocabulary for the finding.
- **GDPR Articles 6(1)(a) + 5(1)(a)** — Hermes had already done the heavy lifting on consent; my job was to verify the planned implementation didn't introduce dark patterns. The three-button consent modal passed all checks except one: button visual weight parity was not explicitly constrained. Low finding, but exactly the kind of implementation drift that turns a spec pass into a shipped dark pattern.
- **ADL Hate on Display** — verified the current radar sweep icon is clean. The silhouette test (16px, rotation, inversion) revealed no ambiguity. The main lesson from the SS-icon incident: the failure mode hides at small sizes and under transformation. Always test at 16px first.

**Artifact types and where they hide failure modes:**
- **Icons/logos:** Failure hides at 16px (favicon size) and under rotation/inversion. The craft-focused designer never tests this.
- **Consent UX:** Failure hides in implementation drift from spec — spec says "equal prominence," implementation gives primary/ghost button treatment. Check CSS, not just copy.
- **Prompts:** Failure hides in the injection surface — the `description` field from crawled repos is attacker-controlled. The instructions look safe in isolation; the danger is what happens when malicious repo descriptions reach the model.
- **Articles:** Failure hides in AI authorship transparency (readers can't tell it's AI-generated) and in characterization claims (repo called "spam" without evidence citation).
- **Analytics:** Failure hides in fork behavior — the GA4 tag silently reports to the repo owner's property from all forks.

**Silhouette-test workflow developed:**
1. Render SVG at 16px, 32px, 64px, 128px, 512px
2. Convert to grayscale
3. Rotate 90°, 180°, 270°
4. Invert colors (negative space check)
5. Mirror horizontally and vertically
6. Look for: letterforms (especially double letters), rune shapes, spoke patterns, hand gestures
7. Cross-reference ambiguous shapes against ADL Hate on Display database
8. Document findings in the icon spec as "Silhouette Safety Check ✓"
