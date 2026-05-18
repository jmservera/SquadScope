# SquadScope Operator Guide

This guide covers everything needed to set up, operate, monitor, and troubleshoot SquadScope in production.

## Prerequisites

Before starting, ensure you have:

1. **A GitHub repository** — Fork or create a copy of SquadScope
2. **GitHub Pages enabled** — In repo settings, set source to "GitHub Actions"
3. **GitHub Copilot subscription** — Required for AI-powered analysis (primary path)
   - Copilot Pro ($20/month) or Copilot Team subscription
   - Account with Copilot API access
4. **Fine-grained Personal Access Token (PAT)**
   - Scope: `github_pat_...` (not `ghp_...`)
   - Permission: Account → Copilot Requests (at least)
   - No expiration recommended (or set far future)
5. **Basic CLI tools** — `gh` CLI installed (`brew install gh` on macOS, `apt install gh` on Linux)

## Initial Setup

### Step 1: Clone the repository

```bash
git clone --recurse-submodules https://github.com/YOUR_USERNAME/SquadScope.git
cd SquadScope
```

If you forgot `--recurse-submodules`, initialize them now:

```bash
git submodule update --init --recursive
```
### Step 2: Verify Hugo version locally

Ensure your Hugo binary is v0.146.0 or newer:

```bash
hugo version
```

