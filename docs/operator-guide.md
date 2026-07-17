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

### Step 5: Configure optional Podcaster handoff

To ask the separate Podcaster service to generate an episode after a normal weekly article is published and deployed, configure:

- Actions variable `PODCASTER_ENDPOINT`, for example `https://<function-app-name>.azurewebsites.net/api/generate` or local testing URL `http://localhost:7071/api/generate`
- Actions secret `PODCASTER_API_KEY`

The workflow sends `week`, `article_url`, `article_path`, `article_sha256` when available, `publish_run_id`, `publish_mode`, and source artifact references after the normal article deploy succeeds. Dry-run, candidate-only, restore, force-replace, no-AI, and failed runs do not call Podcaster. If either endpoint value is missing, the handoff is skipped. The API key is sent only as the `x-podcaster-api-key` header and must not be printed, logged, or committed. Handoff failure is non-critical and does not roll back or block article publication.

### Step 6: Enable GitHub Pages

1. Navigate to repo **Settings → Pages**
2. Set **Source** to "GitHub Actions"
3. (Optional) Configure custom domain if desired
4. Save

### Step 7: Test local build

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

The pipeline runs automatically on Sundays at **11:53 UTC** (`53 11 * * 0`) via `.github/workflows/crawl-and-publish.yml`.

GitHub-hosted scheduled workflows are **best effort**, not an exact-time SLA, so a cron match does not guarantee the job will start at 11:53. Go to your repo's **Actions** tab to monitor runs.

#### Schedule latency and mitigation ladder

SquadScope treats GitHub Actions `schedule` on shared runners as a convenience default, not as a punctual trigger. This repository has already observed multi-hour delays on the previous Monday `06:53 UTC` slot:

- 2026-05-25: started at **11:55 UTC**
- 2026-06-01: started at **14:37 UTC**
- 2026-06-08: started at **12:17 UTC**

Supported operating model, in order:

1. **Default:** keep the current Sunday `53 11 * * 0` cron as the low-effort baseline.
2. **Manual fallback:** run `gh workflow run crawl-and-publish.yml -R YOUR_USERNAME/SquadScope` (or use the Actions UI) when an operator needs to start the pipeline immediately.
3. **Recommended mitigation for punctual launches:** keep the workflow as-is and have an external scheduler call the existing `workflow_dispatch` trigger. Example CLI target for a cron job or scheduler host:

   ```bash
   gh workflow run crawl-and-publish.yml -R YOUR_USERNAME/SquadScope
   ```

   Example GitHub API dispatch:

   ```bash
   curl -L \
     -X POST \
     -H "Accept: application/vnd.github+json" \
     -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.github.com/repos/YOUR_USERNAME/SquadScope/actions/workflows/crawl-and-publish.yml/dispatches \
     -d '{"ref":"main","inputs":{"run_mode":"normal","source_refresh_policy":"reuse-same-day"}}'
   ```

4. **Optional future escalation:** move to self-hosted runners only if you need tighter operational control; that is not required for the default setup.

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

#### Manual rerun modes

Manual runs default to `run_mode=normal` and `source_refresh_policy=reuse-same-day`. Normal mode is fail-closed: it may publish only after the existing analysis and freshness gates pass, and same-day successful source artifacts are reused instead of scraping again. Missing, failed, stale, wrong-week, or wrong-window sources are refreshed.

##### Rerun mode reference

All rerun modes are validated before any publishing side effects:

| Mode | Crawl | Promotion | Intent | Use case |
|------|-------|-----------|--------|----------|
| `normal` (default) | ✓ Fresh | ✓ Guarded gates | Produce fresh analysis, publish if gates pass | Standard weekly run |
| `dry-run` | ✓ Fresh | ✗ Never | Build candidates only for inspection | Test analysis quality, verify gates, debug analysis |
| `candidate-only` | ✓ Fresh | ✗ Manifest blocks | Run crawl/analysis but hold for manual approval | Staged analysis, manual promotion workflow |
| `restore` | ✗ Hydrate | ✓ Guarded gates | Regenerate a prior week from one source-bound immutable raw run | Restore/audit trail, regenerate HTML/feeds |
| `force-replace` | ✓ Fresh | ✓ Guarded gates | Explicit replacement run, gates still enforce | Planned content refresh, operator override |

