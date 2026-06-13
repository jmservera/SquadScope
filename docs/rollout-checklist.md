# SquadScope Rollout Checklist

Use this checklist to verify your SquadScope instance is ready for production. Complete each item before considering the system operational.

## Pre-Launch

- [ ] **Repository created**
  - [ ] GitHub repository exists and is accessible
  - [ ] Submodules initialized: `git submodule update --init --recursive`
  - [ ] Hugo version verified: `hugo version` (must be v0.161.1 to match CI)

- [ ] **Copilot auth configured**
  - [ ] Fine-grained PAT created with **Account → Copilot Requests** permission
  - [ ] Token is `github_pat_...` (not `ghp_...`)
  - [ ] Secret `COPILOT_GH_TOKEN` set in repo: `gh secret set COPILOT_GH_TOKEN --body TOKEN -R OWNER/REPO`
  - [ ] Secret verified: `gh secret list -R OWNER/REPO` shows `COPILOT_GH_TOKEN`
  - [ ] (Optional) Copilot subscription verified at https://github.com/settings/copilot

- [ ] **GitHub Pages enabled**
  - [ ] Repo **Settings → Pages → Source** set to "GitHub Actions"
  - [ ] No errors in Pages deployment section

## First-Time Testing

- [ ] **Local build succeeds**
  - [ ] Run `hugo server` locally and verify site loads at http://localhost:1313
  - [ ] No Hugo build errors in console
  - [ ] Run `hugo --minify` and verify `public/` directory created with HTML files
  - [ ] Run `npx pagefind --site public/` and verify `public/pagefind/pagefind-ui.js` exists

- [ ] **First manual crawl successful**
  - [ ] Trigger: `gh workflow run crawl-and-publish.yml -R OWNER/REPO`
  - [ ] Monitor: `gh run list -R OWNER/REPO --workflow crawl-and-publish.yml`
  - [ ] Verify: Green checkmark in Actions tab
  - [ ] Artifacts created: `data/raw/YYYY-WNN.json` and `data/snapshots/YYYY-WNN-stars.json`

- [ ] **First manual analysis successful**
  - [ ] Previous crawl completed
  - [ ] Verify: `data/analyzed/YYYY-WNN-summary.md` exists and contains valid Markdown + YAML
  - [ ] Check: YAML frontmatter includes `quality_score`, `title`, `date`, `categories`
  - [ ] Check: File contains `## This Week's Trends`, `## Where Industry Meets Code`, `## Signal & Noise`, `## Blind Spots`, `## The Week Ahead`, `## Key References`

- [ ] **Quality gate passed**
  - [ ] Analysis quality_score ≥ 60 (check frontmatter)
  - [ ] Gate did NOT block publish (workflow continued to deploy step)
  - [ ] Content sections present and not empty

- [ ] **Site deploys correctly**
  - [ ] Wait for full workflow to complete (crawl + analyze + generate + deploy)
  - [ ] Monitor: **Actions → Crawl and Publish → Latest run → Deploy Pages** shows success
  - [ ] Verify: GitHub Pages shows "Deployment successful"
  - [ ] Verify: deployed search still works and the build includes fresh `pagefind/` assets

- [ ] **RSS feed accessible**
  - [ ] Visit: `https://PAGES_URL/index.xml` (replace with your Pages domain)
  - [ ] Verify: Valid XML returned (not 404 or error)
  - [ ] Verify: Latest week's summary appears in feed items

- [ ] **Content visible on site**
  - [ ] Visit: `https://PAGES_URL/` (your GitHub Pages site)
  - [ ] Verify: Site loads without errors
  - [ ] Verify: Latest week appears in post list
  - [ ] Click into latest week's article and verify content renders correctly

## Pre-Production

- [ ] **Cron schedule enabled**
  - [ ] Verify workflow file: `.github/workflows/crawl-and-publish.yml` has schedule trigger:
    ```yaml
    schedule:
      - cron: '53 6 * * 1'  # Monday 06:53 UTC
    ```
  - [ ] Confirm schedule is correct for your timezone

