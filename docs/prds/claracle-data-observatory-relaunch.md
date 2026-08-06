---
title: Claracle Data Observatory Relaunch Product Requirements Document
description: Product requirements, delivery state, rollout controls, risks, and acceptance gates for the Claracle Data Observatory relaunch
author: SquadScope Squad
ms.date: 2026-08-05
ms.topic: reference
---
<!-- markdownlint-disable-file -->
<!-- markdown-table-prettify-ignore-start -->
Version 1.4 | Status Acceptance pending | Owner jmservera | Team SquadScope Squad | Target Wave 1 (foundation) | Lifecycle Definition

## Progress Tracker
| Phase | Done | Gaps | Updated |
|-------|------|------|---------|
| Context | Yes | None | 2026-07-29 |
| Problem & Users | Yes | None | 2026-07-29 |
| Scope | Yes | None | 2026-07-29 |
| Requirements | Yes | Incremental generation cost still to quantify | 2026-07-30 |
| Metrics & Risks | Yes | None | 2026-07-29 |
| Operationalization | Yes | Star Velocity Explorer selected; production evidence pending | 2026-07-30 |
| Finalization | No | Security, baseline and consent, accessibility, timing-budget, and visual gates remain open | 2026-08-05 |
Unresolved launch gates: See the launch-gate register | TBDs: 1 (incremental generation cost)

## Acceptance Status

Repository implementation is present, and the GA4/GSC connection, protected downstream
Podcaster run, atomic publication proof, and separate sponsor rollout decisions are
complete. Dated baseline values and production consent observations remain pending.3
NFR-004 final acceptance, remaining production responses, external schema and social
debuggers, accessibility review, timing-budget approval, and refreshed visual evidence
are not recorded. `dynamic_topic_creation` and `repo_pages` remain off pending their
recorded technical conditions and separate activation changes. Delivered-versus-pending
status and the launch-gate register are tracked in the [relaunch status of record](../review/data-observatory-relaunch/status-of-record.md).

Derived from: `docs/brds/claracle-data-observatory-relaunch-brd.md` (BRD-CLARACLE-002, v1.2).

## 1. Executive Summary
### Context
Claracle (codename SquadScope) is a Hugo + PaperMod static site published to GitHub Pages. A weekly pipeline crawls GitHub and external news, runs a two-step Copilot CLI analysis, generates `content/weekly/YYYY/WNN.md`, builds the site, and hands the article to the Podcaster system. Today the site is organized around time (weekly/monthly/yearly). Topics exist as a Hugo taxonomy (`topic`) with per-topic RSS and layouts (`layouts/topics/list.html`, `terms.html`), but weekly content generation does not currently emit a `topics` field, so those hubs stay empty of accumulated issues. On-page SEO is partially implemented (meta description, BlogPosting schema, basic OG/Twitter cards) with known gaps catalogued in `docs/growth/distribution-strategy.md`.

### Core Opportunity
An external SEO analysis concluded discovery (not conversion) is the core problem: near-zero organic traffic and no referral ecosystem. The strategic asset is a longitudinal GitHub trend dataset that is more linkable and rankable than weekly commentary. This PRD specifies the product changes to reposition Claracle into a discoverable, linkable public database of GitHub technology trends, treating the weekly report as one presentation layer over durable, evergreen topic/data/repository pages.

### Goals
| Goal ID | Statement | Type | Baseline | Target | Timeframe | Priority |
|---------|-----------|------|----------|--------|-----------|----------|
| G-001 | Establish a durable, topic-aligned discovery surface | Growth | ~0 evergreen pages | >= 40 evergreen pages indexed | 3 months post-launch | Must |
| G-002 | Grow organic search discovery | Growth | Pending GA4/GSC capture | >= 250 organic sessions/month | 6 months post-launch | Must |
| G-003 | Turn the dataset into a linkable asset | Growth | ~0 backlinks | >= 25 referring domains | 6 months post-launch | Should |
| G-004 | Rank for target head/mid-tail queries | Growth | Pending GSC capture | >= 15 queries in top 20 | 6 months post-launch | Should |
| G-005 | Complete and validate technical SEO | Quality | Partial | 100% checklist met and validated | At launch | Must |
| G-006 | Preserve pipeline integrity and cross-repo contracts | Reliability | Passing | No regression | Ongoing | Must |

