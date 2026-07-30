# Claracle Data Observatory model spike

Issue: [#595](https://github.com/jmservera/SquadScope/issues/595)  
Epic: [#594](https://github.com/jmservera/SquadScope/issues/594)  
Owner: Bender  
Status: design spike, no production code changes

## Scope and guardrails

This note defines a read-only data model for the Claracle Data Observatory relaunch.
It intentionally does **not** change the weekly crawl, analysis pipeline, Podcaster
handoff, or site generation code. The model consumes existing artifacts under
`data/` and is meant to unblock Wave 2 work on topic hubs, data pages, and
repository pages.

The product and business requirements are in:

- `docs/prds/claracle-data-observatory-relaunch.md`
- `docs/brds/claracle-data-observatory-relaunch-brd.md`

Both documents make the same constraint explicit: weekly crawl output is the
authoritative source of truth, the static Hugo/GitHub Pages architecture remains,
and `config/podcast.json` plus `scripts/podcaster_handoff.py` must not change for
this work.

## Existing data sources inspected

### Weekly raw crawl JSON

The crawl writes weekly JSON under `data/raw/`. Gaps from recovered publication
history are available under `data/archive/recovered-W23-W29/`.

Canonical weeks currently available for this spike:

| Week | Preferred path | `trending_repos` | `new_repos` | Total repo records |
| --- | --- | ---: | ---: | ---: |
| 2026-W21 | `data/raw/2026-W21.json` | 215 | 209 | 424 |
| 2026-W22 | `data/raw/2026-W22.json` | 235 | 181 | 416 |
| 2026-W23 | `data/archive/recovered-W23-W29/2026-W23/2026-W23.json` | 238 | 196 | 434 |
| 2026-W24 | `data/archive/recovered-W23-W29/2026-W24/2026-W24.json` | 234 | 156 | 390 |
| 2026-W25 | `data/archive/recovered-W23-W29/2026-W25/2026-W25.json` | 235 | 171 | 406 |
| 2026-W26 | `data/archive/recovered-W23-W29/2026-W26/2026-W26.json` | 234 | 219 | 453 |
| 2026-W27 | `data/archive/recovered-W23-W29/2026-W27/2026-W27.json` | 232 | 241 | 473 |
| 2026-W28 | `data/archive/recovered-W23-W29/2026-W28/2026-W28.json` | 236 | 129 | 365 |
| 2026-W29 | `data/raw/2026-W29.json` | 236 | 214 | 450 |
| 2026-W30 | `data/raw/2026-W30.json` | 237 | 196 | 433 |
| 2026-W31 | `data/raw/2026-W31.json` | 240 | 118 | 358 |

Across those 11 weeks there are 4,602 repo records and 2,242 distinct repository
identities. The observed raw top-level keys are `week`, `crawled_at`,
`trending_repos`, `new_repos`, `signals`, and `metadata`.

Every sampled repository record in `trending_repos` and `new_repos` uses the same
field shape:

- `owner`
- `name`
- `full_name`
- `description`
- `language`
- `stars`
- `forks`
- `created_at`
- `topics`
- `license`
- `url`

Example evidence:

- `data/raw/2026-W21.json` has `freeCodeCamp/freeCodeCamp` with `owner`,
  `name`, `full_name`, `url`, `stars`, `forks`, `language`, `topics`,
  `description`, and `created_at`.
- `data/raw/2026-W21.json` has `Nightmare-Eclipse/YellowKey` in `new_repos`
  with the same field names.

### Snapshots

`data/snapshots/2026-W21-stars.json` exists with:

- `week`
- `captured_at`
- `repository_count`
- `stars`, a mapping of `owner/name` to star count

The snapshot file is currently only a small two-repository sample. The raw weekly
files are therefore the practical source for historical star series today. Future
snapshot expansion would make star velocity cheaper to compute, but Wave 2 should
not require new crawl calls.

### Analysis outputs

Weekly summaries live in `data/analyzed/` as
`data/analyzed/YYYY-WNN-summary.md`. Correlation files live beside them as
`data/analyzed/YYYY-WNN-correlations.json`.

Observed summary frontmatter includes fields such as:

- `title`
- `date`
- `week`
- `year`
- `tags`
- `categories`
- `repos_featured`
- `stars_tracked`
- `top_repo`
- `quality_score`
- `summary`
- `predictions`

`data/analyzed/2026-W31-summary.md`, for example, has `tags:
[ai-agents, agent-skills, developer-tools, local-first, security, simulation]`,
`repos_featured: 300`, `stars_tracked: 21800000`, and `top_repo:
"makecindy/cindy"`.

`data/analyzed/2026-W31-correlations.json` stores a `week` and a `correlations`
array. Correlation records include `repo`, `repo_key`, `press_correlated`,
`correlation_confidence`, `matched_articles`, `matched_article_details`,
`match_type`, `correlation_strength`, `confidence_label`, `temporal_spike`, and
`hype_risk`.

### Data path conventions

`scripts/topic_paths.py` defines the current artifact layout:

- `data/raw/`
- `data/analyzed/`
- `data/metrics/`
- `data/snapshots/`
- `data/cache/`

It also supports topic-aware subdirectories for future use, while preserving the
flat legacy layout when `topic_id` is omitted or `general`.

## Repository identity and metrics

Repository identity is stable enough for the Observatory's first read-only model
when it is read directly from raw crawl records and keyed by normalized
`full_name` (`owner/name` lowercased for comparison, original casing preserved
for display). The raw records consistently include `owner`, `name`,
`full_name`, and `url`; `scripts/correlate.py` and `scripts/analysis_gate.py`
already use `full_name` or an `owner/name` fallback for repository identity.
`scripts/preprocess_for_analysis.py` is different: it combines `new_repos` and
`trending_repos`, deduplicates on bare `name`, then emits compact prompt records
with `name`, `desc`, `stars`, `gained`, `topics`, `lang`, and `age_days`. It
does not retain `owner`, `full_name`, or `url`, so the Observatory repository
model should not derive canonical identity from the compact preprocessing
payload.

Star history is derivable across weeks by grouping raw records on `full_name` and
reading the weekly `stars` value. Examples from the inspected data:

| Repository | Weeks present | Stars observed |
| --- | ---: | --- |
| `anthropics/claude-code` | 11 | 124,518 in W21; 139,221 in W31 |
| `OpenHands/OpenHands` | 11 | 73,933 in W21; 82,210 in W31 |
| `Mintplex-Labs/anything-llm` | 11 | 60,204 in W21; 63,917 in W31 |
| `modelcontextprotocol/servers` | 7 | 85,839 in W21; 88,925 in W31 |
| `ollama/ollama` | 11 | 171,669 in W21; 176,953 in W31 |
| `n8n-io/n8n` | 11 | 188,473 in W21; 198,137 in W31 |

Important limitation: current raw repo records do **not** include a durable
`id`, `node_id`, `archived`, `disabled`, `updated_at`, `pushed_at`,
`stars_gained`, or rename marker. The existing analysis code has optional
references to `stars_gained`, but the inspected raw files only expose absolute
`stars`. Velocity must therefore be computed as a derived difference between
observed weekly star counts, not read as a first-class crawl field.

## Read-only dataset access shape

Wave 2 should introduce a small read-only helper module rather than spreading
ad-hoc JSON reads across templates or generators. Conceptually:

```python
class ObservatoryDataset:
    def weeks(self) -> list[WeekSnapshot]: ...
    def repositories(self) -> dict[str, RepositoryHistory]: ...
    def recurring_repositories(self, min_weeks: int = 4) -> list[RepositoryHistory]: ...
    def topic_mentions(self) -> dict[str, TopicHistory]: ...
    def summary_index(self) -> dict[str, WeeklyAnalysis]: ...
```

Suggested records:

```python
WeekSnapshot:
    week: str
    crawled_at: datetime
    source_path: Path
    trending_repos: list[RepoObservation]
    new_repos: list[RepoObservation]

RepoObservation:
    week: str
    source_bucket: Literal["trending_repos", "new_repos"]
    owner: str
    name: str
    full_name: str
    url: str
    description: str | None
    language: str | None
    stars: int | None
    forks: int | None
    created_at: datetime | None
    topics: list[str]
    license: object | str | None
    source_path: Path

RepositoryHistory:
    full_name: str
    display_name: str
    slug: str
    first_seen_week: str
    last_seen_week: str
    appearances: list[RepoObservation]
    distinct_weeks: set[str]
    star_series: list[tuple[str, int]]
    derived_star_deltas: list[tuple[str, int | None]]
    languages: Counter[str]
    raw_topics: Counter[str]
    related_repos: Counter[str]
```

The helper should be deterministic, read-only, and side-effect-free by default.
It should prefer `data/raw/YYYY-WNN.json` when present and fill historical gaps
from `data/archive/recovered-W23-W29/YYYY-WNN/YYYY-WNN.json`. When duplicate
weeks exist, the non-archive `data/raw/` file wins; the archive copy is retained
as provenance, not counted twice.

## Derived artifact locations

No derived artifacts are created by this spike. When Wave 2 adds generation, the
recommended locations are:

- Public Hugo pages:
  - topic hubs: existing Hugo `topic` taxonomy / `content/topics/`
  - data pages: `content/data/`
  - repository pages: `content/repo/<slug>/index.md` or equivalent Hugo bundle
- Downloadable datasets: `static/datasets/observatory/`
- Non-Hugo intermediate JSON generated from existing data:
  - `data/derived/observatory/repositories.json`
  - `data/derived/observatory/topics.json`
  - `data/derived/observatory/rankings.json`

The `data/derived/observatory/` layer should be generated from checked-in
`data/raw/`, `data/archive/`, `data/snapshots/`, and `data/analyzed/` artifacts.
It should not be a new source of truth and should be safe to regenerate.

## Repository slug scheme

Use the normalized raw `full_name` (`owner/name`) as the source identity key and
derive public page paths from that key. The slug is a routing artifact, not the
primary repository key: split `full_name` into `owner` and `name`, normalize each
component, then join them with a hyphen for the URL path.

Use:

```text
/repo/<owner>-<name>/
```

where `<owner>` and `<name>` are lowercased, Unicode-normalized, and restricted
to URL-safe `a-z`, `0-9`, and hyphen. Existing repository hyphens are preserved.
Any other separator or unsafe character becomes a single hyphen.

Examples:

- `anthropics/claude-code` -> `/repo/anthropics-claude-code/`
- `OpenHands/OpenHands` -> `/repo/openhands-openhands/`
- `modelcontextprotocol/servers` -> `/repo/modelcontextprotocol-servers/`
- `n8n-io/n8n` -> `/repo/n8n-io-n8n/`

The page frontmatter should retain canonical identity separately:

```yaml
repo_owner: "anthropics"
repo_name: "claude-code"
repo_full_name: "anthropics/claude-code"
repo_url: "https://github.com/anthropics/claude-code"
```

## Repository recurrence threshold

Default repository-page creation threshold:

```text
more than 3 distinct weekly issues
```

That is equivalent to at least 4 weekly appearances. The inspected 11-week raw
dataset currently has 263 repositories above this threshold. This is enough to
create useful pages while avoiding a thin page for every one-off crawl hit among
the 2,242 distinct repositories.

Repository pages should show:

- weekly appearances, with links back to weekly issues
- absolute star history from `stars`
- derived week-to-week star deltas where consecutive observations exist
- current known language and raw GitHub topics
- related repositories co-occurring in the same weekly summaries or same topic
  clusters
- provenance: `as_of_week`, `source_path`, and methodology link

## Canonical topics

Initial canonical topic list:

1. AI Coding Agents
2. MCP Ecosystem
3. Open-Source LLMs
4. Developer Tools
5. AI Agents in Healthcare

Evidence from current data:

- Raw GitHub topics across the canonical 11 weeks are led by `ai` (451
  appearances), `python` (391), `llm` (327), `typescript` (284), `javascript`
  (282), `ai-agents` (249), `claude-code` (211), `openai` (179), `mcp` (172),
  `claude` (172), `cli` (165), `open-source` (146), `chatgpt` (143), and
  `machine-learning` (141).
- Weekly summaries repeatedly frame agent skills, coding agents, local-first
  agent tooling, model routing, security, and developer tools:
  - W22: `coding-agents`, `developer-tooling`, `agent-skills`, `ai-memory`
  - W23: `self-hosted`, `agent-skills`, `ai-memory`, `coding-agents`
  - W24: `agent-skills`, `coding-agents`, `local-first`, `ai-security`
  - W26: `agent-frameworks`, `mcp`, `agent-skills`, `model-routing`
  - W29: `ai-agents`, `agent-skills`, `developer-tools`, `local-first`
  - W31: `ai-agents`, `agent-skills`, `developer-tools`, `local-first`,
    `simulation`
- `data/analyzed/2026-W31-summary.md` explicitly links agent work to operating
  surfaces, skills, local workbenches, governance, and NVIDIA medical physics
  simulation, supporting the healthcare/simulation vertical as an initial
  watchlist hub rather than a high-volume general topic.

Suggested topic matching starts with aliases rather than model-generated labels:

| Canonical topic | Seed aliases/signals |
| --- | --- |
| AI Coding Agents | `ai-agents`, `coding-agents`, `agent-skills`, `claude-code`, `openai`, `codex`, `autogpt`, `openhands` |
| MCP Ecosystem | `mcp`, `modelcontextprotocol`, `mcp-server`, `servers`, local agent control-plane language in summaries |
| Open-Source LLMs | `llm`, `open-source`, `ollama`, `transformers`, `huggingface`, `local-ai`, `model-routing` |
| Developer Tools | `developer-tools`, `cli`, `typescript`, `javascript`, `python`, `go`, `rust`, build/test/observability tools |
| AI Agents in Healthcare | `healthcare`, `medical`, `simulation`, `scientific`, `clinical`, healthcare/simulation press-context correlations |

## New-topic heuristic

Default new-topic creation heuristic:

```text
candidate appears in at least 4 weekly issues in the last 2 months
```

Implementation shape:

1. Normalize raw GitHub `topics`, summary `tags`, recurring heading language, and
   correlation labels into candidate tokens.
2. Map known aliases to existing canonical topics.
3. For unmapped candidates, count distinct weekly issues in an 8-week rolling
   window.
4. Require at least 4 distinct weeks plus at least one supporting signal:
   - recurring repo cluster above the repo threshold,
   - analysis-summary tag/heading usage, or
   - press correlation with `confidence_label` of `strong`.
5. Log the candidate topic and evidence before creating a hub.

This keeps the PRD/BRD default while reducing the chance that spam, exploit
churn, or a single press cycle creates a low-quality SEO page.

## Repository lifecycle data needed

Current raw data is sufficient for first-seen/last-seen history and star deltas
but not sufficient for robust lifecycle handling. To support renamed, archived,
and deleted repositories without re-crawling on demand, the dataset needs these
fields captured during the normal weekly crawl or retained from cached responses:

- stable GitHub repository `id` and `node_id`
- `full_name`, `owner.login`, and `name`
- `html_url`/`url`
- `archived`
- `disabled`
- `visibility` if available
- `pushed_at`
- `updated_at`
- `created_at`
- API status when a previously known repository is checked during the normal
  scheduled crawl (`200`, `301`/rename equivalent when available, `404`, `410`)
- `last_seen_week`
- `last_successful_url`
- `renamed_from` / `renamed_to` when inferred

Static-site behavior:

- Rename: generate the new page and add a redirect from the old slug where Hugo
  and GitHub Pages allow.
- Archive: keep the page and add an archived note with `as_of_week`.
- Delete/inaccessible: keep the page for at least three years, remove claims of
  current availability, and show "last seen" provenance.

## Build-cost estimate (Q-01)

Current content inventory has 29 Markdown files under `content/`. The inspected
data would create approximately:

- 5 initial topic hubs
- at least 3 data pages
- up to 263 repository pages at the `>3 weekly issues` threshold

That first Observatory wave is therefore roughly 271 additional content pages
before taxonomy, RSS, sitemap, and listing pages.

One local report-only observation was captured on 2026-07-30 from the current
worktree:

| Command | Pinned version | Duration | Scope |
| --- | --- | ---: | --- |
| `hugo --minify` | Hugo extended `v0.161.1` | 6,668 ms | 2,669 rendered pages |
| `npx pagefind@1.5.2 --site public/` | Pagefind `v1.5.2` | 6,207 ms | 1,477 HTML files scanned and 288 pages indexed; includes local `npx` startup and package resolution |

This observation proves that Hugo and Pagefind complete separately with the
pinned production versions. It is not an external CI baseline and is not enough
to calculate representative statistics. The production CI job now uploads one
machine-readable report per run with separate `duration_ms` values in
report-only mode.

The following acceptance evidence remains pending:

* Three comparable external CI timing reports
* Median and p95 calculated from those reports
* A proposed blocking regression budget based on the measured distribution
* Owner approval of that budget before enforcement

No blocking timing threshold is approved or enforced.

## Open risks for Wave 2

- `stars_gained` is referenced by existing analysis helpers but absent from the
  inspected raw schema. Wave 2 must compute velocity from absolute `stars` unless
  a future scheduled crawl records deltas.
- Lifecycle handling needs `id`/`node_id`, archive/delete fields, and rename
  provenance. The current raw schema does not contain them.
- Topic creation needs a quality gate because the raw crawl includes high-volume
  low-signal and abuse-adjacent repositories; analysis summaries already call out
  this noise floor.
- The pinned local build is healthy, but three comparable external CI runs and
  owner approval are still required before build timing can become blocking.
- Recovered archive data must not double-count duplicate weeks when a matching
  `data/raw/YYYY-WNN.json` exists.
