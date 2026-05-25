# Amy — Cookie Consent vendoring

Date: 2026-05-25

Decision: vendor Cookie Consent v3 directly in `static/vendor/cookieconsent/` and pin it to upstream version `v3.0.1`.

Rationale:
- Cookie consent must run before optional analytics scripts are activated.
- Vendoring avoids relying on the jsDelivr CDN at runtime.
- The pinned files are the published `dist` CSS and UMD bundle from `orestbida/cookieconsent@v3.0.1`.

Checksums:
- `cookieconsent.css`: `sha256 ca046b8b1b1094107205988e7096a687b241c8ef5f3fefe5e543ed28d26646c1`
- `cookieconsent.umd.js`: `sha256 1267fd33fcf3ab4043a7cc62cc9259a2c66f839f695216f7737ed37b7b3e62e6`