### Objectives (Optional)
| Objective | Key Result | Priority | Owner |
|-----------|------------|----------|-------|
| Ship evergreen information architecture | Topic hubs populated + linked from every weekly issue | Must | Amy |
| Expose the dataset | >= 3 data pages + 1 downloadable dataset live | Should | Bender |
| Make it citable | >= 1 embeddable chart + 1 client-side tool | Could | Amy |

## 2. Problem Definition
### Current Situation
Content and information architecture optimize for a weekly cadence rather than for how audiences and search engines discover content. The dataset that differentiates Claracle is locked inside prose; there are no durable landing pages aligned to real search intent, and no on-site linkable-asset or backlink mechanism.

### Problem Statement
Because Claracle's structure is time-first, it accumulates no search authority, exposes no linkable data, and cannot grow discovery organically - despite owning a unique longitudinal GitHub trend dataset.

### Root Causes
* Time-indexed pages are repetitive, time-sensitive, and compete against high-authority incumbents.
* The `topics` taxonomy is not populated because generated weekly frontmatter omits `topics`.
* No data/repository pages, datasets, charts, or tools exist to attract links.

### Impact of Inaction
Discovery stays near zero, the data moat remains hidden, and the weekly investment produces content that neither ranks nor earns backlinks.

## 3. Users & Personas
| Persona | Goals | Pain Points | Impact |
|---------|-------|------------|--------|
| Signal-seeking developer | Find durable, curated insight on a technology (agents, MCP, small models) | Weekly pages are ephemeral; hard to find "the page" on a topic | High - primary organic search audience |
| Tech lead / EM | Understand ecosystem shifts for planning and hiring | No topic-level or repo-level reference to cite in standups | High - repeat visitor, shares links |
| Founder / investor | Track emerging categories and momentum | No data/rankings pages to skim | Medium - values data pages and "State of" reports |
| Data citer (blogger, researcher, journalist) | Cite original data and charts | Nothing linkable; only summaries | High - source of backlinks (G-003) |
| Search visitor (query-driven) | Land on a page matching a specific query or repo name | Only time-based pages exist; poor intent match | High - conversion of organic impressions |

### Journeys (Optional)
Search visitor searches "MCP ecosystem trends" or a repo name, lands on an evergreen topic hub or `/repo/<slug>` page, follows internal links to related weekly issues and data pages, and (for citers) copies a chart embed or downloads a dataset, generating a backlink.

## 4. Scope
### In Scope
* Populate and elevate the existing `topics` taxonomy into evergreen topic hubs, updated automatically from weekly data, with a continuity + dynamic-creation lifecycle.
* Data pages (rankings/"top N") generated from `data/` artifacts.
* Repository pages (`/repo/<slug>`) with growth history, star velocity, appearances, related repos, and lifecycle handling.
* Structured on-page SEO: unique titles/meta, canonical, OG + Twitter cards (closing the catalogued gaps), Schema.org Article + Breadcrumb, Hugo-generated sitemap, RSS (site + per topic), GSC connection.
* Internal linking graph (weekly prev/next, weekly -> topic hubs, weekly -> repo/topic pages) with a CI link-check gate.
* Linkable assets: MIT-licensed downloadable datasets with citations, embeddable charts, at least one client-side-only tool, and periodic "State of" statistics pages.
* `SquadScope` README as a secondary discovery/backlink surface.

### Out of Scope (justify if empty)
* Modifying the weekly crawl/analysis pipeline beyond emitting data needed downstream - the crawl works and must stay untouched.
* Changing the Podcaster handoff contract or `config/podcast.json` schema.
* Paid acquisition, authentication, accounts, or user-generated content.
* Migrating off Hugo / GitHub Pages; any server-backed tool.
* A Google News sitemap (site is not a registered news publisher).

