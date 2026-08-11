---
title: Claracle Data Observatory Runbook
description: Operating, recovery, rollback, ownership, and escalation procedures for generated Observatory content and lifecycle state
author: SquadScope Squad
ms.date: 2026-07-30
ms.topic: how-to
keywords:
  - data observatory
  - operations
  - recovery
  - lifecycle
estimated_reading_time: 12
---

## Operating boundary

The Observatory derives static Hugo pages and public datasets from checked-in weekly
artifacts. It does not recrawl GitHub during generation. Generated pages remain reviewable
repository changes, and publication still uses the existing Hugo deployment workflow.

Two creation controls are intentionally disabled in `config/observatory.toml`:

- `topic_hubs.dynamic_creation.enabled = false`
- `repo_pages.enabled = false`

Do not enable either control as part of routine recovery. Each requires a separate approved
rollout change after its acceptance evidence is complete.

### Repository URL retirement authority

SEC-04 governs lifecycle deletion when crawl evidence indicates that a GitHub repository was
deleted or became inaccessible. BR-003 repository URL retirement is a separate publication-scope
decision: it removes a redundant Claracle page while preserving the checked-in crawl history and
does not assert that the upstream GitHub repository was deleted.

A BR-003 retirement may bypass SEC-04's `deletion_confirmed_at` retention clock only when every URL
is present in the immutable sponsor-approved map, the source checksum matches that map, the
approved-map generator and migration validator pass, and the rollback manifest identifies the
exact pre-migration commit. This authority cannot be inferred from a recommendation or pending
candidate and does not change the SEC-04 behavior in `scripts/observatory_repos.py`.

## Ownership and escalation

| Surface                                                                | Primary owner                    | Review or escalation owner |
| ---------------------------------------------------------------------- | -------------------------------- | -------------------------- |
| Weekly analysis and canonical topic assignment                         | Farnsworth                       | Leela                      |
| Candidate discovery, repository histories, and generated datasets      | Bender                           | Leela                      |
| Hugo layouts, browser tools, embeds, and visual behavior               | Amy                              | Fry                        |
| Tests, deterministic output, links, and acceptance gates               | Fry                              | Leela                      |
| Workflows, deployment, and guardrail failures                          | URL                              | Leela                      |
| Sanitization, privacy, dataset exposure, and lifecycle deletion review | Hermes                           | Leela and jmservera        |
| Production analytics, Search Console, and rollout approval             | jmservera                        | Leela                      |
| Podcaster handoff contract                                             | SquadScope-Podcaster maintainers | URL and Hermes             |

Stop publication and escalate to Leela when generated output cannot be reproduced, a durable
page would be removed without confirmed lifecycle evidence, or a contract test fails. Escalate
secret exposure, unsafe rendering, candidate-title abuse, or unexpected analytics requests to
Hermes and URL. Escalate production, GA4, GSC, DNS, or sponsor approval blockers to jmservera.

## Inputs and durable outputs

| Input or state                                          | Purpose                                                        |
| ------------------------------------------------------- | -------------------------------------------------------------- |
| `content/weekly/`                                       | Published weekly membership and topic frontmatter              |
| `data/raw/` and `data/analyzed/`                        | Checked-in repository and analysis evidence                    |
| `config/observatory.toml`                               | Creation thresholds, flags, retention, and lifecycle overrides |
| `data/taxonomy/`                                        | Canonical topic and tag registries                             |
| `data/topic-candidates.json`                            | Byte-stable candidate evidence and eligibility                 |
| `data/topic-hubs/dynamic-topic-creation.log`            | Append-only dynamic hub creation records                       |
| `data/derived/observatory/`                             | Repository and browser-tool datasets                           |
| `data/derived/observatory/repository-lifecycle.json`    | Persisted identity and lifecycle ledger                        |
| `content/topics/`, `content/repo/`, and `content/data/` | Static Hugo content generated from repository evidence         |

