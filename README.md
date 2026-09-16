# J England

Professional site for tech reviews, the Amazon shop, field notes, and partner codes.

Live: [jenglandblog.netlify.app](https://jenglandblog.netlify.app)

## Add content

No admin panel. Edit a file, push, Netlify rebuilds.

### New review or journal note

1. Copy any file in `src/content/posts/`.
2. Rename it. The filename becomes the URL (`my-post.md` → `/blog/my-post`).
3. Fill in the top block:

```md
---
title: Title people will see
description: One or two sentences for cards and search.
date: 2026-09-16
featured: false
kind: review
rating: 4.5
verdict: Short buy / skip line.
tags:
  - sim-racing
gear:
  - moza-r5-bundle
---

Write in normal markdown.
```

`kind` is `review` or `journal`. Reviews show on `/reviews` with stars. Journal notes show on `/journal`. `gear:` is filenames from `src/content/gear/` (without `.md`) and those Amazon cards appear at the bottom.

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

Edit `src/data/site.ts`. Storefront is already set to [amazon.com/shop/jengland91](https://www.amazon.com/shop/jengland91) with Associates tag `joshrengland-20`.

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
| `/` | Home — website landing, reviews, shop, Amazon storefront |
| `/reviews` | Tech reviews with ratings |
| `/shop` | Amazon product shop (filters). `/gear` redirects here |
| `/journal` | Field notes |
| `/blog` | All writing |
| `/partners` | Moza / Insta360 codes |
| `/links` | Bio hub for Instagram / TikTok |
| `/about` | Who you are |