##### Source refresh policies

Control how same-day artifacts are handled during reruns:

| Policy | Behavior | Use case |
|--------|----------|----------|
| `reuse-same-day` (default) | Reuse eligible same-day raw artifacts; refresh missing/stale/failed sources | Safe rerun without redundant API calls |
| `refresh-missing-stale` | Like reuse-same-day but also refresh sources with missing or stale status | Partial refresh, correct specific source issues |
| `force-refresh` | Refresh all sources regardless of prior status | Force all new data, ignore cache |

Same-day artifact reuse is safe by design:
- Only successfully crawled artifacts are eligible for reuse
- Missing, failed, stale (>24 hours old), or wrong-week sources are always refreshed
- Source status (reused/refreshed/missing/failed/stale) is recorded in the publish manifest for audit trail

Invalid combinations fail immediately with clear error messages:
- `rebuild_week` without `run_mode=restore`
- `run_mode=restore` without both `rebuild_week` and `source_run_id`
- `run_mode=restore` with `source_refresh_policy=force-refresh`
- `publish_release=true` with `dry-run` or `candidate-only`

##### Durable raw evidence and restore

Each publishing crawl writes the current week's raw payloads to the existing
`publish` branch under:

```text
data/raw-store/<week>/<source_run_id>/
```

The run directory is immutable: a repeated write to the same week/run path fails
instead of replacing files. Its `manifest.json` records the source workflow run,
`raw-data` artifact ID/name, source head SHA, original paths, sizes, and SHA-256
hashes.

Restore must identify that exact source run:

```bash
gh workflow run crawl-and-publish.yml \
  -R YOUR_USERNAME/SquadScope \
  -f run_mode=restore \
  -f rebuild_week=2026-W23 \
  -f source_run_id=26753498571
```

The workflow verifies the immutable manifest identity and every stored hash before
copying any file into `data/raw/`. The selected manifest is authoritative for the
week, so same-week raw files left by the checkout or artifact overlay but absent
from that source run are removed before analysis. The publish eligibility manifest
records the verified source run/artifact provenance and rechecks restored input
hashes before promotion.

The GitHub Actions `raw-data` artifact has **90-day retention** and remains a
transport mechanism for jobs, same-day reuse, and emergency recovery only. It is not
the durable raw store. The durable copy is the immutable week/run directory on
`publish`; it is intentionally not synced into `main`.

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

## Understanding Source Artifacts and Reuse

### Source artifact tracking

When SquadScope crawls, it records detailed information about each source artifact:

- **Status:** One of `reused`, `refreshed`, `missing`, `failed`, or `stale`
- **Artifact checksum:** SHA256 of successful crawls for integrity verification
- **Timestamp:** When the artifact was produced or reused
- **Code checksum:** Hash of the crawler code that produced it (detects version drift)

This metadata is stored in the **publish manifest** (`data/candidates/YYYY-WNN/RUN_ID/publish-manifest.json`) for every run, creating an auditable trail of:
- Which sources were fetched vs. reused
- Why sources were refreshed (missing, failed, stale, code drift)
- Provenance of every analysis artifact

### Examining source status

After a run completes, check the publish manifest to see which sources were reused or refreshed:

```bash
# Find the latest manifest for week 2026-W21
find data/candidates/2026-W21 -name publish-manifest.json | sort -V | tail -1 | xargs cat | jq '.source_artifacts'
```

