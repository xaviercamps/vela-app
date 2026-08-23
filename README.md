# vela-app
Marketing site for Vela HRV — Apple Watch stress tracking app.

Served from the domain root (velahrv.com via CNAME). English is the default
locale at `/`; the other 8 locales (es, ca, eu, gl, fr, de, it, pt) live under
`/<code>/`. Each locale has 4 pages: the landing (home), `/support/` (FAQ),
`/privacy/` and `/accessibility/`.

Everything is generated from `tools/gen_locales.py` — edit the content
dictionary there and rerun `python3 tools/gen_locales.py` to regenerate all
36 pages. Do not hand-edit the generated `index.html` files directly, changes
will be overwritten on the next run.

## SEO

`tools/gen_locales.py` also regenerates `sitemap.xml` and `robots.txt` on
every run — they are not maintained by hand. Every one of the 36 generated
pages carries, per locale:

- a self-referencing `<link rel="canonical">`,
- a full hreflang `<link rel="alternate">` cluster (all 9 locales +
  `x-default` pointing at the English/root version),
- a unique `<meta name="description">` (landing pages use a dedicated
  `meta_desc`; support/privacy/accessibility reuse that page's own
  `about_p1` / `highlight` copy so nothing is duplicated across pages or
  locales),
- Open Graph and Twitter Card tags, using `assets/og-image.png` (a 1200×630
  brand card) as the share image, and
- on landing pages only, `SoftwareApplication` JSON-LD structured data
  (`app_json_ld()` in the script).

`sitemap.xml` lists all 36 pages with the same hreflang alternates embedded
as `<xhtml:link>` per Google's recommended sitemap format, and `lastmod` is
stamped with the date the script last ran.

The JSON-LD deliberately omits `aggregateRating`. Fabricating a rating
violates Google's structured-data guidelines, and there's no real App Store
rating/review count wired in yet. Once that data exists, add it to
`app_json_ld()` in `tools/gen_locales.py` as:

```python
"aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "<real value from App Store Connect>",
    "ratingCount": "<real review count>",
},
```

### Verifying the domain in Google Search Console

DNS TXT verification (via your registrar, e.g. Porkbun) works independently
of this repo. The HTML-file method below is the alternative when you'd
rather not touch DNS:

1. In Search Console, add a property for `https://velahrv.com` (or open the
   existing one) and choose the **HTML file** verification method.
2. Download the file Google gives you (named like
   `google1234567890abcdef.html`).
3. Drop it straight into the repo root — the same folder as `CNAME` and this
   README, e.g.:
   ```
   cp ~/Downloads/google1234567890abcdef.html /path/to/vela-app/
   ```
   Do **not** run it through `gen_locales.py` and don't rename it — Google
   checks the exact filename and byte content. The generator only ever
   writes the paths it knows about, so this file is left alone on every
   future run.
4. Commit and push it to `main`. Once GitHub Pages redeploys (usually a
   couple of minutes), confirm it's live at
   `https://velahrv.com/google1234567890abcdef.html`, then click **Verify**
   in Search Console.
5. Once verified, submit `https://velahrv.com/sitemap.xml` under Sitemaps.

### Verifying in Bing Webmaster Tools

The easiest path is importing the Google Search Console verification
directly: in Bing Webmaster Tools, choose **Import from Google Search
Console** and authorize it — no file needed. If you'd rather verify Bing
independently, the same HTML-file approach works: Bing gives you a file
named like `BingSiteAuth.xml`, which also just needs to land in the repo
root and be pushed to `main`. Either way, submit
`https://velahrv.com/sitemap.xml` under Sitemaps once verified.