### Assumptions
* Hugo + PaperMod on GitHub Pages is retained; `topic` taxonomy and per-topic RSS already exist.
* The longitudinal dataset is available/derivable from `data/` artifacts (raw, snapshots, analyzed).
* `markup.goldmark.renderer.unsafe = false` stays; embeds use shortcodes/layouts, not raw HTML in content.

### Constraints
* Weekly crawl output is the single source of truth; features consume it, never re-crawl on demand.
* Tools must be client-side only (no backend on GitHub Pages).
* Cross-repo files (`config/podcast.json`, `scripts/podcaster_handoff.py`) must not break; handoff smoke test must pass.
* CI must be correct, not just green; rendered output verified for site changes.

## 5. Product Overview
### Value Proposition
"The public database of GitHub technology trends." Durable topic, data, and repository pages that accumulate ranking authority and offer citable, MIT-licensed data - with weekly issues as the freshness layer that links into them.

### Differentiators (Optional)
* Original longitudinal dataset vs. generic AI commentary.
* Signal-vs-noise editorial method already established.
* Evergreen pages that compound authority over time.

### UX / UI (Conditional)
Extends the existing PaperMod theme and topic layouts. New page types: topic hub (enhanced taxonomy term page with dataset highlights), data page (ranking tables + charts), repository page (`/repo/<slug>`). Charts and tools ship as Hugo shortcodes/layouts to respect `unsafe = false`. UX Status: Design spike required for the client-side tool (FR-052) and chart embed component (FR-051).

