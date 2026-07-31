---
title: Claracle Data Observatory Relaunch Unit 4 Validation
description: RPI validation of FR-040 and FR-041 for weekly internal links and the CI broken-link gate
ms.date: 2026-07-29
ms.topic: review
---

## Validation status

Status: Partial

* FR-040: Partial. The implementation and all 11 source articles satisfy the
	applicability rules, and screenshots 09 and 10 demonstrate the expected W29
	output. A fresh rendered-corpus check could not run because Hugo is absent
	locally and the pinned binary download failed.
* FR-041: Passed. CI builds the rendered site and invokes the checker as a
	blocking step. The production checker returned exit code 1 for an
	intentionally missing internal target.

## Scope and source limitations

* Implementation plan: Missing
* Changes log: Missing
* Primary requirements: PRD and BRD
* Visual references: Screenshots 09 and 10
* Validation phase: Unit 4 (FR-040 and FR-041)
* Current corpus: 11 weekly articles, W21 through W31 of 2026

The missing implementation plan and changes log prevent planned-versus-claimed
change comparison. This validation reconstructs the through-line from
`docs/prds/claracle-data-observatory-relaunch.md:132-133` and
`docs/brds/claracle-data-observatory-relaunch-brd.md:201-209`, then verifies the
current implementation directly.

## Requirements traceability

| Requirement | Required behavior | Verified implementation | Status |
|-------------|-------------------|-------------------------|--------|
| FR-040 | Weekly articles contain applicable prior/next, topic-hub, and repository/technology links | `layouts/weekly/single.html:37` includes the footer. `layouts/partials/article-footer.html:11-36` emits related and chronological links. `layouts/partials/article-related-links.html:1-81` resolves topic aliases and only emits repository links when a generated page exists. | Partial |
| FR-041 | CI validates rendered internal links and fails for a broken target | `.github/workflows/ci.yml:1-8` runs on pushes and pull requests to `main`; `.github/workflows/ci.yml:53-106` builds and checks `public/`. `scripts/check_internal_links.py:48-144` resolves pages and fragments and reports missing targets. | Passed |

Screenshots `docs/review/data-observatory-relaunch/screenshots/09-weekly-article-internal-links.png`
and `docs/review/data-observatory-relaunch/screenshots/10-internal-linking-block.png`
show W29 with AI Coding Agents and Developer Tools hubs, W28/W30 navigation,
and no repository-page group. That matches W29 applicability: its tags map to
two hubs, while none of its 30 referenced GitHub repositories has a generated
repository page.

## Weekly article coverage

The topic registry at `data/taxonomy/topics.json:1-86` maps weekly tags to five
durable hubs. All current articles declare tags at line 5 of their respective
files. None declares `topics`, so the fallback from tags at
`layouts/partials/article-related-links.html:7-12` controls current behavior.

| Week | Applicable topic hubs | Applicable generated repository pages | Chronological links |
|------|-----------------------|---------------------------------------|---------------------|
| W21 | AI Coding Agents; MCP Ecosystem | 6: affaan-m/ECC, ruvnet/ruflo, n8n-io/n8n, upstash/context7, modelcontextprotocol/servers, anthropics/claude-code | Next W22; no prior endpoint |
| W22 | AI Coding Agents; Developer Tools; Open-Source LLMs | 3: obra/superpowers, anthropics/skills, MemPalace/mempalace | Prior W21; next W23 |
| W23 | AI Coding Agents | 1: pewdiepie-archdaemon/odysseus | Prior W22; next W24 |
| W24 | AI Coding Agents | None of 20 GitHub references has a generated page | Prior W23; next W25 |
| W25 | AI Coding Agents; Open-Source LLMs | 1: DietrichGebert/ponytail | Prior W24; next W26 |
| W26 | MCP Ecosystem; AI Coding Agents; Open-Source LLMs | 3: n8n-io/n8n, anomalyco/opencode, NousResearch/hermes-agent | Prior W25; next W27 |
| W27 | AI Coding Agents | 3: n8n-io/n8n, anomalyco/opencode, NousResearch/hermes-agent | Prior W26; next W28 |
| W28 | AI Coding Agents | None of 39 GitHub references has a generated page | Prior W27; next W29 |
| W29 | AI Coding Agents; Developer Tools | None of 30 GitHub references has a generated page | Prior W28; next W30 |
| W30 | AI Coding Agents; Open-Source LLMs | 3: mem0ai/mem0, thedotmack/claude-mem, Mintplex-Labs/anything-llm | Prior W29; next W31 |
| W31 | AI Coding Agents; Developer Tools; AI Agents in Healthcare | 3: obra/superpowers, affaan-m/ECC, thedotmack/claude-mem | Prior W30; no next endpoint |

