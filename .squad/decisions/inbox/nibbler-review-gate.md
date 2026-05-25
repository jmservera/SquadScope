# Decision: Nibbler Review Gate

**Date:** 2026-05-25  
**Author:** Nibbler (Responsible AI / Safety Reviewer)  
**Status:** Proposed — pending team adoption  
**Depends on:** Nibbler charter (`.squad/agents/nibbler/charter.md`)

---

## Decision

**Nibbler review is required before approval/merge** for any PR that touches:

- **User-facing content** — weekly articles, privacy policy, about page, error pages
- **Design assets** — icon, logo, OG images, favicon, safari-pinned-tab
- **Prompts** — any file under `prompts/` that feeds the Farnsworth pipeline
- **Distribution copy** — launch posts, announcement drafts, community messages
- **Consent UX** — cookie banner, privacy choices, cookie configuration (`data/cookieconsent.json`)
- **Analytics integration** — GA4 tags, any tracking pixel or beacon

**Skip Nibbler review for:**

- Code-only PRs: workflow YAML, scripts, crawler logic, Hugo templates with no user-visible text changes — **unless** they handle user data or AI output
- Dependency bumps, lock file updates, CI config changes
- Content under `data/raw/` or `data/analyzed/` (Farnsworth's working files, not shipped to users)

When in doubt: add the `nibbler-review` label and Nibbler will triage within the SLA below.

---

## How to Request Review

1. Add the **`nibbler-review`** label to the PR, **or**
2. @-mention nibbler in the PR description or a comment

Nibbler will:
- Run the applicable checklist from `.squad/skills/responsible-ai-review/SKILL.md`
- Comment with pass/fail per checklist section
- Block merge (reviewer lock) on blocker/high findings until resolved
- Approve with notes on medium/low findings (tracked as follow-up issues, not blockers)

---

## SLA

**Initial review:** within one working day of label/mention (human-driven workflow).  
**Re-review after fix:** within one working day of fix confirmation.  
**Periodic audit:** once per month against merged content (catch regressions).

---

## Rationale

The SS-icon near-miss (caught by jmservera, not by any agent) established the failure mode: makers focused on craft miss adversarial misreading. Nibbler exists to institutionalize the "hostile reader" perspective before users encounter it. The review gate makes this catch systematic, not accidental.

This gate is lightweight by design. Blocker/high findings are rare; most reviews will be one-line approvals. The cost of the gate is low; the cost of a missed hate-symbol, dark-pattern consent UX, or hallucinated factual claim is not.

---

## References

- RAI skill: `.squad/skills/responsible-ai-review/SKILL.md`
- Nibbler charter: `.squad/agents/nibbler/charter.md`
- Initial audit: `docs/responsible-ai/2026-05-25-initial-audit.md`
- Icon safety incident: `.squad/decisions/inbox/copilot-directive-icon-ss-association.md` (if present)
