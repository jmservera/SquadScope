---
title: Claracle Experience Design Brief
description: Proposed visual and interaction direction for the Claracle post-relaunch experience
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: concept
keywords:
  - claracle
  - design system
  - data observatory
  - user experience
estimated_reading_time: 7
---

## Approval Status

Pending Calculon and sponsor approval. This brief defines the implementation
candidate for BR-001; it does not authorize a visual rollout.

## Subject, Audience, And Job

Claracle is an evidence observatory for changes in open-source technology. Its
primary audience is technology decision-makers comparing signals, timing, and
source strength rather than browsing a general technology publication.

The experience must answer three questions in order:

1. What changed?
2. Why does the evidence matter now?
3. Where can the reader inspect the underlying weekly, monthly, yearly,
   repository, and ranking evidence?

## Proposed Direction: Field Notebook

The visual language should resemble a carefully maintained technical field
notebook: precise grids, visible evidence labels, compact annotations, and
editorial typography. It should not resemble a generic card dashboard, a SaaS
marketing page, or a dark terminal interface.

The first viewport should show Claracle as the product name, the strongest
current evidence, and a visible continuation into the next evidence band. The
page should favor scanning and comparison over decorative containers.

## Typography

* Display and editorial headings: `Source Serif 4`, with Georgia as the local
  fallback
* Interface and body text: `Atkinson Hyperlegible Next`, with Verdana as the
  local fallback
* Data labels and identifiers: `IBM Plex Mono`, with monospace as the fallback
* No font size scales with viewport width
* Letter spacing remains zero
* Long repository names wrap without shrinking controls or changing grid tracks

The selected hosted or bundled font source requires licensing and performance
review before implementation. The fallback stack must remain usable when fonts
fail to load.

## Color Tokens

| Token | Proposed value | Purpose |
|-------|----------------|---------|
| `--claracle-paper` | `#f7f6f2` | Primary reading surface |
| `--claracle-ink` | `#18201f` | Primary text and structural rules |
| `--claracle-signal` | `#006b5f` | Current evidence, links, and selected state |
| `--claracle-alert` | `#b33a2b` | Material decline, stale state, and errors |
| `--claracle-cobalt` | `#275dad` | Comparative series and secondary actions |
| `--claracle-gold` | `#b47a00` | Provisional or review-required evidence |

The palette combines neutral reading surfaces with green, red, blue, and gold
semantic roles. Every state also uses text, shape, or position so color is never
the only encoding. Final values require WCAG contrast verification in light and
dark modes.

## Spacing And Geometry

* Base spacing unit: 4px
* Reading rhythm: 8px, 12px, 16px, 24px, 32px, and 48px
* Cards, when a repeated item genuinely needs a frame: no more than 6px radius
* Evidence bands and page sections: unframed, full-width divisions with strong
  horizontal rules and a constrained inner grid
* Controls: stable dimensions with 44px minimum pointer targets
* Data tables and charts: fixed grid tracks or documented responsive breakpoints
  so labels, status text, and loading states do not shift the surrounding layout

## Layout Concept

The shared shell uses a twelve-column desktop evidence grid and a four-column
mobile grid. A narrow evidence rail carries period, freshness, source, and status
metadata. The main reading column carries summaries and analysis. Comparative
data spans the full grid when labels or trends require room.

Page-specific jobs:

| View | Primary job | Required first evidence |
|------|-------------|-------------------------|
| Homepage | Explain the strongest current changes and route readers to evidence | Current weekly signal plus one longer-term comparison |
| Article | Support a complete analytical narrative | Headline, period, claim provenance, and reading hierarchy |
| Repository summary | Compare momentum and inspect trustworthy context | Search, recent-momentum order, filters, status, and direct GitHub link |
| Ranking page | Answer one stated analytical question | Intended inference, accessible table, provenance, and download |

## Signature Element: Evidence Ruler

Each major evidence surface uses an evidence ruler: a restrained horizontal
timeline showing the covered period, observation density, current point, and
freshness boundary. It is rendered in HTML first and enhanced only when
interaction adds value.

The ruler must:

* State its intended inference in nearby text
* Expose the period and freshness in the accessibility tree
* Use position, labels, and line style in addition to color
* Remain legible at 200% zoom and narrow widths
* Avoid continuous or decorative motion

## Motion And Interaction

Motion is limited to evidence-state transitions that clarify cause and effect:
filter result updates, disclosure expansion, and focus movement. Default
durations should remain between 120 and 180 milliseconds.

Under `prefers-reduced-motion: reduce`, transitions and smooth scrolling are
removed. No essential content, ordering, or status depends on animation. Hover,
focus, touch, keyboard, and assistive-technology interactions expose equivalent
information.

## Representative Acceptance Views

Sponsor review requires mobile and desktop views for:

* Homepage with current and longer-term evidence
* Weekly or yearly article with claim provenance
* Repository summary with filters and empty state
* Ranking page with dense and long-label data
* Light and dark modes where automatic dark mode remains enabled
* Keyboard focus, reduced motion, 200% zoom, and no-JavaScript states

## Self-Critique

The field-notebook direction risks becoming visually dry or overly dense. The
evidence ruler and editorial type create identity without turning every section
into a bordered panel, but representative prototypes must prove that scanning
remains fast on mobile.

The proposed type families improve editorial and data distinction but add font
loading and licensing work. A local fallback-only prototype should be compared
before committing to bundled assets.

The evidence rail could consume too much width or duplicate labels. It should
collapse into a compact metadata row on smaller screens and must be removed when
it adds no information.

The direction is intentionally not implemented until the accountable design and
sponsor reviews approve or revise it.
