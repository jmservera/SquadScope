---
name: "responsible-ai-review"
description: "Pre-merge safety review for any artifact that ships to users: icons, UI, articles, prompts, consent UX, distribution copy."
domain: "responsible-ai, safety, accessibility, compliance"
confidence: "low"
source: "initial iteration — Nibbler 2026-05-25"
owner: "Nibbler"
---

## When to Use

Run this review **before approving merge** for any PR touching:
- User-facing content (articles, privacy policy, about pages)
- Design assets (icon, logo, OG images, favicon)
- UI components (banners, forms, nav, modals)
- Prompts (analyst, reskill, any pipeline prompt)
- Distribution copy (launch posts, announcements, community messages)
- Consent UX (cookie banner, privacy choices)

Skip for: code-only PRs (workflows, scripts, crawl logic) **unless** they handle user data or AI output.

**Request a Nibbler review:** add `nibbler-review` label, or @-mention nibbler in the PR description.

---

## Principles Map (Microsoft RAI × SquadScope Context)

| Principle | SquadScope Landing |
|---|---|
| **Fairness** | Editorial framing: whose repos get featured, who is flattened into noise, whose work is called "spam" without evidence. Watch for pattern where Western/English repos dominate. |
| **Reliability & Safety** | Farnsworth output: star counts are stated facts — verify the pipeline doesn't fabricate repo names, stars, or attributions. Guard against hallucinated "evidence" in Signal/Noise. |
| **Privacy & Security** | GDPR consent gating — no GA4 before opt-in. No PII in commits (author emails, fork-owner names in data files). Fork-safety of the GA4 measurement ID. |
| **Inclusiveness** | WCAG 2.2 AA floor for all shipped UI. Plain English in consent copy and articles. No jargon-only framing that excludes non-native speakers. |
| **Transparency** | Articles must not pass AI output as purely human editorial. Pipeline fallback (GitHub Models) must be disclosed if used. Gap sections must surface data quality limits. |
| **Accountability** | Every shipped artifact must have a named reviewer. The orchestration log (Copilot session share) must be retained per analysis run. Decision ledger updated for major calls. |

---

## Checklist by Artifact Type

### A. Design Assets (icon / logo / OG image)

