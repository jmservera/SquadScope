---
title: Cloudflare Pages deployment
description: Provisioning, cutover, validation, and rollback for the Claracle production site
---

# Cloudflare Pages deployment

Claracle deploys the complete Hugo build and `static/_redirects` atomically to the
Cloudflare Pages project `claracle`. Both production workflows use Wrangler
Direct Upload; GitHub Pages is not a production target.

## One-time provisioning

1. Add `claracle.com` as a Cloudflare zone and replace the Namecheap nameservers
   with the two nameservers assigned by Cloudflare. Wait for the zone to become
   active before changing production traffic.
2. Create the Direct Upload project:

   ```bash
   npx --yes wrangler@4.120.1 pages project create claracle --production-branch main
   ```

3. Add `claracle.com` and `www.claracle.com` as custom domains on the `claracle`
   Pages project. Confirm that Cloudflare provisions both DNS records and TLS
   certificates.
4. Create a scoped API token with only **Account > Cloudflare Pages > Edit** for
   the account that owns the project. Add these GitHub Actions secrets:
   `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.
5. Configure the `cloudflare-pages` GitHub environment to restrict deployment to
   `main`. Disable GitHub Pages only after a Cloudflare preview deployment and
   both custom domains pass validation.

Do not put the token or account ID in repository files. DNS administration uses
a separate operator credential; the deployment token does not need zone-edit
permission.

## Required cutover checks

The workflows block after deployment unless production returns:

* HTTP 200 for an approved retained repository profile.
* HTTP 301, in one hop, from the approved legacy Odysseus URL to its retained
  canonical URL.
* HTTP 404 for an approved retired repository URL.

Also confirm `public/404.html` exists, the sitemap contains no retired repository
URLs, and the rendered site has no internal links to retired URLs. Preserve the
successful workflow URL as the deployment evidence.

## Rollback

Cloudflare retains prior immutable deployments. Promote the prior deployment
from **Workers & Pages > claracle > Deployments**, then verify the custom domains.
If the repository migration itself must be reversed, follow
`data/migrations/repository-migration-rollback.json`, restore the listed paths
from its `pre_migration_commit`, rebuild, and deploy the restored tree.

Do not recreate a retired URL as a temporary 200 response. A rollback must
restore the complete prior site and redirect state as one deployment.
