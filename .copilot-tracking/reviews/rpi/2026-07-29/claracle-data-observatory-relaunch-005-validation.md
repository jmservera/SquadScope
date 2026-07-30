---
title: Claracle Data Observatory Relaunch Unit 5 Validation
description: RPI validation of PRD unit 5 covering FR-050 through FR-053 and FR-060
ms.date: 2026-07-29
ms.topic: reference
---

## Validation Scope

Status: Partial

This validation reconstructs PRD unit 5 traceability because no implementation plan or changes log was provided. Evidence is drawn from the PRD, BRD, screenshots 06 through 08, current implementation files, and tests.

The reconstructed checklist uses FR-050 through FR-053 and FR-060 from
`docs/prds/claracle-data-observatory-relaunch.md:131-135`, with the matching
business acceptance criteria in
`docs/brds/claracle-data-observatory-relaunch-brd.md:215-225`.

## Requirement Status

| Requirement | Status  | Acceptance assessment |
|-------------|---------|-----------------------|
| FR-050      | Passed  | A stable CSV path, MIT license, metadata, and source-complete citation note are published and linked from the State-of page. |
| FR-051      | Passed  | A shortcode-generated iframe snippet targets a standalone chart whose visible caption links to the Claracle source ranking. |
| FR-052      | Partial | The free tool runs from same-origin static JSON with no backend or external API, but the required tool-selection design-spike rationale is absent. |
| FR-053      | Passed  | The State of Open Source AI 2026 report is published and linked from the topics index, individual hubs, and topic layouts. |
| FR-060      | Passed  | The README contains the required purpose, screenshots, architecture, example outputs, and linked weekly-publication statement. |

### FR-050 Downloadable Dataset

The State-of page links the CSV at the stable path
`/datasets/open-source-ai-github-projects-2026/top-github-projects.csv`, plus
metadata, license, and citation files
(`content/state-of/open-source-ai-2026.md:11-17`). The exporter fixes the
dataset slug and output directory (`scripts/export_observatory_dataset.py:20-24`)
and generates all four published artifacts
(`scripts/export_observatory_dataset.py:342-352`).

The dataset carries an MIT grant in
`static/datasets/open-source-ai-github-projects-2026/LICENSE.txt:1-21`. The
citation note names GitHub as the original public source and enumerates all 11
checked-in source artifacts
(`static/datasets/open-source-ai-github-projects-2026/CITATION.md:1-31`). The
State-of page repeats the source list and links the public methodology
(`content/state-of/open-source-ai-2026.md:98-119`). Focused tests verify the
artifact set, MIT text, stable Claracle URL, GitHub citation, and hub backlinks
(`tests/test_export_observatory_dataset.py:12-72`).

### FR-051 Embeddable Chart

The public demo invokes a Hugo shortcode rather than raw content HTML and
provides a stable embed endpoint
(`content/charts/embeddable-rankings/index.md:13-14`). The chart partial creates
the iframe snippet from that endpoint
(`layouts/partials/visuals/observatory-chart.html:29-31`) and renders a visible
source backlink in the standalone frame
(`layouts/partials/visuals/observatory-chart.html:53-65`). Tests assert that the
content contains no raw iframe or script, and that rendered embed output contains
the Claracle ranking backlink, chart data, and iframe snippet
(`tests/test_observatory_embeds.py:13-69`). Screenshot 07 visually confirms the
copyable snippet and visible source attribution.

### FR-052 Client-Side Tool

The selected Star Velocity Explorer declares a same-origin static JSON source
(`content/tools/star-velocity-explorer/index.md:1-10`) and explicitly states that
it uses no backend, authenticated API, third-party script, or external data
service (`content/tools/star-velocity-explorer/index.md:14-21`). Its layout passes
that local path to the browser (`layouts/tools/single.html:21-26`), and the only
network operation in the tool script fetches that path with same-origin
credentials (`assets/js/star-velocity-explorer.js:126-132`). The data exporter
reads checked-in local artifacts and states that no live GitHub API calls are
made (`scripts/export_trend_explorer_data.py:108-160`). Tests cover deterministic
export, freshness, static rendering, malformed data, empty data, and unsafe URL
handling (`tests/test_trend_explorer_tool.py:13-109`). Screenshot 08 visually
confirms the interactive filters and rendered repository results.

The functional tool therefore passes the browser-only and no-external-API
portions, subject to the design-spike finding below.

### FR-053 State-of Page

The published report contains dated statistics, dataset interpretation,
methodology, citations, and exposure review
(`content/state-of/open-source-ai-2026.md:1-119`). The topics index links to it
(`content/topics/_index.md:8-10`), an individual relevant hub links to it
(`content/topics/open-source-llms/_index.md:19-21`), and the shared topic layout
adds the report link to every topic hub
(`layouts/topics/list.html:40-53`). Screenshot 06 visually confirms the rendered
State-of report and its dataset framing.

### FR-060 README Discovery

The README opens with the exact weekly-publication statement and linked Claracle
surfaces (`README.md:6-14`), explains project purpose and audience
(`README.md:16-29`), lists example outputs with live and repository links
(`README.md:31-41`), embeds four real screenshots (`README.md:43-53`), and provides
an architecture diagram plus pipeline explanation (`README.md:55-95`). All
acceptance elements are present.

## Findings

### Critical

None.

### Major

#### FR-052 has no required tool-selection design-spike rationale

FR-052 requires a design spike that compares candidate tools by discoverability
value, build effort, and static-hosting fit before recommending one
(`docs/prds/claracle-data-observatory-relaunch.md:133`). The PRD still records the
tool-selection question as open
(`docs/prds/claracle-data-observatory-relaunch.md:260-261`). The repository's only
Observatory document labeled as a design spike is scoped to the read-only data
model for Wave 2 topic, data, and repository pages
(`docs/design/data-observatory-model.md:1-14`); it does not compare tool options or
record why Star Velocity Explorer was selected. A repository-wide search found
no other design-spike artifact containing the required three-way evaluation.

Impact: the shipped tool's runtime architecture is compliant, but the selection
decision is not auditable against the acceptance criterion. Record the considered
alternatives, score or discuss the three required factors, and state the resulting
recommendation to close FR-052.

### Minor

None.

## Coverage Assessment

Four of five functional requirements fully pass. FR-052 passes its shipped-tool,
client-side-only, no-backend, and no-external-API behavior but misses one explicit
acceptance deliverable. Unit 5 is therefore substantially implemented but not
complete, with overall status **Partial**.

Focused validation completed with `12 passed`, `0 failed`, and `4 skipped` across
`tests/test_export_observatory_dataset.py`, `tests/test_observatory_embeds.py`,
`tests/test_trend_explorer_tool.py`, and `tests/test_topic_hubs.py`. The available
screenshots provide rendered evidence for the skipped Hugo-dependent paths.

Traceability confidence is lower than a normal RPI review because the
implementation plan and changes log are missing. This does not change the
implementation finding, but it prevents comparison against planned task-level
checklists and claimed changes.

## Clarifying Questions

* Does issue 605 or pull request 618 contain an external design-spike comparison
	that was intentionally not checked into the repository? If so, preserve that
	rationale in a repository document and link it from the implementation evidence.

## Recommended Next Validations

* Install Hugo and rerun the focused tests with all render-dependent cases enabled
* Run `hugo --minify` and the internal-link checker against the generated site
* Open the generated embed endpoint independently and confirm its backlink remains visible without parent-page JavaScript
* Inspect browser network traffic for Star Velocity Explorer and confirm the static JSON is the only tool data request
* Verify the production CSV, license, citation, embed, tool, State-of, and README links return successful responses after deployment
