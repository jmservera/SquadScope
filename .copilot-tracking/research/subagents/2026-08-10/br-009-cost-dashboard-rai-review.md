# Nibbler RAI/Safety Acceptance Review — BR-009 Cost Dashboard (commit 9af3026d, PR #697)

## Scope

Post-merge, read-only Responsible AI / safety review of the rendering-side change on `origin/main` at `9af3026d` ("feat(about): render BR-009 reconciled cost schema, retire placeholder total (#697)"). Confirmed the working tree matches `origin/main` exactly for all four reviewed files (zero-line diff), so file contents below are what actually shipped.

Reviewed:
- layouts/partials/cost-dashboard.html
- tests/test_cost_dashboard_rendering.py
- assets/css/common/cost-dashboard.css
- data/schemas/cost-summary.schema.json

Out of scope (per task): scripts/generate_cost_summary.py (not part of this PR).

## Verdict

**ACCEPT WITH FOLLOW-UPS.**

The fail-closed design is real and well-tested for the failure modes it targets (missing file, legacy schema, missing/malformed nested fields, stale/future/non-conforming timestamps, non-numeric `maximum_age_days`, non-object root, malformed identity entries). Disclosure copy is honest, accessibility floor is met, and there is no dark pattern in how the unavailable state is presented. However, there is one validation gap that lets a specific class of malformed-but-"present" data render as a trustworthy dollar figure, contradicting the partial's own stated invariant. It should be closed before the (out-of-scope) generator script starts actually populating `reconciliation.status` with anything other than `"reconciled"`.

## 1. Hallucination / fabrication-risk assessment

**Primary finding — `reconciliation.status` is required to exist but its value is never checked.**

The design principle in this task explicitly lists "unreconciled" as a condition that must fail closed. The schema and the partial both require `reconciliation.status` to be *present* (`$nestedRequired` includes `status` for the `reconciliation` key, cost-summary.schema.json requires the `reconciliation` object generically). But nowhere in `cost-dashboard.html` is the *value* of `reconciliation.status` compared against `"reconciled"` (or any allow-list). It isn't even rendered to the user (only `input_records`, `accepted_records`, `billable_records` are shown in the `<details>` block).

Consequence: a payload with `"reconciliation": {"status": "partial", "input_records": N, "accepted_records": N, "billable_records": N}` (or `"failed"`, `"unreconciled"`, anything) — all other required top-level/nested keys present, fresh `generated_at`, schema_version `"1.0.0"` — passes every current check and renders the full dashboard, including a large, high-contrast dollar total in `--color-accent` at `--text-4xl`, exactly as if the data were successfully reconciled. This is the one place where "looks structurally valid" and "is honest/trustworthy" diverge, and the code only checks the former.

