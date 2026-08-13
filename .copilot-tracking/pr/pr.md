# fix(repository): align explorer filters and release evidence

## Summary

* Fixed `/repo/` filtering so nonmatching repository cards are actually hidden
  and visible results match selected filters, URL state, and announced counts.
* Added accessible copy feedback, reduced-motion behavior, and browser evidence
  for disclosures, focus, touch, mobile, and 200% equivalent viewport states.
* Added a revision-bound Phase 5 release-candidate schema, validator, evidence
  record, tests, and CI gate.

The replacement product candidate is
`c7b08f1f8552ce15f84d12a202e70af6b80ab249`. Exact-candidate automated and
named-owner review passes. Sponsor `jmservera` granted GO after explicitly
deferring DRF-03 and DRF-05 under the time-bounded waiver tracked by
jmservera/SquadScope#714. This is not a passing live-AT result.

## Validation

* 1,670 Python tests; 16 focused candidate-validator tests
* Ruff lint and format
* Two Node unit tests
* Hugo, Pagefind, and internal-link checks
* 172 affected repository, accessibility, and revision-tagged visual scenarios
* Checkov, Zizmor, and Bandit security gates

## Related issue

Related: jmservera/SquadScope#594

## Required DRF-03/DRF-05 live screen-reader review

Use the `site-preview` artifact linked by the preview-bot comment on this PR.
Serve the downloaded artifact over HTTP, then test candidate
the current `candidate_sha` in the release record. Record the reviewer name, date,
operating system/version, browser/version, screen reader/version, findings with
severity, disposition, and unresolved work.

### DRF-03 — copy announcements

1. Open `/charts/embeddable-rankings/` and navigate by keyboard to **Copy embed
   snippet**.
2. Activate it and confirm the screen reader announces “Embed snippet copied to
   the clipboard,” focus stays on the button, and its label returns to **Copy
   embed snippet**.
3. Block clipboard permission in the browser, reload, activate the button
   again, and confirm “Copy failed. Select and copy the embed snippet manually”
   is both spoken and visible while focus remains on the button.

### DRF-05 — live keyboard and screen-reader scenarios

1. Verify headings, landmarks, labels, navigation order, and visible focus on
   the homepage, an article, `/repo/`, a ranking page, and the embed page.
2. On `/repo/`, operate search, topic, language, lifecycle, and observation
   period filters by keyboard; confirm the result count and empty/reset states
   are announced and match the visible cards.
3. Open repository context/provenance disclosures on ranking and embed pages;
   confirm their content is spoken, Escape dismisses them, and focus remains on
   the trigger.
4. At 200% browser zoom, repeat navigation and disclosure checks and confirm
   content and controls are not clipped or obscured.
5. Record every finding as severity 1–4. The disposition may pass only when no
   severity-1 or severity-2 finding remains unresolved.

### Evidence response template

```text
Reviewer:
Reviewed at (UTC):
Candidate SHA: use the current candidate_sha in data/release/claracle-v1.1-release-candidate.json
Operating system/version:
Browser/version:
Screen reader/version:
DRF-03 announcement: Pass/Block
DRF-05 scenarios completed:
Findings and severity: None, or list each finding
Disposition: Pass/Block
Unresolved work: None, or list each item
```

## External-facing changes

- [ ] If this PR ships copy or graphics that will appear OUTSIDE this repo (social posts, launch blog, announcements, press), I tagged @squad:nibbler for an RAI sign-off before merge.
