# J England Blog

One site for the blog, Amazon gear, partner codes, and the socials hub.

Live target: [jenglandblog.netlify.app](https://jenglandblog.netlify.app)

## Add content (this is the whole workflow)

No admin panel. Edit a file, push, Netlify rebuilds.

### New blog post

1. Copy any file in `src/content/posts/`.
2. Rename it. The filename becomes the URL (`my-post.md` → `/blog/my-post`).
3. Fill in the top block:

```md
---
title: Title people will see
description: One or two sentences for cards and search.
date: 2026-09-03
featured: false
tags:
  - sim-racing
gear:
  - moza-r5-bundle
---

Write the post in normal markdown.
```

`gear:` is a list of filenames from `src/content/gear/` (without `.md`). Those products automatically show as Amazon cards at the bottom of the post.

### New Amazon product

1. New file in `src/content/gear/`.
2. Required fields:

```md
---
title: Product name
description: Why you use it.
category: sim-racing
amazonUrl: https://amzn.to/yourShortLink
featured: false
usedFor: Daily sim rig
---

Optional longer notes.
```

`category` must be one of: `sim-racing`, `content`, `photography`, `off-road`.

### New partner code (not Amazon)

New file in `src/content/partners/` with `name`, `offer`, `url`, and `code`.

### Site-wide stuff (name, socials, storefront)

Edit `src/data/site.ts`. Paste your real Amazon storefront URL over `YOUR_STOREFRONT_USERNAME`.

## Local preview

```bash
npm install
npm run dev
```

Then open the URL it prints (usually `http://localhost:4321`).

## Deploy on Netlify

Point the Netlify site (`jenglandblog.netlify.app`) at **this** GitHub repo.

- Build command: `npm run build`
- Publish folder: `dist`
- Node: 22 (already in `netlify.toml`)

The empty `my-affiliate-blog` repo can stay unused. This repo is the source of truth so you are not maintaining two sites.

## Pages

| URL | What it is |
| --- | --- |
| `/` | Home — featured posts + gear + codes |
| `/blog` | All posts |
| `/gear` | All Amazon products, filterable |
| `/partners` | Moza / Insta360 codes |
| `/links` | Bio hub for Instagram / TikTok |
| `/about` | Who you are + how to add files |
