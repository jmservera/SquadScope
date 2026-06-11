---
name: "editorial-site-redesign"
description: "Pattern for redesigning an editorial website with design tokens, phased rollout, and clear handoff"
domain: "design"
confidence: "low"
source: "earned"
---

## Context

When redesigning an editorial or content-heavy website, the challenge is creating a distinctive visual identity while maintaining readability and shipping incrementally. This skill captures the pattern used for SquadScope's 2026 redesign.

## Patterns

1. **Study peer references first**: Fetch 3-4 comparable sites. Capture: layout pattern, typography, color, navigation, density, article treatment. Note what fits and what doesn't.

2. **Lock tokens before components**: Define CSS custom properties (colors, spacing, typography, shadows, radii) as the foundation. Components depend on tokens; tokens don't depend on components.

3. **Phase: tokens → chrome → content → polish**:
   - Phase 1: Design tokens + typography
   - Phase 2: Header + footer (site chrome)
   - Phase 3: Home page layout
   - Phase 4: Article/content layouts
   - Phase 5: Secondary components (dashboards, callouts)
   - Phase 6: Brand assets (icons, OG images)

4. **Specs replace mockups**: Without Figma, write component specs as prose + ASCII diagrams. Include: structure, spacing values, color tokens, states (hover, active, focus), responsive behavior.

5. **Icon from concept**: Start with a narrative (what does the brand represent?), propose 2-3 concepts, recommend one, then hand-code SVG. Use `currentColor` for automatic light/dark adaptation.

6. **WCAG AA from the start**: Verify contrast ratios when defining palette, not after implementation.

## Examples

- `docs/processed/redesign-proposal-2026-05.md` — full proposal with token tables, ASCII layouts, component specs
- `docs/processed/icon-spec.md` — icon narrative, SVG code, asset checklist

## Anti-Patterns

- Designing components before establishing tokens (leads to inconsistency)
- Big-bang redesign (ship nothing until everything is done)
- Copying reference sites literally (lose distinctiveness)
- Skipping accessibility verification (expensive to fix later)
- Using external fonts without fallbacks (FOUT, performance)
