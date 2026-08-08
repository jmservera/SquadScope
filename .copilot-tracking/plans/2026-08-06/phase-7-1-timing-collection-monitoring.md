<!-- markdownlint-disable-file -->

# Phase 7.1 Timing Collection — CI Monitoring Workflow

**Date**: 2026-08-06  
**Status**: Awaiting natural CI pipeline execution  
**Objective**: Collect Hugo and Pagefind duration data from next 2 CI builds; calculate p95 budgets  

---

## Timing Data Already Captured

### Run 1: 2026-08-05 (Baseline ✅)
- **Commit**: 211f0974 (exact-main-31039618366)
- **Hugo**: 15,339 ms
- **Pagefind**: 1,631 ms
- **Source**: CI artifact `reports/build-timing.json` from production-site job

**Status**: ✅ Captured and recorded in timing-analysis.md

---

## Pending Runs: 2-3

### Run 2: Awaiting Next Successful CI Build
- **Trigger**: Automatic on next successful push to main OR manual workflow trigger
- **Expected Date**: 2026-08-07 or later (depends on commit frequency)
- **Action**: Monitor GitHub Actions > CI workflow > Production site job

### Run 3: Awaiting Second CI Build After Run 2
- **Expected Date**: 1-2 days after Run 2
- **Action**: Same monitoring process

---

## Data Extraction Workflow

### Step 1: Monitor CI Runs

**Via GitHub Actions UI**:
1. Navigate to: github.com/jmservera/SquadScope/actions
2. Select: CI workflow (`.github/workflows/ci.yml`)
3. Wait for: `production-site` job to complete successfully
4. Download artifacts: production-quality-reports

**Via gh CLI**:
```bash
# List recent CI runs
gh run list --workflow ci.yml --limit 5

# Get specific run ID
RUN_ID=$(gh run list --workflow ci.yml --limit 1 --json databaseId | jq -r '.[0].databaseId')
echo "Latest run ID: $RUN_ID"

# Download artifacts
gh run download "$RUN_ID" --name production-quality-reports --dir /tmp/timing-run-$RUN_ID
```

### Step 2: Extract Timing Data

**Location**: `reports/build-timing.json` in downloaded artifact

**File Format**:
```json
{
  "hugo": {
    "duration_ms": 15339,
    "timestamp": "2026-08-05T12:34:56Z",
    "commit_sha": "211f0974"
  },
  "pagefind": {
    "duration_ms": 1631,
    "timestamp": "2026-08-05T12:35:20Z"
  }
}
```

**Extraction Command**:
```bash
# Extract Hugo duration
HUGO_MS=$(jq '.hugo.duration_ms' /tmp/timing-run-*/reports/build-timing.json)
echo "Hugo: $HUGO_MS ms"

# Extract Pagefind duration
PAGEFIND_MS=$(jq '.pagefind.duration_ms' /tmp/timing-run-*/reports/build-timing.json)
echo "Pagefind: $PAGEFIND_MS ms"
```

### Step 3: Record in timing-analysis.md

**File**: `docs/review/data-observatory-relaunch/timing-analysis.md`

**Update Template** (lines 60-80):
```markdown
### Run 2: [DATE]
- **Commit**: [SHA]
- **Hugo**: [DURATION_MS] ms
- **Pagefind**: [DURATION_MS] ms
- **Source**: GitHub Actions run [RUN_ID]
- **Status**: ✅ Captured

### Run 3: [DATE]
- **Commit**: [SHA]
- **Hugo**: [DURATION_MS] ms
- **Pagefind**: [DURATION_MS] ms
- **Source**: GitHub Actions run [RUN_ID]
- **Status**: ✅ Captured
```

### Step 4: Calculate Statistics

**After Runs 2-3 captured, update timing-analysis.md "Timing Statistics" section**:

```bash
# Calculate median and p95
RUN1_HUGO=15339
RUN2_HUGO=<from artifact>
RUN3_HUGO=<from artifact>

# Median (middle value when sorted)
MEDIAN_HUGO=$(echo "$RUN1_HUGO $RUN2_HUGO $RUN3_HUGO" | tr ' ' '\n' | sort -n | sed -n '2p')
echo "Hugo Median: $MEDIAN_HUGO ms"

# P95 (highest value in 3-sample set)
P95_HUGO=$(echo "$RUN1_HUGO $RUN2_HUGO $RUN3_HUGO" | tr ' ' '\n' | sort -n | tail -1)
echo "Hugo P95: $P95_HUGO ms"

# Same for Pagefind
```

---

## Budget Thresholds & Approval

### Current Thresholds (Proposed)

