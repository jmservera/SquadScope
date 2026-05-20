# Weekly Analysis Specification

This document defines the analyzer contract between `data/raw/YYYY-WNN.json` and `data/analyzed/YYYY-WNN-summary.md`.

## Purpose

The analyzer turns a weekly GitHub crawl into a structured editorial summary that is:

- consistent enough for CI automation,
- opinionated enough to be worth reading,
- strict enough for downstream site generation, and
- traceable enough for reviewer-gate validation.

The analyzer is a read-only consumer of `data/raw/`. It may interpret, rank, and summarize the crawl, but it must not rewrite the input artifact.

## Editorial Lens

SquadScope analysis uses a three-part editorial lens:

- **Signal** — projects or shifts that matter because they solve real problems, represent credible technical movement, or reveal durable ecosystem direction.
- **Noise** — activity that is loud but weak: marketing-heavy launches, copycat agents, exploit/bypass churn, or trend-chasing with little substance.
- **Gaps** — meaningful absences: categories, problem spaces, or technical needs that should be showing more energy but are not.

The reader-facing markdown keeps the five approved weekly sections, but the analysis itself must explicitly surface **Signal**, **Noise**, and **Gaps** as labeled subsections.

## Input Contract

### File naming

- **Location:** `data/raw/`
- **Filename:** `YYYY-WNN.json`
- **Example:** `data/raw/2026-W21.json`

### Analyzer read scope

The analyzer reads these fields:

- `week`
- `crawled_at`
- `new_repos[]`
- `trending_repos[]`
- `signals.top_topics[]`
- `metadata.partial_failures` *(optional diagnostic input; emitted by `scripts/crawl.py` today, but analyzers must tolerate absence)*
- `metadata.filter_summary` *(optional diagnostic input; emitted by `scripts/crawl.py` today, but analyzers must tolerate absence)*
- `metadata.snapshot_path` *(optional diagnostic input; emitted by `scripts/crawl.py` today, but analyzers must tolerate absence)*

Unknown fields must be ignored. The current crawler emits these diagnostic metadata fields in its own artifacts, but analyzers must not fail when they are missing from backfilled or forward-compatible payloads.

