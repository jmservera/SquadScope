---
title: "Claracle Data Observatory Relaunch — Business Requirements Document"
description: "BRD for the next version of the Claracle site, repositioning it from weekly AI-generated summaries into a discoverable, linkable public database of GitHub technology trends to solve the discovery/SEO problem."
author: "BRD Builder (facilitated)"
ms.date: 07/29/2026
ms.topic: reference
---

# Claracle Data Observatory Relaunch — Business Requirements Document

## Document Control

| Field | Value |
|-------|-------|
| BRD ID | BRD-CLARACLE-002 |
| Status | Ready for review |
| Version | 1.0 |
| Author | BRD Builder (facilitated) |
| Sponsor | jmservera (also the human approval authority) |
| Last updated | 2026-07-29 |
| Related repositories | SquadScope, SquadScope-Podcaster, SquadScope-Coordinator |

---

## 1. Business Context and Background

Claracle (internal codename **SquadScope**) is an AI-powered GitHub trend observatory. A weekly automated pipeline crawls GitHub and selected external news sources, uses Copilot CLI to separate signal from noise, generates Hugo content, and publishes a static site at `www.claracle.com`. Published articles are handed off to the Podcaster system for episode generation.

The current site is organized around **time** — weekly issues (`content/weekly/YYYY/WNN.md`), plus monthly and yearly rollups. Topic hubs exist only in nascent form (a single `content/topics/ai-ml/` hub with placeholder framing). Distribution planning already exists (`docs/growth/distribution-strategy.md`) and an initial on-page SEO metadata audit has been captured, but the underlying **content architecture is still time-first, not topic- or data-first**.

An external SEO/growth analysis (July 2026) reviewed the site's analytics export and positioning. Its central conclusion: **discovery, not conversion, is the core problem.** Traffic is negligible (a handful of sessions, one visit from ChatGPT, no meaningful referral ecosystem). Time-organized weekly summaries are structurally hard to rank because they are time-sensitive, repetitive week-over-week, competing against high-authority incumbents (GitHub, Hacker News, InfoQ, Dev.to, Reddit), and not aligned to durable search intent.

The analysis identifies the strategic asset: Claracle sits on a **longitudinal record of GitHub technology trends**. Unique data is more linkable and more rankable than AI-generated commentary. The recommended strategic shift is to treat the weekly report as a *raw data presentation layer* and build the next version of the site around **evergreen, topic- and data-oriented pages that accumulate authority over time.**

This BRD defines the business requirements for that next version.

---

## 2. Problem Statement and Business Drivers

### 2.1 Problem Statement

Claracle's content and information architecture optimize for a weekly publishing rhythm rather than for how audiences and search engines discover content. As a result:

- Organic discovery is near zero; the site has no accumulating search authority.
- The site's most valuable asset — a multi-year, structured GitHub trend dataset — is not exposed as linkable, citable, or reusable pages/assets.
- There are no durable landing pages aligned to real search demand (topics, repositories, annual "state of" reports).
- There is no linkable-asset or backlink strategy operationalized on the site itself (datasets, charts with embeds, free tools, statistics pages).

### 2.2 Business Drivers

| Driver | Type | Description |
|--------|------|-------------|
| Discovery gap | Growth | Organic search and referral discovery are effectively absent; the site cannot grow without a structural fix. |
| Underused data moat | Competitive | The longitudinal GitHub trend dataset is a differentiator vs. generic AI blogs; it is currently locked inside prose. |
| Authority compounding | Growth | Evergreen topic/data/repository pages accumulate ranking authority; weekly pages do not. |
| Linkable assets | Growth | Datasets, charts, and tools attract backlinks; summaries rarely do. |
| Cross-repo leverage | Efficiency | The SquadScope repository and the dataset can become discovery/backlink engines feeding Claracle. |

---

## 3. Business Objectives and Success Metrics

> Baselines are confirmed near-zero. Discovery is measured with **Google Analytics 4 (GA4)** and **Google Search Console (GSC)**. Because absolute numbers are tiny, several targets are stated as absolute counts rather than only multipliers.

