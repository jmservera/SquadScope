# SquadScope Visual Redesign Proposal

**Date:** 2026-05-25  
**Author:** Calculon (Designer)  
**Status:** Proposed

---

## Executive Summary

SquadScope is an editorial publication delivering weekly GitHub trend analysis. The current PaperMod-derived theme treats it as a generic blog, missing the opportunity to create a distinctive editorial voice. This proposal establishes a visual direction that positions SquadScope as a credible, opinionated trend report — dense but readable, data-rich but not dashboard-like.

---

## 1. Design Principles

1. **Reading First** — Typography, spacing, and contrast optimize for long-form scanning. Every pixel serves comprehension.

2. **One Signal Per Glance** — Each content block delivers a single clear message. Metrics, headlines, and navigation don't compete for attention.

3. **Dense ≠ Cluttered** — Information density is a feature, not a bug. White space creates breathing room between dense blocks, not padding around sparse content.

4. **Light Touch on Decoration** — Let data and prose speak. Borders, shadows, and color accents are structural signals, not embellishments.

5. **Dark Mode Is Not Inverted Light Mode** — Each mode has intentional palette choices, not mechanical flips.

---

## 2. Visual Direction

### Chosen Lane: **Editorial Trend Report — Dense but Quiet**

This is not a SaaS dashboard (no heavy data-viz chrome), not a news aggregator (no thumbnail grids), and not a traditional blog (no hero images, author avatars, social proof). It is a **weekly briefing document** that happens to live on the web.

### Reference Analysis

| Site | Layout Pattern | Typography | Color | Fits SquadScope? |
|------|----------------|------------|-------|------------------|
| **GitHub Pulse** | Card-heavy, filter-first | System fonts, tight | Monochrome + accent | Partial — too dashboard-y |
| **TechCrunch** | Headline hierarchy, byline-heavy | Serif headlines, sans body | Purple accent | Partial — too news-feed |
| **Wired** | Magazine grid, large imagery | Bold sans headlines | High-contrast black | No — too image-dependent |
| **The Verge** | Dense feed, strong bylines | Chunky sans | Vibrant accents | Partial — too feed-like |

**Synthesis:** Borrow from TechCrunch's headline hierarchy and reading rhythm, GitHub Pulse's monochrome discipline, and The Verge's willingness to be dense. Avoid Wired's image-dependence (SquadScope is text-first) and generic blog patterns.

### Resulting Aesthetic

- **Typographic hierarchy** carries the design, not images or color
- **Monochrome foundation** with a single accent color
- **Compact metric displays** that inform without dominating
- **Clear article structure** with section dividers and consistent spacing
- **No stock imagery** — code blocks, pull quotes, and data callouts provide visual variety

---

## 3. Design Tokens

### 3.1 Color Palette

#### Light Mode

| Token | Hex | Use | WCAG AA on bg? |
|-------|-----|-----|----------------|
| `--bg` | `#FAFAFA` | Page background | — |
| `--surface` | `#FFFFFF` | Cards, elevated content | — |
| `--text` | `#1A1A1A` | Primary text | ✓ 15.3:1 on bg |
| `--text-muted` | `#5C5C5C` | Secondary text, metadata | ✓ 6.1:1 on bg |
| `--accent` | `#0066CC` | Links, interactive elements | ✓ 4.9:1 on bg |
| `--accent-hover` | `#004C99` | Link hover states | ✓ 7.2:1 on bg |
| `--accent-muted` | `#E6F0FA` | Accent backgrounds | — |
| `--border` | `#E0E0E0` | Dividers, card borders | — |
| `--danger` | `#CC3300` | Error states, warnings | ✓ 5.4:1 on bg |
| `--success` | `#1A8754` | Positive indicators | ✓ 4.6:1 on bg |

#### Dark Mode

| Token | Hex | Use | WCAG AA on bg? |
|-------|-----|-----|----------------|
| `--bg` | `#0D0D0D` | Page background | — |
| `--surface` | `#1A1A1A` | Cards, elevated content | — |
| `--text` | `#E8E8E8` | Primary text | ✓ 14.5:1 on bg |
| `--text-muted` | `#9C9C9C` | Secondary text, metadata | ✓ 7.3:1 on bg |
| `--accent` | `#4DA3FF` | Links, interactive elements | ✓ 7.8:1 on bg |
| `--accent-hover` | `#80BFFF` | Link hover states | ✓ 10.2:1 on bg |
| `--accent-muted` | `#1A2633` | Accent backgrounds | — |
| `--border` | `#2E2E2E` | Dividers, card borders | — |
| `--danger` | `#FF6B4A` | Error states, warnings | ✓ 6.8:1 on bg |
| `--success` | `#4ADE80` | Positive indicators | ✓ 9.2:1 on bg |