### JSON schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SquadScope Weekly Crawl Payload",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "week",
    "crawled_at",
    "new_repos",
    "trending_repos",
    "signals",
    "metadata"
  ],
  "properties": {
    "week": {
      "type": "string",
      "pattern": "^[0-9]{4}-W[0-9]{2}$"
    },
    "crawled_at": {
      "type": "string",
      "format": "date-time"
    },
    "new_repos": {
      "type": "array",
      "items": { "$ref": "#/$defs/repo" }
    },
    "trending_repos": {
      "type": "array",
      "items": { "$ref": "#/$defs/trendingRepo" }
    },
    "signals": {
      "type": "object",
      "additionalProperties": true,
      "required": ["top_topics"],
      "properties": {
        "top_topics": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["topic", "count"],
            "properties": {
              "topic": { "type": "string" },
              "count": { "type": "integer", "minimum": 0 }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "additionalProperties": true,
      "properties": {
        "api_calls_used": { "type": "integer", "minimum": 0 },
        "cache_hits": { "type": "integer", "minimum": 0 },
        "stale_cache_hits": { "type": "integer", "minimum": 0 },
        "rate_limit_limit": { "type": ["integer", "null"], "minimum": 0 },
        "rate_limit_remaining": { "type": ["integer", "null"], "minimum": 0 },
        "rate_limit_reset": { "type": ["integer", "null"], "minimum": 0 },
        "rate_limit_resource": { "type": ["string", "null"] },
        "partial_failures": {
          "type": "array",
          "items": { "type": "string" }
        },
        "snapshot_path": { "type": "string" },
        "filter_summary": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "additionalProperties": { "type": "integer", "minimum": 0 }
          }
        }
      }
    }
  },
  "$defs": {
    "repo": {
      "type": "object",
      "additionalProperties": true,
      "required": [
        "name",
        "owner",
        "full_name",
        "description",
        "language",
        "stars",
        "forks",
        "created_at",
        "topics",
        "license",
        "url"
      ],
      "properties": {
        "name": { "type": "string" },
        "owner": { "type": "string" },
        "full_name": { "type": "string" },
        "description": { "type": ["string", "null"] },
        "language": { "type": ["string", "null"] },
        "stars": { "type": "integer", "minimum": 0 },
        "forks": { "type": "integer", "minimum": 0 },
        "created_at": { "type": "string", "format": "date-time" },
        "topics": {
          "type": "array",
          "items": { "type": "string" }
        },
        "license": { "type": ["string", "null"] },
        "url": { "type": "string", "format": "uri" }
      }
    },
    "trendingRepo": {
      "allOf": [
        { "$ref": "#/$defs/repo" },
        {
          "type": "object",
          "properties": {
            "stars_gained": { "type": ["integer", "null"], "minimum": 0 }
          }
        }
      ]
    }
  }
}
```

### Input interpretation rules

1. **New repos** are candidates for editorial novelty.
2. **Trending repos** are candidates for momentum, but if `stars_gained` is absent or null, the analyzer must say that momentum is not yet fully measurable.
3. **Top topics** are directional evidence, not conclusions by themselves.
4. **Metadata diagnostics** can justify caveats about crawl quality, filtering, or missing baselines, but must not dominate the summary.

## Output Contract

### File naming

- **Location:** `data/analyzed/`
- **Filename:** `YYYY-WNN-summary.md`
- **Example:** `data/analyzed/2026-W21-summary.md`

### Required frontmatter

The analyzer output must begin with YAML frontmatter containing these fields.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `title` | string | yes | Reader-facing weekly title. Format: `Week NN, YYYY Analysis`. |
| `date` | string | yes | Analysis run timestamp in ISO 8601. |
| `week` | string | yes | Week slug from the raw payload (`YYYY-WNN`). |
| `year` | integer | yes | Numeric year for downstream validation and archive logic. |
| `tags` | array[string] | yes | 3-8 topical tags summarizing the week. |
| `categories` | array[string] | yes | Must include `weekly`. |
| `repos_featured` | integer | yes | Total repos considered in the editorial pass. Typically `len(new_repos) + len(trending_repos)`. |
| `stars_tracked` | integer | yes | Sum of `stars` across all repos considered. |
| `top_repo` | string | yes | The repo that anchors the week’s narrative, not necessarily the highest-star repo. |
| `quality_score` | integer | yes | Reviewer-gate score from 0-100. Must be `>= 60` to publish. |
| `summary` | string | yes | One-sentence editorial thesis for the week. |

No extra frontmatter keys should be emitted unless a later decision extends this contract.

### Required body structure

The body must follow this exact top-level section order:

```md
## This Week's Trends

## Where Industry Meets Code

## Signal & Noise

## Blind Spots

## The Week Ahead

