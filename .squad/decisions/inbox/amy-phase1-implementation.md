# Amy Phase 1 Design Foundation Implementation

**Date:** 2026-05-25  
**Author:** Amy (Frontend Developer)  
**Status:** Implemented

## Decision

Phase 1 tokens and typography are implemented as a Hugo asset-pipeline foundation without changing page layouts.

## File locations

- `assets/css/tokens.css` is the design-system entry point for color, type, spacing, radius, shadow, and line-height tokens.
- `layouts/partials/head.html` loads Inter and JetBrains Mono from Google Fonts using preload + stylesheet links, then includes `tokens.css` before the PaperMod-compatible CSS bundle.
- `assets/css/core/theme-vars.css` maps PaperMod legacy variables to SquadScope tokens so existing templates continue to render.
- `assets/css/core/reset.css` applies the base reset, body typography, heading scale, and monospace stack.
- `assets/css/common/*.css`, `assets/css/extended/squadscope.css`, and `assets/css/badges.css` consume the token aliases while preserving existing layouts.

## How to extend

Future phases should add new tokens to `assets/css/tokens.css` first, then consume them through component or layout CSS. Keep semantic tokens stable (`--color-*`, `--text-*`, `--space-*`) and add component-specific variables only when a pattern repeats across multiple publishing surfaces.

## Gotchas

PaperMod lives as a submodule, so theme CSS changes should be copied into root-level `assets/css/` overrides rather than editing `themes/PaperMod` directly. Hugo resolves these project assets through the existing asset pipeline while leaving the third-party theme clean.