No test fixture exercises this (`VALID_SUMMARY.reconciliation.status` is always `"reconciled"`; none of the nine failure-mode tests vary `status`'s value, only presence of keys elsewhere). The JSON schema doesn't constrain it either — `reconciliation` is declared as bare `{"type": "object"}` with no `required`/`enum`, so there's no schema-level backstop.

Severity: medium-high impact (a headline monetary figure could be shown as reconciled when the source data explicitly says it isn't) but currently unexercised since the generator (out of scope) is the only thing that would produce such a payload, and its actual behavior is unknown from this review.

**Secondary finding — `totals.cost`/`totals.input_tokens`/`totals.output_tokens` use `isset` + `| default 0`, which doesn't distinguish "missing" from "present but null".**

```
{{- $totalCost := float ($totals.cost | default 0) -}}
{{- $inputTokens := int ($totals.input_tokens | default 0) -}}
{{- $outputTokens := int ($totals.output_tokens | default 0) -}}
```

The nested-key guard upstream only checks `isset $nested "cost"` (key existence), not non-nullness. A JSON `"cost": null` (or `input_tokens`/`output_tokens`: null) would satisfy `isset`, then fall through the `default 0` fallback and render as a literal `"0.00"` — precisely the "fabricated 0.00" failure mode the code's own comment says it's guarding against ("a malformed entry must fail closed rather than show a fabricated 0.00"). The existing test `test_about_page_shows_unavailable_when_nested_field_missing` only covers outright *key deletion* (`del payload["totals"]["cost"]`), not an explicit `null` value, so this gap has no regression coverage.

This is narrower than the `reconciliation.status` gap: the JSON schema types these fields as `number`/`integer` (not nullable), so a schema-conformant generator can never emit `null` here — the exposure only exists if the deployed file was hand-edited or corrupted post-schema-validation. Worth closing for defense-in-depth consistency with the rest of the guard logic, but not urgent.

**Not a concern:** `generated_at` and `provenance.maximum_age_days` are both explicitly guarded against non-scalar/non-string shapes and null-like values before use (confirmed via `reflect.IsMap`/`reflect.IsSlice` checks plus regex matching on the stringified value), and have dedicated passing tests (`_for_non_numeric_maximum_age_days`, `_when_generated_at_is_an_object`, `_for_non_string_generated_at`). Text fields rendered without a `default` (`currency`, `pricing_basis`, `provenance.ledger`, `covered_period.start/end`, per-identity fields) fail closed correctly for missing keys (covered by tests) and, if ever `null`, would render blank rather than a fabricated *number* — lower severity than the cost/token case.

**Injection note (adjacent to expertise, not a blocker):** pipeline-sourced strings (`model`, `pricing_basis`, `provenance.ledger`, identity fields) are rendered via Hugo's Go `html/template`-based auto-escaping, so standard HTML/script injection through these fields should be neutralized by the templating layer itself; no custom `safeHTML`/`safeHTMLAttr` escapes-bypass was found in this partial. Not verified against the generator's actual output, since that script is out of scope.

## 2. Disclosure / honesty assessment — pass

> "Cost data is not currently available. The reconciled pipeline cost is generated from accepted, workflow-identified ledger runs and republishes automatically once fresh data clears the freshness and reconciliation checks."

- States plainly that data is absent — no fake placeholder, no silently-omitted section, no "0.00"/"—" masquerading as a real value in this path.
- Explains the mechanism (freshness + reconciliation checks) rather than a vague "something went wrong," which is informative without being alarmist.
- Doesn't promise a specific timeline or falsely imply an active incident response; doesn't apologize in a minimizing way that would suggest the absence is trivial.
- No discrepancy found between what's claimed and what's true, other than the `reconciliation.status` gap in §1, which is a rendering-logic bug rather than a copy/honesty problem — the copy itself is not the issue.

## 3. Accessibility floor — pass

- `aria-labelledby="cost-dashboard-title"` on the `<section>` in **both** the unavailable and available states, pointing at a real, always-rendered `<h2 id="cost-dashboard-title">`. Correct pattern.
- Table (`accepted identities`) has `<caption>`, `<thead><th scope="col">`, and `<th scope="row">` per body row — correct semantic structure (WCAG 1.3.1).
- Horizontally-scrollable table wrapper (`.cost-dashboard__table-wrap[tabindex="0"]`) plus a `:focus-visible` outline — correct keyboard-accessible-reflow pattern for wide tables (WCAG 1.4.10 / 2.1.1).
- `<details>/<summary>` used for the reconciliation/exclusions breakdown — native, accessible disclosure widget; not used to hide the core total or the unavailable-state message (see §4).
- `<time datetime="...">` machine-readable alongside human-formatted display — good practice, no concern.
- Contrast check on `--color-text-muted` (the only non-default text color used in the unavailable state, and for secondary labels generally): computed contrast ratio against `--color-surface`/`--color-bg` is ≈8:1 in both the light palette (`#4B524F` on `#FFFFFF`) and the dark palette (`#B7BAB6` on `#1C2124`) — both comfortably clear WCAG AA (4.5:1) for normal text and approach/exceed AAA. No contrast concern for the disclosure message or any muted label.
- Minor, non-blocking nit: `aria-label="Cost summary"` / `aria-label="Cost data provenance"` on plain `<div>`/`<dl>` wrappers without a visible heading is a legitimate ARIA grouping pattern, not a violation — flagged only as a style observation, not a finding.

## 4. Dark-pattern check — pass

- The unavailable-state card uses the identical container styling (border, background, padding, border-radius) as the success-state card — same visual weight, not shrunk, not recolored to look inert/greyed-out as a whole.
- The section heading (`Pipeline transparency` / `AI pipeline cost`) is rendered at full contrast and normal weight in both states — unchanged between success/failure, so the presence of a problem isn't visually signaled as "less important."
- The disclosure sentence is the *only* content besides the header in the unavailable state — it cannot be missed, is not truncated, and is not tucked inside the collapsed `<details>` element (that element is reserved for the optional reconciliation/exclusions breakdown in the *success* state only).
- The muted color (`--color-text-muted`) applied to the disclosure paragraph is the same treatment used site-wide for ordinary secondary/supporting text (header intro sentences, `dt` labels, table captions) — i.e., it's the established "this is supporting prose, not a headline number" convention, not a mechanism invented specifically to de-emphasize a failure. Combined with the ≈8:1 contrast ratio (§3), this does not rise to a dark pattern (no visual minimization of a real problem into near-invisibility).
- No countdown, no dismiss-and-forget interaction, no confirm-shaming language, no pre-checked opt-in, no forced continuity pattern present in either state.

## Concerns / gaps found (ranked)

1. **[Medium-high, primary]** `reconciliation.status` is required to be *present* but its *value* is never validated against `"reconciled"` (or any allow-list); an "unreconciled"/"partial"/"failed" payload with all other keys populated would still render a full, confident-looking dollar total. This directly contradicts the stated design principle that "unreconciled" data must fail closed, and has no test coverage.
2. **[Low-medium]** `totals.cost` / `totals.input_tokens` / `totals.output_tokens` use `isset` (key existence) + `| default 0`, so a present-but-`null` value for any of these would render a fabricated `"0.00"`/`"0"` rather than failing closed — the exact failure mode the surrounding guard comments say they prevent. Schema types these as non-nullable, so exposure requires a schema-noncompliant file, but there's no defensive check or regression test for it.
3. **[Informational]** `data/schemas/cost-summary.schema.json` declares `provenance`, `covered_period`, `exclusions`, and `reconciliation` as bare `{"type": "object"}` with no `required`/`properties`/`enum` constraints, so schema validation alone would not catch either gap above (or a malformed `covered_period.start/end`, non-numeric `exclusions.*`, etc.). The partial's own template-level guards are currently the *only* backstop for those nested shapes — worth tightening the schema too, in coordination with whoever owns the generator PR.

## Recommended follow-up items

- Add a value check: fail closed unless `reconciliation.status == "reconciled"` (or an explicit allow-list), with a new test fixture (`status: "partial"`/`"failed"`/`"unreconciled"` + all other keys present) asserting the unavailable state renders.
- Add an explicit non-nil/non-null check (or `reflect.IsMap`/`reflect.IsSlice`/emptiness-of-type check consistent with the existing `generated_at`/`maximum_age_days` guards) for `totals.cost`, `totals.input_tokens`, `totals.output_tokens` before the `default 0` fallback, plus a regression test with those fields explicitly set to JSON `null`.
- Tighten `data/schemas/cost-summary.schema.json` to add `required`/`properties`/enum constraints on `reconciliation` (`status` enum), `covered_period` (date-time/string `start`/`end`), and `exclusions` (non-negative integers) so schema validation itself catches these cases at generation time, not just at render time — this should be coordinated with the (out-of-scope) `scripts/generate_cost_summary.py` PR.

## Clarifying questions (not answerable from this review alone)

- Does `scripts/generate_cost_summary.py` (out of scope for this PR) ever emit a `reconciliation.status` other than `"reconciled"` in a payload that is otherwise fully populated (i.e., is finding #1 reachable in practice today, or only a theoretical defense-in-depth gap)? This determines whether follow-up #1 should be treated as urgent/pre-next-generator-release or as routine hardening.
