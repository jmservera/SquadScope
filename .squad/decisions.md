# Squad Decisions

## Impact

Applies to future weekly summaries and any generator work that consumes `data/analyzed/*-summary.md`.

---

# Fry: quality gate fallback hardening

Date: 2026-06-01

## Context
Issue #217 showed the weekly analysis job can fail even when crawl data is healthy because Copilot sometimes returns a generic placeholder title or no output file at all after retries.

## Decision
Keep Copilot CLI as the primary analysis generator, but if its output still fails the quality gate after retries, immediately fall back to `scripts/analyze_fallback.py` via GitHub Models. Also render the prompt with concrete `week`, `year`, and title guidance so the model is less likely to echo placeholder frontmatter.

## Rationale
This keeps the higher-quality primary path, but removes CI flakiness from transient Copilot failures and from prompt placeholders leaking into the final markdown.

---

# Directive: Prevent Recrawl on Previous-Week Rebuilds

**Date:** 2026-05-25T15:55:00+02:00  
**Source:** User directive (jmservera via Copilot)  
**Status:** Active

## Active Decisions

# Leela — PR review gate follow-up

- Date: 2026-06-01
- Context: Round review of PR #218 and PR #219 showed both branches were opened by `jmservera`, which means the current GitHub identity cannot submit an approving review on them.
- Decision: Do not bypass the review gate on self-authored pull requests. Treat independent approval as still required before merging branches opened by the same account Leela is operating under.
- Why: GitHub blocks self-approval, and preserving the review gate matters more than forcing a merge from the lead seat.

## Cost Transparency Placement (2026-05-25)

**Decision:** The AI pipeline cost dashboard is part of `/about/` under a Pipeline transparency section, with the existing `/dashboard/` page retained as a direct audit link that reuses the same shortcode.

**Rationale:** Cost reporting is operational transparency, not a primary navigation destination or product dashboard. Keeping it on About matches the editorial-restrained redesign while preserving the old URL for references.

## Nibbler Review Gate for External-Facing Artifacts (2026-05-25)

**Source:** Nibbler audit recommendation
**Adopted by:** Leela
**Status:** Adopted

External-facing launch and announcement artifacts require Nibbler review before publication or merge. This includes Hacker News posts, LinkedIn announcements, Bluesky threads, Reddit posts, launch blogs, press copy, launch graphics, and similar materials that will appear outside this repository.

PRs that ship this copy or graphics must tag `@squad:nibbler` for RAI sign-off and use the [Responsible AI checklist](skills/responsible-ai-review/SKILL.md) (`.squad/skills/responsible-ai-review/SKILL.md`) before merge.

**Rationale:** Distribution copy can create reputational, safety, accessibility, or policy risk even when the underlying code is unchanged. Nibbler provides the hostile-reader and responsible-AI perspective before users encounter the material.


# AI Disclosure Pattern

**Date:** 2026-05-25  
**Author:** Amy  
**Status:** Proposed  

Every page renders an AI-disclosure footer partial; article pages additionally show a prominent AI-generated badge in the meta block. Single partial = single source of truth.

# Amy — Cookie Consent vendoring

Date: 2026-05-25

Decision: vendor Cookie Consent v3 directly in `static/vendor/cookieconsent/` and pin it to upstream version `v3.0.1`.

Rationale:
- Cookie consent must run before optional analytics scripts are activated.
- Vendoring avoids relying on the jsDelivr CDN at runtime.
- The pinned files are the published `dist` CSS and UMD bundle from `orestbida/cookieconsent@v3.0.1`.

Checksums:
- `cookieconsent.css`: `sha256 ca046b8b1b1094107205988e7096a687b241c8ef5f3fefe5e543ed28d26646c1`
- `cookieconsent.umd.js`: `sha256 1267fd33fcf3ab4043a7cc62cc9259a2c66f839f695216f7737ed37b7b3e62e6`

# Article errata schema

**Date:** 2026-05-25  
**Author:** Amy  
**Status:** Proposed

## Decision