## 6. Functional Requirements
| FR ID | Title | Description | Goals | Personas | Priority | Acceptance | Notes |
|-------|-------|------------|-------|----------|----------|-----------|-------|
| FR-001 | Evergreen topic hubs | Provide >= 5 topic hubs as durable URLs via the `topic` taxonomy, each with unique title/meta/canonical, aggregated issues, dataset highlights, and per-topic RSS. Initial set: AI Coding Agents, MCP Ecosystem, Open-Source LLMs, Developer Tools, plus one vertical (e.g., AI Agents in Healthcare). | G-001,G-002 | Signal-seeker, Search visitor | Must | 5+ hubs live with unique metadata and RSS; each lists related weekly issues. | Maps BR-001; leverages existing `layouts/topics`. |
| FR-002 | Emit topics from generation | `generate_content.py` shall emit a `topics` frontmatter field derived from the weekly analysis so each issue populates its topic hub(s) and links to them. | G-001,G-004 | Search visitor | Must | Generated weekly issues include resolvable `topics`; topic hubs show the issue; CI link-check passes. | Closes current gap: frontmatter omits `topics`. |
| FR-003 | Auto-update hubs on publish | Publishing a weekly issue shall update affected topic hubs (recent issues, latest highlights) with no manual edit. | G-001 | Signal-seeker | Should | New publish updates hub pages automatically in the build. | Maps BR-003. |
| FR-004 | Dynamic topic lifecycle | Create a new topic hub when a candidate trend crosses a configurable importance threshold (default: appears in >= 4 weekly issues within the last two months); hubs persist through quiet weeks (continuity); creation is logged. | G-001,G-002,G-004 | Signal-seeker | Should | Config-driven threshold changeable without code edits; new-hub creation logged; no hub deleted on a single quiet week. | Maps BR-004; reuses existing analysis signals. |
| FR-010 | Data pages | Generate >= 3 data pages from `data/` artifacts (e.g., "Top 100 AI repositories this month", "Fastest-growing repositories this year", "Most starred MCP projects"), each a labeled, timestamped ranking with a methodology link. | G-001,G-003 | Founder, Data citer | Must | 3+ data pages from real artifacts; each shows metric definition, "as of" date, methodology link. | Maps BR-010/011. |
| FR-011 | Data page regeneration | Regenerate data pages on a defined cadence (e.g., monthly) from artifacts without manual intervention. | G-001 | Founder | Should | Scheduled regeneration updates pages automatically. | Maps BR-012. |
| FR-020 | Repository pages | Provide `/repo/<slug>` pages for recurring repositories with growth history, star velocity, weekly appearances, and related repos; stable canonical URLs. | G-001,G-003,G-004 | Search visitor, Data citer | Should | Pages exist for top recurring repos with the four data elements and internal links to hubs/issues. | Maps BR-020/021; built from dataset, no re-crawl. |
| FR-021 | Repo-page creation threshold | Auto-create a repository page once a repo crosses a configurable recurrence threshold (default: > 3 distinct weekly issues). | G-001 | Search visitor | Could | Config-driven threshold triggers creation; changeable without code edits. | Maps BR-022. |
| FR-022 | Repo lifecycle handling | On upstream rename: rename page + redirect where possible. On archive: add "archived" note. On delete: add "deleted" note and retain page >= 3 years with historical data and "as of last seen" date. | G-003,G-005 | Data citer | Should | Rename/archive/delete each handled as specified; deleted pages persist >= 3 years. | Maps BR-023. |
| FR-030 | Unique titles and meta | Every page has a unique, non-empty title tag and meta description. | G-005,G-002 | Search visitor | Must | Automated build check finds no duplicate/empty titles or meta descriptions. | Maps BR-030. |
| FR-031 | Canonical URLs | Every page declares a canonical URL. | G-005 | Search visitor | Must | Canonical present and correct on all page types. | Maps BR-031. |
| FR-032 | OG + Twitter cards | Emit Open Graph and Twitter/X tags including image, `og:image:alt`, width/height, `article:author`, `twitter:creator`, plus a homepage/fallback OG image. | G-005 | Data citer | Must | FB/Twitter debuggers render valid previews with image on homepage and articles; closes gaps 1-7 in distribution-strategy.md. | Uses existing `default_social_image` param. |
| FR-033 | Structured data | Article pages emit Schema.org Article; hub/data/repo pages emit appropriate schema; all hierarchical pages emit Breadcrumb schema. | G-005,G-004 | Search visitor | Must | Google Rich Results Test validates Article + Breadcrumb with no errors. | Extends `schema_json.html`. |
| FR-034 | Sitemap + RSS | Publish Hugo's built-in `sitemap.xml` and RSS feeds (site-wide + per topic). No news sitemap. | G-005,G-002 | Search visitor | Must | Sitemap and feeds reachable/valid; per-topic feeds resolve. | Hugo `outputs` already emit taxonomy RSS. |
| FR-035 | Search Console | Connect and verify Google Search Console (and confirm GA4) for the production domain; submit sitemap. | G-002,G-004 | Search visitor | Must | GSC property verified, sitemap submitted; GA4 receiving data. | Complete by owner confirmation on 2026-08-02: GA4 stream operational, GSC verified, root sitemap submitted, and products linked. |
| FR-040 | Internal linking | Every weekly article links to previous/next week, its topic hubs, and referenced repository/technology pages. | G-001,G-004 | Signal-seeker | Must | Rendered weekly pages contain prev/next, topic-hub, and repo links where applicable. | PaperMod `ShowPostNavLinks` already on. |
| FR-041 | Link-check gate | Validate internal links in CI; broken internal links fail the build gate. | G-005 | - | Should | CI link-check runs and fails on broken internal links. | Partial: satisfied at test level (`tests/test_internal_link_checker.py`); no standalone CI link tool. |
| FR-050 | Downloadable datasets | Offer MIT-licensed downloadable datasets (e.g., CSV of top projects, weekly trend archive) with all sources cited and a stable link. | G-003 | Data citer | Should | >= 1 dataset published under MIT with citation/attribution note and stable download URL. | Maps BR-050. |
| FR-051 | Embeddable charts | Generate charts (growth curves, rankings, momentum) with an embed snippet that links back to Claracle. | G-003 | Data citer | Should | >= 1 chart type embeddable via provided snippet with backlink. | Shortcode/layout, not raw HTML. |
| FR-052 | Client-side tool | Provide >= 1 free, client-side-only interactive tool (e.g., trend explorer, star-velocity tracker), selected via a design spike weighing discoverability value, effort, and static-hosting fit. | G-003,G-002 | Search visitor, Data citer | Could | Design spike recommends one tool with rationale; tool ships and runs fully in-browser with no backend. | Maps BR-052. |
| FR-053 | Statistics pages | Publish annual/periodic "State of" pages (e.g., "State of Open Source AI 2026") linked from relevant hubs. | G-003,G-004 | Founder, Data citer | Should | >= 1 "State of" page published and linked from hubs. | Maps BR-053. |
| FR-060 | README as discovery engine | Improve the `SquadScope` README (purpose, screenshots, architecture, example outputs) and point to published data at Claracle. | G-003 | Data citer | Should | README includes the elements and a "Data published weekly at claracle.com" reference with links. | Maps BR-060. |

