<!-- markdownlint-disable-file -->
# Research: Claracle Data Observatory Relaunch Remediation

## Scope

Plan the missing implementation and acceptance work identified by the 2026-07-29 relaunch review and six RPI validation units.

## Sources

* User request: "plan missing tasks"
* `.copilot-tracking/reviews/2026-07-29/claracle-data-observatory-relaunch-review.md`
* `.copilot-tracking/reviews/rpi/2026-07-29/claracle-data-observatory-relaunch-001-validation.md` through `claracle-data-observatory-relaunch-006-validation.md`
* `.copilot-tracking/research/subagents/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md`
* `docs/prds/claracle-data-observatory-relaunch.md`
* `docs/brds/claracle-data-observatory-relaunch-brd.md`
* `architecture.md`
* `.github/copilot-instructions.md`

## Verified Findings

* Existing generator code can emit canonical weekly topics, but all 11 committed weekly issues lack `topics` frontmatter. A body-preserving deterministic backfill is required.
* Unknown topic candidates cannot enter the current lifecycle because the registry only counts already-canonical topics. Candidate discovery needs a separate evidence artifact built from existing weekly crawl and analysis signals.
* The guarded weekly `publish` transaction is the correct authority for all weekly-derived outputs. It must hydrate previous generated state, run generators in dependency order, and publish all generated paths atomically.
* Repository history is keyed by mutable names and regeneration deletes prior pages. Stable GitHub identity plus a persisted lifecycle ledger is required to enforce rename, archive, deletion, and three-year retention behavior.
* Topic highlights can update at render time from recent matching weekly pages. Raw GitHub topics remain tags; only aliases of promoted editorial topics become repository-to-hub links.
* The active SEO controller is `layouts/partials/seo.html`. Topic, data, and repository surfaces need page-appropriate Schema.org entities, and every social image path needs dimensions.
* Existing rendered checks do not cover canonical correctness, complete social tags, schema contracts, all feeds, or required weekly-link presence.
* Custom analytics events must share the existing consent gate and must not send query text or repository names.
* Dynamic topic creation and repository page creation must default off until separate validation gates pass. Disabling either flag must not delete durable pages.
* Lighthouse, axe, responsive, and build timing evidence needs the new Observatory page classes. A numeric timing gate can only be approved after measured baseline runs.
* The Podcaster smoke must use the exact promoted release payload through a reusable workflow. The successful downstream run remains external evidence.
* FR-050, FR-051, FR-053, FR-060, and the Star Velocity Explorer runtime are already implemented. Preserve them and record the missing tool selection decision.

## Selected Implementation Path

Use the existing weekly guarded publication transaction as the single writer for topic, repository, ranking, dataset, and trend-explorer artifacts. Introduce durable topic-candidate and repository-lifecycle state, then layer rendered contracts and acceptance automation over those stable outputs.

This path is preferred over independent scheduled writers because it avoids branch races, manual merge ambiguity, and partial publication. It also preserves the static Hugo architecture and existing Podcaster payload contract.

## Required Sequencing

1. Establish traceability, off-by-default rollout flags, and baseline evidence.
2. Repair weekly topic assignment and dynamic candidate promotion.
3. Add stable repository identity, lifecycle persistence, retention, and curated hub links.
4. Integrate all generators into the weekly publish and deploy hydration paths.
5. Implement SEO, rendered-link, analytics, browser quality, and Podcaster gates in parallel.
6. Add runbook, ADR, security review, external evidence, visual evidence, and status reconciliation.
7. Run full validation and enable rollout flags separately only after their gates pass.

## External Acceptance Boundaries

Repository implementation cannot itself verify GSC ownership, submit the production sitemap, prove GA4 Realtime receipt, run social debugger services, sign a Hermes review, approve timing budgets, or prove a downstream Podcaster endpoint accepted a release. The plan therefore includes explicit evidence checkpoints and prevents unsupported acceptance claims.

## Planning Decisions

* Backfill all 11 committed weekly issues, not only W31.
* Keep raw GitHub topics as tags and editorial topic aliases as hub links.
* Use `CollectionPage` for topic hubs, `Dataset` with `ItemList` for rankings, and `WebPage` with `SoftwareSourceCode` for repository pages.
* Keep analytics opt-in and bounded.
* Treat deletion as confirmed only by positive lifecycle evidence or a reviewed override; absence from weekly search is not deletion.
* Convert the monthly data-page workflow to a read-only freshness check after the weekly transaction owns publication.
* Keep the Star Velocity Explorer and document its selection rather than reopening implementation.

## Remaining Owner Decisions

* Approve Hugo and Pagefind blocking budgets after at least three representative CI timing runs.
* Choose whether bounded repository lifecycle metadata checks may be added later; the initial safe path uses captured crawl fields plus reviewed deletion overrides.
* Choose the steady-state Podcaster smoke frequency after relaunch acceptance.
* Assign the named operational owner for GA4/GSC review and escalation.