| ID | Objective | KPI | Baseline | Target | Timeframe |
|----|-----------|-----|----------|--------|-----------|
| OBJ-1 | Establish durable, topic-aligned discovery surface | Number of evergreen topic/data/repository pages indexed by Google | ~0 (weekly-only) | ≥ 40 evergreen pages indexed | 3 months post-launch |
| OBJ-2 | Grow organic search discovery | Organic sessions / month (GA4 + GSC) | Near-zero (confirmed) | ≥ 250 organic sessions / month | 6 months post-launch |
| OBJ-3 | Turn the dataset into a linkable asset | Number of external backlinks to data/dataset/chart/tool pages | ~0 | ≥ 25 referring domains | 6 months post-launch |
| OBJ-4 | Rank for target head/mid-tail queries | Queries with impressions in GSC; count in top 20 | Near-zero (confirmed) | ≥ 15 queries in top 20 | 6 months post-launch |
| OBJ-5 | Improve technical SEO completeness | On-page SEO checklist coverage (titles, meta, canonical, OG, Twitter, Article + Breadcrumb schema, sitemaps, RSS) | Partial (see §7) | 100% of checklist items met and validated | At launch |
| OBJ-6 | Preserve pipeline integrity and cross-repo contracts | Weekly pipeline success rate; Podcaster handoff smoke pass rate | Current (assumed passing) | No regression | Ongoing |

---

## 4. Stakeholders and Roles

| Stakeholder | Role | Interest / Responsibility |
|-------------|------|---------------------------|
| jmservera | Sponsor / Product owner | Sets priorities, approves scope, owns brand (Claracle); human approval authority. |
| Leela (squad Lead) | Architecture, review, triage | Approves architecture and information-architecture changes. |
| Amy (squad Frontend) | Hugo templates, CSS, UX | Implements topic hubs, repository pages, structured SEO, internal linking, charts embeds. |
| Bender (squad Crawler) | Data pipeline, GitHub API | Provides/extends structured trend data needed for data and repository pages. |
| Farnsworth (squad Analyst) | Content generation, AI analysis | Ensures generated content links to evergreen hubs and feeds data pages. |
| Fry (squad Tester) | pytest, quality gates | Validates content generation, link integrity, and build gates. |
| URL (DevSecOps) | Guardrail pipeline | Ensures new tooling/pages respect DevSecOps guardrails and CI correctness. |
| Hermes (Security) | Security review, prompt-injection guardrails | Reviews any user-facing tools/embeds and dataset exposure for abuse/injection risk. |
| SquadScope-Podcaster maintainers | Downstream consumer | Depend on `config/podcast.json` and handoff payload contract; must be coordinated on any change. |
| End readers (developers, tech leads, founders/investors) | Audience | Defined personas in `docs/growth/distribution-strategy.md`. |

---

## 5. Scope

### 5.1 In Scope

- Repositioning the site information architecture from time-first to topic/data-first while retaining weekly/monthly/yearly issues as a presentation layer.
- **Evergreen topic hubs** that accumulate authority and are updated as new weekly data lands.
- **Data pages** derived from the GitHub trend dataset (rankings, growth, "top N" lists).
- **Repository pages** for repositories that recur across weekly reports.
- **Structured on-page SEO**: unique titles, meta descriptions, canonical URLs, Open Graph, Twitter/X cards, Schema.org Article + Breadcrumb markup, XML sitemap, RSS feeds, and (if applicable) news sitemap; Google Search Console connected.
- **Internal linking graph**: weekly → previous/next, weekly → topic hubs, weekly → repository/technology pages.
- **Linkable assets**: downloadable datasets, charts with embed codes, and at least one free interactive tool.
- **Statistics / annual "State of" report** pages.
- Repository (`SquadScope`) README/discovery improvements that point to Claracle as the published data source.

### 5.2 Out of Scope

- Rebuilding the crawl/analysis pipeline architecture (Copilot CLI two-step, model routing) beyond what is needed to expose data.
- Changing the Podcaster handoff contract or `config/podcast.json` schema (any change requires separate cross-repo coordination — see §9).
- Paid acquisition / advertising.
- Account-based features, authentication, or user-generated content.
- Migrating off Hugo / GitHub Pages (static-site model is retained).

### 5.3 Assumptions

