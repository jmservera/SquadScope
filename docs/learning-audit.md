# SquadScope Learning System Audit

**Author:** Leela (Lead/Architect)  
**Date:** 2026-05-18T13:20:07.067+02:00  
**Scope:** End-to-end audit of the learning system — can SquadScope actually learn in production?

---

## Executive Summary

**Verdict: The learning system will NOT work in production today.** The design is sound but the implementation is almost entirely absent. Issues #14 and #15 correctly describe what needs to be built, but zero code exists for the reskill cycle. The workflow has no reskill job, no run counter exists, no `.squad/skills/` directory has been created, `wisdom.md` is empty, and there is no hindsight validation mechanism. The learning loop is a design-only artifact.

---

## 1. Reskill Cycle Implementation Status

### Issues #14 and #15 Assessment

| Issue | Title | Design Quality | Implementation | Status |
|-------|-------|---------------|----------------|--------|
| #14 | Implement reskill retrospective workflow and squad-state outputs | ✅ Good | ❌ Zero code | OPEN |
| #15 | Add run counter persistence and every-fifth-run reskill trigger | ✅ Good | ❌ Zero code | OPEN |

### Will the every-5th-run trigger work?

**Design (from `.squad/decisions.md` Decision 6):**
```bash
COUNTER=$(cat .squad/run-counter.txt)
if [ $((COUNTER % 5)) -eq 0 ]; then
  # reskill invocation
fi
```

**Problems with this design:**

1. **No run-counter.txt exists.** The file has never been created. First run would fail with `cat: .squad/run-counter.txt: No such file or directory`.
2. **No increment logic shown.** The decision shows the *check* but not who increments the counter or when. If the counter increments before the check, run 5 triggers. If after, run 6 triggers. The ordering matters and isn't specified.
3. **No atomicity guarantee.** The workflow uses stash/pop for commits but the counter update could race with concurrent `workflow_dispatch` triggers.
4. **No reskill job in the workflow.** `crawl-and-publish.yml` has jobs: `crawl`, `analyze`, `generate`, `deploy`, `notify`. There is no `reskill` job.
5. **Counter survives only if committed.** The workflow commits `data/raw`, `data/snapshots`, `data/analyzed`, and `content/weekly/` — but not `.squad/`. Counter changes would be lost.

### What's missing for #14 and #15:

- A `reskill` job in `crawl-and-publish.yml` (or a separate workflow)
- Counter initialization (`echo 0 > .squad/run-counter.txt`)
- Counter increment step in the crawl or analyze job
- Commit step that includes `.squad/run-counter.txt` changes
- The actual Copilot CLI invocation for reskill analysis
- Output writing to `.squad/reskill/YYYY-WNN.md`
- Commit step for reskill outputs (`.squad/` directory changes)

---

## 2. Learning Inputs

### Current state of each input source:

| Input | Exists? | Has Content? | Accessible in CI? | Notes |
|-------|---------|--------------|-------------------|-------|
| `.squad/agents/*/history.md` | ✅ Yes (7 agents) | ✅ Yes | ✅ Yes (checked out) | Contains real project learnings |
| `.squad/decisions.md` | ✅ Yes | ✅ Yes | ✅ Yes | Rich decision log |
| `.squad/identity/wisdom.md` | ✅ Yes | ❌ Empty (header only) | ✅ Yes | Zero accumulated wisdom |
| `.squad/skills/` | ❌ No | N/A | N/A | Directory never created |
| Past analysis outputs | ⚠️ Partial | Only if runs have occurred | ✅ Yes (`data/analyzed/`) | No historical comparison logic exists |
| Star snapshots | ⚠️ Empty | `data/snapshots/` exists but is empty | ✅ Yes | Crawler writes snapshots but none committed yet |

### Hindsight validation capability:

**Does not exist.** There is no code or process that:
- Compares "what we said was important 5 weeks ago" with "what actually became important"
- Uses star snapshot deltas to validate past predictions
- Measures whether Signal/Noise/Gaps calls were accurate in retrospect

The analysis spec mentions comparing to prior weeks (§ Context dimension), but this is only for the *current* analysis — it doesn't feed backward into learning.

---

## 3. Learning Outputs

### What should change after a reskill:

| Output | Mechanism Defined? | Implementation? | Will It Persist? |
|--------|-------------------|-----------------|-----------------|
| Updated `wisdom.md` heuristics | ⚠️ Implied only | ❌ No code | ❌ No commit step |
| New/updated skills in `.squad/skills/` | ✅ Reskill SKILL.md template exists | ❌ No code | ❌ No commit step, no directory |
| Adjusted significance thresholds | ❌ Not designed | ❌ No code | N/A |
| Updated hype detection patterns | ❌ Not designed | ❌ No code | N/A |
| Revised gap analysis focus | ❌ Not designed | ❌ No code | N/A |
| Reskill report in `.squad/reskill/YYYY-WNN.md` | ✅ Yes (Decision 6) | ❌ No code | ❌ No commit step |

### Critical gap: No feedback into the analysis prompt

Even if reskill produces updated wisdom or patterns, the `prompts/analyze-weekly.md` template has no variable or include that would inject learned heuristics. The analysis prompt is static. Learning outputs have no path back into the analysis pipeline.

---

## 4. Learning Feedback Loop

### Can the system measure improvement?

**No.** There is no mechanism to:

1. **Record predictions with timestamps.** The analysis output exists (`data/analyzed/YYYY-WNN-summary.md`) but Signal/Noise/Gaps claims are not stored in a machine-readable format that enables later comparison.

2. **Compare predictions to outcomes.** Star snapshots (`data/snapshots/`) could provide ground truth (did "Signal" repos actually grow? did "Noise" repos fade?), but:
   - The snapshots directory is currently empty
   - No script compares week N predictions against week N+4 star deltas
   - No "scorecard" format exists

3. **Attribute improvement to reskill changes.** Without a baseline quality metric tracked over time, there's no way to know if reskill actually improved anything.

### Is star snapshot data sufficient?