Article evidence is in `content/weekly/2026/W21.md:5-64`,
`content/weekly/2026/W22.md:5-61`, `content/weekly/2026/W23.md:5-59`,
`content/weekly/2026/W24.md:5-59`, `content/weekly/2026/W25.md:5-61`,
`content/weekly/2026/W26.md:5-60`, `content/weekly/2026/W27.md:5-61`,
`content/weekly/2026/W28.md:5-61`, `content/weekly/2026/W29.md:5-65`,
`content/weekly/2026/W30.md:5-66`, and
`content/weekly/2026/W31.md:5-65`. The matrix applies the exact URL matching and
page-existence conditions from `layouts/partials/article-related-links.html:38-63`.

## Findings

### Critical

No critical findings.

### Major

1. Required weekly-link presence has no automated regression test. The only
	dedicated tests, `tests/test_internal_link_checker.py:10-59`, prove that
	emitted links and fragments resolve. They do not render weekly pages or
	assert the presence of prior/next, topic-hub, or applicable repository
	links. The CI checker collects only links that already exist
	(`scripts/check_internal_links.py:48-57`), so removing a required link group
	would still pass FR-041. This degrades maintainability of the Must-priority
	FR-040 behavior.

### Minor

1. The implementation plan and changes log are missing. Requirement-to-change
	attribution and completion-claim verification are therefore unavailable;
	this review validates the current tree only.

### Informational

1. Current articles omit explicit `topics` frontmatter, for example
	`content/weekly/2026/W29.md:1-12`. FR-040 still works because the related-link
	partial intentionally falls back to tags and resolves registry aliases at
	`layouts/partials/article-related-links.html:7-34`. This is not an FR-040
	failure.

## Coverage assessment

* FR-040 implementation coverage: 11 of 11 articles analyzed; 11 of 11 have
	applicable topic links; 7 of 11 have applicable generated repository links;
	9 of 11 require both chronological directions; W21 and W31 are legitimate
	endpoints.
* FR-040 rendered coverage: W29 verified by screenshots 09 and 10. The other 10
	pages were not freshly rendered in this session.
* FR-041 implementation coverage: workflow trigger, build order, checker
	invocation, URL resolution, page existence, and fragment existence verified.
* FR-041 executable coverage: 5 focused tests passed in 0.14 seconds. A
	disposable link to `/definitely-broken-rpi-validation/` produced the expected
	missing-target diagnostic and process exit code 1.

Overall coverage is high for implementation logic and complete for source
applicability. Status remains Partial because FR-040 acceptance explicitly
requires rendered weekly pages and only one current page has rendered visual
evidence in the supplied artifacts.

## Clarifying questions

None. The endpoint interpretation and “where applicable” behavior are resolved
by the acceptance criteria, current generated-page inventory, and screenshots.

## Recommended next validations

* Install or provide Hugo Extended 0.161.1 and render all 11 weekly pages with
	`hugo --minify`.
* Run `python scripts/check_internal_links.py public --base-url
	"https://claracle.com/"` against that complete render.
* Add a rendered weekly-footer regression test that asserts required topic,
	applicable repository, and prior/next links, including W21/W31 endpoints.
* Run the actual GitHub Actions `Internal links` job on a branch containing an
	intentional broken internal link, then confirm the required check blocks the
	pull request.
