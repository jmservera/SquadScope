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
## Notable New Repositories

## Trending This Week

## Trend Analysis
### Signal
### Noise

## What's Missing
### Gaps

## Conclusion
```

Every repository mentioned in the body must be rendered as a clickable markdown link in this exact format: `[owner/repo](https://github.com/owner/repo)`.

### Image accessibility guidance

If an analysis ever includes an image, chart, or screenshot:

- provide concise, descriptive alt text that explains the information a reader would otherwise miss,
- do not use placeholder alt text like `image`, `screenshot`, or the file name,
- keep decorative images rare; only use empty alt text when the image adds no editorial meaning,
- explain any important numbers or trends in the surrounding prose so the page still works without the image.

### Section guidance

#### 1. Notable New Repositories
- **Purpose:** Curate the week’s most credible new launches.
- **Include:** 3-7 repos, grouped into a coherent story rather than a bullet dump.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Tone:** Selective and judgmental.
- **Length:** ~120-220 words.
- **Avoid:** Exhaustive listings or copy/pasted repo descriptions.

#### 2. Trending This Week
- **Purpose:** Explain where attention moved.
- **Include:** The most relevant momentum winners, plus a caveat if `stars_gained` is unavailable.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Tone:** Analytical, not celebratory.
- **Length:** ~100-180 words.
- **Avoid:** Treating raw popularity as momentum when deltas are missing.

#### 3. Trend Analysis
- **Purpose:** Explain the bigger technical story.
- **Required subsections:**
  - `### Signal` — what looks durable or strategically important.
  - `### Noise` — what looks inflated, repetitive, or low-substance.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Length:** ~150-260 words total.
- **Avoid:** Repeating section 1 and section 2 without synthesis.

#### 4. What's Missing
- **Purpose:** Surface absent or underweighted themes.
- **Required subsection:** `### Gaps`.
- **Include:** 2-4 concrete blind spots or underserved categories.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Length:** ~80-160 words.
- **Avoid:** Generic filler like “more innovation is needed.”

#### 5. Conclusion
- **Purpose:** End with a clear editorial takeaway.
- **Include:** Why the week matters and what to watch next.
- **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
- **Length:** ~50-110 words.
- **Avoid:** Introducing brand-new evidence.

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
- Makes the `What's Missing` section useful and specific.
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
- all five required H2 sections are present in order,
- `Signal`, `Noise`, and `Gaps` subsections are present,
- body word count is at least 200,
- the prose contains no raw JSON, tool logs, or placeholder text.

## Generator Handoff Rules

The generator may assume:

- the summary frontmatter already contains the weekly page fields Amy’s Hugo templates expect,
- `summary` is safe to surface in list views,
- `top_repo` is a deliberate editorial choice,
- body headings are stable and machine-detectable,
- the analyzed summary and published weekly page both use `## Trending This Week` as the stable H2 heading, with any stars-gained caveat expressed in the prose rather than the heading text.

The analyzer may assume:

- `data/raw/` is authoritative input,
- prior-week continuity is optional but preferred,
- missing `stars_gained` must produce a caveat, not a silent omission.
