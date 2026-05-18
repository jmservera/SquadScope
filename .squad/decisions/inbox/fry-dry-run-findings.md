# Fry Dry-Run Findings

Date: 2026-05-18T10:59:10.800+02:00
Issue: #7

## Findings worth tracking

1. **Pin Hugo version everywhere validation runs.** The local environment defaulted to `hugo v0.123.7`, but the repository theme requires `v0.146.0+`. Dry-run validation only succeeded after using `hugo v0.161.1`.
2. **Trending requires historical state.** `data/raw/2026-W21.json` contains no usable `stars_gained` values in `trending_repos`, so the current output is popularity-biased rather than momentum-based.
3. **Crawler filtering still lets through too much off-mission content.** The sample week contains multiple exploit, bypass, cheat, and game-mod repositories high in the “new” ranking. That needs stronger filtering or a quality gate before auto-publish.
4. **Analyze/generate contract needs one final source of truth.** The PRD weekly page shape and the approved analyzer quality-gate contract are close, but not identical, so the generator step should explicitly define how analyzed markdown maps into publishable Hugo content.
