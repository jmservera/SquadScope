---
title: Claracle Data Observatory Relaunch Unit 2 Validation
description: RPI validation of generated data pages and repository lifecycle requirements
author: GitHub Copilot
ms.date: 2026-07-29
ms.topic: reference
---

## Validation Scope

* Phase: PRD unit 2
* Requirements: FR-010, FR-011, FR-020, FR-021, and FR-022
* Status: Partial
* Plan source: `docs/prds/claracle-data-observatory-relaunch.md`
* Supplemental source: `docs/brds/claracle-data-observatory-relaunch-brd.md`
* Changes log: Missing; current implementation evidence is used instead
* Implementation plan: Missing; PRD and BRD requirements are used as the plan baseline
* Visual evidence: `docs/review/data-observatory-relaunch/screenshots/04-repo-ollama.png` and `docs/review/data-observatory-relaunch/screenshots/05-data-trend-page.png`

## Requirement Comparison

The validation result is **Partial**. FR-010 passes. FR-011 and FR-020 are
partially implemented. FR-021 and FR-022 do not meet operational acceptance.

The generated data-page freshness check passed with
`python3 scripts/generate_data_pages.py --check`. Focused pytest execution was
attempted twice, but an already-active terminal session interrupted pytest
before collection. Static test inspection is included as evidence, but those
tests are not reported as executed in this review.

### FR-010 Data Pages

Status: **Passed**

The requirement calls for at least three labeled, timestamped rankings from
real `data/` artifacts, each with a metric definition and methodology link
(`docs/prds/claracle-data-observatory-relaunch.md:118`,
`docs/brds/claracle-data-observatory-relaunch-brd.md:153-158`).

Verified evidence:

* Exactly three generated ranking pages exist under `content/data/`
* `content/data/top-ai-repositories-this-month/index.md` contains 100 ranking rows
* `content/data/fastest-growing-ai-repositories-this-year/index.md` contains 100 ranking rows
* `content/data/most-starred-mcp-projects/index.md` contains 72 ranking rows
* All three pages expose metric definition, `as_of`, `as_of_week`, methodology,
  source artifacts, and cadence at lines 10-15 of each generated file
* The generator reads checked-in raw and recovered artifacts at
  `scripts/generate_data_pages.py:18-19,117-122` and defines all three outputs at
  `scripts/generate_data_pages.py:382-443`
* The shared layout renders provenance and ranking data at
  `layouts/data/single.html:14-35,40-62`
* Screenshot 05 visibly shows the provenance panel and a 100-row ranking; the
  visual review identifies it as FR-010/011 evidence at
  `docs/review/data-observatory-relaunch/README.md:23,57`

### FR-011 Data Page Regeneration

Status: **Partial**

The requirement calls for scheduled regeneration that updates pages without
manual intervention (`docs/prds/claracle-data-observatory-relaunch.md:119`,
`docs/brds/claracle-data-observatory-relaunch-brd.md:155,159`).

Verified evidence:

* `.github/workflows/generate-data-pages.yml:4-7` schedules monthly execution
* `.github/workflows/generate-data-pages.yml:33-34` runs the generator
* `.github/workflows/generate-data-pages.yml:49-57` commits changes and opens a
  pull request
* Generated output is current according to the read-only `--check` execution

Gap: the workflow stops after opening a pull request. It does not merge or
publish the regenerated pages, so updating the site still requires manual
intervention. See finding RPI-002-002.

### FR-020 Repository Pages

Status: **Partial**

The requirement calls for stable `/repo/<slug>` pages with growth history,
star velocity, weekly appearances, related repositories, and internal links to
topic hubs and weekly issues (`docs/prds/claracle-data-observatory-relaunch.md:120`,
`docs/brds/claracle-data-observatory-relaunch-brd.md:165-171`).

Verified evidence:

* `content/repo/_index.md:1-9` records 263 generated pages and the threshold used
* `content/repo/ollama-ollama/index.md:49,83,131` contains star history, weekly
  appearances, and related repositories from 11 checked-in weekly artifacts
* `scripts/observatory_repos.py:404-421` emits all four required data elements,
  tag links, provenance, and the methodology link
* `layouts/repo/single.html:37-90` renders weekly links, growth and velocity,
  tag links, related repository links, and provenance
* `layouts/partials/seo.html:82-84` emits canonical and Open Graph URLs from the
  stable Hugo permalink
* All 11 weekly targets cited by the sample page exist under
  `content/weekly/2026/W21.md` through `content/weekly/2026/W31.md`
* Screenshot 04 visibly shows the sample page's appearances, growth history,
  tags, related repositories, and provenance; the visual review identifies it
  as FR-020/021/022 evidence at
  `docs/review/data-observatory-relaunch/README.md:22,54`

Gap: repository pages contain weekly-issue and related-repository links, but no
`/topics/` links. Raw GitHub topic values are intentionally emitted as `/tags/`
links by `scripts/observatory_repos.py:408-410` and rendered at
`layouts/repo/single.html:66-70`. See finding RPI-002-003.

### FR-021 Repository Page Creation Threshold

Status: **Failed**

The requirement calls for automatic page creation after more than three
distinct weekly appearances, with a threshold changeable without code edits
(`docs/prds/claracle-data-observatory-relaunch.md:121`,
`docs/brds/claracle-data-observatory-relaunch-brd.md:167,172`).

Verified evidence:

* `config/observatory.toml:1-6` configures `> 3` and three retention years
* `scripts/observatory_repos.py:145-153` loads configuration and derives four as
  the minimum eligible week count