### Feature Hierarchy (Optional)
```plain
Discovery IA
  Topic hubs (FR-001..004)
  Data pages (FR-010..011)
  Repository pages (FR-020..022)
Technical SEO (FR-030..035)
Internal linking (FR-040..041)
Linkable assets
  Datasets (FR-050)
  Charts (FR-051)
  Tool (FR-052)
  Statistics pages (FR-053)
Discovery engine
  README (FR-060)
```

## 7. Non-Functional Requirements
| NFR ID | Category | Requirement | Metric/Target | Priority | Validation | Notes |
|--------|----------|------------|--------------|----------|-----------|-------|
| NFR-001 | Performance | New page types keep the site fast on static hosting | Lighthouse Performance >= 90 on hub/data/repo pages | Should | Lighthouse CI or manual audit | Static pre-rendered; charts lazy-loaded |
| NFR-002 | Reliability | No regression to weekly pipeline or handoff | Weekly pipeline success + handoff smoke unchanged (G-006) | Must | `podcaster-handoff-smoke.yml`, pytest | Crawl untouched; restore mode preserves the published weekly transaction (article, summary, promotion record, rollups) rather than overwriting provenance (`#640`/`#646`) |
| NFR-003 | Maintainability | Thresholds are configuration, not code | Topic (FR-004) and repo (FR-021) thresholds set via config | Must | Change threshold with no code edit in review | |
| NFR-004 | Security | No raw HTML in AI content; no secrets in client tool | `unsafe=false` retained; tool ships no secrets; inputs sanitized | Must | Build config check; Hermes review; `sanitize_repo_content` path | Follows prompt-injection guardrails |
| NFR-005 | Accessibility | New pages meet WCAG 2.1 AA basics | Images have alt; charts have text alternative; contrast passes | Should | axe/Lighthouse a11y audit | OG alt also required (FR-032) |
| NFR-006 | SEO correctness | Structured data and metadata validate | 0 errors in Rich Results Test; no duplicate titles/meta | Must | Rich Results Test; build check (FR-030) | |
| NFR-007 | Observability | Discovery is measurable | GA4 + GSC connected; launch baseline snapshot captured | Must | GSC/GA4 dashboards | Pending external evidence |
| NFR-008 | Privacy | Analytics respects existing consent | GA4 gated by existing cookie consent | Must | `data/cookieconsent.json` flow | |
| NFR-009 | Scalability | Generation scales with dataset growth | Full build time stays within CI budget as pages grow | Should | Build timing in CI | Ties to open cost question |
| NFR-010 | Portability | Everything runs within Hugo static build | No server dependency introduced | Must | Build/deploy on GitHub Pages | |
| NFR-011 | Reliability | Deploy and CI build the same hydrated content set | CI reproduces the publish-hydration that deploy performs, so generated-content divergence between `main` and `publish` fails CI rather than the production deploy | Must | CI deploy-parity build; `test_pipeline.py` provenance invariant | Root cause of the 2026-07-31 deploy failure (issue #627) |
| NFR-012 | Reliability | Embedded charts never break the site build | Every `content/embeds/*` `source_page` resolves to an existing data page in the built content set | Must | Build-time reference check | The dangling embed reference aborted the 2026-07-31 deploy |

## 8. Data & Analytics (Conditional)
### Inputs
Weekly crawl artifacts under `data/` (`raw/`, `snapshots/`, `analyzed/`) and existing analysis outputs (summaries, correlations). Repository identity, per-week appearances, and star/growth metrics are derived from these without re-crawling.

### Outputs / Events
Generated Hugo content: topic hubs (taxonomy terms), data pages, repository pages, statistics pages; downloadable dataset files (MIT); chart assets with embed snippets. Analytics events via GA4; search performance via GSC.

### Instrumentation Plan
| Event | Trigger | Payload | Purpose | Owner |
|-------|---------|--------|---------|-------|
| page_view | Any page load (consent-gated) | path, referrer, UTM | Discovery/traffic measurement | Amy |
| dataset_download | Dataset link click | dataset id, path | Track linkable-asset usage (G-003) | Bender |
| chart_embed_view | Embedded chart rendered off-site | chart id, host | Detect backlinks/embeds (G-003) | Amy |
| tool_interaction | Client tool use | tool id, action | Validate tool value (FR-052) | Amy |

### Metrics & Success Criteria
| Metric | Type | Baseline | Target | Window | Source |
|--------|------|----------|--------|--------|--------|
| Evergreen pages indexed | Coverage | ~0 | >= 40 | 3 months | GSC |
| Organic sessions/month | Traffic | Pending capture | >= 250 | 6 months | GA4 |
| Referring domains | Backlinks | ~0 | >= 25 | 6 months | GSC / backlink tool |
| Queries in top 20 | Ranking | Pending capture | >= 15 | 6 months | GSC |
| SEO checklist coverage | Quality | Partial | 100% | Launch | Manual + Rich Results |

## 9. Dependencies
| Dependency | Type | Criticality | Owner | Risk | Mitigation |
|-----------|------|------------|-------|------|-----------|
| Weekly crawl output (`data/`) | Internal data | High | Bender | Schema drift | Consume read-only; validate fields |
| `generate_content.py` | Internal code | High | Farnsworth | Regression on frontmatter | Add `topics` behind tests (FR-002) |
| Hugo `topic` taxonomy + `layouts/topics` | Platform | High | Amy | Layout gaps | Extend existing templates |
| SEO partials (`opengraph`, `twitter_cards`, `schema_json`) | Platform | Medium | Amy | Incomplete tags | Close catalogued gaps (FR-032/033) |
| GA4 + GSC | External | High | jmservera | Baseline and consent evidence | Capture dated values and production consent observations (FR-035, NFR-007/008) |
| Podcaster handoff contract | Cross-repo | High | URL/Hermes | Contract break | Keep payload unchanged; smoke test |
| Client-side charting/tool library | External | Medium | Amy | Static-hosting fit | Design spike (FR-051/052) |

## 10. Risks & Mitigations
| Risk ID | Description | Severity | Likelihood | Mitigation | Owner | Status |
|---------|-------------|---------|-----------|-----------|-------|--------|
| R-01 | Thin/duplicate evergreen pages harm SEO | High | Medium | Real data + provenance; unique titles/meta; content-quality gate; thresholds gate creation | Amy | Open |
| R-02 | Static hosting limits interactive tools | Medium | Medium | Constrain to client-side; design spike validates feasibility | Amy | Open |
| R-03 | Auto-generation breaks internal links | Medium | Medium | CI link-check gate (FR-041) | Fry | Open |
| R-04 | Cross-repo contract regression (Podcaster) | High | Low | Keep handoff payload unchanged; retain smoke test | URL | Closed for relaunch evidence; protected run `30908778884` succeeded and downstream returned `accepted` |
| R-05 | Dataset/tool exposure adds abuse/injection surface | Medium | Low | Hermes review; sanitize inputs; `unsafe=false` | Hermes | Open; sign-off pending |
| R-06 | Generation cost/time grows unbounded | Medium | Medium | Quantify in design spike; cap/paginate; incremental builds | Leela | Open |
| R-07 | Over-scoping delays discovery wins | Medium | Medium | Sequence: IA + SEO + linking first, then assets | Leela | Open |
| R-08 | Deploy hydration wipes committed pages referenced by non-hydrated content, breaking the production build while CI stays green | High | Medium | Keep generated-content sources consistent across `main` and `publish`; add a CI deploy-parity build; validate every `content/embeds/*` `source_page` resolves | URL | Open; interim fix ships `content/data` pages from `main` until the crawl publishes them (issue #627) |

## 11. Privacy, Security & Compliance
### Data Classification
Public GitHub metadata and derived aggregates only; no personal data beyond public repo/author handles already surfaced in weekly content.

### PII Handling
No new PII collected. Analytics (GA4) is consent-gated via the existing cookie-consent flow.

### Threat Considerations
AI-generated content must not render raw HTML (`unsafe=false`); repo-derived text passes existing sanitization (`sanitize_repo_content`, `INJECTION_PHRASES`). Client-side tool must not embed secrets or call authenticated endpoints. Chart embeds must be static/self-contained.

### Regulatory / Compliance (Conditional)
| Regulation | Applicability | Action | Owner | Status |
|-----------|--------------|--------|-------|--------|
| Cookie/consent (EU) | GA4 analytics | Keep consent gate | Amy | In place |
| MIT licensing | Downloadable datasets | Attach LICENSE + citations | Bender | Planned (FR-050) |

## 12. Operational Considerations
| Aspect | Requirement | Notes |
|--------|------------|-------|
| Deployment | GitHub Pages via existing Hugo build/CI | No new infra |
| Rollback | Revert content/layout commits; pages are static | Low risk |
| Monitoring | GA4 traffic + GSC coverage/queries | Weekly review |
| Alerting | CI failures (build, link-check, handoff smoke) | Existing gates + FR-041 |
| Support | Squad ownership per role (Amy/Bender/Farnsworth/Fry) | See BRD s4 |
| Capacity Planning | Watch full-build time as page count grows | NFR-009; open cost item |
| Deploy parity | CI must reproduce the deploy's publish-hydration | Prevents `main`/`publish` divergence from reaching production (NFR-011; issue #627) |

## 13. Rollout & Launch Plan
### Phases / Milestones
| Phase | Date | Gate Criteria | Owner |
|-------|------|--------------|-------|
| Wave 1 - Foundation | TBD | Topic hubs populated (FR-001..004), SEO complete + validated (FR-030..035), internal linking + link-check (FR-040..041), GSC verified | Amy |
| Wave 2 - Data assets | TBD | >= 3 data pages (FR-010..011), repository pages (FR-020..022), 1 MIT dataset (FR-050), 1 "State of" page (FR-053) | Bender |
| Wave 3 - Amplification | TBD | Embeddable charts (FR-051), 1 client-side tool (FR-052), README discovery engine (FR-060) | Amy |

### Feature Flags (Conditional)
| Flag | Purpose | Default | Sunset Criteria |
|------|---------|--------|----------------|
| dynamic_topic_creation | Gate auto-creation of new topic hubs | Off; sponsor approval in principle recorded | Security disposition and one approved canary before a separate activation change |
| repo_pages | Gate repository-page generation | Off; sponsor approval recorded | Separate activation transaction after the approved PR #668 evidence |

Owners, dependencies, and evidence paths for every launch gate (including sponsor rollout approval) are consolidated in the [relaunch status of record launch-gate register](../review/data-observatory-relaunch/status-of-record.md#launch-gate-register).

### Communication Plan (Optional)
Use the existing per-week distribution playbook (`docs/growth/distribution-strategy.md`) for launch posts; announce Wave 2 dataset and Wave 3 tool on developer communities (HN, Lobsters, dev.to) when genuinely useful.

## 14. Open Questions
| Q ID | Question | Owner | Deadline | Status |
|------|----------|-------|---------|--------|
| Q-01 | Quantify incremental generation cost/time for hubs, data, and repo pages | Leela | Design spike | Open |
| Q-02 | Which client-side tool to build first (FR-052) | Amy | 2026-07-30 | Resolved: Star Velocity Explorer; see ADR |
| Q-03 | When can `content/data/` deploy hydration be restored (once the crawl reliably publishes observatory pages to `publish`)? | Bender | Post-#627 crawl run | Resolved: hydration restored via `#637` after the crawl repopulated `publish`; CI embed-source guard (`#641`) prevents recurrence |

## 15. Changelog
| Version | Date | Author | Summary | Type |
|---------|------|-------|---------|------|
| 1.4 | 2026-08-05 | SquadScope Squad | Recorded the successful protected Podcaster run, atomic proof, and separate sponsor decisions while preserving open technical and external gates | Updated |
| 1.3 | 2026-08-02 | SquadScope Squad | Reconciled the #627-#646 workstream: deploy/hydration parity restored and CI embed-source guard shipped (`#634`/`#637`/`#641`), Podcaster smoke hardened (`#636`/`#639`/`#643`/`#645`), restore preserves the published weekly transaction (NFR-002; `#640`/`#646`); recorded FR-041 partial status and linked the status of record | Updated |
| 1.2 | 2026-07-31 | SquadScope Squad | Recorded the deploy hydration content-provenance failure (issue #627), the interim `content/data` fix, and the deploy/CI parity requirement (NFR-011/012, R-08) | Updated |
| 1.1 | 2026-07-30 | SquadScope Squad | Reconciled repository delivery with pending external, security, visual, accessibility, Podcaster, and rollout gates | Updated |
| 1.0 | 2026-07-29 | PRD Builder (facilitated) | Initial PRD derived from BRD-CLARACLE-002 v1.0 | Created |

## 16. References & Provenance
| Ref ID | Type | Source | Summary | Conflict Resolution |
|--------|------|--------|---------|--------------------|
| REF-1 | BRD | `docs/brds/claracle-data-observatory-relaunch-brd.md` | Business requirements this PRD implements | Source of truth for scope |
| REF-2 | Doc | `architecture.md` | Pipeline, stack, handoff contract | Technical grounding |
| REF-3 | Doc | `docs/growth/distribution-strategy.md` | Personas, channels, SEO gap audit (1-7) | On-page SEO gaps drive FR-032/033 |
| REF-4 | Code | `scripts/generate_content.py` | Weekly frontmatter generation | Confirms missing `topics` field (FR-002) |
| REF-5 | Config | `hugo.toml` | `topic` taxonomy, outputs (RSS/JSON), params | Confirms taxonomy + RSS already present |
| REF-6 | Layout | `layouts/topics/list.html` | Existing topic hub scaffold + RSS | Basis for topic hubs (FR-001) |
| REF-7 | Analysis | External SEO analysis (user-provided, 2026-07) | Discovery-first strategy | Primary driver |
| REF-8 | ADR | `docs/decisions/adr-star-velocity-explorer.md` | FR-052 selection and static-hosting rationale | Resolves Q-02 |
| REF-9 | Review | `docs/review/data-observatory-relaunch/README.md` | Bounded acceptance evidence and pending gates | Source of release status |
| REF-10 | Review | `docs/review/data-observatory-relaunch/status-of-record.md` | Reconciled delivered-versus-pending status and launch-gate register | Single readiness view |

### Citation Usage
Functional requirements cite BRD requirement IDs (BR-xxx) inline; technical claims cite the repository files above.

## 17. Appendices (Optional)
### Glossary
| Term | Definition |
|------|-----------|
| Topic hub | Evergreen taxonomy term page aggregating issues + dataset highlights for a technology theme |
| Data page | Generated ranking/"top N" page derived from `data/` artifacts |
| Repository page | Evergreen `/repo/<slug>` page with a repo's Claracle history |
| Evergreen page | A durable URL that accumulates authority over time (vs. time-indexed weekly page) |
| GSC / GA4 | Google Search Console / Google Analytics 4 |

### Additional Notes
The weekly crawl and analysis remain unchanged; this PRD only adds consumers and presentation layers over their output.

Generated 2026-07-29 by PRD Builder (mode: full)
<!-- markdown-table-prettify-ignore-end -->
