---
title: GitHub Pages deployment
description: Deployment, validation, and rollback for the Claracle production site
---

# GitHub Pages deployment

Claracle remains on GitHub Pages. Both production workflows build the complete
Hugo site, upload the Pages artifact, and deploy through the protected
`github-pages` environment.

Repository URLs approved for retirement are absent from the generated site and
return the normal GitHub Pages HTTP 404 response. No repository redirect layer is
required or supported.

## Required checks

The workflows block after deployment unless production returns HTTP 200 for an
approved retained profile and HTTP 404 for the retired legacy Odysseus alias and
its former redirect-only destination.

Also confirm `public/404.html` exists, the sitemap contains no retired repository
URLs, and the rendered site has no internal links to retired URLs.

## Rollback

Follow `data/migrations/repository-migration-rollback.json`, restore the listed
paths from its `pre_migration_commit`, rebuild, and deploy the restored tree
through the normal GitHub Pages workflow.
