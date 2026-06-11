# Article Visual Modules (#328)

Reusable, **locally generated** visual modules that give every weekly article a
meaningful visual or an intentional fallback — without third-party/hotlinked
imagery and without enabling Goldmark `unsafe`.

## Design principles

- **Generated first.** Visuals are built from the article's own data (frontmatter
  metadata) or author-declared shortcode values. No stock images, no hotlinks,
  no `og:image` reuse.
- **Evidence-first.** Modules help scanning/comprehension; they never overstate
  weak signals, hide caveats, or imply rankings. Decorative motifs are disclosed
  (`aria-hidden`) and never carry the data claim — real figures are always text.
- **Safe by construction.** `unsafe = false` stays. HTML lives in partials /
  shortcodes, never in Markdown bodies.
- **No layout breakage.** Missing data yields an intentional fallback card, not an
  empty or broken region. Fixed aspect ratios reserve space (no CLS).

## Module taxonomy

| Module | Source | When to use |
| --- | --- | --- |
| **Generated cover card** (`visuals/cover-card.html`) | frontmatter `week`, `tags`, `repos_featured` | Default header for every weekly article. Bar-field count reflects topic breadth; accessible name reports real week/topic/repo figures. |
| **Topic / star visualization** (`visuals/topic-constellation.html`, shortcode `topic-stars`) | `tags` / author list | Surface the week's topic clusters as equal-weight chips. Honest by construction. |
| **Signal & Noise summary** (`visuals/signal-noise.html`, shortcode `signal-noise`) | frontmatter `signal_noise` or shortcode args | Two-column scannable summary of durable signal vs noise floor, with a required caveat slot. |
| **Repo trend chart** (`visuals/repo-trend.html`, shortcode `repo-trend`) | author/pipeline numeric series | Lightweight bar chart for star/momentum history. Bars are decorative; the series is exposed as a visually-hidden text summary. |
| **Intentional fallback card** (`visuals/fallback-card.html`) | `visual = "none"` | Deliberate "no standalone visual this week" card. |

## Selection rules (orchestrator `visuals/article-cover.html`)

1. `visual = "none"` → intentional fallback card.
2. A **compliant local cover image** (resolves to a Hugo page-bundle or global
   resource) → processed, locally-hosted `<img>`. See safe-cover policy below.
3. Otherwise → generated SVG cover card.

## Declaring modules

- **Automatic (generated metadata):** the cover card renders from existing
  frontmatter (`week`, `tags`, `repos_featured`); the Signal & Noise card renders
  when `signal_noise` is present.
- **Frontmatter example:**

  ```yaml
  signal_noise:
    signal:
      - "Agent skills verticalizing into professional packs"
    noise:
      - "Coordinated activator / star-farm repos"
    caveat: "Editorial judgments, not automated classifications; counts are not rankings."
    source: "Derived from this week's new_repos sample."
  ```

- **Inline shortcodes** (pipe-separated values), for body-level placement:

  - `topic-stars topics="agent-skills|local-first" stars="16480000" repos="390"`
  - `repo-trend repo="cpaczek/skylight" values="120|340|512|890|2332" labels="W20|W21|W22|W23|W24"`
  - `signal-noise signal="A|B" noise="C|D" caveat="…"`

## Safe cover policy hook (#329)

Images are only rendered when `cover.image` resolves to a **locally hosted Hugo
resource** (downloaded + processed). External / hotlinked URLs are intentionally
ignored, and we never rely on fair use or reuse `og:image`. Attribution
(`cover.attribution`) is rendered when present; full CC0/Openverse sourcing,
resizing, attribution, and the image registry are owned by **#329**. Until then,
articles lead with generated visuals + the typographic fallback.

## Accessibility & responsiveness

- SVG motifs are `aria-hidden`; data is always available as text (accessible
  names / visually-hidden summaries).
- Responsive at 320/360/390/414/768px: SVGs use `width:100%` + `viewBox`; the
  signal/noise grid collapses to one column on mobile; no horizontal scroll.
- Aspect ratios reserve space to avoid CLS; interactive targets meet the 44×44
  minimum established in #327.
