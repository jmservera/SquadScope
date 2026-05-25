# Hermes — History

## Core Context
- Owns security review for application code, dependencies, and CI workflow changes.
- Evaluates risk with the full pipeline in mind, not just single-file diffs.

## Learnings
- Branch protection must stay intact; automation should use the shared `branch-protection-pr-workflow` skill instead of bypasses.
- The current pipeline chains GitHub crawl data, press correlation, AI analysis, content generation, and GitHub Pages deployment, so security review must cover every handoff.
- The safest fallback posture is Copilot CLI first, GitHub Models second, and a bounded no-AI summary path after that.
- Retry logic and prompt sanitation both matter for defense-in-depth when external content can influence analysis prompts.
- URL validation must use `urllib.parse.urlparse()` instead of substring checks to avoid time-of-check-time-of-use (TOCTOU) vulnerabilities in test contexts and security checks (CodeQL hardening, PR #164).

## Cookie Consent & Privacy Policy (Issue #183) — 2026-05-25

**Legal Text Patterns Used:**
- GDPR Article 6(1)(a) explicit consent (opt-in only, no pre-ticked boxes)
- GDPR Article 5(1)(a) transparency — all data processors disclosed
- GDPR Articles 13/14 privacy information requirements fully covered
- GDPR Article 21 right to object — revocation mechanism documented
- Zero dark patterns: "Accept all" and "Reject all" equally prominent
- Plain English tone, no legalese; links to external authorities (ICO, Google, GitHub)
- GA4 processor agreement noted; 14-month retention disclosed as default
- Subject access requests via GitHub Issues + direct profile link (proportionate to non-commercial research context)

**Files Created:**
- `content/privacy/_index.md` — Hugo privacy policy (~580 words, covers all GDPR minima)
- `data/cookieconsent.json` — Cookie Consent v3 config (plain English copy, no manipulation)
