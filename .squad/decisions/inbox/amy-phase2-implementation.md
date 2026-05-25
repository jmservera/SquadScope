# Amy Phase 2 Implementation Notes

Date: 2026-05-25
Author: Amy
Status: Implemented in PR branch

## Decisions

- Override PaperMod chrome at the project layer (`layouts/partials/header.html`, `layouts/partials/footer.html`) rather than editing the theme submodule.
- Add `layouts/_default/baseof.html` solely to place the skip-to-content link before the cached header and give the main landmark `id="main-content"`.
- Keep the primary nav intentionally scoped to Weekly, Monthly, Yearly, and About for Phase 2; archive/search/taxonomy links remain in the page body and footer where already present.
- Use a native `<details>` disclosure for mobile navigation so the collapsed menu remains keyboard reachable without adding new JavaScript.

## Implications

Future chrome work should continue to extend root layouts and tokenized CSS. If PaperMod changes its base template, compare against this override before upgrading the theme.
