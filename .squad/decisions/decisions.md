# SquadScope Decisions

## 2026-05-18: Hugo Frontend with PaperMod Theme (Issue #3)

- **Owner:** Amy
- **Date:** 2026-05-18T10:27:35Z
- **Decision:** Use Hugo with the PaperMod theme as the baseline frontend for the MVP.
- **Why:** PaperMod gives the project responsive blog-style layouts, taxonomies, RSS, and built-in search support without adding a Node-based frontend toolchain.
- **Paths:** `hugo.toml`, `content/`, `data/`, `.github/workflows/deploy-site.yml`, `themes/PaperMod`

## 2026-05-18: Hugo Built-in RSS Path (Issue #4)

- **Owner:** Amy
- **Date:** 2026-05-18T10:27:35Z
- **Decision:** Keep SquadScope on Hugo's built-in RSS output path (`/index.xml`) rather than adding a custom `feed.xml` alias for the MVP. Build navigation, archive chronology, and weekly report presentation through Hugo layouts so generated markdown remains the primary source of truth.
- **Why:** Generator and deployment work can target Hugo defaults. Future notification or feed alias work can stay optional.

## 2026-05-18: Stdlib-Only Python Crawler (Issue #5)

- **Owner:** Bender
- **Date:** 2026-05-18T10:27:35Z
- **Decision:** Use a stdlib-only Python crawler (`urllib`) that writes `data/raw/YYYY-WNN.json`, computes trending rank from the latest prior raw snapshot when available, and defaults to fetching the top 250 search results per query while still supporting pagination up to GitHub's 1,000-result search limit via `--max-results`.
- **Why:**
  - Keeps CI setup minimal (`requirements.txt` can stay dependency-free)
  - Makes weekly crawls deterministic and cheap enough for local and Actions runs
  - Preserves a path to deeper crawls without changing the data contract
- **Notes:**
  - Search endpoints: `created:>{date} stars:>50` and `pushed:>{date} stars:>50`
  - Significance filter excludes forks, repos without descriptions, repos without READMEs, and obvious tutorial/homework/template repos
  - Repos with org SAML-blocked README endpoints are skipped instead of failing the crawl

## 2026-05-18: Branch → PR → Review → Merge Workflow

- **Owner:** jmservera (Copilot directive)
- **Date:** 2026-05-18T10:59:10Z
- **Decision:** Follow the typical branch → PR → Review → Merge process for each issue. Do NOT commit directly to main.
- **Why:** For clean and understandable GitHub history. Each issue should get its own branch, a PR, review, then merge.
- **Scope:** Affects all future agent spawns.

## 2026-05-18: Copilot Reviews on PRs

- **Owner:** jmservera (Copilot directive)
- **Date:** 2026-05-18T12:07:20Z
- **Decision:** Copilot reviews are activated on PRs. All review conversations must be resolved before merging.
- **Why:** User request — captured for team memory. Ensures quality and completeness of code review before merge.
- **Scope:** All PR workflows must check for and resolve Copilot review comments before merging.

## 2026-05-18: Crawler Hardening with Filters, Caching, and Rate Limits (Issue #6)

- **Owner:** Bender
- **Date:** 2026-05-18T10:59:10Z
- **Decision:** Treat README lookups as a degradable signal instead of a hard-stop path. The crawler now caches API responses, saves weekly star snapshots under `data/snapshots/`, logs rate-limit state, and caps README retry delays so partial failures are recorded in metadata instead of blocking the full weekly crawl.
- **Why:** Search queries are cheap, but hundreds of README checks can trigger secondary throttling. Bounded retries plus persistent cache keep Phase 1 crawls finishable and give Farnsworth usable JSON even when GitHub responses are partial.
- **Implementation:** PR #26 merged with all Copilot review comments addressed (commit 779f9ef).

## 2026-05-18: Hugo Version Pinning and Dry-Run Validation (Issue #7)

- **Owner:** Fry
- **Date:** 2026-05-18T10:59:10Z
- **Decision:** Pin Hugo version across all validation runs and infrastructure.
- **Key findings:**
  1. Local environment defaulted to `hugo v0.123.7`, but repository theme requires `v0.146.0+`. Dry-run validation only succeeded with `hugo v0.161.1`.
  2. Trending requires historical state; `data/raw/2026-W21.json` contains no usable `stars_gained` values in `trending_repos`, so current output is popularity-biased rather than momentum-based.
  3. Crawler filtering still lets through off-mission content (exploits, bypasses, cheats, game-mods). Needs stronger filtering or quality gate before auto-publish.
  4. Analyze/generate contract needs final alignment. PRD weekly page shape and approved analyzer quality-gate contract are close but not identical.

## 2026-05-18: Analyzed Artifact Schema Alignment (PR #25 Follow-up)

- **Owner:** Leela
- **Date:** 2026-05-18T10:59:10Z
- **Issue:** `data/analyzed/2026-W21-summary.md` is stored in the analyzer contract path but does not follow the approved Analyze → Generate section contract (`Signal`, `Noise`, `Gaps`).
- **Required follow-up:** Either align the analyzed artifact to the approved contract or move the manual validation artifact out of `data/analyzed/` so the repository does not adopt the wrong schema by accident.
- **Status:** Identified in PR #25 review (now merged) — Phase 2 action item.

## 2026-05-19: TechCrunch RSS as Enrichment Signal (PR #55)

- **Owner:** Bender
- **Date:** 2026-05-19
- **Decision:** TechCrunch RSS integration is an enrichment signal (not primary source) with explicit low-expectation framing (5–15% correlation hit rate). Feature degrades to zero noise when no correlations found.
- **Why:** Correlation between press articles and repos is inherently low. Value lies in the delta (hype vs traction), not article summarization. Enrichment positioning allows silent failure without degrading digest.
- **Implications:** All future `DataSource` plugins must declare "primary" or "enrichment" status. Enrichment sources require explicit failure/removal criteria. Farnsworth's analysis treats correlation data as optional context, never required input.

## 2026-05-19: Milestone-based workflow adopted

- **Owner:** jmservera (via Copilot)
- **Date:** 2026-05-19
- **Decision:** All future work organized into versioned milestones (v0.5, v0.6, etc.). PRDs are decomposed into issues, assigned to milestones, then moved to docs/processed/. This enables progress tracking and versioning.
- **Why:** User directive — makes work easier to follow and enables versioning.

## 2026-05-19: Press Context Dual-Mode Rendering

- **Owner:** Farnsworth
- **Date:** 2026-05-19T20:50:22+02:00
- **Status:** Implemented
- **Decision:** Implement dual-mode rendering in `render_press_context.py` to serve AI prompts (full data + instructions) and reader-facing fallback (clean narrative) separately via `reader_mode` parameter and post-processing.
- **Why:** The press context serves two audiences. AI prompts need full data and model instructions; reader-facing pages should not expose AI directives or 100+ repo lists.
- **Changes:**
  - `render_press_context(reader_mode=False)` — new kwarg. When True, limits correlations to top 10, strips `### Instructions` block, and passes reader_mode to `format_divergences()`
  - `format_correlations_list(top_n=None)` — new kwarg. Truncates display and appends "…and N more repos"
  - `format_divergences(reader_mode=False)` — new kwarg. Replaces instruction bullets with reader-friendly narrative
  - `analyze_fallback._strip_ai_instructions(content)` — new helper. Applied in no-AI path to post-process rendered content
- **Consequences:** AI prompt path unchanged (full instructions + list continue to model); no-AI fallback now produces clean reader output. 16 new tests cover truncation, sorting, instruction stripping, narrative injection. All 498 tests passing. PR #135 merged.