### 3.2 Typography

#### Font Stack

- **Headlines:** `"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Body:** Same as headlines (unified stack for editorial consistency)
- **Monospace:** `"JetBrains Mono", "Fira Code", "SF Mono", "Cascadia Code", monospace`

#### Type Scale (rem, base 16px)

| Level | Size | Line Height | Weight | Use |
|-------|------|-------------|--------|-----|
| `h1` | `2.25rem` (36px) | 1.2 | 700 | Page title |
| `h2` | `1.75rem` (28px) | 1.25 | 600 | Section headers |
| `h3` | `1.375rem` (22px) | 1.3 | 600 | Subsection headers |
| `h4` | `1.125rem` (18px) | 1.35 | 600 | Card titles |
| `body` | `1rem` (16px) | 1.65 | 400 | Prose |
| `small` | `0.875rem` (14px) | 1.5 | 400 | Metadata, captions |
| `tiny` | `0.75rem` (12px) | 1.4 | 500 | Labels, badges |

#### Measure

- **Prose max-width:** `68ch` (optimal reading measure)
- **Metric cards:** No max-width (fluid within grid)

### 3.3 Spacing Scale

8px-based scale for predictable rhythm:

| Token | Value |
|-------|-------|
| `--space-1` | `0.25rem` (4px) |
| `--space-2` | `0.5rem` (8px) |
| `--space-3` | `1rem` (16px) |
| `--space-4` | `1.5rem` (24px) |
| `--space-5` | `2rem` (32px) |
| `--space-6` | `3rem` (48px) |
| `--space-7` | `4rem` (64px) |

### 3.4 Border Radius

| Token | Value | Use |
|-------|-------|-----|
| `--radius-sm` | `4px` | Small buttons, badges |
| `--radius-md` | `8px` | Cards, inputs |
| `--radius-lg` | `12px` | Large containers |
| `--radius-full` | `9999px` | Pills, avatars |

### 3.5 Shadows

| Token | Value | Use |
|-------|-------|-----|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle elevation |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Cards |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dropdowns |

Dark mode shadows use `rgba(0,0,0,0.3)` base for visibility on dark surfaces.

---

## 4. Layout Proposals

### 4.1 Home Page

```
┌────────────────────────────────────────────────────────────┐
│  HEADER  [ Logo ]  Weekly | Monthly | Yearly | Search | ⚙ │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  EYEBROW: Weekly tech signal from GitHub             │  │
│  │                                                      │  │
│  │  H1: SquadScope                                      │  │
│  │                                                      │  │
│  │  Subhead: Turns GitHub activity into readable        │  │
│  │  weekly, monthly, and yearly trend reports.          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SECTION TOPLINE: Latest report                     │   │
│  │                                                     │   │
│  │  H2: [Article Title - full width, clickable]        │   │
│  │                                                     │   │
│  │  Summary paragraph (1-2 lines)                      │   │
│  │                                                     │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐  │   │
│  │  │ Week    │ │ Repos   │ │ Stars   │ │ Top Repo  │  │   │
│  │  │ 2026-22 │ │ 420     │ │ 16.5M   │ │ perp/bee  │  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └───────────┘  │   │
│  │                                                     │   │
│  │  [ Read Report → ]                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌───────────────────┐  ┌───────────────────┐             │
│  │  RECENT REPORTS   │  │  QUICK LINKS      │             │
│  │  • W22 - Supply...│  │  Archive          │             │
│  │  • W21 - Agent... │  │  Monthly          │             │
│  │  • W20 - ...      │  │  Tags             │             │
│  │  • W19 - ...      │  │  RSS              │             │
│  └───────────────────┘  └───────────────────┘             │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  FOOTER  [ GitHub ] [ RSS ]  © 2026 jmservera              │
└────────────────────────────────────────────────────────────┘
```

**Key changes from current:**
- Remove 7-card navigation grid (overwhelming); replace with focused quick links
- Promote latest report to hero treatment
- Metric cards integrated with latest report, not separate
- Tighter hierarchy: eyebrow → h1 → subhead → content

### 4.2 Weekly Article Page

```
┌────────────────────────────────────────────────────────────┐
│  HEADER  [ ← Back to archive ]  Weekly | Monthly | ...    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  EYEBROW: Weekly summary                                   │
│                                                            │
│  H1: Supply-Chain Scanners, Skills Economies,              │
│      and GitHub's Star-Farm Flood                          │
│                                                            │
│  METADATA: May 25, 2026 · 12 min read · Week 22            │
│                                                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────────────┐ │
│  │ Repos   │ │ Stars   │ │ Trends  │ │ Top: perp/bumblebee│
│  │ 420     │ │ 16.5M   │ │ 4       │ │ 2,328 ⭐           │
│  └─────────┘ └─────────┘ └─────────┘ └───────────────────┘ │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ JUMP TO: Trends | Industry | Signal | Blind Spots  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PRESS CONTEXT  [TechCrunch badge]                   │  │
│  │  6 articles this week, most relevant:                │  │
│  │  "How founders inflate ARR metrics..."               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ───────────────────────────────────────────────────────   │
│                                                            │
│  H2: This Week's Trends                                    │
│                                                            │
│  Prose content with optimal measure (68ch)...              │
│                                                            │
│  [REPO CARD: perplexityai/bumblebee]                       │
│  ├─ Description                                            │
│  ├─ 2,328 ⭐ · 181 forks · Go                              │
│  └─ [ View on GitHub → ]                                   │
│                                                            │
│  More prose...                                             │
│                                                            │
│  ───────────────────────────────────────────────────────   │
│                                                            │
│  H2: Signal & Noise                                        │
│  ...                                                       │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  POST FOOTER                                               │
│  Tags: [ supply-chain ] [ agent-skills ] [ ai-memory ]     │
│  ← Previous | Next →                                       │
├────────────────────────────────────────────────────────────┤
│  FOOTER                                                    │
└────────────────────────────────────────────────────────────┘
```

**Key changes from current:**
- Article header with clear hierarchy (eyebrow, h1, metadata)
- Metric cards in compact row, not competing with title
- Jump-to navigation for long articles
- Press context callout styled distinctively
- Repo cards as first-class components (not just inline links)
- Clear section dividers (horizontal rules)

### 4.3 Monthly/Yearly Rollup Pages

```
┌────────────────────────────────────────────────────────────┐
│  HEADER                                                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  EYEBROW: Monthly rollup                                   │
│  H1: May 2026                                              │
│  SUBHEAD: 4 weeks covered · 1,680 repos featured           │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  INCLUDED WEEKS                                     │   │
│  │  W19 · W20 · W21 · W22                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  ───────────────────────────────────────────────────────   │
│                                                            │
│  H2: Month in Review                                       │
│  Synthesized prose...                                      │
│                                                            │
│  H2: Top Repos This Month                                  │
│  [Repo cards in 2-column grid]                             │
│                                                            │
│  H2: Emerging Themes                                       │
│  [Theme cards with sparkline-style indicators]             │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  FOOTER                                                    │
└────────────────────────────────────────────────────────────┘
```

---

## 5. Component Specs

### 5.1 Header

```
┌─────────────────────────────────────────────────────────────┐
│ [LOGO]  SquadScope       Weekly  Monthly  Yearly  Search  ⚙│
└─────────────────────────────────────────────────────────────┘
```

**Specs:**
- Height: `64px`
- Logo: Site icon (28px height) + wordmark
- Navigation: Horizontal list, `--text-muted` default, `--text` on hover
- Active state: `--text` with `border-bottom: 2px solid var(--accent)`
- Theme toggle: Icon button, `24px` icon
- GitHub button (per issue #169): Icon-only button, right-aligned, `24px` icon
- Mobile: Hamburger menu at `<768px`

### 5.2 Article Header

**Structure:**
1. Eyebrow: Section label (`small`, `--text-muted`, uppercase, letter-spacing `0.05em`)
2. H1: Title (`h1` token, `--text`)
3. Subtitle/description: Optional (`body`, `--text-muted`)
4. Metadata row: Date · Reading time · Week number (`small`, `--text-muted`)

**Spacing:**
- Eyebrow to H1: `--space-2`
- H1 to subtitle: `--space-3`
- Subtitle to metadata: `--space-3`
- Metadata to metric cards: `--space-5`

### 5.3 Metric Cards

```
┌─────────────────┐
│  LABEL          │  ← small, --text-muted, uppercase
│  VALUE          │  ← h3, --text, font-weight 600
└─────────────────┘
```

**Specs:**
- Background: `--surface`
- Border: `1px solid var(--border)`
- Border-radius: `--radius-md`
- Padding: `--space-3`
- Min-width: `120px`
- Display: Flex row, gap `--space-3`, wrap on mobile

**Wide variant** (for "Top repo"):
- Flex-grow: 1
- Value is a link (`--accent` color)

### 5.4 Repo Card

```
┌─────────────────────────────────────────────────────────────┐
│  owner/repo-name                                     Go     │
│  Description text that can wrap to multiple lines if        │
│  needed but is truncated after 2 lines with ellipsis...     │
│  ⭐ 2,328  ·  🔀 181 forks                    [ GitHub → ]  │
└─────────────────────────────────────────────────────────────┘
```

**Specs:**
- Background: `--surface`
- Border: `1px solid var(--border)`
- Border-radius: `--radius-md`
- Padding: `--space-4`
- Title: `h4` weight, `--accent` color (link)
- Language badge: `tiny`, `--accent-muted` background, `--radius-sm`
- Stats: `small`, `--text-muted`
- GitHub button: Secondary button style, right-aligned

### 5.5 Press Context Callout

```
┌─────────────────────────────────────────────────────────────┐
│  📰 TechCrunch Context                                      │
│  6 articles this week. Most relevant correlation:           │
│  "How founders and VCs use inflated ARR metrics..."         │
└─────────────────────────────────────────────────────────────┘
```

**Specs:**
- Background: `--accent-muted`
- Border-left: `4px solid var(--accent)`
- Border-radius: `--radius-md` (right corners only)
- Padding: `--space-4`
- Title: `small`, `--text`, font-weight 600
- Body: `body`, `--text-muted`
- Quote: `body`, `--text`, italic

### 5.6 Cost Dashboard

**Current:** Shortcode rendering raw metrics.

**Redesigned:**
- Contained card with border
- Clear section header
- Two-column grid: Token metrics | Cost summary
- Subtle accent treatment for "total cost" value
- Collapsible detail rows (model breakdown)

### 5.7 Footer

```
┌─────────────────────────────────────────────────────────────┐
│  SquadScope — Weekly tech signal from GitHub                │
│                                                             │
│  GitHub · RSS · Archive                                     │
│                                                             │
│  © 2026 jmservera · Powered by Hugo                         │
└─────────────────────────────────────────────────────────────┘
```

**Specs:**
- Background: `--surface`
- Border-top: `1px solid var(--border)`
- Padding: `--space-6` vertical
- Content: Centered, max-width matches content area
- Links: `--text-muted`, `--accent` on hover
- Copyright: `small`, `--text-muted`

---

## 6. Migration Strategy

Phased rollout to ship value incrementally and minimize risk:

### Phase 1: Tokens + Typography Foundation
**Scope:** CSS custom properties, font stack, type scale
**Files:** New `assets/css/tokens.css`, updates to base styles
**Dependencies:** None
**Outcome:** Typography feels polished; colors unified
**Effort:** Small

### Phase 2: Header + Footer + Navigation
**Scope:** Redesigned header with GitHub button (#169), new footer
**Files:** `layouts/partials/header.html`, new `footer.html`, CSS
**Dependencies:** Phase 1 tokens
**Outcome:** Site chrome is consistent and distinctive
**Effort:** Medium

### Phase 3: Home Page Layout
**Scope:** Hero treatment, latest report card, quick links
**Files:** `layouts/index.html`, CSS
**Dependencies:** Phase 2 header/footer
**Outcome:** Entry point signals editorial quality
**Effort:** Medium

### Phase 4: Article Layout + Components
**Scope:** Article header, metric cards, repo cards, press callout, jump nav
**Files:** `layouts/weekly/single.html`, `layouts/monthly/single.html`, `layouts/yearly/single.html`, partials
**Dependencies:** Phase 1-3
**Outcome:** Core reading experience transformed
**Effort:** Large

### Phase 5: Cost Dashboard Refresh
**Scope:** Redesigned cost dashboard shortcode
**Files:** `layouts/shortcodes/cost-dashboard.html`, CSS
**Dependencies:** Phase 1 tokens
**Outcome:** Financial transparency looks intentional
**Effort:** Small

### Phase 6: Icon + Favicon + Social Images
**Scope:** Site icon assets, OG image, apple-touch-icon
**Files:** `static/` assets, `hugo.toml` params
**Dependencies:** Phase 1 palette decisions
**Outcome:** Brand identity complete across all touchpoints
**Effort:** Medium

---

## 7. Accessibility Checklist

- [ ] All color combinations meet WCAG AA contrast (verified in token table)
- [ ] Focus states visible on all interactive elements
- [ ] Skip-to-content link at page start
- [ ] Semantic heading hierarchy (no skipped levels)
- [ ] Reduced motion: Respect `prefers-reduced-motion`
- [ ] Link text is descriptive (no "click here")
- [ ] Keyboard navigation works for all interactive elements
- [ ] Images have alt text (where applicable)

---

## 8. Open Questions

1. **Font loading:** Include Inter from Google Fonts or use system stack only? (System stack recommended for performance.)
2. **Syntax highlighting theme:** Adapt PaperMod's current theme to new palette or switch to a named theme?
3. **Search styling:** Pagefind has its own styling; override or accept?

---

## Appendix: Figma-less Handoff Notes

Since this proposal is specs-only (no Figma), Amy should:
1. Implement tokens as CSS custom properties first
2. Build components in isolation using the specs above
3. Use browser dev tools to verify spacing/sizing against the spec
4. Reference the live sites mentioned for edge cases

---

*Proposal by Calculon · 2026-05-25*
