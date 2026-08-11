# feat(repositories): execute approved URL migration

## External-facing changes

- [ ] If this PR ships copy or graphics that will appear OUTSIDE this repo (social posts, launch blog, announcements, press), I tagged @squad:nibbler for an RAI sign-off before merge.

## Summary

- Built the evidence-backed repository explorer and immutable 274-URL migration map.
- Retained `/repo/` plus 10 approved profiles, added one permanent redirect, and retired 262 URL forms.
- Migrated both production workflows from GitHub Pages to atomic Cloudflare Pages Direct Upload.
- Added fail-closed migration, rollback, freshness, rendered-link, and live HTTP checks.

## Validation

- [x] `ruff check .`
- [x] `ruff format --check .`
- [x] `pytest -q tests/` (1,629 passed; two expected warnings)
- [x] `hugo --cleanDestinationDir --minify`
- [x] Local Cloudflare Pages 200/301/404 migration probes
- [x] Checkov 3.2.533 (902 passed, 0 failed, 6 skipped)
- [x] Zizmor changed-workflow scan (no medium/high findings)
- [ ] Required hosted CI, including pinned Zizmor 1.27.0
- [ ] Copilot review of the latest head
- [ ] Human review and unresolved-thread clearance

## Deployment

Do not merge until the `claracle` Cloudflare Pages project, `cloudflare-pages`
GitHub environment, scoped Cloudflare secrets, custom domains, DNS/TLS cutover,
production probes, and rollback evidence are complete.

## Related issues

None. This implements BR-003 under the Claracle post-relaunch consolidation plan.
