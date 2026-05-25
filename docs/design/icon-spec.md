# SquadScope Icon Specification

**Date:** 2026-05-25  
**Author:** Calculon (Designer)  
**Status:** Proposed

---

## 1. Concept

### Brand Essence

**SquadScope** = Scope/spotlight on squads/trends from GitHub

The name combines:
- **Squad:** Teams, communities, groups of developers
- **Scope:** Observation, focus, analysis lens

The icon should convey: **focused observation of developer activity** — not generic surveillance, but intentional signal extraction from noise.

### Candidate Concepts

#### A. Radar Sweep (Recommended)

A stylized radar display with a sweep line, representing continuous scanning of the GitHub landscape. Simple, geometric, works at all sizes.

**Pros:**
- Unique (not the typical eye/magnifier)
- Implies ongoing monitoring, not one-time search
- Clean geometry scales from 16px to 512px
- No licensing concerns

**Cons:**
- Could read as "military" if overdone

#### B. Signal Pulse

A rising waveform with peaks, representing trend signals emerging from data. Modern, data-forward.

**Pros:**
- Directly maps to "trend analysis"
- Distinctive shape

**Cons:**
- May look like audio/music at small sizes
- Less immediate brand recognition

#### C. Bracketed Focus

Square brackets `[ ]` with a dot/star inside, representing focused extraction of a single signal.

**Pros:**
- Typographic, works with wordmark
- Developer-friendly aesthetic

**Cons:**
- May be too abstract
- Brackets are overused in developer tooling

### Recommendation: **Radar Sweep (A)**

The radar concept best captures continuous observation without being a cliché eye or magnifier. It's geometric, works at all sizes, and differentiates SquadScope from generic developer tools.

---

## 2. Icon Design

### Primary Icon SVG

The following SVG is optimized for clarity at 16×16px while looking refined at 512×512px. It uses `viewBox` for scalability and no external fonts.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Background circle (radar field) -->
  <circle cx="32" cy="32" r="28" stroke="currentColor" stroke-width="3" fill="none"/>
  
  <!-- Inner ring -->
  <circle cx="32" cy="32" r="18" stroke="currentColor" stroke-width="2" fill="none" opacity="0.5"/>
  
  <!-- Center ring -->
  <circle cx="32" cy="32" r="8" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
  
  <!-- Center dot -->
  <circle cx="32" cy="32" r="3" fill="currentColor"/>
  
  <!-- Sweep line (the key differentiator) -->
  <path d="M32 32 L32 4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  
  <!-- Signal blip on the sweep -->
  <circle cx="32" cy="12" r="4" fill="currentColor"/>
</svg>
```

**Characteristics:**
- Uses `currentColor` for automatic light/dark mode adaptation
- Stroke-based design for clarity at small sizes
- Concentric circles create depth without fills
- Sweep line at 12 o'clock position for visual balance
- Signal blip represents "detected trend"

### Light Mode Version

For contexts requiring explicit colors:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <circle cx="32" cy="32" r="28" stroke="#1A1A1A" stroke-width="3" fill="none"/>
  <circle cx="32" cy="32" r="18" stroke="#1A1A1A" stroke-width="2" fill="none" opacity="0.5"/>
  <circle cx="32" cy="32" r="8" stroke="#1A1A1A" stroke-width="2" fill="none" opacity="0.3"/>
  <circle cx="32" cy="32" r="3" fill="#1A1A1A"/>
  <path d="M32 32 L32 4" stroke="#0066CC" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="12" r="4" fill="#0066CC"/>
</svg>
```

### Dark Mode Version

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <circle cx="32" cy="32" r="28" stroke="#E8E8E8" stroke-width="3" fill="none"/>
  <circle cx="32" cy="32" r="18" stroke="#E8E8E8" stroke-width="2" fill="none" opacity="0.5"/>
  <circle cx="32" cy="32" r="8" stroke="#E8E8E8" stroke-width="2" fill="none" opacity="0.3"/>
  <circle cx="32" cy="32" r="3" fill="#E8E8E8"/>
  <path d="M32 32 L32 4" stroke="#4DA3FF" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="12" r="4" fill="#4DA3FF"/>
</svg>
```

### Monochrome Version (for Safari pinned tab)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <circle cx="32" cy="32" r="28" stroke="black" stroke-width="3" fill="none"/>
  <circle cx="32" cy="32" r="18" stroke="black" stroke-width="2" fill="none" opacity="0.5"/>
  <circle cx="32" cy="32" r="8" stroke="black" stroke-width="2" fill="none" opacity="0.3"/>
  <circle cx="32" cy="32" r="3" fill="black"/>
  <path d="M32 32 L32 4" stroke="black" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="12" r="4" fill="black"/>
</svg>
```

### Simplified Version (for 16×16 favicon)

At 16×16, detail is lost. Use this simplified version:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none">
  <!-- Outer circle -->
  <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5" fill="none"/>
  
  <!-- Center dot -->
  <circle cx="8" cy="8" r="1.5" fill="currentColor"/>
  
  <!-- Sweep line with blip -->
  <path d="M8 8 L8 1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="8" cy="2.5" r="1.5" fill="currentColor"/>
