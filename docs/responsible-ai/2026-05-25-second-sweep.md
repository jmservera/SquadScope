# Responsible AI — Second-Sweep Audit Report

**Date:** 2026-05-25  
**Auditor:** Nibbler (Responsible AI / Safety Reviewer)  
**Scope:** Current `main` branch after GA4 fork-safety, prompt-injection hardening, Cookie Consent v3, SEO/PWA/distribution work, Phase 5 dashboard, and design-system phases 1–6.  
**Out of scope:** AI-content disclosure PR `squad/208-ai-content-disclosure`, home page restructure `squad/207`, and privacy-policy expansion `squad/206`.

---

## Summary

| Severity | Count |
|---|---:|
| blocker | 0 |
| high | 2 |
| medium | 5 |
| low | 4 |
| info | 5 |

**Overall:** No blockers. The main new posture risk is not consent or prompt-injection anymore; those moved materially forward. The remaining high-risk gaps are editorial governance: SquadScope still lacks a reader-visible correction/report/retraction path, and its source methodology does not yet disclose or measure representation bias from star-ranked GitHub search plus a single English-language press source.

---

## Microsoft RAI Principle Sweep

### 1. Fairness

#### Finding F1 — Source selection can systematically over-represent high-star, English, and BigCo/press-visible projects

**Severity:** high  
**Principle:** Fairness, Transparency  
**Artifacts:** `scripts/crawl.py`, `scripts/techcrunch_crawler.py`, `examples/topics/ai-ml.yml`, `examples/topics/rust.yml`, `README.md`

**Finding:**  
The crawler's default discovery path queries GitHub Search with `stars:>50`, sorts by `stars`, and caps results (`scripts/crawl.py`, search call and default queries). Topic configs repeat the same high-star threshold pattern, with AI/ML additionally boosting Python and Jupyter Notebook. The press context is currently TechCrunch-only (`scripts/techcrunch_crawler.py` uses `https://techcrunch.com/feed/`). README explains that the system crawls GitHub and applies heuristic filtering, but the public site does not disclose what those cutoffs mean for representation.

This creates predictable editorial skew:
- lower-star but regionally important projects are less likely to enter the candidate set;
- non-English descriptions and non-US ecosystems may be underweighted by English keyword/entity heuristics;
- vendor repos with established brands and press adjacency are more likely to look like durable signal;
- TechCrunch as the only press source overweights US startup/funding narratives.

**Positive evidence:**  
The prompts explicitly require blind-spot analysis and warn not to mistake popularity for momentum. W22 also names coordinated star-farming as noise, showing the analyst is not blindly accepting star counts.

**Recommendation:**  
Add a reader-facing methodology page and a machine-readable source-mix report that disclose: GitHub query filters, star thresholds, sorting, date windows, press sources, known blind spots, and weekly distribution by language/topic/org type. Add a fairness check to the analysis gate: each weekly report should either show a minimum diversity sanity check or explicitly state when the source pool is too skewed to generalize.

**Issue:** Open follow-up issue required (`squad`, `rai`).

---

### 2. Reliability & Safety

#### Finding R1 — No public errata, report-this-article, or retraction process exists

**Severity:** high  
**Principle:** Reliability & Safety, Accountability  
**Artifacts:** `content/weekly/2026/W21.md`, `content/weekly/2026/W22.md`, `layouts/weekly/single.html`, `layouts/partials/article-footer.html`, `content/privacy/_index.md`

**Finding:**  
When the AI analysis is wrong, a reader has no article-level recourse. Weekly pages render metadata, article content, taxonomy links, RSS, sharing, and last-updated text, but no "Report an issue with this article" link. The privacy page links GitHub issues for privacy rights, but that path is not present in the global footer or article footer as a content-correction route. The published W21/W22 articles contain no visible correction note pattern, errata section, or retraction convention.

This matters because SquadScope makes factual claims about named repositories, star counts, spam/star-farming patterns, and vendor behavior. Even with the quality gate, a hallucinated or outdated claim needs an explicit correction pathway.

**Recommendation:**  
Add an article-footer link such as `Report an issue with this article` prefilled with the article URL, plus a short public corrections policy. Define statuses for correction, clarification, and retraction; require corrected articles to include a dated note rather than silent rewrites.

**Issue:** Open follow-up issue required (`squad`, `rai`).

---

### 3. Privacy & Security

#### Finding P1 — No site-level Referrer-Policy is configured