Output shows:
```json
{
  "source_artifacts": [
    {
      "role": "raw_github",
      "path": "data/candidates/2026-W21/github-crawl.json",
      "exists": true,
      "size_bytes": 45823,
      "sha256": "686085ace216e10d36837a91471e28a334b2fc3d93cc1085b8d5d0e7616891bf",
      "same_day_reuse": {
        "status": "reused",
        "source": "default"
      },
      "freshness": {
        "status": "fresh",
        "reasons": []
      },
      "provenance": {
        "generated_at": "2026-05-20T10:15:00Z",
        "sha256": "686085ace216e10d36837a91471e28a334b2fc3d93cc1085b8d5d0e7616891bf"
      }
    },
    {
      "role": "external_news",
      "path": "data/candidates/2026-W21/news-articles.json",
      "exists": true,
      "size_bytes": 28941,
      "sha256": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
      "same_day_reuse": {
        "status": "not_reused",
        "source": "refresh_policy"
      },
      "freshness": {
        "status": "stale",
        "reasons": ["source_refresh_policy=refresh-missing-stale"]
      },
      "provenance": {
        "generated_at": "2026-05-21T08:30:00Z",
        "sha256": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
      }
    }
  ]
}
```

### Safe rerun scenario

**Scenario:** You rerun Monday's analysis on Tuesday morning (same week) to fix a quality gate failure.

**Expected behavior with `source_refresh_policy=reuse-same-day` (default):**
1. Monday's successful GitHub crawl is reused (1 API call saved)
2. Any failed or missing sources from Monday are refreshed
3. Analysis gates run on fresh analysis only
4. If gates pass, publish replaces Monday's article
5. If gates fail, the publish manifest blocks the promotion and preserves Monday's good article

**This is safe because:**
- Only Monday's *successful* artifacts are reused
- Any source that failed on Monday is fetched fresh
- The manifest explicitly records what was reused
- Quality gates prevent bad analysis from being published
- Good prior analysis is preserved if the retry fails

### When to use each policy

**Use `reuse-same-day` (default):**
- Standard reruns within the same day
- Debugging analysis issues
- Retrying quality gates after minor fixes

**Use `refresh-missing-stale`:**
- Some sources failed and you've fixed the crawler
- You want to update stale sources without fully refreshing

**Use `force-refresh`:**
- You suspect source data is corrupted or needs manual validation
- You're testing source updates
- Policy: Always use explicit intent for full refresh

## Safe Restore from Backup

### Understanding backups

Before any weekly article or analysis is replaced in the `publish` branch, an immutable backup is created at:

```
data/backups/YYYY-WNN/RUN_ID/[analysis|content]/manifest.json
```

Backups include:
- The exact prior content being replaced (e.g., `content/weekly/2026/W21.md`)
- The prior analysis file (e.g., `data/analyzed/2026-W21-summary.md`)
- SHA256 checksums of all backed-up files
- Timestamp and run context

### When backups are created

A backup is automatically created when:
1. A new analysis is about to replace a prior week's analysis, OR
2. A new content page is about to replace a prior week's HTML page

Backups are immutable—they cannot be modified or deleted by subsequent runs.

### Viewing available backups

```bash
# List all available backups for week 2026-W21
find data/backups/2026-W21 -name manifest.json | sort -V

# Inspect a backup manifest
cat data/backups/2026-W21/RUN_ID/content/manifest.json | jq .
```

Backup manifest shows:
```json
{
  "schema_version": "publish_backup_v1",
  "week": "2026-W21",
  "run_id": 12345678,
  "timestamp": "2026-05-20T10:15:00Z",
  "backed_up_artifacts": [
    {
      "path": "data/analyzed/2026-W21-summary.md",
      "sha256": "abc123...",
      "exists_before_replacement": true
    },
    {
      "path": "content/weekly/2026/W21.md",
      "sha256": "def456...",
      "exists_before_replacement": true
    }
  ]
}
```

### Restore a prior week from backup

To restore a prior week (e.g., restore 2026-W21 to a known-good state):