| Metric | Budget | Margin | Notes |
|--------|--------|--------|-------|
| Hugo p95 | 20,000 ms | 30% | Based on baseline 15,339 ms + 30% headroom |
| Pagefind p95 | 2,500 ms | 50% | Based on baseline 1,631 ms + 50% headroom |

**Status**: Report-only (non-blocking) for Phase 7 acceptance gate

### Approval Process

1. **Calculate** median and p95 from Runs 1-3
2. **Compare** against thresholds
3. **Prepare** summary report:
   ```markdown
   ## Timing Budget Approval (Phase 7.1)
   
   **Collected Data** (3 runs):
   - Hugo: Run1=15,339ms, Run2=[X]ms, Run3=[Y]ms → p95=[MAX]ms ≤ 20,000ms ✅
   - Pagefind: Run1=1,631ms, Run2=[X]ms, Run3=[Y]ms → p95=[MAX]ms ≤ 2,500ms ✅
   
   **Approval**: [✅ Approved | ⚠️ Needs Review]
   **Date**: [APPROVAL_DATE]
   **Approved by**: jmservera
   ```
4. **Submit** to jmservera for sign-off (sponsor)
5. **Record** in status-of-record.md: "Phase 7.1 Security: ✅ Approved [DATE]"

---

## Artifact Retention Warning ⚠️

**Critical**: GitHub Actions artifacts have 30-day retention. Timing data must be downloaded promptly.

**Timeline**:
- Run 1 artifact created: 2026-08-05 (expires 2026-09-04)
- Run 2 artifact created: ~2026-08-07 (expires ~2026-09-06)
- Run 3 artifact created: ~2026-08-08 or later (expires ~2026-09-07 or later)

**Action**: Download artifacts **within 24 hours** of CI job completion to avoid loss.

---

## Execution Checklist

### Run 2 Capture
- [x] CI workflow completes successfully on main — run `31079871801`
- [x] Navigate to GitHub Actions > CI > [Latest Run]
- [x] Confirm `production-site` job succeeded
- [x] Download artifact: `production-quality-reports`
- [x] Extract `reports/build-timing.json`
- [x] Record Hugo + Pagefind durations in timing-analysis.md — Hugo 2,456 / Pagefind 2,255 ms
- [x] Commit update to main

**Expected**: 2026-08-07

### Run 3 Capture
- [x] Next CI workflow completes successfully on main — run `31081291997`
- [x] Repeat Steps 1-6 from Run 2 Capture
- [x] Calculate median and p95 across all 3 runs — medians Hugo 2,822 / Pagefind 2,316 ms; p95 Hugo 3,058 / Pagefind 2,707 ms
- [x] Update timing-analysis.md "Timing Statistics" section

**Expected**: 2026-08-08 or 2026-08-09

### Approval & Closure
- [x] Prepare budget approval summary — proposed budgets and Approval Chain documented in `timing-analysis.md`
- [ ] Submit to jmservera for sign-off — human-authority (owners: timing-budget owner, URL, jmservera)
- [ ] Record approval in status-of-record.md — human-authority; awaits sign-off
- [ ] Mark Phase 7.1 as complete — human-authority; awaits sign-off

**Expected**: 2026-08-09

---

## Timing Analysis Document Status

**File**: `docs/review/data-observatory-relaunch/timing-analysis.md`  
**Current**: 170 lines, Run 1 captured  
**Target**: Add Runs 2-3, calculate statistics, record approval  
**Completion**: 60% (1/3 runs captured)

---

## Manual Workflow Trigger (If Needed)

If main branch has no pending commits and you want to force timing collection:

```bash
# Trigger CI workflow on main
gh workflow run ci.yml --ref main

# Watch for completion
watch -n 10 'gh run list --workflow ci.yml --limit 1'

# When complete, download timing data
RUN_ID=$(gh run list --workflow ci.yml --limit 1 --json databaseId | jq -r '.[0].databaseId')
gh run download "$RUN_ID" --name production-quality-reports
```

---

## Notes for jmservera (Sponsor/Timing-Budget Owner)

**Required Actions**:
1. Monitor for Runs 2-3 CI completions (passive, automatic)
2. When timing-analysis.md updated with Runs 2-3: Review and approve budget thresholds
3. Record approval in status-of-record.md
4. Confirm Phase 7.1 closure in final release readiness assessment

**Timeline**: 2-3 business days (2026-08-08/09 expected)

**Blocker Status**: Report-only (non-blocking for Phase 7 acceptance gate)

---

## Reference: CI Job Locations

- **CI Workflow**: `.github/workflows/ci.yml`
- **Production Site Job**: "Build site and capture Hugo duration" step
- **Timing Data Job**: "Capture timing" step in production-site job
- **Artifact Storage**: GitHub Actions UI > CI > [Run] > Artifacts > production-quality-reports

