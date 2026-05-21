# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `648be6ec-3766-4a31-8546-c0d757752eb1`  
> - **Started:** 5/21/2026, 8:39:43 AM  
> - **Duration:** 7m 36s  
> - **Exported:** 5/21/2026, 8:47:20 AM  

---

<sub>⏱️ 1s</sub>

### 👤 User

Farnsworth, read the file at /tmp/tmp.dRnWFvkwwr — it contains the weekly data and analysis instructions. Follow them exactly and write the analysis to data/analyzed/2026-W21-summary.md.

---

<sub>⏱️ 9s</sub>

### ✅ `bash`

**Read the weekly data file**

$ cat /tmp/tmp.dRnWFvkwwr

<details>
<summary>20 lines</summary>

````
Output too large to read at once (318.0 KB). Saved to: /tmp/copilot-tool-output-1779352793717-j6z9tt.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-21T08:39:29Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-21T08:38:38Z",
  "new_repos": [
    {
      "name
<exited with exit code 0>
````

</details>


---

<sub>⏱️ 15s</sub>

### 💬 Copilot

The file is large (318KB). Farnsworth's on it — reading the full data and writing the analysis now.

---

<sub>⏱️ 15s</sub>

### 📦 task (Completed)

### ✅ `bash`

**List contents of the analysis directory**

$ ls /tmp/tmp.dRnWFvkwwr/

```
ls: cannot access '/tmp/tmp.dRnWFvkwwr/': Not a directory
<exited with exit code 2>
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth.**

/home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth

```
charter.md
history.md
notifications
```


### ✅ `bash`

**Check file type and size**

$ file /tmp/tmp.dRnWFvkwwr && wc -c /tmp/tmp.dRnWFvkwwr

```
/tmp/tmp.dRnWFvkwwr: Unicode text, UTF-8 text, with very long lines (374)
325310 /tmp/tmp.dRnWFvkwwr
<exited with exit code 0>
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/charter.md.**

/home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/charter.md

<details>
<summary>26 lines</summary>

```
1. # Farnsworth — Analyst
2. 
3. > Separates signal from noise and turns raw repo motion into editorial judgment.
4. 
5. ## Identity
6. - **Name:** Farnsworth
7. - **Role:** Analyst / Content Curator
8. - **Expertise:** trend analysis, editorial synthesis, category framing, weekly brief structure
9. 
10. ## What I Own
11. - Weekly analysis markdown consumed by the site generator
12. - Editorial framing for what is hot, important, trending, and missing
13. - Tagging and narrative structure for trend reports
14. 
15. ## How I Work
16. - Favor durable ecosystem signals over short-lived hype spikes.
17. - Explain why a pattern matters, not just that it appeared.
18. - Keep analysis useful to both readers and downstream automation.
19. 
20. ## Boundaries
21. **I handle:** analysis content, trend framing, editorial synthesis, and taxonomy judgment
22. **I don't handle:** data collection, frontend implementation, or architecture decisions
23. 
24. ## Model
25. Preferred: auto
26.
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md.**

/home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md

<details>
<summary>15 lines</summary>

```
1. # Farnsworth — History
2. 
3. ## Core Context
4. - Owns editorial analysis of GitHub and adjacent press signals for the published weekly brief.
5. - Analysis output must stay useful to readers and structured enough for downstream automation.
6. 
7. ## Learnings
8. - The analyzer contract should remain a superset of the published weekly frontmatter plus the quality gate so one artifact serves editorial and pipeline needs.
9. - Weekly briefs work best as named macro trends supported by repo evidence, with repo links rendered from the crawl artifact's `url` field.
10. - Press and industry coverage are correlation signals, not material to repackage; the value is in explaining the gap between narrative and developer traction.
11. - Reader-facing renders need a cleanup pass that strips AI-only scaffolding before publication.
12. - The learning loop only matters when lessons are persisted and injected back into the next prompt through shared wisdom and skills.
13. - The squad reskill audit showed repeated charter and history scaffolding across agents; that boilerplate now lives in `minimal-agent-charter`, `agent-history-hygiene`, and `weekly-learning-loop`.
14. - The reskill pass also cut squad agent-doc footprint from 39568 to 12521 bytes, with every charter at or below the 1.5 KB target and the largest histories back under maintenance limits.
15.
```

</details>


### ✅ `glob`

****/*.md**

"**/*.md" in .squad/skills

<details>
<summary>7 matches</summary>

```
/home/runner/work/SquadScope/SquadScope/.squad/skills/branch-protection-pr-workflow/SKILL.md
/home/runner/work/SquadScope/SquadScope/.squad/skills/ci-data-source-integration-pattern/SKILL.md
/home/runner/work/SquadScope/SquadScope/.squad/skills/agent-history-hygiene/SKILL.md
/home/runner/work/SquadScope/SquadScope/.squad/skills/exponential-backoff-with-jitter/SKILL.md
/home/runner/work/SquadScope/SquadScope/.squad/skills/minimal-agent-charter/SKILL.md
/home/runner/work/SquadScope/SquadScope/.squad/skills/weekly-learning-loop/SKILL.md
/home/runner/work/SquadScope/SquadScope/.squad/skills/pr-review-thread-resolution/SKILL.md
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


### ✅ `bash`

**Read the full analysis prompt and data**

$ cat /tmp/tmp.dRnWFvkwwr

<details>
<summary>20 lines</summary>

````
Output too large to read at once (318.0 KB). Saved to: /tmp/copilot-tool-output-1779352817818-xj2nwr.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-21T08:39:29Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-21T08:38:38Z",
  "new_repos": [
    {
      "name
<exited with exit code 0>
````

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/.squad/skills/weekly-learning-loop/SKILL.md.**

/home/runner/work/SquadScope/SquadScope/.squad/skills/weekly-learning-loop/SKILL.md

<details>
<summary>31 lines</summary>

```
1. ---
2. name: "weekly-learning-loop"
3. description: "Make analysis improvements stick by loading agent identity, persisting learnings, and reinjecting them into the next cycle."
4. domain: "analysis-operations"
5. confidence: "high"
6. source: "recurring learnings in Bender, Farnsworth, Hermes, and Leela histories"
7. ---
8. 
9. ## Context
10. 
11. A weekly AI workflow only improves if lessons survive the run that produced them. The loop is incomplete when learnings are written down but never loaded back into the next prompt.
12. 
13. ## Patterns
14. 
15. - Load the correct agent identity before analysis or reskill work begins.
16. - Persist durable outcomes in history, wisdom, or skill files as part of the same operating cycle.
17. - Inject shared wisdom and skills into the next prompt so the model can act on prior learning.
18. - Keep fallback paths aligned with the same prompt contract so learnings apply across execution modes.
19. 
20. ## Examples
21. 
22. - Good: call Copilot CLI with the registered agent name, not a file path.
23. - Good: store a repeatable lesson in `.squad/skills/` once it shows up across multiple agents.
24. - Good: render prompts with shared wisdom and skill context so new runs inherit the last run's conclusions.
25. 
26. ## Anti-Patterns
27. 
28. - Treating a post-run note as sufficient when the next run never reads it.
29. - Letting the fallback path drift to a different output contract.
30. - Keeping important learnings only in a single dated history entry.
31.
```

</details>


### ✅ `bash`

**Read first 50KB of the prompt file**

$ head -c 50000 /tmp/copilot-tool-output-1779352817818-xj2nwr.txt

<details>
<summary>20 lines</summary>

````
Output too large to read at once (49.1 KB). Saved to: /tmp/copilot-tool-output-1779352821976-kxcx0x.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Weekly Analysis Prompt Template

You are Farnsworth, the analyst for SquadScope.

Your job is to turn one weekly crawler artifact into a structured editorial summary for publication.

## Inputs

- Current datetime: `2026-05-21T08:39:29Z`
- Raw weekly JSON path: `data/raw/2026-W21.json`
- Output path: `data/analyzed/2026-W21-summary.md`
- Previous summary path: `None`

### Raw weekly JSON

```json
{
  "week": "2026-W21",
  "crawled_at": "2026-05-21T08:38:38Z",
  "new_repos": [
    {
      "name
<exited with exit code 0>
````

</details>


### ❌ `bash`

**Parse the raw JSON to get key stats**

$ cat data/raw/2026-W21.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Week:', data['week'])
print('Crawled at:', data['crawled_at'])
print('New repos count:', len(data['new_repos']))
print('Trending repos count:', len(data['trending_repos']))
print('Top topics:', data['signals']['top_topics'][:20])
print('Metadata keys:', list(data.get('metadata', {}).keys()))
"

```
Permission denied and could not request permission from user
```


### ❌ `bash`

**Parse the raw JSON data**

$ python3 -c "
import json
with open('data/raw/2026-W21.json') as f:
    data = json.load(f)
print('Week:', data['week'])
print('Crawled at:', data['crawled_at'])
print('New repos count:', len(data['new_repos']))
print('Trending repos count:', len(data['trending_repos']))
print('Top topics:', json.dumps(data['signals']['top_topics'][:20], indent=2))
print()
meta = data.get('metadata', {})
print('Metadata:', {k: v for k,v in meta.items() if k not in ['filter_summary']})
if 'filter_summary' in meta:
    print('Filter summary:', json.dumps(meta['filter_summary'], indent=2))
if 'partial_failures' in meta:
    print('Partial failures:', meta['partial_failures'])
" 2>&1


```
Permission denied and could not request permission from user
```


### ✅ `bash`

**List raw and analyzed data directories**

$ ls data/raw/ && ls data/analyzed/

```
2026-W21-techcrunch.json  2026-W21.json
2026-W21-correlations.json  2026-W21-press-context.md  2026-W21-summary.md
<exited with exit code 0>
```


### ✅ `bash`

**Check file sizes**

$ wc -l data/raw/2026-W21.json data/raw/2026-W21-techcrunch.json data/analyzed/2026-W21-correlations.json data/analyzed/2026-W21-press-context.md data/analyzed/2026-W21-summary.md

<details>
<summary>7 lines</summary>

```
8316 data/raw/2026-W21.json
   414 data/raw/2026-W21-techcrunch.json
  4455 data/analyzed/2026-W21-correlations.json
   372 data/analyzed/2026-W21-press-context.md
    43 data/analyzed/2026-W21-summary.md
 13600 total
<exited with exit code 0>
```

</details>


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


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-press-context.md.**

/home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-press-context.md

```
File too large to read at once (25.5 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21-techcrunch.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21-techcrunch.json

<details>
<summary>415 lines</summary>

```
1. {
2.   "week": "2026-W21",
3.   "source": "techcrunch",
4.   "crawled_at": "2026-05-21T08:39:14.474016Z",
5.   "articles": [
6.     {
7.       "title": "Truecaller gets into the eSIM business to diversify its revenue streams",
8.       "url": "https://techcrunch.com/2026/05/20/truecaller-gets-into-the-esim-business-to-diversify-its-revenue-streams/",
9.       "published_at": "2026-05-21T06:00:00Z",
10.       "categories": [
11.         "Apps",
12.         "esim",
13.         "travel",
14.         "Truecaller"
15.       ],
16.       "summary": "The company said its plans will range from 1 GB over 7 days to 20 GB over 30 days. Initially, the launch will make the eSIM product available in 29 countries.",
17.       "github_links": [],
18.       "entities": [
19.         "Truecaller"
20.       ],
21.       "relevance_score": 0.2
22.     },
23.     {
24.       "title": "General Catalyst just led a $63M bet on India’s travel payments market",
25.       "url": "https://techcrunch.com/2026/05/20/indian-travel-fintech-scapia-more-than-doubles-valuation-to-over-500m-in-a-year/",
26.       "published_at": "2026-05-21T05:52:38Z",
27.       "categories": [
28.         "Fintech",
29.         "Startups",
30.         "General Catalyst",
31.         "Peak XV Partners",
32.         "Scapia",
33.         "Z47"
34.       ],
35.       "summary": "Scapia, an Indian startup that combines travel booking with co-branded credit cards and mobile payments, said the deal doubles its valuation.",
36.       "github_links": [],
37.       "entities": [
38.         "General",
39.         "Catalyst",
40.         "India"
41.       ],
42.       "relevance_score": 0.6
43.     },
44.     {
45.       "title": "Imperagen raises £5 million to use quantum physics, AI on enzyme engineering",
46.       "url": "https://techcrunch.com/2026/05/20/imperagen-raises-5-million-to-redefine-enzyme-engineering/",
47.       "published_at": "2026-05-21T04:00:00Z",
48.       "categories": [
49.         "Startups",
50.         "Biotech & Health",
51.         "Venture",
52.         "biotech"
53.       ],
54.       "summary": "Biotech company Imperagen announced on Thursday a £5 million ($6.7 million) seed round led by PXN Ventures, with participation from IQ Capital and Northern Gritstone.",
55.       "github_links": [],
56.       "entities": [
57.         "Imperagen",
58.         "AI"
59.       ],
60.       "relevance_score": 0.8
61.     },
62.     {
63.       "title": "Jensen Huang says he’s found a ‘brand new’ $200B market for Nvidia",
64.       "url": "https://techcrunch.com/2026/05/20/jensen-huang-says-hes-found-a-brand-new-200b-market-for-nvidia/",
65.       "published_at": "2026-05-21T00:28:31Z",
66.       "categories": [
67.         "AI",
68.         "Enterprise",
69.         "TC",
70.         "cpus",
71.         "nvidia"
72.       ],
73.       "summary": "The next big thing for Nvidia will be CPUs for AI agents, $200 billion worth, CEO Jensen Huang predicts.",
74.       "github_links": [],
75.       "entities": [
76.         "Jensen",
77.         "Huang",
78.         "Nvidia"
79.       ],
80.       "relevance_score": 0.4
81.     },
82.     {
83.       "title": "Anthropic says it’s about to have its first profitable quarter",
84.       "url": "https://techcrunch.com/2026/05/20/anthropic-says-its-about-to-have-its-first-profitable-quarter/",
85.       "published_at": "2026-05-21T00:21:21Z",
86.       "categories": [
87.         "AI",
88.         "Anthropic",
89.         "Claude",
90.         "OpenAI"
91.       ],
92.       "summary": "Anthropic has told its investors that it will more than double revenue to around $10.9 billion in its second quarter.",
93.       "github_links": [],
94.       "entities": [
95.         "Anthropic"
96.       ],
97.       "relevance_score": 0.2
98.     },
99.     {
100.       "title": "The SpaceX IPO filing is filled with AI bets, Starship dreams, and Elon Musk at the center",
101.       "url": "https://techcrunch.com/2026/05/20/the-spacex-ipo-filing-ai-bets-starship-dreams-elon-musk/",
102.       "published_at": "2026-05-20T23:03:02Z",
103.       "categories": [
104.         "Space",
105.         "Transportation",
106.         "Elon Musk",
107.         "IPOs",
108.         "SpaceX",
109.         "rockets",
110.         "xAI",
111.         "Starlink"
112.       ],
113.       "summary": "SpaceX has finally made the contents of its IPO filing public, weeks ahead of what is expected to be the largest IPO ever and one that will make Musk the CEO, CTO, and chairman of the board.",
114.       "github_links": [],
115.       "entities": [
116.         "SpaceX",
117.         "IPO",
118.         "AI",
119.         "Starship",
120.         "Elon",
121.         "Musk"
122.       ],
123.       "relevance_score": 0.2
124.     },
125.     {
126.       "title": "Clouted wants to take the guesswork out of making short videos go viral",
127.       "url": "https://techcrunch.com/2026/05/20/clouted-wants-to-take-the-guesswork-out-of-making-short-videos-go-viral/",
128.       "published_at": "2026-05-20T22:30:45Z",
129.       "categories": [
130.         "AI",
131.         "Media & Entertainment",
132.         "Startups",
133.         "Clouted",
134.         "Marketing",
135.         "slow ventures",
136.         "social media"
137.       ],
138.       "summary": "The video clipping startup raised a $7 million seed round led by Slow Ventures.",
139.       "github_links": [],
140.       "entities": [
141.         "Clouted"
142.       ],
143.       "relevance_score": 0.4
144.     },
145.     {
146.       "title": "xAI burned $6.4B last year — SpaceX’s IPO filing shows why the spending is far from over",
147.       "url": "https://techcrunch.com/2026/05/20/xai-burned-6-4b-last-year-spacexs-ipo-filing-shows-why-the-spending-is-far-from-over/",
148.       "published_at": "2026-05-20T22:26:08Z",
149.       "categories": [
150.         "AI",
151.         "Space",
152.         "Elon Musk",
153.         "Grok",
154.         "SpaceX",
155.         "spacex ipo",
156.         "X"
157.       ],
158.       "summary": "SpaceX's IPO filing reveals xAI lost $6.4 billion in 2025 while planning a massive Grok expansion — offering the first public look at Elon Musk's AI financials and more details about his ambitions.",
159.       "github_links": [],
160.       "entities": [
161.         "SpaceX",
162.         "IPO"
163.       ],
164.       "relevance_score": 0.2
165.     },
166.     {
167.       "title": "Nvidia posts another record quarter, reveals $43B of holdings in startups",
168.       "url": "https://techcrunch.com/2026/05/20/nvidia-posts-another-record-quarter-reveals-43-billion-of-holdings-in-startups/",
169.       "published_at": "2026-05-20T22:03:51Z",
170.       "categories": [
171.         "AI",
172.         "earnings",
173.         "Jensen Huang",
174.         "nvidia"
175.       ],
176.       "summary": "Nvidia announced another record revenue figure after market close on Wednesday, but forecasted that revenue growth would slow in the following quarter.",
177.       "github_links": [],
178.       "entities": [
179.         "Nvidia"
180.       ],
181.       "relevance_score": 0.4
182.     },
183.     {
184.       "title": "Musk’s xAI is being sued over its data center generators — now it’s buying $2.8B more",
185.       "url": "https://techcrunch.com/2026/05/20/musks-xai-is-being-sued-over-its-data-center-generators-now-its-buying-2-8b-more/",
186.       "published_at": "2026-05-20T21:55:49Z",
187.       "categories": [
188.         "AI",
189.         "Climate",
190.         "air pollution",
191.         "data centers",
192.         "Elon Musk",
193.         "natural gas",
194.         "SpaceX",
195.         "spacex ipo",
196.         "spacexai",
197.         "xAI"
198.       ],
199.       "summary": "Elon Musk's xAI said it will buy $2.8 billion worth of natural gas turbines over the next three years, according to SpaceX's IPO filing.",
200.       "github_links": [],
201.       "entities": [
202.         "Musk"
203.       ],
204.       "relevance_score": 0.2
205.     },
206.     {
207.       "title": "Anthropic will pay xAI $1.25B per month for compute",
208.       "url": "https://techcrunch.com/2026/05/20/anthropic-will-pay-xai-1-25-billion-per-month-for-compute/",
209.       "published_at": "2026-05-20T21:29:22Z",
210.       "categories": [
211.         "AI",
212.         "Anthropic",
213.         "colossus",
214.         "data centers",
215.         "SpaceX",
216.         "xAI"
217.       ],
218.       "summary": "Elon Musk's xAI surprised the AI world when it made a deal to sell compute to Anthropic. Now we know how much it's worth.",
219.       "github_links": [],
220.       "entities": [
221.         "Anthropic"
222.       ],
223.       "relevance_score": 0.4
224.     },
225.     {
226.       "title": "Sam Altman makes ‘mic drop’ offer to every Y Combinator startup",
227.       "url": "https://techcrunch.com/2026/05/20/sam-altman-makes-mic-drop-offer-to-every-y-combinator-startup/",
228.       "published_at": "2026-05-20T21:23:02Z",
229.       "categories": [
230.         "Startups",
231.         "Venture",
232.         "OpenAI",
233.         "sam altman",
234.         "Y Combinator"
235.       ],
236.       "summary": "Altman offered to have OpenAI invest in every single startup in this Y Combinator class: tokens for equity.",
237.       "github_links": [],
238.       "entities": [
239.         "Sam",
240.         "Altman",
241.         "Combinator"
242.       ],
243.       "relevance_score": 0.4
244.     },
245.     {
246.       "title": "You don’t need to be an AI startup to raise. Lucra has $20M to prove it.",
247.       "url": "https://techcrunch.com/video/you-dont-need-to-be-an-ai-startup-to-raise-lucra-has-20m-to-prove-it/",
248.       "published_at": "2026-05-20T21:21:22Z",
249.       "categories": [
250.         "Startups",
251.         "AI startup",
252.         "ark invest",
253.         "Cathie Wood",
254.         "Equity podcast",
255.         "Lucra",
256.         "startup fundraising",
257.         "venture capital"
258.       ],
259.       "summary": "Slapping &#8220;AI&#8221; on your&#160;startup’s&#160;pitch deck is&#160;basically table&#160;stakes right now. When a founder&#160;raised $20 million from Cathie Wood&#8217;s ARK Invest&#160;for an eSports&#160;gamification&#160;loyalty startup without those two letters in the spotlight, it got us wondering how the conversation even started&#160;—&#160;especially&#160;when ARK had already been burned by a company&#160;operating&#160;in the same space.&#160; On this episode of TechCrunch&#821...",
260.       "github_links": [],
261.       "entities": [
262.         "You",
263.         "AI",
264.         "Lucra"
265.       ],
266.       "relevance_score": 0.6
267.     },
268.     {
269.       "title": "Microsoft’s carbon-removal plans aren’t dead after all",
270.       "url": "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/",
271.       "published_at": "2026-05-20T20:30:24Z",
272.       "categories": [
273.         "Climate",
274.         "biogas",
275.         "carbon credits",
276.         "carbon removal",
277.         "Exclusive",
278.         "Microsoft"
279.       ],
280.       "summary": "Microsoft is responsible for over 90% of the carbon-removal market, and reports suggested the company was pausing purchases entirely. This new deal should help assuage the fears of CDR startups.",
281.       "github_links": [],
282.       "entities": [
283.         "Microsoft"
284.       ],
285.       "relevance_score": 0.2
286.     },
287.     {
288.       "title": "OpenAI claims it solved an 80-year-old math problem — for real this time",
289.       "url": "https://techcrunch.com/2026/05/20/openai-claims-it-solved-an-80-year-old-math-problem-for-real-this-time/",
290.       "published_at": "2026-05-20T20:28:27Z",
291.       "categories": [
292.         "AI",
293.         "ChatGPT",
294.         "erdos problems",
295.         "OpenAI",
296.         "reasoning models"
297.       ],
298.       "summary": "OpenAI claims its reasoning model disproved a geometry conjecture unsolved since 1946 — and this time, the mathematicians who exposed its last embarrassing claim are backing it up.",
299.       "github_links": [],
300.       "entities": [
301.         "OpenAI"
302.       ],
303.       "relevance_score": 0.6
304.     },
305.     {
306.       "title": "IrisGo, a startup backed by Andrew Ng, looks to become the AI desktop buddy you never knew you needed",
307.       "url": "https://techcrunch.com/2026/05/20/irisgo-a-startup-backed-by-andrew-ng-looks-to-become-the-ai-desktop-buddy-you-never-knew-you-needed/",
308.       "published_at": "2026-05-20T19:47:20Z",
309.       "categories": [
310.         "AI",
311.         "andrew ng",
312.         "google brain",
313.         "IrisGo"
314.       ],
315.       "summary": "Initially billed as an \"AI butler,\" Iris watches what happens on a user's desktop and automatically learns how to do tasks for them, its co-founder says.",
316.       "github_links": [],
317.       "entities": [
318.         "IrisGo",
319.         "Andrew",
320.         "Ng",
321.         "AI"
322.       ],
323.       "relevance_score": 0.4
324.     },
325.     {
326.       "title": "Tesla’s Full Self-Driving software is creeping into Europe",
327.       "url": "https://techcrunch.com/2026/05/20/teslas-full-self-driving-software-is-creeping-into-europe/",
328.       "published_at": "2026-05-20T18:32:06Z",
329.       "categories": [
330.         "Transportation",
331.         "autonomous vehicles",
332.         "Europe",
333.         "EVs",
334.         "Tesla",
335.         "Tesla FSD"
336.       ],
337.       "summary": "First came the Netherlands, now it's Lithuania. And more European countries appear to be in the queue for Tesla's driver-assistance system.",
338.       "github_links": [],
339.       "entities": [
340.         "Tesla",
341.         "Full",
342.         "Self",
343.         "Driving",
344.         "Europe"
345.       ],
346.       "relevance_score": 0.0
347.     },
348.     {
349.       "title": "Airbnb gets into hotels, expands AI for host onboarding and customer support",
350.       "url": "https://techcrunch.com/2026/05/20/airbnb-gets-into-hotels-expands-ai-for-host-onboarding-and-customer-support/",
351.       "published_at": "2026-05-20T18:14:04Z",
352.       "categories": [
353.         "Apps",
354.         "Airbnb",
355.         "customer support",
356.         "hotel bookings"
357.       ],
358.       "summary": "Airbnb will soon let you book luggage storage and car rental services on its app.",
359.       "github_links": [],
360.       "entities": [
361.         "Airbnb",
362.         "AI"
363.       ],
364.       "relevance_score": 0.4
365.     },
366.     {
367.       "title": "Global EV market goes K-shaped as the US gets left behind",
368.       "url": "https://techcrunch.com/2026/05/20/global-ev-market-goes-k-shaped-as-the-u-s-gets-left-behind/",
369.       "published_at": "2026-05-20T17:34:00Z",
370.       "categories": [
371.         "Climate",
372.         "Transportation",
373.         "Analysis",
374.         "electric vehicles",
375.         "EVs",
376.         "one big beautiful bill"
377.       ],
378.       "summary": "EV sales have surged worldwide in every region but the U.S., posing risks for legacy and startup automakers.",
379.       "github_links": [],
380.       "entities": [
381.         "Global",
382.         "EV",
383.         "US"
384.       ],
385.       "relevance_score": 0.2
386.     },
387.     {
388.       "title": "OpenAI barrels toward IPO that may happen in September",
389.       "url": "https://techcrunch.com/2026/05/20/openai-barrels-toward-ipo-that-may-happen-in-september/",
390.       "published_at": "2026-05-20T17:24:24Z",
391.       "categories": [
392.         "AI",
393.         "Startups",
394.         "Elon Musk",
395.         "In Brief",
396.         "IPOs",
397.         "OpenAI",
398.         "sam altman"
399.       ],
400.       "summary": "A day after Elon Musk lost his lawsuit that threatened OpenAI's structure, leadership, and finances, OpenAI is reportedly back to prepping for its IPO.",
401.       "github_links": [],
402.       "entities": [
403.         "OpenAI",
404.         "IPO",
405.         "September"
406.       ],
407.       "relevance_score": 0.4
408.     }
409.   ],
410.   "metadata": {
411.     "total_articles": 20,
412.     "relevant_articles": 12,
413.     "github_links_found": 0
414.   }
415. }
```

</details>


### ❌ `bash`

**Extract key data from raw JSON**

$ python3 << 'EOF'
import json

with open('data/raw/2026-W21.json') as f:
    data = json.load(f)

print("=== TOP TOPICS ===")
for t in data['signals']['top_topics'][:25]:
    print(f"  {t['topic']}: {t['count']}")

print()
print("=== NEW REPOS SUMMARY (top 30 by stars) ===")
new_repos = sorted(data['new_repos'], key=lambda r: r.get('stars', 0), reverse=True)
for r in new_repos[:30]:
    print(f"  [{r['full_name']}] stars={r.get('stars',0)} lang={r.get('language','')} desc={str(r.get('description',''))[:80]}")

print()
print("=== TRENDING REPOS ===")
for r in data['trending_repos'][:30]:
    print(f"  [{r['full_name']}] stars={r.get('stars',0)} gained={r.get('stars_gained','N/A')} lang={r.get('language','')} desc={str(r.get('description',''))[:80]}")

print()
print("=== METADATA ===")
meta = data.get('metadata', {})
for k, v in meta.items():
    if k not in ['filter_summary']:
        print(f"  {k}: {v}")
if 'filter_summary' in meta:
    print("  filter_summary:", json.dumps(meta['filter_summary'], indent=4))
if 'partial_failures' in meta:
    print("  partial_failures:", meta['partial_failures'])

EOF

```
Permission denied and could not request permission from user
```


### ❌ `bash`

**Extract topics and metadata**

$ python3 -c "
import json
with open('data/raw/2026-W21.json') as f:
    data = json.load(f)
topics = data['signals']['top_topics'][:25]
print('TOPICS:')
for t in topics:
    print(t['topic'], t['count'])
print('NEW:', len(data['new_repos']), 'TRENDING:', len(data['trending_repos']))
meta = data.get('metadata', {})
simple_meta = {k: v for k, v in meta.items() if k not in ['filter_summary']}
print('META:', simple_meta)
if 'filter_summary' in meta:
    print('FILTER:', meta['filter_summary'])
"

```
Permission denied and could not request permission from user
```


### ❌ `bash`

**Quick topic extraction**

$ python3 -c "import json; d=open('data/raw/2026-W21.json').read(); data=json.loads(d); print('TOPICS:'); [print(t['topic'],t['count']) for t in data['signals']['top_topics'][:25]]"

```
Permission denied and could not request permission from user
```


### ❌ `bash`

**Read top topics via jq**

$ jq '.signals.top_topics[:20]' data/raw/2026-W21.json

```
Permission denied and could not request permission from user
```


### ✅ `bash`

**Check available tools and user**

$ which jq python3 python node && id

<details>
<summary>6 lines</summary>

```
/usr/bin/jq
/opt/hostedtoolcache/Python/3.12.13/x64/bin/python3
/opt/hostedtoolcache/Python/3.12.13/x64/bin/python
/opt/hostedtoolcache/node/22.22.2/x64/bin/node
uid=1001(runner) gid=1001(runner) groups=1001(runner),4(adm),100(users),118(docker),999(systemd-journal)
<exited with exit code 0>
```

</details>


### ❌ `bash`

**Check file permissions and read topics**

$ ls -la data/raw/2026-W21.json && cat data/raw/2026-W21.json | jq '.signals.top_topics[:20]'

```
Permission denied and could not request permission from user
```


### ✅ `bash`

**Check file permissions in raw data dir**

$ ls -la data/raw/

<details>
<summary>7 lines</summary>

```
total 268
drwxr-xr-x 2 runner runner   4096 May 21 08:39 .
drwxr-xr-x 6 runner runner   4096 May 21 08:39 ..
-rw-r--r-- 1 runner runner      0 May 21 08:39 .gitkeep
-rw-r--r-- 1 runner runner  14649 May 21 08:39 2026-W21-techcrunch.json
-rw-r--r-- 1 runner runner 246374 May 21 08:39 2026-W21.json
<exited with exit code 0>
```

</details>


### ❌ `bash`

**Read top topics with jq**

$ jq '.signals.top_topics[:20]' data/raw/2026-W21.json

```
Permission denied and could not request permission from user
```


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. {
2.   "week": "2026-W21",
3.   "crawled_at": "2026-05-21T08:38:38Z",
4.   "new_repos": [
5.     {
6.       "name": "zerolang",
7.       "owner": "vercel-labs",
8.       "full_name": "vercel-labs/zerolang",
9.       "description": "The programming language for agents",
10.       "language": "C",
11.       "stars": 4076,
12.       "forks": 242,
13.       "created_at": "2026-05-15T16:55:16Z",
14.       "topics": [],
15.       "license": "Apache-2.0",
16.       "url": "https://github.com/vercel-labs/zerolang"
17.     },
18.     {
19.       "name": "agents-best-practices",
20.       "owner": "DenisSergeevitch",
21.       "full_name": "DenisSergeevitch/agents-best-practices",
22.       "description": "Provider-neutral Agent Skill for Codex, Claude Code, and agentic harness design.",
23.       "language": null,
24.       "stars": 921,
25.       "forks": 84,
26.       "created_at": "2026-05-15T21:32:21Z",
27.       "topics": [
28.         "agent-skill",
29.         "agent-skills",
30.         "agentic-workflows",
31.         "agents",
32.         "ai-agents",
33.         "anthropic",
34.         "claude",
35.         "claude-code",
36.         "codex",
37.         "codex-skill",
38.         "mcp",
39.         "prompt-engineering"
40.       ],
41.       "license": "MIT",
42.       "url": "https://github.com/DenisSergeevitch/agents-best-practices"
43.     },
44.     {
45.       "name": "smallcode",
46.       "owner": "Doorman11991",
47.       "full_name": "Doorman11991/smallcode",
48.       "description": "AI coding agent optimized for small LLMs. 87% benchmark with 4B-active model.",
49.       "language": "JavaScript",
50.       "stars": 916,
51.       "forks": 59,
52.       "created_at": "2026-05-18T06:19:44Z",
53.       "topics": [],
54.       "license": "MIT",
55.       "url": "https://github.com/Doorman11991/smallcode"
56.     },
57.     {
58.       "name": "codex-complexity-optimizer",
59.       "owner": "Kappaemme-git",
60.       "full_name": "Kappaemme-git/codex-complexity-optimizer",
61.       "description": "Codex skill for safe codebase complexity analysis and performance optimization reports",
62.       "language": "Python",
63.       "stars": 808,
64.       "forks": 48,
65.       "created_at": "2026-05-15T13:33:28Z",
66.       "topics": [],
67.       "license": "MIT",
68.       "url": "https://github.com/Kappaemme-git/codex-complexity-optimizer"
69.     },
70.     {
71.       "name": "ROM-MGBA-Pokemon-Emulator-PC",
72.       "owner": "Flizorules05",
73.       "full_name": "Flizorules05/ROM-MGBA-Pokemon-Emulator-PC",
74.       "description": "ROM Emulator Pokemon mGBA eden emulator eden emulator switch 2: download GBA NDS 3DS Switch games, android APK, MelonDS setup guide, Citra Pokemon X Y, Ryujinx Scarlet Violet ROM hack, Pokemon Emerald Randomizer download. Safe ROMs site, Action Replay cheat codes, GameShark codes FireRed, real time clock RTC error fix, trade evolution",
75.       "language": null,
76.       "stars": 632,
77.       "forks": 0,
78.       "created_at": "2026-05-17T17:15:30Z",
79.       "topics": [
80.         "emulator",
81.         "gba",
82.         "gba-emulator",
83.         "mgba",
84.         "mgba-api",
85.         "mgba-emulator",
86.         "pokemmo",
87.         "pokemon",
88.         "pokemon-battle",
89.         "pokemon-emerald",
90.         "pokemon-emulator-games",
91.         "pokemon-emulator-pc",
92.         "pokemon-gba",
93.         "pokemon-pc-emulator",
94.         "pokemon-red",
95.         "pokemon-rom-emulator",
96.         "rom",
97.         "rom-emulator"
98.       ],
99.       "license": "MIT",
100.       "url": "https://github.com/Flizorules05/ROM-MGBA-Pokemon-Emulator-PC"
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 100-300)

<details>
<summary>201 lines</summary>

```
100.       "url": "https://github.com/Flizorules05/ROM-MGBA-Pokemon-Emulator-PC"
101.     },
102.     {
103.       "name": "Stable-Diffusion-WebUI",
104.       "owner": "BasZ4ll",
105.       "full_name": "BasZ4ll/Stable-Diffusion-WebUI",
106.       "description": "Stable Diffusion: webui automatic1111 download free, comfyui setup guide, sdxl checkpoint safetensors, lora model civitai, controlnet extension github. SD WebUI Forge launcher, low VRAM optimization, xformers command line arguments, python torch cuda error fix, out of memory solution, txt2img img2img, inpainting, realesrgan upscaler, local pc insta",
107.       "language": "TypeScript",
108.       "stars": 632,
109.       "forks": 0,
110.       "created_at": "2026-05-17T16:34:12Z",
111.       "topics": [
112.         "ai-image-generator",
113.         "diffusion-model",
114.         "image-to-image",
115.         "offline-image-generator",
116.         "stable-diffusion",
117.         "stable-diffusion-2026",
118.         "stable-diffusion-android",
119.         "stable-diffusion-download",
120.         "stable-diffusion-free",
121.         "stable-diffusion-github",
122.         "stable-diffusion-tutorial",
123.         "stable-diffusion-ui",
124.         "stable-diffusion-web-ui",
125.         "stable-diffusion-webui-forge",
126.         "stable-diffusion-webui-plugin",
127.         "stable-diffusion-windows",
128.         "stable-diffusion-xl",
129.         "stablediffusion3",
130.         "text-to-image"
131.       ],
132.       "license": "MIT",
133.       "url": "https://github.com/BasZ4ll/Stable-Diffusion-WebUI"
134.     },
135.     {
136.       "name": "hydra-launcher",
137.       "owner": "arnabchoudhury404",
138.       "full_name": "arnabchoudhury404/hydra-launcher",
139.       "description": "hydralauncher: Hydra Launcher download free PC library  fontes links baixar , hydralauncher github,  trusted sources url list, steam verde download, hydralauncher github source code, no download available hydra launcher fix. Embedded bittorrent client setup, repack scraper json megathread, hydra cloud save files sync, python rpc server error",
140.       "language": "TypeScript",
141.       "stars": 630,
142.       "forks": 0,
143.       "created_at": "2026-05-17T16:54:12Z",
144.       "topics": [
145.         "epic-games",
146.         "epic-games-store",
147.         "gamelauncher",
148.         "gaming",
149.         "heroic-games-launcher",
150.         "hydra-download",
151.         "hydra-launcher-library",
152.         "hydra-library",
153.         "hydralauncher",
154.         "hydralauncher-download",
155.         "launcher",
156.         "library-hydra",
157.         "pirate-game",
158.         "pirated-steam-games",
159.         "steam"
160.       ],
161.       "license": "MIT",
162.       "url": "https://github.com/arnabchoudhury404/hydra-launcher"
163.     },
164.     {
165.       "name": "rbxfpsunlocker-boost-More-240FPS",
166.       "owner": "Sunislazi",
167.       "full_name": "Sunislazi/rbxfpsunlocker-boost-More-240FPS",
168.       "description": "rbxfpsunlocker Roblox FPS BOOST: Roblox FPS unlocker download free More 240 FPS, uncap 60 FPS limit, axst GitHub source code, high refresh rate monitor, Roblox client lag fix, Byfron Hyperion anti-cheat compatibility, safe to use ban status, settings.ini configuration, rfu.exe not working error, ClientAppSettings json,bloxtstrap fps unlocke",
169.       "language": "TypeScript",
170.       "stars": 626,
171.       "forks": 0,
172.       "created_at": "2026-05-17T16:13:25Z",
173.       "topics": [
174.         "aimlock",
175.         "fps-unlocker",
176.         "fpsunlocker",
177.         "rbx",
178.         "rbxdev",
179.         "roblox",
180.         "robloxfpsbooster",
181.         "robloxfpsbooster-download",
182.         "robloxfpsunlocker-download",
183.         "sober-fps-unlocker",
184.         "universal-fps"
185.       ],
186.       "license": "MIT",
187.       "url": "https://github.com/Sunislazi/rbxfpsunlocker-boost-More-240FPS"
188.     },
189.     {
190.       "name": "DualSenseX-DSX-Steam-Edition",
191.       "owner": "ZoyaMalhotra",
192.       "full_name": "ZoyaMalhotra/DualSenseX-DSX-Steam-Edition",
193.       "description": "DualSenseX Steam: DSX free download github, adaptive triggers test mod PC, audio to haptics setup, Xbox 360 DualShock 4 emulation. ViGEmBus driver error fix, Bluetooth audio latency, Cyberpunk 2077 controller mod, non-steam games controller not working, DS4Windows alternative. Paliverse crack bypass, BSOD crash fix, Steam Xbox Extended Feature",
194.       "language": "C++",
195.       "stars": 616,
196.       "forks": 1,
197.       "created_at": "2026-05-18T16:41:06Z",
198.       "topics": [
199.         "adaptive-triggers-pc",
200.         "ds4",
201.         "ds4-controller",
202.         "ds4-windows",
203.         "ds4windows",
204.         "dsx-download",
205.         "dsx-steam",
206.         "dsx-windows",
207.         "dual-sense-on-pc",
208.         "dualsense",
209.         "dualsense-controller",
210.         "dualsense-pc-adaptive-triggers",
211.         "dualshock4",
212.         "game-controller",
213.         "hidhide",
214.         "ps3-controller",
215.         "ps5-controller",
216.         "psrp",
217.         "steam",
218.         "vigembus"
219.       ],
220.       "license": "MIT",
221.       "url": "https://github.com/ZoyaMalhotra/DualSenseX-DSX-Steam-Edition"
222.     },
223.     {
224.       "name": "Claude-Mythos-AI-Anthropic-App",
225.       "owner": "AbhishekK130804",
226.       "full_name": "AbhishekK130804/Claude-Mythos-AI-Anthropic-App",
227.       "description": "Claude pro free Mythos design Opus Cowork  Sonnet AI Anthropic App: download free PC android apk iOS, Anthropic Claude API key setup, Claude roleplay mythos client, SillyTavern Claude prompt formatting, custom system prompt jailbreak, Mythos AI creative writing app, Claude 3.5 Sonnet Opus API cost, open source LLM frontend, Claude reverse proxy ",
228.       "language": "C#",
229.       "stars": 611,
230.       "forks": 0,
231.       "created_at": "2026-05-18T17:01:42Z",
232.       "topics": [
233.         "claude",
234.         "claude-ai",
235.         "claude-code",
236.         "claude-code-cli",
237.         "claude-code-hooks",
238.         "claude-code-marketplace",
239.         "claude-code-plugin",
240.         "claude-code-plugins",
241.         "claude-code-skill",
242.         "claude-code-skills",
243.         "claude-code-subagents",
244.         "claude-cowork-free",
245.         "claude-design-ai",
246.         "claude-design-alternative",
247.         "claude-design-download",
248.         "claude-design-free",
249.         "claude-mythos",
250.         "claude-opus",
251.         "claude-opus-4-6",
252.         "mythos"
253.       ],
254.       "license": "MIT",
255.       "url": "https://github.com/AbhishekK130804/Claude-Mythos-AI-Anthropic-App"
256.     },
257.     {
258.       "name": "clawpatch",
259.       "owner": "openclaw",
260.       "full_name": "openclaw/clawpatch",
261.       "description": "Review code. Patch bugs. Land PRs.",
262.       "language": "TypeScript",
263.       "stars": 610,
264.       "forks": 89,
265.       "created_at": "2026-05-15T08:43:03Z",
266.       "topics": [
267.         "bot",
268.         "review"
269.       ],
270.       "license": "MIT",
271.       "url": "https://github.com/openclaw/clawpatch"
272.     },
273.     {
274.       "name": "Steam-Tools",
275.       "owner": "haiddrrs",
276.       "full_name": "haiddrrs/Steam-Tools",
277.       "description": "Lua Steam Tools: SteamTools download free PC latest version, lua manifest generator github, steamtools safe to use account ban risk, BeyondDimension SteamTools source code, unlock free steam games dlc unlocker, watt toolkit alternative, steamtools exe local ticket bypass, lua tools manifest downloader, st-setup virus total malware scan, steamtools",
278.       "language": "C#",
279.       "stars": 591,
280.       "forks": 0,
281.       "created_at": "2026-05-18T17:20:43Z",
282.       "topics": [
283.         "lua-steam-tools",
284.         "luatools",
285.         "manifest-steam-tools",
286.         "steam-bypass",
287.         "steam-client",
288.         "steam-data",
289.         "steam-education",
290.         "steam-fix",
291.         "steam-games",
292.         "steam-library",
293.         "steam-lua-tools",
294.         "steam-tools",
295.         "steam-tools-download",
296.         "steam-tools-games",
297.         "steamtool",
298.         "steamtools",
299.         "steamtools-download",
300.         "steamtools-lua",
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 300-600)

<details>
<summary>301 lines</summary>

```
300.         "steamtools-lua",
301.         "steamtools-manifest",
302.         "steamweb"
303.       ],
304.       "license": "MIT",
305.       "url": "https://github.com/haiddrrs/Steam-Tools"
306.     },
307.     {
308.       "name": "HRM-Text",
309.       "owner": "sapientinc",
310.       "full_name": "sapientinc/HRM-Text",
311.       "description": "HRM-Text is a 1B text generation model based on the HRM architecture, strengthened by task completion and latent space reasoning.",
312.       "language": "Python",
313.       "stars": 590,
314.       "forks": 55,
315.       "created_at": "2026-05-18T03:10:52Z",
316.       "topics": [
317.         "hierarchical-reasoning-model",
318.         "hrm",
319.         "large-language-models",
320.         "pretraining"
321.       ],
322.       "license": "Apache-2.0",
323.       "url": "https://github.com/sapientinc/HRM-Text"
324.     },
325.     {
326.       "name": "Lance",
327.       "owner": "bytedance",
328.       "full_name": "bytedance/Lance",
329.       "description": "A 3B-active-parameter native unified multimodal model for image and video understanding, generation, and editing.",
330.       "language": "Python",
331.       "stars": 586,
332.       "forks": 33,
333.       "created_at": "2026-05-15T05:42:08Z",
334.       "topics": [
335.         "image-editing",
336.         "image-generation",
337.         "image-understanding",
338.         "unified-multimodal-models",
339.         "video-generation",
340.         "video-understanding"
341.       ],
342.       "license": "Apache-2.0",
343.       "url": "https://github.com/bytedance/Lance"
344.     },
345.     {
346.       "name": "auto-identity-remove",
347.       "owner": "stephenlthorn",
348.       "full_name": "stephenlthorn/auto-identity-remove",
349.       "description": "Automated data broker opt-out runner — removes your personal info from 30+ people-search sites on a monthly schedule",
350.       "language": "JavaScript",
351.       "stars": 572,
352.       "forks": 20,
353.       "created_at": "2026-05-15T12:40:18Z",
354.       "topics": [],
355.       "license": null,
356.       "url": "https://github.com/stephenlthorn/auto-identity-remove"
357.     },
358.     {
359.       "name": "ultraviewer",
360.       "owner": "tritano",
361.       "full_name": "tritano/ultraviewer",
362.       "description": "Teamviewer UltraViewer download free PC windows 11, portable zip, latest version 6.6, getting my ID stuck fix. Port 2112 firewall block, teamviewer commercial use detected bypass, anydesk alternative. Black screen on connection solution, run with windows administrator, change password, file transfer slow.",
363.       "language": "TypeScript",
364.       "stars": 556,
365.       "forks": 0,
366.       "created_at": "2026-05-16T17:07:32Z",
367.       "topics": [
368.         "anydesk-integration",
369.         "download-ultraviewer",
370.         "download-ultraviewer-for-windows",
371.         "teamviewer",
372.         "ultraviewer",
373.         "ultraviewer-download",
374.         "ultraviewer-download-for-windows",
375.         "ultraviewer-for-windows",
376.         "ultraviewer-pc",
377.         "ultraviewer-unlock"
378.       ],
379.       "license": "MIT",
380.       "url": "https://github.com/tritano/ultraviewer"
381.     },
382.     {
383.       "name": "hyperliquid-whale-order-tracking",
384.       "owner": "Glazenovatag",
385.       "full_name": "Glazenovatag/hyperliquid-whale-order-tracking",
386.       "description": "A real, working Hyperliquid whale tracker not a placeholder. The synthetic-message test passed and the WebSocket subscribe / reconnect logic was verified live.",
387.       "language": "Python",
388.       "stars": 533,
389.       "forks": 0,
390.       "created_at": "2026-05-19T10:31:27Z",
391.       "topics": [
392.         "hyperliquid-whale-alert",
393.         "hyperliquid-whale-tracker"
394.       ],
395.       "license": "MIT",
396.       "url": "https://github.com/Glazenovatag/hyperliquid-whale-order-tracking"
397.     },
398.     {
399.       "name": "UE4SS-Subnautica-2",
400.       "owner": "littlefrogyq",
401.       "full_name": "littlefrogyq/UE4SS-Subnautica-2",
402.       "description": "UE4SS Subnautica 2: UE4SS download github latest version, Subnautica 2 UE5 mod loader setup, xinput1_4.dll dwmapi.dll injector error. REUE4SS UE4SS-settings.ini config, console modding commands, Subnautica 2 crashes on launch fix, dump SDK C++ blueprints, Live Viewport object spacer, GuiConsole visible toggle. Unreal Engine 5.5 compatibility,",
403.       "language": "C++",
404.       "stars": 512,
405.       "forks": 0,
406.       "created_at": "2026-05-19T16:18:16Z",
407.       "topics": [
408.         "early-access-subnautica-2",
409.         "game-mod-manager",
410.         "mod",
411.         "mod-manager",
412.         "modmanager",
413.         "nitrox-pirate",
414.         "subnautica",
415.         "subnautica-2",
416.         "subnautica-2-multiplayer",
417.         "subnautica-2-on-ps5",
418.         "subnautica-2-release",
419.         "subnautica-2-release-date-ps5",
420.         "subnautica-2-xbox",
421.         "subnautica-modding",
422.         "subnautica-multiplayer",
423.         "subnautica2",
424.         "subnautica2-mod",
425.         "subnautica2modmanager",
426.         "ue4ss-subnautica-2"
427.       ],
428.       "license": "MIT",
429.       "url": "https://github.com/littlefrogyq/UE4SS-Subnautica-2"
430.     },
431.     {
432.       "name": "CloakBrowser",
433.       "owner": "SalhaNabil",
434.       "full_name": "SalhaNabil/CloakBrowser",
435.       "description": "CloakBrowser Github: anti-detect browser download, source-level chromium patches, browser fingerprinting spoofing, multi-accounting tool, canvas webgl modification, proxy manager http socks5, cookie isolation, session import export, user-agent switcher, puppeteer playwright automation api, profile sharing, web scraping free, github ",
436.       "language": "TypeScript",
437.       "stars": 507,
438.       "forks": 0,
439.       "created_at": "2026-05-19T17:26:20Z",
440.       "topics": [
441.         "anti-detect",
442.         "anti-detect-browser",
443.         "antidetect-browser",
444.         "chromium",
445.         "cloak-browser",
446.         "cloak-browser-github",
447.         "cloakbrowser",
448.         "cloakbrowser-download",
449.         "cloakbrowser-downloader",
450.         "cloakbrowser-install",
451.         "cloakbrowser-installer",
452.         "stealth-browser"
453.       ],
454.       "license": "MIT",
455.       "url": "https://github.com/SalhaNabil/CloakBrowser"
456.     },
457.     {
458.       "name": "Zephyr-Executor-Free-Roblox-Executor-PC-No-Key-Required-2026",
459.       "owner": "RastProxy88",
460.       "full_name": "RastProxy88/Zephyr-Executor-Free-Roblox-Executor-PC-No-Key-Required-2026",
461.       "description": "Free undetected Roblox script executor with instant injection, full UNC support, and no key system. Clean UI, built-in script hub, regular updates.",
462.       "language": "Lua",
463.       "stars": 480,
464.       "forks": 97,
465.       "created_at": "2026-05-17T17:51:00Z",
466.       "topics": [
467.         "lua",
468.         "roblox"
469.       ],
470.       "license": "MIT",
471.       "url": "https://github.com/RastProxy88/Zephyr-Executor-Free-Roblox-Executor-PC-No-Key-Required-2026"
472.     },
473.     {
474.       "name": "gta-5-mod-menu",
475.       "owner": "trong776",
476.       "full_name": "trong776/gta-5-mod-menu",
477.       "description": "External game enhancement for GTA V single-player. ImGui overlay, no injection, minimal FPS impact. Windows x64, C++17.",
478.       "language": null,
479.       "stars": 458,
480.       "forks": 160,
481.       "created_at": "2026-05-15T16:18:35Z",
482.       "topics": [
483.         "cpp",
484.         "directx",
485.         "enhancement",
486.         "gaming-tool",
487.         "gta-5",
488.         "imgui",
489.         "open-source",
490.         "trainer",
491.         "utility",
492.         "windows"
493.       ],
494.       "license": "MIT",
495.       "url": "https://github.com/trong776/gta-5-mod-menu"
496.     },
497.     {
498.       "name": "Nightlight-Game-Launcher",
499.       "owner": "Alkih",
500.       "full_name": "Alkih/Nightlight-Game-Launcher",
501.       "description": "Nightlight Game Launcher: NLGL download, Rockstar Social Club bypass, GTA V Epic Games launch error, RDR2 offline play, GTA IV Social Club fix. Steam account switcher, Epic Online Services bypass, EOS SDK. dll, -nobattleye, -scOfflineMode, launch options, account manager, local backup, source code GitHub, onajlikezz, open source tool.",
502.       "language": "C#",
503.       "stars": 447,
504.       "forks": 0,
505.       "created_at": "2026-05-15T16:40:59Z",
506.       "topics": [
507.         "bypassing",
508.         "epic-games",
509.         "epicgames",
510.         "fe-bypass",
511.         "grand-theft-auto-v",
512.         "nightlight",
513.         "nightlight-launcher",
514.         "nlgl",
515.         "nlgl-download",
516.         "rdr2",
517.         "reddeadredemption2",
518.         "rockstargames",
519.         "steam",
520.         "uac-bypass",
521.         "vac-bypass"
522.       ],
523.       "license": "MIT",
524.       "url": "https://github.com/Alkih/Nightlight-Game-Launcher"
525.     },
526.     {
527.       "name": "gta-5-mod-menu",
528.       "owner": "SubamanojJ-2004",
529.       "full_name": "SubamanojJ-2004/gta-5-mod-menu",
530.       "description": "Ultimate Enhancement Toolkit for GTA V — powerful mod menu with ESP, vehicle spawner, recovery features, and clean UI",
531.       "language": null,
532.       "stars": 445,
533.       "forks": 61,
534.       "created_at": "2026-05-16T08:50:42Z",
535.       "topics": [
536.         "gameenhancement",
537.         "luauiframework",
538.         "openworldtools",
539.         "runtimeoverlay",
540.         "sandboxextensions"
541.       ],
542.       "license": "MIT",
543.       "url": "https://github.com/SubamanojJ-2004/gta-5-mod-menu"
544.     },
545.     {
546.       "name": "sklauncher-minecraft",
547.       "owner": "Harshit-pruthi",
548.       "full_name": "Harshit-pruthi/sklauncher-minecraft",
549.       "description": "Download SkLauncher Download: Modern Minecraft launcher. Offline mode, premium login, custom skins setup, cape manager, profile creator. Supports Fabric, Forge, Quilt, NeoForge, OptiFine, Iris shaders. Java 21 path, memory allocation, modpack manager, game directory, auto-update, fluent UI themes, portable.",
550.       "language": "C++",
551.       "stars": 418,
552.       "forks": 0,
553.       "created_at": "2026-05-15T15:40:52Z",
554.       "topics": [
555.         "1-12-2-mod",
556.         "download-sklauncher",
557.         "launcher",
558.         "launcher-minecraft",
559.         "mclauncher",
560.         "mcmod",
561.         "minecraft-1-20-2",
562.         "minecraft-builds",
563.         "minecraft-client",
564.         "minecraft-gui",
565.         "minecraft-launcher",
566.         "minecraft-launcher-library",
567.         "minecraft-mod",
568.         "minecraft-website",
569.         "minecraft-world",
570.         "modded-minecraft",
571.         "sklauncher-download",
572.         "sklauncher-minecraft",
573.         "sklauncher-mods",
574.         "sklauncher-skin"
575.       ],
576.       "license": "MIT",
577.       "url": "https://github.com/Harshit-pruthi/sklauncher-minecraft"
578.     },
579.     {
580.       "name": "codiff",
581.       "owner": "nkzw-tech",
582.       "full_name": "nkzw-tech/codiff",
583.       "description": "a fast local diff viewer",
584.       "language": "TypeScript",
585.       "stars": 416,
586.       "forks": 17,
587.       "created_at": "2026-05-15T13:17:31Z",
588.       "topics": [],
589.       "license": "MIT",
590.       "url": "https://github.com/nkzw-tech/codiff"
591.     },
592.     {
593.       "name": "Forza-Horizon-6-Premium",
594.       "owner": "dannyhsueh2",
595.       "full_name": "dannyhsueh2/Forza-Horizon-6-Premium",
596.       "description": "Forza Horizon 6 release date : PC system requirements, early access Steam. Premium Upgrade Bundle, Car Pass, VIP Membership. Japan map, Mt Fuji, Tokyo street racing, Touge Battles, JDM cars, Ferrari J50, Mazda Furai. Expansion 1, Expansion 2, I, , pre-load PC Steam, Game Pass Ultimate.",
597.       "language": "C++",
598.       "stars": 412,
599.       "forks": 1,
600.       "created_at": "2026-05-15T16:07:55Z",
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 600-900)

<details>
<summary>301 lines</summary>

```
600.       "created_at": "2026-05-15T16:07:55Z",
601.       "topics": [
602.         "forza",
603.         "forza-horizon",
604.         "forza-horizon-4",
605.         "forza-horizon-5",
606.         "forza-horizon-6",
607.         "forza-horizon-6-download",
608.         "forza-horizon-6-free",
609.         "forza-horizon-6-install",
610.         "forza-horizon-6-pc",
611.         "forza-horizon-6-premium",
612.         "forza-horizon-6-release",
613.         "forza-horizon-6-steam",
614.         "forza-motorsport",
615.         "game",
616.         "open-source-game"
617.       ],
618.       "license": "MIT",
619.       "url": "https://github.com/dannyhsueh2/Forza-Horizon-6-Premium"
620.     },
621.     {
622.       "name": "LSFG-Desktop",
623.       "owner": "uktrash",
624.       "full_name": "uktrash/LSFG-Desktop",
625.       "description": "Lossless Scaling github steam reddit LSFG 3 frame generation  v3.22, uncap FPS low end PC, AMD FSR NIS scaling, cursor lag fix. Double FPS laptop guide, windowed to borderless fullscreen, ghosting artifact solution, capture API DXGI GDI, half refresh rate VSync. anime4k ,  version , latency reduction, lsfg",
626.       "language": "C#",
627.       "stars": 411,
628.       "forks": 0,
629.       "created_at": "2026-05-20T12:51:00Z",
630.       "topics": [
631.         "crimson-desert-lsfg",
632.         "frame-generation",
633.         "gaming-performance",
634.         "lossless-frame-generation",
635.         "lossless-scaling",
636.         "lossless-scaling-2026",
637.         "lossless-scaling-android",
638.         "lossless-scaling-download",
639.         "lossless-scaling-github",
640.         "lossless-scaling-lsfg",
641.         "lossless-scaling-pc",
642.         "lossless-scaling-reddit",
643.         "lossless-scaling-software",
644.         "lossless-scaling-steam",
645.         "lossless-scaling-v3",
646.         "lsfg",
647.         "lsfg-ai-upscaling",
648.         "lsfg-vk",
649.         "optiscaler",
650.         "smooth-gaming"
651.       ],
652.       "license": "MIT",
653.       "url": "https://github.com/uktrash/LSFG-Desktop"
654.     },
655.     {
656.       "name": "aida64",
657.       "owner": "CylinderChairman",
658.       "full_name": "CylinderChairman/aida64",
659.       "description": "aida64 unlocker extreme edition",
660.       "language": "PowerShell",
661.       "stars": 396,
662.       "forks": 0,
663.       "created_at": "2026-05-20T10:52:40Z",
664.       "topics": [
665.         "aida64",
666.         "aida64-extreme-patch",
667.         "aida64-unlocker"
668.       ],
669.       "license": "MIT",
670.       "url": "https://github.com/CylinderChairman/aida64"
671.     },
672.     {
673.       "name": "audit",
674.       "owner": "evilsocket",
675.       "full_name": "evilsocket/audit",
676.       "description": "An 8-stage vulnerability-discovery agent.",
677.       "language": "Python",
678.       "stars": 384,
679.       "forks": 53,
680.       "created_at": "2026-05-18T20:42:44Z",
681.       "topics": [],
682.       "license": "MIT",
683.       "url": "https://github.com/evilsocket/audit"
684.     },
685.     {
686.       "name": "YellowKey-Bitlocker",
687.       "owner": "rahul03524",
688.       "full_name": "rahul03524/YellowKey-Bitlocker",
689.       "description": "YellowKey Github: bitlocker encryption bypass tool, winre physical access zero-day exploit, chaotic eclipse nightmare-eclipse github, tpm-only default configuration vulnerability. windows 11 server 2022 2025 unpatched, fstx folder system volume information, transactional ntfs metadata exploit, usb ",
690.       "language": "TypeScript",
691.       "stars": 380,
692.       "forks": 1,
693.       "created_at": "2026-05-20T14:26:15Z",
694.       "topics": [
695.         "bitlocker",
696.         "bitlocker-drive-encryption",
697.         "bitlocker-drive-management",
698.         "bypass-uac",
699.         "yellowkey",
700.         "yellowkey-bitlocker",
701.         "yellowkey-github"
702.       ],
703.       "license": "MIT",
704.       "url": "https://github.com/rahul03524/YellowKey-Bitlocker"
705.     },
706.     {
707.       "name": "Deepseek-v4-pro-app",
708.       "owner": "MFS9628",
709.       "full_name": "MFS9628/Deepseek-v4-pro-app",
710.       "description": "DeepSeek v4 Pro github Flash chat: API flash gemma 4 gemini qwen claude chatgpt 4  key pricing tier, open source weights, huggingface model repository, local execution ollama setup. context window token limit, coding benchmark leaderboard ranking, reasoning model architecture v4,  .visual studio code extension integration, cursor ai ",
711.       "language": null,
712.       "stars": 380,
713.       "forks": 0,
714.       "created_at": "2026-05-20T13:56:54Z",
715.       "topics": [
716.         "ai-app",
717.         "ai-powered-applications",
718.         "artificial-intelligence-projects",
719.         "deep-seek",
720.         "deepseek",
721.         "deepseek-api",
722.         "deepseek-free-api",
723.         "deepseek-integration",
724.         "deepseek-ocr-2",
725.         "deepseek-r1",
726.         "deepseek-r1-zero",
727.         "deepseek-v3",
728.         "deepseek-v4",
729.         "deepseek-v4-api",
730.         "deepseek-v4-app",
731.         "deepseek-v4-free",
732.         "deepseek-v4-pro",
733.         "deepseekv4",
734.         "deepseekv4-flash",
735.         "free-api"
736.       ],
737.       "license": "MIT",
738.       "url": "https://github.com/MFS9628/Deepseek-v4-pro-app"
739.     },
740.     {
741.       "name": "KMSTools",
742.       "owner": "ZettPW",
743.       "full_name": "ZettPW/KMSTools",
744.       "description": "windows tool, office 2026 perpetual license command, net download, digital entitlement permanent custom host ",
745.       "language": "C#",
746.       "stars": 379,
747.       "forks": 0,
748.       "created_at": "2026-05-20T16:09:42Z",
749.       "topics": [
750.         "activator",
751.         "kms",
752.         "kms-activation-github",
753.         "kms-client",
754.         "kms-host-server",
755.         "kms-office",
756.         "kms-script",
757.         "kms-server",
758.         "kms-studio-dev",
759.         "kmsauto-",
760.         "kmsauto-net-2026",
761.         "kmsauto-portable-official",
762.         "kmspico-2027",
763.         "kmspico-portable-2026",
764.         "kmspico-update",
765.         "permanent-windows-activator-2026",
766.         "windows-11-activator-kmsauto",
767.         "windows-activaton",
768.         "windows-activator-free"
769.       ],
770.       "license": "MIT",
771.       "url": "https://github.com/ZettPW/KMSTools"
772.     },
773.     {
774.       "name": "elephant-agent",
775.       "owner": "agentic-in",
776.       "full_name": "agentic-in/elephant-agent",
777.       "description": "Personal-Model First Self Evolving AI Agent 🐘",
778.       "language": "Python",
779.       "stars": 373,
780.       "forks": 26,
781.       "created_at": "2026-05-15T07:08:17Z",
782.       "topics": [
783.         "agent",
784.         "agentic",
785.         "agentic-ai",
786.         "context",
787.         "llm",
788.         "memory",
789.         "models",
790.         "personal-ai",
791.         "self-evolution"
792.       ],
793.       "license": null,
794.       "url": "https://github.com/agentic-in/elephant-agent"
795.     },
796.     {
797.       "name": "JennyMod-All-Versions",
798.       "owner": "AppleOnFire",
799.       "full_name": "AppleOnFire/JennyMod-All-Versions",
800.       "description": "jenny mod minecraft pe mc video download pc java curseforge forge fabric  girlfriend addon pocket edition download .jar mediafire link realistic animations render pass bed interaction companion skin texture bedrock edition mcpack free portable zip apk mobile character custom dialogue chat adult content",
801.       "language": "Java",
802.       "stars": 360,
803.       "forks": 0,
804.       "created_at": "2026-05-20T16:33:36Z",
805.       "topics": [
806.         "all-the-mods-modpack",
807.         "jenny",
808.         "jenny-mod-2026",
809.         "jennybot",
810.         "jennymod",
811.         "jennymod-2026",
812.         "minecraft-jenny-mod",
813.         "minecraft-jenny-mod-2026",
814.         "minecraft-mc",
815.         "minecraft-mod",
816.         "minecraft-nsfw-mod",
817.         "minecraftjennymod",
818.         "minecraftjennymod-2026",
819.         "modded-minecraft",
820.         "modded-minecraft-modpack",
821.         "nsfw-minecraft-mod",
822.         "nsfw-mod",
823.         "tminecaft"
824.       ],
825.       "license": "MIT",
826.       "url": "https://github.com/AppleOnFire/JennyMod-All-Versions"
827.     },
828.     {
829.       "name": "loom",
830.       "owner": "husu",
831.       "full_name": "husu/loom",
832.       "description": "一个写接口文档的AI Agent。支持使用Vibe coding 的方式，编写接口文档，同时自带友好的文档查看工具与接口Mock工具",
833.       "language": null,
834.       "stars": 339,
835.       "forks": 20,
836.       "created_at": "2026-05-15T09:19:02Z",
837.       "topics": [],
838.       "license": null,
839.       "url": "https://github.com/husu/loom"
840.     },
841.     {
842.       "name": "vpnhostinglist",
843.       "owner": "internetkafe",
844.       "full_name": "internetkafe/vpnhostinglist",
845.       "description": "vps hosting list / список ссылок на vps хостинги | RemnaWave / 3X-UI / MarzBan / PasarGuard",
846.       "language": null,
847.       "stars": 330,
848.       "forks": 17,
849.       "created_at": "2026-05-20T04:31:43Z",
850.       "topics": [
851.         "3x-ui",
852.         "marzban",
853.         "remnawave"
854.       ],
855.       "license": "GPL-3.0",
856.       "url": "https://github.com/internetkafe/vpnhostinglist"
857.     },
858.     {
859.       "name": "dota2-gameplay-tools",
860.       "owner": "MediatorSpeak",
861.       "full_name": "MediatorSpeak/dota2-gameplay-tools",
862.       "description": "A modular data visualization framework and telemetry toolkit for Dota 2. Designed for real-time match analysis, custom UI prototyping, and gameplay mechanics testing in controlled environments.",
863.       "language": null,
864.       "stars": 324,
865.       "forks": 121,
866.       "created_at": "2026-05-16T18:46:37Z",
867.       "topics": [
868.         "data-visualization",
869.         "dota2",
870.         "game-analytics",
871.         "overlay-system",
872.         "ui-framework"
873.       ],
874.       "license": "MIT",
875.       "url": "https://github.com/MediatorSpeak/dota2-gameplay-tools"
876.     },
877.     {
878.       "name": "burn-baby-burn",
879.       "owner": "dtnewman",
880.       "full_name": "dtnewman/burn-baby-burn",
881.       "description": "Be the most productive engineer on your team 🚀🚀🚀",
882.       "language": "Shell",
883.       "stars": 323,
884.       "forks": 8,
885.       "created_at": "2026-05-15T16:51:59Z",
886.       "topics": [],
887.       "license": "MIT",
888.       "url": "https://github.com/dtnewman/burn-baby-burn"
889.     },
890.     {
891.       "name": "shushu-internship-tool",
892.       "owner": "LiuMengxuan04",
893.       "full_name": "LiuMengxuan04/shushu-internship-tool",
894.       "description": "把岗位描述变项目，把项目变简历，把简历变面试。",
895.       "language": "Python",
896.       "stars": 302,
897.       "forks": 11,
898.       "created_at": "2026-05-17T11:25:47Z",
899.       "topics": [
900.         "ai",
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 900-1200)

<details>
<summary>301 lines</summary>

```
900.         "ai",
901.         "ai-agents",
902.         "skills"
903.       ],
904.       "license": "NOASSERTION",
905.       "url": "https://github.com/LiuMengxuan04/shushu-internship-tool"
906.     },
907.     {
908.       "name": "phosphene",
909.       "owner": "kageroumado",
910.       "full_name": "kageroumado/phosphene",
911.       "description": "A video wallpaper engine for macOS Tahoe",
912.       "language": "Swift",
913.       "stars": 295,
914.       "forks": 6,
915.       "created_at": "2026-05-20T23:33:59Z",
916.       "topics": [],
917.       "license": "MIT",
918.       "url": "https://github.com/kageroumado/phosphene"
919.     },
920.     {
921.       "name": "polymarket-trading-bot",
922.       "owner": "texsellix",
923.       "full_name": "texsellix/polymarket-trading-bot",
924.       "description": "Polymarket from your terminal. Copy whales, run autonomous strategies, place orders with one command. CLI-only, no dashboard, no setup.",
925.       "language": "TypeScript",
926.       "stars": 289,
927.       "forks": 27,
928.       "created_at": "2026-05-20T23:12:49Z",
929.       "topics": [
930.         "ai-agent",
931.         "algorithmic-trading",
932.         "autonomous-trading",
933.         "cli",
934.         "clob",
935.         "copy-trading",
936.         "crypto-trading",
937.         "ethers",
938.         "polygon",
939.         "polymarket",
940.         "prediction-markets",
941.         "trading-bot",
942.         "typescript",
943.         "web3"
944.       ],
945.       "license": "MIT",
946.       "url": "https://github.com/texsellix/polymarket-trading-bot"
947.     },
948.     {
949.       "name": "Vivid-R6-Cracked-2026",
950.       "owner": "RastProxy88",
951.       "full_name": "RastProxy88/Vivid-R6-Cracked-2026",
952.       "description": "External memory analysis framework for Rainbow Six Siege. Features ESP, aimbot, skeleton rendering via DirectX 11 overlay. Read-only operation with direct syscall stubs. Supports Y8S4 — Y9S2. C++17, x64, MIT license.",
953.       "language": "C++",
954.       "stars": 286,
955.       "forks": 0,
956.       "created_at": "2026-05-16T12:46:41Z",
957.       "topics": [
958.         "cpp17",
959.         "directx11",
960.         "educational",
961.         "external-tool",
962.         "game-tool",
963.         "memory-analysis",
964.         "open-source",
965.         "overlay-renderer",
966.         "rainbow6",
967.         "read-only",
968.         "reverse-engineering",
969.         "win32-api"
970.       ],
971.       "license": "MIT",
972.       "url": "https://github.com/RastProxy88/Vivid-R6-Cracked-2026"
973.     },
974.     {
975.       "name": "infinite-canvas",
976.       "owner": "basketikun",
977.       "full_name": "basketikun/infinite-canvas",
978.       "description": "面向AI创作的开源无限画布工作台，集成 AI 生图、参考图编辑、画布编排、对话助手、提示词库和素材管理等功能。",
979.       "language": "TypeScript",
980.       "stars": 273,
981.       "forks": 49,
982.       "created_at": "2026-05-18T23:45:50Z",
983.       "topics": [],
984.       "license": "AGPL-3.0",
985.       "url": "https://github.com/basketikun/infinite-canvas"
986.     },
987.     {
988.       "name": "slopless",
989.       "owner": "agent-quality-controls",
990.       "full_name": "agent-quality-controls/slopless",
991.       "description": "Deterministic textlint rules and CLI for catching prose slop in Markdown",
992.       "language": "TypeScript",
993.       "stars": 255,
994.       "forks": 38,
995.       "created_at": "2026-05-16T20:44:14Z",
996.       "topics": [
997.         "ai",
998.         "cli",
999.         "lint",
1000.         "linter",
1001.         "llm",
1002.         "markdown",
1003.         "nodejs",
1004.         "prose",
1005.         "quality",
1006.         "slop",
1007.         "static-analysis",
1008.         "style-guide",
1009.         "textlint",
1010.         "typescript",
1011.         "writing"
1012.       ],
1013.       "license": "MIT",
1014.       "url": "https://github.com/agent-quality-controls/slopless"
1015.     },
1016.     {
1017.       "name": "humanize-text",
1018.       "owner": "lynote-ai",
1019.       "full_name": "lynote-ai/humanize-text",
1020.       "description": "Free open-source AI text humanizer to convert AI-generated content into undetectable, human-like writing. Bypass Turnitin, GPTZero, and all major AI detectors. No sign-up required. Try our unlimited free online tool",
1021.       "language": "Python",
1022.       "stars": 255,
1023.       "forks": 6,
1024.       "created_at": "2026-05-18T10:12:15Z",
1025.       "topics": [
1026.         "ai-humanize",
1027.         "ai-humanizer",
1028.         "gptzero-bypass",
1029.         "humanization",
1030.         "humanize-ai",
1031.         "humanize-ai-text",
1032.         "humanize-text",
1033.         "humanizer",
1034.         "undetectable-ai-alternative"
1035.       ],
1036.       "license": "MIT",
1037.       "url": "https://github.com/lynote-ai/humanize-text"
1038.     },
1039.     {
1040.       "name": "claude-fuer-deutsches-recht",
1041.       "owner": "Klotzkette",
1042.       "full_name": "Klotzkette/claude-fuer-deutsches-recht",
1043.       "description": "⚠️ Experimentelle Skill-Sammlung für deutsches Recht (Arbeits-, Gesellschafts-, Insolvenz-, Datenschutz-, Prozessrecht u.a.) – inzwischen verbessert und im Alltag getestet, aber weiterhin Experiment. Bitte selber ausprobieren, Issues/PRs willkommen! Keine Rechtsberatung. Mandatsgeheimnis (§§ 203/204 StGB, § 43e BRAO), DSGVO, US-Transfer, KI-VO & Co",
1044.       "language": "Python",
1045.       "stars": 247,
1046.       "forks": 13,
1047.       "created_at": "2026-05-18T16:43:56Z",
1048.       "topics": [
1049.         "anthropic",
1050.         "bgh",
1051.         "claude-skills",
1052.         "deutsches-recht",
1053.         "dsgvo",
1054.         "german-law",
1055.         "kanzlei",
1056.         "legal-ai",
1057.         "legaltech"
1058.       ],
1059.       "license": "NOASSERTION",
1060.       "url": "https://github.com/Klotzkette/claude-fuer-deutsches-recht"
1061.     },
1062.     {
1063.       "name": "openai-plus-vxt",
1064.       "owner": "suyancc",
1065.       "full_name": "suyancc/openai-plus-vxt",
1066.       "description": "一个基于 WXT 的浏览器插件，用于辅助 ChatGPT 注册、Checkout 链接提取、随机地址资料生成，以及 OpenAI/PayPal 支付页资料自动填写。",
1067.       "language": "TypeScript",
1068.       "stars": 208,
1069.       "forks": 57,
1070.       "created_at": "2026-05-19T02:24:31Z",
1071.       "topics": [],
1072.       "license": null,
1073.       "url": "https://github.com/suyancc/openai-plus-vxt"
1074.     },
1075.     {
1076.       "name": "android-testing-skills",
1077.       "owner": "skydoves",
1078.       "full_name": "skydoves/android-testing-skills",
1079.       "description": "⚡️ A set of skills for Android testing: Compose UI, AndroidX Test, JVM unit tests, and ADB.",
1080.       "language": "Shell",
1081.       "stars": 205,
1082.       "forks": 3,
1083.       "created_at": "2026-05-15T07:38:44Z",
1084.       "topics": [],
1085.       "license": "Apache-2.0",
1086.       "url": "https://github.com/skydoves/android-testing-skills"
1087.     },
1088.     {
1089.       "name": "polymarket-trading-bot",
1090.       "owner": "Multichain-Bot-Lab",
1091.       "full_name": "Multichain-Bot-Lab/polymarket-trading-bot",
1092.       "description": "polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot polymarket arbitrage trading bot polymarket arbitrage bot polymarket trading bot",
1093.       "language": "TypeScript",
1094.       "stars": 202,
1095.       "forks": 4500,
1096.       "created_at": "2026-05-15T16:46:39Z",
1097.       "topics": [
1098.         "polymarket-arbitrage-bot",
1099.         "polymarket-arbitrage-trading-bot",
1100.         "polymarket-trading-bot"
1101.       ],
1102.       "license": null,
1103.       "url": "https://github.com/Multichain-Bot-Lab/polymarket-trading-bot"
1104.     },
1105.     {
1106.       "name": "polymarket-copy-trading-bot",
1107.       "owner": "Multichain-Bot-Lab",
1108.       "full_name": "Multichain-Bot-Lab/polymarket-copy-trading-bot",
1109.       "description": "polymarket copy trading Bot polymarket copy trading Bot polymarket copy trading Bot polymarket copy trading Bot polymarket copy trading Bot polymarket copy trading Bot polymarket copytrading bot polymarket copytrading bot polymarket copytrading bot polymarket copytrading bot polymarket copytrading bot polymarket copytrading bot polymarket copytrade",
1110.       "language": "TypeScript",
1111.       "stars": 196,
1112.       "forks": 928,
1113.       "created_at": "2026-05-15T16:51:06Z",
1114.       "topics": [
1115.         "polymarket-copy-bot",
1116.         "polymarket-copy-trading-bot",
1117.         "polymarket-copytrade-bot",
1118.         "polymarket-copytrading-bot"
1119.       ],
1120.       "license": null,
1121.       "url": "https://github.com/Multichain-Bot-Lab/polymarket-copy-trading-bot"
1122.     },
1123.     {
1124.       "name": "technical-writing",
1125.       "owner": "luoling8192",
1126.       "full_name": "luoling8192/technical-writing",
1127.       "description": "中文内部技术写作的 agent skill，约束设计文档 / 评审稿 / postmortem / 分享稿场景的语气、句法、结构",
1128.       "language": null,
1129.       "stars": 176,
1130.       "forks": 9,
1131.       "created_at": "2026-05-15T12:31:42Z",
1132.       "topics": [
1133.         "agent-skill",
1134.         "chinese",
1135.         "claude-code",
1136.         "codex",
1137.         "documentation",
1138.         "technical-writing"
1139.       ],
1140.       "license": "MIT",
1141.       "url": "https://github.com/luoling8192/technical-writing"
1142.     },
1143.     {
1144.       "name": "HermesPet",
1145.       "owner": "basionwang-bot",
1146.       "full_name": "basionwang-bot/HermesPet",
1147.       "description": "让 AI 住在你 MacBook 的刘海里 · 零依赖开箱即用 · 多引擎并行的桌面 AI 伴侣（Swift 6 / SwiftUI / macOS 14+）",
1148.       "language": "Swift",
1149.       "stars": 171,
1150.       "forks": 23,
1151.       "created_at": "2026-05-15T06:03:02Z",
1152.       "topics": [
1153.         "ai",
1154.         "chatgpt",
1155.         "chinese",
1156.         "claude",
1157.         "deepseek",
1158.         "desktop-app",
1159.         "dynamic-island",
1160.         "llm",
1161.         "macos",
1162.         "menu-bar-app",
1163.         "swift",
1164.         "swiftui"
1165.       ],
1166.       "license": "Apache-2.0",
1167.       "url": "https://github.com/basionwang-bot/HermesPet"
1168.     },
1169.     {
1170.       "name": "Agent-Learning-Hub",
1171.       "owner": "datawhalechina",
1172.       "full_name": "datawhalechina/Agent-Learning-Hub",
1173.       "description": "AI Agent 学习路线与资料库收集",
1174.       "language": null,
1175.       "stars": 164,
1176.       "forks": 13,
1177.       "created_at": "2026-05-17T06:41:12Z",
1178.       "topics": [],
1179.       "license": "MIT",
1180.       "url": "https://github.com/datawhalechina/Agent-Learning-Hub"
1181.     },
1182.     {
1183.       "name": "PhantomKiller",
1184.       "owner": "redteamfortress",
1185.       "full_name": "redteamfortress/PhantomKiller",
1186.       "description": "Another BYOVD process killer. works on all EDR's. fully signed.",
1187.       "language": "C++",
1188.       "stars": 163,
1189.       "forks": 30,
1190.       "created_at": "2026-05-19T07:00:59Z",
1191.       "topics": [
1192.         "byovd",
1193.         "edr",
1194.         "edr-bypass",
1195.         "edr-evasion",
1196.         "redteaming"
1197.       ],
1198.       "license": null,
1199.       "url": "https://github.com/redteamfortress/PhantomKiller"
1200.     },
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 1200-1500)

<details>
<summary>301 lines</summary>

```
1200.     },
1201.     {
1202.       "name": "expo-motion-tabs",
1203.       "owner": "rit3zh",
1204.       "full_name": "rit3zh/expo-motion-tabs",
1205.       "description": "⚡️ Smooth motion tabs for Expo Router",
1206.       "language": "TypeScript",
1207.       "stars": 162,
1208.       "forks": 10,
1209.       "created_at": "2026-05-17T12:21:01Z",
1210.       "topics": [],
1211.       "license": null,
1212.       "url": "https://github.com/rit3zh/expo-motion-tabs"
1213.     },
1214.     {
1215.       "name": "1m_release",
1216.       "owner": "2b2tplace",
1217.       "full_name": "2b2tplace/1m_release",
1218.       "description": "The Largest World Download Project in 2b2t, and in Minecraft altogether. Full info + Renders + Timelapses (+ Torrent soon)",
1219.       "language": null,
1220.       "stars": 161,
1221.       "forks": 1,
1222.       "created_at": "2026-05-16T21:24:05Z",
1223.       "topics": [],
1224.       "license": "CC0-1.0",
1225.       "url": "https://github.com/2b2tplace/1m_release"
1226.     },
1227.     {
1228.       "name": "kalshi-trading-bot",
1229.       "owner": "sachmalan",
1230.       "full_name": "sachmalan/kalshi-trading-bot",
1231.       "description": "kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot kalshi bot kalshi trading bot",
1232.       "language": "TypeScript",
1233.       "stars": 153,
1234.       "forks": 2072,
1235.       "created_at": "2026-05-17T06:24:13Z",
1236.       "topics": [
1237.         "bot",
1238.         "kalshi",
1239.         "kalshi-trade",
1240.         "kalshi-trading-bot",
1241.         "nodejs",
1242.         "trading"
1243.       ],
1244.       "license": null,
1245.       "url": "https://github.com/sachmalan/kalshi-trading-bot"
1246.     },
1247.     {
1248.       "name": "solana-trading-bot",
1249.       "owner": "VAENPP",
1250.       "full_name": "VAENPP/solana-trading-bot",
1251.       "description": "solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot solana bot solana trading bot",
1252.       "language": "TypeScript",
1253.       "stars": 152,
1254.       "forks": 2465,
1255.       "created_at": "2026-05-16T17:33:57Z",
1256.       "topics": [
1257.         "bot",
1258.         "nodejs",
1259.         "solana",
1260.         "solana-trade",
1261.         "solana-trading-bot",
1262.         "trading"
1263.       ],
1264.       "license": "MS-PL",
1265.       "url": "https://github.com/VAENPP/solana-trading-bot"
1266.     },
1267.     {
1268.       "name": "polymarket-mcp-server",
1269.       "owner": "japp-fi",
1270.       "full_name": "japp-fi/polymarket-mcp-server",
1271.       "description": "polymarket mcp server market discovery and analysis via public APIs; optional authenticated trading and portfolio tools when your wallet derives (or supplies) CLOB L2 credentials polymarket mcp server market discovery and analysis via public APIs; optional authenticated trading and portfolio tools when your wallet derives (or supplies) CLOB L2",
1272.       "language": "TypeScript",
1273.       "stars": 152,
1274.       "forks": 2600,
1275.       "created_at": "2026-05-15T19:57:43Z",
1276.       "topics": [
1277.         "mcp-server",
1278.         "mcp-servers",
1279.         "polymarket",
1280.         "polymarket-mcp-server"
1281.       ],
1282.       "license": null,
1283.       "url": "https://github.com/japp-fi/polymarket-mcp-server"
1284.     },
1285.     {
1286.       "name": "solana-pumpfun-token-bundler",
1287.       "owner": "Alchemz",
1288.       "full_name": "Alchemz/solana-pumpfun-token-bundler",
1289.       "description": "solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler pumpfun bundler solana bundler token bundler",
1290.       "language": "TypeScript",
1291.       "stars": 152,
1292.       "forks": 2465,
1293.       "created_at": "2026-05-16T18:57:25Z",
1294.       "topics": [
1295.         "axiom",
1296.         "bubblemap",
1297.         "bundler",
1298.         "meme",
1299.         "nodejs",
1300.         "pumpfun",
1301.         "solana",
1302.         "token",
1303.         "trading",
1304.         "trojan"
1305.       ],
1306.       "license": null,
1307.       "url": "https://github.com/Alchemz/solana-pumpfun-token-bundler"
1308.     },
1309.     {
1310.       "name": "polymarket-weather-trading-bot",
1311.       "owner": "OpenPatchLab",
1312.       "full_name": "OpenPatchLab/polymarket-weather-trading-bot",
1313.       "description": "polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot polymarket weather bot polymarket weather trading bot weather bot",
1314.       "language": "TypeScript",
1315.       "stars": 152,
1316.       "forks": 2469,
1317.       "created_at": "2026-05-16T20:11:40Z",
1318.       "topics": [
1319.         "bot",
1320.         "polymarket",
1321.         "trading",
1322.         "weather"
1323.       ],
1324.       "license": "MIT",
1325.       "url": "https://github.com/OpenPatchLab/polymarket-weather-trading-bot"
1326.     },
1327.     {
1328.       "name": "hyperliquid-trading-bot",
1329.       "owner": "fristork",
1330.       "full_name": "fristork/hyperliquid-trading-bot",
1331.       "description": "hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot hyperliquid trading bot hyperliquid bot hyperliquid copytrading bot",
1332.       "language": "TypeScript",
1333.       "stars": 151,
1334.       "forks": 2462,
1335.       "created_at": "2026-05-16T19:09:13Z",
1336.       "topics": [
1337.         "bot",
1338.         "hyperliquid",
1339.         "hyperliquid-dex",
1340.         "trading"
1341.       ],
1342.       "license": "Apache-2.0",
1343.       "url": "https://github.com/fristork/hyperliquid-trading-bot"
1344.     },
1345.     {
1346.       "name": "x-algorithm-wiki",
1347.       "owner": "cclank",
1348.       "full_name": "cclank/x-algorithm-wiki",
1349.       "description": "Architecture wiki for the open-sourced X \"For You\" recommendation algorithm (xai-org/x-algorithm) — 21 source-anchored pages",
1350.       "language": "HTML",
1351.       "stars": 144,
1352.       "forks": 14,
1353.       "created_at": "2026-05-16T02:58:56Z",
1354.       "topics": [],
1355.       "license": null,
1356.       "url": "https://github.com/cclank/x-algorithm-wiki"
1357.     },
1358.     {
1359.       "name": "Game-Icon-Pack",
1360.       "owner": "Nieobie",
1361.       "full_name": "Nieobie/Game-Icon-Pack",
1362.       "description": "570+ rounded style icons",
1363.       "language": null,
1364.       "stars": 143,
1365.       "forks": 10,
1366.       "created_at": "2026-05-17T03:05:14Z",
1367.       "topics": [
1368.         "game-assets",
1369.         "icon",
1370.         "icon-pack",
1371.         "icons",
1372.         "rounded-corners",
1373.         "svg",
1374.         "svg-icons"
1375.       ],
1376.       "license": "NOASSERTION",
1377.       "url": "https://github.com/Nieobie/Game-Icon-Pack"
1378.     },
1379.     {
1380.       "name": "lightroom-cc-on-linux",
1381.       "owner": "sander110419",
1382.       "full_name": "sander110419/lightroom-cc-on-linux",
1383.       "description": "Reproducible recipe for running Adobe Lightroom CC on Linux via Wine 11.8 staging. Researched and verified end-to-end by Claude Opus 4.7.",
1384.       "language": "C",
1385.       "stars": 139,
1386.       "forks": 4,
1387.       "created_at": "2026-05-17T09:17:14Z",
1388.       "topics": [],
1389.       "license": "NOASSERTION",
1390.       "url": "https://github.com/sander110419/lightroom-cc-on-linux"
1391.     },
1392.     {
1393.       "name": "PaperSpine",
1394.       "owner": "WUBING2023",
1395.       "full_name": "WUBING2023/PaperSpine",
1396.       "description": "PaperSpine is a motivation-driven Codex skill for learning from strong academic papers, building a paper’s central argument, and rewriting manuscripts through evidence-aware blueprints, revision matrices, and LaTeX-safe audits.",
1397.       "language": "Python",
1398.       "stars": 134,
1399.       "forks": 7,
1400.       "created_at": "2026-05-17T08:37:31Z",
1401.       "topics": [],
1402.       "license": "MIT",
1403.       "url": "https://github.com/WUBING2023/PaperSpine"
1404.     },
1405.     {
1406.       "name": "Cola-DLM",
1407.       "owner": "ByteDance-Seed",
1408.       "full_name": "ByteDance-Seed/Cola-DLM",
1409.       "description": "The codebase of Cola DLM",
1410.       "language": "Python",
1411.       "stars": 134,
1412.       "forks": 4,
1413.       "created_at": "2026-05-15T07:09:04Z",
1414.       "topics": [],
1415.       "license": "Apache-2.0",
1416.       "url": "https://github.com/ByteDance-Seed/Cola-DLM"
1417.     },
1418.     {
1419.       "name": "distributed-system-testing",
1420.       "owner": "shenli",
1421.       "full_name": "shenli/distributed-system-testing",
1422.       "description": "AI-agent skills for distributed-systems testing",
1423.       "language": null,
1424.       "stars": 130,
1425.       "forks": 9,
1426.       "created_at": "2026-05-16T20:51:13Z",
1427.       "topics": [
1428.         "agent-skills",
1429.         "ai-agents",
1430.         "chaos-engineering",
1431.         "distributed-systems",
1432.         "testing"
1433.       ],
1434.       "license": "MIT",
1435.       "url": "https://github.com/shenli/distributed-system-testing"
1436.     },
1437.     {
1438.       "name": "yapsnap",
1439.       "owner": "kouhxp",
1440.       "full_name": "kouhxp/yapsnap",
1441.       "description": "Snap any video URL or audio file into plaintext. No GPU. No cloud. One command.",
1442.       "language": "Python",
1443.       "stars": 129,
1444.       "forks": 3,
1445.       "created_at": "2026-05-20T21:01:24Z",
1446.       "topics": [],
1447.       "license": "Apache-2.0",
1448.       "url": "https://github.com/kouhxp/yapsnap"
1449.     },
1450.     {
1451.       "name": "QuantumFlow",
1452.       "owner": "zimingttkx",
1453.       "full_name": "zimingttkx/QuantumFlow",
1454.       "description": "QuantumFlow - Distributed LLM inference scheduling framework with multi-backend support (vLLM, TGI, SGLang), adaptive scheduling strategies, and cluster management.",
1455.       "language": "Python",
1456.       "stars": 126,
1457.       "forks": 0,
1458.       "created_at": "2026-05-16T03:51:46Z",
1459.       "topics": [],
1460.       "license": "MIT",
1461.       "url": "https://github.com/zimingttkx/QuantumFlow"
1462.     },
1463.     {
1464.       "name": "cdn-ip-finder",
1465.       "owner": "hossein8360",
1466.       "full_name": "hossein8360/cdn-ip-finder",
1467.       "description": "CDN IP finder for ShirOKhorshid domain fronting",
1468.       "language": "HTML",
1469.       "stars": 122,
1470.       "forks": 49,
1471.       "created_at": "2026-05-17T20:36:39Z",
1472.       "topics": [],
1473.       "license": null,
1474.       "url": "https://github.com/hossein8360/cdn-ip-finder"
1475.     },
1476.     {
1477.       "name": "Maya",
1478.       "owner": "ronaldo-avalos",
1479.       "full_name": "ronaldo-avalos/Maya",
1480.       "description": "🖥️ 📱 ▶️ Wrap your iPhone screen recordings in a beautiful device frame, add cinematic zoom moments, and export ready-to-share videos.",
1481.       "language": "Swift",
1482.       "stars": 120,
1483.       "forks": 16,
1484.       "created_at": "2026-05-17T04:00:39Z",
1485.       "topics": [
1486.         "iphone-screen-recordings",
1487.         "macos-app",
1488.         "screen-recordings"
1489.       ],
1490.       "license": "MIT",
1491.       "url": "https://github.com/ronaldo-avalos/Maya"
1492.     },
1493.     {
1494.       "name": "nikvpn-codespace",
1495.       "owner": "nikvpn-iran",
1496.       "full_name": "nikvpn-iran/nikvpn-codespace",
1497.       "description": "Free VLESS proxy using GitHub Codespaces - NikVPN for Iran",
1498.       "language": "Shell",
1499.       "stars": 117,
1500.       "forks": 947,
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 1500-1800)

<details>
<summary>301 lines</summary>

```
1500.       "forks": 947,
1501.       "created_at": "2026-05-15T15:07:46Z",
1502.       "topics": [],
1503.       "license": "MIT",
1504.       "url": "https://github.com/nikvpn-iran/nikvpn-codespace"
1505.     },
1506.     {
1507.       "name": "Awesome-Datasets-Hub",
1508.       "owner": "ahammadmejbah",
1509.       "full_name": "ahammadmejbah/Awesome-Datasets-Hub",
1510.       "description": "A curated collection of datasets for Large Language Models (LLMs), covering medical AI, NLP, multimodal learning, instruction tuning, reasoning, code generation, and evaluation benchmarks.",
1511.       "language": null,
1512.       "stars": 117,
1513.       "forks": 34,
1514.       "created_at": "2026-05-15T14:58:14Z",
1515.       "topics": [
1516.         "benchmark",
1517.         "benchmarking",
1518.         "deep-learning",
1519.         "deep-neural-networks",
1520.         "deeplearning",
1521.         "genetic-algorithm",
1522.         "llm",
1523.         "llm-evaluation",
1524.         "llm-inference",
1525.         "machine-learning",
1526.         "machine-learning-algorithms",
1527.         "machinelearning",
1528.         "neural-network"
1529.       ],
1530.       "license": null,
1531.       "url": "https://github.com/ahammadmejbah/Awesome-Datasets-Hub"
1532.     },
1533.     {
1534.       "name": "teams-policy-export",
1535.       "owner": "disintegr8te",
1536.       "full_name": "disintegr8te/teams-policy-export",
1537.       "description": "PowerShell tool to export Microsoft Teams policies and generate stakeholder decision workbooks",
1538.       "language": "PowerShell",
1539.       "stars": 116,
1540.       "forks": 12,
1541.       "created_at": "2026-05-17T19:16:59Z",
1542.       "topics": [],
1543.       "license": "Apache-2.0",
1544.       "url": "https://github.com/disintegr8te/teams-policy-export"
1545.     },
1546.     {
1547.       "name": "founders-playbook-zh",
1548.       "owner": "yangliu2060",
1549.       "full_name": "yangliu2060/founders-playbook-zh",
1550.       "description": "Anthropic《The Founder's Playbook: Building an AI-Native Startup》非官方中文翻译版（含中文信息图表）",
1551.       "language": null,
1552.       "stars": 115,
1553.       "forks": 15,
1554.       "created_at": "2026-05-15T14:12:49Z",
1555.       "topics": [],
1556.       "license": null,
1557.       "url": "https://github.com/yangliu2060/founders-playbook-zh"
1558.     },
1559.     {
1560.       "name": "vibe-observer",
1561.       "owner": "AIchovy",
1562.       "full_name": "AIchovy/vibe-observer",
1563.       "description": "Claude Code Tracer & Observer",
1564.       "language": "Rust",
1565.       "stars": 115,
1566.       "forks": 1,
1567.       "created_at": "2026-05-17T05:50:21Z",
1568.       "topics": [],
1569.       "license": "MIT",
1570.       "url": "https://github.com/AIchovy/vibe-observer"
1571.     },
1572.     {
1573.       "name": "HOA",
1574.       "owner": "harmony-on-android",
1575.       "full_name": "harmony-on-android/HOA",
1576.       "description": "Run OpenHarmony hap on Android",
1577.       "language": "Kotlin",
1578.       "stars": 110,
1579.       "forks": 5,
1580.       "created_at": "2026-05-15T16:22:46Z",
1581.       "topics": [],
1582.       "license": null,
1583.       "url": "https://github.com/harmony-on-android/HOA"
1584.     },
1585.     {
1586.       "name": "NESLab",
1587.       "owner": "ip-arch",
1588.       "full_name": "ip-arch/NESLab",
1589.       "description": "Educational materials for Embedded systems with NES",
1590.       "language": "C++",
1591.       "stars": 109,
1592.       "forks": 6,
1593.       "created_at": "2026-05-17T01:15:37Z",
1594.       "topics": [],
1595.       "license": "GPL-3.0",
1596.       "url": "https://github.com/ip-arch/NESLab"
1597.     },
1598.     {
1599.       "name": "tilelang-cuda-skills",
1600.       "owner": "sablin39",
1601.       "full_name": "sablin39/tilelang-cuda-skills",
1602.       "description": "Skills for writing tilelang and debugging with CUDA toolkits. ",
1603.       "language": "Python",
1604.       "stars": 108,
1605.       "forks": 3,
1606.       "created_at": "2026-05-16T12:17:08Z",
1607.       "topics": [],
1608.       "license": null,
1609.       "url": "https://github.com/sablin39/tilelang-cuda-skills"
1610.     },
1611.     {
1612.       "name": "ClockMaster",
1613.       "owner": "amrdoh",
1614.       "full_name": "amrdoh/ClockMaster",
1615.       "description": "Material Expressive clock app for android 🕛⏰",
1616.       "language": "Kotlin",
1617.       "stars": 102,
1618.       "forks": 1194,
1619.       "created_at": "2026-05-15T04:48:13Z",
1620.       "topics": [],
1621.       "license": "Apache-2.0",
1622.       "url": "https://github.com/amrdoh/ClockMaster"
1623.     },
1624.     {
1625.       "name": "markov-hedge-fund-method",
1626.       "owner": "jackson-video-resources",
1627.       "full_name": "jackson-video-resources/markov-hedge-fund-method",
1628.       "description": "Markov regime detection skill + one-shot install prompt + Pine indicator. Companion to Quant Series video 1. Framework by Roan (@RohOnChain).",
1629.       "language": "Python",
1630.       "stars": 102,
1631.       "forks": 63,
1632.       "created_at": "2026-05-19T14:22:02Z",
1633.       "topics": [],
1634.       "license": "NOASSERTION",
1635.       "url": "https://github.com/jackson-video-resources/markov-hedge-fund-method"
1636.     },
1637.     {
1638.       "name": "OpenCodex",
1639.       "owner": "RyensX",
1640.       "full_name": "RyensX/OpenCodex",
1641.       "description": "OpenCodex是一个轻量级Codex运行环境，可以让你的任意设备通过Web使用你的电脑上的Codex。/ OpenCodex is a lightweight Codex runtime environment that allows any of your devices to use the Codex on your computer via the Web.",
1642.       "language": "TypeScript",
1643.       "stars": 102,
1644.       "forks": 9,
1645.       "created_at": "2026-05-15T15:33:26Z",
1646.       "topics": [],
1647.       "license": "AGPL-3.0",
1648.       "url": "https://github.com/RyensX/OpenCodex"
1649.     },
1650.     {
1651.       "name": "google-ai-search-optimization",
1652.       "owner": "deepakness",
1653.       "full_name": "deepakness/google-ai-search-optimization",
1654.       "description": "Unofficial Agent Skill based on Google Search guidance for AI Overviews, AI Mode, and SEO audits.",
1655.       "language": null,
1656.       "stars": 98,
1657.       "forks": 5,
1658.       "created_at": "2026-05-16T13:55:02Z",
1659.       "topics": [
1660.         "ai-agents",
1661.         "ai-seo",
1662.         "seo"
1663.       ],
1664.       "license": null,
1665.       "url": "https://github.com/deepakness/google-ai-search-optimization"
1666.     },
1667.     {
1668.       "name": "comfyui-mesh",
1669.       "owner": "shootthesound",
1670.       "full_name": "shootthesound/comfyui-mesh",
1671.       "description": "Split FLUX.2 and LTX 2.3 across two GPUs (LAN or same-machine) — NVENC compresses activations live on the wire. Icarus (ComfyUI node) + Daedalus (back-half server).",
1672.       "language": "Python",
1673.       "stars": 98,
1674.       "forks": 13,
1675.       "created_at": "2026-05-16T01:48:45Z",
1676.       "topics": [
1677.         "comfyui",
1678.         "comfyui-node",
1679.         "diffusion-models",
1680.         "distributed-inference",
1681.         "flux",
1682.         "flux2",
1683.         "image-generation",
1684.         "ltx-video",
1685.         "multi-gpu",
1686.         "nvenc",
1687.         "pipeline-parallelism",
1688.         "pytorch",
1689.         "video-generation"
1690.       ],
1691.       "license": null,
1692.       "url": "https://github.com/shootthesound/comfyui-mesh"
1693.     },
1694.     {
1695.       "name": "ratscad",
1696.       "owner": "qewer33",
1697.       "full_name": "qewer33/ratscad",
1698.       "description": "CAD for the terminal",
1699.       "language": "Rust",
1700.       "stars": 96,
1701.       "forks": 3,
1702.       "created_at": "2026-05-17T14:37:30Z",
1703.       "topics": [],
1704.       "license": "MIT",
1705.       "url": "https://github.com/qewer33/ratscad"
1706.     },
1707.     {
1708.       "name": "WindsurfX",
1709.       "owner": "huey1in",
1710.       "full_name": "huey1in/WindsurfX",
1711.       "description": "Windsurf 协议注册机 | Windsurf (windsurf.com) 批量自动注册工具",
1712.       "language": "Python",
1713.       "stars": 95,
1714.       "forks": 41,
1715.       "created_at": "2026-05-18T12:27:52Z",
1716.       "topics": [
1717.         "auto-register",
1718.         "codeium-cascade",
1719.         "moemail",
1720.         "python",
1721.         "windsurf"
1722.       ],
1723.       "license": "MIT",
1724.       "url": "https://github.com/huey1in/WindsurfX"
1725.     },
1726.     {
1727.       "name": "forza-painter-fh6",
1728.       "owner": "bvzrays",
1729.       "full_name": "bvzrays/forza-painter-fh6",
1730.       "description": "Vinyl Painter Import Tool - FH6 ( Original repository: https://github.com/forza-painter/forza-painter )",
1731.       "language": "Python",
1732.       "stars": 95,
1733.       "forks": 7,
1734.       "created_at": "2026-05-17T09:06:18Z",
1735.       "topics": [],
1736.       "license": "NOASSERTION",
1737.       "url": "https://github.com/bvzrays/forza-painter-fh6"
1738.     },
1739.     {
1740.       "name": "tech-interview-handbook",
1741.       "owner": "julianommartins",
1742.       "full_name": "julianommartins/tech-interview-handbook",
1743.       "description": "Um guia honesto sobre entrevistas técnicas, system design e senioridade em engenharia de software, baseado em padrões observados ao longo de centenas de entrevistas reais.",
1744.       "language": null,
1745.       "stars": 94,
1746.       "forks": 7,
1747.       "created_at": "2026-05-18T13:31:33Z",
1748.       "topics": [],
1749.       "license": "Apache-2.0",
1750.       "url": "https://github.com/julianommartins/tech-interview-handbook"
1751.     },
1752.     {
1753.       "name": "Windows-Activator",
1754.       "owner": "gazelleandrewrasmussenmouj2",
1755.       "full_name": "gazelleandrewrasmussenmouj2/Windows-Activator",
1756.       "description": "Windows KMS activator office365",
1757.       "language": null,
1758.       "stars": 93,
1759.       "forks": 66,
1760.       "created_at": "2026-05-16T15:17:13Z",
1761.       "topics": [
1762.         "copilot",
1763.         "kms",
1764.         "microsoft",
1765.         "office365",
1766.         "windows-10",
1767.         "windows-11",
1768.         "windows-service"
1769.       ],
1770.       "license": null,
1771.       "url": "https://github.com/gazelleandrewrasmussenmouj2/Windows-Activator"
1772.     },
1773.     {
1774.       "name": "Brovan",
1775.       "owner": "AdvDebug",
1776.       "full_name": "AdvDebug/Brovan",
1777.       "description": "Brovan is a user-mode x86_64 binary emulator for PE, ELF, memory dumps, and unrecognized file formats.",
1778.       "language": "C#",
1779.       "stars": 92,
1780.       "forks": 7,
1781.       "created_at": "2026-05-15T02:12:23Z",
1782.       "topics": [
1783.         "antivirus",
1784.         "binary-analysis",
1785.         "csharp",
1786.         "drm",
1787.         "emulator",
1788.         "linux",
1789.         "malware",
1790.         "malware-analysis",
1791.         "reverse-engineering",
1792.         "sandbox",
1793.         "sandboxing",
1794.         "windows"
1795.       ],
1796.       "license": "GPL-2.0",
1797.       "url": "https://github.com/AdvDebug/Brovan"
1798.     },
1799.     {
1800.       "name": "POHA",
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 1800-2100)

<details>
<summary>301 lines</summary>

```
1800.       "name": "POHA",
1801.       "owner": "jigripokri",
1802.       "full_name": "jigripokri/POHA",
1803.       "description": "Personal Overnight Helper Agent. Runs while you sleep. Serves up a morning brief before your alarm.",
1804.       "language": null,
1805.       "stars": 92,
1806.       "forks": 29,
1807.       "created_at": "2026-05-18T04:14:57Z",
1808.       "topics": [
1809.         "ai-assistant",
1810.         "claude",
1811.         "claude-code",
1812.         "morning-brief",
1813.         "personal-assistant",
1814.         "poha",
1815.         "productivity",
1816.         "second-brain"
1817.       ],
1818.       "license": "MIT",
1819.       "url": "https://github.com/jigripokri/POHA"
1820.     },
1821.     {
1822.       "name": "WindowsDelta",
1823.       "owner": "akuma815",
1824.       "full_name": "akuma815/WindowsDelta",
1825.       "description": "Delta is a precision-engineered executor , third-party client for Roblox, specifically architected to dismantle performance bottlenecks. By bypassing standard client limitations, Delta provides a high-fidelity, low-latency environment tailored for power users and competitive players on Windows 10 and 11.",
1826.       "language": null,
1827.       "stars": 90,
1828.       "forks": 0,
1829.       "created_at": "2026-05-16T08:42:29Z",
1830.       "topics": [],
1831.       "license": "MIT",
1832.       "url": "https://github.com/akuma815/WindowsDelta"
1833.     },
1834.     {
1835.       "name": "rmux",
1836.       "owner": "Helvesec",
1837.       "full_name": "Helvesec/rmux",
1838.       "description": "Universal Rust multiplexer with a typed SDK — drive any CLI or TUI app from code. Native on Linux, macOS, and Windows.",
1839.       "language": "Rust",
1840.       "stars": 90,
1841.       "forks": 1,
1842.       "created_at": "2026-05-15T15:22:10Z",
1843.       "topics": [
1844.         "agent",
1845.         "ai",
1846.         "multiplexer",
1847.         "rust"
1848.       ],
1849.       "license": "Apache-2.0",
1850.       "url": "https://github.com/Helvesec/rmux"
1851.     },
1852.     {
1853.       "name": "trading-bot",
1854.       "owner": "yenjenchen",
1855.       "full_name": "yenjenchen/trading-bot",
1856.       "description": "Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot Polymarket trading bot polymarket trading bot bot",
1857.       "language": "TypeScript",
1858.       "stars": 87,
1859.       "forks": 1233,
1860.       "created_at": "2026-05-20T14:51:28Z",
1861.       "topics": [
1862.         "arbitrage-bot",
1863.         "arbitrage-trading-bot",
1864.         "bot",
1865.         "poly-bot",
1866.         "polymarket-arbitrage-bot",
1867.         "polymarket-arbitrage-trading-bot",
1868.         "polymarket-bot",
1869.         "polymarket-trading-bot",
1870.         "trading-bot"
1871.       ],
1872.       "license": null,
1873.       "url": "https://github.com/yenjenchen/trading-bot"
1874.     },
1875.     {
1876.       "name": "Valorant-External-Framework",
1877.       "owner": "MediatorSpeak",
1878.       "full_name": "MediatorSpeak/Valorant-External-Framework",
1879.       "description": "A clean C++ External overlay featuring ESP, Aimbot, and Skinchanger concepts. Powered by a kernel-mode driver for educational purposes. Regularly update",
1880.       "language": null,
1881.       "stars": 86,
1882.       "forks": 42,
1883.       "created_at": "2026-05-16T19:31:14Z",
1884.       "topics": [
1885.         "cpp",
1886.         "kernel-driver",
1887.         "overlay",
1888.         "reverse-engineering",
1889.         "valorant"
1890.       ],
1891.       "license": "MIT",
1892.       "url": "https://github.com/MediatorSpeak/Valorant-External-Framework"
1893.     },
1894.     {
1895.       "name": "cyber_rss",
1896.       "owner": "mr-r3b00t",
1897.       "full_name": "mr-r3b00t/cyber_rss",
1898.       "description": "a list of useful feeds",
1899.       "language": null,
1900.       "stars": 86,
1901.       "forks": 10,
1902.       "created_at": "2026-05-15T20:07:03Z",
1903.       "topics": [],
1904.       "license": null,
1905.       "url": "https://github.com/mr-r3b00t/cyber_rss"
1906.     },
1907.     {
1908.       "name": "MergeableView",
1909.       "owner": "noppefoxwolf",
1910.       "full_name": "noppefoxwolf/MergeableView",
1911.       "description": "SwiftUI package for merging Liquid Glass views with drag gestures.",
1912.       "language": "Swift",
1913.       "stars": 83,
1914.       "forks": 1,
1915.       "created_at": "2026-05-15T15:57:09Z",
1916.       "topics": [
1917.         "animation",
1918.         "drag-gesture",
1919.         "glass-effect",
1920.         "ios",
1921.         "liquid-glass",
1922.         "mergeable",
1923.         "swift",
1924.         "swift-package",
1925.         "swiftui"
1926.       ],
1927.       "license": "MIT",
1928.       "url": "https://github.com/noppefoxwolf/MergeableView"
1929.     },
1930.     {
1931.       "name": "dejavu",
1932.       "owner": "JSingletonAI",
1933.       "full_name": "JSingletonAI/dejavu",
1934.       "description": "Memory that follows you across every AI tool. No cloud storage. No account required. Set it up once, use it everywhere.",
1935.       "language": "Python",
1936.       "stars": 83,
1937.       "forks": 6,
1938.       "created_at": "2026-05-18T23:04:01Z",
1939.       "topics": [
1940.         "ai-agents",
1941.         "claude",
1942.         "llm",
1943.         "local-first",
1944.         "mcp",
1945.         "memory",
1946.         "privacy",
1947.         "rag",
1948.         "sqlite",
1949.         "venice"
1950.       ],
1951.       "license": "Apache-2.0",
1952.       "url": "https://github.com/JSingletonAI/dejavu"
1953.     },
1954.     {
1955.       "name": "quickshell",
1956.       "owner": "bjarneo",
1957.       "full_name": "bjarneo/quickshell",
1958.       "description": "Quickshell configs for Omarchy. Navbar. Omni menu. + more",
1959.       "language": "QML",
1960.       "stars": 83,
1961.       "forks": 1,
1962.       "created_at": "2026-05-16T18:41:26Z",
1963.       "topics": [
1964.         "omarchy"
1965.       ],
1966.       "license": null,
1967.       "url": "https://github.com/bjarneo/quickshell"
1968.     },
1969.     {
1970.       "name": "type-review",
1971.       "owner": "xiaolai",
1972.       "full_name": "xiaolai/type-review",
1973.       "description": "TYPE — adaptive typing practice that lives in your browser. Live at https://type.review",
1974.       "language": "TypeScript",
1975.       "stars": 82,
1976.       "forks": 17,
1977.       "created_at": "2026-05-17T07:34:55Z",
1978.       "topics": [],
1979.       "license": "NOASSERTION",
1980.       "url": "https://github.com/xiaolai/type-review"
1981.     },
1982.     {
1983.       "name": "CyberSecurity-Skills",
1984.       "owner": "Hi-FullHouse",
1985.       "full_name": "Hi-FullHouse/CyberSecurity-Skills",
1986.       "description": "一个由AI运维的网络安全Skill知识库",
1987.       "language": "Python",
1988.       "stars": 82,
1989.       "forks": 14,
1990.       "created_at": "2026-05-15T09:47:32Z",
1991.       "topics": [],
1992.       "license": "MIT",
1993.       "url": "https://github.com/Hi-FullHouse/CyberSecurity-Skills"
1994.     },
1995.     {
1996.       "name": "windsurf-assistant",
1997.       "owner": "zhouyoukang1234-spec",
1998.       "full_name": "zhouyoukang1234-spec/windsurf-assistant",
1999.       "description": "A fully decentralized Windsurf assistant &mdash; **一气化三清 · 道并行而不悖** · 印 65 三清立 · 印 101 大道至简 · **印 ∞ 道法自然推进到底·★ 对照 tab 默见·左 A/B 双路·中 WAM 无感** · 反者道之动 · 为道日损.",
2000.       "language": "JavaScript",
2001.       "stars": 81,
2002.       "forks": 18,
2003.       "created_at": "2026-05-17T15:43:18Z",
2004.       "topics": [],
2005.       "license": "MIT",
2006.       "url": "https://github.com/zhouyoukang1234-spec/windsurf-assistant"
2007.     },
2008.     {
2009.       "name": "huashu-weread",
2010.       "owner": "alchaincyf",
2011.       "full_name": "alchaincyf/huashu-weread",
2012.       "description": "微信读书高阶顾问 · 在官方 weread skill 之上加一层「读书顾问的工作流」· 书架+笔记交叉分析 · 4 个 workflow (advisor/path/alchemy/review) · Made by 花叔",
2013.       "language": null,
2014.       "stars": 77,
2015.       "forks": 4,
2016.       "created_at": "2026-05-17T12:12:02Z",
2017.       "topics": [],
2018.       "license": "MIT",
2019.       "url": "https://github.com/alchaincyf/huashu-weread"
2020.     },
2021.     {
2022.       "name": "usage",
2023.       "owner": "aqua5230",
2024.       "full_name": "aqua5230/usage",
2025.       "description": "Privacy-first macOS menu bar tracker for Claude Code & Codex usage — no provider API calls",
2026.       "language": "Python",
2027.       "stars": 76,
2028.       "forks": 13,
2029.       "created_at": "2026-05-17T11:52:27Z",
2030.       "topics": [
2031.         "claude-code",
2032.         "codex",
2033.         "launchagent",
2034.         "macos",
2035.         "menubar",
2036.         "pyobjc",
2037.         "statusline-hook",
2038.         "usage-tracker"
2039.       ],
2040.       "license": "MIT",
2041.       "url": "https://github.com/aqua5230/usage"
2042.     },
2043.     {
2044.       "name": "SWIM",
2045.       "owner": "HumanMLLM",
2046.       "full_name": "HumanMLLM/SWIM",
2047.       "description": "Official Code for See What I Mean: Aligning Vision and Language Representations for Video Fine-grained Object Understanding (CVPR 2026)",
2048.       "language": "Python",
2049.       "stars": 75,
2050.       "forks": 0,
2051.       "created_at": "2026-05-18T03:55:19Z",
2052.       "topics": [],
2053.       "license": null,
2054.       "url": "https://github.com/HumanMLLM/SWIM"
2055.     },
2056.     {
2057.       "name": "openwrt-win98-theme",
2058.       "owner": "fffonion",
2059.       "full_name": "fffonion/openwrt-win98-theme",
2060.       "description": "OpenWRT Windows 98 Theme",
2061.       "language": "CSS",
2062.       "stars": 75,
2063.       "forks": 3,
2064.       "created_at": "2026-05-15T20:20:06Z",
2065.       "topics": [],
2066.       "license": null,
2067.       "url": "https://github.com/fffonion/openwrt-win98-theme"
2068.     },
2069.     {
2070.       "name": "stainful",
2071.       "owner": "stainlu",
2072.       "full_name": "stainlu/stainful",
2073.       "description": "The open-source Stainless — point your existing stainless.yml at it and get the same idiomatic Python SDK. Zero migration. No SaaS.",
2074.       "language": "Python",
2075.       "stars": 75,
2076.       "forks": 8,
2077.       "created_at": "2026-05-19T08:37:26Z",
2078.       "topics": [
2079.         "api-client",
2080.         "codegen",
2081.         "developer-tools",
2082.         "httpx",
2083.         "openapi",
2084.         "openapi-codegen",
2085.         "oss-alternative",
2086.         "pydantic",
2087.         "python",
2088.         "sdk-generator",
2089.         "stainless"
2090.       ],
2091.       "license": "MIT",
2092.       "url": "https://github.com/stainlu/stainful"
2093.     },
2094.     {
2095.       "name": "reframe",
2096.       "owner": "mrdoob",
2097.       "full_name": "mrdoob/reframe",
2098.       "description": "Webapp for framing a video clip and exporting an MP4.",
2099.       "language": "JavaScript",
2100.       "stars": 74,
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 8200-8316)

<details>
<summary>117 lines</summary>

```
8200.       "stars": 51877,
8201.       "forks": 4721,
8202.       "created_at": "2016-11-29T17:13:37Z",
8203.       "topics": [
8204.         "angular",
8205.         "ast",
8206.         "css",
8207.         "flow",
8208.         "formatter",
8209.         "graphql",
8210.         "html",
8211.         "javascript",
8212.         "json",
8213.         "jsx",
8214.         "less",
8215.         "markdown",
8216.         "prettier",
8217.         "printer",
8218.         "scss",
8219.         "typescript",
8220.         "vue",
8221.         "yaml"
8222.       ],
8223.       "license": "MIT",
8224.       "url": "https://github.com/prettier/prettier"
8225.     }
8226.   ],
8227.   "signals": {
8228.     "top_topics": [
8229.       {
8230.         "topic": "ai",
8231.         "count": 37
8232.       },
8233.       {
8234.         "topic": "python",
8235.         "count": 37
8236.       },
8237.       {
8238.         "topic": "llm",
8239.         "count": 30
8240.       },
8241.       {
8242.         "topic": "javascript",
8243.         "count": 29
8244.       },
8245.       {
8246.         "topic": "hacktoberfest",
8247.         "count": 24
8248.       },
8249.       {
8250.         "topic": "typescript",
8251.         "count": 23
8252.       },
8253.       {
8254.         "topic": "ai-agents",
8255.         "count": 20
8256.       },
8257.       {
8258.         "topic": "nodejs",
8259.         "count": 20
8260.       },
8261.       {
8262.         "topic": "react",
8263.         "count": 18
8264.       },
8265.       {
8266.         "topic": "claude-code",
8267.         "count": 17
8268.       },
8269.       {
8270.         "topic": "rust",
8271.         "count": 17
8272.       },
8273.       {
8274.         "topic": "claude",
8275.         "count": 16
8276.       },
8277.       {
8278.         "topic": "mcp",
8279.         "count": 15
8280.       },
8281.       {
8282.         "topic": "chatgpt",
8283.         "count": 15
8284.       },
8285.       {
8286.         "topic": "go",
8287.         "count": 15
8288.       }
8289.     ]
8290.   },
8291.   "metadata": {
8292.     "api_calls_used": 27,
8293.     "cache_hits": 365,
8294.     "stale_cache_hits": 0,
8295.     "rate_limit_limit": 5000,
8296.     "rate_limit_remaining": 4932,
8297.     "rate_limit_reset": 1779352962,
8298.     "rate_limit_resource": "core",
8299.     "partial_failures": [],
8300.     "filter_summary": {
8301.       "new_repos": {
8302.         "missing_description": 32,
8303.         "low_signal_keyword": 6,
8304.         "missing_readme": 5,
8305.         "low_signal_topic": 1
8306.       },
8307.       "trending_repos": {
8308.         "low_signal_topic": 8,
8309.         "low_signal_phrase": 1,
8310.         "low_signal_keyword": 5,
8311.         "template_repo": 1
8312.       }
8313.     },
8314.     "snapshot_path": "data/snapshots/2026-W21-stars.json"
8315.   }
8316. }
```

</details>


### 💬 Copilot

Now let me look at the trending repos section and the correlations:

### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 2100-2500)

<details>
<summary>401 lines</summary>

```
2100.       "stars": 74,
2101.       "forks": 6,
2102.       "created_at": "2026-05-16T02:55:55Z",
2103.       "topics": [],
2104.       "license": "MIT",
2105.       "url": "https://github.com/mrdoob/reframe"
2106.     },
2107.     {
2108.       "name": "Glass",
2109.       "owner": "azw413",
2110.       "full_name": "azw413/Glass",
2111.       "description": "Glass - a fast and free IDA Pro alternative",
2112.       "language": "Rust",
2113.       "stars": 73,
2114.       "forks": 5,
2115.       "created_at": "2026-05-15T18:41:51Z",
2116.       "topics": [],
2117.       "license": "GPL-3.0",
2118.       "url": "https://github.com/azw413/Glass"
2119.     },
2120.     {
2121.       "name": "Fortnite-External-Cheat-2026",
2122.       "owner": "RastProxy88",
2123.       "full_name": "RastProxy88/Fortnite-External-Cheat-2026",
2124.       "description": "⭐️ External Fortnite cheat featuring smooth aimbot, player/item ESP with skeleton and loot rarity, and a fully external overlay. No injection needed — reads memory through kernel driver. Undetected as of May 2026. Built in C++20 with ImGui menu, config system, and regular offset updates.⭐️ ",
2125.       "language": "C++",
2126.       "stars": 72,
2127.       "forks": 54,
2128.       "created_at": "2026-05-20T18:33:06Z",
2129.       "topics": [
2130.         "cheatfree",
2131.         "fortnite",
2132.         "fortnite-god-menu",
2133.         "gamehacks",
2134.         "gs",
2135.         "ofgn",
2136.         "undeteced"
2137.       ],
2138.       "license": "MIT",
2139.       "url": "https://github.com/RastProxy88/Fortnite-External-Cheat-2026"
2140.     },
2141.     {
2142.       "name": "qiaomu-userscripts",
2143.       "owner": "joeseesun",
2144.       "full_name": "joeseesun/qiaomu-userscripts",
2145.       "description": "Tampermonkey userscripts for WeChat, Douyin, and X content workflows",
2146.       "language": "JavaScript",
2147.       "stars": 72,
2148.       "forks": 9,
2149.       "created_at": "2026-05-19T16:12:42Z",
2150.       "topics": [
2151.         "douyin",
2152.         "productivity",
2153.         "tampermonkey",
2154.         "userscript",
2155.         "userscripts",
2156.         "wechat",
2157.         "x",
2158.         "xiaohongshu"
2159.       ],
2160.       "license": "MIT",
2161.       "url": "https://github.com/joeseesun/qiaomu-userscripts"
2162.     },
2163.     {
2164.       "name": "CryptoBots-Solana-Sniper-PumpFun-Free",
2165.       "owner": "DeFiCryptoBots",
2166.       "full_name": "DeFiCryptoBots/CryptoBots-Solana-Sniper-PumpFun-Free",
2167.       "description": "Our Free Solana Sniper for Pumpfun with multiple strategies",
2168.       "language": "JavaScript",
2169.       "stars": 70,
2170.       "forks": 8,
2171.       "created_at": "2026-05-18T13:38:23Z",
2172.       "topics": [
2173.         "snipe-bot",
2174.         "snipebot"
2175.       ],
2176.       "license": null,
2177.       "url": "https://github.com/DeFiCryptoBots/CryptoBots-Solana-Sniper-PumpFun-Free"
2178.     },
2179.     {
2180.       "name": "can-i-finetune-this",
2181.       "owner": "DaoyuanLi2816",
2182.       "full_name": "DaoyuanLi2816/can-i-finetune-this",
2183.       "description": "Estimate whether a Hugging Face model fits and fine-tunes on your local GPU.",
2184.       "language": "Python",
2185.       "stars": 70,
2186.       "forks": 10,
2187.       "created_at": "2026-05-16T17:14:13Z",
2188.       "topics": [
2189.         "bitsandbytes",
2190.         "fine-tuning",
2191.         "gpu",
2192.         "hugging-face",
2193.         "llm",
2194.         "lora",
2195.         "memory-estimation",
2196.         "peft",
2197.         "pytorch",
2198.         "qlora",
2199.         "transformers",
2200.         "vram"
2201.       ],
2202.       "license": "MIT",
2203.       "url": "https://github.com/DaoyuanLi2816/can-i-finetune-this"
2204.     },
2205.     {
2206.       "name": "nextssrf",
2207.       "owner": "ynsmroztas",
2208.       "full_name": "ynsmroztas/nextssrf",
2209.       "description": "NextSSRF — CVE-2026-44578 Scanner & Exploit          ║ ║   Next.js WebSocket Upgrade Handler SSRF",
2210.       "language": "Python",
2211.       "stars": 70,
2212.       "forks": 16,
2213.       "created_at": "2026-05-15T05:02:38Z",
2214.       "topics": [],
2215.       "license": null,
2216.       "url": "https://github.com/ynsmroztas/nextssrf"
2217.     },
2218.     {
2219.       "name": "renewlet",
2220.       "owner": "zhiyingzzhou",
2221.       "full_name": "zhiyingzzhou/renewlet",
2222.       "description": "Self-hosted subscription tracker for recurring renewals, with timezone-aware reminders, six notification channels, budgets, and spending insights.",
2223.       "language": "TypeScript",
2224.       "stars": 69,
2225.       "forks": 10,
2226.       "created_at": "2026-05-17T00:39:48Z",
2227.       "topics": [],
2228.       "license": "MIT",
2229.       "url": "https://github.com/zhiyingzzhou/renewlet"
2230.     },
2231.     {
2232.       "name": "The-Delta-Executor",
2233.       "owner": "thaddeuswilkersonqbaj13",
2234.       "full_name": "thaddeuswilkersonqbaj13/The-Delta-Executor",
2235.       "description": "Advanced Delta Executor Framework ( Utility ) . Lua execution engine for perfomance testing , debugging , and custom script development .",
2236.       "language": "Lua",
2237.       "stars": 69,
2238.       "forks": 11,
2239.       "created_at": "2026-05-17T17:11:12Z",
2240.       "topics": [
2241.         "roblox",
2242.         "roblox-script-lua",
2243.         "scripts"
2244.       ],
2245.       "license": null,
2246.       "url": "https://github.com/thaddeuswilkersonqbaj13/The-Delta-Executor"
2247.     },
2248.     {
2249.       "name": "peezy-cli",
2250.       "owner": "p0systems",
2251.       "full_name": "p0systems/peezy-cli",
2252.       "description": "A terminal coding agent for real project work.",
2253.       "language": "TypeScript",
2254.       "stars": 68,
2255.       "forks": 18,
2256.       "created_at": "2026-05-17T19:42:31Z",
2257.       "topics": [],
2258.       "license": "MIT",
2259.       "url": "https://github.com/p0systems/peezy-cli"
2260.     },
2261.     {
2262.       "name": "OpenYSM",
2263.       "owner": "OpenYSMDev",
2264.       "full_name": "OpenYSMDev/OpenYSM",
2265.       "description": "A mod that modifies the vanilla player model",
2266.       "language": "Java",
2267.       "stars": 64,
2268.       "forks": 1,
2269.       "created_at": "2026-05-20T13:31:18Z",
2270.       "topics": [],
2271.       "license": "MIT",
2272.       "url": "https://github.com/OpenYSMDev/OpenYSM"
2273.     },
2274.     {
2275.       "name": "ARIS-in-AI-Offer",
2276.       "owner": "wanshuiyin",
2277.       "full_name": "wanshuiyin/ARIS-in-AI-Offer",
2278.       "description": "Bilingual ML / LLM / multimodal / diffusion / agent / generative-model interview cheat sheets (秋招经验手册) — single-file HTML reads anywhere on phone, iPad, and laptop — auto-generated by the ARIS /render-html workflow 🌱",
2279.       "language": "Python",
2280.       "stars": 64,
2281.       "forks": 3,
2282.       "created_at": "2026-05-19T04:51:36Z",
2283.       "topics": [
2284.         "ai-interview",
2285.         "aris",
2286.         "autumn-recruiting",
2287.         "cheatsheet",
2288.         "chinese",
2289.         "claude-code",
2290.         "deep-learning",
2291.         "diffusion",
2292.         "flow-matching",
2293.         "interview-prep",
2294.         "llm",
2295.         "machine-learning",
2296.         "moe",
2297.         "nerf",
2298.         "pytorch",
2299.         "quantization",
2300.         "rlhf",
2301.         "transformer",
2302.         "video-generation",
2303.         "vision-language-model"
2304.       ],
2305.       "license": "MIT",
2306.       "url": "https://github.com/wanshuiyin/ARIS-in-AI-Offer"
2307.     },
2308.     {
2309.       "name": "PlayDL",
2310.       "owner": "ZethRise",
2311.       "full_name": "ZethRise/PlayDL",
2312.       "description": "a google play APK File Downloader Bot for telegram in Python",
2313.       "language": "Python",
2314.       "stars": 63,
2315.       "forks": 11,
2316.       "created_at": "2026-05-15T04:17:15Z",
2317.       "topics": [
2318.         "downloader",
2319.         "python",
2320.         "telegram"
2321.       ],
2322.       "license": "MIT",
2323.       "url": "https://github.com/ZethRise/PlayDL"
2324.     },
2325.     {
2326.       "name": "novel2hermes_jp",
2327.       "owner": "kgmkm",
2328.       "full_name": "kgmkm/novel2hermes_jp",
2329.       "description": "メモリ機能が強力なhermes-agentと、日本語検索に強い外部メモリvecmemoriを活かし、長文に耐える小説を企画/プロッティング/執筆するためのskills.md",
2330.       "language": null,
2331.       "stars": 63,
2332.       "forks": 6,
2333.       "created_at": "2026-05-16T08:52:53Z",
2334.       "topics": [],
2335.       "license": "MIT",
2336.       "url": "https://github.com/kgmkm/novel2hermes_jp"
2337.     },
2338.     {
2339.       "name": "bc250-40cu-unlock",
2340.       "owner": "duggasco",
2341.       "full_name": "duggasco/bc250-40cu-unlock",
2342.       "description": "Re-enable all 40 CUs on the AMD BC-250 (gfx1013 / Cyan Skillfish). Kernel patch + build script. 1.61x compute scaling verified.",
2343.       "language": "Shell",
2344.       "stars": 63,
2345.       "forks": 6,
2346.       "created_at": "2026-05-18T20:30:07Z",
2347.       "topics": [],
2348.       "license": null,
2349.       "url": "https://github.com/duggasco/bc250-40cu-unlock"
2350.     },
2351.     {
2352.       "name": "go-argus",
2353.       "owner": "kamalyes",
2354.       "full_name": "kamalyes/go-argus",
2355.       "description": "零依赖 · 高性能 Go 结构体校验器",
2356.       "language": "Go",
2357.       "stars": 63,
2358.       "forks": 0,
2359.       "created_at": "2026-05-16T00:18:31Z",
2360.       "topics": [],
2361.       "license": "Apache-2.0",
2362.       "url": "https://github.com/kamalyes/go-argus"
2363.     },
2364.     {
2365.       "name": "video-spec-builder",
2366.       "owner": "feicaiclub",
2367.       "full_name": "feicaiclub/video-spec-builder",
2368.       "description": "video-spec-builder —— 把我想做个视频逼成一份精确到秒的分镜脚本 video-spec.md,交给 HyperFrames 渲染。一条命令装到 Claude Code / Cursor / Codex:npx skills add feicaiclub/video-spec-builder",
2369.       "language": "JavaScript",
2370.       "stars": 61,
2371.       "forks": 15,
2372.       "created_at": "2026-05-16T13:10:41Z",
2373.       "topics": [],
2374.       "license": "MIT",
2375.       "url": "https://github.com/feicaiclub/video-spec-builder"
2376.     },
2377.     {
2378.       "name": "throttnux",
2379.       "owner": "frayude",
2380.       "full_name": "frayude/throttnux",
2381.       "description": "A Linux tool to limit the bandwidth of any device on your local network, no router access required.",
2382.       "language": "Python",
2383.       "stars": 60,
2384.       "forks": 20,
2385.       "created_at": "2026-05-17T15:37:29Z",
2386.       "topics": [
2387.         "arp-spoofing",
2388.         "bandiwth-monitor",
2389.         "bandwith-limiter",
2390.         "linux",
2391.         "network-tools",
2392.         "networking",
2393.         "python",
2394.         "traffic-shaping"
2395.       ],
2396.       "license": null,
2397.       "url": "https://github.com/frayude/throttnux"
2398.     },
2399.     {
2400.       "name": "AI-Text-Humanizer-Protocol",
2401.       "owner": "Pythonation",
2402.       "full_name": "Pythonation/AI-Text-Humanizer-Protocol",
2403.       "description": " موجه (Prompt) نظامي متقدم لاكتشاف وإزالة أنماط الكتابة الآلية وتحويل نصوص الذكاء الاصطناعي إلى نصوص بشرية طبيعية وواقعية.",
2404.       "language": null,
2405.       "stars": 60,
2406.       "forks": 19,
2407.       "created_at": "2026-05-18T17:22:33Z",
2408.       "topics": [],
2409.       "license": "MIT",
2410.       "url": "https://github.com/Pythonation/AI-Text-Humanizer-Protocol"
2411.     },
2412.     {
2413.       "name": "puttyalt",
2414.       "owner": "chillymasterio",
2415.       "full_name": "chillymasterio/puttyalt",
2416.       "description": "PuTTY 0.83 fork with tabs, SFTP panel, session manager, and modern UX — free & open-source",
2417.       "language": "C",
2418.       "stars": 59,
2419.       "forks": 0,
2420.       "created_at": "2026-05-15T20:53:46Z",
2421.       "topics": [],
2422.       "license": "NOASSERTION",
2423.       "url": "https://github.com/chillymasterio/puttyalt"
2424.     },
2425.     {
2426.       "name": "SherlockMaps",
2427.       "owner": "Ayyouboss0011",
2428.       "full_name": "Ayyouboss0011/SherlockMaps",
2429.       "description": "Powerful Google Maps Crawler / Scraper tool with REST API, Docker support & multi-format export",
2430.       "language": "Python",
2431.       "stars": 58,
2432.       "forks": 5,
2433.       "created_at": "2026-05-17T05:54:12Z",
2434.       "topics": [
2435.         "browser-automation",
2436.         "data-extraction",
2437.         "docker",
2438.         "google",
2439.         "google-maps",
2440.         "maps",
2441.         "maps-api",
2442.         "playwright",
2443.         "python",
2444.         "rest-api",
2445.         "scrapi",
2446.         "scraping",
2447.         "web-crawler"
2448.       ],
2449.       "license": "MIT",
2450.       "url": "https://github.com/Ayyouboss0011/SherlockMaps"
2451.     },
2452.     {
2453.       "name": "besur-themes",
2454.       "owner": "Ballwictb",
2455.       "full_name": "Ballwictb/besur-themes",
2456.       "description": "Vibrant color themes (dark, soft, light) with extended language support: JS/TS, Python, Rust, Go, PHP, SQL, XML, YAML, TOML, Markdown, Bash, and more.",
2457.       "language": "CSS",
2458.       "stars": 58,
2459.       "forks": 0,
2460.       "created_at": "2026-05-16T15:27:55Z",
2461.       "topics": [
2462.         "developer-tools",
2463.         "open-vsx",
2464.         "openvsx",
2465.         "theme",
2466.         "themes",
2467.         "vscode-extension",
2468.         "vscode-theme",
2469.         "windsurf-extension"
2470.       ],
2471.       "license": "NOASSERTION",
2472.       "url": "https://github.com/Ballwictb/besur-themes"
2473.     },
2474.     {
2475.       "name": "manga-pdf-to-epub",
2476.       "owner": "0xH4KU",
2477.       "full_name": "0xH4KU/manga-pdf-to-epub",
2478.       "description": "Lossless PDF to EPUB/CBZ tools for manga readers who care about page pairing, cover gaps, and Apple Books layout quirks.",
2479.       "language": "Python",
2480.       "stars": 58,
2481.       "forks": 0,
2482.       "created_at": "2026-05-17T08:59:59Z",
2483.       "topics": [],
2484.       "license": "MIT",
2485.       "url": "https://github.com/0xH4KU/manga-pdf-to-epub"
2486.     },
2487.     {
2488.       "name": "grok-video-workflow",
2489.       "owner": "Rion-Wu-tech",
2490.       "full_name": "Rion-Wu-tech/grok-video-workflow",
2491.       "description": "Codex workflow for Grok Imagine Video API generation, download, and frame review",
2492.       "language": "JavaScript",
2493.       "stars": 57,
2494.       "forks": 10,
2495.       "created_at": "2026-05-18T14:18:06Z",
2496.       "topics": [],
2497.       "license": "MIT",
2498.       "url": "https://github.com/Rion-Wu-tech/grok-video-workflow"
2499.     },
2500.     {
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-correlations.json.**

/home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-correlations.json (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. {
2.   "week": "2026-W21",
3.   "correlations": [
4.     {
5.       "repo": "microsoft/vscode",
6.       "press_correlated": true,
7.       "correlation_confidence": 0.8,
8.       "matched_articles": [
9.         "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/"
10.       ],
11.       "match_type": "org_name",
12.       "hype_risk": "medium"
13.     },
14.     {
15.       "repo": "microsoft/PowerToys",
16.       "press_correlated": true,
17.       "correlation_confidence": 0.8,
18.       "matched_articles": [
19.         "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/"
20.       ],
21.       "match_type": "org_name",
22.       "hype_risk": "medium"
23.     },
24.     {
25.       "repo": "microsoft/generative-ai-for-beginners",
26.       "press_correlated": true,
27.       "correlation_confidence": 0.8,
28.       "matched_articles": [
29.         "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/"
30.       ],
31.       "match_type": "org_name",
32.       "hype_risk": "medium"
33.     },
34.     {
35.       "repo": "microsoft/TypeScript",
36.       "press_correlated": true,
37.       "correlation_confidence": 0.8,
38.       "matched_articles": [
39.         "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/"
40.       ],
41.       "match_type": "org_name",
42.       "hype_risk": "medium"
43.     },
44.     {
45.       "repo": "microsoft/terminal",
46.       "press_correlated": true,
47.       "correlation_confidence": 0.8,
48.       "matched_articles": [
49.         "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/"
50.       ],
51.       "match_type": "org_name",
52.       "hype_risk": "medium"
53.     },
54.     {
55.       "repo": "microsoft/playwright",
56.       "press_correlated": true,
57.       "correlation_confidence": 0.8,
58.       "matched_articles": [
59.         "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/"
60.       ],
61.       "match_type": "org_name",
62.       "hype_risk": "medium"
63.     },
64.     {
65.       "repo": "openai/codex",
66.       "press_correlated": true,
67.       "correlation_confidence": 0.8,
68.       "matched_articles": [
69.         "https://techcrunch.com/2026/05/20/openai-claims-it-solved-an-80-year-old-math-problem-for-real-this-time/",
70.         "https://techcrunch.com/2026/05/20/openai-barrels-toward-ipo-that-may-happen-in-september/"
71.       ],
72.       "match_type": "org_name",
73.       "hype_risk": "medium"
74.     },
75.     {
76.       "repo": "microsoft/ai-agents-for-beginners",
77.       "press_correlated": true,
78.       "correlation_confidence": 0.8,
79.       "matched_articles": [
80.         "https://techcrunch.com/2026/05/20/microsofts-carbon-removal-plans-arent-dead-after-all/"
81.       ],
82.       "match_type": "org_name",
83.       "hype_risk": "medium"
84.     },
85.     {
86.       "repo": "starship/starship",
87.       "press_correlated": true,
88.       "correlation_confidence": 0.8,
89.       "matched_articles": [
90.         "https://techcrunch.com/2026/05/20/the-spacex-ipo-filing-ai-bets-starship-dreams-elon-musk/"
91.       ],
92.       "match_type": "org_name",
93.       "hype_risk": "medium"
94.     },
95.     {
96.       "repo": "AbhishekK130804/Claude-Mythos-AI-Anthropic-App",
97.       "press_correlated": true,
98.       "correlation_confidence": 0.6,
99.       "matched_articles": [
100.         "https://techcrunch.com/2026/05/20/imperagen-raises-5-million-to-redefine-enzyme-engineering/",
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 2500-2900)

<details>
<summary>401 lines</summary>

```
2500.     {
2501.       "name": "RAEv2",
2502.       "owner": "nanovisionx",
2503.       "full_name": "nanovisionx/RAEv2",
2504.       "description": "Official Implemenation for RAEv2: Improved Baselines with Representation Autoencoders",
2505.       "language": "Python",
2506.       "stars": 57,
2507.       "forks": 2,
2508.       "created_at": "2026-05-15T10:50:17Z",
2509.       "topics": [],
2510.       "license": "NOASSERTION",
2511.       "url": "https://github.com/nanovisionx/RAEv2"
2512.     },
2513.     {
2514.       "name": "papr",
2515.       "owner": "l0ng-ai",
2516.       "full_name": "l0ng-ai/papr",
2517.       "description": "A fast, native RSS reader for the desktop.",
2518.       "language": "Rust",
2519.       "stars": 57,
2520.       "forks": 5,
2521.       "created_at": "2026-05-17T14:12:46Z",
2522.       "topics": [
2523.         "desktop-app",
2524.         "feed-reader",
2525.         "react",
2526.         "rss",
2527.         "rss-reader",
2528.         "rust",
2529.         "tauri"
2530.       ],
2531.       "license": "MIT",
2532.       "url": "https://github.com/l0ng-ai/papr"
2533.     },
2534.     {
2535.       "name": "kiro-pro-batch",
2536.       "owner": "guowang23333",
2537.       "full_name": "guowang23333/kiro-pro-batch",
2538.       "description": "Kiro Pro/Pro+ 批量订阅自动化工具，支持 GitHub/Google/AWS Builder ID 登录 + Stripe 自动支付",
2539.       "language": "JavaScript",
2540.       "stars": 57,
2541.       "forks": 41,
2542.       "created_at": "2026-05-20T02:34:56Z",
2543.       "topics": [],
2544.       "license": null,
2545.       "url": "https://github.com/guowang23333/kiro-pro-batch"
2546.     },
2547.     {
2548.       "name": "filemention.nvim",
2549.       "owner": "not-manu",
2550.       "full_name": "not-manu/filemention.nvim",
2551.       "description": "@ file mentions in neovim. for prompts, notes, commits.",
2552.       "language": "Lua",
2553.       "stars": 57,
2554.       "forks": 0,
2555.       "created_at": "2026-05-15T13:12:39Z",
2556.       "topics": [
2557.         "ai",
2558.         "blink-cmp",
2559.         "claude",
2560.         "claude-code",
2561.         "completion-source",
2562.         "cursor",
2563.         "file",
2564.         "markdown",
2565.         "mention",
2566.         "neovim",
2567.         "neovim-plugin",
2568.         "nvim",
2569.         "nvim-cmp",
2570.         "prompt",
2571.         "prompts",
2572.         "vim"
2573.       ],
2574.       "license": "MIT",
2575.       "url": "https://github.com/not-manu/filemention.nvim"
2576.     },
2577.     {
2578.       "name": "remotion-ad-video-skill",
2579.       "owner": "leosssvip-dot",
2580.       "full_name": "leosssvip-dot/remotion-ad-video-skill",
2581.       "description": "Create Remotion ad video projects from a URL with an AI coding agent, no video-generation AI required.",
2582.       "language": "JavaScript",
2583.       "stars": 55,
2584.       "forks": 4,
2585.       "created_at": "2026-05-19T11:56:23Z",
2586.       "topics": [],
2587.       "license": "MIT",
2588.       "url": "https://github.com/leosssvip-dot/remotion-ad-video-skill"
2589.     },
2590.     {
2591.       "name": "RFD-Classification-Machine-Learning-Project",
2592.       "owner": "rajchandran006-ops",
2593.       "full_name": "rajchandran006-ops/RFD-Classification-Machine-Learning-Project",
2594.       "description": "RFD Classification Machine Learning project developed using Python and Jupyter Notebook. This project includes data preprocessing, exploratory data analysis, feature engineering, and implementation of multiple classification algorithms such as Logistic Regression, Random Forest, SVM, KNN, and Naive Bayes for prediction and accuracy evaluation.",
2595.       "language": "Jupyter Notebook",
2596.       "stars": 55,
2597.       "forks": 0,
2598.       "created_at": "2026-05-17T07:21:43Z",
2599.       "topics": [],
2600.       "license": "MIT",
2601.       "url": "https://github.com/rajchandran006-ops/RFD-Classification-Machine-Learning-Project"
2602.     },
2603.     {
2604.       "name": "UAV-GPS-DQN-Detection",
2605.       "owner": "zhw040803-glitch",
2606.       "full_name": "zhw040803-glitch/UAV-GPS-DQN-Detection",
2607.       "description": "基于DQN的无人机GPS欺骗攻击检测系统 | 随机攻击、重放攻击、隐蔽攻击",
2608.       "language": "Python",
2609.       "stars": 54,
2610.       "forks": 2,
2611.       "created_at": "2026-05-20T03:34:56Z",
2612.       "topics": [],
2613.       "license": null,
2614.       "url": "https://github.com/zhw040803-glitch/UAV-GPS-DQN-Detection"
2615.     },
2616.     {
2617.       "name": "git-switch",
2618.       "owner": "Avijit07x",
2619.       "full_name": "Avijit07x/git-switch",
2620.       "description": "A fast, native Git client that runs your dev servers too.",
2621.       "language": "TypeScript",
2622.       "stars": 54,
2623.       "forks": 0,
2624.       "created_at": "2026-05-16T05:21:25Z",
2625.       "topics": [
2626.         "dev-server",
2627.         "developer-tools",
2628.         "git",
2629.         "gitgui",
2630.         "macos-app",
2631.         "multirepo-maintenance",
2632.         "reactjs",
2633.         "rust",
2634.         "tauri-app",
2635.         "xterm"
2636.       ],
2637.       "license": "MIT",
2638.       "url": "https://github.com/Avijit07x/git-switch"
2639.     },
2640.     {
2641.       "name": "MultiClass-LungDisease-Detection-Using-XAI",
2642.       "owner": "Stevia-S",
2643.       "full_name": "Stevia-S/MultiClass-LungDisease-Detection-Using-XAI",
2644.       "description": "Explainable deep learning framework for multi-class lung disease detection from CT scan images using ResNet50, VGG16 feature fusion, and Grad-CAM visualization.",
2645.       "language": "Python",
2646.       "stars": 54,
2647.       "forks": 1,
2648.       "created_at": "2026-05-17T05:17:53Z",
2649.       "topics": [],
2650.       "license": null,
2651.       "url": "https://github.com/Stevia-S/MultiClass-LungDisease-Detection-Using-XAI"
2652.     },
2653.     {
2654.       "name": "diskwatch",
2655.       "owner": "matthart1983",
2656.       "full_name": "matthart1983/diskwatch",
2657.       "description": "Single-host, read-only disk diagnostics TUI. Sibling to netwatch and syswatch.",
2658.       "language": "Rust",
2659.       "stars": 53,
2660.       "forks": 1,
2661.       "created_at": "2026-05-16T03:18:53Z",
2662.       "topics": [],
2663.       "license": "MIT",
2664.       "url": "https://github.com/matthart1983/diskwatch"
2665.     },
2666.     {
2667.       "name": "Irodori-TTS-Lite",
2668.       "owner": "kizuna-intelligence",
2669.       "full_name": "kizuna-intelligence/Irodori-TTS-Lite",
2670.       "description": "Int4-quantized inference runtime for Faster-Irodori-TTS2 voice-design DiT. ~1GB VRAM end-to-end.",
2671.       "language": "Python",
2672.       "stars": 53,
2673.       "forks": 3,
2674.       "created_at": "2026-05-18T16:17:15Z",
2675.       "topics": [],
2676.       "license": "NOASSERTION",
2677.       "url": "https://github.com/kizuna-intelligence/Irodori-TTS-Lite"
2678.     },
2679.     {
2680.       "name": "handwritten-digit-recognition-cnn",
2681.       "owner": "sanjanaprasath01-hue",
2682.       "full_name": "sanjanaprasath01-hue/handwritten-digit-recognition-cnn",
2683.       "description": "A deep learning project to recognize handwritten digits using CNN",
2684.       "language": "Jupyter Notebook",
2685.       "stars": 52,
2686.       "forks": 0,
2687.       "created_at": "2026-05-16T19:12:37Z",
2688.       "topics": [],
2689.       "license": null,
2690.       "url": "https://github.com/sanjanaprasath01-hue/handwritten-digit-recognition-cnn"
2691.     },
2692.     {
2693.       "name": "Pneumonia-Detection-With-Explainable-AI",
2694.       "owner": "Yuvan-x",
2695.       "full_name": "Yuvan-x/Pneumonia-Detection-With-Explainable-AI",
2696.       "description": "AI-based medical image classifier that identifies Pneumonia from chest X-ray images through CNN along with visualization of areas with abnormalities through Grad-CAM Explainable AI",
2697.       "language": "Python",
2698.       "stars": 52,
2699.       "forks": 0,
2700.       "created_at": "2026-05-16T13:28:38Z",
2701.       "topics": [],
2702.       "license": null,
2703.       "url": "https://github.com/Yuvan-x/Pneumonia-Detection-With-Explainable-AI"
2704.     },
2705.     {
2706.       "name": "InterviewForge",
2707.       "owner": "K1XE",
2708.       "full_name": "K1XE/InterviewForge",
2709.       "description": "Local-first interview recording review reports with a Codex skill and CLI.",
2710.       "language": "Python",
2711.       "stars": 52,
2712.       "forks": 6,
2713.       "created_at": "2026-05-15T10:37:31Z",
2714.       "topics": [],
2715.       "license": "MIT",
2716.       "url": "https://github.com/K1XE/InterviewForge"
2717.     },
2718.     {
2719.       "name": "DukeX",
2720.       "owner": "MaftyManicEMU",
2721.       "full_name": "MaftyManicEMU/DukeX",
2722.       "description": "Xbox Emulation on iOS",
2723.       "language": "C",
2724.       "stars": 51,
2725.       "forks": 1,
2726.       "created_at": "2026-05-15T04:48:45Z",
2727.       "topics": [],
2728.       "license": "NOASSERTION",
2729.       "url": "https://github.com/MaftyManicEMU/DukeX"
2730.     }
2731.   ],
2732.   "trending_repos": [
2733.     {
2734.       "name": "freeCodeCamp",
2735.       "owner": "freeCodeCamp",
2736.       "full_name": "freeCodeCamp/freeCodeCamp",
2737.       "description": "freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming, and computer science for free.",
2738.       "language": "TypeScript",
2739.       "stars": 445213,
2740.       "forks": 44646,
2741.       "created_at": "2014-12-24T17:49:19Z",
2742.       "topics": [
2743.         "careers",
2744.         "certification",
2745.         "community",
2746.         "curriculum",
2747.         "d3",
2748.         "education",
2749.         "freecodecamp",
2750.         "javascript",
2751.         "learn-to-code",
2752.         "math",
2753.         "nodejs",
2754.         "nonprofits",
2755.         "programming",
2756.         "react",
2757.         "teachers"
2758.       ],
2759.       "license": "BSD-3-Clause",
2760.       "url": "https://github.com/freeCodeCamp/freeCodeCamp"
2761.     },
2762.     {
2763.       "name": "public-apis",
2764.       "owner": "public-apis",
2765.       "full_name": "public-apis/public-apis",
2766.       "description": "A collective list of free APIs",
2767.       "language": "Python",
2768.       "stars": 436214,
2769.       "forks": 47817,
2770.       "created_at": "2016-03-20T23:49:42Z",
2771.       "topics": [
2772.         "api",
2773.         "apis",
2774.         "dataset",
2775.         "development",
2776.         "free",
2777.         "list",
2778.         "lists",
2779.         "open-source",
2780.         "public",
2781.         "public-api",
2782.         "public-apis",
2783.         "resources",
2784.         "software"
2785.       ],
2786.       "license": "MIT",
2787.       "url": "https://github.com/public-apis/public-apis"
2788.     },
2789.     {
2790.       "name": "free-programming-books",
2791.       "owner": "EbookFoundation",
2792.       "full_name": "EbookFoundation/free-programming-books",
2793.       "description": ":books: Freely available programming books",
2794.       "language": "Python",
2795.       "stars": 388668,
2796.       "forks": 66329,
2797.       "created_at": "2013-10-11T06:50:37Z",
2798.       "topics": [
2799.         "books",
2800.         "education",
2801.         "hacktoberfest",
2802.         "list",
2803.         "resource"
2804.       ],
2805.       "license": "CC-BY-4.0",
2806.       "url": "https://github.com/EbookFoundation/free-programming-books"
2807.     },
2808.     {
2809.       "name": "openclaw",
2810.       "owner": "openclaw",
2811.       "full_name": "openclaw/openclaw",
2812.       "description": "Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞 ",
2813.       "language": "TypeScript",
2814.       "stars": 373636,
2815.       "forks": 77597,
2816.       "created_at": "2025-11-24T10:16:47Z",
2817.       "topics": [
2818.         "ai",
2819.         "assistant",
2820.         "crustacean",
2821.         "molty",
2822.         "openclaw",
2823.         "own-your-data",
2824.         "personal"
2825.       ],
2826.       "license": "MIT",
2827.       "url": "https://github.com/openclaw/openclaw"
2828.     },
2829.     {
2830.       "name": "developer-roadmap",
2831.       "owner": "nilbuild",
2832.       "full_name": "nilbuild/developer-roadmap",
2833.       "description": "Interactive roadmaps, guides and other educational content to help developers grow in their careers.",
2834.       "language": "TypeScript",
2835.       "stars": 355168,
2836.       "forks": 44090,
2837.       "created_at": "2017-03-15T13:45:52Z",
2838.       "topics": [
2839.         "angular-roadmap",
2840.         "backend-roadmap",
2841.         "blockchain-roadmap",
2842.         "computer-science",
2843.         "dba-roadmap",
2844.         "developer-roadmap",
2845.         "devops-roadmap",
2846.         "frontend-roadmap",
2847.         "go-roadmap",
2848.         "java-roadmap",
2849.         "javascript-roadmap",
2850.         "nodejs-roadmap",
2851.         "python-roadmap",
2852.         "qa-roadmap",
2853.         "react-roadmap",
2854.         "roadmap",
2855.         "software-architect-roadmap",
2856.         "vue-roadmap"
2857.       ],
2858.       "license": "NOASSERTION",
2859.       "url": "https://github.com/nilbuild/developer-roadmap"
2860.     },
2861.     {
2862.       "name": "awesome-python",
2863.       "owner": "vinta",
2864.       "full_name": "vinta/awesome-python",
2865.       "description": "An opinionated list of Python frameworks, libraries, tools, and resources",
2866.       "language": "Python",
2867.       "stars": 298793,
2868.       "forks": 27943,
2869.       "created_at": "2014-06-27T21:00:06Z",
2870.       "topics": [
2871.         "awesome",
2872.         "collections",
2873.         "python",
2874.         "python-frameworks",
2875.         "python-libraries",
2876.         "python-tools"
2877.       ],
2878.       "license": "NOASSERTION",
2879.       "url": "https://github.com/vinta/awesome-python"
2880.     },
2881.     {
2882.       "name": "awesome-selfhosted",
2883.       "owner": "awesome-selfhosted",
2884.       "full_name": "awesome-selfhosted/awesome-selfhosted",
2885.       "description": "A list of Free Software network services and web applications which can be hosted on your own servers",
2886.       "language": null,
2887.       "stars": 294205,
2888.       "forks": 13656,
2889.       "created_at": "2015-06-01T02:33:17Z",
2890.       "topics": [
2891.         "awesome",
2892.         "awesome-list",
2893.         "cloud",
2894.         "free-software",
2895.         "hosting",
2896.         "privacy",
2897.         "self-hosted",
2898.         "selfhosted"
2899.       ],
2900.       "license": "NOASSERTION",
```

</details>


### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-press-context.md.**

/home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-press-context.md (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. ## Press Context (TechCrunch, week of 2026-W21)
2. 12 articles published relevant to tech/open-source.
3. 
4. Notable coverage:
5. - [General Catalyst just led a $63M bet on India’s travel payments market](https://techcrunch.com/2026/05/20/indian-travel-fintech-scapia-more-than-doubles-valuation-to-over-500m-in-a-year/) [Fintech, Startups, General Catalyst, Peak XV Partners, Scapia, Z47]
6. - [Imperagen raises £5 million to use quantum physics, AI on enzyme engineering](https://techcrunch.com/2026/05/20/imperagen-raises-5-million-to-redefine-enzyme-engineering/) [Startups, Biotech & Health, Venture, biotech]
7. - [Jensen Huang says he’s found a ‘brand new’ $200B market for Nvidia](https://techcrunch.com/2026/05/20/jensen-huang-says-hes-found-a-brand-new-200b-market-for-nvidia/) [AI, Enterprise, TC, cpus, nvidia]
8. - [Clouted wants to take the guesswork out of making short videos go viral](https://techcrunch.com/2026/05/20/clouted-wants-to-take-the-guesswork-out-of-making-short-videos-go-viral/) [AI, Media & Entertainment, Startups, Clouted, Marketing, slow ventures, social media]
9. - [Nvidia posts another record quarter, reveals $43B of holdings in startups](https://techcrunch.com/2026/05/20/nvidia-posts-another-record-quarter-reveals-43-billion-of-holdings-in-startups/) [AI, earnings, Jensen Huang, nvidia]
10. - [Anthropic will pay xAI $1.25B per month for compute](https://techcrunch.com/2026/05/20/anthropic-will-pay-xai-1-25-billion-per-month-for-compute/) [AI, Anthropic, colossus, data centers, SpaceX, xAI]
11. - [Sam Altman makes ‘mic drop’ offer to every Y Combinator startup](https://techcrunch.com/2026/05/20/sam-altman-makes-mic-drop-offer-to-every-y-combinator-startup/) [Startups, Venture, OpenAI, sam altman, Y Combinator]
12. - [You don’t need to be an AI startup to raise. Lucra has $20M to prove it.](https://techcrunch.com/video/you-dont-need-to-be-an-ai-startup-to-raise-lucra-has-20m-to-prove-it/) [Startups, AI startup, ark invest, Cathie Wood, Equity podcast, Lucra, startup fundraising, venture capital]
13. - [OpenAI claims it solved an 80-year-old math problem — for real this time](https://techcrunch.com/2026/05/20/openai-claims-it-solved-an-80-year-old-math-problem-for-real-this-time/) [AI, ChatGPT, erdos problems, OpenAI, reasoning models]
14. - [IrisGo, a startup backed by Andrew Ng, looks to become the AI desktop buddy you never knew you needed](https://techcrunch.com/2026/05/20/irisgo-a-startup-backed-by-andrew-ng-looks-to-become-the-ai-desktop-buddy-you-never-knew-you-needed/) [AI, andrew ng, google brain, IrisGo]
15. - [Airbnb gets into hotels, expands AI for host onboarding and customer support](https://techcrunch.com/2026/05/20/airbnb-gets-into-hotels-expands-ai-for-host-onboarding-and-customer-support/) [Apps, Airbnb, customer support, hotel bookings]
16. - [OpenAI barrels toward IPO that may happen in September](https://techcrunch.com/2026/05/20/openai-barrels-toward-ipo-that-may-happen-in-september/) [AI, Startups, Elon Musk, In Brief, IPOs, OpenAI, sam altman]
17. 
18. ### Correlation Summary
19. 84 repos have press correlation:
20. - microsoft/vscode — match: org_name, confidence: 0.8, hype_risk: medium
21. - microsoft/PowerToys — match: org_name, confidence: 0.8, hype_risk: medium
22. - microsoft/generative-ai-for-beginners — match: org_name, confidence: 0.8, hype_risk: medium
23. - microsoft/TypeScript — match: org_name, confidence: 0.8, hype_risk: medium
24. - microsoft/terminal — match: org_name, confidence: 0.8, hype_risk: medium
25. - microsoft/playwright — match: org_name, confidence: 0.8, hype_risk: medium
26. - openai/codex — match: org_name, confidence: 0.8, hype_risk: medium
27. - microsoft/ai-agents-for-beginners — match: org_name, confidence: 0.8, hype_risk: medium
28. - starship/starship — match: org_name, confidence: 0.8, hype_risk: medium
29. - AbhishekK130804/Claude-Mythos-AI-Anthropic-App — match: project_name, confidence: 0.6, hype_risk: medium
30. - suyancc/openai-plus-vxt — match: project_name, confidence: 0.6, hype_risk: medium
31. - ip-arch/NESLab — match: project_name, confidence: 0.6, hype_risk: medium
32. - deepakness/google-ai-search-optimization — match: project_name, confidence: 0.6, hype_risk: medium
33. - aqua5230/usage — match: project_name, confidence: 0.6, hype_risk: medium
34. - OpenYSMDev/OpenYSM — match: project_name, confidence: 0.6, hype_risk: medium
35. - wanshuiyin/ARIS-in-AI-Offer — match: project_name, confidence: 0.6, hype_risk: medium
36. - Pythonation/AI-Text-Humanizer-Protocol — match: project_name, confidence: 0.6, hype_risk: medium
37. - Yuvan-x/Pneumonia-Detection-With-Explainable-AI — match: project_name, confidence: 0.6, hype_risk: medium
38. - openclaw/openclaw — match: project_name, confidence: 0.6, hype_risk: medium
39. - open-webui/open-webui — match: project_name, confidence: 0.6, hype_risk: medium
40. - x1xhlol/system-prompts-and-models-of-ai-tools — match: project_name, confidence: 0.6, hype_risk: medium
41. - electron/electron — match: project_name, confidence: 0.6, hype_risk: medium
42. - nodejs/node — match: project_name, confidence: 0.6, hype_risk: medium
43. - rust-lang/rust — match: project_name, confidence: 0.6, hype_risk: medium
44. - tauri-apps/tauri — match: project_name, confidence: 0.6, hype_risk: medium
45. - gohugoio/hugo — match: project_name, confidence: 0.6, hype_risk: medium
46. - opencv/opencv — match: project_name, confidence: 0.6, hype_risk: medium
47. - OpenHands/OpenHands — match: project_name, confidence: 0.6, hype_risk: medium
48. - base/node — match: project_name, confidence: 0.6, hype_risk: medium
49. - OpenBB-finance/OpenBB — match: project_name, confidence: 0.6, hype_risk: medium
50. - JuliusBrussee/caveman — match: project_name, confidence: 0.6, hype_risk: medium
51. - commaai/openpilot — match: project_name, confidence: 0.6, hype_risk: medium
52. - virattt/ai-hedge-fund — match: project_name, confidence: 0.6, hype_risk: medium
53. - rclone/rclone — match: project_name, confidence: 0.6, hype_risk: medium
54. - go-gitea/gitea — match: project_name, confidence: 0.6, hype_risk: medium
55. - typst/typst — match: project_name, confidence: 0.6, hype_risk: medium
56. - DenisSergeevitch/agents-best-practices — match: category, confidence: 0.4, hype_risk: low
57. - LiuMengxuan04/shushu-internship-tool — match: category, confidence: 0.4, hype_risk: low
58. - agent-quality-controls/slopless — match: category, confidence: 0.4, hype_risk: low
59. - Klotzkette/claude-fuer-deutsches-recht — match: category, confidence: 0.4, hype_risk: low
60. - basionwang-bot/HermesPet — match: category, confidence: 0.4, hype_risk: low
61. - gazelleandrewrasmussenmouj2/Windows-Activator — match: category, confidence: 0.4, hype_risk: low
62. - jigripokri/POHA — match: category, confidence: 0.4, hype_risk: low
63. - Helvesec/rmux — match: category, confidence: 0.4, hype_risk: low
64. - JSingletonAI/dejavu — match: category, confidence: 0.4, hype_risk: low
65. - joeseesun/qiaomu-userscripts — match: category, confidence: 0.4, hype_risk: low
66. - not-manu/filemention.nvim — match: category, confidence: 0.4, hype_risk: low
67. - n8n-io/n8n — match: category, confidence: 0.4, hype_risk: low
68. - affaan-m/ECC — match: category, confidence: 0.4, hype_risk: low
69. - Significant-Gravitas/AutoGPT — match: category, confidence: 0.4, hype_risk: low
70. - f/prompts.chat — match: category, confidence: 0.4, hype_risk: low
71. - NousResearch/hermes-agent — match: category, confidence: 0.4, hype_risk: low
72. - langflow-ai/langflow — match: category, confidence: 0.4, hype_risk: low
73. - langgenius/dify — match: category, confidence: 0.4, hype_risk: low
74. - langchain-ai/langchain — match: category, confidence: 0.4, hype_risk: low
75. - firecrawl/firecrawl — match: category, confidence: 0.4, hype_risk: low
76. - Comfy-Org/ComfyUI — match: category, confidence: 0.4, hype_risk: low
77. - jaywcjlove/awesome-mac — match: category, confidence: 0.4, hype_risk: low
78. - google-gemini/gemini-cli — match: category, confidence: 0.4, hype_risk: low
79. - github/spec-kit — match: category, confidence: 0.4, hype_risk: low
80. - hacksider/Deep-Live-Cam — match: category, confidence: 0.4, hype_risk: low
81. - ChatGPTNextWeb/NextChat — match: category, confidence: 0.4, hype_risk: low
82. - infiniflow/ragflow — match: category, confidence: 0.4, hype_risk: low
83. - vllm-project/vllm — match: category, confidence: 0.4, hype_risk: low
84. - netdata/netdata — match: category, confidence: 0.4, hype_risk: low
85. - lobehub/lobehub — match: category, confidence: 0.4, hype_risk: low
86. - thedotmack/claude-mem — match: category, confidence: 0.4, hype_risk: low
87. - daytonaio/daytona — match: category, confidence: 0.4, hype_risk: low
88. - hiyouga/LlamaFactory — match: category, confidence: 0.4, hype_risk: low
89. - bytedance/deer-flow — match: category, confidence: 0.4, hype_risk: low
90. - xtekky/gpt4free — match: category, confidence: 0.4, hype_risk: low
91. - unslothai/unsloth — match: category, confidence: 0.4, hype_risk: low
92. - openinterpreter/open-interpreter — match: category, confidence: 0.4, hype_risk: low
93. - ComposioHQ/awesome-claude-skills — match: category, confidence: 0.4, hype_risk: low
94. - docling-project/docling — match: category, confidence: 0.4, hype_risk: low
95. - code-yeongyu/oh-my-openagent — match: category, confidence: 0.4, hype_risk: low
96. - meilisearch/meilisearch — match: category, confidence: 0.4, hype_risk: low
97. - harry0703/MoneyPrinterTurbo — match: category, confidence: 0.4, hype_risk: low
98. - mem0ai/mem0 — match: category, confidence: 0.4, hype_risk: low
99. - koala73/worldmonitor — match: category, confidence: 0.4, hype_risk: low
100. - FlowiseAI/Flowise — match: category, confidence: 0.4, hype_risk: low
```

</details>


### 💬 Copilot

Now I have enough data to write the analysis. Let me look at a few more trending repos before writing:

### ✅ `view`

**view the file at /home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json.**

/home/runner/work/SquadScope/SquadScope/data/raw/2026-W21.json (lines 2900-3200)

<details>
<summary>301 lines</summary>

```
2900.       "license": "NOASSERTION",
2901.       "url": "https://github.com/awesome-selfhosted/awesome-selfhosted"
2902.     },
2903.     {
2904.       "name": "react",
2905.       "owner": "facebook",
2906.       "full_name": "facebook/react",
2907.       "description": "The library for web and native user interfaces.",
2908.       "language": "JavaScript",
2909.       "stars": 245154,
2910.       "forks": 51092,
2911.       "created_at": "2013-05-24T16:15:54Z",
2912.       "topics": [
2913.         "declarative",
2914.         "frontend",
2915.         "javascript",
2916.         "library",
2917.         "react",
2918.         "ui"
2919.       ],
2920.       "license": "MIT",
2921.       "url": "https://github.com/facebook/react"
2922.     },
2923.     {
2924.       "name": "linux",
2925.       "owner": "torvalds",
2926.       "full_name": "torvalds/linux",
2927.       "description": "Linux kernel source tree",
2928.       "language": "C",
2929.       "stars": 233918,
2930.       "forks": 62416,
2931.       "created_at": "2011-09-04T22:48:12Z",
2932.       "topics": [],
2933.       "license": "NOASSERTION",
2934.       "url": "https://github.com/torvalds/linux"
2935.     },
2936.     {
2937.       "name": "Python",
2938.       "owner": "TheAlgorithms",
2939.       "full_name": "TheAlgorithms/Python",
2940.       "description": "All Algorithms implemented in Python",
2941.       "language": "Python",
2942.       "stars": 221272,
2943.       "forks": 50661,
2944.       "created_at": "2016-07-16T09:44:01Z",
2945.       "topics": [
2946.         "algorithm",
2947.         "algorithm-competitions",
2948.         "algorithms-implemented",
2949.         "algos",
2950.         "community-driven",
2951.         "education",
2952.         "hacktoberfest",
2953.         "interview",
2954.         "learn",
2955.         "practice",
2956.         "python",
2957.         "searches",
2958.         "sorting-algorithms",
2959.         "sorts"
2960.       ],
2961.       "license": "MIT",
2962.       "url": "https://github.com/TheAlgorithms/Python"
2963.     },
2964.     {
2965.       "name": "javascript-algorithms",
2966.       "owner": "trekhleb",
2967.       "full_name": "trekhleb/javascript-algorithms",
2968.       "description": "📝 Algorithms and data structures implemented in JavaScript with explanations and links to further readings",
2969.       "language": "JavaScript",
2970.       "stars": 195980,
2971.       "forks": 31064,
2972.       "created_at": "2018-03-24T07:47:04Z",
2973.       "topics": [
2974.         "algorithm",
2975.         "algorithms",
2976.         "computer-science",
2977.         "data-structures",
2978.         "interview",
2979.         "interview-preparation",
2980.         "javascript",
2981.         "javascript-algorithms"
2982.       ],
2983.       "license": "MIT",
2984.       "url": "https://github.com/trekhleb/javascript-algorithms"
2985.     },
2986.     {
2987.       "name": "tensorflow",
2988.       "owner": "tensorflow",
2989.       "full_name": "tensorflow/tensorflow",
2990.       "description": "An Open Source Machine Learning Framework for Everyone",
2991.       "language": "C++",
2992.       "stars": 195211,
2993.       "forks": 75312,
2994.       "created_at": "2015-11-07T01:19:20Z",
2995.       "topics": [
2996.         "deep-learning",
2997.         "deep-neural-networks",
2998.         "distributed",
2999.         "machine-learning",
3000.         "ml",
3001.         "neural-network",
3002.         "python",
3003.         "tensorflow"
3004.       ],
3005.       "license": "Apache-2.0",
3006.       "url": "https://github.com/tensorflow/tensorflow"
3007.     },
3008.     {
3009.       "name": "claw-code",
3010.       "owner": "ultraworkers",
3011.       "full_name": "ultraworkers/claw-code",
3012.       "description": "The repo is finally unlocked. enjoy the party! The fastest repo in history to surpass 100K stars ⭐. Join Discord: https://discord.gg/5TUQKqFWd Built in Rust using oh-my-codex.",
3013.       "language": "Rust",
3014.       "stars": 192126,
3015.       "forks": 109954,
3016.       "created_at": "2026-03-31T08:58:08Z",
3017.       "topics": [],
3018.       "license": "MIT",
3019.       "url": "https://github.com/ultraworkers/claw-code"
3020.     },
3021.     {
3022.       "name": "n8n",
3023.       "owner": "n8n-io",
3024.       "full_name": "n8n-io/n8n",
3025.       "description": "Fair-code workflow automation platform with native AI capabilities. Combine visual building with custom code, self-host or cloud, 400+ integrations.",
3026.       "language": "TypeScript",
3027.       "stars": 188950,
3028.       "forks": 57865,
3029.       "created_at": "2019-06-22T09:24:21Z",
3030.       "topics": [
3031.         "ai",
3032.         "apis",
3033.         "automation",
3034.         "cli",
3035.         "data-flow",
3036.         "development",
3037.         "integration-framework",
3038.         "integrations",
3039.         "ipaas",
3040.         "low-code",
3041.         "low-code-platform",
3042.         "mcp",
3043.         "mcp-client",
3044.         "mcp-server",
3045.         "n8n",
3046.         "no-code",
3047.         "self-hosted",
3048.         "typescript",
3049.         "workflow",
3050.         "workflow-automation"
3051.       ],
3052.       "license": "NOASSERTION",
3053.       "url": "https://github.com/n8n-io/n8n"
3054.     },
3055.     {
3056.       "name": "ECC",
3057.       "owner": "affaan-m",
3058.       "full_name": "affaan-m/ECC",
3059.       "description": "The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond.",
3060.       "language": "JavaScript",
3061.       "stars": 187899,
3062.       "forks": 29079,
3063.       "created_at": "2026-01-18T00:51:51Z",
3064.       "topics": [
3065.         "ai-agents",
3066.         "anthropic",
3067.         "claude",
3068.         "claude-code",
3069.         "developer-tools",
3070.         "llm",
3071.         "mcp",
3072.         "productivity"
3073.       ],
3074.       "license": "MIT",
3075.       "url": "https://github.com/affaan-m/ECC"
3076.     },
3077.     {
3078.       "name": "ohmyzsh",
3079.       "owner": "ohmyzsh",
3080.       "full_name": "ohmyzsh/ohmyzsh",
3081.       "description": "🙃   A delightful community-driven (with 2,500+ contributors) framework for managing your zsh configuration. Includes 300+ optional plugins (rails, git, macOS, hub, docker, homebrew, node, php, python, etc), 140+ themes to spice up your morning, and an auto-update tool that makes it easy to keep up with the latest updates from the community.",
3082.       "language": "Shell",
3083.       "stars": 187156,
3084.       "forks": 26374,
3085.       "created_at": "2009-08-28T18:15:37Z",
3086.       "topics": [
3087.         "cli",
3088.         "cli-app",
3089.         "oh-my-zsh",
3090.         "oh-my-zsh-plugin",
3091.         "oh-my-zsh-theme",
3092.         "ohmyzsh",
3093.         "plugin-framework",
3094.         "plugins",
3095.         "productivity",
3096.         "shell",
3097.         "terminal",
3098.         "theme",
3099.         "themes",
3100.         "zsh",
3101.         "zsh-configuration"
3102.       ],
3103.       "license": "MIT",
3104.       "url": "https://github.com/ohmyzsh/ohmyzsh"
3105.     },
3106.     {
3107.       "name": "vscode",
3108.       "owner": "microsoft",
3109.       "full_name": "microsoft/vscode",
3110.       "description": "Visual Studio Code",
3111.       "language": "TypeScript",
3112.       "stars": 185161,
3113.       "forks": 40020,
3114.       "created_at": "2015-09-03T20:23:38Z",
3115.       "topics": [
3116.         "editor",
3117.         "electron",
3118.         "microsoft",
3119.         "typescript",
3120.         "visual-studio-code"
3121.       ],
3122.       "license": "MIT",
3123.       "url": "https://github.com/microsoft/vscode"
3124.     },
3125.     {
3126.       "name": "AutoGPT",
3127.       "owner": "Significant-Gravitas",
3128.       "full_name": "Significant-Gravitas/AutoGPT",
3129.       "description": "AutoGPT is the vision of accessible AI for everyone, to use and to build on. Our mission is to provide the tools, so that you can focus on what matters.",
3130.       "language": "Python",
3131.       "stars": 184441,
3132.       "forks": 46226,
3133.       "created_at": "2023-03-16T09:21:07Z",
3134.       "topics": [
3135.         "agentic-ai",
3136.         "agents",
3137.         "ai",
3138.         "artificial-intelligence",
3139.         "autonomous-agents",
3140.         "claude",
3141.         "gpt",
3142.         "llama-api",
3143.         "llm",
3144.         "openai",
3145.         "python"
3146.       ],
3147.       "license": "NOASSERTION",
3148.       "url": "https://github.com/Significant-Gravitas/AutoGPT"
3149.     },
3150.     {
3151.       "name": "flutter",
3152.       "owner": "flutter",
3153.       "full_name": "flutter/flutter",
3154.       "description": "Flutter makes it easy and fast to build beautiful apps for mobile and beyond",
3155.       "language": "Dart",
3156.       "stars": 176405,
3157.       "forks": 30387,
3158.       "created_at": "2015-03-06T22:54:58Z",
3159.       "topics": [
3160.         "android",
3161.         "app-framework",
3162.         "cross-platform",
3163.         "dart",
3164.         "dart-platform",
3165.         "desktop",
3166.         "flutter",
3167.         "flutter-package",
3168.         "fuchsia",
3169.         "ios",
3170.         "linux-desktop",
3171.         "macos",
3172.         "material-design",
3173.         "mobile",
3174.         "mobile-development",
3175.         "skia",
3176.         "web",
3177.         "web-framework",
3178.         "windows"
3179.       ],
3180.       "license": "BSD-3-Clause",
3181.       "url": "https://github.com/flutter/flutter"
3182.     },
3183.     {
3184.       "name": "bootstrap",
3185.       "owner": "twbs",
3186.       "full_name": "twbs/bootstrap",
3187.       "description": "The most popular HTML, CSS, and JavaScript framework for developing responsive, mobile first projects on the web.",
3188.       "language": "MDX",
3189.       "stars": 174262,
3190.       "forks": 78877,
3191.       "created_at": "2011-07-29T21:19:00Z",
3192.       "topics": [
3193.         "bootstrap",
3194.         "css",
3195.         "css-framework",
3196.         "html",
3197.         "javascript",
3198.         "sass",
3199.         "scss"
3200.       ],
```

</details>


### 💬 Copilot

I now have a complete picture of the data. The existing file has the wrong section structure (doesn't conform to the spec). I'll replace it entirely with the correct analysis.

### ✅ `edit`

**edit the file at /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md.**

/home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md

```
File /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W21-summary.md updated with changes.
```


### 💬 Copilot

Now update the history file with learnings:

### ✅ `edit`

**edit the file at /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md.**

/home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md

```
File /home/runner/work/SquadScope/SquadScope/.squad/agents/farnsworth/history.md updated with changes.
```


### 💬 Copilot

Now verify the output file is well-formed:

### ✅ `bash`

**Verify section structure of output file**

$ wc -l data/analyzed/2026-W21-summary.md && grep "^## " data/analyzed/2026-W21-summary.md && grep "^### " data/analyzed/2026-W21-summary.md

<details>
<summary>10 lines</summary>

```
76 data/analyzed/2026-W21-summary.md
## This Week's Trends
## Where Industry Meets Code
## Signal & Noise
## Blind Spots
## The Week Ahead
## Key References
### Notable Projects
### Press & Industry
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Verify frontmatter**

$ head -15 data/analyzed/2026-W21-summary.md

<details>
<summary>15 lines</summary>

```
---
title: "Week 21, 2026 Analysis"
date: 2026-05-21T08:39:29Z
week: "2026-W21"
year: 2026
tags: [ai, agents, agent-skills, developer-tooling, small-models, code-automation, llm, noise]
categories: [weekly]
repos_featured: 424
stars_tracked: 20204141
top_repo: "vercel-labs/zerolang"
quality_score: 72
summary: "The agent skill format is hardening into a real packaging pattern — but Week 21 is also the noisiest crawl on record, with game cheats, Windows activators, and fake trading bots inflating star counts and making momentum nearly impossible to read cleanly."
---

## This Week's Trends
<exited with exit code 0>
```

</details>


### 💬 Copilot

The output is clean and spec-conforming. Here's a summary of what was produced:

---

## `data/analyzed/2026-W21-summary.md` — Done

The previous draft had the wrong section structure (spec non-conforming headers). I replaced it completely with a full spec-compliant analysis.

### What the analysis found

**Five editorial trends:**

1. **Agent skill packaging** — `claude-code` (17 topic hits), `mcp` (15), and a cross-domain cohort of skill repos (Android testing, CUDA, distributed systems, German law, technical writing) signal that reusable agent skills are becoming a real distribution format, not just a naming convention.

2. **Infrastructure for agents** — [vercel-labs/zerolang](https://github.com/vercel-labs/zerolang) (4,076 stars, written in C) positions itself as a programming language for agents, backed by the trending [affaan-m/ECC](https://github.com/affaan-m/ECC) (188k stars) at the harness layer.

3. **Small LLM operationalization** — [Doorman11991/smallcode](https://github.com/Doorman11991/smallcode) (87% benchmark at 4B), [sapientinc/HRM-Text](https://github.com/sapientinc/HRM-Text), and [bytedance/Lance](https://github.com/bytedance/Lance) cluster around the argument that capable models are moving below the hyperscaler threshold.

4. **Automated code quality tooling** — [openclaw/clawpatch](https://github.com/openclaw/clawpatch), [agent-quality-controls/slopless](https://github.com/agent-quality-controls/slopless), and [evilsocket/audit](https://github.com/evilsocket/audit) converge independently on programmatic enforcement.

5. **Noise at unprecedented scale** — Game cheats, Windows activators, Roblox executors, and trading-bot spam clusters with 2,000–4,500 fake forks distort the star distribution. `hacktoberfest` appearing 24 times in May is a topic-stuffing tell. All trending repos lack `stars_gained`, so momentum is unverifiable.

**Press/code gap:** Industry press focused on Nvidia's $200B agent CPU claim, Anthropic/xAI compute deal, and OpenAI IPO. None of those narratives have developer-side counterparts in the crawl. The divergence is the story.

**Three learnings** appended to history: the coordinated noise pattern, the `stars_gained`-missing caveat rule, and the agent-skill-packaging pattern as a candidate for a new `.squad/skills/` entry.


---

<sub>⏱️ 7m 36s</sub>

### 💬 Copilot

✅ Done. The analysis is written to `data/analyzed/2026-W21-summary.md`.

**W21 in brief:** Five editorial trends — agent skill packaging, infrastructure for agents (including a C-based agentic programming language), small LLM operationalization below the hyperscaler threshold, automated code quality tooling, and a significant noise problem (game cheats, fake forks, topic stuffing). Notable press/code gap: the Nvidia $200B agent CPU and OpenAI IPO narratives have no developer-side counterparts in the crawl.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
