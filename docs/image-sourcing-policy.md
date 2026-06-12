# Image Sourcing Policy

This document defines the copyright-safe image sourcing policy for Claracle (SquadScope).

## Core Principle

**Fair use is not an automated image policy.** All images used in generated content must be explicitly licensed, locally hosted, and registry-tracked.

## Image Preference Order

1. **Generated data visuals (preferred):** Mermaid diagrams, SVG charts, repo trend cards, signal/noise summaries, star/topic visualizations. These are original works created by the pipeline.
2. **CC0 / Openverse images:** Only when downloaded, locally hosted, resized to required dimensions, attributed where the source requests it, and recorded in `data/image-registry.json`.
3. **Local assets:** Original artwork or icons created for the project, registered as `local-asset` license type.

## Prohibited Practices

- **No hotlinking:** Never reference external image URLs in published content. All images must be served from the local repository/deploy.
- **No `og:image` reuse:** Do not scrape or reuse `og:image` meta tags from external articles. An Open Graph tag is not a reuse license.
- **No fair-use automation:** Do not rely on fair use as a justification for automated image sourcing. Fair use requires case-by-case human judgment.
- **No unattributed use:** CC0 images do not legally require attribution, but the registry should still record the source for provenance.
- **No secrets in URLs:** Image paths must never contain SAS tokens, API keys, credentials, or tracking parameters.

## GitHub OG Previews

GitHub auto-generated Open Graph preview images may be used **only when**:
- They are generated/controlled by this repo or repo owner
- They are downloaded and stored locally
- Provenance is recorded in the image registry
- They are NOT scraped from third-party repositories

## Image Registry

All non-generated cover images are tracked in `data/image-registry.json`:
- **Schema:** `data/image-registry.schema.json`
- **Management:** `scripts/manage_image_registry.py` (add, validate, list)
- **Validation:** `scripts/validate_content_images.py` (CI gate)

### Required Registry Fields

| Field | Description |
|-------|-------------|
| `filename` | Relative path from repo root |
| `license` | One of: `CC0`, `Openverse`, `local-asset` |
| `added_by` | Person or automation identifier |

### Recommended Fields

| Field | Description |
|-------|-------------|
| `source_url` | Original source for provenance |
| `attribution` | Attribution text |
| `added_at` | ISO date added |
| `used_in` | Content paths using this image |
| `dimensions` | Width/height object |

## Validation Gates

CI enforces:
1. `scripts/manage_image_registry.py validate` — registry schema integrity
2. `scripts/validate_content_images.py` — no hotlinks, no secrets, no unregistered covers in published content

## Hugo Configuration

Hugo Goldmark must remain configured with `unsafe = false`. Image rendering relies on local paths and Hugo's resource pipeline, not raw HTML injection.

## Workflow

1. Pipeline generates data visuals (Mermaid/SVG) → used directly, no registry needed
2. If a non-generated cover is needed:
   a. Find CC0/Openverse source
   b. Download to `assets/covers/`
   c. Resize to required dimensions
   d. Register via `scripts/manage_image_registry.py add`
   e. Reference in frontmatter using the Hugo asset-relative path (e.g., `covers/foo.webp`)
      — Hugo resolves this via `resources.Get`; the on-disk file lives at `assets/covers/foo.webp`
3. CI validates on every PR (registry must exist; path normalization handles both forms)

## Ownership

- **Bender:** Pipeline metadata, registry schema, download/resize automation
- **Hermes:** Copyright/privacy/security policy review
- **Calculon:** Visual/cover design decisions
- **Amy:** Hugo/frontmatter consumption of registered images
- **Fry:** Validation tests and CI gates