If needed, download the extended version:
- macOS: `brew install hugo`
- Linux: Download from [hugo releases](https://github.com/gohugoio/hugo/releases)
- Windows: Download from releases or use Chocolatey

### Step 3: Configure GitHub Copilot secret

Create a fine-grained PAT on GitHub:

1. Navigate to **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Configure:
   - **Token name:** `SquadScope-Copilot-Token`
   - **Expiration:** No expiration (or set to 1 year)
   - **Repository access:** Select your SquadScope repository
   - **Account permissions:** Scroll to **Copilot Requests** and select **Read and write**
   - Click **Generate token**
4. Copy the token (you won't see it again)

Add the token as a repository secret:

```bash
# Using GitHub CLI
gh secret set COPILOT_GH_TOKEN --body YOUR_PAT_HERE -R YOUR_USERNAME/SquadScope

# Or manually in repo settings:
# Settings → Secrets and variables → Actions → New repository secret
# Name: COPILOT_GH_TOKEN
# Value: github_pat_...
```

Verify the secret exists:

```bash
gh secret list -R YOUR_USERNAME/SquadScope
```

### Step 4: Configure optional webhook notifications

To notify a team channel whenever a weekly summary is published, add a repository secret named `WEBHOOK_URL` (a secret, not a variable, because webhook URLs are credentials that should be masked and protected):

```bash
gh secret set WEBHOOK_URL --body "https://example.com/webhook" -R YOUR_USERNAME/SquadScope
```

You can also add it in the GitHub UI under **Settings → Secrets and variables → Actions → Secrets**.

Supported endpoints:

- **Discord:** Create a webhook in the target channel's **Edit Channel → Integrations → Webhooks** settings, then paste that webhook URL into `WEBHOOK_URL`.
- **Slack:** Create an **Incoming Webhook** app for the target channel, then paste that webhook URL into `WEBHOOK_URL`.
- **Custom endpoint:** Any endpoint that accepts an HTTP `POST` with a JSON body containing `content` and `username` fields.

If `WEBHOOK_URL` is unset, the workflow skips the webhook step automatically.

### Step 5: Enable GitHub Pages

1. Navigate to repo **Settings → Pages**
2. Set **Source** to "GitHub Actions"
3. (Optional) Configure custom domain if desired
4. Save

### Step 6: Test local build

Ensure the Hugo build works locally:

```bash
hugo server
```

Visit `http://localhost:1313` and verify the site loads. Press `Ctrl+C` to stop.

For production build:

```bash
hugo --minify
```

This generates the `public/` directory with optimized static assets.

## Running the Pipeline

### Option A: Automatic scheduling (default)

The pipeline runs automatically every **Monday at 08:00 UTC** via `.github/workflows/crawl-and-publish.yml`.

You don't need to do anything. Go to your repo's **Actions** tab to monitor runs.

### Option B: Manual trigger

Run the workflow manually:

```bash
gh workflow run crawl-and-publish.yml -R YOUR_USERNAME/SquadScope
```

Or through the GitHub UI:
1. Go to **Actions → Crawl and Publish**
2. Click **Run workflow**
3. Confirm

The workflow takes ~2-3 minutes depending on GitHub API response times.

### Option C: Run individual stages locally

For debugging or testing, run stages separately:

#### Crawl

```bash
python3 scripts/crawl.py --as-of 2026-05-18
```

Output: `data/raw/2026-W20.json`, `data/snapshots/2026-W20-stars.json`

#### Analyze (Fallback — if Copilot unavailable)

```bash
python3 scripts/analyze_fallback.py \
  --raw-json data/raw/2026-W20.json \
  --output data/analyzed/2026-W20-summary.md \
  --current-datetime 2026-05-18T16:00:00Z
```

Output: `data/analyzed/2026-W20-summary.md`

#### Quality gate

```bash
python3 scripts/analysis_gate.py \
  --analysis-file data/analyzed/2026-W20-summary.md \
  --raw-json data/raw/2026-W20.json \
  --current-datetime 2026-05-18T16:00:00Z
```

If the gate fails, it will exit with a non-zero code and log the reason (e.g., quality_score < 60).

#### Generate

```bash
python3 scripts/generate_content.py data/analyzed/2026-W20-summary.md
```

Output: `content/weekly/2026/W20.md`

#### Build and deploy

```bash
hugo --minify
```

Output: `public/` directory ready for GitHub Pages.

## Monitoring the Cron Schedule

### View recent runs

```bash
gh run list -R YOUR_USERNAME/SquadScope --workflow crawl-and-publish.yml --limit 10
```

### Check a specific run

```bash
gh run view RUN_ID -R YOUR_USERNAME/SquadScope
```

### Stream live logs

```bash
gh run view RUN_ID -R YOUR_USERNAME/SquadScope --log
```

### Monitor in the UI

Navigate to **Actions → Crawl and Publish** in your repo. Green checkmarks = success, red X = failure.

## Troubleshooting Common Failures

### ❌ Copilot auth failure

**Error message:** `COPILOT_GITHUB_TOKEN not configured` or `401 Unauthorized`

**Cause:** The `COPILOT_GH_TOKEN` secret is missing, expired, or has insufficient permissions.

**Fix:**
1. Verify the secret exists: `gh secret list -R YOUR_USERNAME/SquadScope`
2. Regenerate the PAT if expired (Settings → Developer settings → Personal access tokens)
3. Confirm it has **Account → Copilot Requests** permission
4. Update the secret: `gh secret set COPILOT_GH_TOKEN --body YOUR_NEW_PAT -R YOUR_USERNAME/SquadScope`
5. Re-run the workflow

**Fallback:** The workflow automatically falls back to GitHub Models API if Copilot fails. Check the workflow logs to see which path was used.

### ❌ GitHub API rate limits exceeded

**Error message:** `API rate limit exceeded (60/60)` or `secondary rate limit`

**Cause:** Too many API calls in a short time window. GitHub's search endpoint is particularly strict.

**Fix:**
1. The crawler has built-in backoff logic. Wait 15 minutes and retry.
2. For immediate relief, configure a `GITHUB_TOKEN` (built-in) in the workflow to increase rate limits from 60/hour to 5,000/hour.
3. If using a fine-grained PAT, ensure it has minimal required permissions (reduces quota consumption).

**Avoid:** Running crawl jobs back-to-back in rapid succession.

### ❌ Copilot quota exhausted

**Error message:** `Quota exhausted` or `429 Too Many Requests`

**Cause:** You've used up your Copilot API requests for the billing cycle (typically thousands per month for Copilot Pro).

**Fix:**
1. Check your Copilot usage: https://github.com/settings/copilot
2. If you hit the limit, wait for the next billing cycle or upgrade your plan
3. The workflow will automatically fall back to GitHub Models API (lower quality, but functional)

**Mitigation:** Copilot Pro includes generous quota. For automated pipelines, consider Copilot Team (more quota, better for organizations).

### ❌ Hugo build fails

**Error message:** `error: /content/weekly/... failed to parse date` or `theme not found`

**Cause:** 
- Hugo version mismatch (too old)
- Theme submodules not initialized
- Corrupted frontmatter in generated content

**Fix:**
1. Check Hugo version: `hugo version` (must be v0.146.0+)
2. Verify submodules: `git submodule update --init --recursive`
3. Check generated markdown in `content/weekly/` for valid YAML frontmatter
4. Run locally: `hugo server` to see detailed error messages

### ❌ GitHub Pages doesn't update

**Error message:** Site shows old content or doesn't deploy

**Cause:** 
- Pages source not set to "GitHub Actions"
- Deployment workflow didn't complete successfully
- Cache not cleared

**Fix:**
1. Verify Pages source: Repo **Settings → Pages → Source = "GitHub Actions"**
2. Check the **Actions** tab for failed deploy jobs
3. Clear browser cache (`Ctrl+Shift+Delete`) and refresh
4. Force redeploy: Push a dummy commit to `main` or manually trigger `deploy-site.yml` workflow

### ❌ Quality gate blocks publish

**Error message:** `quality_score < 60` or `Missing required sections (Signal, Noise, Gaps)`

**Cause:** The AI analysis didn't meet quality thresholds. This is a **feature, not a bug** — the gate prevents low-quality content from publishing.

**Fix:**
1. Check the analysis file: `cat data/analyzed/YYYY-WNN-summary.md`
2. Review the quality_score in the YAML frontmatter
3. If analysis is genuinely poor, this may indicate a problem with the raw data (crawler issue) or Copilot API issues
4. **Do NOT bypass the gate.** Instead:
   - Investigate why analysis quality was low
   - Retry the workflow (Copilot may have had transient issues)
   - If consistent, open an issue with the analyzed output for review

### ❌ Reskill workflow doesn't trigger

**Error message:** Reskill job skipped in the logs

**Cause:** Reskill only runs every 5th pipeline execution. If you've only run 1-4 times, it won't trigger yet.

**Fix:**
1. Run the workflow 4 more times to trigger a reskill (or wait for 4 more weeks)
2. Check `.squad/run-counter.txt` to see how many runs have executed
3. To manually test reskill logic, run: `python3 scripts/reskill.py --current-week YYYY-WNN --current-datetime 2026-05-18T16:00:00Z` (or wait for automatic 5th run trigger in `crawl-and-publish.yml`)

## The Reskill Cycle

Every 5th pipeline run, SquadScope enters a "reskill" phase where it reviews its own behavior and proposes improvements.

### What happens

1. **Copilot reads:**
   - `.squad/agents/*/history.md` — Learnings from all agents
   - `.squad/decisions.md` — Architectural decisions made
   - `data/analyzed/` — Recent analysis outputs (quality trend)
   - `.squad/run-counter.txt` — Run history

2. **Analysis:**
   - What patterns are working well?
   - What should change in prompts or logic?
   - Are there quality drift signals?

3. **Output:**
   - Recommendations written to `.squad/reskill/YYYY-WNN.md`
   - Optional: PR proposed with prompt refinements (not auto-merged)

### What to expect

- **First reskill (run 5):** Observations and baseline recommendations
- **Subsequent reskills:** Trend analysis ("quality is improving" vs. "signal/noise classification drifting")
- **Prompts may be refined:** If reskill suggests prompt changes, review the PR and decide whether to merge

### No manual action required

Reskill runs automatically. You can review the outputs in `.squad/reskill/` directory, but the system works fine without human intervention.

## Updating Configuration

### Change the crawl schedule

Edit `.github/workflows/crawl-and-publish.yml`:

```yaml
on:
  schedule:
    - cron: '0 8 * * 1'  # Change to your desired time (UTC)
```

Times are in UTC. Use crontab.guru to generate your schedule.

### Change the reskill interval

Edit `.github/workflows/crawl-and-publish.yml` or `.squad/run-counter.txt`:

```yaml
# In workflow, modify the modulo check:
if [ $((COUNTER % 5)) -eq 0 ]; then  # Change 5 to desired interval
```

### Update the analyzer prompts

Prompts live in `prompts/` directory. Edit and commit changes. They take effect on the next workflow run.

### Customize quality gate thresholds

Edit `scripts/analysis_gate.py`:

```python
MIN_QUALITY_SCORE = 60  # Change threshold here
MIN_WORD_COUNT = 200
```

## Monitoring Site Health

### Check RSS feed generation

```bash
curl https://YOUR_SITE/index.xml
```

Should return valid XML with recent article entries.

### Verify Hugo build output

```bash
# After running locally:
ls public/
hugo --minify && wc -l public/*.html
```

Should show HTML files for each content page.

### Monitor GitHub API usage

Check your GitHub API rate limits:

```bash
gh api rate_limit
```

Output shows `limit`, `remaining`, and `reset` time. If you're consistently hitting limits, consider:
- Running less frequently
- Optimizing the crawler queries
- Using a GitHub App instead of PAT (higher limits)

## Disaster Recovery

### Revert a bad analysis

If analysis was published but is clearly incorrect:

1. Manually edit `data/analyzed/YYYY-WNN-summary.md` to correct it
2. Commit and push
3. Re-run `generate` and `deploy` stages (or full pipeline)
4. The week's content will be regenerated with corrected data

### Reset the run counter

If you want reskill to trigger immediately:

```bash
echo "5" > .squad/run-counter.txt
git add .squad/run-counter.txt
git commit -m "Reset run counter to trigger reskill"
git push
```

Next run will trigger reskill logic.

### Restore from a previous week

Content is immutable by design. If you need to restore:

1. Check git history: `git log --oneline -- data/analyzed/YYYY-WNN-summary.md`
2. Revert if necessary: `git revert COMMIT_HASH`
3. Regenerate and deploy

## Getting Help

- **Logs:** Check **Actions** tab in GitHub UI for detailed workflow logs
- **Common issues:** See troubleshooting section above
- **Architecture questions:** See `.squad/decisions.md` for design rationale
- **PRD:** See `docs/PRD.md` for feature requirements and future phases
- **Issues:** Open an issue in the repository with logs and error messages

## What's Next?

Once SquadScope is running smoothly:

1. **Monitor quality:** Review weekly analyses for patterns and trends
2. **Iterate prompts:** Based on reskill recommendations, refine analysis quality
3. **Extend sources:** Add additional data sources (HackerNews, Reddit, etc.) via MCP tools
4. **Add notifications:** Configure GitHub Releases, Discord/Slack webhooks, or custom webhook integrations
5. **Topic channels:** Explore multi-topic feature (see `docs/PRD-topic-channels.md`)

SquadScope is designed to improve itself. Trust the system, monitor the trends, and enjoy curated tech news delivered every week.