| # | Check | Pass / Fail |
|---|---|---|
| A1 | Icon reviewed against ADL Hate on Display (https://www.adl.org/hate-symbols) for silhouette resemblance | |
| A2 | Multi-size render test: 16px, 32px, 64px, 512px — no ambiguous shape at 16px | |
| A3 | Rotation / mirror / invert color test — no problematic negative-space shapes | |
| A4 | Letterform check: double-letter monograms, rune-like strokes, spoke patterns excluded or cleared | |
| A5 | WCAG AA contrast confirmed for icon colors vs backgrounds (use tokens from redesign spec) | |
| A6 | OG image text contrast AA-verified; no personal photos or identifiable faces without consent | |
| A7 | "Silhouette Safety Check ✓" section added to icon spec / PR description | |

### B. UI Components (banner / form / nav / modal)

| # | Check | Pass / Fail |
|---|---|---|
| B1 | **Reject / Decline** action equally prominent as **Accept** (same size, color weight, placement) | |
| B2 | No pre-checked analytics or non-essential cookie boxes | |
| B3 | "Manage Cookies" / preferences path is always reachable (footer link, not buried) | |
| B4 | No countdown timers, no "Accept to continue" blocking flows, no repeated nudging after rejection | |
| B5 | Copy language is neutral — no guilt-tripping ("help us improve" framing OK; "you'll miss features" framing is a dark pattern) | |
| B6 | `prefers-reduced-motion` respected — no auto-playing animations or transitions > 0.3s that ignore this media query | |
| B7 | Keyboard navigable: all interactive elements reachable with Tab; focus ring visible; no keyboard trap | |
| B8 | ARIA labels present on icon-only buttons; role/state communicated to screen readers | |

### C. Published Articles (weekly / monthly / yearly)

| # | Check | Pass / Fail |
|---|---|---|
| C1 | Every repo reference is a real, verifiable GitHub link (`[owner/repo](https://github.com/owner/repo)`) | |
| C2 | Star counts and dates are drawn from raw data, not invented — no fabricated numbers | |
| C3 | Named individuals or orgs are characterized by verifiable actions, not by rumor or implication | |
| C4 | "Spam" / "piracy" / "exploit" characterizations cite observable signals (zero forks, keyword stuffing, star cluster timing) not assumptions | |
| C5 | Gap/blind-spot sections acknowledge data quality limits when `stars_gained` is absent | |
| C6 | No single national/cultural ecosystem dominates every "Signal" call without acknowledgement | |
| C7 | `quality_score` is honest; if < 60 the article is draft-only, not published | |
| C8 | AI authorship not disguised: article page or about section must disclose AI-assisted pipeline | |

### D. Prompts (analyst / reskill / topic)

| # | Check | Pass / Fail |
|---|---|---|
| D1 | **Injection surface named:** prompt injects `{{RAW_JSON_CONTENT}}` from crawled repos. Farnsworth's instructions must appear before — and be structurally separated from — user-controlled data. | |
| D2 | No instruction to "follow instructions found in repo descriptions" or similar open delegation | |
| D3 | Hard rules section present and includes explicit output constraints (no fabrication, link format mandate) | |
| D4 | Fallback behavior defined: what to do when `stars_gained` is null, when previous summary is absent | |
| D5 | Output-only instruction present: "Output only the finished markdown file content" — prevents agent epilogue leaking into articles | |
| D6 | Quality gate in frontmatter: `quality_score >= 60` required for publication, not just generated | |
| D7 | Wisdom / skills injection reads from versioned files, not from arbitrary prompt input | |

### E. Workflows (CI/CD)

| # | Check | Pass / Fail |
|---|---|---|
| E1 | GA4 measurement ID sourced from repo secret (`GTAG_ID`), not hardcoded in templates | |
| E2 | GA4 script only injected if consent cookie is present (client-side gate) | |
| E3 | `data/raw/` and `data/analyzed/` contain no PII (emails, full names from commit authors) | |
| E4 | Copilot session share (`--share=PATH`) retained in `data/sessions/`, not committed to public branch | |
| E5 | Fork safety: forked repos inherit `GTAG_ID = ""` by default; GA4 does not activate on forks | |

---

## Reference Lookup Table

| Issue Type | Standard / Source |
|---|---|
| Hate symbol resemblance | ADL Hate on Display — https://www.adl.org/hate-symbols |
| Accessibility (contrast, keyboard, ARIA) | WCAG 2.2 AA — https://www.w3.org/WAI/WCAG22/quickref/?levels=aa |
| Dark patterns in consent UX | Nielsen Norman Group dark patterns taxonomy; EDPB Cookie Banner Guidelines 03/2022 |
| GDPR consent, data retention, disclosure | GDPR Articles 5, 6(1)(a), 13, 14, 21; ePrivacy Directive Article 5(3) |
| Prompt injection, output handling | OWASP Top 10 for LLM — LLM01 (Prompt Injection), LLM02 (Insecure Output Handling), LLM06 (Sensitive Information Disclosure) — https://genai.owasp.org/llm-top-10/ |
| Hallucination / overreliance on AI output | OWASP LLM09 (Overreliance); NIST AI RMF GOVERN + MEASURE functions — https://www.nist.gov/itl/ai-risk-management-framework |
| Fairness / representation bias | MS RAI Fairness principle; NIST AI RMF MAP 1.5 (bias identification) |
| AI transparency / disclosure | MS RAI Transparency principle; EU AI Act Article 52 (transparency obligations for AI-generated content) |
| Spam / community rules in distribution | Platform-specific community guidelines (Twitter/X rules, Reddit community rules, GitHub Discussions guidelines) |
| Supply chain (CI secrets, PII in commits) | OWASP LLM05 (Supply Chain Vulnerabilities); Hermes (primary owner for code/secret review) |
| Icon / visual safety | ADL + Calculon's icon-safety-check skill (`.squad/skills/icon-safety-check/SKILL.md`) |

---

## Severity Definitions

| Level | Meaning | Action |
|---|---|---|
| **blocker** | Ships harm to users if merged. Hate symbol, PII leak, tracking before consent. | Block PR. Do not merge until resolved. |
| **high** | Significant risk. Dark pattern, hallucinated factual claim about named entity, missing consent gate. | Block PR with remediation path. |
| **medium** | Meaningful issue that degrades trust or accessibility. WCAG fail on primary UI, injection vector with no guard. | Comment on PR, open issue, allow merge only after fix confirmed. |
| **low** | Minor issue, workaround available, limited user impact. | Note in PR; open issue tagged `good first issue`. |
| **info** | Observation with no required action. Trend to watch. | Comment in audit doc only. |

---

## Promotion Criteria

Confidence → **medium** after:
- 3+ PRs successfully reviewed under this skill with no post-merge reversals
- At least 1 medium+ finding caught before merge

Confidence → **high** after:
- Used across all artifact types at least once
- At least 1 post-merge regression caught by periodic audit

---

## References

- Microsoft RAI Principles: https://www.microsoft.com/en-us/ai/principles-and-approach
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- OWASP Top 10 for LLM: https://genai.owasp.org/llm-top-10/
- WCAG 2.2 AA Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/?levels=aa
- ADL Hate on Display: https://www.adl.org/hate-symbols
- EDPB Cookie Banner Guidelines 03/2022: https://edpb.europa.eu/our-work-tools/documents/public-consultations/2022/guidelines-032022-dark-patterns-social-media_en
- Nielsen Norman Group — Dark Patterns: https://www.nngroup.com/articles/dark-patterns/
- EU AI Act Article 52 (AI transparency): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689