**Severity:** medium  
**Principle:** Privacy & Security  
**Artifacts:** `layouts/partials/head.html`, `content/privacy/_index.md`

**Finding:**  
The site links to GitHub, TechCrunch, Google Fonts, Google Analytics, Hugo, RSS, and share-mailto flows, but no `Referrer-Policy` meta tag or deploy header is present. Without a policy, external destinations can receive the full page URL as referrer depending on browser defaults and link context. Weekly article URLs can encode which report a reader was viewing.

**Recommendation:**  
Set `Referrer-Policy: strict-origin-when-cross-origin` at the hosting layer if possible, and add `<meta name="referrer" content="strict-origin-when-cross-origin">` as a static-site fallback. If the project wants stronger privacy, use `same-origin`.

---

#### Finding P2 — Vendored CookieConsent assets are same-origin but not integrity-pinned in markup

**Severity:** low  
**Principle:** Privacy & Security, Reliability & Safety  
**Artifacts:** `layouts/partials/cookie-consent.html`, `static/vendor/cookieconsent/`

**Finding:**  
CookieConsent v3 assets are vendored locally, which is better than loading a consent library from a third-party CDN. However, the script and stylesheet are loaded without an integrity attribute or documented checksum in the page markup. This is lower risk because the assets are same-origin, but the consent library is a privacy-control dependency; accidental drift should be detectable.

**Recommendation:**  
Keep vendoring, but record version and SHA-256 hashes in the decision note and/or render Subresource Integrity attributes for the local script and stylesheet when practical.

---

#### Finding P3 — GA4 consent/fork-safety posture is materially improved

**Severity:** info  
**Principle:** Privacy & Security  
**Artifacts:** `hugo.toml`, `.github/workflows/deploy-site.yml`, `layouts/partials/analytics.html`, `data/cookieconsent.json`

**Finding:**  
The GA measurement ID defaults to empty in Hugo config, deploy injects it from `secrets.GA_MEASUREMENT_ID`, analytics scripts are `type="text/plain"` with CookieConsent analytics categories, and CookieConsent is opt-in. The current `gtag('config', ...)` partial does not override GA4's default IP-anonymization behavior.

**Recommendation:**  
No new gap beyond P1/P2. Keep the first-visit no-consent network test in the release checklist.

---

#### Finding P4 — No comment system or contact form found

**Severity:** info  
**Principle:** Privacy & Security  
**Artifacts:** `layouts/_default/single.html`, content tree, layout search

**Finding:**  
No deployed comment provider or contact form was found. This is good: there is no extra visitor-submitted personal-data flow beyond analytics consent, Google Fonts requests, GitHub Pages hosting, outbound links, and RSS.

**Recommendation:**  
If comments or forms are added later, require a fresh privacy/RAI review before merge.

---

### 4. Inclusiveness (WCAG 2.2 AA quick sweep)

#### Finding A1 — Small status badges fail AA contrast in light mode

**Severity:** medium  
**Principle:** Inclusiveness  
**Artifacts:** `assets/css/badges.css`, `layouts/partials/correlation-badge.html`, `assets/css/tokens.css`

**Finding:**  
The `badge-organic` small-text color contrast is about **3.90:1** on its mixed light background, below the WCAG AA 4.5:1 threshold for normal text. `badge-hype` is approximately **4.48:1**, effectively at/just below the threshold. These badges are `0.75rem` text, so they need normal-text contrast, not large-text contrast.

**Recommendation:**  
Darken the success/danger badge foregrounds for light mode or use a higher-contrast background/foreground pairing. Re-run contrast checks for all badge variants in light and dark themes.

---

#### Finding A2 — Reduced-motion support exists for smooth scrolling, but CSS transitions are not globally disabled

**Severity:** low  
**Principle:** Inclusiveness  
**Artifacts:** `layouts/partials/footer.html`, `assets/css/common/footer.css`

**Finding:**  
Anchor smooth scrolling respects `prefers-reduced-motion: reduce`, which is good. The floating top-link still has `transition: visibility .3s, opacity .3s ...` with no reduced-motion override. This is minor, but it shows reduced-motion coverage is component-by-component rather than systemic.

**Recommendation:**  
Add a global reduced-motion rule that disables non-essential transitions/animations, or at least override `.top-link` transition under `@media (prefers-reduced-motion: reduce)`.

---

#### Finding A3 — Heading order, keyboard labels, and `lang` pass the quick source sweep

**Severity:** info  
**Principle:** Inclusiveness  
**Artifacts:** `layouts/index.html`, `layouts/weekly/single.html`, `layouts/partials/header.html`, `layouts/_default/baseof.html`, `layouts/partials/footer.html`

