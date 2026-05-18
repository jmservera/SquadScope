# PRD: Topic-Specific News Channels for SquadScope

**Author:** Leela (Lead/Architect)  
**Date:** 2026-05-18  
**Status:** Draft  
**Type:** Feature PRD  
**Depends on:** docs/PRD.md (original), docs/learning-audit.md

---

## Executive Summary

SquadScope currently crawls all of GitHub looking for "what's interesting this week." This produces broad but shallow coverage — jack of all topics, master of none. This PRD defines how to generalize SquadScope into a **topic-channel system** where each deployment is configured for a specific domain (e.g., `ai-ml`, `rust`, `security`), producing focused, expert-level weekly digests with calibrated learning per topic.

The approach is **feature first, not a separate platform.** v1 delivers a single configurable topic per instance (one fork/config per topic). Multi-topic single-instance is deferred to v2.

---

## Problem Statement

### Why topic-specific is better than general

1. **Signal quality degrades with breadth.** A general GitHub crawl returns repos spanning AI, systems programming, web frameworks, security tools, and student homework. No single editorial voice can meaningfully assess "is this Rust crate important?" and "is this ML paper implementation notable?" in the same breath.

2. **Learning cannot calibrate across domains.** The learning audit (docs/learning-audit.md) identified that wisdom must flow back into analysis (G7). But shared wisdom across domains produces uncalibrated judgments — a heuristic like "repos with >500 stars/week are always significant" is true in AI/ML but false in niche systems programming.

3. **GitHub topic filtering is noisy.** Simply adding `topic:rust` to a search query returns thousands of results including tutorials, homework, and abandoned projects. Topic filtering needs a multi-stage pipeline: query → score → filter → analyze.

4. **Readers want depth, not breadth.** A security professional subscribing to SquadScope doesn't want to scroll past 15 ML repos to find the 3 security tools that matter this week.

5. **Predictions need domain context.** "This will be important" means something different in each field. A prediction ledger must be per-topic to be meaningful.

---

## Goals & Non-Goals

### Goals

- **G1:** Define a topic configuration format (`squadscope.topic.yml`) that controls all topic-specific behavior
- **G2:** Namespace all data, content, prompts, RSS, and learning state by topic
- **G3:** Deliver per-topic RSS feeds at `/topics/{topic}/index.xml`
- **G4:** Implement a scoring pipeline for GitHub results (not just keyword filters)
- **G5:** Isolate learning state per topic (wisdom, skills, prediction scores)
- **G6:** Add a prediction ledger that tracks claims vs outcomes per topic
- **G7:** Define topic quality criteria (minimum viable coverage thresholds)
- **G8:** Ship 2 example topic configs: `ai-ml` and `rust`

### Non-Goals

- Multi-topic single-instance deployment (v2)
- Topic marketplace or discovery
- User-facing topic configuration UI
- Real-time or daily publishing cadence
- Cross-topic trend correlation
- Non-GitHub data sources per topic (future enhancement)

---

## Topic Configuration

### File: `squadscope.topic.yml`

Each SquadScope instance has exactly one topic config at the repository root.

