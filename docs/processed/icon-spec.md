# SquadScope Icon Spec

> **Archived (processed) — historical reference.** This spec is implemented (issues #175 and #176 closed). Retained for design history; the shipped icon/favicon assets are the live source of truth.

## Concept

**Robot with binoculars.** A minimalist robot head holding binoculars to its eyes — keeps the "scope/observation" metaphor (binoculars = signal-spotting) and grounds it in a friendly editorial personality (this site IS auto-generated weekly trend analysis; the robot is honest about that).

Replaces the previously-proposed Radar Sweep concept. Radar was visually generic and the SquadScope homepage briefly used "SS" as a text monogram in the header, which the user flagged as risking accidental association with the Nazi SS rune. This icon resolves both: original visual identity + no letterforms that can be misread.

## Visual

### Master SVG (64×64 viewBox, hand-coded original)

The robot design uses a rounded-square head with a single antenna (critical for "robot" read at small sizes), two circular binocular eyepieces connected by a bridge (differentiates from googly eyes), a subtle mouth grille for personality, and optional shoulder hints for anchoring.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Antenna: single post with ball tip (robot identifier at small sizes) -->
  <line x1="32" y1="4" x2="32" y2="14"/>
  <circle cx="32" cy="4" r="3" fill="currentColor" stroke="none"/>
  
  <!-- Robot head: rounded square, slightly trapezoid feel -->
  <rect x="10" y="14" width="44" height="36" rx="8" ry="8"/>
  
  <!-- Left binocular eyepiece -->
  <circle cx="22" cy="30" r="9"/>
  <circle cx="22" cy="30" r="4" fill="currentColor" stroke="none"/>
  
  <!-- Right binocular eyepiece -->
  <circle cx="42" cy="30" r="9"/>
  <circle cx="42" cy="30" r="4" fill="currentColor" stroke="none"/>
  
  <!-- Binocular bridge (the key "binoculars" differentiator) -->
  <line x1="31" y1="30" x2="33" y2="30" stroke-width="4"/>
  
  <!-- Mouth grille: two horizontal lines for friendly robot personality -->
  <line x1="26" y1="42" x2="38" y2="42"/>
  <line x1="28" y1="45" x2="36" y2="45"/>
  
  <!-- Shoulder chassis hints at bottom (anchors the head) -->
  <path d="M14 54 L14 58 Q14 62 18 62 L46 62 Q50 62 50 58 L50 54" stroke-width="2"/>
</svg>
```

**Design rationale:**
- **Antenna with ball tip:** Single antenna reads cleanest at 16px; the filled ball adds weight for visibility
- **Rounded-square head:** Differentiates from circular emoji faces; the 8px corner radius keeps it friendly
- **Binocular eyepieces:** 9px radius outer ring + 4px filled pupil gives depth; the 4px-thick bridge is the "this is binoculars" cue
- **Mouth grille:** Two lines suggest a speaker/vent — friendly robot without being cartoonish
- **Shoulder chassis:** 8px-tall curved shape anchors the floating head, gives editorial gravitas
- **Stroke-based:** 2.5px stroke works at all sizes; no fills except pupils and antenna ball

### At 16×16 (favicon-optimized)

Simplified for pixel clarity: thinner strokes, reduced elements, merged bridge into eyepiece proximity.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Antenna -->
  <line x1="8" y1="1" x2="8" y2="3"/>
  <circle cx="8" cy="1" r="1" fill="currentColor" stroke="none"/>
  
  <!-- Head -->
  <rect x="2" y="3" width="12" height="10" rx="2" ry="2"/>
  
  <!-- Binocular eyepieces (close together = implied bridge) -->
  <circle cx="5.5" cy="7" r="2"/>
  <circle cx="5.5" cy="7" r="0.75" fill="currentColor" stroke="none"/>
  <circle cx="10.5" cy="7" r="2"/>
  <circle cx="10.5" cy="7" r="0.75" fill="currentColor" stroke="none"/>
  
  <!-- Mouth (single line at this scale) -->
  <line x1="6" y1="11" x2="10" y2="11"/>
  
  <!-- Shoulder hint -->
  <path d="M4 13 L4 14.5 Q4 15 5 15 L11 15 Q12 15 12 14.5 L12 13" stroke-width="1"/>
</svg>
```

Scales cleanly — silhouette reads as robot with binoculars at favicon size.

## Design tokens

- **Color:** `var(--color-text)` via `currentColor` — auto-adapts to light/dark themes
- **Stroke width (64px):** 2.5px main elements, 4px binocular bridge, 2px shoulder
- **Stroke width (16px):** 1.5px main elements, 1px shoulder
- **Corner radius:** 8px head (64px), 2px head (16px)

## Silhouette safety check (the lesson from the SS incident)

Confirmed against ADL Hate on Display + general silhouette test:
- ❌ Not a rune — no angular lightning-bolt shapes
- ❌ Not a letterform that could be misread — no S, SS, or similar
- ❌ Not a sun/cross variant — rounded rectangle, not radial
- ❌ Not a hand gesture — clearly a robot head
- ✅ At 16px the silhouette reads as: **robot face with antenna and prominent circular "eyes"**

The binoculars read as large round eyes at small sizes, which reinforces the "observing" concept. The antenna is the critical robot identifier.

## Asset list (Amy implements in Phase 6 #175)

PNG sizes needed for full favicon + PWA support (per faviconbuilder.com guide):

| File | Size | Format | Notes |
|------|------|--------|-------|
| `favicon.ico` | 16, 32, 48 multi-size | ICO | Use 16px SVG variant |
| `favicon-16x16.png` | 16×16 | PNG | From 16px SVG |
| `favicon-32x32.png` | 32×32 | PNG | From master SVG |
| `favicon-96x96.png` | 96×96 | PNG | From master SVG |
| `apple-touch-icon.png` | 180×180 | PNG | Master SVG + 10% padding + `--bg` fill |
| `android-chrome-192x192.png` | 192×192 | PNG | Master SVG + padding |
| `android-chrome-512x512.png` | 512×512 | PNG | Master SVG + padding |
| `mstile-150x150.png` | 150×150 | PNG | Master SVG centered |
| `safari-pinned-tab.svg` | scalable | SVG | Monochrome, single path conversion |
| `og-image.png` | 1200×630 | PNG | Robot motif as anchor; Amy designs composition |
| `site.webmanifest` | — | JSON | References 192 + 512 sizes |

All generated from the master SVG above.

## Header inline usage

The header (`layouts/partials/header.html`) uses this SVG INLINE (no img tag) so it can take `currentColor` from the surrounding text color. The `.site-brand__mark` container provides the border/background; the SVG just renders inside at 100% of the container's dimensions.

Example markup (see matching PR diff):
```html
<span class="site-brand__mark" aria-hidden="true">
  <svg viewBox="0 0 64 64" width="100%" height="100%" fill="none" stroke="currentColor" ...>
    <!-- robot SVG paths -->
  </svg>
</span>
```

---

*Specification by Calculon · 2026-05-25 (redo — replaces radar sweep concept)*