**Finding:**  
Key templates use one H1 followed by H2/H3 structures; the GitHub icon button has an `aria-label`; the theme toggle and mobile menu summary have labels; the skip link targets `#main-content`; the footer Manage Cookies control is a native button; and `<html lang="{{ site.Language }}">` is set.

**Recommendation:**  
No gap found in the source sweep. Once the Hugo build baseline is fixed, run rendered-page keyboard and screen-reader smoke tests on home, a weekly article, privacy, and dashboard.

---

### 5. Transparency

#### Finding T1 — Source-data methodology is not reader-facing

**Severity:** medium  
**Principle:** Transparency, Fairness  
**Artifacts:** `README.md`, `docs/analysis-spec.md`, `scripts/crawl.py`, `content/about/_index.md`

**Finding:**  
Operator-facing docs explain the analyzer contract and README describes the pipeline. A normal reader on the public site sees an About page and cost dashboard, but not a methodology page that explains how repos are selected, what "trending" means, what cutoff dates apply, why TechCrunch is used for press context, or why star deltas may be missing.

**Recommendation:**  
Publish a short `/methodology/` page linked from article footers and About. It should be plain-language, not an implementation spec: inputs, cutoffs, ranking, limitations, correction path, and source-bias caveats.

---

#### Finding T2 — Prompts are public and tracked

**Severity:** info  
**Principle:** Transparency  
**Artifacts:** `prompts/analyze-weekly.md`, `prompts/analyze-topic.md`, `prompts/reskill.md`, `.gitignore`

**Finding:**  
The prompts directory is tracked and not ignored. This is a transparency strength: readers and contributors can inspect the instructions that shape the editorial output.

**Recommendation:**  
Link to the prompts from the future methodology page so transparency is discoverable without browsing the repository tree.

---

#### Finding T3 — Model naming is mixed: disclosure can stay generic, cost dashboard is specific

**Severity:** low  
**Principle:** Transparency  
**Artifacts:** `content/about/_index.md`, `layouts/partials/cost-dashboard.html`, `data/metrics/cost-summary.json`

**Finding:**  
The About page uses generic language ("automated AI analysis pipeline"), while the cost dashboard renders model names from the metrics ledger. Specific model names are useful for cost accountability, but they should not be presented as quality endorsements or marketing claims.

**Recommendation:**  
Keep article-level AI disclosure generic, and label the dashboard's model field as operational metadata only.

---

### 6. Accountability

#### Finding C1 — No site-wide content contact path in footer

**Severity:** medium  
**Principle:** Accountability, Reliability & Safety  
**Artifacts:** `layouts/partials/footer.html`, `content/privacy/_index.md`

**Finding:**  
The privacy page has a GitHub issues contact path, but the global footer only links Privacy, Manage cookies, GitHub, RSS, and Archive. A reader who finds an editorial error on an article page has to infer that GitHub is the right place to report it.

**Recommendation:**  
Add a footer `Contact` or `Report an issue` link to GitHub Issues, and add article-specific links with page context. This should be implemented with Finding R1.

---

#### Finding C2 — No content license or reuse terms found

**Severity:** medium  
**Principle:** Accountability, Transparency  
**Artifacts:** repository root, `README.md`, `content/weekly/`, `content/about/_index.md`

**Finding:**  
No `LICENSE`, `COPYING`, terms page, or content reuse statement was found. The site publishes AI-assisted editorial text and repository summaries, but contributors and readers do not know whether the code, generated content, raw data, and analysis are reusable under the same terms.

**Recommendation:**  
Add an explicit repository license and content license/reuse statement. If code and content use different licenses, state that clearly in README and the public site footer.

---

#### Finding C3 — Maintainer ownership is partially named, but editorial ownership is still vague

**Severity:** low  
**Principle:** Accountability  
**Artifacts:** `content/privacy/_index.md`, `README.md`, `content/about/_index.md`

**Finding:**  
The privacy page names `jmservera` as data controller and site operator. That is enough for privacy ownership, but editorial ownership is still framed mostly as an automated pipeline rather than a person or project maintainer accountable for corrections.

**Recommendation:**  
On About or Methodology, state that jmservera is the maintainer/operator and that corrections should be filed through GitHub Issues.

---

## EU AI Act transparency checks

### Article 50 / Article 52 — AI-generated or manipulated content must be distinguishable at delivery time