- The site remains a Hugo + PaperMod static site on GitHub Pages.
- The longitudinal trend data exists and is (or can be made) queryable from pipeline artifacts under `data/`.
- No secrets are exposed; all new automation follows existing DevSecOps guardrails.

### 5.4 Constraints

- **The weekly trend crawl is working and must remain untouched.** Its output is the authoritative data base for topic hubs, data pages, and repository pages; this initiative consumes that output rather than modifying the crawl.
- Static-site constraints: interactive "tools" must run **client-side only** (no server backend implied by current GitHub Pages hosting).
- CI must be correct, not just green; rendered output must be verified for site changes.
- Cross-repo files (`config/podcast.json`, `scripts/podcaster_handoff.py`) are contract surfaces and must not be broken.

---

## 6. Business Requirements

> Priority scale: **Must** (launch-blocking), **Should** (high value, near-term), **Could** (opportunistic). Each requirement links to an objective and lists acceptance criteria.

### 6.1 Content Architecture — Topic Hubs

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| BR-001 | The site shall provide evergreen topic hub pages (e.g., AI Coding Agents, MCP Ecosystem, Open-Source LLMs, Developer Tools, AI Agents in Healthcare) that persist and accumulate content over time. | OBJ-1, OBJ-2 | Must |
| BR-002 | Each weekly issue shall link to the relevant topic hub(s) it references. | OBJ-1, OBJ-4 | Must |
| BR-003 | Each topic hub shall be updated automatically as new weekly data lands, without manual rewrites. | OBJ-1 | Should |
| BR-004 | Topic hubs shall follow a **continuity + dynamic** lifecycle: existing hubs persist and accumulate over time, and a new hub shall be created when the pipeline detects a new, sufficiently important technology trend not covered by an existing hub. Topics shall stay aligned with current technology trends to maximize discoverability. | OBJ-1, OBJ-2, OBJ-4 | Should |

- **BR-001 acceptance:** At least 5 topic hubs exist as durable URLs with unique title/meta/canonical; each aggregates related weekly issues and dataset highlights; each has its own RSS feed. Initial set (subject to trend alignment): AI Coding Agents, MCP Ecosystem, Open-Source LLMs, Developer Tools, plus one vertical (e.g., AI Agents in Healthcare).
- **BR-002 acceptance:** Generated weekly content contains resolvable internal links to every topic hub it discusses; link check passes in CI.
- **BR-003 acceptance:** A new weekly publish updates affected topic hubs (e.g., "recent issues", latest rankings) with no manual edit.
- **BR-004 acceptance:** A **configurable** importance threshold/heuristic (default: a candidate topic appears in **4 or more weekly issues within the last two months**), derived from existing weekly crawl+analysis signals, triggers creation of a new topic hub; the threshold can be changed without code edits; hubs are never deleted on a single quiet week (continuity), and new-hub creation is logged. The weekly crawl itself is not modified — its output is the input to this logic (see §5.4).

### 6.2 Data Pages

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| BR-010 | The site shall publish data pages derived from the trend dataset (e.g., "Top 100 AI repositories this month", "Fastest-growing repositories this year", "Most starred MCP projects"). | OBJ-1, OBJ-3 | Must |
| BR-011 | Each data page shall present a clearly labeled, timestamped ranking with a documented methodology reference. | OBJ-3, OBJ-5 | Must |
| BR-012 | Data pages shall be regenerated on a defined cadence (e.g., monthly) from pipeline artifacts. | OBJ-1 | Should |

- **BR-010 acceptance:** At least 3 data pages published from real dataset artifacts; each ranks repositories with a defined metric.
- **BR-011 acceptance:** Every ranking shows "as of" date, metric definition, and a link to the public methodology page.
- **BR-012 acceptance:** Regeneration runs on schedule and updates pages without manual intervention.

### 6.3 Repository Pages

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| BR-020 | The site shall provide dedicated pages for repositories that recur across weekly reports (e.g., `/repo/<slug>`). | OBJ-1, OBJ-3, OBJ-4 | Should |
| BR-021 | Each repository page shall include growth history, star velocity, weekly-report appearances, and related repositories. | OBJ-3 | Should |
| BR-022 | Repository pages shall be created automatically once a repository crosses a **configurable** recurrence threshold (default: appears in **more than 3 distinct weekly issues**). | OBJ-1 | Could |
| BR-023 | Repository pages shall handle upstream lifecycle changes: on **rename**, rename the page and add a redirect from the old URL where possible; on **archive**, add an "archived" note; on **delete**, add a "deleted" note and retain the page as a historical record for **at least 3 years**. | OBJ-3, OBJ-5 | Should |

