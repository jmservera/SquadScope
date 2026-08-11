# BR-005 Representation Evidence

## Questions And Intended Inferences

* **Absolute rankings:** Which repositories have the highest latest observed
  star counts? The intended inference is absolute popularity, not growth.
* **Growth ranking:** Which repositories gained the most stars across 2026
  observations? The intended inference is absolute observed momentum, not a
  growth rate.

The selected representations are a common-baseline dot/lollipop chart for
absolute stars and a start-to-end range chart for growth. The complete
server-rendered tables remain authoritative.

## Fixture Coverage

Dense, sparse, tied, zero, long-label, top-10, top-100, and mobile paths were
checked through the template and generated-data tests. Ties retain distinct
ranks and exact values; a zero lollipop remains at the baseline and a zero
range overlaps its endpoints; labels longer than 30 characters are shortened in
the SVG while their complete values remain in SVG titles and tables. Top-10
SVGs avoid dense-chart compression, while the complete table/explorer retains
up to 100 records.

Direct visual evidence was captured by
`tests/visual/observatory-visual-regression.spec.mjs` in desktop light, desktop
dark, mobile light, and mobile dark for:

* `data-growth.png`
* `data-top-month.png`
* `data-mcp.png`

The mobile presentation intentionally replaces the SVG with a horizontally
scrollable table containing the same exact facts. The browser matrix passed
without horizontal page overflow, and Axe found no serious or critical WCAG
2.1 A/AA violations on the ranking page.

## Five-Member Proxy Comprehension Panel

Each member independently answered five questions for both representations:
encoding, top repository/value, edge-fixture behavior, mobile fact recovery,
and interpretation without color. A member passed with at least four correct
answers and no critical inference misunderstanding.

### Amy — Mobile And UX

**Range raw answers:** marker positions are earliest/latest stars and segment
length is observed gain; the leader is `mattpocock/skills`, +121,392 stars
(90,287 to 211,679); code inspection shows ties retain values, zero overlaps
endpoints, and full long names survive in titles/tables; mobile exposes the same
Start/End/Gain facts in the scrollable table; rank, geometry, dot size, numeric
labels, and the table avoid color dependence. **5/5, pass.**

**Dot raw answers:** position and stem length encode absolute stars; leaders are
`openclaw/openclaw` at 385,733 and `affaan-m/ECC` at 239,078; code inspection
shows ties retain separate ranks, zero stays at the baseline, and full long
names survive in titles/tables; mobile exposes Rank/Repository/Metric in the
scrollable table; geometry, rank, exact text, and tables avoid color
dependence. **5/5, pass.**

### Calculon — Visual Clarity

**Range raw answers:** endpoints encode initial/final stars and extent encodes
gain; the leader is `mattpocock/skills`, +121,392 (90,287 to 211,679); code
inspection shows tied gains can occupy different positions, zero collapses, and
long labels retain full fallbacks; mobile facts remain in the table; position,
extent, dot size, rank, and text are non-color encodings. **5/5, pass.**

**Dot raw answers:** common-baseline stem length and position encode absolute
stars; leaders are `openclaw/openclaw` at 385,733 and `affaan-m/ECC` at
239,078; code inspection shows ties share positions, zero has a zero-length
stem, and fallbacks retain full labels; mobile uses the complete table;
position, length, rank, metrics, and table are independent of color.
**5/5, pass.**

### Fry — Accessibility And Fallback

**Range raw answers:** circles encode start/end stars and their segment encodes
gain; the leader is `mattpocock/skills`, +121,392 (90,287 to 211,679); code
inspection shows rank/text preserve tied, zero, and long-label facts; mobile
retains repository, start, end, and gain in the keyboard-accessible table;
semantic text and geometry avoid color dependence. **5/5, pass.**

**Dot raw answers:** stem extent and circle position encode absolute stars;
leaders are `openclaw/openclaw` at 385,733 and `affaan-m/ECC` at 239,078; code
inspection shows separate rows preserve ties, zero retains a visible origin
dot, and complete names remain in fallbacks; mobile retains exact table facts;
rank, position, length, labels, and table are redundant. **5/5, pass.**

### Leela — Maintainability And Comprehension

**Range raw answers:** endpoint positions encode earliest/latest stars and
extent encodes observed gain; the leader is `mattpocock/skills`, +121,392;
code inspection shows ties retain exact values, zero overlaps endpoints, and
long labels retain full fallbacks; mobile uses the same generated records in
the table; position, extent, dot size, rank, and labels avoid color dependence.
**5/5, pass.**

**Dot raw answers:** stem extent and endpoint position encode absolute stars;
leaders are `openclaw/openclaw` at 385,733 and `affaan-m/ECC` at 239,078; code
inspection shows ties remain separate rows, zero stays on the axis, and full
names remain in titles/tables; mobile retains exact metrics via the table;
rank, geometry, exact text, and table avoid color dependence. **5/5, pass.**

### Farnsworth — Analytical Fidelity

**Range raw answers:** horizontal positions encode absolute earliest/latest
stars and segment length encodes absolute gain, not rate; the leader is
`mattpocock/skills`, +121,392; code inspection shows equal gains can have
different positions, zero safely collapses, and long labels remain complete in
fallbacks; mobile preserves start/end/gain in the table; geometry, endpoint
marks, ranks, labels, and table avoid color dependence. **5/5, pass.**

**Dot raw answers:** endpoint position and line length from zero encode absolute
stars, not growth; leaders are `openclaw/openclaw` at 385,733 and
`affaan-m/ECC` at 239,078; code inspection shows equal values share endpoints,
zero maps to baseline, and complete labels remain in fallbacks; mobile preserves
exact facts through the table; position, line length, rank, and exact text
avoid color dependence. **5/5, pass.**

## Gate Result

| Representation | Passing members | Required | Result |
|---|---:|---:|---|
| Dot/lollipop absolute ranking | 5/5 | 4/5 | Pass |
| Start-to-end growth range | 5/5 | 4/5 | Pass |

No blocking comprehension defect remains. Both representations communicate
their intended inference without relying on color and preserve equivalent
mobile and accessible tabular facts.