1. **Identify the backup manifest** you want to restore:
   ```bash
   # List backups for week 2026-W21, sorted by timestamp
   find data/backups/2026-W21 -name manifest.json | sort -V
   ```

2. **Trigger the restore workflow:**
   ```bash
   gh workflow run restore-publish-backup.yml \
     -R YOUR_USERNAME/SquadScope \
     -f "backup_manifest=data/backups/2026-W21/RUN_ID/content/manifest.json"
   ```

   Or through the UI:
   - Go to **Actions → Restore publish backup**
   - Click **Run workflow**
   - Paste the backup manifest path (e.g., `data/backups/2026-W21/12345678/content/manifest.json`)
   - Click **Run workflow**

3. **Restore will:**
   - Check out the `publish` branch
   - Validate the backup manifest integrity
   - Restore all backed-up files to their pre-replacement state
   - Commit with message: `restore: publish backup {manifest_path}`
   - Force-push to `publish` with lease safety guards

4. **Monitor the restore:**
   ```bash
   gh run view --log -R YOUR_USERNAME/SquadScope
   ```

### Restore operation guarantees

- **Immutable:** Backup manifests are never modified after creation
- **Atomic:** Restore applies all backed-up files or fails with no partial changes
- **Lease-guarded:** Force-push uses `--force-with-lease` to detect concurrent modifications
- **Audited:** Restore commit message includes the backup manifest path for traceability
- **Non-destructive:** Restoring does not delete new backups created since the restore date

**After a restore:**
- The `publish` branch is reverted to the state before that run
- Previous good analysis remains published
- The restore itself appears in git history for audit trail

## No-AI Fallback Policy

### Why no-AI is not a replacement strategy

SquadScope includes a no-AI fallback analysis script (`scripts/analyze_fallback.py`) that can generate a basic summary using heuristics when Copilot is unavailable. However, **no-AI output is explicitly not a replacement for Copilot analysis** and has specific constraints:

**No-AI fallback is used only when:**
1. Copilot CLI fails with a non-auth error (after retries), OR
2. Copilot encounters a non-recoverable error (e.g., context too large), OR
3. Copilot is completely inaccessible

**No-AI output characteristics:**
- Lower quality_score (typically 40–50 vs. 60+ for Copilot)
- Simple heuristic categorization (no editorial synthesis)
- May have incomplete signal/noise/gaps sections
- Preserved as a "rejected candidate" artifact
- **Does not publish without explicit operator override**

### Publish manifest promotion policy

When Copilot fails and no-AI fallback is generated:
1. The no-AI candidate is created and stored in `data/candidates/YYYY-WNN/RUN_ID/`
2. The publish manifest records `analysis_source: "no-ai"` and `quality_validation: "failed"`
3. **The promotion guard blocks publication** regardless of whether gates pass
4. The prior week's good analysis remains published (safe default)

To inspect a rejected no-AI candidate:

```bash
# List rejected candidates for week 2026-W21
find data/candidates/2026-W21 -name 'candidate-no-ai-attempt-*.md'

# Review the no-AI candidate and its gate report
cat data/candidates/2026-W21/RUN_ID/diagnostics/candidate-no-ai-attempt-0.md
cat data/candidates/2026-W21/RUN_ID/diagnostics/gate-no-ai-attempt-0.json | jq '.validation_failures'
```

### Copilot access failures

If Copilot CLI fails with an authentication or access error:
- The workflow **fails immediately without attempting no-AI fallback**
- An issue is created (or updated) to notify the operator to renew `COPILOT_GH_TOKEN`
- The failure report is available at `data/candidates/YYYY-WNN/RUN_ID/diagnostics/copilot-cli-failure-*.json`

This ensures that **transient Copilot issues do not silently degrade to no-AI analysis.**

### Copilot retries