Articles declare corrections in front-matter using `errata: [{date, note}]`; the article footer renders those entries at the end of the article.

## Schema example

```yaml
errata:
  - date: 2026-05-26
    note: "Corrected the company name in the EU AI Act section (was 'Mistral.ai', now 'Mistral AI')."
```

## Rationale

Keeping corrections in front-matter makes the article-level errata path data-driven, reviewable in Git, and visible to readers without requiring silent edits to published analysis.

# Home hero restructure

**Date:** 2026-05-25  
**Author:** Amy (Frontend Engineer)  
**Status:** Proposed

## Decision

Home page is a publication front page — the latest weekly analysis IS the hero. Explainer lives at `/about/`.

# Amy Phase 1 Design Foundation Implementation

**Date:** 2026-05-25  
**Author:** Amy (Frontend Developer)  
**Status:** Implemented

## Decision

Phase 1 tokens and typography are implemented as a Hugo asset-pipeline foundation without changing page layouts.

## File locations

- `assets/css/tokens.css` is the design-system entry point for color, type, spacing, radius, shadow, and line-height tokens.
- `layouts/partials/head.html` loads Inter and JetBrains Mono from Google Fonts using preload + stylesheet links, then includes `tokens.css` before the PaperMod-compatible CSS bundle.
- `assets/css/core/theme-vars.css` maps PaperMod legacy variables to SquadScope tokens so existing templates continue to render.
- `assets/css/core/reset.css` applies the base reset, body typography, heading scale, and monospace stack.
- `assets/css/common/*.css`, `assets/css/extended/squadscope.css`, and `assets/css/badges.css` consume the token aliases while preserving existing layouts.

## How to extend

Future phases should add new tokens to `assets/css/tokens.css` first, then consume them through component or layout CSS. Keep semantic tokens stable (`--color-*`, `--text-*`, `--space-*`) and add component-specific variables only when a pattern repeats across multiple publishing surfaces.

## Gotchas

PaperMod lives as a submodule, so theme CSS changes should be copied into root-level `assets/css/` overrides rather than editing `themes/PaperMod` directly. Hugo resolves these project assets through the existing asset pipeline while leaving the third-party theme clean.

# Amy Phase 2 Implementation Notes

Date: 2026-05-25
Author: Amy
Status: Implemented in PR branch

## Decisions

- Override PaperMod chrome at the project layer (`layouts/partials/header.html`, `layouts/partials/footer.html`) rather than editing the theme submodule.
- Add `layouts/_default/baseof.html` solely to place the skip-to-content link before the cached header and give the main landmark `id="main-content"`.
- Keep the primary nav intentionally scoped to Weekly, Monthly, Yearly, and About for Phase 2; archive/search/taxonomy links remain in the page body and footer where already present.
- Use a native `<details>` disclosure for mobile navigation so the collapsed menu remains keyboard reachable without adding new JavaScript.

## Implications

Future chrome work should continue to extend root layouts and tokenized CSS. If PaperMod changes its base template, compare against this override before upgrading the theme.

# Amy — Topic buttons follow-up

- Date: 2026-06-01
- Context: Issue #216 mobile topic buttons regression
- Proposal: Keep topic discovery centered on `/topics/`, remove the global header topic shortcut strip, and hide per-report topic chips on screens up to 768px while leaving desktop topic browsing available through the homepage rail and Topics page.
- Why: The repeated chip rows were consuming too much vertical space on mobile and duplicated navigation that already exists in the primary menu.

# Decision: GA4 fork-safe secret injection

**Date:** 2026-05-25T22:30:00+02:00  
**Author:** Bender (Crawler/CI)  
**Status:** Proposed

## Context

SquadScope needs GA4 analytics for the upstream site, but forks must not silently report traffic to the maintainer's GA property. Repository secrets are not inherited by forks, so analytics must depend on an explicitly provided secret and render nothing when absent.

## Decision

