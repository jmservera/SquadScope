# fix(repository): align explorer filters and release evidence

## Summary

* Fixed `/repo/` filtering so nonmatching repository cards are actually hidden
  and visible results match selected filters, URL state, and announced counts.
* Added accessible copy feedback, reduced-motion behavior, and browser evidence
  for disclosures, focus, touch, mobile, and 200% equivalent viewport states.
* Added a revision-bound Phase 5 release-candidate schema, validator, evidence
  record, tests, and CI gate.

The frozen product candidate is
`31ab98c99c7175adf83d62321dd6f592ab54a5fd`, with product-tree digest
`25f9fcc8a8b8e41c4a073f3eb057ca0b55ada6c23b3901896d4838863ddb75cf`.
The release remains blocked on final named owner review and genuine live
screen-reader evidence for DRF-05; this PR does not claim sponsor GO or
deployment readiness.

## Validation

* 1,670 Python tests; 16 focused candidate-validator tests
* Ruff lint and format
* Two Node unit tests
* Hugo, Pagefind, and internal-link checks
* 172 affected repository, accessibility, and revision-tagged visual scenarios
* Checkov, Zizmor, and Bandit security gates

## Related issue

Related: jmservera/SquadScope#594

## External-facing changes

- [ ] If this PR ships copy or graphics that will appear OUTSIDE this repo (social posts, launch blog, announcements, press), I tagged @squad:nibbler for an RAI sign-off before merge.
