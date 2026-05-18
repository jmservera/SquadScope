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