Treat the lifecycle ledger, generated content, and taxonomy registries as one transaction. Review
their diff together. Never infer deletion from absence in a crawl or a quiet week.

## Generation order

Run generation from the repository root in this order. Keep both rollout flags at their current
values unless a separately approved rollout explicitly changes them.

1. Generate or refresh weekly content through the existing pipeline.
2. Backfill canonical topics when historical weekly membership needs reconciliation.
3. Refresh taxonomy registries.
4. Discover dynamic topic candidates from weekly, analyzed, and raw evidence.
5. Review candidates, then run topic promotion only under an approved dynamic-topic rollout.
6. Generate data pages and public dataset exports.
7. Generate repository pages only under an approved repository-page rollout.
8. Build Hugo, generate Pagefind output, and run internal-link and relevant test gates.

Representative repository commands are:

```bash
python scripts/backfill_weekly_topics.py
python scripts/taxonomy_registry.py
python scripts/discover_topic_candidates.py
python scripts/generate_data_pages.py
python scripts/export_observatory_dataset.py
python scripts/observatory_repos.py
hugo --minify
npx "pagefind@1.5.2" --site public/
python scripts/check_internal_links.py public --base-url "https://claracle.com/"
```

Before relying on an unfamiliar command, run it with `--help`. Script interfaces are the source
of truth when they differ from this runbook.

## Flags and lifecycle overrides

The topic threshold is at least four distinct weekly issues in a 62-day lookback. The repository
threshold is more than three distinct weekly issues, equivalent to four observed weeks. Thresholds
are configuration, not permission to publish: the associated `enabled` value is the release gate.

Repository lifecycle overrides live under `[repo_pages.lifecycle]` in
`config/observatory.toml`. Add an override only from reviewed upstream evidence. Record the
canonical repository identity, status, effective date, and rename target or deletion confirmation
required by the generator contract. A missing repository in fresh input is not evidence.

Deletion handling follows these rules:

* A confirmed deletion becomes a retained historical page with a tombstone and last-seen data
* Every `status = "deleted"` override requires a valid, non-future `deletion_confirmed_at`
* `deletion_confirmed_at` starts the configured retention period; `last_seen_week` is provenance only
* An operator-supplied `retained_until` cannot shorten the configured retention period
* `retained_until` is derived from the confirmation date and persisted in the lifecycle ledger
* Removal occurs only when the generation `--as-of` date is later than `retained_until`
* `--as-of` is for deterministic lifecycle checks and reviewed expiry execution, not for shortening retention

Seed durable lifecycle history before repository-page rollout with:

```bash
python scripts/observatory_repos.py --seed-lifecycle
```

Keep production `repo_pages.enabled = false` during this operation. The seed loads checked-in
observations and prior ledger state, then compares every qualified repository name and slug with
the generated pages and `data/derived/observatory/repositories.json`. Any mismatch stops before a
write and requires review. A successful seed atomically replaces only
`data/derived/observatory/repository-lifecycle.json`; it does not query GitHub, generate pages,
refresh taxonomy, or rewrite derived repository data. Run the command twice and confirm that the
second run leaves the ledger byte-identical.

If a seed is interrupted before replacement, rerun it against the same reviewed revision. If
parity fails, restore the page, derived data, raw observations, configuration, and prior ledger
from one reviewed revision before retrying. Do not bypass parity checks or invent stable IDs.

Rename handling preserves prior slugs as aliases where the static content model permits. Archive
handling adds status evidence without deleting history. Quiet topics and repositories remain
durable.

## Freshness and acceptance checks

Before publication, verify all of the following:

* Source weeks and generated `as_of` values match the intended reporting window
* A second generation pass is byte-stable
* Candidate evidence cites repository paths and observed weeks
* Topic hubs show real weekly membership rather than placeholder text
- Generated repository pages meet the recurrence threshold or carry reviewed retained lifecycle state
- The lifecycle ledger contains no unexplained identity, status, or retention change
- No disabled rollout flag changed
- Hugo, Pagefind, internal links, targeted tests, and Markdown validation pass
- Podcaster handoff tests pass when weekly publication or its workflow changed