Use a secret-default-empty pattern: Hugo config defines `params.ga_measurement_id = ""`, while the Pages deploy workflow injects `${{ secrets.GA_MEASUREMENT_ID }}` through `HUGO_PARAMS_GA_MEASUREMENT_ID`. Hugo maps that environment key to `params.ga.measurement.id`, and the analytics partial renders GA4 only when either config path is non-empty. The rendered scripts are marked with `data-cc-category="analytics"` so Cookie Consent v3 can load them only after analytics consent.

## Rationale

The empty config default is safe for forks and local builds. The environment override keeps the maintainer measurement ID out of source control while still enabling analytics in the upstream deployment. Consent-category script tagging keeps analytics dormant until the consent integration activates the analytics category.

## Impact

- Upstream deploys can enable GA4 by setting `GA_MEASUREMENT_ID`.
- Forks build without analytics by default.
- Maintainers can opt out by deleting the secret.
- Cookie consent integration can activate the tagged scripts without changing the GA4 partial.

# Decision: Journalistic shell baseline

**Date:** 2026-05-25T23:31:03+02:00  
**Owner:** Calculon  
**Status:** Proposed

## Decision

The journalistic shell is a non-negotiable baseline for SquadScope. Navigation density, search, weekly archive access, and topic shortcuts must remain present in future home-page cleanups.

## Rationale

jmservera rejected the PR #205 revision because it over-pruned the publication shell. Future cleanups may relocate explanatory body content, but they must not remove the publication affordances that make the site feel like an editorial front page.

## Implications

- Keep top-level access to all weeks, topics, and search.
- Keep a home-page rail or equivalent surfacing active topics and recent issues.
- Preserve `/about/` as the home for the explainer and transparency dashboard.

# Design Direction: Editorial Trend Report

**Date:** 2026-05-25  
**Author:** Calculon (Designer)  
**Status:** Proposed

## Decision

**Visual Direction:** Editorial Trend Report — Dense but Quiet

This positions SquadScope as a credible, opinionated weekly briefing rather than a generic blog or SaaS dashboard. Typography carries the design; images and color accents are supporting actors.

## Rationale

After studying GitHub Pulse, TechCrunch, Wired, and The Verge:
- GitHub Pulse is too dashboard-like for editorial content
- TechCrunch provides good headline hierarchy but is too news-feed
- Wired is too image-dependent for text-first analysis
- The Verge shows density can work if hierarchy is clear

SquadScope is closer to a weekly briefing document than any of these. The design borrows TechCrunch's reading rhythm, GitHub Pulse's monochrome discipline, and The Verge's willingness to be dense — while avoiding their weaknesses.

## Token Summary