- **BR-020 acceptance:** Repository pages exist for the top recurring repositories with stable, canonical URLs.
- **BR-021 acceptance:** Each page shows the four data elements sourced from the dataset, plus internal links to the topic hubs and weekly issues where the repo appeared.
- **BR-022 acceptance:** A recurrence threshold (default: > 3 distinct weekly issues) triggers page creation during generation; the threshold is exposed as configuration and can be changed without code edits.
- **BR-023 acceptance:** Rename produces a renamed page with a redirect (where the static host allows); archive and delete each add the corresponding note; deleted-repo pages persist ≥ 3 years with their historical data and an "as of last seen" date.

> **What a "repository page" is and its implications.** A repository page is a dedicated, evergreen landing page for a single GitHub repository that Claracle has tracked over time (e.g., `/repo/langchain-langchain/`). It is generated from the existing crawl/analysis dataset — not by re-crawling on demand — and presents that repo's Claracle history: star/growth trajectory, star velocity, the list of weekly issues it appeared in, and related repositories seen alongside it. Its purpose is to capture existing search demand (people already search specific repo names) and to become a citable reference.
>
> Implications to plan for:
> - **Content model:** requires a per-repository identity/slug and a way to accumulate a repo's appearances and metrics across weeks from `data/` artifacts (no new crawl).
> - **Volume & quality:** unbounded auto-generation risks thin/duplicate pages that hurt SEO; a recurrence threshold (BR-022) gates creation so only repositories with enough signal get a page.
> - **Stability & change data:** URLs must stay stable; repos can be renamed, archived, or deleted upstream — pages need a defined handling (mark archived, keep historical data, avoid dead outbound links).
> - **Maintenance:** pages update on the normal generation cadence; internal links to/from topic hubs and weekly issues must stay valid (covered by the CI link-check, BR-041).
> - **Provenance:** each metric shows an "as of" date and links to methodology (DR-003), since the data is historical, not live.

### 6.4 Structured On-Page SEO

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| BR-030 | Every page shall have a unique title tag and meta description. | OBJ-5, OBJ-2 | Must |
| BR-031 | Every page shall declare a canonical URL. | OBJ-5 | Must |
| BR-032 | Every page shall emit Open Graph and Twitter/X card tags, including image, image alt, and dimensions, with a homepage/fallback OG image. | OBJ-5 | Must |
| BR-033 | Article pages shall emit Schema.org Article markup; hub/data/repository pages shall emit appropriate schema; all pages in a hierarchy shall emit Breadcrumb schema. | OBJ-5, OBJ-4 | Must |
| BR-034 | The site shall publish an XML sitemap using **Hugo's built-in sitemap generation** and RSS feeds (site-wide and per topic). A separate Google News sitemap is **not required** (the site is not a registered news publisher; the standard sitemap suffices). | OBJ-5, OBJ-2 | Must |
| BR-035 | Google Search Console shall be connected and verified for the production domain. | OBJ-2, OBJ-4 | Must |

- **BR-030 acceptance:** Automated check confirms no duplicate or empty titles/meta descriptions across the build.
- **BR-032 acceptance:** Facebook/Twitter link debuggers render a valid preview with image for homepage and article pages (closes gaps 1–7 in `docs/growth/distribution-strategy.md`).
- **BR-033 acceptance:** Google Rich Results Test validates Article and Breadcrumb markup with no errors.
- **BR-034 acceptance:** Hugo-generated `sitemap.xml` and RSS feeds are reachable and valid; per-topic feeds resolve. No separate news sitemap is produced.
- **BR-035 acceptance:** Search Console verifies the property and receives sitemap submission.

### 6.5 Internal Linking

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| BR-040 | Every weekly article shall link to the previous and next week, its topic hubs, and referenced repository/technology pages. | OBJ-1, OBJ-4 | Must |
| BR-041 | Internal links shall be validated in CI; broken internal links shall fail the build gate. | OBJ-5 | Should |