```yaml
# squadscope.topic.yml — defines a single topic channel
topic:
  id: ai-ml                          # URL-safe identifier
  name: "AI & Machine Learning"      # Human-readable name
  description: "Weekly digest of significant AI/ML repositories, frameworks, and research implementations on GitHub"

# Crawler queries — multiple queries combined for coverage
queries:
  primary:
    - "topic:machine-learning stars:>50 pushed:>{last_week}"
    - "topic:deep-learning stars:>50 pushed:>{last_week}"
    - "topic:artificial-intelligence stars:>30 pushed:>{last_week}"
    - "topic:llm stars:>20 pushed:>{last_week}"
  secondary:
    - "topic:transformers stars:>100 pushed:>{last_week}"
    - "topic:diffusion stars:>30 pushed:>{last_week}"
    - "topic:rag stars:>20 pushed:>{last_week}"

# Scoring pipeline — repos must pass these filters
scoring:
  min_stars: 20                      # Absolute minimum to consider
  min_stars_gained: 10               # Minimum weekly star delta
  max_age_days: 365                  # Exclude repos older than this from "new" category
  language_boost:                    # Boost score for expected languages
    - python: 1.2
    - jupyter-notebook: 1.1
    - rust: 1.0
  topic_relevance:                   # Required topic overlap (at least one must match)
    - machine-learning
    - deep-learning
    - artificial-intelligence
    - neural-network
    - llm
    - nlp
    - computer-vision
    - reinforcement-learning
  noise_topics:                      # Penalty topics (reduce score)
    - tutorial
    - course
    - awesome-list
    - homework
  noise_name_patterns:               # Regex patterns that reduce relevance score
    - "^awesome-"
    - "-tutorial$"
    - "-course$"

# Quality thresholds — topic must meet these to justify a channel
quality:
  min_repos_per_week: 8              # Minimum repos passing filters weekly
  max_false_positive_rate: 0.25      # Max 25% irrelevant results after scoring
  min_signal_repos: 3                # At least 3 genuinely significant repos per issue

# Content configuration
content:
  tone: "technical, analytical"
  audience: "ML engineers and researchers"
  emphasis:
    - "Novel architectures and training techniques"
    - "Production-ready frameworks and tools"
    - "Significant performance improvements"
  de_emphasis:
    - "Yet another wrapper around OpenAI API"
    - "Awesome lists and link collections"
    - "Course materials and tutorials"

# Learning configuration
learning:
  wisdom_file: "topics/ai-ml/wisdom.md"
  skills_dir: "topics/ai-ml/skills/"
  predictions_file: "topics/ai-ml/predictions.jsonl"
  reskill_context:
    - "What ML-specific heuristics should we update?"
    - "Are we over/under-weighting any sub-domain?"
    - "Which prediction categories are we worst at?"
```

### Second example: `rust`

```yaml
topic:
  id: rust
  name: "Rust Ecosystem"
  description: "Weekly digest of significant Rust crates, tools, and ecosystem developments"

queries:
  primary:
    - "language:rust stars:>30 pushed:>{last_week}"
    - "topic:rust stars:>20 pushed:>{last_week}"
    - "topic:rust-lang stars:>20 pushed:>{last_week}"
  secondary:
    - "topic:cargo stars:>50 pushed:>{last_week}"
    - "topic:wasm language:rust stars:>30 pushed:>{last_week}"

scoring:
  min_stars: 15
  min_stars_gained: 8
  max_age_days: 730
  language_boost:
    - rust: 1.5
    - c: 1.0
  topic_relevance:
    - rust
    - rust-lang
    - cargo
    - wasm
    - systems-programming
    - embedded
  noise_topics:
    - tutorial
    - learning-rust
    - rust-exercises
  noise_name_patterns:
    - "^rust-by-example"
    - "-exercises$"

quality:
  min_repos_per_week: 5
  max_false_positive_rate: 0.30
  min_signal_repos: 2

content:
  tone: "systems-oriented, precise"
  audience: "Rust developers and systems programmers"
  emphasis:
    - "Crates reaching stability milestones"
    - "Performance and safety innovations"
    - "Ecosystem tooling improvements"
  de_emphasis:
    - "Beginner tutorials"
    - "Reimplementations of existing tools without novel approach"

learning:
  wisdom_file: "topics/rust/wisdom.md"
  skills_dir: "topics/rust/skills/"
  predictions_file: "topics/rust/predictions.jsonl"
  reskill_context:
    - "Are we calibrated for the Rust ecosystem's smaller scale?"
    - "Which crate categories are we missing?"
```

---

## Pipeline Changes

### Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Topic-Aware Pipeline (v1)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  squadscope.topic.yml                                                   │
│         │                                                               │
│         ▼                                                               │
│  ┌───────────┐  query+   ┌───────────┐  scored   ┌──────────────┐     │
│  │  Crawler   │──────────►│  Scorer   │──────────►│   Analyzer   │     │
│  └───────────┘  raw JSON  └───────────┘  repos    └──────────────┘     │
│                                                          │              │
│                                              ┌───────────┼──────────┐  │
│                                              ▼           ▼          ▼  │
│                                        ┌─────────┐ ┌──────────┐ ┌────┐│
│                                        │ Content │ │Prediction│ │RSS ││
│                                        │  Page   │ │  Ledger  │ │Feed││
│                                        └─────────┘ └──────────┘ └────┘│
│                                                                         │
│  Learning loop (per topic):                                             │
│  predictions.jsonl → validate_predictions.py → scorecard → reskill     │
│  → updated wisdom.md → injected into next analysis prompt              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1. Crawler Changes (`scripts/crawl.py`)

**Current:** Hardcoded queries in `crawl.py` searching for generic trending repos.

**Proposed:**
- Read `squadscope.topic.yml` at startup
- Build search queries from `queries.primary` and `queries.secondary`
- Apply `scoring.min_stars` as a pre-filter in the GitHub API query
- Template `{last_week}` in query strings to ISO date of 7 days ago
- Output to `data/raw/{topic_id}/YYYY-WNN.json` (namespaced)

```python
# Pseudocode for topic-aware crawling
config = load_topic_config("squadscope.topic.yml")
queries = config["queries"]["primary"] + config["queries"]["secondary"]
for q in queries:
    q = q.replace("{last_week}", last_week_iso())
    results = search_github(q)
    all_repos.extend(results)

# Deduplicate by full_name
unique_repos = deduplicate(all_repos)
write_json(f"data/raw/{config['topic']['id']}/YYYY-WNN.json", unique_repos)
```

### 2. New: Scoring Pipeline (`scripts/score_repos.py`)

A new pipeline stage between crawl and analyze. Repos get a **relevance score** (0-100):

| Factor | Weight | Scoring Logic |
|--------|--------|---------------|
| Topic overlap | 30% | Count of repo topics matching `scoring.topic_relevance` |
| Star momentum | 25% | `stars_gained / min_stars_gained` ratio (capped at 3x) |
| Language match | 15% | Boost from `scoring.language_boost` |
| Noise penalty | -20% | Repos matching `noise_topics` or `noise_name_patterns` |
| Recency | 10% | Days since last push (more recent = higher) |

**Output:** `data/scored/{topic_id}/YYYY-WNN.json` — same schema as raw but with `relevance_score` field added. Only repos with `relevance_score >= 40` pass to analysis.

### 3. Analysis Prompt Changes (`prompts/analyze-weekly.md`)

**Current:** Static prompt with no topic context or learned state.

**Proposed:** Topic-aware prompt template with injection points:

```markdown
# Weekly Analysis: {{TOPIC_NAME}}

You are analyzing GitHub repositories for the **{{TOPIC_NAME}}** channel.
Audience: {{AUDIENCE}}
Tone: {{TONE}}

## Emphasis
{{EMPHASIS_LIST}}

## De-emphasis
{{DE_EMPHASIS_LIST}}

## Learned Wisdom (from prior reskill cycles)
{{WISDOM_CONTENT}}

## Active Skills
{{SKILLS_CONTENT}}

## Prediction Track Record
{{PREDICTION_SCORECARD}}

## Instructions
Analyze the scored repositories in `data/scored/{{TOPIC_ID}}/YYYY-WNN.json`.
...
```

### 4. Content Namespacing

| Asset | Current Path | Topic-Aware Path |
|-------|-------------|-----------------|
| Raw crawl data | `data/raw/YYYY-WNN.json` | `data/raw/{topic_id}/YYYY-WNN.json` |
| Scored data | N/A (new) | `data/scored/{topic_id}/YYYY-WNN.json` |
| Analysis output | `data/analyzed/YYYY-WNN-summary.md` | `data/analyzed/{topic_id}/YYYY-WNN-summary.md` |
| Star snapshots | `data/snapshots/YYYY-WNN.json` | `data/snapshots/{topic_id}/YYYY-WNN.json` |
| Hugo content | `content/weekly/YYYY-WNN.md` | `content/topics/{topic_id}/YYYY-WNN.md` |
| RSS feed | `/index.xml` | `/topics/{topic_id}/index.xml` |
| Wisdom | `.squad/identity/wisdom.md` | `topics/{topic_id}/wisdom.md` |
| Skills | `.squad/skills/` | `topics/{topic_id}/skills/` |
| Predictions | N/A (new) | `topics/{topic_id}/predictions.jsonl` |

