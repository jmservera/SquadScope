# Design Direction: Editorial Trend Report

**Date:** 2026-05-25  
**Author:** Calculon (Designer)  
**Status:** Proposed

## Decision

**Visual Direction:** Editorial Trend Report — Dense but Quiet

This positions SquadScope as a credible, opinionated weekly briefing rather than a generic blog or SaaS dashboard. Typography carries the design; images and color accents are supporting actors.

## Rationale

After studying GitHub Pulse, TechCrunch, Wired, and The Verge:
- GitHub Pulse is too dashboard-like for editorial content
- TechCrunch provides good headline hierarchy but is too news-feed
- Wired is too image-dependent for text-first analysis
- The Verge shows density can work if hierarchy is clear

SquadScope is closer to a weekly briefing document than any of these. The design borrows TechCrunch's reading rhythm, GitHub Pulse's monochrome discipline, and The Verge's willingness to be dense — while avoiding their weaknesses.

## Token Summary

**Palette:** Monochrome foundation with single accent (#0066CC light, #4DA3FF dark). All combinations WCAG AA verified.

**Typography:** Inter system stack for headlines and body. JetBrains Mono for code. Type scale from 0.75rem (tiny) to 2.25rem (h1). Optimal prose measure 68ch.

## Phase Plan

1. Tokens + Typography Foundation
2. Header + Footer + Navigation
3. Home Page Layout
4. Article Layout + Components
5. Cost Dashboard Refresh
6. Icon + Favicon + Social Images

Each phase ships independently. Tokens must land first; other phases have light dependencies.

## Icon

Radar sweep concept — concentric circles with sweep line and signal blip. Represents continuous scanning. Hand-coded SVG, no external fonts, under 2KB. Uses currentColor for automatic mode adaptation.

## References

- `docs/design/redesign-proposal-2026-05.md`
- `docs/design/icon-spec.md`
- Issues #170-#177
