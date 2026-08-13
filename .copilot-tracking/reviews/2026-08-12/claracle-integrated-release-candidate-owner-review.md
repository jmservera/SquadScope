# Claracle Integrated Release Candidate Owner Review

## Review Boundary

* Candidate: `8af4f4a4332db005924fc4281b9a32d039d80d5a`
* Baseline: `f9fb5d88fefde9b6143adda2d57e20d18f6b5e25`
* Reviewers: Amy, Fry, Leela, Hermes, URL, Nibbler, Zapp, and Farnsworth
* Overall disposition: Block

This review did not simulate or claim DRF-05 live assistive-technology
acceptance.

## Blocking Findings

1. Closed findings did not require nonempty revision-bound evidence or named
   owner dispositions.
2. DRF-05 could not record structured findings, severity, and unresolved work.
3. Candidate ancestry validation was incompatible with repository squash
   merges.
4. Evidence paths were not checked for existence or content hashes.
5. Sponsor, rollback, deployment, and outcome lifecycle transitions were
   under-enforced.
6. DRF-02 lacked expanded-state captures and sequential keyboard evidence.
7. DRF-03 failure guidance was announced but not visibly available.
8. DRF-04 used a narrow viewport as a proxy rather than exercising 200% page
   zoom.

## Dispositions

| Reviewer | Disposition | Primary boundary |
|---|---|---|
| Amy | Block | DRF-02 and DRF-03 interaction evidence |
| Fry | Block | Keyboard, visible guidance, and zoom evidence |
| Leela | Block | Fail-open release contract |
| Hermes | Block | Unsupported GO/deployed states |
| URL | Block | Squash compatibility and evidence provenance |
| Nibbler | Block | Incomplete live-review attestation model |
| Zapp | Block | Rollback and outcome enforcement |
| Farnsworth | Block | Acceptance claims exceeded retained proof |

## Required Disposition

The candidate is invalidated. Reopen affected P01-P03 markers, remediate every
automatable finding, rerun validation, freeze a new product candidate, and
repeat named owner review. DRF-05 remains blocked until a genuine named human
review is supplied.

## Replacement Pre-Freeze Review

Candidate `9d5e55d9c47882b4a6349f9d7cad595972a06e2c` was reviewed after the first
remediation pass but before its evidence record was frozen. The named review
confirmed the interaction, lifecycle, evidence-hash, and chronology
remediations, then returned **Block** for:

1. the expected pre-freeze absence of exact-candidate evidence and
   dispositions;
2. a real integrity gap where the current product digest was checked without
   independently computing the declared candidate commit's digest; and
3. missing OBJ-02 baseline and objective thresholds in the delayed outcome
   contract.

The validator now computes both the declared candidate revision digest and the
current product digest. Both must equal the recorded digest. The outcome
contract now retains the approved 0-session/149-impression/0-click baseline,
the 250-organic-session complete-month target, and the 15-top-20-query
six-month target. Candidate `9d5e55d` was never frozen, so no evidence or
disposition was invalidated by these fixes.

## Candidate 31ab98c Final Review

The final named review confirmed:

* Amy and Fry pass the automated portions of DRF-01 through DRF-04;
* Hermes passes security;
* URL passes CI and release provenance;
* Nibbler passes prompt-injection, AI-safety, and truthful-attestation review;
* Farnsworth passes editorial and data-integrity claims;
* Leela and Zapp found one remaining evidence-only severity-2 defect: the
  250-organic-session target was assigned to D+28 rather than the approved
  six-month window.

The outcome record now keeps D+28 as a migration/organic evidence review and
applies both approved OBJ-02 thresholds at six months: at least 250 organic
sessions per complete 28-day month and at least 15 queries in the top 20.

No automatable severity-1 or severity-2 finding remains. DRF-03 live
announcement confirmation and DRF-05 live keyboard/screen-reader acceptance
remain genuine named-human blockers.

## Candidate 3271024 PR-Fix Review

Candidate `31ab98c` was invalidated before human review after Copilot identified
three valid PR findings. Candidate
`327102410d5ade6048408463a27872cfd0bedc60` includes race-safe copy feedback,
order-independent repository URL assertions, accurate blocker wording, and
detailed DRF-03/DRF-05 human-review instructions.

The repeated exact-candidate review confirms:

* Amy and Fry pass the automated portions of DRF-01 through DRF-04;
* Leela passes functional correctness and the release-state boundary;
* Hermes passes Bandit, Checkov, and workflow-security review;
* URL passes CI and revision-bound evidence provenance;
* Nibbler passes truthful live-AT attestation and prompt-safety review;
* Zapp and Farnsworth pass outcome, editorial, and data-integrity claims.

No automatable severity-1 or severity-2 finding remains. DRF-03 live
announcement confirmation and DRF-05 live keyboard/screen-reader acceptance
remain genuine named-human blockers.

---

## Candidate 6ba13b5 — Deferred/Waiver Freeze Review (2026-08-13)

### Leela (Architecture / Release-State Boundary)

**Disposition**: Pass

The deferred/waiver design is architecturally sound and fail-closed:
- `deferred` is a distinct first-class status; no finding is fabricated as closed.
- `live_at_review: null` is preserved — no fake pass exists anywhere.
- The waiver is mandatory, schema-validated, and bound to the exact candidate SHA.
- Expiry is enforced unconditionally by the validator: once the waiver clock runs
  out, CI blocks every PR repo-wide until the finding is genuinely resolved or
  the waiver is explicitly renewed. This provides teeth without fabrication.
- The GO-blocking calculation correctly exempts deferred findings (they can only
  reach that state if all waiver checks pass, so this is safe).
- Issue #714 tracks the genuine resolution path.

**Pending reviews**: Hermes (security), Fry (test), Nibbler (AI safety) reviews
are pending as a follow-up on this candidate. Their dispositions are not written
here — each owner must supply their own.
