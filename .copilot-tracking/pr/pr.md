# fix(repository): align explorer filters and release evidence

## Summary

* Fixed `/repo/` filtering so nonmatching repository cards are actually hidden
  and visible results match selected filters, URL state, and announced counts.
* Added accessible copy feedback, reduced-motion behavior, and browser evidence
  for disclosures, focus, touch, mobile, and 200% equivalent viewport states.
* Added a revision-bound Phase 5 release-candidate schema, validator, evidence
  record, tests, and CI gate.

The frozen product candidate is
`8af4f4a4332db005924fc4281b9a32d039d80d5a`. The release remains blocked on
named owner review and genuine live screen-reader evidence for DRF-05; this PR
does not claim sponsor GO or deployment readiness.

## Validation

* 1,663 Python tests
* Ruff lint and format
* Two Node unit tests
* Hugo, Pagefind, and internal-link checks
* 157 browser acceptance tests plus four CI-configured analytics scenarios
* 76 revision-tagged visual checks
* Checkov, Zizmor, and Bandit security gates

## Related issue

Related: jmservera/SquadScope#594

## External-facing changes

- [ ] If this PR ships copy or graphics that will appear OUTSIDE this repo (social posts, launch blog, announcements, press), I tagged @squad:nibbler for an RAI sign-off before merge.