## Key References
### Notable Projects
### Press & Industry
```

Every repository mentioned in the body must be rendered as a clickable markdown link in this exact format: `[owner/repo](https://github.com/owner/repo)`.

### Image accessibility guidance

If an analysis ever includes an image, chart, or screenshot:

- provide concise, descriptive alt text that explains the information a reader would otherwise miss,
- do not use placeholder alt text like `image`, `screenshot`, or the file name,
- keep decorative images rare; only use empty alt text when the image adds no editorial meaning,
- explain any important numbers or trends in the surrounding prose so the page still works without the image.

### Section guidance

#### 1. This Week's Trends
- **Purpose:** Name and explain the week's 3-5 macro trends — the big themes that cut across individual repos.
- **Include:** A clear name for each trend, what is driving it, and its significance to practitioners. Reference specific repos as evidence.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Tone:** Analytical and opinionated — write like a Gartner analyst, not a GitHub trending page.
- **Length:** ~200-350 words.
- **Avoid:** Listing repos without synthesis. Every repo reference must support a named trend.

#### 2. Where Industry Meets Code
- **Purpose:** Compare press coverage against what developers are actually building.
- **Include:** 2-4 correlations (where press and dev activity align) and 2-3 divergences (media-covered topics with no dev traction, and developer movements the press is ignoring). If no press data was available, state that explicitly.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Tone:** Editorial and skeptical — the interesting story is usually in the gap.
- **Length:** ~150-250 words.
- **Avoid:** Summarizing press articles without connecting them to developer evidence.

#### 3. Signal & Noise
- **Purpose:** Deliver integrated editorial judgment on what is real versus hype.
- **Required:** Write as coherent prose — do **not** use `### Signal` and `### Noise` sub-headings. The distinction should emerge from the writing itself.
- **Include:** Durable, technically credible patterns (signal) and inflated, copycat, or marketing-driven patterns (noise). Name specific repos and patterns in both categories.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Length:** ~150-260 words.
- **Avoid:** Repeating trend descriptions from section 1 without adding critical judgment.

#### 4. Blind Spots
- **Purpose:** Surface what is absent from both press coverage and developer activity.
- **Include:** 2-4 specific, concrete blind spots — name the missing category, why it matters, and what its absence signals.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Length:** ~80-160 words.
- **Avoid:** Generic filler like "more innovation is needed" or restating known gaps without editorial insight.

#### 5. The Week Ahead
- **Purpose:** End with a forward-looking editorial close.
- **Include:** What trends are in motion that have not peaked yet? What should readers watch for next week? What does this week's activity suggest about where the ecosystem is heading?
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Length:** ~50-110 words.
- **Avoid:** Introducing brand-new evidence or restating section 1.

#### 6. Key References
- **Purpose:** Give readers the 5-10 most important repos and 3-5 most relevant press items in one scannable place.
- **Required subsections:** `### Notable Projects` and `### Press & Industry`.
- **Notable Projects:** 5-10 repos with one sentence of context each — why it matters, not just what it is. Every repo must be a link.
- **Press & Industry:** 3-5 articles or sources with markdown links. If no press data was available, write: "No press data was provided this week."
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.

## Analysis Dimensions

Every weekly analysis must apply these dimensions explicitly.

### Importance Assessment
Ask whether a repo or theme solves a real problem, reduces friction, opens a new workflow, or signals credible adoption. Prefer practical utility over novelty theater.

### Trend Detection
Look for repeated patterns across topics, repo types, and—when available—previous weekly summaries. A single loud repo is not a trend; clustered movement is.

### Hype Detection
Separate genuine substance from branding, wrappers, thinly differentiated agent launches, or exploit-driven attention. If the repo sounds bigger than it is, say so.

### Gap Analysis
Identify what should be showing up but is not: missing infrastructure, underrepresented defensive/security work, absent tooling for known pain points, or stagnant categories.

### Context
Compare the current week to the prior week when a prior summary exists. Note continuity, acceleration, reversal, or broadening of a theme. If no prior summary exists, say so briefly and avoid pretending longitudinal certainty.

## Quality Criteria

### Good analysis
- Synthesizes, ranks, and judges instead of listing.
- Connects individual repos into ecosystem-level patterns.
- Names uncertainty honestly when data quality is limited.
- Uses evidence from the payload without sounding like the payload.
- Makes the `Blind Spots` section useful and specific.
- Leaves Amy’s generator with all frontmatter needed for site publication.

### Bad analysis
- Reads like release notes or a changelog.
- Repeats repo descriptions without editorial value.
- Confuses total stars with weekly momentum.
- Refuses to criticize obvious hype or noise.
- Omits gaps, caveats, or trend continuity.
- Produces frontmatter that cannot drive the weekly page template.

## Reviewer-Gate Expectations

A weekly analysis is publishable only if all of the following are true:

- `quality_score >= 60`
- all required frontmatter fields are present,
- all six required H2 sections are present in order (`This Week's Trends`, `Where Industry Meets Code`, `Signal & Noise`, `Blind Spots`, `The Week Ahead`, `Key References`),
- `### Notable Projects` and `### Press & Industry` subsections are present under `## Key References`,
- body word count is at least 200,
- the prose contains no raw JSON, tool logs, or placeholder text.

## Generator Handoff Rules

The generator may assume:

- the summary frontmatter already contains the weekly page fields Amy’s Hugo templates expect,
- `summary` is safe to surface in list views,
- `top_repo` is a deliberate editorial choice,
- body headings are stable and machine-detectable,
- body headings use the stable structure defined in this spec; the generator can extract any section by heading name.

The analyzer may assume:

- `data/raw/` is authoritative input,
- prior-week continuity is optional but preferred,
- missing `stars_gained` must produce a caveat, not a silent omission.
