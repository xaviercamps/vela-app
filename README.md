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
