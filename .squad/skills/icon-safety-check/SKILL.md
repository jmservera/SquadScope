# Icon Safety Check

**Owner:** Calculon (Designer)  
**Confidence:** low  
**Created:** 2026-05-25

## Purpose

Verify icon designs don't accidentally resemble hate symbols or extremist imagery before shipping. Small sizes (16px favicon) are where ambiguity hides most.

## When to Apply

- Before finalizing any new icon/logo design
- When evaluating icon concepts that use letterforms, runes, or geometric patterns
- As part of icon spec review

## Steps

### 1. Pre-Design Awareness

Avoid these patterns without explicit safety review:
- Double-letter monograms (especially S, H, N)
- Single lightning bolts / rune-like strokes
- Certain cross variants (Iron Cross, Celtic Cross in certain contexts)
- Sun-wheel / spoke patterns
- Hand gesture shapes

### 2. Post-Design Verification

**Multi-size render test:**
- 16px (favicon) — most critical, ambiguity peaks here
- 32px, 64px, 128px, 512px

**Transformation tests:**
- Rotate 90°, 180°, 270° — no problematic shapes should emerge
- Mirror horizontally and vertically
- Invert colors (what does negative space reveal?)

**Reference check:**
- ADL Hate on Display database: https://www.adl.org/hate-symbols
- Similar resources for regional/cultural symbols

### 3. Documentation

Include in icon spec:
- "Silhouette Safety Check ✓" section
- List what was verified and against what references
- Note any considerations for future modifications

## Example

See `docs/design/icon-spec.md` — Section 2 "Silhouette Safety Check" documents the robot-with-binoculars verification.

## Promotion Criteria

Confidence → medium after:
- 2+ icon designs successfully use this pattern
- 1+ actual ambiguity caught and fixed

## References

- Branding-safety directive: `.squad/decisions/inbox/copilot-directive-icon-ss-association.md`
- Icon spec with example: `docs/design/icon-spec.md`