- **BR-040 acceptance:** Rendered weekly pages contain prev/next, topic-hub, and repo links where applicable.
- **BR-041 acceptance:** A link-check step runs in CI and fails on broken internal links.

### 6.6 Linkable Assets (Datasets, Charts, Tools)

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| BR-050 | The site shall offer downloadable datasets (e.g., CSV of top GitHub projects, weekly trend archive) released under the **MIT license**, with **all sources/references cited**. | OBJ-3 | Should |
| BR-051 | The site shall generate charts (growth curves, technology rankings, momentum) with an embed mechanism so third parties can reuse them with attribution/backlink. | OBJ-3 | Should |
| BR-052 | The site shall provide at least one free, **client-side-only** interactive tool (e.g., GitHub trend explorer, star-velocity tracker). The specific tool and its client-side technology shall be selected via a short design spike evaluating discoverability value, build effort, and static-hosting fit. | OBJ-3, OBJ-2 | Could |
| BR-053 | The site shall publish annual/periodic statistics pages (e.g., "State of Open Source AI 2026"). | OBJ-3, OBJ-4 | Should |

- **BR-050 acceptance:** At least one downloadable dataset is published under the MIT license with an accompanying citation/attribution note listing all sources; download link is stable.
- **BR-051 acceptance:** At least one chart type is embeddable via provided snippet that links back to Claracle.
- **BR-052 acceptance:** A design spike recommends one client-side-only tool with rationale; the selected tool ships and runs entirely in the browser with no backend dependency.
- **BR-053 acceptance:** At least one "State of…" report page is published and linked from relevant hubs.

### 6.7 Repository as Discovery Engine

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| BR-060 | The `SquadScope` repository README shall present the project clearly (purpose, screenshots, architecture, example outputs) and point to the published data at Claracle. | OBJ-3 | Should |

- **BR-060 acceptance:** README includes description, screenshots/diagram, example outputs, and a "Data published weekly at claracle.com" reference with links.

---

## 7. Current and Future Business Processes

### 7.1 Current State (As-Is)

1. Weekly crawl → two-step Copilot analysis → generate `content/weekly/YYYY/WNN.md` → Hugo build → GitHub Pages → Podcaster handoff.
2. Content is time-indexed (weekly/monthly/yearly). Topic hubs are placeholder-only.
3. On-page SEO is partially implemented: meta description, BlogPosting schema, basic OG and Twitter cards are present; OG image fallback/alt/dimensions, `article:author`, `twitter:creator`, and homepage OG image are **gaps** already catalogued in `docs/growth/distribution-strategy.md`.
4. Distribution is a manual per-week social playbook; no operational linkable-asset or backlink engine on-site.

### 7.2 Future State (To-Be)

1. The pipeline continues to produce weekly issues, but generation also **updates evergreen topic hubs, data pages, and repository pages** from the same dataset.
2. Content is discoverable by **topic and data**, with weekly issues acting as the presentation/freshness layer that links into evergreen hubs.
3. On-page SEO is complete and validated (titles, meta, canonical, OG, Twitter, Article + Breadcrumb schema, sitemaps, RSS, Search Console).
4. The site hosts **linkable assets** (datasets, embeddable charts, at least one tool, annual reports); the repository README functions as a secondary discovery/backlink surface.

---

## 8. Data and Reporting Requirements

| ID | Requirement | Objective | Priority |
|----|-------------|-----------|----------|
| DR-001 | The trend dataset (repositories, metrics, weekly appearances, growth/velocity over time) shall be exposed in a structured, queryable form usable by content generation for hubs, data pages, and repo pages. | OBJ-1, OBJ-3 | Must |
| DR-002 | Discovery and ranking performance shall be measurable via **Google Analytics 4 and Google Search Console**; baseline is confirmed near-zero and both properties shall be connected/verified for the production domain. | OBJ-2, OBJ-4 | Must |
| DR-003 | Published rankings and datasets shall carry provenance (source, "as of" date, methodology link) consistent with the existing methodology and corrections policy. | OBJ-5 | Must |

- **DR-002 note:** Analytics stack is confirmed as GA4 + GSC. Baseline is near-zero; capture a dated snapshot of sessions, sources, and query impressions at launch to anchor the KPI trend line.