* `scripts/observatory_repos.py:281-289` applies the threshold during generation
* `tests/test_observatory_repos.py:53-91` defines a focused threshold test

Gap: no tracked workflow invokes `scripts/observatory_repos.py`. The only unit 2
generator invocation found under `.github/workflows/` is the data-page command
at `.github/workflows/generate-data-pages.yml:34`. Threshold crossing therefore
does not automatically create or refresh a repository page. See finding
RPI-002-004.

### FR-022 Repository Lifecycle Handling

Status: **Failed**

The requirement calls for upstream rename redirects, archive and delete notes,
and enforcement of at least three years of deleted-page retention with
historical data and a last-seen date
(`docs/prds/claracle-data-observatory-relaunch.md:122`,
`docs/brds/claracle-data-observatory-relaunch-brd.md:173`).

Verified evidence:

* `scripts/observatory_repos.py:253-278,473-482` can merge a configured rename
  and emit a Hugo alias
* `scripts/observatory_repos.py:367-373,436-448` can render configured archive
  and delete notes with a calculated retention date
* `tests/test_observatory_repos.py:166-220` defines synthetic rename, archive,
  delete, alias, and retention-date assertions

Gaps:

* `config/observatory.toml:8-11` states that current raw data lacks stable GitHub
  identity, archive flags, and deletion status; the lifecycle override section
  is empty
* No lifecycle field was found in current raw or recovered artifacts
* None of the 263 generated repository pages has archived, deleted, or renamed
  status, and none has an alias
* `scripts/observatory_repos.py:465-470` deletes every generated repo
  directory before writing only currently eligible histories
* `retained_until` is descriptive metadata. No code preserves a prior deleted
  page until that date if its source history is no longer loaded

See finding RPI-002-001.

## Findings

### Critical

#### RPI-002-001 Lifecycle changes and retention are not operational

FR-022 is represented by rendering logic and a synthetic unit test, but the
live input path cannot detect rename or deletion and is documented as lacking
archive state. The checked-in lifecycle configuration contains no overrides,
and current generated output demonstrates none of the required states.

The unconditional cleanup at `scripts/observatory_repos.py:465-470` also makes
three-year retention dependent on old source artifacts remaining discoverable.
The calculated date at `scripts/observatory_repos.py:369-373` does not enforce
retention. A deleted page can disappear on regeneration if its history falls
out of the loader, contrary to FR-022.

Required correction: introduce durable repository identity and lifecycle state
from an automated metadata source, persist tombstones and rename mappings, and
make cleanup preserve deleted pages until `retained_until`. Exercise those
states through the actual scheduled generation path.

### Major

#### RPI-002-002 Monthly regeneration does not publish without intervention

The scheduled workflow generates and commits data pages, then opens a pull
request at `.github/workflows/generate-data-pages.yml:49-57`. It does not update
the published branch. This falls short of the explicit no-manual-intervention
acceptance in `docs/brds/claracle-data-observatory-relaunch-brd.md:159`.

Required correction: define an approved automated merge or direct publication
path with the existing quality gates, or revise acceptance to state that
scheduled PR creation is the intended control point.

#### RPI-002-003 Repository pages omit required topic-hub links

FR-020 requires links to hubs and issues. Weekly issue links exist, but the
generator emits raw GitHub topics only as `/tags/` links at
`scripts/observatory_repos.py:408-410`. No `/topics/` link exists in any checked-in
repository page.

Required correction: derive curated topic associations for repository
histories and emit resolvable `/topics/<slug>/` links alongside raw GitHub tags.

#### RPI-002-004 Repository generation is not cadence-integrated

The threshold is correctly configurable and applied by the generator, but no
tracked workflow or pipeline invokes that generator. New qualifying
repositories therefore require a manual command and commit, which fails the
automatic-creation behavior in FR-021.

Required correction: invoke `scripts/observatory_repos.py` after new weekly
artifacts land, include generated repository and derived data changes in the
controlled publication path, and add a stale-output check in CI.

### Minor

No Minor findings.

## Coverage Assessment

Requirement coverage is one Passed, two Partial, and two Failed.

* FR-010: Passed
* FR-011: Partial
* FR-020: Partial
* FR-021: Failed
* FR-022: Failed

The implementation has strong generated data quantity and provenance. It also
has complete repository field rendering and useful synthetic tests. Coverage
drops at operational boundaries: publication automation, repository generator
integration, curated topic links, lifecycle signal acquisition, and retention
enforcement.

## Recommended Next Validations

* [ ] Run `pytest -q tests/test_generate_data_pages.py tests/test_observatory_repos.py` in a clean terminal or CI worker
* [ ] Run `hugo --minify` and the internal link checker against the resulting site
* [ ] Trigger the monthly workflow in a test branch and verify whether policy can publish its pull request without human action
* [ ] Add and execute an end-to-end workflow fixture where a repository crosses the recurrence threshold
* [ ] Add and execute lifecycle fixtures through the real artifact ingestion path for rename, archive, and delete
* [ ] Prove that a deleted page survives regeneration after its observations are removed while its three-year retention period remains active
* [ ] Verify rendered repository pages link to curated topic hubs after the mapping gap is corrected

## Clarifying Questions

* Is scheduled pull-request creation intentionally considered sufficient for
  "without manual intervention," or must regeneration reach the published
  branch automatically?
* Is an external, untracked workflow responsible for invoking
  `scripts/observatory_repos.py` after weekly artifacts land?
* Are weekly raw and recovered artifacts governed by a documented retention
  policy of at least three years? If so, where is that policy enforced?