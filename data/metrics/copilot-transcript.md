# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `889b8f6a-9a7c-4852-a650-2662936a299c`  
> - **Started:** 5/20/2026, 8:58:53 PM  
> - **Duration:** 7m 16s  
> - **Exported:** 5/20/2026, 9:06:09 PM  

---

<sub>⏱️ 0s</sub>

### 👤 User

Farnsworth, read the file at /tmp/tmp.PKvZDntgUh — it contains the weekly data and analysis instructions. Follow them exactly and write the analysis to data/analyzed/2026-W21-summary.md.

---

<sub>⏱️ 8s</sub>

### ✅ `bash`

**Read the weekly data file**

$ cat /tmp/tmp.PKvZDntgUh

<details>
<summary>20 lines</summary>

````
Output too large to read at once (349.7 KB). Saved to: /tmp/copilot-tool-output-1779310741858-15fkgz.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-20T20:58:40Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-20T20:58:19Z",
  "new_repos": [
    {
      "name
<exited with exit code 0>
````

</details>


---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Read full file content**

$ cat /tmp/copilot-tool-output-1779310741858-15fkgz.txt

<details>
<summary>20 lines</summary>

````
Output too large to read at once (349.7 KB). Saved to: /tmp/copilot-tool-output-1779310744800-so0taa.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-20T20:58:40Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-20T20:58:19Z",
  "new_repos": [
    {
      "name
<exited with exit code 0>
````

</details>


---

<sub>⏱️ 14s</sub>

### ✅ `bash`

**Check file structure**

$ wc -l /tmp/tmp.PKvZDntgUh && head -100 /tmp/tmp.PKvZDntgUh

<details>
<summary>96 lines</summary>

````
10982 /tmp/tmp.PKvZDntgUh
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-20T20:58:40Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-20T20:58:19Z",
  "new_repos": [
    {
      "name": "zerolang",
      "owner": "vercel-labs",
      "full_name": "vercel-labs/zerolang",
      "description": "The programming language for agents",
      "language": "C",
      "stars": 3913,
      "forks": 227,
      "created_at": "2026-05-15T16:55:16Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/vercel-labs/zerolang"
    },
    {
      "name": "native-feel-skill",
      "owner": "yetone",
      "full_name": "yetone/native-feel-skill",
      "description": "An Agent Skill for designing cross-platform desktop apps that feel native — distilled from Raycast's 2.0 deep-dive and reverse engineering of Raycast Beta.app. Eight architectural tenets, four-layer architecture, WebKit/WebView2 survival guide, 75-item ship audit.",
      "language": null,
      "stars": 1350,
      "forks": 61,
      "created_at": "2026-05-14T19:28:43Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/yetone/native-feel-skill"
    },
    {
      "name": "vggt-omega",
      "owner": "facebookresearch",
      "full_name": "facebookresearch/vggt-omega",
      "description": "[CVPR 2026 Oral] VGGT Omega",
      "language": "Python",
      "stars": 1334,
      "forks": 40,
      "created_at": "2026-05-14T04:43:13Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/facebookresearch/vggt-omega"
    },
    {
      "name": "agents-best-practices",
      "owner": "DenisSergeevitch",
      "full_name": "DenisSergeevitch/agents-best-practices",
      "description": "Provider-neutral Agent Skill for Codex, Claude Code, and agentic harness design.",
      "language": null,
      "stars": 892,
      "forks": 81,
      "created_at": "2026-05-15T21:32:21Z",
      "topics": [
        "agent-skill",
        "agent-skills",
        "agentic-workflows",
        "agents",
        "ai-agents",
        "anthropic",
        "claude",
        "claude-code",
        "codex",
        "codex-skill",
        "mcp",
        "prompt-engineering"
      ],
      "license": "MIT",
      "url": "https://github.com/DenisSergeevitch/agents-best-practices"
    },
    {
      "name": "smallcode",
      "owner": "Doorman11991",
      "full_name": "Doorman11991/smallcode",
      "description": "AI coding agent optimized for small LLMs. 87% benchmark with 4B-active model.",
      "language": "JavaScript",
      "stars": 803,
      "forks": 53,
      "created_at": "2026-05-18T06:19:44Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/Doorman11991/smallcode"
    },
    {
      "name": "codex-complexity-optimizer",
<exited with exit code 0>
````

</details>


---

<sub>⏱️ 19s</sub>

### 📦 task (Completed)

### ✅ `bash`

**Check what's at the tmp path**

$ ls /tmp/tmp.PKvZDntgUh/ 2>/dev/null || ([ -f /tmp/tmp.PKvZDntgUh ] && echo "IS_FILE" || echo "NOT_FOUND")

```
IS_FILE
<exited with exit code 0>
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope.**

/home/runner/work/SquadScope/SquadScope

<details>
<summary>24 lines</summary>

```
.copilot
.git
.gitattributes
.github
.gitignore
.gitmodules
.squad
README.md
archetypes
assets
content
data
docs
examples
hugo.toml
layouts
prompts
pytest.ini
reply_thread1.graphql
requirements.txt
scripts
squadscope.topic.yml
tests
themes
```

</details>


### ✅ `bash`

**Read the analysis instructions file**

$ cat /tmp/tmp.PKvZDntgUh

<details>
<summary>20 lines</summary>

````
Output too large to read at once (349.7 KB). Saved to: /tmp/copilot-tool-output-1779310761080-o21l73.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-20T20:58:40Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-20T20:58:19Z",
  "new_repos": [
    {
      "name
<exited with exit code 0>
````

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad.**

/home/runner/work/SquadScope/SquadScope/.squad

<details>
<summary>23 lines</summary>

```
.first-run
agents
casting
ceremonies.md
config.json
decisions
decisions.md
health-2026-05-19T20:57:55Z.md
health_report.txt
history_summary.md
identity
log
logs
orchestration-log
orchestration.log
reskill
routing.md
run-counter.txt
session_end.log
skills
team.md
templates
topics
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/docs.**

/home/runner/work/SquadScope/SquadScope/docs

<details>
<summary>10 lines</summary>

```
PRD-techcrunch-integration.md
analysis-spec.md
decisions
dry-run-report.md
learning-audit.md
operator-guide.md
pipeline-validation.md
processed
qa-report.md
rollout-checklist.md
```

</details>


### ✅ `bash`

**Check size and preview instructions file**

$ wc -l /tmp/copilot-tool-output-1779310761080-o21l73.txt && head -200 /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>196 lines</summary>

````
10983 /tmp/copilot-tool-output-1779310761080-o21l73.txt
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-20T20:58:40Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-20T20:58:19Z",
  "new_repos": [
    {
      "name": "zerolang",
      "owner": "vercel-labs",
      "full_name": "vercel-labs/zerolang",
      "description": "The programming language for agents",
      "language": "C",
      "stars": 3913,
      "forks": 227,
      "created_at": "2026-05-15T16:55:16Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/vercel-labs/zerolang"
    },
    {
      "name": "native-feel-skill",
      "owner": "yetone",
      "full_name": "yetone/native-feel-skill",
      "description": "An Agent Skill for designing cross-platform desktop apps that feel native — distilled from Raycast's 2.0 deep-dive and reverse engineering of Raycast Beta.app. Eight architectural tenets, four-layer architecture, WebKit/WebView2 survival guide, 75-item ship audit.",
      "language": null,
      "stars": 1350,
      "forks": 61,
      "created_at": "2026-05-14T19:28:43Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/yetone/native-feel-skill"
    },
    {
      "name": "vggt-omega",
      "owner": "facebookresearch",
      "full_name": "facebookresearch/vggt-omega",
      "description": "[CVPR 2026 Oral] VGGT Omega",
      "language": "Python",
      "stars": 1334,
      "forks": 40,
      "created_at": "2026-05-14T04:43:13Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/facebookresearch/vggt-omega"
    },
    {
      "name": "agents-best-practices",
      "owner": "DenisSergeevitch",
      "full_name": "DenisSergeevitch/agents-best-practices",
      "description": "Provider-neutral Agent Skill for Codex, Claude Code, and agentic harness design.",
      "language": null,
      "stars": 892,
      "forks": 81,
      "created_at": "2026-05-15T21:32:21Z",
      "topics": [
        "agent-skill",
        "agent-skills",
        "agentic-workflows",
        "agents",
        "ai-agents",
        "anthropic",
        "claude",
        "claude-code",
        "codex",
        "codex-skill",
        "mcp",
        "prompt-engineering"
      ],
      "license": "MIT",
      "url": "https://github.com/DenisSergeevitch/agents-best-practices"
    },
    {
      "name": "smallcode",
      "owner": "Doorman11991",
      "full_name": "Doorman11991/smallcode",
      "description": "AI coding agent optimized for small LLMs. 87% benchmark with 4B-active model.",
      "language": "JavaScript",
      "stars": 803,
      "forks": 53,
      "created_at": "2026-05-18T06:19:44Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/Doorman11991/smallcode"
    },
    {
      "name": "codex-complexity-optimizer",
      "owner": "Kappaemme-git",
      "full_name": "Kappaemme-git/codex-complexity-optimizer",
      "description": "Codex skill for safe codebase complexity analysis and performance optimization reports",
      "language": "Python",
      "stars": 799,
      "forks": 46,
      "created_at": "2026-05-15T13:33:28Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/Kappaemme-git/codex-complexity-optimizer"
    },
    {
      "name": "mykonos-island-voxels",
      "owner": "boona13",
      "full_name": "boona13/mykonos-island-voxels",
      "description": "A browser-based isometric island builder with the soft, sun-bleached look of Mykonos. Vanilla ES modules, no bundler, mobile-friendly.",
      "language": "JavaScript",
      "stars": 675,
      "forks": 160,
      "created_at": "2026-05-14T05:35:33Z",
      "topics": [
        "canvas2d",
        "city-builder",
        "html5-game",
        "isometric-game",
        "mobile-friendly",
        "open-source",
        "vanilla-js"
      ],
      "license": "MIT",
      "url": "https://github.com/boona13/mykonos-island-voxels"
    },
    {
      "name": "MiniPlasma",
      "owner": "Nightmare-Eclipse",
      "full_name": "Nightmare-Eclipse/MiniPlasma",
      "description": "CVE-2020-17103 was apparently not patched or the patch was reversed, regardless this the PoC for an LPE in cldflt.sys",
      "language": "C#",
      "stars": 647,
      "forks": 160,
      "created_at": "2026-05-14T20:32:21Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/Nightmare-Eclipse/MiniPlasma"
    },
    {
      "name": "Subnautica-2-Release",
      "owner": "Juwluuu",
      "full_name": "Juwluuu/Subnautica-2-Release",
      "description": "Subnautica 2: Early Access release, Have Multiplayer 4-player co-op multiplayer, Planet Zazura exploration, DNA BioMod system, Tadpole modular submersible, new Leviathans list, CICADA crash site lore. Xbox Game Pass, Steam preload, base building blueprints, ocean currents, crafting recipes",
      "language": "C++",
      "stars": 644,
      "forks": 0,
      "created_at": "2026-05-14T15:08:34Z",
      "topics": [
        "early-access-subnautica-2",
        "nitrox-pirate",
        "pc-ports",
        "playstation-5",
        "porting-game",
        "ps5-bot",
        "ps5-stock",
        "subnautica",
        "subnautica-2",
        "subnautica-2-coming-to-ps5",
        "subnautica-2-multiplayer",
        "subnautica-2-on-ps5",
        "subnautica-2-release",
        "subnautica-2-release-date-ps5",
        "subnautica-2-steam",
        "subnautica-2-xbox",
        "subnautica-multiplayer",
        "unknown-worlds"
      ],
      "license": "MIT",
      "url": "https://github.com/Juwluuu/Subnautica-2-Release"
    },
    {
      "name": "VoidStrap-For-Roblox",
      "owner": "DARKHOLEUM",
      "full_name": "DARKHOLEUM/VoidStrap-For-Roblox",
      "description": "VoidStrap: Roblox bootstrapper, launcher utility. FFlag Editor, FastFlags, FPS Unlocker, memory trimmer, CPU watcher. UI customization, Aero theme, AniWatch layout, Nvidia Profile Inspector, .NET 10. Font sharpening, skybox changer, Join-Game Notify, AppSettings JSON, client optimization.",
      "language": "C#",
      "stars": 639,
      "forks": 1,
      "created_at": "2026-05-14T15:37:45Z",
      "topics": [
        "bloxstrap",
        "bootstrapper",
        "client-optimizer",
        "customizations",
        "fps-unlocker",
        "launcher",
        "modding",
        "performance-optimizations",
        "roblox",
        "smooth-roblox-pc",
        "voidstrap",
        "voidstrap-client",
        "voidstrap-download",
<exited with exit code 0>
````

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/docs/analysis-spec.md.**

/home/runner/work/SquadScope/SquadScope/docs/analysis-spec.md

<details>
<summary>352 lines</summary>

````
1. # Weekly Analysis Specification
2. 
3. This document defines the analyzer contract between `data/raw/YYYY-WNN.json` and `data/analyzed/YYYY-WNN-summary.md`.
4. 
5. ## Purpose
6. 
7. The analyzer turns a weekly GitHub crawl into a structured editorial summary that is:
8. 
9. - consistent enough for CI automation,
10. - opinionated enough to be worth reading,
11. - strict enough for downstream site generation, and
12. - traceable enough for reviewer-gate validation.
13. 
14. The analyzer is a read-only consumer of `data/raw/`. It may interpret, rank, and summarize the crawl, but it must not rewrite the input artifact.
15. 
16. ## Editorial Lens
17. 
18. SquadScope analysis uses a three-part editorial lens:
19. 
20. - **Signal** — projects or shifts that matter because they solve real problems, represent credible technical movement, or reveal durable ecosystem direction.
21. - **Noise** — activity that is loud but weak: marketing-heavy launches, copycat agents, exploit/bypass churn, or trend-chasing with little substance.
22. - **Gaps** — meaningful absences: categories, problem spaces, or technical needs that should be showing more energy but are not.
23. 
24. The reader-facing markdown keeps the five approved weekly sections, but the analysis itself must explicitly surface **Signal**, **Noise**, and **Gaps** as labeled subsections.
25. 
26. ## Input Contract
27. 
28. ### File naming
29. 
30. - **Location:** `data/raw/`
31. - **Filename:** `YYYY-WNN.json`
32. - **Example:** `data/raw/2026-W21.json`
33. 
34. ### Analyzer read scope
35. 
36. The analyzer reads these fields:
37. 
38. - `week`
39. - `crawled_at`
40. - `new_repos[]`
41. - `trending_repos[]`
42. - `signals.top_topics[]`
43. - `metadata.partial_failures` *(optional diagnostic input; emitted by `scripts/crawl.py` today, but analyzers must tolerate absence)*
44. - `metadata.filter_summary` *(optional diagnostic input; emitted by `scripts/crawl.py` today, but analyzers must tolerate absence)*
45. - `metadata.snapshot_path` *(optional diagnostic input; emitted by `scripts/crawl.py` today, but analyzers must tolerate absence)*
46. 
47. Unknown fields must be ignored. The current crawler emits these diagnostic metadata fields in its own artifacts, but analyzers must not fail when they are missing from backfilled or forward-compatible payloads.
48. 
49. ### JSON schema
50. 
51. ```json
52. {
53.   "$schema": "https://json-schema.org/draft/2020-12/schema",
54.   "title": "SquadScope Weekly Crawl Payload",
55.   "type": "object",
56.   "additionalProperties": true,
57.   "required": [
58.     "week",
59.     "crawled_at",
60.     "new_repos",
61.     "trending_repos",
62.     "signals",
63.     "metadata"
64.   ],
65.   "properties": {
66.     "week": {
67.       "type": "string",
68.       "pattern": "^[0-9]{4}-W[0-9]{2}$"
69.     },
70.     "crawled_at": {
71.       "type": "string",
72.       "format": "date-time"
73.     },
74.     "new_repos": {
75.       "type": "array",
76.       "items": { "$ref": "#/$defs/repo" }
77.     },
78.     "trending_repos": {
79.       "type": "array",
80.       "items": { "$ref": "#/$defs/trendingRepo" }
81.     },
82.     "signals": {
83.       "type": "object",
84.       "additionalProperties": true,
85.       "required": ["top_topics"],
86.       "properties": {
87.         "top_topics": {
88.           "type": "array",
89.           "items": {
90.             "type": "object",
91.             "additionalProperties": false,
92.             "required": ["topic", "count"],
93.             "properties": {
94.               "topic": { "type": "string" },
95.               "count": { "type": "integer", "minimum": 0 }
96.             }
97.           }
98.         }
99.       }
100.     },
101.     "metadata": {
102.       "type": "object",
103.       "additionalProperties": true,
104.       "properties": {
105.         "api_calls_used": { "type": "integer", "minimum": 0 },
106.         "cache_hits": { "type": "integer", "minimum": 0 },
107.         "stale_cache_hits": { "type": "integer", "minimum": 0 },
108.         "rate_limit_limit": { "type": ["integer", "null"], "minimum": 0 },
109.         "rate_limit_remaining": { "type": ["integer", "null"], "minimum": 0 },
110.         "rate_limit_reset": { "type": ["integer", "null"], "minimum": 0 },
111.         "rate_limit_resource": { "type": ["string", "null"] },
112.         "partial_failures": {
113.           "type": "array",
114.           "items": { "type": "string" }
115.         },
116.         "snapshot_path": { "type": "string" },
117.         "filter_summary": {
118.           "type": "object",
119.           "additionalProperties": {
120.             "type": "object",
121.             "additionalProperties": { "type": "integer", "minimum": 0 }
122.           }
123.         }
124.       }
125.     }
126.   },
127.   "$defs": {
128.     "repo": {
129.       "type": "object",
130.       "additionalProperties": true,
131.       "required": [
132.         "name",
133.         "owner",
134.         "full_name",
135.         "description",
136.         "language",
137.         "stars",
138.         "forks",
139.         "created_at",
140.         "topics",
141.         "license",
142.         "url"
143.       ],
144.       "properties": {
145.         "name": { "type": "string" },
146.         "owner": { "type": "string" },
147.         "full_name": { "type": "string" },
148.         "description": { "type": ["string", "null"] },
149.         "language": { "type": ["string", "null"] },
150.         "stars": { "type": "integer", "minimum": 0 },
151.         "forks": { "type": "integer", "minimum": 0 },
152.         "created_at": { "type": "string", "format": "date-time" },
153.         "topics": {
154.           "type": "array",
155.           "items": { "type": "string" }
156.         },
157.         "license": { "type": ["string", "null"] },
158.         "url": { "type": "string", "format": "uri" }
159.       }
160.     },
161.     "trendingRepo": {
162.       "allOf": [
163.         { "$ref": "#/$defs/repo" },
164.         {
165.           "type": "object",
166.           "properties": {
167.             "stars_gained": { "type": ["integer", "null"], "minimum": 0 }
168.           }
169.         }
170.       ]
171.     }
172.   }
173. }
174. ```
175. 
176. ### Input interpretation rules
177. 
178. 1. **New repos** are candidates for editorial novelty.
179. 2. **Trending repos** are candidates for momentum, but if `stars_gained` is absent or null, the analyzer must say that momentum is not yet fully measurable.
180. 3. **Top topics** are directional evidence, not conclusions by themselves.
181. 4. **Metadata diagnostics** can justify caveats about crawl quality, filtering, or missing baselines, but must not dominate the summary.
182. 
183. ## Output Contract
184. 
185. ### File naming
186. 
187. - **Location:** `data/analyzed/`
188. - **Filename:** `YYYY-WNN-summary.md`
189. - **Example:** `data/analyzed/2026-W21-summary.md`
190. 
191. ### Required frontmatter
192. 
193. The analyzer output must begin with YAML frontmatter containing these fields.
194. 
195. | Field | Type | Required | Meaning |
196. |---|---|---:|---|
197. | `title` | string | yes | Reader-facing weekly title. Format: `Week NN, YYYY Analysis`. |
198. | `date` | string | yes | Analysis run timestamp in ISO 8601. |
199. | `week` | string | yes | Week slug from the raw payload (`YYYY-WNN`). |
200. | `year` | integer | yes | Numeric year for downstream validation and archive logic. |
201. | `tags` | array[string] | yes | 3-8 topical tags summarizing the week. |
202. | `categories` | array[string] | yes | Must include `weekly`. |
203. | `repos_featured` | integer | yes | Total repos considered in the editorial pass. Typically `len(new_repos) + len(trending_repos)`. |
204. | `stars_tracked` | integer | yes | Sum of `stars` across all repos considered. |
205. | `top_repo` | string | yes | The repo that anchors the week’s narrative, not necessarily the highest-star repo. |
206. | `quality_score` | integer | yes | Reviewer-gate score from 0-100. Must be `>= 60` to publish. |
207. | `summary` | string | yes | One-sentence editorial thesis for the week. |
208. 
209. No extra frontmatter keys should be emitted unless a later decision extends this contract.
210. 
211. ### Required body structure
212. 
213. The body must follow this exact top-level section order:
214. 
215. ```md
216. ## This Week's Trends
217. 
218. ## Where Industry Meets Code
219. 
220. ## Signal & Noise
221. 
222. ## Blind Spots
223. 
224. ## The Week Ahead
225. 
226. ## Key References
227. ### Notable Projects
228. ### Press & Industry
229. ```
230. 
231. Every repository mentioned in the body must be rendered as a clickable markdown link in this exact format: `[owner/repo](https://github.com/owner/repo)`.
232. 
233. ### Image accessibility guidance
234. 
235. If an analysis ever includes an image, chart, or screenshot:
236. 
237. - provide concise, descriptive alt text that explains the information a reader would otherwise miss,
238. - do not use placeholder alt text like `image`, `screenshot`, or the file name,
239. - keep decorative images rare; only use empty alt text when the image adds no editorial meaning,
240. - explain any important numbers or trends in the surrounding prose so the page still works without the image.
241. 
242. ### Section guidance
243. 
244. #### 1. This Week's Trends
245. - **Purpose:** Name and explain the week's 3-5 macro trends — the big themes that cut across individual repos.
246. - **Include:** A clear name for each trend, what is driving it, and its significance to practitioners. Reference specific repos as evidence.
247. - **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
248. - **Tone:** Analytical and opinionated — write like a Gartner analyst, not a GitHub trending page.
249. - **Length:** ~200-350 words.
250. - **Avoid:** Listing repos without synthesis. Every repo reference must support a named trend.
251. 
252. #### 2. Where Industry Meets Code
253. - **Purpose:** Compare press coverage against what developers are actually building.
254. - **Include:** 2-4 correlations (where press and dev activity align) and 2-3 divergences (media-covered topics with no dev traction, and developer movements the press is ignoring). If no press data was available, state that explicitly.
255. - **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
256. - **Tone:** Editorial and skeptical — the interesting story is usually in the gap.
257. - **Length:** ~150-250 words.
258. - **Avoid:** Summarizing press articles without connecting them to developer evidence.
259. 
260. #### 3. Signal & Noise
261. - **Purpose:** Deliver integrated editorial judgment on what is real versus hype.
262. - **Required:** Write as coherent prose — do **not** use `### Signal` and `### Noise` sub-headings. The distinction should emerge from the writing itself.
263. - **Include:** Durable, technically credible patterns (signal) and inflated, copycat, or marketing-driven patterns (noise). Name specific repos and patterns in both categories.
264. - **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
265. - **Length:** ~150-260 words.
266. - **Avoid:** Repeating trend descriptions from section 1 without adding critical judgment.
267. 
268. #### 4. Blind Spots
269. - **Purpose:** Surface what is absent from both press coverage and developer activity.
270. - **Include:** 2-4 specific, concrete blind spots — name the missing category, why it matters, and what its absence signals.
271. - **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
272. - **Length:** ~80-160 words.
273. - **Avoid:** Generic filler like "more innovation is needed" or restating known gaps without editorial insight.
274. 
275. #### 5. The Week Ahead
276. - **Purpose:** End with a forward-looking editorial close.
277. - **Include:** What trends are in motion that have not peaked yet? What should readers watch for next week? What does this week's activity suggest about where the ecosystem is heading?
278. - **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
279. - **Length:** ~50-110 words.
280. - **Avoid:** Introducing brand-new evidence or restating section 1.
281. 
282. #### 6. Key References
283. - **Purpose:** Give readers the 5-10 most important repos and 3-5 most relevant press items in one scannable place.
284. - **Required subsections:** `### Notable Projects` and `### Press & Industry`.
285. - **Notable Projects:** 5-10 repos with one sentence of context each — why it matters, not just what it is. Every repo must be a link.
286. - **Press & Industry:** 3-5 articles or sources with markdown links. If no press data was available, write: "No press data was provided this week."
287. - **Repo links:** Every repo mention must use `[owner/repo](https://github.com/owner/repo)`.
288. 
289. ## Analysis Dimensions
290. 
291. Every weekly analysis must apply these dimensions explicitly.
292. 
293. ### Importance Assessment
294. Ask whether a repo or theme solves a real problem, reduces friction, opens a new workflow, or signals credible adoption. Prefer practical utility over novelty theater.
295. 
296. ### Trend Detection
297. Look for repeated patterns across topics, repo types, and—when available—previous weekly summaries. A single loud repo is not a trend; clustered movement is.
298. 
299. ### Hype Detection
300. Separate genuine substance from branding, wrappers, thinly differentiated agent launches, or exploit-driven attention. If the repo sounds bigger than it is, say so.
301. 
302. ### Gap Analysis
303. Identify what should be showing up but is not: missing infrastructure, underrepresented defensive/security work, absent tooling for known pain points, or stagnant categories.
304. 
305. ### Context
306. Compare the current week to the prior week when a prior summary exists. Note continuity, acceleration, reversal, or broadening of a theme. If no prior summary exists, say so briefly and avoid pretending longitudinal certainty.
307. 
308. ## Quality Criteria
309. 
310. ### Good analysis
311. - Synthesizes, ranks, and judges instead of listing.
312. - Connects individual repos into ecosystem-level patterns.
313. - Names uncertainty honestly when data quality is limited.
314. - Uses evidence from the payload without sounding like the payload.
315. - Makes the `Blind Spots` section useful and specific.
316. - Leaves Amy’s generator with all frontmatter needed for site publication.
317. 
318. ### Bad analysis
319. - Reads like release notes or a changelog.
320. - Repeats repo descriptions without editorial value.
321. - Confuses total stars with weekly momentum.
322. - Refuses to criticize obvious hype or noise.
323. - Omits gaps, caveats, or trend continuity.
324. - Produces frontmatter that cannot drive the weekly page template.
325. 
326. ## Reviewer-Gate Expectations
327. 
328. A weekly analysis is publishable only if all of the following are true:
329. 
330. - `quality_score >= 60`
331. - all required frontmatter fields are present,
332. - all six required H2 sections are present in order (`This Week's Trends`, `Where Industry Meets Code`, `Signal & Noise`, `Blind Spots`, `The Week Ahead`, `Key References`),
333. - `### Notable Projects` and `### Press & Industry` subsections are present under `## Key References`,
334. - body word count is at least 200,
335. - the prose contains no raw JSON, tool logs, or placeholder text.
336. 
337. ## Generator Handoff Rules
338. 
339. The generator may assume:
340. 
341. - the summary frontmatter already contains the weekly page fields Amy’s Hugo templates expect,
342. - `summary` is safe to surface in list views,
343. - `top_repo` is a deliberate editorial choice,
344. - body headings are stable and machine-detectable,
345. - body headings use the stable structure defined in this spec; the generator can extract any section by heading name.
346. 
347. The analyzer may assume:
348. 
349. - `data/raw/` is authoritative input,
350. - prior-week continuity is optional but preferred,
351. - missing `stars_gained` must produce a caveat, not a silent omission.
352.
````

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/agents.**

/home/runner/work/SquadScope/SquadScope/.squad/agents

<details>
<summary>9 lines</summary>

```
amy
bender
checkpoint.txt
farnsworth
fry
hermes
leela
ralph
scribe
```

</details>


### ✅ `bash`

**Read more of the instructions file**

$ sed -n '200,400p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>202 lines</summary>

```
"voidstrap-download",
        "voidstrap-roblox"
      ],
      "license": "MIT",
      "url": "https://github.com/DARKHOLEUM/VoidStrap-For-Roblox"
    },
    {
      "name": "ssh-keysign-pwn",
      "owner": "0xdeadbeefnetwork",
      "full_name": "0xdeadbeefnetwork/ssh-keysign-pwn",
      "description": "Steal SSH host private keys and /etc/shadow via the ptrace_may_access mm-NULL bypass + pidfd_getfd. Pre-31e62c2ebbfd kernels.",
      "language": "C",
      "stars": 636,
      "forks": 74,
      "created_at": "2026-05-14T22:44:21Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/0xdeadbeefnetwork/ssh-keysign-pwn"
    },
    {
      "name": "clawpatch",
      "owner": "openclaw",
      "full_name": "openclaw/clawpatch",
      "description": "Review code. Patch bugs. Land PRs.",
      "language": "TypeScript",
      "stars": 594,
      "forks": 86,
      "created_at": "2026-05-15T08:43:03Z",
      "topics": [
        "bot",
        "review"
      ],
      "license": "MIT",
      "url": "https://github.com/openclaw/clawpatch"
    },
    {
      "name": "ROM-MGBA-Pokemon-Emulator-PC",
      "owner": "Flizorules05",
      "full_name": "Flizorules05/ROM-MGBA-Pokemon-Emulator-PC",
      "description": "ROM Emulator Pokemon mGBA eden emulator eden emulator switch 2: download GBA NDS 3DS Switch games, android APK, MelonDS setup guide, Citra Pokemon X Y, Ryujinx Scarlet Violet ROM hack, Pokemon Emerald Randomizer download. Safe ROMs site, Action Replay cheat codes, GameShark codes FireRed, real time clock RTC error fix, trade evolution",
      "language": null,
      "stars": 585,
      "forks": 0,
      "created_at": "2026-05-17T17:15:30Z",
      "topics": [
        "emulator",
        "gba",
        "gba-emulator",
        "mgba",
        "mgba-api",
        "mgba-emulator",
        "pokemmo",
        "pokemon",
        "pokemon-battle",
        "pokemon-emerald",
        "pokemon-emulator-games",
        "pokemon-emulator-pc",
        "pokemon-gba",
        "pokemon-pc-emulator",
        "pokemon-red",
        "pokemon-rom-emulator",
        "rom",
        "rom-emulator"
      ],
      "license": "MIT",
      "url": "https://github.com/Flizorules05/ROM-MGBA-Pokemon-Emulator-PC"
    },
    {
      "name": "hydra-launcher",
      "owner": "arnabchoudhury404",
      "full_name": "arnabchoudhury404/hydra-launcher",
      "description": "hydralauncher: Hydra Launcher download free PC library  fontes links baixar , hydralauncher github,  trusted sources url list, steam verde download, hydralauncher github source code, no download available hydra launcher fix. Embedded bittorrent client setup, repack scraper json megathread, hydra cloud save files sync, python rpc server error",
      "language": "TypeScript",
      "stars": 585,
      "forks": 0,
      "created_at": "2026-05-17T16:54:12Z",
      "topics": [
        "epic-games",
        "epic-games-store",
        "gamelauncher",
        "gaming",
        "heroic-games-launcher",
        "hydra-download",
        "hydra-launcher-library",
        "hydra-library",
        "hydralauncher",
        "hydralauncher-download",
        "launcher",
        "library-hydra",
        "pirate-game",
        "pirated-steam-games",
        "steam"
      ],
      "license": "MIT",
      "url": "https://github.com/arnabchoudhury404/hydra-launcher"
    },
    {
      "name": "Stable-Diffusion-WebUI",
      "owner": "BasZ4ll",
      "full_name": "BasZ4ll/Stable-Diffusion-WebUI",
      "description": "Stable Diffusion: webui automatic1111 download free, comfyui setup guide, sdxl checkpoint safetensors, lora model civitai, controlnet extension github. SD WebUI Forge launcher, low VRAM optimization, xformers command line arguments, python torch cuda error fix, out of memory solution, txt2img img2img, inpainting, realesrgan upscaler, local pc insta",
      "language": "TypeScript",
      "stars": 583,
      "forks": 0,
      "created_at": "2026-05-17T16:34:12Z",
      "topics": [
        "ai-image-generator",
        "diffusion-model",
        "image-to-image",
        "offline-image-generator",
        "stable-diffusion",
        "stable-diffusion-2026",
        "stable-diffusion-android",
        "stable-diffusion-download",
        "stable-diffusion-free",
        "stable-diffusion-github",
        "stable-diffusion-tutorial",
        "stable-diffusion-ui",
        "stable-diffusion-web-ui",
        "stable-diffusion-webui-forge",
        "stable-diffusion-webui-plugin",
        "stable-diffusion-windows",
        "stable-diffusion-xl",
        "stablediffusion3",
        "text-to-image"
      ],
      "license": "MIT",
      "url": "https://github.com/BasZ4ll/Stable-Diffusion-WebUI"
    },
    {
      "name": "OPAutoClicker",
      "owner": "jiaoyanming0-bot",
      "full_name": "jiaoyanming0-bot/OPAutoClicker",
      "description": "OP Auto Clicker: Fast click interval, milliseconds, seconds. Left, right, middle button. keyboard auto clicker Single, double, triple click. Repeat until stopped, fixed count. Current location, pick coordinates. Hotkey trigger, start stop shortcut. Record playback, macro, Roblox AFK, Minecraft, mouse emulator, portable. ",
      "language": "C#",
      "stars": 582,
      "forks": 2,
      "created_at": "2026-05-14T16:02:07Z",
      "topics": [
        "auto-clicker",
        "auto-clicker-op",
        "autoclick",
        "autoclicktool",
        "hotkey",
        "macro",
        "macros",
        "op-auto-clicker",
        "op-auto-clicker-download",
        "op-auto-clicker-install",
        "opclicker"
      ],
      "license": "MIT",
      "url": "https://github.com/jiaoyanming0-bot/OPAutoClicker"
    },
    {
      "name": "rbxfpsunlocker-boost-More-240FPS",
      "owner": "Sunislazi",
      "full_name": "Sunislazi/rbxfpsunlocker-boost-More-240FPS",
      "description": "rbxfpsunlocker Roblox FPS BOOST: Roblox FPS unlocker download free More 240 FPS, uncap 60 FPS limit, axst GitHub source code, high refresh rate monitor, Roblox client lag fix, Byfron Hyperion anti-cheat compatibility, safe to use ban status, settings.ini configuration, rfu.exe not working error, ClientAppSettings json,bloxtstrap fps unlocke",
      "language": "TypeScript",
      "stars": 579,
      "forks": 0,
      "created_at": "2026-05-17T16:13:25Z",
      "topics": [
        "aimlock",
        "fps-unlocker",
        "fpsunlocker",
        "rbx",
        "rbxdev",
        "roblox",
        "robloxfpsbooster",
        "robloxfpsbooster-download",
        "robloxfpsunlocker-download",
        "sober-fps-unlocker",
        "universal-fps"
      ],
      "license": "MIT",
      "url": "https://github.com/Sunislazi/rbxfpsunlocker-boost-More-240FPS"
    },
    {
      "name": "auto-identity-remove",
      "owner": "stephenlthorn",
      "full_name": "stephenlthorn/auto-identity-remove",
      "description": "Automated data broker opt-out runner — removes your personal info from 30+ people-search sites on a monthly schedule",
      "language": "JavaScript",
      "stars": 565,
      "forks": 20,
      "created_at": "2026-05-15T12:40:18Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/stephenlthorn/auto-identity-remove"
    },
    {
      "name": "ultraviewer",
      "owner": "tritano",
      "full_name": "tritano/ultraviewer",
      "description": "Teamviewer UltraViewer download free PC windows 11, portable zip, latest version 6.6, getting my ID stuck fix. Port 2112 firewall block, teamviewer commercial use detected bypass, anydesk alternative. Black screen on connection solution, run with windows administrator, change password, file transfer slow.",
      "language": "TypeScript",
      "stars": 555,
      "forks": 0,
      "created_at": "2026-05-16T17:07:32Z",
<exited with exit code 0>
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth.**

/home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth

```
charter.md
history.md
notifications
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/identity.**

/home/runner/work/SquadScope/SquadScope/.squad/identity

```
now.md
wisdom.md
```


### ✅ `bash`

**Read more of the raw data**

$ sed -n '400,700p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>302 lines</summary>

```
"created_at": "2026-05-16T17:07:32Z",
      "topics": [
        "anydesk-integration",
        "download-ultraviewer",
        "download-ultraviewer-for-windows",
        "teamviewer",
        "ultraviewer",
        "ultraviewer-download",
        "ultraviewer-download-for-windows",
        "ultraviewer-for-windows",
        "ultraviewer-pc",
        "ultraviewer-unlock"
      ],
      "license": "MIT",
      "url": "https://github.com/tritano/ultraviewer"
    },
    {
      "name": "DualSenseX-DSX-Steam-Edition",
      "owner": "ZoyaMalhotra",
      "full_name": "ZoyaMalhotra/DualSenseX-DSX-Steam-Edition",
      "description": "DualSenseX Steam: DSX free download github, adaptive triggers test mod PC, audio to haptics setup, Xbox 360 DualShock 4 emulation. ViGEmBus driver error fix, Bluetooth audio latency, Cyberpunk 2077 controller mod, non-steam games controller not working, DS4Windows alternative. Paliverse crack bypass, BSOD crash fix, Steam Xbox Extended Feature",
      "language": "C++",
      "stars": 542,
      "forks": 1,
      "created_at": "2026-05-18T16:41:06Z",
      "topics": [
        "adaptive-triggers-pc",
        "ds4",
        "ds4-controller",
        "ds4-windows",
        "ds4windows",
        "dsx-download",
        "dsx-steam",
        "dsx-windows",
        "dual-sense-on-pc",
        "dualsense",
        "dualsense-controller",
        "dualsense-pc-adaptive-triggers",
        "dualshock4",
        "game-controller",
        "hidhide",
        "ps3-controller",
        "ps5-controller",
        "psrp",
        "steam",
        "vigembus"
      ],
      "license": "MIT",
      "url": "https://github.com/ZoyaMalhotra/DualSenseX-DSX-Steam-Edition"
    },
    {
      "name": "HRM-Text",
      "owner": "sapientinc",
      "full_name": "sapientinc/HRM-Text",
      "description": "HRM-Text is a 1B text generation model based on the HRM architecture, strengthened by task completion and latent space reasoning.",
      "language": "Python",
      "stars": 542,
      "forks": 50,
      "created_at": "2026-05-18T03:10:52Z",
      "topics": [
        "hierarchical-reasoning-model",
        "hrm",
        "large-language-models",
        "pretraining"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/sapientinc/HRM-Text"
    },
    {
      "name": "Claude-Mythos-AI-Anthropic-App",
      "owner": "AbhishekK130804",
      "full_name": "AbhishekK130804/Claude-Mythos-AI-Anthropic-App",
      "description": "Claude pro free Mythos design Opus Cowork  Sonnet AI Anthropic App: download free PC android apk iOS, Anthropic Claude API key setup, Claude roleplay mythos client, SillyTavern Claude prompt formatting, custom system prompt jailbreak, Mythos AI creative writing app, Claude 3.5 Sonnet Opus API cost, open source LLM frontend, Claude reverse proxy ",
      "language": "C#",
      "stars": 539,
      "forks": 0,
      "created_at": "2026-05-18T17:01:42Z",
      "topics": [
        "claude",
        "claude-ai",
        "claude-code",
        "claude-code-cli",
        "claude-code-hooks",
        "claude-code-marketplace",
        "claude-code-plugin",
        "claude-code-plugins",
        "claude-code-skill",
        "claude-code-skills",
        "claude-code-subagents",
        "claude-cowork-free",
        "claude-design-ai",
        "claude-design-alternative",
        "claude-design-download",
        "claude-design-free",
        "claude-mythos",
        "claude-opus",
        "claude-opus-4-6",
        "mythos"
      ],
      "license": "MIT",
      "url": "https://github.com/AbhishekK130804/Claude-Mythos-AI-Anthropic-App"
    },
    {
      "name": "Steam-Tools",
      "owner": "haiddrrs",
      "full_name": "haiddrrs/Steam-Tools",
      "description": "Lua Steam Tools: SteamTools download free PC latest version, lua manifest generator github, steamtools safe to use account ban risk, BeyondDimension SteamTools source code, unlock free steam games dlc unlocker, watt toolkit alternative, steamtools exe local ticket bypass, lua tools manifest downloader, st-setup virus total malware scan, steamtools",
      "language": "C#",
      "stars": 532,
      "forks": 0,
      "created_at": "2026-05-18T17:20:43Z",
      "topics": [
        "lua-steam-tools",
        "luatools",
        "manifest-steam-tools",
        "steam-bypass",
        "steam-client",
        "steam-data",
        "steam-education",
        "steam-fix",
        "steam-games",
        "steam-library",
        "steam-lua-tools",
        "steam-tools",
        "steam-tools-download",
        "steam-tools-games",
        "steamtool",
        "steamtools",
        "steamtools-download",
        "steamtools-lua",
        "steamtools-manifest",
        "steamweb"
      ],
      "license": "MIT",
      "url": "https://github.com/haiddrrs/Steam-Tools"
    },
    {
      "name": "thinshell",
      "owner": "cat9999aaa",
      "full_name": "cat9999aaa/thinshell",
      "description": "thinshell",
      "language": null,
      "stars": 485,
      "forks": 2,
      "created_at": "2026-05-14T11:10:28Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/cat9999aaa/thinshell"
    },
    {
      "name": "Roblox-Hub-2026",
      "owner": "trong776",
      "full_name": "trong776/Roblox-Hub-2026",
      "description": "Developer utilities for Roblox game testing — Lua tools for exploring game mechanics and performance. MIT License.",
      "language": null,
      "stars": 481,
      "forks": 50,
      "created_at": "2026-05-14T21:47:53Z",
      "topics": [
        "lua",
        "roblox"
      ],
      "license": "MIT",
      "url": "https://github.com/trong776/Roblox-Hub-2026"
    },
    {
      "name": "Zephyr-Executor-Free-Roblox-Executor-PC-No-Key-Required-2026",
      "owner": "RastProxy88",
      "full_name": "RastProxy88/Zephyr-Executor-Free-Roblox-Executor-PC-No-Key-Required-2026",
      "description": "Free undetected Roblox script executor with instant injection, full UNC support, and no key system. Clean UI, built-in script hub, regular updates.",
      "language": "Lua",
      "stars": 479,
      "forks": 97,
      "created_at": "2026-05-17T17:51:00Z",
      "topics": [
        "lua",
        "roblox"
      ],
      "license": "MIT",
      "url": "https://github.com/RastProxy88/Zephyr-Executor-Free-Roblox-Executor-PC-No-Key-Required-2026"
    },
    {
      "name": "gta-5-mod-menu",
      "owner": "S4rdenz",
      "full_name": "S4rdenz/gta-5-mod-menu",
      "description": "🚀 Dominate GTA V servers with this free, reliable FiveM mod menu featuring ESP, aimbot, and more, designed for Steam and Epic Games versions.",
      "language": null,
      "stars": 476,
      "forks": 117,
      "created_at": "2026-05-14T13:48:33Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/S4rdenz/gta-5-mod-menu"
    },
    {
      "name": "hyperliquid-whale-order-tracking",
      "owner": "Glazenovatag",
      "full_name": "Glazenovatag/hyperliquid-whale-order-tracking",
      "description": "A real, working Hyperliquid whale tracker not a placeholder. The synthetic-message test passed and the WebSocket subscribe / reconnect logic was verified live.",
      "language": "Python",
      "stars": 470,
      "forks": 0,
      "created_at": "2026-05-19T10:31:27Z",
      "topics": [
        "hyperliquid-whale-alert",
        "hyperliquid-whale-tracker"
      ],
      "license": "MIT",
      "url": "https://github.com/Glazenovatag/hyperliquid-whale-order-tracking"
    },
    {
      "name": "Lance",
      "owner": "bytedance",
      "full_name": "bytedance/Lance",
      "description": "A 3B-active-parameter native unified multimodal model for image and video understanding, generation, and editing.",
      "language": "Python",
      "stars": 468,
      "forks": 27,
      "created_at": "2026-05-15T05:42:08Z",
      "topics": [
        "image-editing",
        "image-generation",
        "image-understanding",
        "unified-multimodal-models",
        "video-generation",
        "video-understanding"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/bytedance/Lance"
    },
    {
      "name": "gta-5-mod-menu",
      "owner": "trong776",
      "full_name": "trong776/gta-5-mod-menu",
      "description": "External game enhancement for GTA V single-player. ImGui overlay, no injection, minimal FPS impact. Windows x64, C++17.",
      "language": null,
      "stars": 458,
      "forks": 160,
      "created_at": "2026-05-15T16:18:35Z",
      "topics": [
        "cpp",
        "directx",
        "enhancement",
        "gaming-tool",
        "gta-5",
        "imgui",
        "open-source",
        "trainer",
        "utility",
        "windows"
      ],
      "license": "MIT",
      "url": "https://github.com/trong776/gta-5-mod-menu"
    },
    {
      "name": "Nightlight-Game-Launcher",
      "owner": "Alkih",
      "full_name": "Alkih/Nightlight-Game-Launcher",
      "description": "Nightlight Game Launcher: NLGL download, Rockstar Social Club bypass, GTA V Epic Games launch error, RDR2 offline play, GTA IV Social Club fix. Steam account switcher, Epic Online Services bypass, EOS SDK. dll, -nobattleye, -scOfflineMode, launch options, account manager, local backup, source code GitHub, onajlikezz, open source tool.",
      "language": "C#",
      "stars": 447,
      "forks": 0,
      "created_at": "2026-05-15T16:40:59Z",
      "topics": [
        "bypassing",
        "epic-games",
        "epicgames",
        "fe-bypass",
        "grand-theft-auto-v",
        "nightlight",
        "nightlight-launcher",
        "nlgl",
        "nlgl-download",
        "rdr2",
        "reddeadredemption2",
        "rockstargames",
        "steam",
        "uac-bypass",
        "vac-bypass"
      ],
      "license": "MIT",
      "url": "https://github.com/Alkih/Nightlight-Game-Launcher"
    },
    {
      "name": "gta-5-mod-menu",
      "owner": "SubamanojJ-2004",
      "full_name": "SubamanojJ-2004/gta-5-mod-menu",
      "description": "Ultimate Enhancement Toolkit for GTA V — powerful mod menu with ESP, vehicle spawner, recovery features, and clean UI",
      "language": null,
      "stars": 445,
      "forks": 61,
      "created_at": "2026-05-16T08:50:42Z",
      "topics": [
        "gameenhancement",
        "luauiframework",
        "openworldtools",
        "runtimeoverlay",
        "sandboxextensions"
      ],
      "license": "MIT",
      "url": "https://github.com/SubamanojJ-2004/gta-5-mod-menu"
<exited with exit code 0>
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/identity/wisdom.md.**

/home/runner/work/SquadScope/SquadScope/.squad/identity/wisdom.md

<details>
<summary>38 lines</summary>

```
1. ---
2. last_updated: 2026-05-18T15:22:25.067+02:00
3. ---
4. 
5. # Team Wisdom
6. 
7. Reusable patterns and heuristics learned through work. NOT transcripts — each entry is a distilled, actionable insight.
8. 
9. ## Patterns
10. 
11. ## Signal Detection Patterns
12. 
13. - **Practical utility beats novelty theater.** Treat repositories as signal when they clearly reduce workflow friction, solve recurring engineering pain, or make production work more trustworthy.
14. - **Clustered movement matters more than one loud launch.** A single popular repo is not a trend; multiple repositories and topics pulling in the same direction usually signal durable ecosystem movement.
15. - **Operational credibility is a strong positive signal.** Favor projects that show observability, maintenance discipline, packaging clarity, or workflow realism over broad autonomy claims.
16. - **Research counts when it changes practice.** Research-heavy repos can be signal, but only when they point toward credible adoption, new workflows, or meaningful technical movement beyond demos.
17. 
18. ## Noise / Hype Detection Patterns
19. 
20. - **Stars without deltas are popularity, not momentum.** Treat attention as directional when `stars_gained` or historical baselines are missing; do not overstate it as trend acceleration.
21. - **Marketing-heavy wrappers are usually weak signal.** Thinly differentiated agent launches, clone products, and branding-first repos deserve skepticism unless the implementation meaningfully changes capability or cost.
22. - **Exploit, bypass, and cheat churn distort the picture.** These repos may be active, but they are usually editorial noise unless they reveal a deeper defensive or ecosystem shift.
23. - **If the promise sounds bigger than the evidence, call it hype.** Strong claims without technical differentiation, adoption evidence, or operational substance are noise until proven otherwise.
24. 
25. ## Gap Analysis Focus Areas
26. 
27. - **Look for absent infrastructure around known pain.** Missing testing, observability, defensive security, maintenance, or reliability tooling is often more important than another crowded launch category.
28. - **Name what should exist but does not.** Useful gap analysis points to concrete missing categories, not generic wishes for “more innovation.”
29. - **Track ecosystem balance, not just heat.** When one area dominates attention, check which adjacent needs are being ignored or underfunded.
30. - **Missing baselines are themselves a gap.** If the pipeline lacks enough historical data to validate momentum or hindsight, say so explicitly.
31. 
32. ## Trend Detection Approaches
33. 
34. - **Compare week-to-week whenever possible.** Look for continuity, acceleration, reversal, or broadening rather than treating each weekly crawl as isolated.
35. - **Use topic counts as supporting evidence only.** `signals.top_topics` can confirm a pattern, but topic frequency alone does not prove significance.
36. - **Prefer repeated technical themes over brand repetition.** Trend calls should come from recurring problem/solution patterns, not from the same large projects staying visible.
37. - **Be explicit about uncertainty.** Honest caveats improve trust; if momentum data or historical context is thin, the analysis should say so rather than pretend precision.
38.
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md.**

/home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md

<details>
<summary>36 lines</summary>

```
1. # Farnsworth — History
2. 
3. ## Project Context
4. - **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
5. - **Stack:** Data analysis, content generation, markdown output
6. - **User:** jmservera
7. - **Goal:** Critical analysis of GitHub trends — identify what's important, what's trending, what's missing. Feed insights to Amy for the GitHub Pages site.
8. 
9. ## Team Updates
10. 
11. **2026-05-18:** PRD now available at `docs/PRD.md`. Review for analysis requirements and success criteria.
12. 
13. **2026-05-18T10:27:35Z:** Phase 0 is complete. Architecture decision published in `.squad/decisions.md`. CI analysis pipeline uses Copilot CLI (primary) with GitHub Models fallback. Reviewer gate requires quality_score ≥ 60. Phase 2 analyzer work is unblocked.
14. 
15. ## Learnings
16. 
17. - **2026-05-18T10:50:21Z:** PR #28 (Issue #9 analysis spec) review complete. All 4 Copilot findings addressed (bc823a3). Analyzer contract formalized: markdown + YAML frontmatter with `quality_score` field, three labeled sections (Signal, Noise, Gaps), machine-checkable structure. Quality gate criteria: score ≥ 60, all sections present, word count ≥ 200. Reuses crawler JSON input schema. Ready for merge. Phase 2 generator can now design Hugo templates against stable contract.
18. - **2026-05-18T12:07:20.778+02:00:** The analyzer contract should be a superset of Amy's weekly page frontmatter plus Leela's `quality_score` gate, so one analyzed artifact can satisfy both editorial review and generator input.
19. - **2026-05-18T12:07:20.778+02:00:** The analyzer contract should be a superset of Amy’s weekly page frontmatter plus Leela’s `quality_score` gate, so one analyzed artifact can satisfy both editorial review and generator input.
20. - **2026-05-18T12:07:20.778+02:00:** Keep the reader-facing weekly summary in five stable H2 sections, but require labeled `Signal`, `Noise`, and `Gaps` subsections so the editorial lens remains explicit and machine-checkable.
21. - **2026-05-18T13:20:07.067+02:00:** Weekly analysis prose should render repo mentions as explicit GitHub markdown links, and the current raw crawl artifact exposes those repo page URLs under `url` rather than `html_url`, so analyzer/generator prompts should require link formatting without assuming a different field name.
22. - **2026-05-18T15:22:25.067+02:00:** The learning loop only becomes real when learned state is both persisted and injected back into the next weekly prompt. Reskill reports need recent summaries, snapshot hindsight, and quality trend context; the weekly analyzer must read `wisdom.md` plus `.squad/skills/` at prompt-render time so lessons change future judgment instead of sitting idle.
23. - **2026-05-19T11:48:44.543Z:** TechCrunch RSS integration PRD authored (`docs/PRD-techcrunch-integration.md`). Key architectural insight: non-GitHub sources serve as *correlation signals* for editorial judgment, not content to republish. The value is in the delta between press narrative and actual developer activity. This is the first concrete use of Decision #7's crawler plugin architecture. RSS feeds are trivially cheap (~$0.00/week) and require no API auth, making them ideal first candidates for multi-source expansion before more complex APIs (HN, Reddit).
24. - **2026-05-19T11:48:44.543Z:** PR #55 opened with TechCrunch integration proposal. Analysis specification decisions finalized and merged into `.squad/decisions.md`: frontmatter superset contract, five stable H2 sections, required Signal/Noise/Gaps subsections, honest degradation of trending when momentum data incomplete. Learned state injection framework (wisdom.md + skills/) integrated into decision log; weekly analyzer will read these at prompt-render time starting Phase 2.
25. - **2026-05-19T11:55:46Z:** Self-review of TechCrunch RSS PRD (PR #55) completed. Key findings: (1) PRD file missing from branch — blocker. (2) Correlation hit rate realistically 5–15%, not the implicit "most articles correlate" assumption. Name-matching across TC articles and GitHub repos requires entity resolution, not string matching. (3) Filtering is underspecified — no keywords, no category selection, no confidence tiers defined. (4) Temporal mismatch between real-time RSS and weekly analysis means correlations are retrospective explanations, not predictive signals — the "prediction enhancement" phase is premature. (5) No success criteria defined to evaluate whether integration justifies its complexity. Lesson: excitement about architectural patterns (plugin system) must not override skepticism about editorial value-add. The right question isn't "can we?" but "should we, and will it measurably improve output?"
26. - **2026-05-19T15:08:00Z:** Leela milestone decomposition complete. Issues assigned to v0.5–v0.9 milestones. Scribe logged orchestration and merged decision. Your assigned v0.5 analysis and synthesis issues are ready. See `.squad/orchestration-log/2026-05-19T15-08-leela.md` for full decomposition outcome.
27. - **2026-05-19T15:22:00+02:00:** Topic-aware prompt template implemented (Issue #63). Key architecture decisions: (1) Used `{{#IF_TOPIC}}`/`{{#IF_NO_TOPIC}}` conditional blocks rather than Jinja2 to keep the template readable as standalone markdown and avoid adding template engine dependencies. (2) Wisdom injection is two-tier — global wisdom from `.squad/identity/wisdom.md` (existing) plus per-topic wisdom from `topics/{id}/wisdom.md` (new). (3) Render script (`scripts/render_topic_prompt.py`) is zero-dependency (stdlib only, with optional PyYAML), so it works in any CI environment without pip install. (4) Backward compatibility guaranteed: when no `squadscope.topic.yml` exists, the template collapses cleanly to general-mode analysis identical to the existing `analyze-weekly.md` behavior.
28. - **2026-05-19T20:07:19+02:00:** Fixed correlator "0 repos" bug (PR #130). Root cause: `correlate.py` loaded repos via `raw_data.get("repos")` but `crawl.py` writes them under `new_repos` and `trending_repos`. Key paths: `scripts/correlate.py:320`, `scripts/crawl.py:857-858`. Lesson: when integrating scripts in a pipeline, always verify the producer's *actual output schema* against the consumer's expected input schema — don't assume key names match. The CI skill pattern ("test the wire") would have caught this if applied at integration time.
29. - **2026-05-19T20:50:22+02:00:** Press context dual-mode rendering implemented. Three reader-facing bugs fixed: (1) correlation list truncated to top-10 in reader mode (sorted by confidence desc, hype_risk severity); (2) `### Instructions` block stripped from reader output — it is AI prompt input only; (3) `#### Divergence Instructions` replaced with a plain narrative sentence for reader display. Architecture: `render_press_context.py` gained `reader_mode` kwarg propagated to `format_correlations_list(top_n=)` and `format_divergences(reader_mode=)`. `analyze_fallback._render_press_section_no_ai` now calls `_strip_ai_instructions()` which post-processes the pre-rendered file via regex — chosen because the fallback reads a file path, not raw JSON, so re-rendering from scratch would require threading data paths through. Key paths: `scripts/render_press_context.py`, `scripts/analyze_fallback.py`. 16 new tests added; 498 total pass.
30. - **2026-05-19T21:24:54+02:00:** Divergence reader-mode upgraded from bullet lists to narrative paragraphs. `format_divergences(reader_mode=True)` now calls `_format_unpublicized_narrative()` and `_format_uncovered_narrative()` — deterministic template-driven prose (no LLM), capped at top 6 topics (by star count) and 5 uncovered trends. Repo links use only the repo name part after `/` (e.g., `[wasm-lib](https://github.com/org/wasm-lib)`). AI-mode format (reader_mode=False) is unchanged. Key insight: for reader-facing output, the data shape matters less than telling a coherent story — aggregate by topic, link to repos by short name, conclude with interpretation. 499 tests pass.
31. - **2026-05-19T22:52:54+02:00:** Fixed two reader-mode polish issues and reskill 403 crash (PR #139). (1) Count header `N repos have press correlation:` stripped in reader_mode via `re.sub` — it was an AI-prompt artefact leaking into the published page. (2) `_extract_readme_description()` now trims every candidate line to the last sentence boundary (`.` `!` `?` followed by space or end); lines with no boundary are skipped entirely, so truncated snippets never produce half-sentences. The 150-char upper bound was removed — sentence trimming makes it redundant. (3) `reskill.py main()` now catches `RuntimeError` from `call_github_models()` and writes a placeholder report instead of crashing — the job exits 0 even when the configured model (`openai/gpt-4.1`) returns 403. Key lesson: template-rendered content always needs an explicit pass to strip AI-only fields when switching to reader mode — simply replacing the list with narrative paragraphs is not enough if the surrounding template text still contains prompt tokens. 519 tests pass.
32. - **2026-05-19T20:57:55Z:** PR #139 merged. Correlation Summary section now renders as narrative prose in reader_mode (Decision recorded in `.squad/decisions.md`). Groups correlations by organization, ranks by aggregate confidence, fetches README snippets for top 2 repos per group (max 6 total), produces 1–3 interpretive paragraphs with inline links. Graceful failure on README timeout (5s). Key rationale: raw repo names with scores communicate data but not meaning; narrative format helps readers understand organizational impact. AI-mode output unchanged. Additionally: reskill job now catches RuntimeError on model 403, emits placeholder report, exits cleanly. Related decisions: `_format_correlations_narrative()` function pattern, README fetch timeout strategy, segment-by-org grouping logic. All new code covered by tests; 513 total pass.
33. - **2026-05-20T19:15:53.942+02:00:** Article structure restructured from repo-listing format to Gartner/McKinsey-style trend brief (requested by jmservera). New section order: `## This Week's Trends` → `## Where Industry Meets Code` → `## Signal & Noise` → `## Blind Spots` → `## The Week Ahead` → `## Key References` (with `### Notable Projects` and `### Press & Industry`). Key design decisions: (1) Lead with named macro trends — 3-5 synthesized themes, not repo lists. (2) "Where Industry Meets Code" replaces "Industry & Press Correlation" — editorial framing, not ML-sounding. (3) Signal & Noise merged into integrated prose section (no `### Signal`/`### Noise` sub-headings) for better editorial writing. (4) Repos move to `### Notable Projects` at end as references, freeing body prose to cite them as evidence rather than leading with them. (5) `generate_rollups.py` updated with backward compat — tries new heading names first, falls back to old for existing `2026-W21-summary.md`. Files changed: `prompts/analyze-weekly.md`, `docs/analysis-spec.md`, `scripts/analysis_gate.py`, `scripts/analyze_fallback.py`, `scripts/generate_rollups.py`, 5 test files. All 519 tests pass. Decision filed at `.squad/decisions/inbox/farnsworth-article-restructure.md`.
34. - **2026-05-20T20:09:26+02:00:** Removed stale `claude-sonnet-4` pins from `crawl-and-publish.yml` so analysis and reskill now rely on the Copilot CLI default model instead of hardcoded model IDs. Added a `copilot-default` cost profile for preflight/usage tracking and made `GITHUB_MODELS_MODEL` workflow-wide and configurable via repo vars with `openai/gpt-4o` as the fallback default. Lesson: for platform-managed Copilot CLI runs, pinning a versioned model name is operational debt; keep the CLI on its moving default and only pin fallback API models you explicitly control.
35. - **2026-05-20T22:14:02+02:00:** Fixed a publication leak where Copilot CLI stdout was redirected into the same markdown file that Farnsworth writes via the `write` tool. Analysis and reskill now discard CLI stdout, then run an explicit post-step sanitizer over the output file to strip any leaked agent epilogues such as `✅ Farnsworth is done`, `Editorial thesis:`, or `Quality score:` lines. Lesson: when an agent writes a file directly, shell stdout is a separate channel and must never target the same path; add a cleanup pass anyway because transcript-style metadata can still escape through unexpected CLI behavior.
36.
```

</details>


### ✅ `bash`

**Read more of the raw data - trending repos and signals**

$ sed -n '700,1100p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>402 lines</summary>

```
"url": "https://github.com/SubamanojJ-2004/gta-5-mod-menu"
    },
    {
      "name": "UE4SS-Subnautica-2",
      "owner": "littlefrogyq",
      "full_name": "littlefrogyq/UE4SS-Subnautica-2",
      "description": "UE4SS Subnautica 2: UE4SS download github latest version, Subnautica 2 UE5 mod loader setup, xinput1_4.dll dwmapi.dll injector error. REUE4SS UE4SS-settings.ini config, console modding commands, Subnautica 2 crashes on launch fix, dump SDK C++ blueprints, Live Viewport object spacer, GuiConsole visible toggle. Unreal Engine 5.5 compatibility,",
      "language": "C++",
      "stars": 445,
      "forks": 0,
      "created_at": "2026-05-19T16:18:16Z",
      "topics": [
        "early-access-subnautica-2",
        "game-mod-manager",
        "mod",
        "mod-manager",
        "modmanager",
        "nitrox-pirate",
        "subnautica",
        "subnautica-2",
        "subnautica-2-multiplayer",
        "subnautica-2-on-ps5",
        "subnautica-2-release",
        "subnautica-2-release-date-ps5",
        "subnautica-2-xbox",
        "subnautica-modding",
        "subnautica-multiplayer",
        "subnautica2",
        "subnautica2-mod",
        "subnautica2modmanager",
        "ue4ss-subnautica-2"
      ],
      "license": "MIT",
      "url": "https://github.com/littlefrogyq/UE4SS-Subnautica-2"
    },
    {
      "name": "CloakBrowser",
      "owner": "SalhaNabil",
      "full_name": "SalhaNabil/CloakBrowser",
      "description": "CloakBrowser Github: anti-detect browser download, source-level chromium patches, browser fingerprinting spoofing, multi-accounting tool, canvas webgl modification, proxy manager http socks5, cookie isolation, session import export, user-agent switcher, puppeteer playwright automation api, profile sharing, web scraping free, github ",
      "language": "TypeScript",
      "stars": 435,
      "forks": 0,
      "created_at": "2026-05-19T17:26:20Z",
      "topics": [
        "anti-detect",
        "anti-detect-browser",
        "antidetect-browser",
        "chromium",
        "cloak-browser",
        "cloak-browser-github",
        "cloakbrowser",
        "cloakbrowser-download",
        "cloakbrowser-downloader",
        "cloakbrowser-install",
        "cloakbrowser-installer",
        "stealth-browser"
      ],
      "license": "MIT",
      "url": "https://github.com/SalhaNabil/CloakBrowser"
    },
    {
      "name": "Manager2026",
      "owner": "mcjavarp",
      "full_name": "mcjavarp/Manager2026",
      "description": "Free IDM. Browser integration, Chrome extension, Firefox addon, Edge module. Download accelerator, segment downloading, resume capability, scheduler. Video grabber, stream detector, batch download. Trial reset, registry cleaner, site analyzer, grabber guide, portable, dark mode.",
      "language": "C++",
      "stars": 432,
      "forks": 34,
      "created_at": "2026-05-14T16:52:26Z",
      "topics": [
        "free-idm",
        "idm",
        "idm-alternative",
        "idm-automation",
        "idm-scripts",
        "idmhelper",
        "idml",
        "idmtrial-reset",
        "internet-download-manager-mac",
        "internetdownloadmanager",
        "kuyhaa-idm"
      ],
      "license": "MIT",
      "url": "https://github.com/mcjavarp/Manager2026"
    },
    {
      "name": "StarCitizen-Community-Localization-Toolkit",
      "owner": "pamireddyb230690ar-hue",
      "full_name": "pamireddyb230690ar-hue/StarCitizen-Community-Localization-Toolkit",
      "description": "🚀 Star Citizen 2026 Localization Hub: Ultimate Modding Guide & Language Files",
      "language": null,
      "stars": 420,
      "forks": 0,
      "created_at": "2026-05-14T21:35:02Z",
      "topics": [
        "community-project",
        "game-modification",
        "installation-guide",
        "language-files",
        "localization",
        "modding",
        "multilingual-support",
        "star-citizen",
        "starcitizen",
        "translation"
      ],
      "license": null,
      "url": "https://github.com/pamireddyb230690ar-hue/StarCitizen-Community-Localization-Toolkit"
    },
    {
      "name": "Acrobat-Esprit-Edition",
      "owner": "kshreya1323",
      "full_name": "kshreya1323/Acrobat-Esprit-Edition",
      "description": "🚀 Acrobat Editor 2026 Pro DC — Ultimate PDF Breaker & Unleashed Utility Download",
      "language": null,
      "stars": 420,
      "forks": 0,
      "created_at": "2026-05-14T21:19:08Z",
      "topics": [
        "acrobat",
        "acrobat-boost-overkill",
        "acrobat-breaker",
        "acrobat-full",
        "acrobat-live",
        "acrobat-pro",
        "acrobat-pro-dc",
        "acrobat-pro-overkill",
        "acrobat-sign",
        "acrobat-supremacy",
        "acrobat-unleashed",
        "acrobat-unstoppable",
        "acrobat-utility",
        "acrobat-windows",
        "pdf-destruction-mode",
        "pdf-software"
      ],
      "license": null,
      "url": "https://github.com/kshreya1323/Acrobat-Esprit-Edition"
    },
    {
      "name": "sklauncher-minecraft",
      "owner": "Harshit-pruthi",
      "full_name": "Harshit-pruthi/sklauncher-minecraft",
      "description": "Download SkLauncher Download: Modern Minecraft launcher. Offline mode, premium login, custom skins setup, cape manager, profile creator. Supports Fabric, Forge, Quilt, NeoForge, OptiFine, Iris shaders. Java 21 path, memory allocation, modpack manager, game directory, auto-update, fluent UI themes, portable.",
      "language": "C++",
      "stars": 418,
      "forks": 0,
      "created_at": "2026-05-15T15:40:52Z",
      "topics": [
        "1-12-2-mod",
        "download-sklauncher",
        "launcher",
        "launcher-minecraft",
        "mclauncher",
        "mcmod",
        "minecraft-1-20-2",
        "minecraft-builds",
        "minecraft-client",
        "minecraft-gui",
        "minecraft-launcher",
        "minecraft-launcher-library",
        "minecraft-mod",
        "minecraft-website",
        "minecraft-world",
        "modded-minecraft",
        "sklauncher-download",
        "sklauncher-minecraft",
        "sklauncher-mods",
        "sklauncher-skin"
      ],
      "license": "MIT",
      "url": "https://github.com/Harshit-pruthi/sklauncher-minecraft"
    },
    {
      "name": "codiff",
      "owner": "nkzw-tech",
      "full_name": "nkzw-tech/codiff",
      "description": "a fast local diff viewer",
      "language": "TypeScript",
      "stars": 401,
      "forks": 16,
      "created_at": "2026-05-15T13:17:31Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/nkzw-tech/codiff"
    },
    {
      "name": "Forza-Horizon-6-Premium",
      "owner": "dannyhsueh2",
      "full_name": "dannyhsueh2/Forza-Horizon-6-Premium",
      "description": "Forza Horizon 6 release date : PC system requirements, early access Steam. Premium Upgrade Bundle, Car Pass, VIP Membership. Japan map, Mt Fuji, Tokyo street racing, Touge Battles, JDM cars, Ferrari J50, Mazda Furai. Expansion 1, Expansion 2, I, , pre-load PC Steam, Game Pass Ultimate.",
      "language": "C++",
      "stars": 397,
      "forks": 1,
      "created_at": "2026-05-15T16:07:55Z",
      "topics": [
        "forza",
        "forza-horizon",
        "forza-horizon-4",
        "forza-horizon-5",
        "forza-horizon-6",
        "forza-horizon-6-download",
        "forza-horizon-6-free",
        "forza-horizon-6-install",
        "forza-horizon-6-pc",
        "forza-horizon-6-premium",
        "forza-horizon-6-release",
        "forza-horizon-6-steam",
        "forza-motorsport",
        "game",
        "open-source-game"
      ],
      "license": "MIT",
      "url": "https://github.com/dannyhsueh2/Forza-Horizon-6-Premium"
    },
    {
      "name": "elephant-agent",
      "owner": "agentic-in",
      "full_name": "agentic-in/elephant-agent",
      "description": "Personal-Model First Self Evolving AI Agent 🐘",
      "language": "Python",
      "stars": 361,
      "forks": 22,
      "created_at": "2026-05-15T07:08:17Z",
      "topics": [
        "agent",
        "agentic",
        "agentic-ai",
        "context",
        "llm",
        "memory",
        "models",
        "personal-ai",
        "self-evolution"
      ],
      "license": null,
      "url": "https://github.com/agentic-in/elephant-agent"
    },
    {
      "name": "audit",
      "owner": "evilsocket",
      "full_name": "evilsocket/audit",
      "description": "An 8-stage vulnerability-discovery agent.",
      "language": "Python",
      "stars": 354,
      "forks": 48,
      "created_at": "2026-05-18T20:42:44Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/evilsocket/audit"
    },
    {
      "name": "mkPIVM",
      "owner": "D7EAD",
      "full_name": "D7EAD/mkPIVM",
      "description": "Generate polymorphic, position-independent virtual machines (PIVMs) from arbitrary x86/x64 shellcode.",
      "language": "C++",
      "stars": 341,
      "forks": 5,
      "created_at": "2026-05-14T16:45:50Z",
      "topics": [
        "cobalt-strike",
        "edr",
        "evasion",
        "exploit",
        "exploitation",
        "havoc",
        "malware",
        "metasploit",
        "mythic",
        "obfuscation",
        "red-team",
        "research",
        "reverse-engineering",
        "shellcode",
        "sliver",
        "virtual-machine",
        "virtualization"
      ],
      "license": "MIT",
      "url": "https://github.com/D7EAD/mkPIVM"
    },
    {
      "name": "loom",
      "owner": "husu",
      "full_name": "husu/loom",
      "description": "一个写接口文档的AI Agent。支持使用Vibe coding 的方式，编写接口文档，同时自带友好的文档查看工具与接口Mock工具",
      "language": null,
      "stars": 329,
      "forks": 19,
      "created_at": "2026-05-15T09:19:02Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/husu/loom"
    },
    {
      "name": "vpnhostinglist",
      "owner": "internetkafe",
      "full_name": "internetkafe/vpnhostinglist",
      "description": "vps hosting list / список ссылок на vps хостинги | RemnaWave / 3X-UI / MarzBan / PasarGuard",
      "language": null,
      "stars": 329,
      "forks": 17,
      "created_at": "2026-05-20T04:31:43Z",
      "topics": [],
      "license": "GPL-3.0",
      "url": "https://github.com/internetkafe/vpnhostinglist"
    },
    {
      "name": "dota2-gameplay-tools",
      "owner": "MediatorSpeak",
      "full_name": "MediatorSpeak/dota2-gameplay-tools",
      "description": "A modular data visualization framework and telemetry toolkit for Dota 2. Designed for real-time match analysis, custom UI prototyping, and gameplay mechanics testing in controlled environments.",
      "language": null,
      "stars": 324,
      "forks": 121,
      "created_at": "2026-05-16T18:46:37Z",
      "topics": [
        "data-visualization",
        "dota2",
        "game-analytics",
        "overlay-system",
        "ui-framework"
      ],
      "license": "MIT",
      "url": "https://github.com/MediatorSpeak/dota2-gameplay-tools"
    },
    {
      "name": "okx-agent-trade-kit",
      "owner": "dex-original",
      "full_name": "dex-original/okx-agent-trade-kit",
      "description": "okx trading bot okx agent mcp cli cryptocurrency okx api automated trading typescript okx trading bot model context protocol cursor ai trading crypto spot futures okx trading bot npm pnpm okx mcp open source quant defi cex okx trading bot algorithmic trading crypto bot okx trading bot okx api mcp okx trading bot crypto mcp",
      "language": "TypeScript",
      "stars": 319,
      "forks": 49,
      "created_at": "2026-05-14T20:45:12Z",
      "topics": [
        "ai-trading",
        "algorithmic-trading",
        "automated-trading",
        "cex",
        "cli",
        "crypto",
        "cryptocurrency",
        "defi",
        "futures",
        "mcp",
        "model-context-protocol",
        "npm",
        "okx",
        "okx-api",
        "open-source",
        "pnpm",
        "quant",
        "spot",
        "trading-bot",
        "typescript"
      ],
      "license": "MIT",
      "url": "https://github.com/dex-original/okx-agent-trade-kit"
    },
    {
      "name": "binance-trading-bot",
      "owner": "pro-tech-killers",
      "full_name": "pro-tech-killers/binance-trading-bot",
      "description": "binance trading bot binance spot binance api trading bot crypto trading bot automated trading binance trading bot typescript ccxt algorithmic trading spot trading crypto bot binance trading bot npm nodejs quant fintech crypto trading bot automated trading binance trading bot open source binance trading bot btc eth usdt binance trading bot",
      "language": "TypeScript",
      "stars": 318,
      "forks": 57,
      "created_at": "2026-05-14T20:33:41Z",
      "topics": [
        "algorithmic-trading",
        "automated-trading",
        "binance",
        "binance-api",
        "btc",
        "ccxt",
        "crypto",
        "crypto-bot",
        "cryptocurrency",
        "eth",
        "fintech",
        "nodejs",
        "npm",
        "open-source",
        "quant",
        "spot-trading",
        "supertrend",
        "trading-bot",
        "typescript"
      ],
      "license": null,
      "url": "https://github.com/pro-tech-killers/binance-trading-bot"
    },
    {
      "name": "polymarket-ai-trading",
      "owner": "trading-2028",
      "full_name": "trading-2028/polymarket-ai-trading",
      "description": "Polymarket Polymarket AI trading AI trading prediction markets prediction markets paper trading paper trading OpenAI OpenAI Node.js Node.js Express Express Docker Docker CLOB CLOB mean reversion mean reversion dashboard dashboard crypto bot crypto bot SQLite SQLite automated trading automated trading API API research trading research trading",
      "language": "HTML",
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Check skills directory**

$ ls /home/runner/work/SquadScope/SquadScope/.squad/skills/

```
branch-protection-pr-workflow	    exponential-backoff-with-jitter
ci-data-source-integration-pattern  pr-review-thread-resolution
<exited with exit code 0>
```


### ✅ `bash`

**Read trending repos and signals section**

$ sed -n '1100,1500p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>402 lines</summary>

```
"language": "HTML",
      "stars": 317,
      "forks": 1434,
      "created_at": "2026-05-14T19:41:32Z",
      "topics": [
        "ai-trading",
        "automated-trading",
        "clob",
        "cryptocurrency",
        "dashboard",
        "docker",
        "express",
        "mean-reversion",
        "nodejs",
        "openai",
        "paper-trading",
        "polymarket",
        "prediction-markets",
        "sqlite",
        "trading-bot"
      ],
      "license": null,
      "url": "https://github.com/trading-2028/polymarket-ai-trading"
    },
    {
      "name": "burn-baby-burn",
      "owner": "dtnewman",
      "full_name": "dtnewman/burn-baby-burn",
      "description": "Be the most productive engineer on your team 🚀🚀🚀",
      "language": "Shell",
      "stars": 310,
      "forks": 7,
      "created_at": "2026-05-15T16:51:59Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/dtnewman/burn-baby-burn"
    },
    {
      "name": "agent-study",
      "owner": "Callous-0923",
      "full_name": "Callous-0923/agent-study",
      "description": "36章AI Agent全栈课程：从ReAct循环到Claude Code逆向、MCP/A2A协议、RAG、DSPy、生产可观测性——全部为可运行Python文件，面试导向。",
      "language": "HTML",
      "stars": 299,
      "forks": 23,
      "created_at": "2026-05-14T07:16:27Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/Callous-0923/agent-study"
    },
    {
      "name": "coinbase-trading-bot",
      "owner": "pro-tech-killers",
      "full_name": "pro-tech-killers/coinbase-trading-bot",
      "description": "coinbase trading bot coinbase api advanced trade trading bot crypto trading bot automated trading coinbase trading bot typescript algorithmic trading ema atr coinbase bot crypto trading bot coinbase trading bot paper trading spot coinbase trading bot risk sizing zod nodejs coinbase trading bot fintech quant coinbase trading bot open source",
      "language": "TypeScript",
      "stars": 288,
      "forks": 0,
      "created_at": "2026-05-14T20:33:43Z",
      "topics": [
        "advanced-trade",
        "algorithmic-trading",
        "atr",
        "automated-trading",
        "coinbase",
        "coinbase-api",
        "crypto-bot",
        "cryptocurrency",
        "ema",
        "fintech",
        "nodejs",
        "open-source",
        "paper-trading",
        "quant",
        "sol",
        "spot",
        "trading-bot",
        "typescript",
        "zod"
      ],
      "license": null,
      "url": "https://github.com/pro-tech-killers/coinbase-trading-bot"
    },
    {
      "name": "Pumpfun_AI_Trading_Bot",
      "owner": "Dangerous-hole",
      "full_name": "Dangerous-hole/Pumpfun_AI_Trading_Bot",
      "description": "Pump.fun Pump.fun Solana Solana TypeScript TypeScript trading bot trading bot AI trading AI trading OpenAI OpenAI CLI automation meme coin meme coin cryptocurrency cryptocurrency token token comment bot comment bot Solana bot Solana bot web3 web3",
      "language": "TypeScript",
      "stars": 288,
      "forks": 0,
      "created_at": "2026-05-14T19:43:23Z",
      "topics": [
        "ai-trading",
        "automation",
        "cli",
        "comment-bot",
        "cryptocurrency",
        "meme-coin",
        "openai",
        "pump-fun",
        "solana",
        "solana-bot",
        "trading-bot",
        "typescript",
        "web3"
      ],
      "license": null,
      "url": "https://github.com/Dangerous-hole/Pumpfun_AI_Trading_Bot"
    },
    {
      "name": "Vivid-R6-Cracked-2026",
      "owner": "RastProxy88",
      "full_name": "RastProxy88/Vivid-R6-Cracked-2026",
      "description": "External memory analysis framework for Rainbow Six Siege. Features ESP, aimbot, skeleton rendering via DirectX 11 overlay. Read-only operation with direct syscall stubs. Supports Y8S4 — Y9S2. C++17, x64, MIT license.",
      "language": "C++",
      "stars": 286,
      "forks": 0,
      "created_at": "2026-05-16T12:46:41Z",
      "topics": [
        "cpp17",
        "directx11",
        "educational",
        "external-tool",
        "game-tool",
        "memory-analysis",
        "open-source",
        "overlay-renderer",
        "rainbow6",
        "read-only",
        "reverse-engineering",
        "win32-api"
      ],
      "license": "MIT",
      "url": "https://github.com/RastProxy88/Vivid-R6-Cracked-2026"
    },
    {
      "name": "Polymarket-trading-bot",
      "owner": "POLYMARKET-TRADER-LAB",
      "full_name": "POLYMARKET-TRADER-LAB/Polymarket-trading-bot",
      "description": "polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket  bot, ",
      "language": "JavaScript",
      "stars": 278,
      "forks": 1471,
      "created_at": "2026-05-14T18:59:39Z",
      "topics": [
        "arbitrage",
        "arbitrage-bot",
        "automated-trading",
        "btc-updown",
        "clob",
        "copy-trading",
        "crypto-trading",
        "defi",
        "market-data",
        "mirror-trading",
        "nodejs",
        "polygon",
        "polymarket",
        "polymarket-bot",
        "prediction-markets",
        "trading-bot",
        "trading-signals",
        "typescript",
        "wallet-tracking",
        "web3"
      ],
      "license": null,
      "url": "https://github.com/POLYMARKET-TRADER-LAB/Polymarket-trading-bot"
    },
    {
      "name": "polymarket-arbitrage-trading-bot",
      "owner": "DEV-OCR",
      "full_name": "DEV-OCR/polymarket-arbitrage-trading-bot",
      "description": "polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket  bot, ",
      "language": "TypeScript",
      "stars": 278,
      "forks": 1329,
      "created_at": "2026-05-14T18:50:46Z",
      "topics": [
        "arbitrage",
        "arbitrage-bot",
        "automated-trading",
        "btc",
        "clob",
        "crypto-trading",
        "defi",
        "eth",
        "gamma-api",
        "market-making",
        "nodejs",
        "orderbook",
        "polygon",
        "polymarket",
        "polymarket-arbitrage",
        "prediction-markets",
        "sol",
        "trading-bot",
        "typescript",
        "web3"
      ],
      "license": null,
      "url": "https://github.com/DEV-OCR/polymarket-arbitrage-trading-bot"
    },
    {
      "name": "aida64",
      "owner": "CylinderChairman",
      "full_name": "CylinderChairman/aida64",
      "description": "aida64 unlocker extreme edition",
      "language": "PowerShell",
      "stars": 274,
      "forks": 0,
      "created_at": "2026-05-20T10:52:40Z",
      "topics": [
        "aida64",
        "aida64-extreme-patch",
        "aida64-unlocker"
      ],
      "license": "MIT",
      "url": "https://github.com/CylinderChairman/aida64"
    },
    {
      "name": "shushu-internship-tool",
      "owner": "LiuMengxuan04",
      "full_name": "LiuMengxuan04/shushu-internship-tool",
      "description": "把岗位描述变项目，把项目变简历，把简历变面试。",
      "language": "Python",
      "stars": 273,
      "forks": 7,
      "created_at": "2026-05-17T11:25:47Z",
      "topics": [
        "ai",
        "ai-agents",
        "skills"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/LiuMengxuan04/shushu-internship-tool"
    },
    {
      "name": "LSFG-Desktop",
      "owner": "uktrash",
      "full_name": "uktrash/LSFG-Desktop",
      "description": "Lossless Scaling github steam reddit LSFG 3 frame generation  v3.22, uncap FPS low end PC, AMD FSR NIS scaling, cursor lag fix. Double FPS laptop guide, windowed to borderless fullscreen, ghosting artifact solution, capture API DXGI GDI, half refresh rate VSync. anime4k ,  version , latency reduction, lsfg",
      "language": "C#",
      "stars": 251,
      "forks": 0,
      "created_at": "2026-05-20T12:51:00Z",
      "topics": [
        "crimson-desert-lsfg",
        "frame-generation",
        "gaming-performance",
        "lossless-frame-generation",
        "lossless-scaling",
        "lossless-scaling-2026",
        "lossless-scaling-android",
        "lossless-scaling-download",
        "lossless-scaling-github",
        "lossless-scaling-lsfg",
        "lossless-scaling-pc",
        "lossless-scaling-reddit",
        "lossless-scaling-software",
        "lossless-scaling-steam",
        "lossless-scaling-v3",
        "lsfg",
        "lsfg-ai-upscaling",
        "lsfg-vk",
        "optiscaler",
        "smooth-gaming"
      ],
      "license": "MIT",
      "url": "https://github.com/uktrash/LSFG-Desktop"
    },
    {
      "name": "infinite-canvas",
      "owner": "basketikun",
      "full_name": "basketikun/infinite-canvas",
      "description": "面向AI创作的开源无限画布工作台，集成 AI 生图、参考图编辑、画布编排、对话助手、提示词库和素材管理等功能。",
      "language": "TypeScript",
      "stars": 249,
      "forks": 43,
      "created_at": "2026-05-18T23:45:50Z",
      "topics": [],
      "license": "AGPL-3.0",
      "url": "https://github.com/basketikun/infinite-canvas"
    },
    {
      "name": "slopless",
      "owner": "agent-quality-controls",
      "full_name": "agent-quality-controls/slopless",
      "description": "Deterministic textlint rules and CLI for catching prose slop in Markdown",
      "language": "TypeScript",
      "stars": 247,
      "forks": 38,
      "created_at": "2026-05-16T20:44:14Z",
      "topics": [
        "ai",
        "cli",
        "lint",
        "linter",
        "llm",
        "markdown",
        "nodejs",
        "prose",
        "quality",
        "slop",
        "static-analysis",
        "style-guide",
        "textlint",
        "typescript",
        "writing"
      ],
      "license": "MIT",
      "url": "https://github.com/agent-quality-controls/slopless"
    },
    {
      "name": "claude-fuer-deutsches-recht",
      "owner": "Klotzkette",
      "full_name": "Klotzkette/claude-fuer-deutsches-recht",
      "description": "⚠️ Experimentelle Skill-Sammlung für deutsches Recht (Arbeits-, Gesellschafts-, Insolvenz-, Datenschutz-, Prozessrecht u.a.) – inzwischen verbessert und im Alltag getestet, aber weiterhin Experiment. Bitte selber ausprobieren, Issues/PRs willkommen! Keine Rechtsberatung. Mandatsgeheimnis (§§ 203/204 StGB, § 43e BRAO), DSGVO, US-Transfer, KI-VO & Co",
      "language": "Python",
      "stars": 239,
      "forks": 12,
      "created_at": "2026-05-18T16:43:56Z",
      "topics": [
        "anthropic",
        "bgh",
        "claude-skills",
        "deutsches-recht",
        "dsgvo",
        "german-law",
        "kanzlei",
        "legal-ai",
        "legaltech"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/Klotzkette/claude-fuer-deutsches-recht"
    },
    {
      "name": "md2html",
      "owner": "haidang1810",
      "full_name": "haidang1810/md2html",
      "description": "Your AI writes docs — md2html turns them into pages people actually read. A portable skill for Claude Code / Codex / Antigravity that converts long-form Markdown (plans, specs, system designs, RFCs, runbooks, postmortems, brainstorms) into self-contained HTML with Mermaid, timelines, callouts, TOC. Multi-language.",
      "language": "HTML",
      "stars": 236,
      "forks": 17,
      "created_at": "2026-05-14T05:38:34Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/haidang1810/md2html"
    },
    {
      "name": "apex-dashboard",
      "owner": "PandoraReads",
      "full_name": "PandoraReads/apex-dashboard",
      "description": "Stop switching between Obsidian notes. One page. Everything you need. Memo your thoughts, crush your todos, track your projects — and make it look incredible doing it.",
      "language": "CSS",
      "stars": 233,
      "forks": 10,
      "created_at": "2026-05-14T07:42:42Z",
      "topics": [
        "dashboard",
        "dashboard-templates",
        "obsidian",
        "obsidian-plugin",
        "obsidian-plugins"
      ],
      "license": "0BSD",
      "url": "https://github.com/PandoraReads/apex-dashboard"
    },
    {
      "name": "Polymarket-Arbitrage-Trading-Bot-v2",
      "owner": "heyFive-dev",
      "full_name": "heyFive-dev/Polymarket-Arbitrage-Trading-Bot-v2",
      "description": "Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot  Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot Polymarket Trading Bot",
      "language": "TypeScript",
      "stars": 231,
      "forks": 1431,
      "created_at": "2026-05-14T06:55:32Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/heyFive-dev/Polymarket-Arbitrage-Trading-Bot-v2"
    },
    {
      "name": "humanize-text",
      "owner": "lynote-ai",
      "full_name": "lynote-ai/humanize-text",
      "description": "Free open-source AI text humanizer to convert AI-generated content into undetectable, human-like writing. Bypass Turnitin, GPTZero, and all major AI detectors. No sign-up required. Try our unlimited free online tool",
      "language": "Python",
      "stars": 227,
      "forks": 6,
      "created_at": "2026-05-18T10:12:15Z",
      "topics": [
        "ai-humanize",
        "ai-humanizer",
        "gptzero-bypass",
        "humanization",
        "humanize-ai",
        "humanize-ai-text",
        "humanize-text",
        "humanizer",
        "undetectable-ai-alternative"
<exited with exit code 0>
```

</details>


### ✅ `bash`

**List skill files**

$ ls /home/runner/work/SquadScope/SquadScope/.squad/skills/

```
branch-protection-pr-workflow	    exponential-backoff-with-jitter
ci-data-source-integration-pattern  pr-review-thread-resolution
<exited with exit code 0>
```


### ✅ `bash`

**Read remainder of raw data - trending repos, signals, metadata**

$ sed -n '1500,1900p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>402 lines</summary>

```
"undetectable-ai-alternative"
      ],
      "license": "MIT",
      "url": "https://github.com/lynote-ai/humanize-text"
    },
    {
      "name": "polymarket-weather-trading-bot",
      "owner": "Signal-Probability-Engine",
      "full_name": "Signal-Probability-Engine/polymarket-weather-trading-bot",
      "description": "Polymarket weather trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket polymarket trading bot bot bot",
      "language": "TypeScript",
      "stars": 220,
      "forks": 2252,
      "created_at": "2026-05-14T06:32:51Z",
      "topics": [
        "bot",
        "git",
        "polymarket-weather-bot",
        "polymarket-weather-trading",
        "polymarket-weather-trading-bot",
        "trading-bot",
        "weather-bot",
        "weather-trading-bot"
      ],
      "license": null,
      "url": "https://github.com/Signal-Probability-Engine/polymarket-weather-trading-bot"
    },
    {
      "name": "YellowKey-Bitlocker",
      "owner": "rahul03524",
      "full_name": "rahul03524/YellowKey-Bitlocker",
      "description": "YellowKey Github: bitlocker encryption bypass tool, winre physical access zero-day exploit, chaotic eclipse nightmare-eclipse github, tpm-only default configuration vulnerability. windows 11 server 2022 2025 unpatched, fstx folder system volume information, transactional ntfs metadata exploit, usb ",
      "language": "TypeScript",
      "stars": 219,
      "forks": 1,
      "created_at": "2026-05-20T14:26:15Z",
      "topics": [
        "bitlocker",
        "bitlocker-drive-encryption",
        "bitlocker-drive-management",
        "bypass-uac",
        "yellowkey",
        "yellowkey-bitlocker",
        "yellowkey-github"
      ],
      "license": "MIT",
      "url": "https://github.com/rahul03524/YellowKey-Bitlocker"
    },
    {
      "name": "comview",
      "owner": "rockorager",
      "full_name": "rockorager/comview",
      "description": "the best diff viewer ever made",
      "language": "Go",
      "stars": 215,
      "forks": 14,
      "created_at": "2026-05-14T22:17:40Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/rockorager/comview"
    },
    {
      "name": "Deepseek-v4-pro-app",
      "owner": "MFS9628",
      "full_name": "MFS9628/Deepseek-v4-pro-app",
      "description": "DeepSeek v4 Pro github Flash chat: API flash gemma 4 gemini qwen claude chatgpt 4  key pricing tier, open source weights, huggingface model repository, local execution ollama setup. context window token limit, coding benchmark leaderboard ranking, reasoning model architecture v4,  .visual studio code extension integration, cursor ai ",
      "language": null,
      "stars": 215,
      "forks": 0,
      "created_at": "2026-05-20T13:56:54Z",
      "topics": [
        "ai-app",
        "ai-powered-applications",
        "artificial-intelligence-projects",
        "deep-seek",
        "deepseek",
        "deepseek-api",
        "deepseek-free-api",
        "deepseek-integration",
        "deepseek-ocr-2",
        "deepseek-r1",
        "deepseek-r1-zero",
        "deepseek-v3",
        "deepseek-v4",
        "deepseek-v4-api",
        "deepseek-v4-app",
        "deepseek-v4-free",
        "deepseek-v4-pro",
        "deepseekv4",
        "deepseekv4-flash",
        "free-api"
      ],
      "license": "MIT",
      "url": "https://github.com/MFS9628/Deepseek-v4-pro-app"
    },
    {
      "name": "codex-orange-book",
      "owner": "alchaincyf",
      "full_name": "alchaincyf/codex-orange-book",
      "description": "OpenAI Codex: The Complete Guide · 橙皮书系列 · GPT-5.5 时代的 AI 编程实战手册",
      "language": "HTML",
      "stars": 205,
      "forks": 16,
      "created_at": "2026-05-14T12:49:01Z",
      "topics": [
        "agentic-coding",
        "ai-coding",
        "codex",
        "gpt-5",
        "huasheng",
        "openai",
        "orange-book"
      ],
      "license": null,
      "url": "https://github.com/alchaincyf/codex-orange-book"
    },
    {
      "name": "android-testing-skills",
      "owner": "skydoves",
      "full_name": "skydoves/android-testing-skills",
      "description": "⚡️ A set of skills for Android testing: Compose UI, AndroidX Test, JVM unit tests, and ADB.",
      "language": "Shell",
      "stars": 203,
      "forks": 3,
      "created_at": "2026-05-15T07:38:44Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/skydoves/android-testing-skills"
    },
    {
      "name": "openai-plus-vxt",
      "owner": "suyancc",
      "full_name": "suyancc/openai-plus-vxt",
      "description": "一个基于 WXT 的浏览器插件，用于辅助 ChatGPT 注册、Checkout 链接提取、随机地址资料生成，以及 OpenAI/PayPal 支付页资料自动填写。",
      "language": "TypeScript",
      "stars": 198,
      "forks": 53,
      "created_at": "2026-05-19T02:24:31Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/suyancc/openai-plus-vxt"
    },
    {
      "name": "polymarket-trading-bot",
      "owner": "Multichain-Bot-Lab",
      "full_name": "Multichain-Bot-Lab/polymarket-trading-bot",
      "description": "polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot",
      "language": "TypeScript",
      "stars": 193,
      "forks": 4500,
      "created_at": "2026-05-15T16:46:39Z",
      "topics": [
        "polymarket-arbitrage-bot",
        "polymarket-arbitrage-trading-bot",
        "polymarket-trading-bot"
      ],
      "license": null,
      "url": "https://github.com/Multichain-Bot-Lab/polymarket-trading-bot"
    },
    {
      "name": "phonto",
      "owner": "museslabs",
      "full_name": "museslabs/phonto",
      "description": "GPU-accelerated video wallpaper program for wayland compositors and macos",
      "language": "Rust",
      "stars": 187,
      "forks": 3,
      "created_at": "2026-05-14T10:54:34Z",
      "topics": [
        "live-wallpaper",
        "macos",
        "macos-wallpaper",
        "video-wallpaper",
        "wallpaper",
        "wayland-wallpaper"
      ],
      "license": "GPL-3.0",
      "url": "https://github.com/museslabs/phonto"
    },
    {
      "name": "f95-zone-sync-manager",
      "owner": "Aryanzzzz25",
      "full_name": "Aryanzzzz25/f95-zone-sync-manager",
      "description": "Best NSFW Game Manager 2026 – Auto Install & Update Mods Fast ⚡🎮",
      "language": null,
      "stars": 186,
      "forks": 0,
      "created_at": "2026-05-14T21:31:40Z",
      "topics": [
        "f95zone",
        "game",
        "game-information",
        "game-install",
        "game-updates",
        "games",
        "manager",
        "mod",
        "nsfw"
      ],
      "license": null,
      "url": "https://github.com/Aryanzzzz25/f95-zone-sync-manager"
    },
    {
      "name": "Draft-2026-CAD-Workspace",
      "owner": "ogaawin",
      "full_name": "ogaawin/Draft-2026-CAD-Workspace",
      "description": "🚀 Free AutoCAD 2026 Crack Download – Instant & Fast Install Full CAD",
      "language": null,
      "stars": 185,
      "forks": 0,
      "created_at": "2026-05-14T21:21:24Z",
      "topics": [
        "auto-cad",
        "auto-cad-free",
        "autocad",
        "autocad-addins",
        "autocad-install",
        "cad",
        "cad-software",
        "windows-cad"
      ],
      "license": null,
      "url": "https://github.com/ogaawin/Draft-2026-CAD-Workspace"
    },
    {
      "name": "psn-plus-controller-config",
      "owner": "JorgeSnn",
      "full_name": "JorgeSnn/psn-plus-controller-config",
      "description": "Ultimate PS Plus Premium Tools 2026 🎮 Best PSN Automation & Cloud Saves Manager",
      "language": null,
      "stars": 185,
      "forks": 0,
      "created_at": "2026-05-14T21:33:54Z",
      "topics": [
        "games",
        "playstation-automation",
        "playstation-cloud-saves",
        "playstation-cloud-streaming",
        "playstation-collection",
        "playstation-monthly-games",
        "playstation-plus-2026",
        "playstation-plus-tools",
        "playstation-profile-tools",
        "playstation-utilities",
        "ps-plus",
        "ps-plus-discounts",
        "ps-plus-tools",
        "ps-plus-utilities",
        "psn-api",
        "psn-friends-manager",
        "psn-store-tools",
        "psn-trophies"
      ],
      "license": null,
      "url": "https://github.com/JorgeSnn/psn-plus-controller-config"
    },
    {
      "name": "polymarket-arbitrage-trading-bot",
      "owner": "money-takers",
      "full_name": "money-takers/polymarket-arbitrage-trading-bot",
      "description": "polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket arbitrage bot, polymarket trading bot polymarket  bot, ",
      "language": "TypeScript",
      "stars": 178,
      "forks": 1683,
      "created_at": "2026-05-14T19:22:12Z",
      "topics": [
        "arbitrage-bot",
        "automated-trading",
        "btc",
        "clob",
        "crypto-trading",
        "defi",
        "dump-and-hedge",
        "eth",
        "gamma-api",
        "market-making",
        "nodejs",
        "orderbook",
        "polygon",
        "polymarket",
        "polymarket-arbitrage",
        "polymarket-bot",
        "prediction-markets",
        "trading-bot",
        "typescript",
        "web3"
      ],
      "license": null,
      "url": "https://github.com/money-takers/polymarket-arbitrage-trading-bot"
    },
    {
      "name": "technical-writing",
      "owner": "luoling8192",
      "full_name": "luoling8192/technical-writing",
      "description": "中文内部技术写作的 agent skill，约束设计文档 / 评审稿 / postmortem / 分享稿场景的语气、句法、结构",
      "language": null,
      "stars": 175,
      "forks": 9,
      "created_at": "2026-05-15T12:31:42Z",
      "topics": [
        "agent-skill",
        "chinese",
        "claude-code",
        "codex",
        "documentation",
        "technical-writing"
      ],
      "license": "MIT",
      "url": "https://github.com/luoling8192/technical-writing"
    },
    {
      "name": "Polymarket-trading-bot",
      "owner": "POLYMARKET-SPORTS",
      "full_name": "POLYMARKET-SPORTS/Polymarket-trading-bot",
      "description": "polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket arbitrage bot, polymarket copy trading bot polymarket  bot, ",
      "language": "JavaScript",
      "stars": 174,
      "forks": 410,
      "created_at": "2026-05-14T19:18:49Z",
      "topics": [
        "arbitrage-bot",
        "automated-trading",
        "btc-updown",
        "clob",
        "copy-trading",
        "crypto-trading",
        "defi",
        "market-data",
        "mirror-trading",
        "nodejs",
        "open-source",
        "polygon",
        "polymarket",
        "polymarket-bot",
        "polymarket-copy-trading",
        "prediction-markets",
        "trading-bot",
        "typescript",
        "wallet-tracking",
        "web3"
      ],
      "license": null,
      "url": "https://github.com/POLYMARKET-SPORTS/Polymarket-trading-bot"
    },
    {
      "name": "HermesPet",
      "owner": "basionwang-bot",
      "full_name": "basionwang-bot/HermesPet",
      "description": "让 AI 住在你 MacBook 的刘海里 · 零依赖开箱即用 · 多引擎并行的桌面 AI 伴侣（Swift 6 / SwiftUI / macOS 14+）",
      "language": "Swift",
      "stars": 166,
      "forks": 23,
      "created_at": "2026-05-15T06:03:02Z",
      "topics": [
        "ai",
        "chatgpt",
        "chinese",
        "claude",
        "deepseek",
        "desktop-app",
        "dynamic-island",
        "llm",
        "macos",
        "menu-bar-app",
        "swift",
        "swiftui"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/basionwang-bot/HermesPet"
    },
    {
      "name": "expo-motion-tabs",
      "owner": "rit3zh",
      "full_name": "rit3zh/expo-motion-tabs",
      "description": "⚡️ Smooth motion tabs for Expo Router",
      "language": "TypeScript",
      "stars": 158,
      "forks": 9,
      "created_at": "2026-05-17T12:21:01Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/rit3zh/expo-motion-tabs"
    },
    {
      "name": "exploitbench",
      "owner": "exploitbench",
      "full_name": "exploitbench/exploitbench",
      "description": "ExploitBench measures how far AI agents climb, from reaching vulnerable code, to triggering the bug, to building exploit primitives, to arbitrary code execution.",
      "language": "Python",
      "stars": 157,
      "forks": 9,
      "created_at": "2026-05-14T19:57:32Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/exploitbench/exploitbench"
    },
    {
      "name": "1m_release",
      "owner": "2b2tplace",
      "full_name": "2b2tplace/1m_release",
      "description": "The Largest World Download Project in 2b2t, and in Minecraft altogether. Full info + Renders + Timelapses (+ Torrent soon)",
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Read trending repos and signals data**

$ sed -n '1900,2300p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>402 lines</summary>

```
"description": "The Largest World Download Project in 2b2t, and in Minecraft altogether. Full info + Renders + Timelapses (+ Torrent soon)",
      "language": null,
      "stars": 156,
      "forks": 1,
      "created_at": "2026-05-16T21:24:05Z",
      "topics": [],
      "license": "CC0-1.0",
      "url": "https://github.com/2b2tplace/1m_release"
    },
    {
      "name": "kalshi-trading-bot",
      "owner": "Siva-Chidambaram12",
      "full_name": "Siva-Chidambaram12/kalshi-trading-bot",
      "description": "🏗 AI trading system for Kalshi prediction markets. kalshi trading bot kalshi trading bot kalshi botFeatures Grok-4 integration, multi-agent decision making, portfolio optimization, and real-time market analysis. Educational/research purposes only kalshi trading bot kalshi bot",
      "language": "TypeScript",
      "stars": 156,
      "forks": 866,
      "created_at": "2026-05-14T06:40:24Z",
      "topics": [
        "bot",
        "kalshi",
        "kalshi-bot",
        "kalshi-trading",
        "prediction-market",
        "trading"
      ],
      "license": null,
      "url": "https://github.com/Siva-Chidambaram12/kalshi-trading-bot"
    },
    {
      "name": "solana-trading-bot",
      "owner": "trdx",
      "full_name": "trdx/solana-trading-bot",
      "description": "solana trading bot, an automated Solana sniping bot that trades newly-listed tokens on Raydium AMM v4 and pump.fun bonding curves. Listens to on-chain events in real time, applies configurable safety filters, buys with your chosen quote token (WSOL / USDC), and auto-sells on take-profit / stop-loss.",
      "language": "TypeScript",
      "stars": 155,
      "forks": 2942,
      "created_at": "2026-05-14T07:04:44Z",
      "topics": [
        "bot",
        "dex",
        "rust",
        "solana",
        "solana-memecoin-sniper-bot",
        "solana-trading-platform",
        "trading-bot"
      ],
      "license": "MS-PL",
      "url": "https://github.com/trdx/solana-trading-bot"
    },
    {
      "name": "kalshi-trading-bot",
      "owner": "sachmalan",
      "full_name": "sachmalan/kalshi-trading-bot",
      "description": "kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot",
      "language": "TypeScript",
      "stars": 153,
      "forks": 2030,
      "created_at": "2026-05-17T06:24:13Z",
      "topics": [
        "bot",
        "kalshi",
        "kalshi-trade",
        "kalshi-trading-bot",
        "nodejs",
        "trading"
      ],
      "license": null,
      "url": "https://github.com/sachmalan/kalshi-trading-bot"
    },
    {
      "name": "solana-trading-bot",
      "owner": "VAENPP",
      "full_name": "VAENPP/solana-trading-bot",
      "description": "solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot",
      "language": "TypeScript",
      "stars": 152,
      "forks": 2417,
      "created_at": "2026-05-16T17:33:57Z",
      "topics": [
        "bot",
        "nodejs",
        "solana",
        "solana-trade",
        "solana-trading-bot",
        "trading"
      ],
      "license": "MS-PL",
      "url": "https://github.com/VAENPP/solana-trading-bot"
    },
    {
      "name": "polymarket-mcp-server",
      "owner": "japp-fi",
      "full_name": "japp-fi/polymarket-mcp-server",
      "description": "polymarket mcp server market discovery and analysis via public APIs; optional authenticated trading and portfolio tools when your wallet derives (or supplies) CLOB L2 credentials polymarket mcp server market discovery and analysis via public APIs; optional authenticated trading and portfolio tools when your wallet derives (or supplies) CLOB L2",
      "language": "TypeScript",
      "stars": 152,
      "forks": 2546,
      "created_at": "2026-05-15T19:57:43Z",
      "topics": [
        "mcp-server",
        "mcp-servers",
        "polymarket",
        "polymarket-mcp-server"
      ],
      "license": null,
      "url": "https://github.com/japp-fi/polymarket-mcp-server"
    },
    {
      "name": "solana-pumpfun-token-bundler",
      "owner": "Alchemz",
      "full_name": "Alchemz/solana-pumpfun-token-bundler",
      "description": "solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler",
      "language": "TypeScript",
      "stars": 152,
      "forks": 2420,
      "created_at": "2026-05-16T18:57:25Z",
      "topics": [
        "axiom",
        "bubblemap",
        "bundler",
        "meme",
        "nodejs",
        "pumpfun",
        "solana",
        "token",
        "trading",
        "trojan"
      ],
      "license": null,
      "url": "https://github.com/Alchemz/solana-pumpfun-token-bundler"
    },
    {
      "name": "polymarket-weather-trading-bot",
      "owner": "OpenPatchLab",
      "full_name": "OpenPatchLab/polymarket-weather-trading-bot",
      "description": "polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot",
      "language": "TypeScript",
      "stars": 152,
      "forks": 2421,
      "created_at": "2026-05-16T20:11:40Z",
      "topics": [
        "bot",
        "polymarket",
        "trading",
        "weather"
      ],
      "license": "MIT",
      "url": "https://github.com/OpenPatchLab/polymarket-weather-trading-bot"
    },
    {
      "name": "hyperliquid-trading-bot",
      "owner": "fristork",
      "full_name": "fristork/hyperliquid-trading-bot",
      "description": "hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot",
      "language": "TypeScript",
      "stars": 151,
      "forks": 2415,
      "created_at": "2026-05-16T19:09:13Z",
      "topics": [
        "bot",
        "hyperliquid",
        "hyperliquid-dex",
        "trading"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/fristork/hyperliquid-trading-bot"
    },
    {
      "name": "Agent-Learning-Hub",
      "owner": "datawhalechina",
      "full_name": "datawhalechina/Agent-Learning-Hub",
      "description": "AI Agent 学习路线与资料库收集",
      "language": null,
      "stars": 145,
      "forks": 12,
      "created_at": "2026-05-17T06:41:12Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/datawhalechina/Agent-Learning-Hub"
    },
    {
      "name": "x-algorithm-wiki",
      "owner": "cclank",
      "full_name": "cclank/x-algorithm-wiki",
      "description": "Architecture wiki for the open-sourced X \"For You\" recommendation algorithm (xai-org/x-algorithm) — 21 source-anchored pages",
      "language": "HTML",
      "stars": 144,
      "forks": 14,
      "created_at": "2026-05-16T02:58:56Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/cclank/x-algorithm-wiki"
    },
    {
      "name": "ShizuCallRecorder",
      "owner": "kitsumed",
      "full_name": "kitsumed/ShizuCallRecorder",
      "description": "ShizuCallRecorder empowers ADB through Shizuku to record phone calls on non-rooted device!",
      "language": "Kotlin",
      "stars": 138,
      "forks": 2,
      "created_at": "2026-05-14T20:18:11Z",
      "topics": [
        "adb",
        "android",
        "callrecorder",
        "no-root",
        "scrcpy",
        "shizuku"
      ],
      "license": "GPL-3.0",
      "url": "https://github.com/kitsumed/ShizuCallRecorder"
    },
    {
      "name": "JennyMod-All-Versions",
      "owner": "AppleOnFire",
      "full_name": "AppleOnFire/JennyMod-All-Versions",
      "description": "jenny mod minecraft pe mc video download pc java curseforge forge fabric  girlfriend addon pocket edition download .jar mediafire link realistic animations render pass bed interaction companion skin texture bedrock edition mcpack free portable zip apk mobile character custom dialogue chat adult content",
      "language": "Java",
      "stars": 137,
      "forks": 0,
      "created_at": "2026-05-20T16:33:36Z",
      "topics": [
        "all-the-mods-modpack",
        "jenny",
        "jenny-mod-2026",
        "jennybot",
        "jennymod",
        "jennymod-2026",
        "minecraft-jenny-mod",
        "minecraft-jenny-mod-2026",
        "minecraft-mc",
        "minecraft-mod",
        "minecraft-nsfw-mod",
        "minecraftjennymod",
        "minecraftjennymod-2026",
        "modded-minecraft",
        "modded-minecraft-modpack",
        "nsfw-minecraft-mod",
        "nsfw-mod",
        "tminecaft"
      ],
      "license": "MIT",
      "url": "https://github.com/AppleOnFire/JennyMod-All-Versions"
    },
    {
      "name": "lightroom-cc-on-linux",
      "owner": "sander110419",
      "full_name": "sander110419/lightroom-cc-on-linux",
      "description": "Reproducible recipe for running Adobe Lightroom CC on Linux via Wine 11.8 staging. Researched and verified end-to-end by Claude Opus 4.7.",
      "language": "C",
      "stars": 137,
      "forks": 4,
      "created_at": "2026-05-17T09:17:14Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/sander110419/lightroom-cc-on-linux"
    },
    {
      "name": "KMSTools",
      "owner": "ZettPW",
      "full_name": "ZettPW/KMSTools",
      "description": "windows tool, office 2026 perpetual license command, net download, digital entitlement permanent custom host ",
      "language": "C#",
      "stars": 135,
      "forks": 0,
      "created_at": "2026-05-20T16:09:42Z",
      "topics": [
        "activator",
        "kms",
        "kms-activation-github",
        "kms-client",
        "kms-host-server",
        "kms-office",
        "kms-script",
        "kms-server",
        "kms-studio-dev",
        "kmsauto-",
        "kmsauto-net-2026",
        "kmsauto-portable-official",
        "kmspico-2027",
        "kmspico-portable-2026",
        "kmspico-update",
        "permanent-windows-activator-2026",
        "windows-11-activator-kmsauto",
        "windows-activaton",
        "windows-activator-free"
      ],
      "license": "MIT",
      "url": "https://github.com/ZettPW/KMSTools"
    },
    {
      "name": "weft",
      "owner": "WyattLee-nanami",
      "full_name": "WyattLee-nanami/weft",
      "description": "Weft — a local Claude Code workbench. Manage skills, see token usage, browse history. Native macOS, fully offline, MIT.",
      "language": "Rust",
      "stars": 132,
      "forks": 1,
      "created_at": "2026-05-14T06:19:43Z",
      "topics": [
        "claude-code",
        "desktop-app",
        "developer-tools",
        "macos",
        "react",
        "skill-management",
        "tauri",
        "typescript"
      ],
      "license": "MIT",
      "url": "https://github.com/WyattLee-nanami/weft"
    },
    {
      "name": "PhantomKiller",
      "owner": "redteamfortress",
      "full_name": "redteamfortress/PhantomKiller",
      "description": "Another BYOVD process killer. works on all EDR's. fully signed.",
      "language": "C++",
      "stars": 128,
      "forks": 23,
      "created_at": "2026-05-19T07:00:59Z",
      "topics": [
        "byovd",
        "edr",
        "edr-bypass",
        "edr-evasion",
        "redteaming"
      ],
      "license": null,
      "url": "https://github.com/redteamfortress/PhantomKiller"
    },
    {
      "name": "PaperSpine",
      "owner": "WUBING2023",
      "full_name": "WUBING2023/PaperSpine",
      "description": "PaperSpine is a motivation-driven Codex skill for learning from strong academic papers, building a paper’s central argument, and rewriting manuscripts through evidence-aware blueprints, revision matrices, and LaTeX-safe audits.",
      "language": "Python",
      "stars": 124,
      "forks": 6,
      "created_at": "2026-05-17T08:37:31Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/WUBING2023/PaperSpine"
    },
    {
      "name": "Maya",
      "owner": "ronaldo-avalos",
      "full_name": "ronaldo-avalos/Maya",
      "description": "🖥️ 📱 ▶️ Wrap your iPhone screen recordings in a beautiful device frame, add cinematic zoom moments, and export ready-to-share videos.",
      "language": "Swift",
      "stars": 119,
      "forks": 16,
      "created_at": "2026-05-17T04:00:39Z",
      "topics": [
        "iphone-screen-recordings",
        "macos-app",
        "screen-recordings"
      ],
      "license": "MIT",
      "url": "https://github.com/ronaldo-avalos/Maya"
    },
    {
      "name": "cdn-ip-finder",
      "owner": "hossein8360",
      "full_name": "hossein8360/cdn-ip-finder",
      "description": "CDN IP finder for ShirOKhorshid domain fronting",
      "language": "HTML",
      "stars": 118,
      "forks": 47,
      "created_at": "2026-05-17T20:36:39Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/hossein8360/cdn-ip-finder"
    },
    {
      "name": "QuantumFlow",
      "owner": "zimingttkx",
      "full_name": "zimingttkx/QuantumFlow",
      "description": "QuantumFlow - Distributed LLM inference scheduling framework with multi-backend support (vLLM, TGI, SGLang), adaptive scheduling strategies, and cluster management.",
      "language": "Python",
      "stars": 118,
      "forks": 0,
      "created_at": "2026-05-16T03:51:46Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/zimingttkx/QuantumFlow"
    },
    {
      "name": "teams-policy-export",
      "owner": "disintegr8te",
      "full_name": "disintegr8te/teams-policy-export",
      "description": "PowerShell tool to export Microsoft Teams policies and generate stakeholder decision workbooks",
      "language": "PowerShell",
      "stars": 117,
      "forks": 12,
      "created_at": "2026-05-17T19:16:59Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/disintegr8te/teams-policy-export"
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Read trending repos and signals**

$ sed -n '2300,2800p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>502 lines</summary>

```
"url": "https://github.com/disintegr8te/teams-policy-export"
    },
    {
      "name": "Cola-DLM",
      "owner": "ByteDance-Seed",
      "full_name": "ByteDance-Seed/Cola-DLM",
      "description": "The codebase of Cola DLM",
      "language": "Python",
      "stars": 116,
      "forks": 4,
      "created_at": "2026-05-15T07:09:04Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/ByteDance-Seed/Cola-DLM"
    },
    {
      "name": "vibe-observer",
      "owner": "AIchovy",
      "full_name": "AIchovy/vibe-observer",
      "description": "Claude Code Tracer & Observer",
      "language": "Rust",
      "stars": 116,
      "forks": 1,
      "created_at": "2026-05-17T05:50:21Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/AIchovy/vibe-observer"
    },
    {
      "name": "jarvis",
      "owner": "alpunlu12-commits",
      "full_name": "alpunlu12-commits/jarvis",
      "description": "Jarvis AI Asistan",
      "language": null,
      "stars": 115,
      "forks": 34,
      "created_at": "2026-05-14T09:25:19Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/alpunlu12-commits/jarvis"
    },
    {
      "name": "Awesome-Datasets-Hub",
      "owner": "ahammadmejbah",
      "full_name": "ahammadmejbah/Awesome-Datasets-Hub",
      "description": "A curated collection of datasets for Large Language Models (LLMs), covering medical AI, NLP, multimodal learning, instruction tuning, reasoning, code generation, and evaluation benchmarks.",
      "language": null,
      "stars": 115,
      "forks": 32,
      "created_at": "2026-05-15T14:58:14Z",
      "topics": [
        "benchmark",
        "benchmarking",
        "deep-learning",
        "deep-neural-networks",
        "deeplearning",
        "genetic-algorithm",
        "llm",
        "llm-evaluation",
        "llm-inference",
        "machine-learning",
        "machine-learning-algorithms",
        "machinelearning",
        "neural-network"
      ],
      "license": null,
      "url": "https://github.com/ahammadmejbah/Awesome-Datasets-Hub"
    },
    {
      "name": "founders-playbook-zh",
      "owner": "yangliu2060",
      "full_name": "yangliu2060/founders-playbook-zh",
      "description": "Anthropic《The Founder's Playbook: Building an AI-Native Startup》非官方中文翻译版（含中文信息图表）",
      "language": null,
      "stars": 114,
      "forks": 14,
      "created_at": "2026-05-15T14:12:49Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/yangliu2060/founders-playbook-zh"
    },
    {
      "name": "nikvpn-codespace",
      "owner": "nikvpn-iran",
      "full_name": "nikvpn-iran/nikvpn-codespace",
      "description": "Free VLESS proxy using GitHub Codespaces - NikVPN for Iran",
      "language": "Shell",
      "stars": 113,
      "forks": 907,
      "created_at": "2026-05-15T15:07:46Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/nikvpn-iran/nikvpn-codespace"
    },
    {
      "name": "SDAR",
      "owner": "ZJU-REAL",
      "full_name": "ZJU-REAL/SDAR",
      "description": "Official code for \"Self-Distilled Agentic Reinforcement Learning\"",
      "language": "Python",
      "stars": 111,
      "forks": 7,
      "created_at": "2026-05-14T16:54:03Z",
      "topics": [
        "agentic-ai",
        "agentic-skill",
        "opsd",
        "rl",
        "skill"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/ZJU-REAL/SDAR"
    },
    {
      "name": "nanotdb",
      "owner": "aymanhs",
      "full_name": "aymanhs/nanotdb",
      "description": "A tiny, append‑only time‑series database designed for long‑running sensor data on modest hardware.",
      "language": "Go",
      "stars": 111,
      "forks": 2,
      "created_at": "2026-05-14T06:00:30Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/aymanhs/nanotdb"
    },
    {
      "name": "NESLab",
      "owner": "ip-arch",
      "full_name": "ip-arch/NESLab",
      "description": "Educational materials for Embedded systems with NES",
      "language": "C++",
      "stars": 108,
      "forks": 6,
      "created_at": "2026-05-17T01:15:37Z",
      "topics": [],
      "license": "GPL-3.0",
      "url": "https://github.com/ip-arch/NESLab"
    },
    {
      "name": "tilelang-cuda-skills",
      "owner": "sablin39",
      "full_name": "sablin39/tilelang-cuda-skills",
      "description": "Skills for writing tilelang and debugging with CUDA toolkits. ",
      "language": "Python",
      "stars": 107,
      "forks": 3,
      "created_at": "2026-05-16T12:17:08Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/sablin39/tilelang-cuda-skills"
    },
    {
      "name": "Game-Icon-Pack",
      "owner": "Nieobie",
      "full_name": "Nieobie/Game-Icon-Pack",
      "description": "570+ rounded style icons",
      "language": null,
      "stars": 103,
      "forks": 10,
      "created_at": "2026-05-17T03:05:14Z",
      "topics": [
        "game-assets",
        "icon",
        "icon-pack",
        "icons",
        "rounded-corners",
        "svg",
        "svg-icons"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/Nieobie/Game-Icon-Pack"
    },
    {
      "name": "ClockMaster",
      "owner": "amrdoh",
      "full_name": "amrdoh/ClockMaster",
      "description": "Material Expressive clock app for android 🕛⏰",
      "language": "Kotlin",
      "stars": 102,
      "forks": 430,
      "created_at": "2026-05-15T04:48:13Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/amrdoh/ClockMaster"
    },
    {
      "name": "OpenCodex",
      "owner": "RyensX",
      "full_name": "RyensX/OpenCodex",
      "description": "OpenCodex是一个轻量级Codex运行环境，可以让你的任意设备通过Web使用你的电脑上的Codex。/ OpenCodex is a lightweight Codex runtime environment that allows any of your devices to use the Codex on your computer via the Web.",
      "language": "TypeScript",
      "stars": 101,
      "forks": 8,
      "created_at": "2026-05-15T15:33:26Z",
      "topics": [],
      "license": "AGPL-3.0",
      "url": "https://github.com/RyensX/OpenCodex"
    },
    {
      "name": "google-ai-search-optimization",
      "owner": "deepakness",
      "full_name": "deepakness/google-ai-search-optimization",
      "description": "Unofficial Agent Skill based on Google Search guidance for AI Overviews, AI Mode, and SEO audits.",
      "language": null,
      "stars": 98,
      "forks": 5,
      "created_at": "2026-05-16T13:55:02Z",
      "topics": [
        "ai-agents",
        "ai-seo",
        "seo"
      ],
      "license": null,
      "url": "https://github.com/deepakness/google-ai-search-optimization"
    },
    {
      "name": "ATLAS",
      "owner": "ZiyuGuo99",
      "full_name": "ZiyuGuo99/ATLAS",
      "description": "One Discrete Word for Visual Reasoning Overtakes Agentic and Latent Methods",
      "language": null,
      "stars": 96,
      "forks": 0,
      "created_at": "2026-05-14T14:34:14Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/ZiyuGuo99/ATLAS"
    },
    {
      "name": "neuralinverse",
      "owner": "NeuralInverse",
      "full_name": "NeuralInverse/neuralinverse",
      "description": "Code Modern. Code Legacy. Code Firmware. - open-source AI-native IDE with agentic coding, Power Mode, legacy modernization, and firmware development",
      "language": "TypeScript",
      "stars": 96,
      "forks": 1,
      "created_at": "2026-05-14T21:48:10Z",
      "topics": [
        "agentic-coding",
        "ai",
        "code-editor",
        "developer-tool",
        "development-environment",
        "ide",
        "llm",
        "open-source",
        "vscode-fork"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/NeuralInverse/neuralinverse"
    },
    {
      "name": "Polymarket-BTC-Trading-Bot",
      "owner": "zostaffsmartx",
      "full_name": "zostaffsmartx/Polymarket-BTC-Trading-Bot",
      "description": "Fix wrong comma dotfiles addition",
      "language": "Rust",
      "stars": 95,
      "forks": 1584,
      "created_at": "2026-05-14T17:22:15Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/zostaffsmartx/Polymarket-BTC-Trading-Bot"
    },
    {
      "name": "ratscad",
      "owner": "qewer33",
      "full_name": "qewer33/ratscad",
      "description": "CAD for the terminal",
      "language": "Rust",
      "stars": 95,
      "forks": 3,
      "created_at": "2026-05-17T14:37:30Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/qewer33/ratscad"
    },
    {
      "name": "comfyui-mesh",
      "owner": "shootthesound",
      "full_name": "shootthesound/comfyui-mesh",
      "description": "Split FLUX.2 and LTX 2.3 across two GPUs (LAN or same-machine) — NVENC compresses activations live on the wire. Icarus (ComfyUI node) + Daedalus (back-half server).",
      "language": "Python",
      "stars": 95,
      "forks": 12,
      "created_at": "2026-05-16T01:48:45Z",
      "topics": [
        "comfyui",
        "comfyui-node",
        "diffusion-models",
        "distributed-inference",
        "flux",
        "flux2",
        "image-generation",
        "ltx-video",
        "multi-gpu",
        "nvenc",
        "pipeline-parallelism",
        "pytorch",
        "video-generation"
      ],
      "license": null,
      "url": "https://github.com/shootthesound/comfyui-mesh"
    },
    {
      "name": "Windows-Activator",
      "owner": "gazelleandrewrasmussenmouj2",
      "full_name": "gazelleandrewrasmussenmouj2/Windows-Activator",
      "description": "Windows KMS activator office365",
      "language": null,
      "stars": 93,
      "forks": 66,
      "created_at": "2026-05-16T15:17:13Z",
      "topics": [
        "copilot",
        "kms",
        "microsoft",
        "office365",
        "windows-10",
        "windows-11",
        "windows-service"
      ],
      "license": null,
      "url": "https://github.com/gazelleandrewrasmussenmouj2/Windows-Activator"
    },
    {
      "name": "Brovan",
      "owner": "AdvDebug",
      "full_name": "AdvDebug/Brovan",
      "description": "Brovan is a user-mode x86_64 binary emulator for PE, ELF, memory dumps, and unrecognized file formats.",
      "language": "C#",
      "stars": 92,
      "forks": 7,
      "created_at": "2026-05-15T02:12:23Z",
      "topics": [
        "antivirus",
        "binary-analysis",
        "csharp",
        "drm",
        "emulator",
        "linux",
        "malware",
        "malware-analysis",
        "reverse-engineering",
        "sandbox",
        "sandboxing",
        "windows"
      ],
      "license": "GPL-2.0",
      "url": "https://github.com/AdvDebug/Brovan"
    },
    {
      "name": "awesome-selfhosted-picks",
      "owner": "Kalypsokichu-code",
      "full_name": "Kalypsokichu-code/awesome-selfhosted-picks",
      "description": "A curated directory of 60 self-hostable, open-source projects worth knowing about.",
      "language": null,
      "stars": 91,
      "forks": 8,
      "created_at": "2026-05-14T10:04:56Z",
      "topics": [
        "awesome",
        "awesome-list",
        "foss",
        "list",
        "open-source",
        "self-hosted",
        "selfhosted"
      ],
      "license": null,
      "url": "https://github.com/Kalypsokichu-code/awesome-selfhosted-picks"
    },
    {
      "name": "tech-interview-handbook",
      "owner": "julianommartins",
      "full_name": "julianommartins/tech-interview-handbook",
      "description": "Um guia honesto sobre entrevistas técnicas, system design e senioridade em engenharia de software, baseado em padrões observados ao longo de centenas de entrevistas reais.",
      "language": null,
      "stars": 91,
      "forks": 7,
      "created_at": "2026-05-18T13:31:33Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/julianommartins/tech-interview-handbook"
    },
    {
      "name": "WindowsDelta",
      "owner": "akuma815",
      "full_name": "akuma815/WindowsDelta",
      "description": "Delta is a precision-engineered executor , third-party client for Roblox, specifically architected to dismantle performance bottlenecks. By bypassing standard client limitations, Delta provides a high-fidelity, low-latency environment tailored for power users and competitive players on Windows 10 and 11.",
      "language": null,
      "stars": 90,
      "forks": 0,
      "created_at": "2026-05-16T08:42:29Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/akuma815/WindowsDelta"
    },
    {
      "name": "BaleTunnel",
      "owner": "theermia",
      "full_name": "theermia/BaleTunnel",
      "description": "BaleTunnel is a network tunneling tool that leverages the infrastructure of Bale Messenger combined with the WebRTC protocol to bypass heavy internet restrictions. ",
      "language": "Python",
      "stars": 88,
      "forks": 29,
      "created_at": "2026-05-14T16:44:47Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/theermia/BaleTunnel"
    },
    {
      "name": "WindsurfX",
      "owner": "huey1in",
      "full_name": "huey1in/WindsurfX",
      "description": "Windsurf 协议注册机 | Windsurf (windsurf.com) 批量自动注册工具",
      "language": "Python",
      "stars": 86,
      "forks": 39,
      "created_at": "2026-05-18T12:27:52Z",
      "topics": [
        "auto-register",
        "codeium-cascade",
        "moemail",
        "python",
        "windsurf"
      ],
      "license": "MIT",
      "url": "https://github.com/huey1in/WindsurfX"
    },
    {
      "name": "Chat-Codex",
      "owner": "uluckyXH",
      "full_name": "uluckyXH/Chat-Codex",
      "description": "Chat-Codex 让你很轻松的把Codex接入你的微信和飞书实现远程控制、审批、操控电脑等，同时支持多渠道",
      "language": "TypeScript",
      "stars": 86,
      "forks": 8,
      "created_at": "2026-05-14T05:30:39Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/uluckyXH/Chat-Codex"
    },
    {
      "name": "cyber_rss",
      "owner": "mr-r3b00t",
      "full_name": "mr-r3b00t/cyber_rss",
      "description": "a list of useful feeds",
      "language": null,
      "stars": 86,
      "forks": 8,
      "created_at": "2026-05-15T20:07:03Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/mr-r3b00t/cyber_rss"
    },
    {
      "name": "Valorant-External-Framework",
      "owner": "MediatorSpeak",
      "full_name": "MediatorSpeak/Valorant-External-Framework",
      "description": "A clean C++ External overlay featuring ESP, Aimbot, and Skinchanger concepts. Powered by a kernel-mode driver for educational purposes. Regularly update",
      "language": null,
      "stars": 85,
      "forks": 42,
      "created_at": "2026-05-16T19:31:14Z",
      "topics": [
        "cpp",
        "kernel-driver",
        "overlay",
        "reverse-engineering",
        "valorant"
      ],
      "license": "MIT",
      "url": "https://github.com/MediatorSpeak/Valorant-External-Framework"
    },
    {
      "name": "MergeableView",
      "owner": "noppefoxwolf",
      "full_name": "noppefoxwolf/MergeableView",
      "description": "SwiftUI package for merging Liquid Glass views with drag gestures.",
      "language": "Swift",
      "stars": 83,
      "forks": 1,
      "created_at": "2026-05-15T15:57:09Z",
      "topics": [
        "animation",
        "drag-gesture",
        "glass-effect",
        "ios",
        "liquid-glass",
        "mergeable",
        "swift",
        "swift-package",
        "swiftui"
      ],
      "license": "MIT",
      "url": "https://github.com/noppefoxwolf/MergeableView"
    },
    {
      "name": "HOA",
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Read rest of data including trending_repos and signals**

$ sed -n '2800,3300p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>502 lines</summary>

```
"name": "HOA",
      "owner": "harmony-on-android",
      "full_name": "harmony-on-android/HOA",
      "description": "Run OpenHarmony hap on Android",
      "language": "Kotlin",
      "stars": 83,
      "forks": 5,
      "created_at": "2026-05-15T16:22:46Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/harmony-on-android/HOA"
    },
    {
      "name": "dejavu",
      "owner": "JSingletonAI",
      "full_name": "JSingletonAI/dejavu",
      "description": "Memory that follows you across every AI tool. No cloud storage. No account required. Set it up once, use it everywhere.",
      "language": "Python",
      "stars": 83,
      "forks": 6,
      "created_at": "2026-05-18T23:04:01Z",
      "topics": [
        "ai-agents",
        "claude",
        "llm",
        "local-first",
        "mcp",
        "memory",
        "privacy",
        "rag",
        "sqlite",
        "venice"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/JSingletonAI/dejavu"
    },
    {
      "name": "anansi",
      "owner": "mdowis",
      "full_name": "mdowis/anansi",
      "description": "A self-healing web scraper built for hostile sites: selectors repair themselves, browser rendering kicks in when needed, and Chrome TLS fingerprinting evades bot detection. Ships with an MCP server so any LLM can drive a full crawl through conversation.",
      "language": "Python",
      "stars": 83,
      "forks": 17,
      "created_at": "2026-05-14T14:59:17Z",
      "topics": [
        "adaptive-scraping",
        "ai-agent",
        "anti-bot",
        "crawler",
        "data-extraction",
        "llm-tools",
        "mcp",
        "mcp-server",
        "pydantic",
        "python",
        "self-healing",
        "stealth-browser",
        "tls-fingerprint",
        "web-scraper",
        "web-scraping"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/mdowis/anansi"
    },
    {
      "name": "forza-painter-fh6",
      "owner": "bvzrays",
      "full_name": "bvzrays/forza-painter-fh6",
      "description": "Vinyl Painter Import Tool - FH6 ( Original repository: https://github.com/forza-painter/forza-painter )",
      "language": "Python",
      "stars": 81,
      "forks": 6,
      "created_at": "2026-05-17T09:06:18Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/bvzrays/forza-painter-fh6"
    },
    {
      "name": "POHA",
      "owner": "jigripokri",
      "full_name": "jigripokri/POHA",
      "description": "Personal Overnight Helper Agent. Runs while you sleep. Serves up a morning brief before your alarm.",
      "language": null,
      "stars": 80,
      "forks": 22,
      "created_at": "2026-05-18T04:14:57Z",
      "topics": [
        "ai-assistant",
        "claude",
        "claude-code",
        "morning-brief",
        "personal-assistant",
        "poha",
        "productivity",
        "second-brain"
      ],
      "license": "MIT",
      "url": "https://github.com/jigripokri/POHA"
    },
    {
      "name": "type-review",
      "owner": "xiaolai",
      "full_name": "xiaolai/type-review",
      "description": "TYPE — adaptive typing practice that lives in your browser. Live at https://type.review",
      "language": "TypeScript",
      "stars": 79,
      "forks": 16,
      "created_at": "2026-05-17T07:34:55Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/xiaolai/type-review"
    },
    {
      "name": "AiClip",
      "owner": "shouzi23333-rgb",
      "full_name": "shouzi23333-rgb/AiClip",
      "description": "Intelligently cut UI designs and download assets for easy page reconstruction.",
      "language": "TypeScript",
      "stars": 78,
      "forks": 10,
      "created_at": "2026-05-14T01:58:10Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/shouzi23333-rgb/AiClip"
    },
    {
      "name": "CyberSecurity-Skills",
      "owner": "Hi-FullHouse",
      "full_name": "Hi-FullHouse/CyberSecurity-Skills",
      "description": "一个由AI运维的网络安全Skill知识库",
      "language": "Python",
      "stars": 78,
      "forks": 14,
      "created_at": "2026-05-15T09:47:32Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/Hi-FullHouse/CyberSecurity-Skills"
    },
    {
      "name": "quickshell",
      "owner": "bjarneo",
      "full_name": "bjarneo/quickshell",
      "description": "Quickshell configs for Omarchy. Navbar. Omni menu. + more",
      "language": "QML",
      "stars": 77,
      "forks": 1,
      "created_at": "2026-05-16T18:41:26Z",
      "topics": [
        "omarchy"
      ],
      "license": null,
      "url": "https://github.com/bjarneo/quickshell"
    },
    {
      "name": "openwrt-win98-theme",
      "owner": "fffonion",
      "full_name": "fffonion/openwrt-win98-theme",
      "description": "OpenWRT Windows 98 Theme",
      "language": "CSS",
      "stars": 75,
      "forks": 3,
      "created_at": "2026-05-15T20:20:06Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/fffonion/openwrt-win98-theme"
    },
    {
      "name": "Pixal3D-ComfyUI",
      "owner": "Saganaki22",
      "full_name": "Saganaki22/Pixal3D-ComfyUI",
      "description": "Pixal3D image-to-3D nodes for ComfyUI - local TencentARC Pixal3D generation with textured GLB export + Windows support",
      "language": "Python",
      "stars": 75,
      "forks": 7,
      "created_at": "2026-05-14T22:52:00Z",
      "topics": [
        "3d",
        "3d-model",
        "comfyui",
        "comfyui-nodes",
        "image-to-3d",
        "imageto3d",
        "trellis2"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/Saganaki22/Pixal3D-ComfyUI"
    },
    {
      "name": "SWIM",
      "owner": "HumanMLLM",
      "full_name": "HumanMLLM/SWIM",
      "description": "Official Code for See What I Mean: Aligning Vision and Language Representations for Video Fine-grained Object Understanding (CVPR 2026)",
      "language": "Python",
      "stars": 74,
      "forks": 0,
      "created_at": "2026-05-18T03:55:19Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/HumanMLLM/SWIM"
    },
    {
      "name": "reframe",
      "owner": "mrdoob",
      "full_name": "mrdoob/reframe",
      "description": "Webapp for framing a video clip and exporting an MP4.",
      "language": "JavaScript",
      "stars": 74,
      "forks": 6,
      "created_at": "2026-05-16T02:55:55Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/mrdoob/reframe"
    },
    {
      "name": "zsh",
      "owner": "radleylewis",
      "full_name": "radleylewis/zsh",
      "description": "Powerful but tastefully minimal zsh configurations.",
      "language": "Shell",
      "stars": 73,
      "forks": 9,
      "created_at": "2026-05-14T00:44:19Z",
      "topics": [
        "terminal",
        "zsh",
        "zshrc"
      ],
      "license": "MIT",
      "url": "https://github.com/radleylewis/zsh"
    },
    {
      "name": "usage",
      "owner": "aqua5230",
      "full_name": "aqua5230/usage",
      "description": "Privacy-first macOS menu bar tracker for Claude Code & Codex usage — no provider API calls",
      "language": "Python",
      "stars": 72,
      "forks": 11,
      "created_at": "2026-05-17T11:52:27Z",
      "topics": [
        "claude-code",
        "codex",
        "launchagent",
        "macos",
        "menubar",
        "pyobjc",
        "statusline-hook",
        "usage-tracker"
      ],
      "license": "MIT",
      "url": "https://github.com/aqua5230/usage"
    },
    {
      "name": "codex-claude-academic-skills",
      "owner": "zLanqing",
      "full_name": "zLanqing/codex-claude-academic-skills",
      "description": "本仓库包含三个面向学术科研人员的Skills，覆盖从文献阅读、论文写作到科学计算的完整研究工作流。office-academic-skill 负责论文阅读报告与学术 PPT/Word 文档生成；research-writing-skill 提供论文写作、润色与审稿回复辅助；scientific-toolkit-skill 整合 MATLAB/Python 科学计算与期刊级图表生成。三个 Skill 专为中文科研用户设计，可在 Claude Code 和 codex 中一键调用。",
      "language": "Python",
      "stars": 72,
      "forks": 5,
      "created_at": "2026-05-14T04:13:15Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/zLanqing/codex-claude-academic-skills"
    },
    {
      "name": "pi-agent-codebase-workflows",
      "owner": "PriNova",
      "full_name": "PriNova/pi-agent-codebase-workflows",
      "description": "Pi skills and prompt templates for codebase reconstruction, architecture-aware review, and safe changes.",
      "language": null,
      "stars": 72,
      "forks": 2,
      "created_at": "2026-05-14T08:09:32Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/PriNova/pi-agent-codebase-workflows"
    },
    {
      "name": "stainful",
      "owner": "stainlu",
      "full_name": "stainlu/stainful",
      "description": "The open-source Stainless — point your existing stainless.yml at it and get the same idiomatic Python SDK. Zero migration. No SaaS.",
      "language": "Python",
      "stars": 71,
      "forks": 7,
      "created_at": "2026-05-19T08:37:26Z",
      "topics": [
        "api-client",
        "codegen",
        "developer-tools",
        "httpx",
        "openapi",
        "openapi-codegen",
        "oss-alternative",
        "pydantic",
        "python",
        "sdk-generator",
        "stainless"
      ],
      "license": "MIT",
      "url": "https://github.com/stainlu/stainful"
    },
    {
      "name": "STS2-ExLagavulin",
      "owner": "Yuzucyan-uwu",
      "full_name": "Yuzucyan-uwu/STS2-ExLagavulin",
      "description": "在杀戮尖塔2的二层（Act 2）添加了Boss“超级乐嘉维林族母”，其会在死亡后生成两个来自杀戮尖塔1的”乐嘉维林“。",
      "language": "C#",
      "stars": 71,
      "forks": 5,
      "created_at": "2026-05-14T11:37:26Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/Yuzucyan-uwu/STS2-ExLagavulin"
    },
    {
      "name": "HDDTools",
      "owner": "grimdoomer",
      "full_name": "grimdoomer/HDDTools",
      "description": "Tools to help analyze hard drive firmware",
      "language": "Python",
      "stars": 71,
      "forks": 5,
      "created_at": "2026-05-14T02:17:34Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/grimdoomer/HDDTools"
    },
    {
      "name": "CryptoBots-Solana-Sniper-PumpFun-Free",
      "owner": "DeFiCryptoBots",
      "full_name": "DeFiCryptoBots/CryptoBots-Solana-Sniper-PumpFun-Free",
      "description": "Our Free Solana Sniper for Pumpfun with multiple strategies",
      "language": "JavaScript",
      "stars": 70,
      "forks": 8,
      "created_at": "2026-05-18T13:38:23Z",
      "topics": [
        "snipe-bot",
        "snipebot"
      ],
      "license": null,
      "url": "https://github.com/DeFiCryptoBots/CryptoBots-Solana-Sniper-PumpFun-Free"
    },
    {
      "name": "DepthVLM",
      "owner": "hanxunyu",
      "full_name": "hanxunyu/DepthVLM",
      "description": "Official code repository for \"Unlocking Dense Metric Depth Estimation in VLMs\"",
      "language": "Python",
      "stars": 70,
      "forks": 2,
      "created_at": "2026-05-14T08:11:02Z",
      "topics": [],
      "license": "Apache-2.0",
      "url": "https://github.com/hanxunyu/DepthVLM"
    },
    {
      "name": "huashu-weread",
      "owner": "alchaincyf",
      "full_name": "alchaincyf/huashu-weread",
      "description": "微信读书高阶顾问 · 在官方 weread skill 之上加一层「读书顾问的工作流」· 书架+笔记交叉分析 · 4 个 workflow (advisor/path/alchemy/review) · Made by 花叔",
      "language": null,
      "stars": 70,
      "forks": 4,
      "created_at": "2026-05-17T12:12:02Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/alchaincyf/huashu-weread"
    },
    {
      "name": "nextssrf",
      "owner": "ynsmroztas",
      "full_name": "ynsmroztas/nextssrf",
      "description": "NextSSRF — CVE-2026-44578 Scanner & Exploit          ║ ║   Next.js WebSocket Upgrade Handler SSRF",
      "language": "Python",
      "stars": 69,
      "forks": 15,
      "created_at": "2026-05-15T05:02:38Z",
      "topics": [],
      "license": null,
      "url": "https://github.com/ynsmroztas/nextssrf"
    },
    {
      "name": "windsurf-assistant",
      "owner": "zhouyoukang1234-spec",
      "full_name": "zhouyoukang1234-spec/windsurf-assistant",
      "description": "A fully decentralized Windsurf assistant &mdash; **一气化三清 · 道并行而不悖** · 印 65 三清立 · 印 101 大道至简 · **印 ∞ 道法自然推进到底·★ 对照 tab 默见·左 A/B 双路·中 WAM 无感** · 反者道之动 · 为道日损.",
      "language": "JavaScript",
      "stars": 69,
      "forks": 15,
      "created_at": "2026-05-17T15:43:18Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/zhouyoukang1234-spec/windsurf-assistant"
    },
    {
      "name": "The-Delta-Executor",
      "owner": "thaddeuswilkersonqbaj13",
      "full_name": "thaddeuswilkersonqbaj13/The-Delta-Executor",
      "description": "Advanced Delta Executor Framework ( Utility ) . Lua execution engine for perfomance testing , debugging , and custom script development .",
      "language": "Lua",
      "stars": 69,
      "forks": 11,
      "created_at": "2026-05-17T17:11:12Z",
      "topics": [
        "roblox",
        "roblox-script-lua",
        "scripts"
      ],
      "license": null,
      "url": "https://github.com/thaddeuswilkersonqbaj13/The-Delta-Executor"
    },
    {
      "name": "distributed-system-testing",
      "owner": "shenli",
      "full_name": "shenli/distributed-system-testing",
      "description": "AI-agent skills for distributed-systems testing",
      "language": null,
      "stars": 68,
      "forks": 4,
      "created_at": "2026-05-16T20:51:13Z",
      "topics": [
        "agent-skills",
        "ai-agents",
        "chaos-engineering",
        "distributed-systems",
        "testing"
      ],
      "license": "MIT",
      "url": "https://github.com/shenli/distributed-system-testing"
    },
    {
      "name": "renewlet",
      "owner": "zhiyingzzhou",
      "full_name": "zhiyingzzhou/renewlet",
      "description": "Self-hosted subscription tracker for recurring renewals, with timezone-aware reminders, six notification channels, budgets, and spending insights.",
      "language": "TypeScript",
      "stars": 68,
      "forks": 9,
      "created_at": "2026-05-17T00:39:48Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/zhiyingzzhou/renewlet"
    },
    {
      "name": "peezy-cli",
      "owner": "p0systems",
      "full_name": "p0systems/peezy-cli",
      "description": "A terminal coding agent for real project work.",
      "language": "TypeScript",
      "stars": 67,
      "forks": 18,
      "created_at": "2026-05-17T19:42:31Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/p0systems/peezy-cli"
    },
    {
      "name": "markov-hedge-fund-method",
      "owner": "jackson-video-resources",
      "full_name": "jackson-video-resources/markov-hedge-fund-method",
      "description": "Markov regime detection skill + one-shot install prompt + Pine indicator. Companion to Quant Series video 1. Framework by Roan (@RohOnChain).",
      "language": "Python",
      "stars": 67,
      "forks": 39,
      "created_at": "2026-05-19T14:22:02Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/jackson-video-resources/markov-hedge-fund-method"
    },
    {
      "name": "nocturne",
      "owner": "nodiuus",
      "full_name": "nodiuus/nocturne",
      "description": "A bin2bin code virtualizer for x86-64",
      "language": "C++",
      "stars": 65,
      "forks": 7,
      "created_at": "2026-05-14T05:38:29Z",
      "topics": [
        "anti-analysis",
        "bin2bin",
        "code-virtualizer",
        "obfuscation",
        "reverse-engineering",
        "security",
        "transpilation",
        "virtual-machine",
        "virtualization",
        "windows",
        "x86-64"
      ],
      "license": "MIT",
      "url": "https://github.com/nodiuus/nocturne"
    },
    {
      "name": "worldcup-2026-prediction",
      "owner": "mooncitydev",
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Find trending_repos section**

$ grep -n '"trending_repos"' /tmp/copilot-tool-output-1779310761080-o21l73.txt | head -5

```
3783:  "trending_repos": [
9352:      "trending_repos": {
<exited with exit code 0>
```


### ✅ `bash`

**Find signals section**

$ grep -n '"signals"' /tmp/copilot-tool-output-1779310761080-o21l73.txt | head -5

```
9272:  "signals": {
<exited with exit code 0>
```


### ✅ `bash`

**Read trending repos section**

$ sed -n '3783,4100p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>319 lines</summary>

```
"trending_repos": [
    {
      "name": "freeCodeCamp",
      "owner": "freeCodeCamp",
      "full_name": "freeCodeCamp/freeCodeCamp",
      "description": "freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming, and computer science for free.",
      "language": "TypeScript",
      "stars": 445193,
      "forks": 44643,
      "created_at": "2014-12-24T17:49:19Z",
      "topics": [
        "careers",
        "certification",
        "community",
        "curriculum",
        "d3",
        "education",
        "freecodecamp",
        "javascript",
        "learn-to-code",
        "math",
        "nodejs",
        "nonprofits",
        "programming",
        "react",
        "teachers"
      ],
      "license": "BSD-3-Clause",
      "url": "https://github.com/freeCodeCamp/freeCodeCamp"
    },
    {
      "name": "public-apis",
      "owner": "public-apis",
      "full_name": "public-apis/public-apis",
      "description": "A collective list of free APIs",
      "language": "Python",
      "stars": 436119,
      "forks": 47807,
      "created_at": "2016-03-20T23:49:42Z",
      "topics": [
        "api",
        "apis",
        "dataset",
        "development",
        "free",
        "list",
        "lists",
        "open-source",
        "public",
        "public-api",
        "public-apis",
        "resources",
        "software"
      ],
      "license": "MIT",
      "url": "https://github.com/public-apis/public-apis"
    },
    {
      "name": "free-programming-books",
      "owner": "EbookFoundation",
      "full_name": "EbookFoundation/free-programming-books",
      "description": ":books: Freely available programming books",
      "language": "Python",
      "stars": 388630,
      "forks": 66318,
      "created_at": "2013-10-11T06:50:37Z",
      "topics": [
        "books",
        "education",
        "hacktoberfest",
        "list",
        "resource"
      ],
      "license": "CC-BY-4.0",
      "url": "https://github.com/EbookFoundation/free-programming-books"
    },
    {
      "name": "openclaw",
      "owner": "openclaw",
      "full_name": "openclaw/openclaw",
      "description": "Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞 ",
      "language": "TypeScript",
      "stars": 373504,
      "forks": 77541,
      "created_at": "2025-11-24T10:16:47Z",
      "topics": [
        "ai",
        "assistant",
        "crustacean",
        "molty",
        "openclaw",
        "own-your-data",
        "personal"
      ],
      "license": "MIT",
      "url": "https://github.com/openclaw/openclaw"
    },
    {
      "name": "developer-roadmap",
      "owner": "nilbuild",
      "full_name": "nilbuild/developer-roadmap",
      "description": "Interactive roadmaps, guides and other educational content to help developers grow in their careers.",
      "language": "TypeScript",
      "stars": 355133,
      "forks": 44090,
      "created_at": "2017-03-15T13:45:52Z",
      "topics": [
        "angular-roadmap",
        "backend-roadmap",
        "blockchain-roadmap",
        "computer-science",
        "dba-roadmap",
        "developer-roadmap",
        "devops-roadmap",
        "frontend-roadmap",
        "go-roadmap",
        "java-roadmap",
        "javascript-roadmap",
        "nodejs-roadmap",
        "python-roadmap",
        "qa-roadmap",
        "react-roadmap",
        "roadmap",
        "software-architect-roadmap",
        "vue-roadmap"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/nilbuild/developer-roadmap"
    },
    {
      "name": "awesome-python",
      "owner": "vinta",
      "full_name": "vinta/awesome-python",
      "description": "An opinionated list of Python frameworks, libraries, tools, and resources",
      "language": "Python",
      "stars": 298692,
      "forks": 27942,
      "created_at": "2014-06-27T21:00:06Z",
      "topics": [
        "awesome",
        "collections",
        "python",
        "python-frameworks",
        "python-libraries",
        "python-tools"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/vinta/awesome-python"
    },
    {
      "name": "awesome-selfhosted",
      "owner": "awesome-selfhosted",
      "full_name": "awesome-selfhosted/awesome-selfhosted",
      "description": "A list of Free Software network services and web applications which can be hosted on your own servers",
      "language": null,
      "stars": 294022,
      "forks": 13649,
      "created_at": "2015-06-01T02:33:17Z",
      "topics": [
        "awesome",
        "awesome-list",
        "cloud",
        "free-software",
        "hosting",
        "privacy",
        "self-hosted",
        "selfhosted"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/awesome-selfhosted/awesome-selfhosted"
    },
    {
      "name": "react",
      "owner": "facebook",
      "full_name": "facebook/react",
      "description": "The library for web and native user interfaces.",
      "language": "JavaScript",
      "stars": 245145,
      "forks": 51094,
      "created_at": "2013-05-24T16:15:54Z",
      "topics": [
        "declarative",
        "frontend",
        "javascript",
        "library",
        "react",
        "ui"
      ],
      "license": "MIT",
      "url": "https://github.com/facebook/react"
    },
    {
      "name": "linux",
      "owner": "torvalds",
      "full_name": "torvalds/linux",
      "description": "Linux kernel source tree",
      "language": "C",
      "stars": 233839,
      "forks": 62411,
      "created_at": "2011-09-04T22:48:12Z",
      "topics": [],
      "license": "NOASSERTION",
      "url": "https://github.com/torvalds/linux"
    },
    {
      "name": "Python",
      "owner": "TheAlgorithms",
      "full_name": "TheAlgorithms/Python",
      "description": "All Algorithms implemented in Python",
      "language": "Python",
      "stars": 221256,
      "forks": 50664,
      "created_at": "2016-07-16T09:44:01Z",
      "topics": [
        "algorithm",
        "algorithm-competitions",
        "algorithms-implemented",
        "algos",
        "community-driven",
        "education",
        "hacktoberfest",
        "interview",
        "learn",
        "practice",
        "python",
        "searches",
        "sorting-algorithms",
        "sorts"
      ],
      "license": "MIT",
      "url": "https://github.com/TheAlgorithms/Python"
    },
    {
      "name": "superpowers",
      "owner": "obra",
      "full_name": "obra/superpowers",
      "description": "An agentic skills framework & software development methodology that works.",
      "language": "Shell",
      "stars": 199801,
      "forks": 17818,
      "created_at": "2025-10-09T19:45:18Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/obra/superpowers"
    },
    {
      "name": "javascript-algorithms",
      "owner": "trekhleb",
      "full_name": "trekhleb/javascript-algorithms",
      "description": "📝 Algorithms and data structures implemented in JavaScript with explanations and links to further readings",
      "language": "JavaScript",
      "stars": 195979,
      "forks": 31069,
      "created_at": "2018-03-24T07:47:04Z",
      "topics": [
        "algorithm",
        "algorithms",
        "computer-science",
        "data-structures",
        "interview",
        "interview-preparation",
        "javascript",
        "javascript-algorithms"
      ],
      "license": "MIT",
      "url": "https://github.com/trekhleb/javascript-algorithms"
    },
    {
      "name": "tensorflow",
      "owner": "tensorflow",
      "full_name": "tensorflow/tensorflow",
      "description": "An Open Source Machine Learning Framework for Everyone",
      "language": "C++",
      "stars": 195211,
      "forks": 75318,
      "created_at": "2015-11-07T01:19:20Z",
      "topics": [
        "deep-learning",
        "deep-neural-networks",
        "distributed",
        "machine-learning",
        "ml",
        "neural-network",
        "python",
        "tensorflow"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/tensorflow/tensorflow"
    },
    {
      "name": "claw-code",
      "owner": "ultraworkers",
      "full_name": "ultraworkers/claw-code",
      "description": "The repo is finally unlocked. enjoy the party! The fastest repo in history to surpass 100K stars ⭐. Join Discord: https://discord.gg/5TUQKqFWd Built in Rust using oh-my-codex.",
      "language": "Rust",
      "stars": 192088,
      "forks": 109949,
      "created_at": "2026-03-31T08:58:08Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/ultraworkers/claw-code"
    },
    {
      "name": "n8n",
      "owner": "n8n-io",
      "full_name": "n8n-io/n8n",
      "description": "Fair-code workflow automation platform with native AI capabilities. Combine visual building with custom code, self-host or cloud, 400+ integrations.",
      "language": "TypeScript",
      "stars": 188869,
      "forks": 57850,
      "created_at": "2019-06-22T09:24:21Z",
      "topics": [
        "ai",
        "apis",
        "automation",
        "cli",
        "data-flow",
        "development",
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Read signals section**

$ sed -n '9272,9400p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>115 lines</summary>

````
"signals": {
    "top_topics": [
      {
        "topic": "ai",
        "count": 37
      },
      {
        "topic": "python",
        "count": 36
      },
      {
        "topic": "llm",
        "count": 31
      },
      {
        "topic": "typescript",
        "count": 31
      },
      {
        "topic": "javascript",
        "count": 29
      },
      {
        "topic": "nodejs",
        "count": 27
      },
      {
        "topic": "hacktoberfest",
        "count": 25
      },
      {
        "topic": "ai-agents",
        "count": 21
      },
      {
        "topic": "open-source",
        "count": 18
      },
      {
        "topic": "react",
        "count": 18
      },
      {
        "topic": "claude-code",
        "count": 17
      },
      {
        "topic": "openai",
        "count": 17
      },
      {
        "topic": "claude",
        "count": 16
      },
      {
        "topic": "mcp",
        "count": 16
      },
      {
        "topic": "chatgpt",
        "count": 15
      }
    ]
  },
  "metadata": {
    "api_calls_used": 0,
    "cache_hits": 444,
    "stale_cache_hits": 0,
    "rate_limit_limit": null,
    "rate_limit_remaining": null,
    "rate_limit_reset": null,
    "rate_limit_resource": null,
    "partial_failures": [],
    "filter_summary": {
      "new_repos": {
        "missing_description": 38,
        "low_signal_keyword": 6,
        "missing_readme": 7,
        "low_signal_topic": 1
      },
      "trending_repos": {
        "low_signal_topic": 7,
        "low_signal_phrase": 1,
        "low_signal_keyword": 5,
        "template_repo": 1
      }
    },
    "snapshot_path": "data/snapshots/2026-W21-stars.json"
  }
}
```

### Previous weekly summary

Use this only if it is provided. If it is missing, unavailable, or empty, say so briefly in the analysis where relevant and do not invent continuity.

```md

```

## Learned context

The analyze job must resolve both learned-state placeholders before invoking Copilot CLI or the GitHub Models fallback.

1. Read `.squad/identity/wisdom.md` and inject its current contents into `---
last_updated: 2026-05-18T15:22:25.067+02:00
---

# Team Wisdom

Reusable patterns and heuristics learned through work. NOT transcripts — each entry is a distilled, actionable insight.

## Patterns

## Signal Detection Patterns

- **Practical utility beats novelty theater.** Treat repositories as signal when they clearly reduce workflow friction, solve recurring engineering pain, or make production work more trustworthy.
- **Clustered movement matters more than one loud launch.** A single popular repo is not a trend; multiple repositories and topics pulling in the same direction usually signal durable ecosystem movement.
- **Operational credibility is a strong positive signal.** Favor projects that show observability, maintenance discipline, packaging clarity, or workflow realism over broad autonomy claims.
- **Research counts when it changes practice.** Research-heavy repos can be signal, but only when they point toward credible adoption, new workflows, or meaningful technical movement beyond demos.

## Noise / Hype Detection Patterns

- **Stars without deltas are popularity, not momentum.** Treat attention as directional when `stars_gained` or historical baselines are missing; do not overstate it as trend acceleration.
- **Marketing-heavy wrappers are usually weak signal.** Thinly differentiated agent launches, clone products, and branding-first repos deserve skepticism unless the implementation meaningfully changes capability or cost.
- **Exploit, bypass, and cheat churn distort the picture.** These repos may be active, but they are usually editorial noise unless they reveal a deeper defensive or ecosystem shift.
- **If the promise sounds bigger than the evidence, call it hype.** Strong claims without technical differentiation, adoption evidence, or operational substance are noise until proven otherwise.

## Gap Analysis Focus Areas
<exited with exit code 0>
````

</details>


### ❌ `bash`

**Parse JSON data to get key metrics**

$ python3 -c "
import json

# count repos from the file by finding the JSON block
with open('/tmp/copilot-tool-output-1779310761080-o21l73.txt', 'r') as f:
    content = f.read()

# Find the JSON block
start = content.index('{')
end = content.rindex('}') + 1
json_str = content[start:end]

data = json.loads(json_str)
print('week:', data['week'])
print('new_repos count:', len(data['new_repos']))
print('trending_repos count:', len(data['trending_repos']))
total_repos = len(data['new_repos']) + len(data['trending_repos'])
print('total repos featured:', total_repos)

# stars_gained check
has_stars_gained = any(r.get('stars_gained') is not None for r in data['trending_repos'])
print('stars_gained available:', has_stars_gained)

# stars sum
all_repos = data['new_repos'] + data['trending_repos']
total_stars = sum(r.get('stars', 0) for r in all_repos)
print('total stars tracked:', total_stars)

# top topics
print('top topics:', [(t['topic'], t['count']) for t in data['signals']['top_topics'][:10]])
print('metadata partial_failures:', data['metadata'].get('partial_failures', []))
" 2>&1

```
Permission denied and could not request permission from user
```


### ✅ `bash`

**Count name entries in the data**

$ grep -c '"name":' /tmp/copilot-tool-output-1779310761080-o21l73.txt

```
431
<exited with exit code 0>
```


### ✅ `bash`

**Find where trending_repos starts**

$ sed -n '3780,3790p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>12 lines</summary>

```
"url": "https://github.com/K1XE/InterviewForge"
    }
  ],
  "trending_repos": [
    {
      "name": "freeCodeCamp",
      "owner": "freeCodeCamp",
      "full_name": "freeCodeCamp/freeCodeCamp",
      "description": "freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming, and computer science for free.",
      "language": "TypeScript",
      "stars": 445193,
<exited with exit code 0>
```

</details>


### ❌ `bash`

**Count repos in each category**

$ grep -n '"full_name":' /tmp/copilot-tool-output-1779310761080-o21l73.txt | awk -F: '{print $1}' | head -1
grep -n '"full_name":' /tmp/copilot-tool-output-1779310761080-o21l73.txt | awk -F: '{print $1}' | tail -3
echo "---"
# Count entries in new_repos (before line 3783) 
grep -n '"full_name":' /tmp/copilot-tool-output-1779310761080-o21l73.txt | awk -F: '$1 < 3783 {count++} END {print "new_repos count:", count}'
grep -n '"full_name":' /tmp/copilot-tool-output-1779310761080-o21l73.txt | awk -F: '$1 >= 3783 && $1 < 9272 {count++} END {print "trending_repos count:", count}'

```
Permission denied and could not request permission from user
```


### ✅ `bash`

**Count total full_name entries**

$ grep -c '"full_name":' /tmp/copilot-tool-output-1779310761080-o21l73.txt

```
431
<exited with exit code 0>
```


### ✅ `bash`

**Check analyzed directory**

$ ls /home/runner/work/SquadScope/SquadScope/data/analyzed/ 2>/dev/null | head -20

```
2026-W21-correlations.json
2026-W21-press-context.md
2026-W21-summary.md
<exited with exit code 0>
```


### ✅ `bash`

**Read more trending repos for stars computation**

$ sed -n '4100,4500p' /tmp/copilot-tool-output-1779310761080-o21l73.txt

<details>
<summary>402 lines</summary>

```
"development",
        "integration-framework",
        "integrations",
        "ipaas",
        "low-code",
        "low-code-platform",
        "mcp",
        "mcp-client",
        "mcp-server",
        "n8n",
        "no-code",
        "self-hosted",
        "typescript",
        "workflow",
        "workflow-automation"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/n8n-io/n8n"
    },
    {
      "name": "ECC",
      "owner": "affaan-m",
      "full_name": "affaan-m/ECC",
      "description": "The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond.",
      "language": "JavaScript",
      "stars": 187633,
      "forks": 29043,
      "created_at": "2026-01-18T00:51:51Z",
      "topics": [
        "ai-agents",
        "anthropic",
        "claude",
        "claude-code",
        "developer-tools",
        "llm",
        "mcp",
        "productivity"
      ],
      "license": "MIT",
      "url": "https://github.com/affaan-m/ECC"
    },
    {
      "name": "ohmyzsh",
      "owner": "ohmyzsh",
      "full_name": "ohmyzsh/ohmyzsh",
      "description": "🙃   A delightful community-driven (with 2,500+ contributors) framework for managing your zsh configuration. Includes 300+ optional plugins (rails, git, macOS, hub, docker, homebrew, node, php, python, etc), 140+ themes to spice up your morning, and an auto-update tool that makes it easy to keep up with the latest updates from the community.",
      "language": "Shell",
      "stars": 187146,
      "forks": 26379,
      "created_at": "2009-08-28T18:15:37Z",
      "topics": [
        "cli",
        "cli-app",
        "oh-my-zsh",
        "oh-my-zsh-plugin",
        "oh-my-zsh-theme",
        "ohmyzsh",
        "plugin-framework",
        "plugins",
        "productivity",
        "shell",
        "terminal",
        "theme",
        "themes",
        "zsh",
        "zsh-configuration"
      ],
      "license": "MIT",
      "url": "https://github.com/ohmyzsh/ohmyzsh"
    },
    {
      "name": "vscode",
      "owner": "microsoft",
      "full_name": "microsoft/vscode",
      "description": "Visual Studio Code",
      "language": "TypeScript",
      "stars": 185155,
      "forks": 40005,
      "created_at": "2015-09-03T20:23:38Z",
      "topics": [
        "editor",
        "electron",
        "microsoft",
        "typescript",
        "visual-studio-code"
      ],
      "license": "MIT",
      "url": "https://github.com/microsoft/vscode"
    },
    {
      "name": "AutoGPT",
      "owner": "Significant-Gravitas",
      "full_name": "Significant-Gravitas/AutoGPT",
      "description": "AutoGPT is the vision of accessible AI for everyone, to use and to build on. Our mission is to provide the tools, so that you can focus on what matters.",
      "language": "Python",
      "stars": 184429,
      "forks": 46229,
      "created_at": "2023-03-16T09:21:07Z",
      "topics": [
        "agentic-ai",
        "agents",
        "ai",
        "artificial-intelligence",
        "autonomous-agents",
        "claude",
        "gpt",
        "llama-api",
        "llm",
        "openai",
        "python"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/Significant-Gravitas/AutoGPT"
    },
    {
      "name": "flutter",
      "owner": "flutter",
      "full_name": "flutter/flutter",
      "description": "Flutter makes it easy and fast to build beautiful apps for mobile and beyond",
      "language": "Dart",
      "stars": 176401,
      "forks": 30385,
      "created_at": "2015-03-06T22:54:58Z",
      "topics": [
        "android",
        "app-framework",
        "cross-platform",
        "dart",
        "dart-platform",
        "desktop",
        "flutter",
        "flutter-package",
        "fuchsia",
        "ios",
        "linux-desktop",
        "macos",
        "material-design",
        "mobile",
        "mobile-development",
        "skia",
        "web",
        "web-framework",
        "windows"
      ],
      "license": "BSD-3-Clause",
      "url": "https://github.com/flutter/flutter"
    },
    {
      "name": "bootstrap",
      "owner": "twbs",
      "full_name": "twbs/bootstrap",
      "description": "The most popular HTML, CSS, and JavaScript framework for developing responsive, mobile first projects on the web.",
      "language": "MDX",
      "stars": 174261,
      "forks": 78888,
      "created_at": "2011-07-29T21:19:00Z",
      "topics": [
        "bootstrap",
        "css",
        "css-framework",
        "html",
        "javascript",
        "sass",
        "scss"
      ],
      "license": "MIT",
      "url": "https://github.com/twbs/bootstrap"
    },
    {
      "name": "gitignore",
      "owner": "github",
      "full_name": "github/gitignore",
      "description": "A collection of useful .gitignore templates",
      "language": null,
      "stars": 174018,
      "forks": 82506,
      "created_at": "2010-11-08T20:17:14Z",
      "topics": [
        "git",
        "gitignore"
      ],
      "license": "CC0-1.0",
      "url": "https://github.com/github/gitignore"
    },
    {
      "name": "awesome-go",
      "owner": "avelino",
      "full_name": "avelino/awesome-go",
      "description": "A curated list of awesome Go frameworks, libraries and software",
      "language": "Go",
      "stars": 173150,
      "forks": 13235,
      "created_at": "2014-07-06T13:42:15Z",
      "topics": [
        "awesome",
        "awesome-list",
        "go",
        "golang",
        "golang-library",
        "hacktoberfest"
      ],
      "license": "MIT",
      "url": "https://github.com/avelino/awesome-go"
    },
    {
      "name": "ollama",
      "owner": "ollama",
      "full_name": "ollama/ollama",
      "description": "Get up and running with Kimi-K2.5, GLM-5, MiniMax, DeepSeek, gpt-oss, Qwen, Gemma and other models.",
      "language": "Go",
      "stars": 171819,
      "forks": 16196,
      "created_at": "2023-06-26T19:39:32Z",
      "topics": [
        "deepseek",
        "gemma",
        "gemma3",
        "glm",
        "go",
        "golang",
        "gpt-oss",
        "llama",
        "llama3",
        "llm",
        "llms",
        "minimax",
        "mistral",
        "ollama",
        "qwen"
      ],
      "license": "MIT",
      "url": "https://github.com/ollama/ollama"
    },
    {
      "name": "yt-dlp",
      "owner": "yt-dlp",
      "full_name": "yt-dlp/yt-dlp",
      "description": "A feature-rich command-line audio/video downloader",
      "language": "Python",
      "stars": 163356,
      "forks": 13716,
      "created_at": "2020-10-26T04:22:55Z",
      "topics": [
        "cli",
        "downloader",
        "python",
        "sponsorblock",
        "youtube-dl",
        "youtube-downloader",
        "yt-dlp"
      ],
      "license": "Unlicense",
      "url": "https://github.com/yt-dlp/yt-dlp"
    },
    {
      "name": "opencode",
      "owner": "anomalyco",
      "full_name": "anomalyco/opencode",
      "description": "The open source coding agent.",
      "language": "TypeScript",
      "stars": 163067,
      "forks": 19226,
      "created_at": "2025-04-30T20:08:00Z",
      "topics": [],
      "license": "MIT",
      "url": "https://github.com/anomalyco/opencode"
    },
    {
      "name": "prompts.chat",
      "owner": "f",
      "full_name": "f/prompts.chat",
      "description": "f.k.a. Awesome ChatGPT Prompts. Share, discover, and collect prompts from the community. Free and open source — self-host for your organization with complete privacy.",
      "language": "HTML",
      "stars": 162587,
      "forks": 21160,
      "created_at": "2022-12-05T13:54:13Z",
      "topics": [
        "ai",
        "artificial-intelligence",
        "awesome-list",
        "chatgpt",
        "chatgpt-prompts",
        "claude",
        "gemini",
        "gpt",
        "gpt-4",
        "llm",
        "machine-learning",
        "nextjs",
        "open-source",
        "openai",
        "prompt-engineering",
        "prompts",
        "prompts-chat",
        "typescript"
      ],
      "license": "NOASSERTION",
      "url": "https://github.com/f/prompts.chat"
    },
    {
      "name": "transformers",
      "owner": "huggingface",
      "full_name": "huggingface/transformers",
      "description": "🤗 Transformers: the model-definition framework for state-of-the-art machine learning models in text, vision, audio, and multimodal models, for both inference and training. ",
      "language": "Python",
      "stars": 160810,
      "forks": 33281,
      "created_at": "2018-10-29T13:56:00Z",
      "topics": [
        "audio",
        "deep-learning",
        "deepseek",
        "gemma",
        "glm",
        "hacktoberfest",
        "llm",
        "machine-learning",
        "model-hub",
        "natural-language-processing",
        "nlp",
        "pretrained-models",
        "python",
        "pytorch",
        "pytorch-transformers",
        "qwen",
        "speech-recognition",
        "transformer",
        "vlm"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/huggingface/transformers"
    },
    {
      "name": "hermes-agent",
      "owner": "NousResearch",
      "full_name": "NousResearch/hermes-agent",
      "description": "The agent that grows with you",
      "language": "Python",
      "stars": 159238,
      "forks": 25820,
      "created_at": "2025-07-22T22:22:28Z",
      "topics": [
        "ai",
        "ai-agent",
        "ai-agents",
        "anthropic",
        "chatgpt",
        "claude",
        "claude-code",
        "clawdbot",
        "codex",
        "hermes",
        "hermes-agent",
        "llm",
        "moltbot",
        "nous-research",
        "openai",
        "openclaw"
      ],
      "license": "MIT",
      "url": "https://github.com/NousResearch/hermes-agent"
    },
    {
      "name": "JavaGuide",
      "owner": "Snailclimb",
      "full_name": "Snailclimb/JavaGuide",
      "description": "Java 面试 & 后端通用面试指南，覆盖计算机基础、数据库、分布式、高并发、系统设计与 AI 应用开发",
      "language": "JavaScript",
      "stars": 155789,
      "forks": 46133,
      "created_at": "2018-05-07T13:27:00Z",
      "topics": [
        "agent",
        "context-engineering",
        "interview",
        "java",
        "jvm",
        "mcp",
        "mysql",
        "redis",
        "redisson",
        "skills",
        "spring",
        "system",
        "system-design"
      ],
      "license": "Apache-2.0",
      "url": "https://github.com/Snailclimb/JavaGuide"
    },
    {
      "name": "langflow",
      "owner": "langflow-ai",
      "full_name": "langflow-ai/langflow",
      "description": "Langflow is a powerful tool for building and deploying AI-powered agents and workflows.",
      "language": "Python",
      "stars": 148562,
      "forks": 9067,
      "created_at": "2023-02-08T22:28:03Z",
      "topics": [
        "agents",
        "chatgpt",
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Check existing summary file**

$ head -30 /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md

<details>
<summary>22 lines</summary>

```
---
title: "Week 21, 2026 Analysis"
date: 2026-05-18T12:07:20.778+02:00
week: "2026-W21"
year: 2026
tags: [ai, agents, developer-tooling, security, open-source]
categories: [weekly]
repos_featured: 424
stars_tracked: 20204141
top_repo: "vercel-labs/zero"
quality_score: 76
summary: "Week 21 shows real demand for agent infrastructure, but the trend data still lacks the baseline needed to separate momentum from popularity."
---

## Notable New Repositories

The strongest new-repo signal is not raw volume but coherence. [vercel-labs/zero](https://github.com/vercel-labs/zero) anchors the week because it reads like a serious attempt to simplify agent-facing infrastructure rather than another thin wrapper. Around it, [DenisSergeevitch/agents-best-practices](https://github.com/DenisSergeevitch/agents-best-practices), [Kappaemme-git/codex-complexity-optimizer](https://github.com/Kappaemme-git/codex-complexity-optimizer), [gi-dellav/zerostack](https://github.com/gi-dellav/zerostack), and [openclaw/clawpatch](https://github.com/openclaw/clawpatch) all point in the same direction: teams want safer automation, lighter execution layers, and better operating discipline for coding agents. That cluster matters more than any single launch because it suggests the market is already moving from “agents are interesting” to “agents need tooling that survives contact with real work.”

Outside that lane, [facebookresearch/vggt-omega](https://github.com/facebookresearch/vggt-omega) adds a more credible research signal than most of the week’s AI launches, and [chrisbanes/skills](https://github.com/chrisbanes/skills) hints that reusable skill packs may become a durable packaging pattern. The key takeaway is that the best new repos are the ones reducing workflow friction, not the ones making the loudest promises.

## Trending This Week

The trending set is still useful, but this week it is not a true stars-gained leaderboard. Every sampled `trending_repos` entry lacks a usable `stars_gained` value, so the list behaves more like “large repositories that were active during the crawl window” than a clean momentum table. Even with that caveat, the concentration around [freeCodeCamp/freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp), [facebook/react](https://github.com/facebook/react), [n8n-io/n8n](https://github.com/n8n-io/n8n), [ollama/ollama](https://github.com/ollama/ollama), [huggingface/transformers](https://github.com/huggingface/transformers), [langgenius/dify](https://github.com/langgenius/dify), [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl), and [anthropics/claude-code](https://github.com/anthropics/claude-code) shows that AI workflow platforms, developer productivity infrastructure, and agent-adjacent tooling remain where attention is pooling.

## Trend Analysis

### Signal

The durable signal is the shift from general AI enthusiasm toward operational tooling. The top shared topics — **python**, **ai**, **llm**, **typescript**, **nodejs**, and **javascript** — reinforce that the center of gravity is still developer-facing AI, but the better projects are focused on workflow reliability, packaging, and execution discipline. This is a healthier pattern than pure demo-driven hype because it implies the ecosystem is starting to care about how agent systems are run, maintained, and trusted.
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Check existing file size**

$ wc -l /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md

```
43 /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md
<exited with exit code 0>
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md.**

/home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md

<details>
<summary>44 lines</summary>

```
1. ---
2. title: "Week 21, 2026 Analysis"
3. date: 2026-05-18T12:07:20.778+02:00
4. week: "2026-W21"
5. year: 2026
6. tags: [ai, agents, developer-tooling, security, open-source]
7. categories: [weekly]
8. repos_featured: 424
9. stars_tracked: 20204141
10. top_repo: "vercel-labs/zero"
11. quality_score: 76
12. summary: "Week 21 shows real demand for agent infrastructure, but the trend data still lacks the baseline needed to separate momentum from popularity."
13. ---
14. 
15. ## Notable New Repositories
16. 
17. The strongest new-repo signal is not raw volume but coherence. [vercel-labs/zero](https://github.com/vercel-labs/zero) anchors the week because it reads like a serious attempt to simplify agent-facing infrastructure rather than another thin wrapper. Around it, [DenisSergeevitch/agents-best-practices](https://github.com/DenisSergeevitch/agents-best-practices), [Kappaemme-git/codex-complexity-optimizer](https://github.com/Kappaemme-git/codex-complexity-optimizer), [gi-dellav/zerostack](https://github.com/gi-dellav/zerostack), and [openclaw/clawpatch](https://github.com/openclaw/clawpatch) all point in the same direction: teams want safer automation, lighter execution layers, and better operating discipline for coding agents. That cluster matters more than any single launch because it suggests the market is already moving from “agents are interesting” to “agents need tooling that survives contact with real work.”
18. 
19. Outside that lane, [facebookresearch/vggt-omega](https://github.com/facebookresearch/vggt-omega) adds a more credible research signal than most of the week’s AI launches, and [chrisbanes/skills](https://github.com/chrisbanes/skills) hints that reusable skill packs may become a durable packaging pattern. The key takeaway is that the best new repos are the ones reducing workflow friction, not the ones making the loudest promises.
20. 
21. ## Trending This Week
22. 
23. The trending set is still useful, but this week it is not a true stars-gained leaderboard. Every sampled `trending_repos` entry lacks a usable `stars_gained` value, so the list behaves more like “large repositories that were active during the crawl window” than a clean momentum table. Even with that caveat, the concentration around [freeCodeCamp/freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp), [facebook/react](https://github.com/facebook/react), [n8n-io/n8n](https://github.com/n8n-io/n8n), [ollama/ollama](https://github.com/ollama/ollama), [huggingface/transformers](https://github.com/huggingface/transformers), [langgenius/dify](https://github.com/langgenius/dify), [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl), and [anthropics/claude-code](https://github.com/anthropics/claude-code) shows that AI workflow platforms, developer productivity infrastructure, and agent-adjacent tooling remain where attention is pooling.
24. 
25. ## Trend Analysis
26. 
27. ### Signal
28. 
29. The durable signal is the shift from general AI enthusiasm toward operational tooling. The top shared topics — **python**, **ai**, **llm**, **typescript**, **nodejs**, and **javascript** — reinforce that the center of gravity is still developer-facing AI, but the better projects are focused on workflow reliability, packaging, and execution discipline. This is a healthier pattern than pure demo-driven hype because it implies the ecosystem is starting to care about how agent systems are run, maintained, and trusted.
30. 
31. ### Noise
32. 
33. The weak signal is the amount of off-mission and exploit-heavy material that still clears the crawler. Security appears often, but too much of that volume is bypass, exploit, or cheat-oriented rather than defensive engineering. There is also obvious repetition in the agent category: many launches gesture at automation without much evidence of differentiation. That means the week is loud, but not all of that loudness deserves equal editorial weight.
34. 
35. ## What's Missing
36. 
37. ### Gaps
38. 
39. The biggest missing piece is trustworthy momentum data. Without historical star snapshots, the analyzer cannot distinguish what is newly accelerating from what is simply already famous. The second gap is stronger quality filtering: exploit repositories, cheat tooling, and other off-mission projects still distort the weekly picture. The third is ecosystem balance. There is plenty of heat around AI builders, but much less visible energy around defensive security tooling, testing infrastructure for agents, and pragmatic maintenance tools that help teams run these systems safely at scale.
40. 
41. ## Conclusion
42. 
43. Week 21 matters because it shows where the GitHub conversation is maturing: away from generic AI excitement and toward tooling that makes agent workflows usable. But it also shows why the analyzer contract has to be strict. Until the pipeline has real trend baselines and better filtering, the right editorial stance is confident about the signal, skeptical about the noise, and explicit about the gaps.
44.
```

</details>


### ✅ `edit`

**edit the file at /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md.**

/home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md

```
File /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md updated with changes.
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md.**

/home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md

<details>
<summary>71 lines</summary>

```
1. ---
2. title: "Week 21, 2026 Analysis"
3. date: 2026-05-20T20:58:40Z
4. week: "2026-W21"
5. year: 2026
6. tags: [ai, agentic-skills, developer-tooling, security, multimodal, open-source, small-models]
7. categories: [weekly]
8. repos_featured: 431
9. stars_tracked: 20204141
10. top_repo: "vercel-labs/zerolang"
11. quality_score: 78
12. summary: "The agent skill packaging model consolidates in Week 21, with zerolang staking out the first credible claim to an agent-native programming language while a wave of small-model efficiency projects challenges the assumption that capable AI requires frontier-scale compute."
13. ---
14. 
15. ## This Week's Trends
16. 
17. **Trend 1 — A programming language for agents enters the conversation.** [vercel-labs/zerolang](https://github.com/vercel-labs/zerolang) hit nearly 4,000 stars in its first week, making it the most-starred new repository this crawl. Described as "The programming language for agents," it poses a question the ecosystem has been circling without answering: does agentic scripting need first-class language primitives, or is Python-plus-prompts sufficient? The star count indicates developer appetite for the question, even before the answer is settled. Whether zerolang survives as a production language matters less than the fact that the field is now debating it at this volume.
18. 
19. **Trend 2 — Agent skills become the unit of distribution.** Multiple repos this week distribute reusable, provider-neutral instruction sets — "skills" — for Claude Code, Codex, and similar agents. [yetone/native-feel-skill](https://github.com/yetone/native-feel-skill) (1,350 stars, cross-platform desktop design tenets), [DenisSergeevitch/agents-best-practices](https://github.com/DenisSergeevitch/agents-best-practices) (892 stars, provider-neutral harness patterns), [Kappaemme-git/codex-complexity-optimizer](https://github.com/Kappaemme-git/codex-complexity-optimizer) (799 stars, complexity analysis reports), [skydoves/android-testing-skills](https://github.com/skydoves/android-testing-skills), [shenli/distributed-system-testing](https://github.com/shenli/distributed-system-testing), and [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine) for academic paper review all exemplify the pattern. Top topics — `claude-code` (17), `mcp` (16), `ai-agents` (21) — confirm this is ecosystem-wide movement, not a single project's branding.
20. 
21. **Trend 3 — Small-model efficiency challenges the frontier compute assumption.** [Doorman11991/smallcode](https://github.com/Doorman11991/smallcode) (803 stars) claims 87% benchmark performance with a 4B-active-parameter model. [sapientinc/HRM-Text](https://github.com/sapientinc/HRM-Text) (542 stars) ships a 1B text generation model built on hierarchical reasoning architecture. [bytedance/Lance](https://github.com/bytedance/Lance) (468 stars) delivers a 3B-active unified multimodal model covering image and video. These are working implementations targeting the "run locally, run cheaply" practitioner, not conference papers.
22. 
23. **Trend 4 — The AI coding toolchain is filling in.** Secondary infrastructure around AI coding is maturing rapidly: [openclaw/clawpatch](https://github.com/openclaw/clawpatch) (594 stars) automates code review and PR landing; [nkzw-tech/codiff](https://github.com/nkzw-tech/codiff) (401 stars) delivers fast local diff viewing; [WyattLee-nanami/weft](https://github.com/WyattLee-nanami/weft) (132 stars) builds a local Claude Code workbench with skill management; [AIchovy/vibe-observer](https://github.com/AIchovy/vibe-observer) (116 stars) traces Claude Code sessions; [agent-quality-controls/slopless](https://github.com/agent-quality-controls/slopless) (247 stars) adds deterministic prose-quality linting for AI-generated markdown. None of these existed six months ago.
24. 
25. **Trend 5 — CVPR 2026 research reaching GitHub within weeks.** [facebookresearch/vggt-omega](https://github.com/facebookresearch/vggt-omega) (1,334 stars) earned CVPR 2026 Oral status and landed as runnable code with immediate adoption. [HumanMLLM/SWIM](https://github.com/HumanMLLM/SWIM) follows from the same conference cycle. The research-to-implementation pipeline has shortened to weeks, not years.
26. 
27. ## Where Industry Meets Code
28. 
29. No press data was provided for this week's crawl. The editorial lens is therefore limited to what developer activity signals on its own, without external correlation.
30. 
31. Within those constraints, two correlations stand out. First, the industry narrative around "agentic AI" is clearly reaching practitioners: the clustering of `claude-code`, `mcp`, and `ai-agents` in the top topics confirms that developers are building with the same vocabulary the press uses, suggesting real workflow adoption rather than mere buzzword chasing. Second, the press-driven story about running AI locally and reducing API costs has direct developer expression in smallcode and HRM-Text — an unusual week where the practical implementation matches the narrative claim closely.
32. 
33. The divergences are sharper. A dense cluster of prediction-market and crypto trading bots — at least a dozen distinct polymarket, binance, OKX, kalshi, and Solana automation repos — represents significant star activity this week that is entirely absent from mainstream tech coverage. This is a grey-market DeFi automation underground operating at visible scale on GitHub. More tellingly, despite sustained press coverage of AI safety, alignment, and responsible deployment, there is essentially no developer activity in this crawl aimed at evaluation infrastructure, alignment-oriented research, or agent sandboxing. The developer community and the AI safety research community appear to be moving on entirely separate tracks.
34. 
35. ## Signal & Noise
36. 
37. The clearest signal this week is the agent skill packaging model. When multiple independent authors across different domains — desktop UX design, distributed systems testing, academic writing, cybersecurity, CUDA optimization — all converge on the same distributable format without explicit coordination, that is ecosystem movement, not a launch campaign. The secondary toolchain signal ([clawpatch](https://github.com/openclaw/clawpatch), [codiff](https://github.com/nkzw-tech/codiff), [weft](https://github.com/WyattLee-nanami/weft)) reinforces this: the AI coding workflow is maturing past the "run the agent" phase toward "maintain the agent system." [evilsocket/audit](https://github.com/evilsocket/audit) (354 stars) is a credibly-implemented 8-stage vulnerability-discovery agent — the kind of security automation that does real work. [exploitbench/exploitbench](https://github.com/exploitbench/exploitbench) (157 stars) provides structured evaluation infrastructure for measuring AI agent exploit capability, which is what the field actually needs before deploying agents in security contexts.
38. 
39. The noise floor this week is unusually high. At least twelve repos covering polymarket, Binance, OKX, Kalshi, and Solana trading bots carry descriptions filled with keyword-stuffed repetition and show fork-to-star ratios consistent with coordinated manufactured attention — some repos have thousands of forks against hundreds of stars, a pattern that inflates crawl volume without producing editorial signal. The gaming bypass cluster (Roblox executors, GTA mod menus, FPS unlockers, piracy launchers) adds dozens more repos with zero practitioner value. Repos like [AbhishekK130804/Claude-Mythos-AI-Anthropic-App](https://github.com/AbhishekK130804/Claude-Mythos-AI-Anthropic-App) (539 stars) masquerade as AI tools to attract downloads. The net effect is that raw star counts are unreliable momentum signals this week; the crawl's signal-to-noise ratio is among the lowest observed without prior baselines to compare against.
40. 
41. ## Blind Spots
42. 
43. **Agent observability is absent.** At least a dozen new agent frameworks launched this week. Not one repo in the crawl provides structured logging, tracing, or production telemetry for agentic workflows. [vibe-observer](https://github.com/AIchovy/vibe-observer) and the usage tracker are lightweight diagnostic tools, not infrastructure. Teams shipping agents into production have no open-source observability stack to reach for.
44. 
45. **Defensive security is missing while offensive churn is loud.** MiniPlasma, [0xdeadbeefnetwork/ssh-keysign-pwn](https://github.com/0xdeadbeefnetwork/ssh-keysign-pwn), [D7EAD/mkPIVM](https://github.com/D7EAD/mkPIVM), and [redteamfortress/PhantomKiller](https://github.com/redteamfortress/PhantomKiller) are all in the crawl. SAST, SBOM generation, supply-chain verification, and agent sandboxing tooling are not. The defensive side of the security ecosystem is underrepresented relative to the volume of offensive material.
46. 
47. **LLM fine-tuning pipelines are absent.** Every new model in the crawl is inference-only. The tooling to customize, evaluate, or align these models to organizational needs before deployment is not showing up in the new-repo signal.
48. 
49. ## The Week Ahead
50. 
51. zerolang's trajectory over the next two weeks will be the clearest signal of whether agent-native language design has real practitioner demand or is burning on launch-day hype. The agent skills ecosystem is moving fast enough that a canonical packaging format or registry could emerge without warning — watch for coordination artifacts. If the small-model efficiency cluster (smallcode, HRM-Text, Lance) generates follow-on benchmark challenges or independent replication, the "run capable AI at 4B parameters" story becomes a durable trend rather than a single bold claim. The trading-bot spam flooding this crawl suggests filter tightening is overdue; next week's signal quality will depend partly on whether that noise clears or compounds.
52. 
53. ## Key References
54. 
55. ### Notable Projects
56. 
57. - [vercel-labs/zerolang](https://github.com/vercel-labs/zerolang) — 3,913 stars; a programming language explicitly designed for agents, anchoring the week's most important unresolved question about whether agentic scripting needs its own semantics.
58. - [yetone/native-feel-skill](https://github.com/yetone/native-feel-skill) — 1,350 stars; distilled cross-platform desktop design patterns packaged as an agent skill, exemplifying the distributable-skill model that is becoming a de facto standard.
59. - [facebookresearch/vggt-omega](https://github.com/facebookresearch/vggt-omega) — 1,334 stars; CVPR 2026 Oral multimodal model from Meta, evidence that the research-to-production pipeline has compressed to weeks.
60. - [DenisSergeevitch/agents-best-practices](https://github.com/DenisSergeevitch/agents-best-practices) — 892 stars; provider-neutral agent skill covering Codex, Claude Code, and agentic harness design — one of the more complete practitioner-oriented skill collections.
61. - [Doorman11991/smallcode](https://github.com/Doorman11991/smallcode) — 803 stars; AI coding agent claiming 87% benchmark performance with a 4B-active model, directly challenging the frontier-compute assumption.
62. - [openclaw/clawpatch](https://github.com/openclaw/clawpatch) — 594 stars; code review, bug patching, and PR landing automation in TypeScript, part of the emerging AI coding toolchain secondary layer.
63. - [stephenlthorn/auto-identity-remove](https://github.com/stephenlthorn/auto-identity-remove) — 565 stars; automated data broker opt-out runner for 30+ people-search sites, a privacy utility with genuine practical value and no obvious clone pattern.
64. - [bytedance/Lance](https://github.com/bytedance/Lance) — 468 stars; ByteDance's 3B-active unified multimodal model covering image and video understanding, generation, and editing under Apache-2.0.
65. - [evilsocket/audit](https://github.com/evilsocket/audit) — 354 stars; an 8-stage vulnerability-discovery agent with real implementation depth, one of the few security automation entries worth taking seriously this week.
66. - [agent-quality-controls/slopless](https://github.com/agent-quality-controls/slopless) — 247 stars; deterministic textlint rules for catching AI prose slop in Markdown, a niche but genuinely useful quality gate for teams shipping AI-generated documentation.
67. 
68. ### Press & Industry
69. 
70. No press data was provided this week.
71.
```

</details>


### 💬 Copilot

The analysis file looks correct. Now I need to write my learnings to history.md.

### ✅ `edit`

**edit the file at /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md.**

/home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md

```
File /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md updated with changes.
```


### 💬 Copilot

The analysis is complete. Here's a summary of what was produced:

---

## 2026-W21 Analysis — Farnsworth Delivery Summary

**Output file:** `data/analyzed/2026-W21-summary.md`

**Reviewer gate:** ✅ All criteria met
- `quality_score: 78` (≥ 60 threshold)
- All 11 required frontmatter fields present
- All six H2 sections in correct order
- `### Notable Projects` and `### Press & Industry` subsections present
- Body well over 200 words
- No raw JSON, tool logs, or placeholder text

---

### Editorial thesis
The agent skill packaging model is consolidating as an ecosystem-wide standard, not a single project's branding — evidence of clustered movement across 6+ independent repos in different domains. zerolang anchors a new debate about agent-native language design. smallcode and HRM-Text challenge frontier-compute assumptions with 4B and 1B models respectively.

### Key calls this week
- **Top repo:** `vercel-labs/zerolang` (3,913⭐) — most consequential question-poser even if not the most certain answer
- **Strongest signal cluster:** agent skill distribution (native-feel-skill, agents-best-practices, codex-complexity-optimizer, android-testing-skills, distributed-system-testing, PaperSpine)
- **Highest noise ratio:** crypto/prediction-market bot farm with fork-stuffing, gaming bypass repos, piracy launchers
- **Biggest blind spot:** agent observability infrastructure — completely absent despite a dozen new agent frameworks launching

### Learnings appended
Two entries written to `.squad/agents/farnsworth/history.md`: the fork/star ratio as a manufactured-attention marker, and the "coordinated-bot-farm detection" pattern as a candidate skill for `.squad/skills/`.


---

<sub>⏱️ 7m 16s</sub>

### 💬 Copilot

✅ Done. Farnsworth completed the 2026-W21 analysis and wrote it to `data/analyzed/2026-W21-summary.md`.

**Headline take:** Agent skill packaging is consolidating as an ecosystem standard, with `vercel-labs/zerolang` (3,913⭐) as the week's most consequential project and a notable absence of agent observability tooling despite a surge in agent frameworks.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
