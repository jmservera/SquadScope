# Amy decision inbox — generate and deploy workflow

- **Date:** 2026-05-18T13:20:07.067+02:00
- **Issue:** #11 — Implement generate-and-deploy workflow for GitHub Pages

## Proposed decision

Keep `.github/workflows/deploy-site.yml` for push-to-main deployments, and let `.github/workflows/crawl-and-publish.yml` own the weekly automation path end-to-end.

### Implementation details

1. The weekly workflow should run `crawl → analyze → generate → deploy` in a single pipeline.
2. The `generate` stage should write the weekly Hugo page into `content/weekly/YYYY/WNN.md` using archetype-compatible frontmatter derived from `data/analyzed/YYYY-WNN-summary.md`.
3. The generated weekly page should be committed back to the default branch before the Pages build so future archive builds retain previously published weekly content.
4. The publish artifact should be built with Hugo 0.161.1 and Pagefind, then deployed with `actions/deploy-pages@v4` under the `github-pages` environment.
