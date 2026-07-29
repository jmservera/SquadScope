+++
title = "Star Velocity Explorer"
date = "2026-07-29T14:05:00Z"
lastmod = "2026-07-29T14:05:00Z"
draft = false
summary = "Explore which AI and developer-tool repositories gained the most observed stars in Claracle's checked-in weekly GitHub trend artifacts."
description = "A client-side Star Velocity Explorer for filtering repositories by language and topic using one pre-generated static JSON file."
layout = "single"
data_source = "/tools/star-velocity-explorer.json"
categories = ["Data Observatory"]
tags = ["interactive-tools", "github-trends", "star-velocity"]
keywords = ["Claracle Star Velocity Explorer", "GitHub star velocity tool", "client-side trend explorer"]
hideMeta = true
+++

The Star Velocity Explorer turns Claracle's weekly public GitHub trend artifacts
into an in-browser ranking of observed star gains. It derives velocity from
checked-in snapshots only: latest observed stars minus first observed stars.

No backend, authenticated API, third-party script, or external data service is
used. The page fetches a same-origin static JSON file generated from repository
artifacts already in this site.