**Palette:** Monochrome foundation with single accent (#0066CC light, #4DA3FF dark). All combinations WCAG AA verified.

**Typography:** Inter system stack for headlines and body. JetBrains Mono for code. Type scale from 0.75rem (tiny) to 2.25rem (h1). Optimal prose measure 68ch.

## Phase Plan

1. Tokens + Typography Foundation
2. Header + Footer + Navigation
3. Home Page Layout
4. Article Layout + Components
5. Cost Dashboard Refresh
6. Icon + Favicon + Social Images

Each phase ships independently. Tokens must land first; other phases have light dependencies.

## Icon

Radar sweep concept — concentric circles with sweep line and signal blip. Represents continuous scanning. Hand-coded SVG, no external fonts, under 2KB. Uses currentColor for automatic mode adaptation.

## References

- `docs/design/redesign-proposal-2026-05.md`
- `docs/design/icon-spec.md`
- Issues #170-#177


# Source-selection methodology disclosure

- **Date:** 2026-05-25
- **Owner:** Farnsworth
- **Status:** Proposed for merge

## Decision

Source-selection biases are publicly disclosed at `/methodology/`; updates to scoring, source ingestion, crawl thresholds, or press coverage should be reflected there.

## Context

Nibbler's second responsible-AI sweep identified source-selection bias disclosure as a high-severity fairness and transparency gap. The methodology page gives readers a plain-English explanation of source inputs, ranking logic, and interpretation limits.

## Consequences

- Pipeline changes that alter source mix or scoring should include a reader-facing methodology update.
- Future bias metrics can link back to `/methodology/` as the stable disclosure surface.

# BaseURL-aware links in data files

Date: 2026-05-25
Owner: Hermes

## Decision

Links inside `data/*.json` files must use `__TOKEN__` placeholders substituted by partials with Hugo URL helpers; never hardcode `/path/` prefixes inside data files.

## Rationale

SquadScope is currently deployed on GitHub project Pages under `/SquadScope/`, so root-relative links such as `/privacy/` resolve outside the site and can 404. If the site later moves to an apex/custom domain, Hugo URL helpers will render the same logical route correctly without changing legal-copy JSON.

## Implementation note

For cookie-consent copy, `data/cookieconsent.json` uses `__PRIVACY_URL__`, and `layouts/partials/cookie-consent.html` replaces it with `"privacy/" | relURL` before initializing Cookie Consent.

# Hermes Privacy Policy v1

Date: 2026-05-25
Author: Hermes (Security & Legal)
Status: Proposed

## Decision

GA4 is our ONLY analytics; no first-party tracking.

## Context

SquadScope is a static editorial trend-analysis site with no accounts, signup, comments, contact form, or newsletter. The site is hosted on GitHub Pages and uses a cookie consent banner before analytics can run.

## Consequences

- SquadScope must not add first-party visitor profiling, server-side personal-data storage, or additional analytics tools without a new privacy review.
- GA4 must remain consent-gated behind the analytics cookie category.
- Privacy disclosures should continue to identify GitHub Pages hosting logs, GA4, Google Fonts if used, and the essential consent cookie.

# Prompt Injection Hardening for Analysis Prompts

**Date:** 2026-05-25
**Author:** Hermes
**Status:** Proposed

## Context

Nibbler's RAI audit identified user-controlled GitHub repository descriptions entering the weekly analysis prompt through `{{RAW_JSON_CONTENT}}`. A malicious repo description can contain prompt-injection text that attempts to override Farnsworth's editorial instructions.

## Decision

Apply a layered OWASP LLM01 defense for analyzer prompt rendering:

1. Mark raw crawl JSON as untrusted data with explicit `<untrusted-content>` boundaries.
2. Sanitize repository descriptions before prompt rendering by stripping leading whitespace, escaping boundary-closing tags, truncating long text, and warning on common prompt-injection phrases.
3. Add output guardrails telling the analyst to stop on unsupported claims and avoid verbatim descriptions containing meta-instructions.
4. Repeat the editorial mission after the untrusted content so late prompt text reinforces trusted instructions.

## Consequences

The analyzer keeps using the same editorial structure, but prompt provenance is clearer and repository descriptions have bounded influence. Suspicious descriptions are logged and truncated rather than blocked to avoid false positives disrupting publication.

---

# Fry: quality gate fallback hardening

Date: 2026-06-01

## Context
Issue #217 showed the weekly analysis job can fail even when crawl data is healthy because Copilot sometimes returns a generic placeholder title or no output file at all after retries.

## Decision
Keep Copilot CLI as the primary analysis generator, but if its output still fails the quality gate after retries, immediately fall back to `scripts/analyze_fallback.py` via GitHub Models. Also render the prompt with concrete `week`, `year`, and title guidance so the model is less likely to echo placeholder frontmatter.

## Rationale
This keeps the higher-quality primary path, but removes CI flakiness from transient Copilot failures and from prompt placeholders leaking into the final markdown.

---

# Fry — generate-step failure handling

Date: 2026-06-01

## Context
Issue #220 showed the crawl-and-publish workflow could finish crawl and analysis successfully, then fail in the generate handoff because the generated weekly page path was absolute while the publish-branch restore logic assumed a repository-relative path. The same workflow also lacked a failure-to-issue bridge, so repeated pipeline failures did not automatically open or update a GitHub issue.

## Decision
Normalize `page_path` to a repo-relative `content/weekly/...` path inside the generate commit step before copying weekly output onto the publish branch. Add a dedicated `notify-failure` job that always evaluates after the pipeline jobs and creates or updates a GitHub issue whenever any crawl/analyze/generate/deploy/notify job fails.

## Rationale
The path normalization fixes the actual handoff bug without changing `scripts/generate_content.py`, which already returns an absolute file path used elsewhere in tests. A separate failure notifier makes regressions visible even when later jobs are skipped, which is the exact reliability gap that hid the recent failures.


---

# Amy — Share button implementation

Date: 2026-06-01

## Context
Issue #226 adds article-level sharing. PaperMod already ships a share-buttons partial, but SquadScope also needs mobile-native sharing through the Web Share API and token-aligned styling.

## Decision
Enable PaperMod share support through `hugo.toml` (`params.ShowShareButtons` plus an explicit `params.ShareButtons` allowlist), then override `layouts/partials/share_icons.html` in the project to add a mobile-only native share button while keeping desktop fallback links for X, LinkedIn, and Facebook. To keep the site buildable with the current PaperMod submodule layout, vendor the theme partials the site already relies on into `layouts/partials/` instead of editing the theme.

## Rationale
This keeps the third-party theme submodule untouched, reuses the existing article-footer insertion point, and scopes the share customization to a project-level partial plus tokenized footer styles. Vendoring the required PaperMod partials also makes the build deterministic for SquadScope without depending on theme-internal `_partials` resolution quirks.

---

# Farnsworth — Hindsight validation decision

Date: 2026-06-01

## Decision
Use an optional `predictions` frontmatter registry on weekly analysis summaries with entries shaped as `{repo, direction, confidence}`.

## Why
The published markdown is already the durable editorial artifact, so embedding prediction intent there avoids a separate ledger drifting out of sync. Legacy summaries still need heuristic extraction from Signal/Noise/Gaps prose, but future summaries should register explicit repo-level calls for cleaner hindsight scoring.

## Operational note
The validator writes a human scorecard to `.squad/reskill/scorecards/YYYY-WNN.md` and a machine-readable companion to `data/metrics/scorecards/YYYY-WNN-scorecard.json` so the current reskill tooling can ingest the same run.

---

# Fry — Generate-step failure handling

Date: 2026-06-01

## Context
Issue #220 showed the crawl-and-publish workflow could finish crawl and analysis successfully, then fail in the generate handoff because the generated weekly page path was absolute while the publish-branch restore logic assumed a repository-relative path. The same workflow also lacked a failure-to-issue bridge, so repeated pipeline failures did not automatically open or update a GitHub issue.

## Decision
Normalize `page_path` to a repo-relative `content/weekly/...` path inside the generate commit step before copying weekly output onto the publish branch. Add a dedicated `notify-failure` job that always evaluates after the pipeline jobs and creates or updates a GitHub issue whenever any crawl/analyze/generate/deploy/notify job fails.

## Rationale
The path normalization fixes the actual handoff bug without changing `scripts/generate_content.py`, which already returns an absolute file path used elsewhere in tests. A separate failure notifier makes regressions visible even when later jobs are skipped, which is the exact reliability gap that hid the recent failures.

---

# Farnsworth hindsight validation decision

Date: 2026-06-01

## Decision
Use an optional `predictions` frontmatter registry on weekly analysis summaries with entries shaped as `{repo, direction, confidence}`.

## Why
The published markdown is already the durable editorial artifact, so embedding prediction intent there avoids a separate ledger drifting out of sync. Legacy summaries still need heuristic extraction from Signal/Noise/Gaps prose, but future summaries should register explicit repo-level calls for cleaner hindsight scoring.

## Operational note
The validator writes a human scorecard to `.squad/reskill/scorecards/YYYY-WNN.md` and a machine-readable companion to `data/metrics/scorecards/YYYY-WNN-scorecard.json` so the current reskill tooling can ingest the same run.

---

# Fry QA triage decision

Date: 2026-06-05T15:36:19.379+00:00

## Decision

The crawl-and-publish analysis stage should degrade to a data-only no-AI weekly summary when both Copilot output and GitHub Models output are unavailable or rejected by the quality gate.

## Rationale

A missing or unauthorized model is an operational dependency failure, but the pipeline still has verified crawl data. Publishing a clearly labeled data-only summary is more reliable than failing the entire weekly handoff after preserving no reader-facing output.

## Follow-up

If model access is restored, the AI analysis path remains preferred. The no-AI path is only a terminal fallback after Copilot and GitHub Models fail.

---

# Leela: Close unverifiable W23 growth execution

Date: 2026-06-05T15:36:19.379+00:00

**By:** Leela

## Decision

Issue #188 was closed as obsolete/unverifiable rather than reconstructed or rerouted. W23 draft files under `.squad/posts/`, the requested `.squad/metrics/2026/w23-distribution.md`, and platform posting evidence were absent from the working tree, git history, related issues, and PR context. PR #190 and `docs/growth/distribution-strategy.md` only provide the launch strategy/template, not the W23 execution artifacts.

## Rationale

Recreating social posts and metrics after the distribution window would create misleading evidence. Future growth execution issues should remain open until artifact-backed proof exists, or be closed explicitly when the posting window expires without evidence.

---

# Fry PR #236 QA Review

Date: 2026-06-05T15:36:19.379+00:00

PR #236 keeps RSS enrichment in the existing crawl job with bounded in-process parallel fetching instead of separate Actions jobs.

QA verified the diff covers config loading, multi-source crawl aggregation, metadata/errors, legacy `*-techcrunch.json` fallback, correlation handoff, press-context resolution, and rebuild hydration.

Validation run in an isolated PR worktree:
- `PYTHONPATH=. .venv/bin/python -m pytest tests -q` → 554 passed
- Live RSS smoke with `--max-workers 5` → 54 articles from 5 sources, no feed errors

Verdict: approve; no follow-up implementation owner required.

---

# Hermes security review — PR #236 external RSS feeds

Date: 2026-06-05T15:36:19.379+00:00

## Verdict

Request changes before merge.

## Rationale

PR #236 keeps workflow secrets out of the RSS step and does not add new dependency classes, but the new config-driven fetcher currently trusts `feed_url` values without enforcing scheme/host boundaries and calls `feedparser.parse(url)` without an explicit per-request timeout. Because the workflow runs this in CI and later grants `contents: write` in the same job, external-network behavior should fail closed around the intended RSS allowlist and fail fast on slow/unresponsive feeds.

## Required fixes

- Validate source config with `urllib.parse.urlparse()` before crawling:
  - require `https`;
  - require hostnames to match the repository-owned allowlist for the five intended feeds;
  - reject credentials, local/private/link-local hosts, and unexpected ports.
- Fetch feeds through a code path with explicit timeout and bounded retry/backoff behavior; do not rely on the default socket timeout.
- Keep bounded concurrency; optionally validate `--max-workers` to a safe range.

## Suggested owner

Bender should own the fixes so Leela does not review her own implementation changes.

---

# PR #236 security unblock

Date: 2026-06-05T16:00:00+00:00

Hermes re-reviewed PR #236 at Bender fix commit `e91e2a5b33b816191148125d40192b3fff8fbc6a`.

Security blockers from the prior review are resolved:
- external RSS feed URLs are parsed with `urllib.parse.urlparse()` and restricted to HTTPS on the approved host allowlist;
- credentials, localhost/local domains, private/link-local IP literals, invalid ports, and non-443 ports are rejected;
- RSS fetches use `urlopen(..., timeout=DEFAULT_FETCH_TIMEOUT_SECONDS)` with bounded retry attempts;
- parallel RSS crawling caps workers at `DEFAULT_MAX_WORKERS` and rejects `--max-workers < 1`;
- tests cover unsafe URL rejection and explicit timeout propagation.

Validation: `PYTHONPATH=. python -m pytest tests -q` in an isolated PR worktree passed with 563 tests.

Decision: Hermes security approval/unblock for merge, with CodeQL checks green on the PR.