### 5. RSS Per Topic

Hugo taxonomy configuration:

```toml
# hugo.toml additions
[taxonomies]
  topic = "topics"

[outputFormats.RSS]
  mediaType = "application/rss+xml"
  baseName = "index"

[params]
  topicId = "ai-ml"  # From squadscope.topic.yml
```

Each topic gets its own RSS feed at `/topics/{topic_id}/index.xml`. The site root `/index.xml` remains as an aggregate feed (or is removed in single-topic mode).

---

## Learning System Integration

### Per-Topic Learning State

Each topic maintains isolated learning state:

```
topics/{topic_id}/
├── wisdom.md              # Accumulated heuristics for this domain
├── skills/                # Extracted patterns and rules
│   ├── SKILL-001.md
│   └── SKILL-002.md
├── predictions.jsonl      # Prediction ledger (append-only)
└── scorecards/            # Hindsight validation results
    ├── 2026-W21.json
    └── 2026-W25.json
```

### Why Isolation Matters

From the learning audit: "shared wisdom across domains produces uncalibrated judgments." Examples:

- AI/ML wisdom: "Repos with HuggingFace integrations tend to gain adoption quickly" → **meaningless for Rust**
- Rust wisdom: "Crates with `no_std` support indicate systems-level seriousness" → **meaningless for AI/ML**
- Security wisdom: "CVE-related repos spike and fade within 2 weeks" → **misleading if applied to general software**

### Prediction Ledger (`predictions.jsonl`)

Each analysis produces machine-readable predictions appended to the ledger:

```jsonl
{"week":"2026-W21","repo":"owner/name","claim":"signal","confidence":0.8,"category":"framework","predicted_stars_4w":500}
{"week":"2026-W21","repo":"owner/name","claim":"noise","confidence":0.7,"category":"wrapper","reason":"thin wrapper around existing API"}
{"week":"2026-W21","repo":"owner/name","claim":"gap","confidence":0.6,"category":"missing-tooling","description":"No good Rust WASM debugger exists yet"}
```

**Fields:**
- `week`: ISO week of the prediction
- `repo`: Full repository name (or null for gap predictions)
- `claim`: One of `signal`, `noise`, `gap`
- `confidence`: 0.0-1.0 how sure the system is
- `category`: Domain-specific category
- `predicted_stars_4w`: Expected star count in 4 weeks (for signal/noise)
- `reason`/`description`: Human-readable explanation

### Hindsight Validation (`scripts/validate_predictions.py`)

Runs 4 weeks after predictions are made. Compares claims to outcomes:

```python
# Validation logic
for prediction in load_predictions(topic_id, target_week):
    if prediction["claim"] == "signal":
        actual_stars = get_current_stars(prediction["repo"])
        predicted = prediction["predicted_stars_4w"]
        score = min(actual_stars / predicted, 2.0)  # Cap at 2x
        scorecard.append({"prediction": prediction, "actual": actual_stars, "score": score})
    elif prediction["claim"] == "noise":
        # Noise repos should have plateaued or declined
        delta = get_star_delta(prediction["repo"], weeks=4)
        score = 1.0 if delta < prediction.get("predicted_stars_4w", 50) else 0.0
        scorecard.append({"prediction": prediction, "actual_delta": delta, "score": score})
```

**Scorecard output** feeds into reskill: "Last month we were 72% accurate on signal calls but only 45% on noise calls in ai-ml. We tend to overestimate wrapper libraries."

### Reskill Integration