If Copilot produces output that doesn't pass the quality gate, the workflow automatically retries up to 3 times:
- Each retry includes focused diagnostics from the prior gate failure
- If all retries fail, no-AI fallback is attempted as a last resort
- Each retry and its diagnostics are recorded for audit trail

## Rejected Candidate Diagnostics

When analysis fails to pass quality gates, detailed diagnostics are recorded for investigation:

### Candidate directory structure

```
data/candidates/YYYY-WNN/RUN_ID/
  ├── YYYY-WNN-summary.md              # Candidate analysis (if produced)
  ├── YYYY-WNN-content.md              # Generated HTML candidate (if produced)
  ├── publish-manifest.json            # Eligibility and provenance
  └── diagnostics/
      ├── analysis-preflight.json      # Deterministic input manifest, context budget, evidence inventory
      ├── analysis-preflight.md        # Preflight diagnostic report
      ├── copilot-cli-attempt-N.log    # Raw Copilot CLI stderr/stdout
      ├── gate-copilot-cli-attempt-N.json  # Quality gate failure details
      ├── candidate-copilot-cli-attempt-N.md  # Candidate snapshot
      ├── candidate-no-ai-attempt-0.md      # No-AI fallback (if used)
      └── gate-no-ai-attempt-0.json        # No-AI gate report
```

### Examining a failed gate report

```bash
# View gate failure for attempt 0
cat data/candidates/2026-W21/RUN_ID/diagnostics/gate-copilot-cli-attempt-0.json | jq '{
  passed: .passed,
  gates: .gates,
  errors_before_repair: .errors_before_repair,
  repair_actions: .repair_actions,
  failure_class: .failure_class,
  failure_summary: .failure_summary
}'
```

Gate report output:
```json
{
  "passed": false,
  "gates": {
    "structural_schema": {
      "passed": false,
      "errors": [
        "Signal section is empty or malformed",
        "Signal section must contain at least 3 significant claims"
      ]
    },
    "editorial_quality": {
      "passed": false,
      "errors": [
        "Noise section has fewer than 3 spurious claims"
      ]
    },
    "ai_provenance": {
      "passed": true,
      "errors": []
    },
    "evidence_citation": {
      "passed": true,
      "errors": []
    }
  },
  "errors_before_repair": [
    "Signal section is empty or malformed",
    "Signal section must contain at least 3 significant claims",
    "Noise section has fewer than 3 spurious claims"
  ],
  "repair_actions": [
    "Expanded Signal section with 3 significant claims from trending repositories",
    "Added 3 spurious/false claims to Noise section"
  ],
  "errors_after_repair": [],
  "failure_class": "passed",
  "failure_summary": {
    "failure_class": "passed",
    "failure_categories": [],
    "error_count": 0,
    "retryable": false
  }
}
```

`analysis-preflight.json` is the source of truth for prompt inputs. It includes byte/token/checksum metadata for each prompt component and evidence inventories (`raw_new_repos`, `raw_trending_repos`, `prompt_new_repos`, `prompt_trending_repos`) so operators can verify whether a final repo link was present in current crawl evidence or only in compacted prompt context.

### Quality gate specifics

The publish manifest records:
- `quality_score`: 0–100, where 60+ is publishable
- `quality_source`: "copilot-cli", "no-ai", etc.
- `validation_status`: "passed" or "failed"
- `validation_failures`: Array of specific failures with repair suggestions

Failed gates block promotion but don't prevent the candidate from being stored for audit trail.

## Map/Reduce Analysis Status (Dry-Run Only)

### Why map/reduce remains experimental

SquadScope's analysis pipeline is currently single-pass for production use. Map/reduce analysis—dividing evidence into smaller chunks, analyzing each independently, then combining results—is **only available as a dry-run experimental feature** and cannot publish. This decision was made after evidence from live runs and is documented in `docs/PRD-matrix-crawl-map-reduce-analysis.md`.

### Current limitations preventing map/reduce publication