</svg>
```

---

## 3. Color Guidance

The icon uses design tokens from the redesign proposal:

| Context | Radar Rings | Sweep Line & Blip |
|---------|-------------|-------------------|
| Light mode | `--text` (#1A1A1A) | `--accent` (#0066CC) |
| Dark mode | `--text` (#E8E8E8) | `--accent` (#4DA3FF) |
| Monochrome | black | black |

For single-color contexts (favicon.ico, Safari pinned tab), use only the primary text color.

---

## 4. Asset List

Amy should produce the following assets from the SVG specs above:

### Favicons

| File | Size | Format | Notes |
|------|------|--------|-------|
| `favicon.ico` | 16×16, 32×32, 48×48 | ICO (multi-size) | Use simplified SVG for 16px |
| `favicon-16x16.png` | 16×16 | PNG | Simplified version |
| `favicon-32x32.png` | 32×32 | PNG | Primary icon |
| `favicon.svg` | Scalable | SVG | currentColor version for modern browsers |

### Apple Touch Icons

| File | Size | Format | Notes |
|------|------|--------|-------|
| `apple-touch-icon.png` | 180×180 | PNG | Add 10% padding, solid `--bg` background |

### Safari Pinned Tab

| File | Size | Format | Notes |
|------|------|--------|-------|
| `safari-pinned-tab.svg` | Scalable | SVG | Monochrome black only |

### Header Logo

| File | Size | Format | Notes |
|------|------|--------|-------|
| `logo.svg` | Height 28-32px | SVG | Icon + "SquadScope" wordmark |
| `logo-icon-only.svg` | 32×32 | SVG | For mobile/compact contexts |

### Social/OG Images

| File | Size | Format | Notes |
|------|------|--------|-------|
| `og-image.png` | 1200×630 | PNG | See spec below |
| `og-image-weekly.png` | 1200×630 | PNG | Template for weekly articles |

---

## 5. OG Image Specification

### Default OG Image (`og-image.png`)

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                                                                │
│     ┌─────┐                                                    │
│     │ ◎   │   SquadScope                                       │
│     └─────┘                                                    │
│                                                                │
│            Weekly tech signal from GitHub                      │
│                                                                │
│                                                                │
│            jmservera.github.io/SquadScope                      │
│                                                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Specs:**
- Size: 1200×630px
- Background: `--bg` (#FAFAFA light / #0D0D0D dark — produce both)
- Icon: 120px height, left of wordmark
- Wordmark: Inter Bold, 72px, `--text`
- Tagline: Inter Regular, 32px, `--text-muted`
- URL: Inter Regular, 24px, `--text-muted`
- All content vertically centered, left-aligned with 80px margin

### Weekly Article OG Template (`og-image-weekly.png`)

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  WEEK 22 · MAY 2026                          [SquadScope ◎]   │
│                                                                │
│  Supply-Chain Scanners, Skills                                 │
│  Economies, and GitHub's                                       │
│  Star-Farm Flood                                               │
│                                                                │
│            ┌─────────────────────────────────────────┐         │
│            │ Repos: 420  ·  Stars: 16.5M  ·  Top: ⭐ │         │
│            └─────────────────────────────────────────┘         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Specs:**
- Size: 1200×630px
- Background: Gradient from `--bg` to `--surface`
- Eyebrow: Inter Medium, 24px, `--accent`
- Title: Inter Bold, 56px, `--text`, max 3 lines
- Metrics bar: Rounded rect with `--accent-muted` background
- Logo: Top-right corner, 48px height

---

## 6. Generation Prompt (Optional)

If a richer hero/OG image is desired using an image generation model, here is a prompt:

```
A minimalist digital illustration of a radar screen showing concentric circles
on a dark background (#0D0D0D). A single bright blue (#4DA3FF) sweep line
extends from the center to the top of the screen. Where the sweep line meets
the outer ring, there is a glowing blue dot representing a detected signal.
The style is clean, geometric, and technical — like a modernized NORAD display
but elegant and editorial. No text, no labels, just the pure radar visualization.
Aspect ratio 1200x630 for social media preview.
```

**Note:** The hand-coded SVG icon above is the canonical brand mark. Any generated imagery should complement it, not replace it.

---

## 7. Implementation Checklist

- [ ] Export all PNG assets at 2x resolution for Retina displays
- [ ] Test favicon.ico in Chrome, Firefox, Safari, Edge
- [ ] Verify safari-pinned-tab.svg renders correctly in Safari
- [ ] Add icon references to `hugo.toml` under `[params]`
- [ ] Update `layouts/partials/head.html` with favicon links
- [ ] Test OG images with Twitter Card Validator and Facebook Debugger

---

## 8. File Locations

All assets should be placed in:

```
static/
├── favicon.ico
├── favicon.svg
├── favicon-16x16.png
├── favicon-32x32.png
├── apple-touch-icon.png
├── safari-pinned-tab.svg
├── logo.svg
├── logo-icon-only.svg
├── og-image.png
├── og-image-dark.png
└── og-image-weekly-template.png
```

Update `hugo.toml`:

```toml
[params.label]
  icon = "logo-icon-only.svg"
  iconHeight = 28
```

---

*Specification by Calculon · 2026-05-25*