Use `python scripts/observatory_repos.py --check` only when repository-page generation is enabled.
With the flag disabled, the script intentionally reports a no-op and does not delete durable pages.

## Routine dashboards and evidence

GitHub Actions is the operational dashboard for build, deploy, link, security, and Podcaster smoke
results. GA4 and GSC are external discovery dashboards, not proof of repository correctness. Record
dated links and observed values in the relaunch evidence index; never replace network, schema,
lifecycle, or metadata evidence with a screenshot.

Review these signals after an approved production deployment:

- Deployment and reusable Podcaster smoke conclusions
- Production sitemap and feed response status
- GA4 consent-denied network behavior and consent-granted Realtime receipt
- GSC property verification, sitemap submission, and processing state
- Rich Results, Schema.org, and social-preview debugger results
- Accessibility findings and visual acceptance captures

## Cross-origin embed privacy

Claracle's consent controls govern scripts, cookies, and telemetry on the Claracle origin. They
cannot inherit or inspect consent collected by an embedding site. Use the generated official
snippet unchanged: it includes `referrerpolicy="no-referrer"`. Publishers can alter copied iframe
attributes, so production review must inspect the markup actually deployed by the publisher.

The iframe starts Claracle analytics disabled. Only an explicit analytics choice in the Claracle
consent UI inside that frame can enable telemetry; parent-page consent is not inferred or
transferred. Third-party storage blocking may prevent the choice from persisting and cause another
prompt, but it must never enable analytics.

Before publication, test the fresh, denied, granted, reloaded, and withdrawn frame-local consent
states while capturing iframe requests and storage behavior. Confirm the deployed iframe retains
`no-referrer`. If an embed sends requests before Claracle consent, continues after withdrawal, or
cannot be inspected reliably, remove or disable the embed, stop publication of the affected page,
preserve the request evidence and deployed revision, and escalate to Hermes and URL. Repository
tests establish the implementation contract; Hermes approval and production evidence remain
pending.

## Failed-run recovery

1. Stop before deployment and preserve the failing command output.
2. Identify the first stale or malformed generated artifact rather than editing generated output by hand.
3. Confirm that input weeks, registries, configuration, and the lifecycle ledger belong to the same revision.
4. Restore any required missing input through its owning pipeline step.
5. Rerun from the earliest affected generation stage in the documented order.
6. Run the same focused failing check, then the full relevant build and link gates.
7. Review generated additions, modifications, aliases, and removals before publication.

For candidate-title abuse or malformed source text, quarantine the source evidence and involve
Hermes. Do not promote the candidate or weaken sanitization. For an interrupted lifecycle write,
regenerate the content and ledger from the last reviewed repository state; do not invent dates.

## Rollback

Rollback creation by reverting the approved generated-content transaction and its configuration
change. Do not delete previously durable pages as part of a flag rollback. Setting a creation flag
to `false` stops new creation; it is not a bulk deletion mechanism.

For a bad topic promotion, restore the prior taxonomy registry, weekly topic assignments, generated
hub content, and creation log state from the same reviewed revision. For a bad repository lifecycle
change, restore the prior override, lifecycle ledger, aliases, derived dataset, and generated page
together. Rebuild and rerun links after either rollback.

Production rollback uses the Cloudflare Pages procedure in
`docs/deployment/cloudflare-pages.md`. Preserve the failed run URL and the corrective deployment
URL in acceptance evidence. If rollback would alter
`config/podcast.json` or `scripts/podcaster_handoff.py`, stop and coordinate with the
SquadScope-Podcaster repository first.

## Incident closure

Close an incident only after the original failing check passes, generated output is reproducible,
durable pages are accounted for, and the owner records the recovery evidence. Security and privacy
incidents require Hermes disposition. Production rollout incidents require jmservera approval.