**Status:** Covered by in-flight AI-content disclosure PR (`squad/208-ai-content-disclosure`) per scope instruction; not audited here.

**Residual recommendation:**  
The disclosure must be per article and visible at delivery time, not only in a policy page. It should link to the methodology/corrections pages once those exist.

### Foundation model labeling

**Status:** In-flight disclosure is expected to cover this. Cost dashboard already records model metadata for operations, but article disclosure should avoid implying model endorsement.

---

## Cross-cutting issues

1. **Governance is now the main RAI gap.** Cookie consent, GA4 fork-safety, and prompt-injection hardening moved the technical baseline forward. The remaining risk is what happens after publication: who corrects, retracts, or explains errors.
2. **Methodology needs to move from repo docs to reader docs.** `README.md` and `docs/analysis-spec.md` are useful to operators, but public readers need a shorter explanation of source selection and limitations.
3. **Representation risk is measurable.** The pipeline already has enough structured data (`language`, `owner`, `topics`, `stars`, `forks`, `created_at`) to produce weekly source-mix telemetry. This should become a standard transparency artifact.
4. **A11y regressions are small but concrete.** The new design system mostly passes the quick source sweep, but badge contrast is below AA and reduced-motion coverage should be centralized.
5. **Privacy posture is mostly improved.** No comment/form surface was found; GA4 is consent-gated and fork-safe. The missing browser privacy control is Referrer-Policy.

---

## Comparison with First Sweep

| First-sweep finding | Status in second sweep | Evidence / note |
|---|---|---|
| Old SS-like icon failure mode | Closed / institutionalized | Current robot/binoculars icon remains distinct; icon-safety skill exists. No new hate-symbol resemblance found in source sweep. |
| Cookie consent visual-weight parity | Closed | CookieConsent config sets `equalWeightButtons: true`; footer Manage Cookies exists. |
| GA4 fork-safety | Closed | Measurement ID defaults empty and deploy injects from secret; analytics partial emits nothing without ID. |
| GA4 consent gate | Closed with watch item | Scripts are `type="text/plain"` and category-gated by CookieConsent. Keep first-visit network test. |
| Distribution copy review | Mostly closed | Distribution strategy exists; no new manipulative copy found in current public site. Continue Nibbler review for launch/community posts. |
| Prompt-injection untrusted repo descriptions | Mostly closed | Prompts now wrap raw JSON in `<untrusted-content>` and sanitizer handles suspicious description patterns. Remaining watch item: post-generation external URL validation. |
| Article AI authorship disclosure | In progress outside scope | Amy-11 PR covers this; not audited here. |
| Header GitHub icon ARIA | Closed | Header GitHub link has `aria-label="GitHub"`; theme/menu controls also labeled. |
| `prefers-reduced-motion` absent | Partially closed | Smooth scrolling respects reduced motion, but top-link transition remains unguarded. |
| Reskill prompt human-review gap | Open / not re-audited deeply | No evidence of a new human checkpoint in this sweep; lower priority than public correction/methodology gaps. |

### New findings in this sweep

- **High:** Source methodology/fairness disclosure gap.
- **High:** No article-level errata/report/retraction process.
- **Medium:** No Referrer-Policy.
- **Medium:** Badge contrast below WCAG AA.
- **Medium:** No site-wide content contact path.
- **Medium:** No content license/reuse terms.
- **Low:** CookieConsent vendored asset integrity not pinned in markup.
- **Low:** Reduced-motion coverage not global.
- **Low:** Model naming should stay operational, not promotional.
- **Low:** Maintainer/editorial accountability copy remains vague.

---

## Follow-Up Issues to Open

- **Issue A:** `rai: disclose and measure source-selection bias in methodology` — high / Fairness + Transparency.
- **Issue B:** `rai: add article errata/report/retraction path` — high / Reliability & Safety + Accountability.

---

## Validation notes

- Reviewed `scripts/analyze_fallback.py`, `scripts/sanitize_repo_content.py`, prompts, topic configs, workflows, privacy/about pages, key layouts, and design CSS.
- Ran a local contrast calculation for design tokens and badges.
- Attempted `hugo --minify`; build failed on the current baseline before any audit-doc change because `layouts/partials/head.html` expects missing PaperMod CSS resources (`css/core/zmedia.css`, `css/core/license.css`, `css/includes/*`). This audit is documentation-only; no runtime code was changed.

*Nibbler — Responsible AI / Safety Reviewer*  
*2026-05-25 | Second sweep — posture: improved technical controls, open governance gaps*