The reskill prompt (run every 5th cycle) now receives:
1. Topic-specific wisdom from `topics/{topic_id}/wisdom.md`
2. Latest scorecard from `topics/{topic_id}/scorecards/`
3. Prediction accuracy trend across last 5 scorecards
4. Topic config context (what we're optimizing for)

Reskill outputs are written back to topic-specific paths, ensuring one topic's learnings never contaminate another.

---

## Content Architecture

### Topic Channels

URL structure:
```
/                           → Home (links to topic channel)
/topics/{topic_id}/         → Topic landing page (latest + archive)
/topics/{topic_id}/2026-W21 → Weekly issue page
/topics/{topic_id}/index.xml → RSS feed for this topic
```

### Hugo Content Structure

```
content/
└── topics/
    └── ai-ml/
        ├── _index.md          # Topic landing page
        ├── 2026-W21.md        # Weekly issue
        ├── 2026-W22.md
        └── ...
```

### Navigation

For v1 (single-topic instance), the site homepage redirects to the topic channel. The topic archive page lists all weekly issues with summaries.

For v2 (multi-topic), a topic selector would appear in navigation.

---

## v1 Scope: Single Configurable Topic

### What ships in v1

1. **`squadscope.topic.yml` config format** — fully specified, validated at pipeline start
2. **Topic-aware crawler** — reads queries from config, outputs to namespaced paths
3. **Scoring pipeline** — `scripts/score_repos.py` with configurable weights
4. **Topic-aware analysis prompt** — injects topic context, wisdom, and scorecard
5. **Prediction ledger** — appended to after each analysis
6. **Hindsight validation script** — runs on 4-week-old predictions
7. **Per-topic learning state** — isolated wisdom, skills, scorecards
8. **Topic RSS feed** — at `/topics/{topic_id}/index.xml`
9. **Two example configs** — `examples/topics/ai-ml.yml` and `examples/topics/rust.yml`
10. **Config validation script** — `scripts/validate_topic_config.py`

### What does NOT ship in v1

- Multi-topic in a single instance
- Topic discovery or marketplace
- Cross-topic learning transfer
- Dynamic query generation
- Topic health monitoring dashboard

### Deployment Model (v1)

One SquadScope fork per topic. Each fork:
- Has its own `squadscope.topic.yml`
- Runs its own GitHub Actions schedule
- Produces its own GitHub Pages site
- Accumulates its own learning state
- Has its own RSS feed

This is intentionally simple. Forks share the same codebase but diverge on configuration and learned state.

---

## v2 Vision: Multi-Topic Single Instance

**Deferred.** Documented here for future planning only.

### What v2 would add

- Single instance running multiple topics on different schedules
- Shared infrastructure, isolated topic state
- Topic health monitoring (auto-disable topics below quality thresholds)
- Cross-topic signals ("this repo is trending in BOTH ai-ml and rust channels")
- Topic marketplace (community-contributed topic configs)
- Unified navigation across topics

### Why v2 is premature now

- Adds orchestration complexity (per-topic cron, per-topic secrets)
- Learning isolation is harder in shared instances (accidental cross-contamination)
- No user demand signal yet — need v1 adoption data first
- GitHub Actions concurrency constraints make multi-topic scheduling complex

---

## Implementation Plan

### Issues to Create

| # | Title | Phase | Depends On | Assignee Profile |
|---|-------|-------|-----------|-----------------|
| 1 | Define `squadscope.topic.yml` schema and validator | Foundation | — | Architect |
| 2 | Namespace data directories by topic ID | Foundation | #1 | Crawler |
| 3 | Implement scoring pipeline (`scripts/score_repos.py`) | Pipeline | #1, #2 | Crawler |
| 4 | Make crawler read queries from topic config | Pipeline | #1, #2 | Crawler |
| 5 | Create topic-aware analysis prompt template | Pipeline | #1 | Analyzer |
| 6 | Add prediction ledger output to analysis | Pipeline | #5 | Analyzer |
| 7 | Implement hindsight validation script | Learning | #6 | Analyzer |
| 8 | Per-topic learning state directories and seeding | Learning | #1 | Architect |
| 9 | Wire prediction scorecard into reskill prompt | Learning | #7 | Analyzer |
| 10 | Hugo topic taxonomy and per-topic RSS | Content | #2 | Site |
| 11 | Topic landing page template | Content | #10 | Site |
| 12 | Example config: ai-ml | Validation | #1-#4 | Validator |
| 13 | Example config: rust | Validation | #1-#4 | Validator |
| 14 | Topic quality threshold enforcement | Quality | #3 | Crawler |
| 15 | End-to-end integration test with example topic | Validation | All | Validator |

### Dependencies

```
#1 (schema) ─┬─► #2 (namespacing) ─┬─► #3 (scorer) ──► #4 (crawler)
              │                      │                        │
              │                      └─► #10 (Hugo)          ▼
              │                                          #12, #13 (examples)
              └─► #5 (prompt) ──► #6 (predictions) ──► #7 (validation)
                                                            │
                                                            ▼
                                                    #9 (reskill wiring)
```

### Estimated Effort

- **Foundation (Issues 1-2):** 1 session
- **Pipeline (Issues 3-6):** 2-3 sessions
- **Learning (Issues 7-9):** 2 sessions
- **Content (Issues 10-11):** 1 session
- **Validation (Issues 12-15):** 1-2 sessions

**Total:** ~7-9 work sessions

---

## Open Questions

| # | Question | Impact | Proposed Resolution |
|---|----------|--------|-------------------|
| OQ1 | Should topic configs live in repo root or `topics/` dir? | File organization | Repo root for v1 (single topic); move to `topics/` in v2 |
| OQ2 | How to handle repos that span multiple topics? | Dedup in multi-topic v2 | v1: irrelevant (single topic). v2: each topic scores independently |
| OQ3 | What's the minimum weeks of data before learning is meaningful? | Reskill timing | Propose 4 weeks minimum before first hindsight validation runs |
| OQ4 | Should prediction confidence be system-generated or human-calibrated initially? | Learning accuracy | Start with fixed confidence (0.7 for signal, 0.5 for noise), calibrate after 8 weeks of scorecard data |
| OQ5 | Enrichment signals beyond stars — which to add first? | Prediction quality | Forks and contributor count (cheapest API calls, highest signal per learning-audit G13) |
| OQ6 | Should topic quality thresholds auto-disable a topic or just warn? | Reliability | Warn-only for v1 (log to workflow summary), auto-disable in v2 |

---

## Success Metrics

### Quantitative (measurable after 8 weeks of operation)

| Metric | Target | Measurement |
|--------|--------|-------------|
| False positive rate | < 25% per topic | Manual audit of 20 random "signal" calls per month |
| Prediction accuracy (signal) | > 65% | Hindsight validation scorecard |
| Prediction accuracy (noise) | > 55% | Hindsight validation scorecard |
| Repos per weekly issue | ≥ quality.min_repos_per_week from config | Automated count |
| RSS subscribers per topic | > 0 within 4 weeks | Analytics (if available) |
| Learning improvement trend | Prediction accuracy increases by ≥ 5% over 8 weeks | Scorecard comparison |

### Qualitative

- Topic experts find the digest "saves them time" vs. manual GitHub browsing
- Analysis tone matches configured audience expectations
- Signal/Noise/Gaps sections feel calibrated to the specific domain
- Learned wisdom in `wisdom.md` contains domain-specific (not generic) heuristics after 3 reskill cycles

---

## Relationship to Existing Work

### PRD.md (original)
This PRD extends the original architecture. All existing pipeline contracts (Crawl → Analyze → Generate → Deploy) remain valid — they gain a topic namespace prefix but keep the same data formats and quality gates.

### Learning Audit (docs/learning-audit.md)
This PRD directly addresses:
- **G7 (prompt feedback loop):** Topic-aware prompt template with `{{WISDOM_CONTENT}}` injection
- **G8 (hindsight validation):** `scripts/validate_predictions.py` with per-topic scorecards
- **G9 (prediction registry):** `predictions.jsonl` format defined
- **G13 (enrichment signals):** Fork/contributor data noted as OQ5, planned for scorer enrichment

### Decisions.md
- Respects Decision 3 (pipeline stage contracts) — adds a scoring stage but preserves existing boundaries
- Respects Decision 4 (reviewer gate) — quality gate applies per-topic
- Extends Decision 6 (reskill) — reskill reads per-topic state instead of global state
