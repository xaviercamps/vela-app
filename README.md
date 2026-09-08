# vela-app
Marketing site for Vela HRV — Apple Watch stress tracking app.

Served from the domain root (velahrv.com via CNAME). English is the default
locale at `/`; the other 11 locales (es, ca, eu, gl, fr, de, it, pt, cs, el, ja)
live under `/<code>/`. Each locale has 5 pages: the landing (home), `/support/`
(FAQ), `/privacy/`, `/accessibility/` and `/changelog/`.

Everything is generated from `tools/gen_locales.py` — edit the content
dictionary there and rerun `python3 tools/gen_locales.py` to regenerate all
60 pages. Do not hand-edit the generated `index.html` files directly, changes
will be overwritten on the next run.

The changelog's version history mirrors the app repo's version tags; the entry
for a build still in App Store review carries `"status": "review"` so the page
shows it as not-yet-available.