---

## 9. Cross-Repository Impact and Coordination

Per repository conventions, the following must be coordinated with **SquadScope-Podcaster** and tracked under the DevSecOps Guardrails epic where relevant:

- Changes to `config/podcast.json` — Podcaster reads this config; out of scope here, but any incidental change requires coordination.
- Changes to `scripts/podcaster_handoff.py` — defines the handoff payload contract; must not break.
- New site content types (topic hubs, data/repo pages) must not alter the handoff payload (`week`, `article_url`, `article_content`, `article_title`, `article_sha256`, `source_artifacts`, `podcast_config`, `script_directions`, `breaking_news`).
- The handoff smoke test (`.github/workflows/podcaster-handoff-smoke.yml`) must continue to pass.

---

## 10. Benefits and High-Level Economics

- **Primary benefit:** A compounding organic-discovery surface that grows without paid acquisition, converting an existing data asset into durable ranking authority and backlinks.
- **Strategic benefit:** Repositions Claracle from "another AI blog" to "the public database of GitHub technology trends" — a defensible moat.
- **Cost profile:** Predominantly build effort within the existing static-site + pipeline model; no new hosting backend implied. Incremental generation cost for hubs/data/repo pages should be quantified during design (TODO).

---

## 11. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Thin/duplicate evergreen pages harm SEO instead of helping | High | Medium | Enforce unique titles/meta, real data, and methodology provenance; add content-quality gates. |
| Static hosting limits "interactive tools" | Medium | Medium | Constrain tools to client-side or pre-generated data; validate feasibility in design. |
| Automated page generation breaks internal links | Medium | Medium | CI link-check gate (BR-041). |
| Cross-repo contract regression (Podcaster) | High | Low | Keep handoff payload unchanged; retain smoke test (§9). |
| Dataset/tool exposure introduces abuse or prompt-injection surface | Medium | Low | Security review by Hermes; follow `docs/prompt-injection-guardrails.md`. |
| Baseline metrics unavailable, making success unmeasurable | Medium | Medium | Capture Search Console + analytics baseline before build (DR-002). |
| Over-scoping (tools, datasets, reports all at once) delays discovery wins | Medium | Medium | Sequence per SEO analysis: architecture + linking first, then assets. |

---

## 12. Suggested Sequencing (Non-Binding)

Aligned to the SEO analysis phasing; final sequencing is a delivery decision.

- **Wave 1 (foundation):** Topic hubs (BR-001–003), structured SEO (BR-030–035), internal linking (BR-040–041), Search Console. → OBJ-1, OBJ-5.
- **Wave 2 (data assets):** Data pages (BR-010–012), repository pages (BR-020–022), first downloadable dataset (BR-050), first "State of" report (BR-053). → OBJ-3.
- **Wave 3 (amplification):** Embeddable charts (BR-051), one free tool (BR-052), repository README as discovery engine (BR-060). → OBJ-2, OBJ-3.

---

## 13. Open Questions / TODO

Resolved in elicitation (2026-07-29):

- ✅ Sponsor and approval authority: **jmservera** (human approval authority).
- ✅ Analytics baseline: **near-zero, confirmed**; measured with **GA4 + GSC**.
- ✅ Wave 1 topic hubs: AI Coding Agents, MCP Ecosystem, Open-Source LLMs, Developer Tools, plus one vertical (e.g., AI Agents in Healthcare) — kept **trend-aligned and dynamic** (BR-004).
- ✅ Dataset licensing: **MIT**, cite all references (BR-050).
- ✅ Free tool: **client-side-only**, specific tool chosen via design spike (BR-052).
- ✅ Repository pages: definition and implications documented (§6.3).
- ✅ Repository-page recurrence threshold: **configurable**, default **> 3 distinct weekly issues** (BR-022).
- ✅ Repository lifecycle handling: rename+redirect, archived note, deleted note retained **≥ 3 years** (BR-023).
- ✅ New-topic-hub trigger: **configurable**, default **≥ 4 weekly issues within the last two months** (BR-004).
- ✅ Sitemap: use **Hugo's built-in** sitemap; **no** separate news sitemap (BR-034).

Still open:

1. Quantify **incremental generation cost/time** for hubs, data, and repository pages.