- [ ] **Run counter initialized**
  - [ ] File exists: `.squad/run-counter.txt`
  - [ ] Contains integer counter (e.g., `1`)
  - [ ] Reskill only triggers on positive multiples of 5 (`5`, `10`, `15`, ...), not when the counter is `0`

## First Automated Run

- [ ] **Automated run completed (wait until next Monday 06:53 UTC or manual trigger)**
  - [ ] Check Actions tab at scheduled time
  - [ ] Verify workflow completed with green checkmark
  - [ ] Monitor logs for any warnings or errors

- [ ] **Data artifacts generated**
  - [ ] `data/raw/YYYY-WNN.json` created (current week)
  - [ ] `data/analyzed/YYYY-WNN-summary.md` created
  - [ ] `content/weekly/YYYY/WNN.md` created

- [ ] **Pages deployment succeeded**
  - [ ] Pages Shows "Deployment successful" in deployment history
  - [ ] Site updated with new week's content

- [ ] **RSS feed updated**
  - [ ] `https://PAGES_URL/index.xml` now shows the latest entry
  - [ ] Feed readers can subscribe and receive new entries

## Post-Launch Monitoring

- [ ] **Weekly runs continue automatically**
  - [ ] Check Actions every Monday morning to confirm workflow ran
  - [ ] (Optional) Set a calendar reminder to check on Mondays

- [ ] **Quality remains consistent**
  - [ ] Review a few published analyses for quality
  - [ ] If quality degrades, check workflow logs and Copilot API status

- [ ] **Site remains accessible**
  - [ ] Periodically visit your SquadScope site
  - [ ] Verify RSS feed is updated each week

## Optional Verification

- [ ] **Manual stage execution (debug only)**
  - [ ] Crawl: `python3 scripts/crawl.py --as-of 2026-05-18`
  - [ ] Analyze (local debug only — not a production fallback): `python3 scripts/analyze_fallback.py --raw-json data/raw/YYYY-WNN.json --output ./scratch-analysis.md --current-datetime 2026-05-18T16:00:00Z`
  - [ ] Gate: `python3 scripts/analysis_gate.py --analysis-file data/analyzed/YYYY-WNN-summary.md --raw-json data/raw/YYYY-WNN.json --current-datetime 2026-05-18T16:00:00Z`
  - [ ] Generate: `python3 scripts/generate_content.py data/analyzed/YYYY-WNN-summary.md`
  - [ ] Build search assets after Hugo: `npx pagefind --site public/`

- [ ] **Copilot auth failure handling (fail-closed verification)**
  - [ ] Comment out or rename `COPILOT_GH_TOKEN` secret temporarily
  - [ ] Manually trigger workflow
  - [ ] Verify workflow fails cleanly with a clear error (no fallback — pipeline is Copilot-only, fail-closed)
  - [ ] Confirm token-renewal issue automation triggers if configured
  - [ ] Restore secret after testing

- [ ] **Reskill cycle verified (after 5 runs)**
  - [ ] Count automated runs (every Monday = 1 run)
  - [ ] After 5 weeks, check for `.squad/reskill/YYYY-WNN.md` file
  - [ ] Verify the workflow invokes the real reskill path (`scripts/reskill.py`) and outputs analysis + recommendations

## Sign-Off

- **Operator name:** _______________
- **Date:** _______________
- **SquadScope instance:** https://_______________
- **All items checked:** Yes ☐ / No ☐

**Notes:**
```
[Space for operator notes or issues encountered]




```

---

## Troubleshooting During Rollout

If any checklist item fails, see `docs/operator-guide.md` for troubleshooting guidance:

- **Auth failures:** Section "Copilot auth failure"
- **Rate limits:** Section "GitHub API rate limits exceeded"
- **Build failures:** Section "Hugo build fails"
- **Quality gate blocks:** Section "Quality gate blocks publish"
- **Pages doesn't update:** Section "GitHub Pages doesn't update"
- **Reskill doesn't trigger:** Section "Reskill workflow doesn't trigger"

Good luck with your SquadScope rollout! 🚀