1. **Analysis specification mismatch:** Map/reduce mapper outputs would create intermediate artifacts not conforming to `docs/analysis-spec.md`
2. **Citation preservation:** Combining mapper outputs risks losing original citations and creating false attribution
3. **Claim deduplication:** Reducer must reliably dedupe claims across mappers; no production-grade deduplication exists yet
4. **Token accounting:** Final combined analysis may exceed token budgets; mechanism for bounded reduction is unproven
5. **Quality gate compliance:** Existing gates expect single-pass analysis structure; map/reduce will need new gates

### QA gates required before map/reduce can publish (#258)

Before map/reduce analysis can be enabled for production promotion, all of these QA gates must pass:

- [ ] **Mapper-reducer contract testing:** Mappers and reducers in sandboxed runs must produce deterministic, validated outputs
- [ ] **Citation preservation testing:** Full analysis -> map/reduce roundtrip must preserve or improve citation count/accuracy
- [ ] **Claim deduplication testing:** Reducer must reliably identify and merge duplicate claims across mappers
- [ ] **Token budget compliance:** End-to-end analysis must stay within token limits; no truncation or quality regression
- [ ] **Spec compliance testing:** Generated analysis must pass all existing `analysis_gate.py` checks without modification
- [ ] **Human editorial review:** Blind A/B comparison of single-pass vs. map/reduce outputs from 4+ weeks of real data
- [ ] **Fallback behavior:** Ensure Copilot retries and no-AI fallback work correctly with map/reduce logic

### Testing map/reduce in dry-run mode

To test map/reduce without risk of publication:

```bash
gh workflow run crawl-and-publish.yml \
  -R YOUR_USERNAME/SquadScope \
  -f "run_mode=dry-run"
```

Dry-run mode ensures:
- Analysis is generated but never promoted
- No HTML is published
- Candidates are stored for inspection
- You can review results before any live traffic sees them

### Expected timeline

Map/reduce publication will be enabled in a future phase after:
- All QA gates (#258) are implemented and passing
- Human review confirms output quality meets or exceeds single-pass
- Operator documentation is completed
- Rollback procedures are tested

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

**Fallback:** There is no GitHub Models/OpenAI fallback for weekly analysis. Token/auth failures fail immediately and create or update an issue assigned to `@jmservera` to renew `COPILOT_GH_TOKEN`.

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
3. The workflow retries transient Copilot failures, but no GitHub Models/OpenAI fallback is configured for weekly analysis.

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
    - cron: '53 11 * * 0'  # Sunday 11:53 UTC; still best-effort on GitHub-hosted runners
```

Times are in UTC. Use crontab.guru to generate your schedule, but assume GitHub-hosted `schedule` can start late and use the `workflow_dispatch` mitigation ladder above if exact timing matters.

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

## Manual Pipeline Tools

These scripts are not part of the automated weekly pipeline but are available
for manual operator use.

### Hindsight Validation

Validates predictions from N weeks ago against actual outcomes. Run periodically
to track prediction accuracy:

```bash
python scripts/hindsight_validation.py --topic ai-ml --weeks-ago 4
```

Output: a scorecard summary comparing predicted outcomes with real data.

### Topic Learning Initialization

Bootstraps per-topic learning state directories with seeded wisdom. Use when
adding a new topic channel or resetting learning state:

```bash
python scripts/init_topic_learning.py --topic my-new-topic
```

### Momentum Tracker

Checks press-correlated repos at week +2/+4 and classifies growth as
"sustained" or "faded". Already referenced in site methodology content:

```bash
python scripts/momentum_tracker.py --topic ai-ml --week 2026-W21 --lag 4
```

### Budget Alerts

Evaluates run cost and monthly cumulative spend against thresholds. Wired into
the `crawl-and-publish` workflow automatically, but can also be run manually:

```bash
python scripts/budget_alerts.py --metrics data/metrics/token-usage.jsonl
```

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