**Partially.** Star snapshots can validate:
- ✅ "This repo is gaining momentum" (compare stars at week N vs N+4)
- ✅ "This is hype" (stars plateau or decline)
- ❌ "This gap matters" (absence can't be validated by stars alone)
- ❌ "This trend is durable" (needs signals beyond stars — commits, forks, adoption)

### Missing data collection for better learning:

1. **Prediction registry:** Machine-readable claims from each analysis (repo X will grow, theme Y is noise) with confidence scores
2. **Outcome tracker:** Script that revisits predictions after N weeks using snapshot data
3. **Quality trend log:** `quality_score` from each analysis plotted over time
4. **External validation signals:** Fork counts, contributor growth, dependency adoption — richer than stars alone

---

## 5. Persistence

### Will learnings survive across sessions and workflow runs?

| Question | Answer | Evidence |
|----------|--------|----------|
| Are `.squad/` files committed after reskill? | ❌ **No** | No commit step for `.squad/` exists in the workflow |
| Does the workflow have `contents: write`? | ✅ **Yes** | `analyze` job has `contents: write`; would need same for reskill job |
| Will Copilot CLI have `.squad/` state during reskill? | ✅ **Yes** (if checkout is full) | The workflow checks out with `fetch-depth: 0` — `.squad/` is in the repo |
| Is `run-counter.txt` persisted? | ❌ **No** | File doesn't exist; no commit step would save it |
| Are reskill outputs persisted? | ❌ **No** | `.squad/reskill/` directory doesn't exist; no commit step |

### The persistence chain is broken at every link:

```
Run → Counter increment → [NOT COMMITTED] → Lost
Reskill → wisdom.md update → [NOT COMMITTED] → Lost  
Reskill → skill extraction → [NO DIRECTORY] → Lost
Reskill → report → [NOT COMMITTED] → Lost
```

**The workflow only commits:** `data/raw/`, `data/snapshots/`, `data/analyzed/`, `content/weekly/`. Squad state changes are invisible to git.

---

## 6. Gap Analysis

### Critical Gaps (Learning will not happen without these)

| # | Gap | Impact | Proposed Fix | New Issue? |
|---|-----|--------|--------------|------------|
| G1 | No reskill job in workflow | Reskill never triggers | Add `reskill` job to `crawl-and-publish.yml` with counter check | Part of #15 |
| G2 | No `run-counter.txt` | Counter check fails on first run | Initialize file; add increment in crawl job commit step | Part of #15 |
| G3 | No `.squad/` commit step | All learning outputs lost between runs | Add commit step for `.squad/` after reskill | Part of #14 |
| G4 | No `.squad/skills/` directory | Skill extraction has nowhere to write | Create directory with `.gitkeep` | Part of #14 |
| G5 | No `.squad/reskill/` directory | Reskill reports have nowhere to go | Create directory with `.gitkeep` | Part of #14 |
| G6 | Empty `wisdom.md` | No heuristics available for first reskill to build on | Seed with initial heuristics from analysis-spec patterns | Part of #14 |
| G7 | Analysis prompt ignores learned state | Even if wisdom exists, it's not injected into analysis | Add `{{WISDOM_CONTENT}}` variable to `prompts/analyze-weekly.md` | **Yes — new issue** |

### Serious Gaps (Learning will be shallow without these)

| # | Gap | Impact | Proposed Fix | New Issue? |
|---|-----|--------|--------------|------------|
| G8 | No hindsight validation | Can't measure if past calls were right | Build `scripts/validate_predictions.py` that compares analysis claims to snapshot deltas | **Yes — new issue** |
| G9 | No prediction registry format | Claims aren't machine-readable for later comparison | Define frontmatter or sidecar format for testable predictions | **Yes — new issue** |
| G10 | Star snapshots empty | No ground-truth data for validation | Ensure crawler commits snapshots (workflow does commit `data/snapshots/` — crawler must produce them) | Bug in #6 or crawl schedule |
| G11 | No quality trend tracking | Can't measure improvement over time | Add `scripts/track_quality_trend.py` reading `quality_score` from all `data/analyzed/` files | Part of #14 |
| G12 | Reskill prompt too vague | "Assess what's working" is underspecified | Write structured reskill prompt in `prompts/reskill.md` with specific review criteria | Part of #14 |

### Minor Gaps (Nice-to-have for deeper learning)

| # | Gap | Impact | Proposed Fix | New Issue? |
|---|-----|--------|--------------|------------|
| G13 | No fork/contributor signals in snapshots | Star-only validation is one-dimensional | Extend crawler to capture fork_count and contributor_count in snapshots | Future enhancement |
| G14 | No reskill PR review gate | Reskill could degrade squad state | Reskill outputs as PR (not direct commit) for human review | Design decision needed |
| G15 | No rollback mechanism | Bad reskill can't be undone | Git history provides implicit rollback; add explicit `squad revert-reskill` | Future enhancement |

---

## 7. Recommendations

### Immediate (must-do before claiming "SquadScope learns")

1. **Implement Issue #15 — Run counter:**
   - Create `.squad/run-counter.txt` initialized to `0`
   - Add counter increment to the `crawl` job commit step
   - Include `.squad/run-counter.txt` in the git add paths

2. **Implement Issue #14 — Reskill job:**
   - Add a `reskill` job in `crawl-and-publish.yml` (conditional on counter % 5 == 0)
   - Write a structured prompt at `prompts/reskill.md` that reads squad state, past analyses, and star snapshots
   - Create `.squad/skills/` and `.squad/reskill/` directories
   - Add commit step that pushes `.squad/` changes

3. **Close the prompt feedback loop (new issue needed):**
   - Add `{{WISDOM_CONTENT}}` and `{{SKILLS_CONTENT}}` variables to `prompts/analyze-weekly.md`
   - The analysis fallback script must read and inject these
   - Without this, learning has no effect on future analysis quality

4. **Seed `wisdom.md`:**
   - Extract initial heuristics from the analysis-spec's editorial dimensions
   - This gives the first reskill something to refine rather than starting from zero

### Near-term (should do within 2 reskill cycles)

5. **Build hindsight validation (new issue):**
   - Script that loads analysis from week N, loads star snapshots from week N+4
   - Scores whether "Signal" repos grew, "Noise" repos stalled
   - Produces a scorecard that feeds into the next reskill

6. **Define prediction registry format (new issue):**
   - Frontmatter additions: `predictions: [{repo, direction, confidence}]`
   - Machine-readable claims enable automated scoring

7. **Verify star snapshots are being produced:**
   - The crawler has snapshot logic but `data/snapshots/` is empty
   - Likely because no successful cron run has occurred yet
   - Validate on first manual `workflow_dispatch` run

### Architecture constraints to respect:

- Reskill MUST NOT modify `data/raw/` or `data/analyzed/` (immutability contract)
- Reskill outputs should be PR-based if they modify prompts or specs (governance)
- Counter must be atomic and race-safe under concurrency controls already in the workflow

---

## Conclusion

SquadScope's learning differentiator is currently a **design document, not a system**. The architecture is well-thought-out (counter mechanism, squad state as context, reskill outputs), but the implementation gap is total: zero lines of reskill code exist in the workflow or scripts. Three new issues are needed beyond #14 and #15 to close the feedback loop completely. Until at minimum #14, #15, and the prompt injection gap (G7) are resolved, SquadScope does not learn — it merely remembers what humans and squad sessions manually append to history files.
