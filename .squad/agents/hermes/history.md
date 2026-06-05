# Hermes — History

## Core Context
- Owns security review for application code, dependencies, and CI workflow changes.
- Evaluates risk with the full pipeline in mind, not just single-file diffs.

## Learnings
- Branch protection must stay intact; automation should use the shared `branch-protection-pr-workflow` skill instead of bypasses.
- The current pipeline chains GitHub crawl data, press correlation, AI analysis, content generation, and GitHub Pages deployment, so security review must cover every handoff.
- The safest fallback posture is Copilot CLI first, GitHub Models second, and a bounded no-AI summary path after that.
- Retry logic and prompt sanitation both matter for defense-in-depth when external content can influence analysis prompts.
- Prompt-injection hardening should layer untrusted-content boundaries, pre-render sanitization, output evidence guards, and a closing trusted-mission reminder; sanitize repo descriptions by stripping leading whitespace, escaping boundary-close tags, truncating length, and warning on common injection phrases.
- URL validation must use `urllib.parse.urlparse()` instead of substring checks to avoid time-of-check-time-of-use (TOCTOU) vulnerabilities in test contexts and security checks (CodeQL hardening, PR #164).
- Config-driven external HTTP fetchers must enforce the intended allowlist in code (HTTPS + approved hosts), per-request timeouts, bounded retries, and bounded concurrency before running in CI.

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

## Cookie Banner BaseURL-Aware Links — 2026-05-25

- Cookie-banner in-site links must not hardcode root-relative paths like `/privacy/` because GitHub project Pages deploys SquadScope under `/SquadScope/`.
- Data-file legal copy should use placeholders such as `__PRIVACY_URL__`, with Hugo partials substituting them through URL helpers (`relURL` or `absURL`) at render time.

## PR #236 Security Review (2026-06-05)

- Security review of PR #236 external RSS feeds integration complete
- **Verdict: Request changes** (blocking issues found)
- Formal approval blocked by GitHub own-PR rules (self-authored by Hermes as PR author)
- Posted blocking security comment to PR #236
- **Blocking Requirements:**
  1. URL validation with `urllib.parse.urlparse()`: enforce HTTPS + allowlist hosts only
  2. Reject credentials, local/private/link-local hosts, unexpected ports
  3. Explicit per-request timeout in feed fetch code path
  4. Bounded retry/backoff behavior
  5. Optional `--max-workers` concurrency validation
- **Ownership:** Bender assigned as revision owner to avoid Leela reviewing own implementation changes
- **Impact:** PR #236 cannot merge until security fixes implemented and re-reviewed
