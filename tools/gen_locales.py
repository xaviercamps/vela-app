#!/usr/bin/env python3
"""Generates every page of the vela-app site — landing (home), support, privacy,
accessibility and changelog — for all 12 locales (en, es, ca, eu, gl, fr, de,
it, pt, cs, el, ja) from a single content dictionary. Run from anywhere; SITE is
the repo root (tools/..). The site is served from the domain root (see CNAME),
so URLs have no path prefix: EN lives at the root, other locales under
/<code>/."""

import json
import re
from datetime import date
from pathlib import Path

SITE = Path(__file__).parent.parent
MAIL = "xaviercampsnovi@gmail.com"
ORDER = ["es", "en", "ca", "eu", "gl", "fr", "de", "it", "pt", "cs", "el", "ja"]
APPSTORE_URL = "https://apps.apple.com/app/vela-hrv/id6762096428"
# Per-language images made by vela-store/2.0.0/scripts/web_images.py (Apple Watch Ultra,
# Ocean band, the app in that language). 1920x1920 JPEG.
# Single watches on a transparent background (WebP), made by vela-store/2.0.0/scripts/web_images.py.
STRESS_TOUR = ["tour-score", "tour-trend", "tour-ranges"]
BATTERY_TOUR = ["tour-charge", "tour-curve", "tour-spent"]
SITE_URL = "https://velahrv.com"
DEFAULT_LOCALE = "en"  # served at the domain root; used as the x-default hreflang target
BUILD_DATE = date.today().isoformat()
PAGES = ["landing", "support", "privacy", "accessibility", "changelog", "legal"]

# BCP47 tag Google/Bing expect for each site locale in hreflang and og:locale
HREFLANG_TAG = {
    "es": "es", "en": "en", "ca": "ca", "eu": "eu", "gl": "gl", "fr": "fr",
    "de": "de", "it": "it", "pt": "pt-PT", "cs": "cs", "el": "el", "ja": "ja",
}
OG_LOCALE = {
    "es": "es_ES", "en": "en_US", "ca": "ca_ES", "eu": "eu_ES", "gl": "gl_ES", "fr": "fr_FR",
    "de": "de_DE", "it": "it_IT", "pt": "pt_PT", "cs": "cs_CZ", "el": "el_GR", "ja": "ja_JP",
}

def path_for(code: str, page: str) -> str:
    """page is one of: landing, support, privacy, accessibility, changelog, legal."""
    base = "/" if code == "en" else f"/{code}/"
    return base if page == "landing" else f"{base}{page}/"

def abs_url(code: str, page: str) -> str:
    return SITE_URL + path_for(code, page)

def out_path(code: str, page: str) -> Path:
    rel = path_for(code, page).strip("/")
    return (SITE / rel / "index.html") if rel else (SITE / "index.html")

def lang_row(page: str, current: str, aria: str) -> str:
    parts = []
    for c in ORDER:
        label = c.upper()
        if c == current:
            parts.append(f'<span aria-current="true">{label}</span>')
        else:
            parts.append(f'<a href="{path_for(c, page)}" hreflang="{c}">{label}</a>')
    return f'<nav class="lang-row" aria-label="{aria}">{" · ".join(parts)}</nav>'

def esc_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;")

def plain(s: str) -> str:
    """Copy reused as a meta description: drop inline markup and entities."""
    return re.sub(r"<[^>]+>", "", s).replace("&nbsp;", " ")

def seo_head(code: str, page: str, title: str, desc: str, image: str = "og-image.png") -> str:
    """Canonical link, full hreflang cluster (+ x-default), and Open Graph /
    Twitter Card tags for a single page. Shared by every page type so the
    12 locales x 5 pages all carry the same SEO scaffolding."""
    canonical = abs_url(code, page)
    title_a, desc_a = esc_attr(plain(title)), esc_attr(plain(desc))
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{HREFLANG_TAG[c]}" href="{abs_url(c, page)}">'
        for c in ORDER)
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{abs_url(DEFAULT_LOCALE, page)}">'
    image_url = f"{SITE_URL}/assets/{image}"
    locales = "".join(f'<meta property="og:locale:alternate" content="{OG_LOCALE[c]}">\n'
                      for c in ORDER if c != code)
    return f"""<meta name="description" content="{desc_a}">
<link rel="canonical" href="{canonical}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Vela HRV">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title_a}">
<meta property="og:description" content="{desc_a}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{OG_LOCALE[code]}">
{locales}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_a}">
<meta name="twitter:description" content="{desc_a}">
<meta name="twitter:image" content="{image_url}">"""

def app_json_ld(code: str, t: dict) -> str:
    """SoftwareApplication structured data for the landing page, one per
    locale. The app is free to download (Vela Pro is an in-app purchase), so
    the offer is price 0. No aggregateRating is emitted: fabricating one
    would violate Google's structured-data guidelines. Add it once real App
    Store review data exists (see README)."""
    L = t["landing"]
    data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Vela HRV",
        "description": plain(L["meta_desc"]),
        "applicationCategory": "HealthApplication",
        "operatingSystem": "watchOS 26",
        "url": abs_url(code, "landing"),
        "image": f"{SITE_URL}/assets/icon-1024.png",
        "downloadUrl": APPSTORE_URL,
        "inLanguage": HREFLANG_TAG[code],
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "EUR",
            "url": APPSTORE_URL,
        },
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'

LANG_ROW_CSS = """    .lang-row { margin-top: 1rem; }
    .lang-row a, .lang-row span {
      color: var(--text-tertiary);
      text-decoration: none;
      font-size: 0.78rem;
      letter-spacing: 0.06em;
    }
    .lang-row a:hover { color: var(--primary-bright); }
    .lang-row span { color: var(--primary-bright); }
"""

REDUCED_MOTION_CSS = """    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      .fade-in, .hero-icon { animation: none; opacity: 1; transform: none; }
    }
"""

# ---------------------------------------------------------------- templates

HERO_SVG = """<svg class="hero-icon" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <circle cx="40" cy="40" r="30" stroke="#4A9EFF" stroke-width="1.2" opacity="0.5" filter="url(#glow)"/>
        <circle cx="40" cy="40" r="30" stroke="#8ECFFF" stroke-width="0.6" opacity="0.3"/>
        <path d="M8 40 C14 40 16 32 22 32 C28 32 30 48 36 48 C42 48 44 28 50 28 C56 28 58 44 64 44 C68 44 70 40 72 40"
              stroke="white" stroke-width="1.4" stroke-linecap="round" fill="none" opacity="0.9"/>
        <circle cx="40" cy="38" r="2" fill="white" opacity="0.9"/>
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
      </svg>"""

SUPPORT_CSS = """    :root {
      --bg: #0A1628;
      --bg-deep: #060D1A;
      --primary: #4A9EFF;
      --primary-bright: #8ECFFF;
      --text: #FFFFFF;
      --text-secondary: rgba(255,255,255,0.6);
      --text-tertiary: rgba(255,255,255,0.35);
      --surface: rgba(255,255,255,0.06);
      --border: rgba(255,255,255,0.08);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-weight: 300;
      min-height: 100vh;
      overflow-x: hidden;
    }
    body::before {
      content: '';
      position: fixed;
      top: -200px;
      left: 50%;
      transform: translateX(-50%);
      width: 800px;
      height: 800px;
      background: radial-gradient(ellipse, rgba(74,158,255,0.08) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }
    .hero-icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 2rem;
      animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.85; transform: scale(0.97); }
    }
    .container {
      max-width: 640px;
      margin: 0 auto;
      padding: 0 1.5rem;
      position: relative;
      z-index: 1;
    }
    header {
      padding: 5rem 0 4rem;
      text-align: center;
    }
    .back-link {
      display: inline-block;
      color: var(--primary-bright);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 400;
      letter-spacing: 0.04em;
      margin-bottom: 2.5rem;
      opacity: 0.7;
      transition: opacity 0.2s;
    }
    .back-link:hover { opacity: 1; }
    .app-name {
      font-family: 'DM Serif Display', serif;
      font-size: clamp(2.2rem, 6vw, 3rem);
      font-weight: 400;
      letter-spacing: -0.02em;
      color: var(--text);
      margin-bottom: 0.5rem;
    }
    .app-tagline {
      font-size: 0.95rem;
      color: var(--text-secondary);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 400;
    }
    .divider {
      width: 40px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--primary), transparent);
      margin: 3rem auto;
    }
    section { margin-bottom: 3rem; }
    h2 {
      font-family: 'DM Serif Display', serif;
      font-size: 1.4rem;
      font-weight: 400;
      color: var(--text);
      margin-bottom: 1rem;
      letter-spacing: -0.01em;
    }
    p {
      font-size: 0.95rem;
      line-height: 1.75;
      color: var(--text-secondary);
    }
    p + p { margin-top: 0.75rem; }
    .faq-item {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 0.75rem;
      transition: border-color 0.2s;
    }
    .faq-item:hover { border-color: rgba(74,158,255,0.2); }
    .faq-item h3 {
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--text);
      margin-bottom: 0.5rem;
      letter-spacing: 0.01em;
    }
    .faq-item p { font-size: 0.88rem; line-height: 1.65; }
    .faq-item a { color: var(--primary-bright); text-decoration: none; border-bottom: 1px solid rgba(142,207,255,0.3); }
    .faq-item:target { border-color: rgba(74,158,255,0.45); }
    .contact-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 2rem;
      text-align: center;
    }
    .contact-card p { margin-bottom: 1.25rem; }
    .contact-link {
      display: inline-block;
      color: var(--primary-bright);
      text-decoration: none;
      font-size: 0.95rem;
      font-weight: 500;
      border-bottom: 1px solid rgba(142,207,255,0.3);
      padding-bottom: 2px;
      transition: border-color 0.2s, color 0.2s;
    }
    .contact-link:hover { color: #fff; border-color: rgba(255,255,255,0.4); }
    footer {
      padding: 3rem 0 4rem;
      text-align: center;
      border-top: 1px solid var(--border);
    }
    footer p { font-size: 0.8rem; color: var(--text-tertiary); }
    footer p a { color: inherit; text-decoration: none; }
    footer p a:hover { color: var(--primary-bright); }
""" + LANG_ROW_CSS + """    .fade-in {
      opacity: 0;
      transform: translateY(16px);
      animation: fadeUp 0.6s ease forwards;
    }
    .fade-in:nth-child(1) { animation-delay: 0.1s; }
    .fade-in:nth-child(2) { animation-delay: 0.2s; }
    .fade-in:nth-child(3) { animation-delay: 0.3s; }
    .fade-in:nth-child(4) { animation-delay: 0.4s; }
    @keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }
""" + REDUCED_MOTION_CSS

SUB_CSS = """    :root {
      --bg: #0A1628;
      --bg-deep: #060D1A;
      --primary: #4A9EFF;
      --primary-bright: #8ECFFF;
      --text: #FFFFFF;
      --text-secondary: rgba(255,255,255,0.6);
      --text-tertiary: rgba(255,255,255,0.35);
      --surface: rgba(255,255,255,0.06);
      --border: rgba(255,255,255,0.08);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-weight: 300;
      min-height: 100vh;
      overflow-x: hidden;
    }
    body::before {
      content: '';
      position: fixed;
      top: -200px;
      left: 50%;
      transform: translateX(-50%);
      width: 800px;
      height: 800px;
      background: radial-gradient(ellipse, rgba(74,158,255,0.08) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }
    .container {
      max-width: 640px;
      margin: 0 auto;
      padding: 0 1.5rem;
      position: relative;
      z-index: 1;
    }
    header {
      padding: 5rem 0 3rem;
      text-align: center;
    }
    .back-link {
      display: inline-block;
      color: var(--primary-bright);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 400;
      letter-spacing: 0.04em;
      margin-bottom: 2.5rem;
      opacity: 0.7;
      transition: opacity 0.2s;
    }
    .back-link:hover { opacity: 1; }
    .page-title {
      font-family: 'DM Serif Display', serif;
      font-size: clamp(2rem, 6vw, 2.8rem);
      font-weight: 400;
      letter-spacing: -0.02em;
      color: var(--text);
      margin-bottom: 0.5rem;
    }
    .page-meta {
      font-size: 0.85rem;
      color: var(--text-tertiary);
      letter-spacing: 0.04em;
    }
    .divider {
      width: 40px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--primary), transparent);
      margin: 3rem auto;
    }
    section { margin-bottom: 2.5rem; }
    h2 {
      font-family: 'DM Serif Display', serif;
      font-size: 1.3rem;
      font-weight: 400;
      color: var(--text);
      margin-bottom: 0.85rem;
      letter-spacing: -0.01em;
    }
    p {
      font-size: 0.93rem;
      line-height: 1.75;
      color: var(--text-secondary);
    }
    p + p { margin-top: 0.75rem; }
    ul {
      list-style: none;
      margin-top: 0.75rem;
    }
    li {
      font-size: 0.93rem;
      line-height: 1.75;
      color: var(--text-secondary);
      padding-left: 1.4rem;
      position: relative;
      margin-bottom: 0.6rem;
    }
    li::before {
      content: '·';
      position: absolute;
      left: 0.4rem;
      color: var(--primary-bright);
    }
    li strong { color: var(--text); font-weight: 500; }
    .highlight-card {
      background: var(--surface);
      border: 1px solid rgba(74,158,255,0.15);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin: 1.5rem 0;
    }
    .highlight-card p {
      font-size: 0.9rem;
      color: var(--primary-bright);
    }
    .contact-link {
      color: var(--primary-bright);
      text-decoration: none;
      border-bottom: 1px solid rgba(142,207,255,0.3);
      padding-bottom: 2px;
      transition: border-color 0.2s, color 0.2s;
    }
    .contact-link:hover { color: #fff; border-color: rgba(255,255,255,0.4); }
    footer {
      padding: 3rem 0 4rem;
      text-align: center;
      border-top: 1px solid var(--border);
    }
    footer p { font-size: 0.8rem; color: var(--text-tertiary); }
    footer p a { color: inherit; text-decoration: none; }
    footer p a:hover { color: var(--primary-bright); }
""" + LANG_ROW_CSS + """    .fade-in {
      opacity: 0;
      transform: translateY(16px);
      animation: fadeUp 0.6s ease forwards;
    }
    .fade-in:nth-child(1) { animation-delay: 0.05s; }
    .fade-in:nth-child(2) { animation-delay: 0.15s; }
    .fade-in:nth-child(3) { animation-delay: 0.25s; }
    .fade-in:nth-child(4) { animation-delay: 0.35s; }
    .fade-in:nth-child(5) { animation-delay: 0.45s; }
    @keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }
""" + REDUCED_MOTION_CSS

CHANGELOG_CSS = SUB_CSS + """    .release { margin-bottom: 2.75rem; }
    .release + .release { border-top: 1px solid var(--border); padding-top: 2.75rem; }
    .release-head { display: flex; align-items: baseline; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.4rem; }
    .release-head h2 { margin-bottom: 0; }
    .release-date { font-size: 0.82rem; color: var(--text-tertiary); letter-spacing: 0.02em; }
    .badge {
      display: inline-block; font-size: 0.72rem; font-weight: 500;
      letter-spacing: 0.06em; text-transform: uppercase;
      padding: 0.28rem 0.62rem; border-radius: 999px; margin-bottom: 1rem;
      border: 1px solid rgba(74,158,255,0.35); color: var(--primary-bright);
    }
    .badge.review { border-color: rgba(255,190,90,0.5); color: #FFCF8E; }
    .badge.beta { border-color: rgba(61,207,207,0.5); color: #7EEAEA; }
    .release p a { color: var(--primary-bright); }
"""

LANDING_CSS = """  :root{
    --bg: #0A1628;
    --bg-deep: #060D14;
    --surface: rgba(245,248,252,0.045);
    --hairline: rgba(245,248,252,0.09);
    --teal: #3DCFCF;
    --teal-dim: rgba(61,207,207,0.18);
    --score-low: #4A9EFF;
    --score-mid: #A78BFA;
    --score-high: #FF5E5E;
    --text-1: #F5F8FC;
    --text-2: rgba(245,248,252,0.64);
    --text-3: rgba(245,248,252,0.38);
    --display: 'Fraunces', serif;
    --body: 'Work Sans', sans-serif;
    --mono: 'JetBrains Mono', monospace;
  }

  *{ box-sizing:border-box; margin:0; padding:0; }

  html{ scroll-behavior:smooth; }

  body{
    background:var(--bg);
    color:var(--text-1);
    font-family:var(--body);
    line-height:1.5;
    -webkit-font-smoothing:antialiased;
    overflow-x:hidden;
  }

  a{ color:inherit; }

  img{ max-width:100%; display:block; }

  :focus-visible{
    outline:2px solid var(--teal);
    outline-offset:3px;
    border-radius:4px;
  }

  .wrap{
    max-width:1080px;
    margin:0 auto;
    padding:0 24px;
  }

  .eyebrow{
    font-family:var(--mono);
    font-size:12px;
    letter-spacing:0.14em;
    text-transform:uppercase;
    color:var(--teal);
    display:flex;
    align-items:center;
    gap:10px;
  }
  .eyebrow::before{
    content:'';
    width:6px; height:6px;
    border-radius:50%;
    background:var(--teal);
    box-shadow:0 0 8px var(--teal);
  }

  h1,h2,h3{
    font-family:var(--display);
    font-weight:500;
    letter-spacing:-0.01em;
  }

  /* ---------- NAV ---------- */
  header{
    position:sticky; top:0; z-index:50;
    background:rgba(10,22,40,0.72);
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
    border-bottom:1px solid var(--hairline);
  }
  nav{
    display:flex; align-items:center; justify-content:space-between;
    padding:16px 24px;
    max-width:1080px; margin:0 auto;
  }
  .brand{
    display:flex; align-items:center; gap:10px;
    font-family:var(--display); font-weight:600; font-size:19px;
    text-decoration:none;
  }
  .brand img{ width:26px; height:26px; border-radius:7px; }
  .nav-links{ display:flex; gap:28px; margin-left:auto; margin-right:28px; }
  .nav-links a{
    font-family:var(--mono); font-size:13px; color:var(--text-2);
    text-decoration:none; transition:color .16s ease;
  }
  .nav-links a:hover{ color:var(--teal); }
  section[id]{ scroll-margin-top:72px; }
  .pulse-dot{
    width:6px; height:6px; border-radius:50%;
    background:var(--teal);
    box-shadow:0 0 8px var(--teal);
    animation:pulse 2.6s ease-in-out infinite;
  }
  @keyframes pulse{
    0%,100%{ opacity:1; }
    50%{ opacity:0.35; }
  }
  .nav-cta{
    font-family:var(--mono);
    font-size:13px;
    padding:9px 18px;
    border:1px solid var(--teal);
    border-radius:100px;
    text-decoration:none;
    color:var(--teal);
    transition:background .18s ease, color .18s ease;
    white-space:nowrap;
  }
  .nav-cta:hover{ background:var(--teal); color:var(--bg-deep); }
  .beta-cta{
    display:inline-block;
    margin-top:28px;
    font-family:var(--mono);
    font-size:14px;
    padding:12px 22px;
    border-radius:100px;
    text-decoration:none;
    background:var(--teal);
    color:var(--bg-deep);
    transition:opacity .18s ease;
  }
  .beta-cta:hover{ opacity:0.85; }
  .v2-showcase{ max-width:960px; margin:0 auto; }
  .v2-showcase img{ border-radius:18px; }
  .v2-zoom{ cursor:zoom-in; }
  .v2-zoom:focus-visible{ outline:2px solid var(--teal); outline-offset:4px; border-radius:18px; }
  .v2-hint{ margin-top:12px; text-align:center; font-size:13px; color:var(--text-3); }
  .v2-lightbox{
    border:0; padding:0; margin:0; width:100vw; height:100vh; max-width:none; max-height:none;
    background:rgba(6,13,20,0.96); color:var(--text-1);
  }
  .v2-lightbox::backdrop{ background:rgba(6,13,20,0.96); }
  .v2-lightbox-scroll{ width:100%; height:100%; overflow:auto; display:flex; align-items:center; cursor:zoom-out; }
  .v2-lightbox-scroll img{ display:block; margin:auto; width:min(96vw, 1800px); height:auto; border-radius:12px; }
  @media (max-width:700px){
    /* The overview's small print needs real pixels on a phone: scroll it sideways. */
    .v2-lightbox-scroll img{ width:1400px; max-width:none; margin:24px; }
  }
  .v2-close{
    position:fixed; top:16px; right:16px; z-index:1;
    width:44px; height:44px; border-radius:50%;
    border:1px solid var(--hairline); background:rgba(6,13,20,0.8); color:var(--text-1);
    font-size:26px; line-height:1; cursor:pointer;
  }
  .v2-close:focus-visible{ outline:2px solid var(--teal); outline-offset:2px; }

  /* ---------- HERO ---------- */
  .hero{
    padding:88px 0 64px;
    position:relative;
  }
  .hero-text{ max-width:720px; }
  .hero-shot{ max-width:1040px; margin:56px auto 0; }
  .hero .v2-hint{ max-width:none; margin:12px 0 0; font-size:13px; }
  .hero h1{
    font-size:clamp(34px, 5vw, 58px);
    line-height:1.06;
    margin:18px 0 22px;
    color:var(--text-1);
  }
  .hero h1 em{
    font-style:italic;
    color:var(--teal);
  }
  .hero p{
    font-size:17px;
    color:var(--text-2);
    max-width:46ch;
    margin-bottom:34px;
  }
  .cta-row{
    display:flex; gap:14px; flex-wrap:wrap;
  }
  .btn{
    font-family:var(--mono);
    font-size:14px;
    padding:13px 22px;
    border-radius:10px;
    text-decoration:none;
    display:inline-flex;
    align-items:center;
    gap:8px;
    transition:transform .16s ease, box-shadow .16s ease, opacity .16s ease;
  }
  .btn-primary{
    background:var(--teal);
    color:var(--bg-deep);
    font-weight:500;
  }
  .btn-primary:hover{ transform:translateY(-1px); box-shadow:0 8px 24px rgba(61,207,207,0.28); }
  .btn-ghost{
    border:1px solid var(--hairline);
    color:var(--text-2);
  }
  .btn-ghost:hover{ border-color:var(--teal); color:var(--teal); }

  .badge-link{ display:inline-block; }
  .badge-appstore{
    height:52px;
    width:auto;
    border-radius:10px;
    transition:transform .16s ease, box-shadow .16s ease;
  }
  .badge-appstore:hover{
    transform:translateY(-1px);
    box-shadow:0 8px 24px rgba(0,0,0,0.4);
  }


  /* ---------- SECTION SHELL ---------- */
  section{ padding:96px 0; }
  .section-head{ max-width:640px; margin-bottom:52px; }
  .section-head h2{
    font-size:clamp(26px, 3.4vw, 38px);
    line-height:1.14;
    margin-top:16px;
    color:var(--text-1);
  }
  .section-head p{
    color:var(--text-2);
    margin-top:16px;
    font-size:16px;
    max-width:56ch;
  }

  /* ---------- BASELINE / PROBLEM ---------- */
  .baseline{ background:var(--bg-deep); border-top:1px solid var(--hairline); border-bottom:1px solid var(--hairline); }
  .baseline-figure{
    border:1px solid var(--hairline);
    border-radius:20px;
    padding:32px 28px;
    background:rgba(245,248,252,0.02);
  }
  .baseline-figure svg{ width:100%; height:auto; display:block; }
  .baseline-legend{
    display:flex; gap:28px; margin-top:22px; flex-wrap:wrap;
    font-family:var(--mono); font-size:12.5px; color:var(--text-2);
  }
  .legend-item{ display:flex; align-items:center; gap:8px; }
  .legend-swatch{ width:22px; height:2px; }
  .legend-swatch.dashed{ background:repeating-linear-gradient(90deg, var(--text-3) 0 6px, transparent 6px 11px); }
  .legend-swatch.solid{ background:var(--teal); box-shadow:0 0 6px var(--teal); }

  /* ---------- PRINCIPLES ---------- */
  .principles-grid{
    display:grid;
    grid-template-columns:repeat(2, 1fr);
    gap:1px;
    background:var(--hairline);
    border:1px solid var(--hairline);
    border-radius:20px;
    overflow:hidden;
  }
  .principle{
    background:var(--bg);
    padding:32px 28px;
  }
  .principle .tag{
    font-family:var(--mono);
    font-size:11px;
    letter-spacing:0.08em;
    color:var(--teal);
    text-transform:uppercase;
    margin-bottom:14px;
    display:block;
  }
  .principle p{
    color:var(--text-2);
    font-size:15px;
  }
  .principle strong{ color:var(--text-1); font-weight:500; }
  .principle.wide{ grid-column:1 / -1; }
  .principle a{ color:var(--teal); text-decoration:underline; text-underline-offset:3px; }

  /* ---------- WATCH SHOWCASE ---------- */
  /* Montages of several watches keep the app's background, framed as a card like the
     rest of the page's panels. Single watches (the tours) are transparent and sit on the page. */
  .frame{
    display:block;
    border:1px solid var(--hairline);
    border-radius:20px;
    overflow:hidden;
  }
  .frame img{ width:100%; height:auto; display:block; }

  .watch-showcase{ max-width:720px; margin:0 auto; }

  .tour-grid{
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:28px;
  }
  .tour-item img{ width:100%; height:auto; display:block; margin-bottom:12px; }
  .tour-item .tag{
    font-family:var(--mono);
    font-size:11px;
    letter-spacing:0.08em;
    color:var(--teal);
    text-transform:uppercase;
    display:block;
    margin-bottom:8px;
  }
  .tour-item p{
    color:var(--text-2);
    font-size:14.5px;
  }
  .tier{
    display:inline-block; margin-left:10px; padding:2px 8px;
    border:1px solid var(--hairline); border-radius:100px;
    font-size:10px; letter-spacing:0.08em; color:var(--text-3); vertical-align:1px;
  }
  .tier-pro{ border-color:rgba(61,207,207,0.45); color:var(--teal); }

  /* ---------- PRICING ---------- */
  .plans{ display:grid; grid-template-columns:repeat(2, 1fr); gap:24px; }
  .plan{
    border:1px solid var(--hairline); border-radius:20px;
    padding:32px 28px; background:var(--bg);
  }
  .plan-pro{ border-color:rgba(61,207,207,0.45); box-shadow:0 0 40px rgba(61,207,207,0.08); }
  .plan .tag{
    font-family:var(--mono); font-size:11px; letter-spacing:0.08em;
    color:var(--teal); text-transform:uppercase; display:block;
  }
  .plan-sub{ color:var(--text-1); font-size:20px; margin:10px 0 20px; }
  .plan ul{ list-style:none; padding:0; margin:0; }
  .plan li{
    color:var(--text-2); font-size:15px; padding:9px 0 9px 22px; position:relative;
    border-top:1px solid var(--hairline);
  }
  .plan li::before{ content:""; position:absolute; left:2px; top:17px; width:8px; height:8px; border-radius:50%; background:var(--teal); opacity:0.7; }

  /* ---------- CLOSING ---------- */
  .closing{
    text-align:center;
    padding:110px 0 100px;
    background:radial-gradient(ellipse at 50% 0%, rgba(61,207,207,0.08), transparent 60%);
  }
  .closing h2{
    font-size:clamp(30px, 5vw, 48px);
    margin-bottom:16px;
  }
  .closing h2 em{ font-style:italic; color:var(--teal); }
  .closing p{
    color:var(--text-2);
    max-width:50ch;
    margin:0 auto 36px;
    font-size:16px;
  }
  .closing .cta-row{ justify-content:center; }

  /* ---------- FOOTER ---------- */
  footer{
    border-top:1px solid var(--hairline);
    padding:36px 0;
  }
  .footer-row{
    display:flex; justify-content:space-between; align-items:center;
    flex-wrap:wrap; gap:16px;
    font-family:var(--mono); font-size:12px; color:var(--text-3);
  }
  .footer-links{ display:flex; gap:22px; flex-wrap:wrap; }
  .footer-links a{ text-decoration:none; color:var(--text-3); transition:color .16s ease; }
  .footer-links a:hover{ color:var(--teal); }
  .lang-row{ margin-top:14px; font-family:var(--mono); font-size:11px; letter-spacing:0.04em; color:var(--text-3); }
  .lang-row a, .lang-row span{ color:var(--text-3); text-decoration:none; }
  .lang-row a:hover{ color:var(--teal); }
  .lang-row span{ color:var(--teal); }

  @media (max-width:820px){
    .plans{ grid-template-columns:1fr; }
    .nav-links{ display:none; }
    .principles-grid{ grid-template-columns:1fr; }
    .tour-grid{ grid-template-columns:1fr; gap:40px; }
    .hero{ padding-top:56px; }
    section{ padding:72px 0; }
  }

  @media (prefers-reduced-motion: reduce){
    .pulse-dot{ animation:none; }
    *{ scroll-behavior:auto !important; }
  }
"""

HEAD = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
{seo}
  <link rel="icon" href="/assets/icon-1024.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet" />
  <style>
{css}  </style>
</head>
"""

LANDING_HEAD = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{seo}
{jsonld}
<link rel="icon" href="/assets/icon-1024.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Work+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{css}</style>
</head>
"""

def footer(t, page, code):
    return f"""    <footer>
      <p>© 2026 Vela HRV · {t['rights']} · <a href="{path_for(code, 'legal')}">{LEGAL[code]['footer']}</a></p>
      {lang_row(page, code, t['lang_label'])}
    </footer>"""

def render_support(code, t):
    # An entry can carry a third element, its anchor id, so other pages can link to it.
    # Answers may hold {legal} and {appstore}, filled in here.
    def faq_item(q, a, anchor=None):
        a = a.replace("{legal}", path_for(code, "legal")).replace("{appstore}", APPSTORE_URL)
        attr = f' id="{anchor}"' if anchor else ""
        return f'''        <div class="faq-item"{attr}>
          <h3>{q}</h3>
          <p>{a}</p>
        </div>'''
    faqs = "\n\n".join(faq_item(*item) for item in t["faq"])
    return HEAD.format(lang=code, title=t["support_title"], css=SUPPORT_CSS,
                       seo=seo_head(code, "support", t["support_title"], t["about_p1"])) + f"""<body>
  <div class="container">
    <header>
      <a class="back-link" href="{path_for(code, 'landing')}">{t['back_home']}</a>
      {HERO_SVG}
      <h1 class="app-name">Vela HRV</h1>
      <p class="app-tagline">Apple Watch · Stress Tracking</p>
    </header>

    <div class="fade-in">
      <section>
        <h2>{t['about_h']}</h2>
        <p>{t['about_p1']}</p>
        <p>{t['about_p2']}</p>
      </section>
    </div>

    <div class="divider"></div>

    <div class="fade-in">
      <section>
        <h2>{t['faq_h']}</h2>

{faqs}
      </section>
    </div>

    <div class="divider"></div>

    <div class="fade-in">
      <section>
        <h2>{t['contact_h']}</h2>
        <div class="contact-card">
          <p>{t['contact_p']}</p>
          <a class="contact-link" href="mailto:{MAIL}">{MAIL}</a>
        </div>
      </section>
    </div>

{footer(t, 'support', code)}
  </div>
</body>
</html>
"""

def render_privacy(code, t):
    p = t["privacy"]
    sections = "\n".join(
        f"""    <div class="fade-in">
      <section>
        <h2>{h}</h2>
        {"".join(f'<p>{x}</p>' for x in ps)}
      </section>
    </div>"""
        for h, ps in p["sections"])
    return HEAD.format(lang=code, title=p["title_tag"], css=SUB_CSS,
                       seo=seo_head(code, "privacy", p["title_tag"], p["highlight"])) + f"""<body>
  <div class="container">
    <header>
      <a class="back-link" href="{path_for(code, 'support')}">{t['back']}</a>
      <h1 class="page-title">{p['title']}</h1>
      <p class="page-meta">{p['updated']}</p>
    </header>

    <div class="highlight-card fade-in">
      <p>{p['highlight']}</p>
    </div>

    <div class="divider"></div>

{sections}
    <div class="fade-in">
      <section>
        <h2>{p['contact_h']}</h2>
        <p>{p['contact_pre']}<a class="contact-link" href="mailto:{MAIL}">{MAIL}</a>{p['contact_post']}</p>
      </section>
    </div>

{footer(t, 'privacy', code)}
  </div>
</body>
</html>
"""

def render_a11y(code, t):
    a = t["a11y"]
    lis = "\n".join(f"          <li><strong>{s}</strong> {d}</li>" for s, d in a["items"])
    return HEAD.format(lang=code, title=a["title_tag"], css=SUB_CSS,
                       seo=seo_head(code, "accessibility", a["title_tag"], a["highlight"])) + f"""<body>
  <div class="container">
    <header>
      <a class="back-link" href="{path_for(code, 'support')}">{t['back']}</a>
      <h1 class="page-title">{a['title']}</h1>
      <p class="page-meta">{a['updated']}</p>
    </header>

    <div class="highlight-card fade-in">
      <p>{a['highlight']}</p>
    </div>

    <div class="divider"></div>

    <div class="fade-in">
      <section>
        <h2>{a['approach_h']}</h2>
        <p>{a['approach_p']}</p>
      </section>
    </div>

    <div class="fade-in">
      <section>
        <h2>{a['supported_h']}</h2>
        <ul>
{lis}
        </ul>
        <p>{a['no_media']}</p>
      </section>
    </div>

    <div class="fade-in">
      <section>
        <h2>{a['verify_h']}</h2>
        <p>{a['verify_p']}</p>
      </section>
    </div>

    <div class="fade-in">
      <section>
        <h2>{a['feedback_h']}</h2>
        <p>{a['feedback_pre']}<a class="contact-link" href="mailto:{MAIL}">{MAIL}</a>{a['feedback_post']}</p>
      </section>
    </div>

{footer(t, 'accessibility', code)}
  </div>
</body>
</html>
"""

def render_changelog(code, t):
    c = t["changelog"]
    blocks = []
    for e in c["entries"]:
        status = e.get("status")
        if status == "review":
            badge = f'\n        <span class="badge review">{c["status_review"]}</span>'
            note = f'\n        <p>{c["unreleased_note"]}</p>'
        elif status == "beta":
            badge = f'\n        <span class="badge beta">{c["status_beta"]}</span>'
            note = f'\n        <p>{c["beta_note"]}</p>'
        else:
            badge = note = ""
        changes = "\n".join(f"          <li>{x}</li>" for x in e["changes"])
        blocks.append(f"""    <div class="fade-in">
      <section class="release">
        <div class="release-head">
          <h2>{e['version']}</h2>
          <span class="release-date">{e['date']}</span>
        </div>{badge}{note}
        <ul>
{changes}
        </ul>
      </section>
    </div>""")
    body = "\n".join(blocks)
    return HEAD.format(lang=code, title=c["title_tag"], css=CHANGELOG_CSS,
                       seo=seo_head(code, "changelog", c["title_tag"], c["intro"])) + f"""<body>
  <div class="container">
    <header>
      <a class="back-link" href="{path_for(code, 'landing')}">{t['back_home']}</a>
      <h1 class="page-title">{c['title']}</h1>
      <p class="page-meta">{c['intro']}</p>
    </header>

    <div class="divider"></div>

{body}

{footer(t, 'changelog', code)}
  </div>
</body>
</html>
"""

def render_landing(code, t):
    L = t["landing"]
    V = L["v2"]
    # The fifth principle (wellness, not medicine) spans the whole grid and links to the FAQ
    # entry that explains why there's no health certification.
    faq_link = path_for(code, "support") + "#medical"
    principles = "\n".join(
        f'''        <div class="principle{' wide' if i == 4 else ''}">
          <span class="tag">{tag}</span>
          <p><strong>{strong}</strong> {rest.replace("{faq}", faq_link)}</p>
        </div>'''
        for i, (tag, strong, rest) in enumerate(L["principles"]))

    def tour(items, images, tier=None):
        # tier: one entry per item, "free" / "pro" / None, shown as a small badge next to the tag.
        tier = tier or [None] * len(items)
        badge = {"free": f'<span class="tier">{L["tier_free"]}</span>',
                 "pro": f'<span class="tier tier-pro">{L["tier_pro"]}</span>', None: ""}
        return "\n".join(
            f'''        <div class="tour-item">
          <img src="/assets/{img}-{code}.webp" alt="{alt}" width="1200" height="1200" loading="lazy" decoding="async">
          <span class="tag">{tag}{badge[tr]}</span>
          <p>{p}</p>
        </div>'''
            for (tag, p, alt), img, tr in zip(items, images, tier))

    def plan(title, sub, items, cls):
        lis = "\n".join(f"            <li>{i}</li>" for i in items)
        return f'''        <div class="plan {cls}">
          <span class="tag">{title}</span>
          <p class="plan-sub">{sub}</p>
          <ul>
{lis}
          </ul>
        </div>'''

    return LANDING_HEAD.format(lang=code, title=L["title_tag"], css=LANDING_CSS,
                               seo=seo_head(code, "landing", L["title_tag"], L["meta_desc"]),
                               jsonld=app_json_ld(code, t)) + f"""<body>

<header>
  <nav>
    <a class="brand" href="#top">
      <img src="/assets/icon-1024.png" alt="">
      vela
    </a>
    <div class="nav-links">
      <a href="#battery">{L['nav_battery']}</a>
      <a href="#stress">{L['nav_stress']}</a>
      <a href="#pricing">{L['nav_pricing']}</a>
    </div>
    <a class="nav-cta" href="{APPSTORE_URL}" target="_blank" rel="noopener">{L['nav_cta']}</a>
  </nav>
</header>

<main id="top">

  <section class="hero">
    <div class="wrap">
      <div class="hero-text">
        <p class="eyebrow">{L['eyebrow1']}</p>
        <h1>{L['h1']}</h1>
        <p>{L['hero_p']}</p>
        <div class="cta-row">
          <a class="badge-link" href="{APPSTORE_URL}" target="_blank" rel="noopener">
            <img class="badge-appstore" src="/assets/app-store-badge-white.svg" alt="{L['badge_alt']}">
          </a>
        </div>
      </div>
      <div class="hero-shot">
        <a class="frame v2-zoom" href="/assets/{V2_IMAGE[code]}" aria-haspopup="dialog">
          <img src="/assets/{V2_IMAGE[code]}" alt="{V['alt']}" width="2400" height="1600" decoding="async">
        </a>
        <p class="v2-hint">{V['zoom']}</p>
      </div>
      <dialog class="v2-lightbox" id="v2-lightbox" aria-label="{L['h1_plain']}">
        <button class="v2-close" type="button" aria-label="{V['close']}">×</button>
        <div class="v2-lightbox-scroll">
          <img src="/assets/{V2_IMAGE[code]}" alt="{V['alt']}" width="2400" height="1600" loading="lazy" decoding="async">
        </div>
      </dialog>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['story_eyebrow']}</p>
        <h2>{L['story_h2']}</h2>
        <p>{L['story_p']}</p>
      </div>
    </div>
  </section>

  <section class="baseline">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['baseline_eyebrow']}</p>
        <h2>{L['baseline_h2']}</h2>
        <p>{L['baseline_p']}</p>
      </div>
      <div class="baseline-figure">
        <svg viewBox="0 0 800 180" preserveAspectRatio="none">
          <line x1="0" y1="70" x2="800" y2="70" stroke="rgba(245,248,252,0.28)" stroke-width="1.5" stroke-dasharray="6 7"/>
          <path d="M0,120 C40,60 80,150 120,90 C160,40 200,140 240,100 C280,50 320,130 360,80 C400,110 440,55 480,120 C520,70 560,150 600,90 C640,50 680,130 720,95 C750,75 780,110 800,90"
                fill="none" stroke="var(--score-mid)" stroke-width="2" opacity="0.75"/>
          <path d="M0,95 C60,88 120,100 180,92 C240,85 300,96 360,90 C420,86 480,93 540,88 C600,85 660,90 720,87 C750,86 780,88 800,87"
                fill="none" stroke="#3DCFCF" stroke-width="2.5" style="filter:drop-shadow(0 0 6px rgba(61,207,207,0.55))"/>
        </svg>
        <div class="baseline-legend">
          <div class="legend-item"><span class="legend-swatch dashed"></span> {L['legend1']}</div>
          <div class="legend-item"><span class="legend-swatch" style="background:var(--score-mid)"></span> {L['legend2']}</div>
          <div class="legend-item"><span class="legend-swatch solid"></span> {L['legend3']}</div>
        </div>
      </div>
    </div>
  </section>

  <section id="battery">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['battery_eyebrow']}</p>
        <h2>{V['h2']}</h2>
        <p>{L['battery_p']}</p>
      </div>
      <div class="tour-grid">
{tour(L['battery_tour'], BATTERY_TOUR, ["free", "pro", "pro"])}
      </div>
    </div>
  </section>

  <section id="stress">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['stress_eyebrow']}</p>
        <h2>{L['stress_h2']}</h2>
        <p>{L['stress_p']}</p>
      </div>
      <div class="tour-grid">
{tour(L['tour'], STRESS_TOUR)}
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['principles_eyebrow']}</p>
        <h2>{L['principles_h2']}</h2>
      </div>
      <div class="principles-grid">
{principles}
      </div>
    </div>
  </section>

  <section id="pricing" class="baseline">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['pricing_eyebrow']}</p>
        <h2>{L['pricing_h2']}</h2>
        <p>{L['pricing_p']}</p>
      </div>
      <div class="plans">
{plan(L['tier_free'], L['free_sub'], L['free_items'], "plan-free")}
{plan("Vela Pro", L['pro_sub'], L['pro_items'], "plan-pro")}
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['onboarding_eyebrow']}</p>
        <h2>{L['onboarding_h2']}</h2>
        <p>{L['onboarding_p']}</p>
      </div>
      <div class="watch-showcase">
        <div class="frame">
          <img src="/assets/onboarding-{code}.jpg" alt="{L['onboarding_alt']}" width="1920" height="1920" loading="lazy" decoding="async">
        </div>
      </div>
    </div>
  </section>

  <section class="closing">
    <div class="wrap">
      <p class="eyebrow" style="justify-content:center">{L['closing_eyebrow']}</p>
      <h2>{L['closing_h2']}</h2>
      <p>{L['closing_p']}</p>
      <div class="cta-row">
        <a class="badge-link" href="{APPSTORE_URL}" target="_blank" rel="noopener">
          <img class="badge-appstore" src="/assets/app-store-badge-white.svg" alt="{L['badge_alt']}">
        </a>
      </div>
    </div>
  </section>

</main>

<footer>
  <div class="wrap footer-row">
    <span>© 2026 Vela</span>
    <div class="footer-links">
      <a href="{path_for(code, 'support')}">{L['footer_support']}</a>
      <a href="{path_for(code, 'changelog')}">{L['footer_changelog']}</a>
      <a href="{path_for(code, 'privacy')}">{L['footer_privacy']}</a>
      <a href="{path_for(code, 'legal')}">{LEGAL[code]['footer']}</a>
      <a href="mailto:{MAIL}">{L['footer_contact']}</a>
    </div>
  </div>
  <div class="wrap">
    {lang_row('landing', code, t['lang_label'])}
  </div>
</footer>

<script>
(function(){{
  var zoom = document.querySelector('.v2-zoom');
  var box = document.getElementById('v2-lightbox');
  if(!zoom || !box || typeof box.showModal !== 'function') return;  // no dialog support: the link opens the image
  zoom.addEventListener('click', function(e){{ e.preventDefault(); box.showModal(); }});
  box.querySelector('.v2-close').addEventListener('click', function(){{ box.close(); }});
  box.addEventListener('click', function(e){{
    // On a phone the image is scrolled sideways, so only a tap off the image closes.
    if(e.target === box || e.target.classList.contains('v2-lightbox-scroll') || window.innerWidth > 700) box.close();
  }});
  box.addEventListener('close', function(){{ zoom.focus(); }});
}})();
</script>

</body>
</html>
"""

# ---------------------------------------------------------------- content

L = {}

L["es"] = {
  "lang_label": "Idioma", "back": "← Volver al soporte", "back_home": "← Volver a Vela", "rights": "Todos los derechos reservados",
  "support_title": "Vela HRV — Soporte",
  "about_h": "Sobre la app",
  "about_p1": "Vela mide tu nivel de estrés usando la variabilidad de la frecuencia cardíaca (HRV) directamente desde tu Apple Watch. Todo el procesamiento ocurre en tu dispositivo — tus datos no salen de tu Apple Watch ni de tu iCloud privado.",
  "about_p2": "Durante los primeros días, Vela construye tu baseline personal para que cada lectura tenga sentido para tu cuerpo, no para una media estadística.",
  "faq_h": "Preguntas frecuentes",
  "faq": [
    ("¿Qué Apple Watch necesito?", "Vela requiere Apple Watch con watchOS 26 o superior. Funciona como app independiente — no necesita el iPhone abierto para medir."),
    ("¿Por qué tarda unos días en mostrar mi score?", "Vela necesita conocer tu HRV personal antes de calcular un score con sentido. Durante los primeros 7–14 días construye tu baseline — a partir de ahí, cada lectura refleja tu estado real."),
    ("¿Dónde se guardan mis datos?", "Tus datos se sincronizan de forma privada a través de tu propio iCloud. Vela no tiene servidores propios — nunca enviamos ni almacenamos tus datos fuera de tu cuenta."),
    ("¿Qué permisos necesita Vela?", "Vela solicita acceso de solo lectura a HealthKit: la variabilidad de frecuencia cardíaca para tu score de estrés, y el sueño, los pasos, la energía activa, los entrenos y la frecuencia cardíaca para tu Batería. Son datos que tu Apple Watch ya recoge automáticamente. Si quieres, también te pide permiso para enviarte notificaciones con los avisos de estrés."),
  ],
  "contact_h": "Contacto y soporte",
  "contact_p": "¿Tienes alguna pregunta, has encontrado un error o quieres compartir feedback? Escríbenos directamente.",
  "privacy": {
    "title_tag": "Vela HRV — Política de Privacidad", "title": "Política de Privacidad",
    "updated": "Última actualización: noviembre 2026",
    "highlight": "Vela no recopila, transmite ni almacena ningún dato personal en servidores externos. Todo permanece en tu dispositivo y en tu iCloud privado.",
    "sections": [
      ("Qué datos utiliza Vela", [
        "Vela lee datos de Apple HealthKit, solo en modo lectura: la variabilidad de frecuencia cardíaca (HRV) para calcular tu score de estrés personal, y el sueño, los pasos, la energía activa, los entrenos, la frecuencia cardíaca y la frecuencia cardíaca en reposo para calcular tu Batería: cuánto la carga el sueño y qué la gasta durante el día. Estos datos ya los recoge automáticamente tu Apple Watch. Vela nunca escribe en HealthKit.",
        "Vela también almacena las lecturas que calcula: tu historial de score de estrés, tu baseline personal de HRV, las muestras de HRV usadas para el cálculo del baseline y los niveles de tu Batería."]),
      ("Dónde viven tus datos", [
        "Todos los datos se almacenan localmente en tu Apple Watch y se sincronizan de forma privada a través de tu propia cuenta de iCloud usando el framework CloudKit de Apple. Vela no tiene servidores. Ningún dato pasa nunca por sistemas propiedad de Vela.",
        "Solo tú puedes acceder a tus datos. Ni nosotros ni terceros."]),
      ("Terceros", [
        "Vela no comparte ningún dato con terceros. No utilizamos servicios de analítica, SDKs publicitarios ni herramientas de seguimiento externas."]),
      ("Datos de salud", [
        "Vela accede a datos de salud únicamente para proporcionar su funcionalidad principal: medir y hacer seguimiento de tu nivel de estrés y de tu Batería. Los datos de salud nunca se usan con fines publicitarios ni se venden a ninguna parte."]),
      ("Compras", [
        "Vela Pro es una compra única dentro de la app que gestiona Apple a través del App Store. Vela nunca recibe tus datos de pago: la app solo comprueba en tu dispositivo, mediante StoreKit de Apple, si Vela Pro está desbloqueado."]),
      ("Menores", [
        "Vela no está diseñada específicamente para niños. Como no recopila datos de nadie, tampoco recopila datos de menores."]),
      ("Cambios en esta política", [
        "Si esta política de privacidad cambia, la versión actualizada se publicará en esta URL con una nueva fecha. El uso continuado de la app tras los cambios implica la aceptación de la política actualizada."]),
    ],
    "contact_h": "Contacto",
    "contact_pre": "¿Preguntas sobre esta política de privacidad? Escríbenos a ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Accesibilidad", "title": "Accesibilidad",
    "updated": "Última actualización: julio 2026",
    "highlight": "Vela está diseñada para poder usarse por completo sin ver la pantalla: todas las pantallas funcionan con VoiceOver y ninguna información depende únicamente del color.",
    "approach_h": "Nuestro enfoque",
    "approach_p": "Vela mide el estrés a través de la variabilidad de la frecuencia cardiaca en el Apple Watch. Entender tu propio cuerpo no debería depender de cómo ves, así que la accesibilidad se trata como una funcionalidad central: el principio rector es que una persona ciega pueda consultar su nivel de estrés, explorar su historial, leer sus análisis semanales y configurar la app de forma completamente autónoma.",
    "supported_h": "Compatibilidad en Apple Watch",
    "items": [
      ("VoiceOver.", "Todos los elementos tienen etiqueta, valor y descripción con significado. Los gráficos se exponen como Audio Graphs: el historial de estrés puede explorarse mediante sonido con la corona digital."),
      ("Texto más grande.", "La interfaz usa Dynamic Type en toda la app. Los indicadores compactos, como el anillo de puntuación, ofrecen el visor de contenido ampliado."),
      ("Interfaz oscura.", "La interfaz de Vela es oscura por diseño en todas las pantallas, sin destellos brillantes."),
      ("Diferenciar no solo con color.", "Los niveles de estrés se refuerzan siempre con una cifra y una palabra — nunca solo con color. Los gráficos añaden líneas de zona al activar “Diferenciar sin color”."),
      ("Contraste suficiente.", "Todo el texto cumple la ratio de contraste WCAG AA (4,5:1 o superior) sobre el fondo oscuro."),
      ("Reducir movimiento.", "Las animaciones se desactivan o se sustituyen por alternativas estáticas con “Reducir movimiento” activado. Vela también respeta Reducir transparencia y Texto en negrita."),
    ],
    "no_media": "Vela no contiene audio ni vídeo, por lo que los subtítulos y las audiodescripciones no aplican.",
    "verify_h": "Cómo lo verificamos",
    "verify_p": "Todas las pantallas pasan por las auditorías automáticas de accesibilidad de Apple — etiquetas, contraste, tamaño de las áreas táctiles y escalado de texto — como parte de la batería de tests de la app, junto con revisión manual con VoiceOver. Estas comprobaciones se repiten con cada cambio de interfaz, de modo que la accesibilidad no se degrada silenciosamente entre versiones.",
    "feedback_h": "Comentarios",
    "feedback_pre": "Si algo en Vela resulta difícil de usar con tecnología de asistencia, es un bug. Escríbenos a ",
    "feedback_post": " — los reportes de accesibilidad se priorizan para la siguiente versión.",
  },
  "landing": {
    "nav_cta": "Descargar",
    "nav_battery": "Batería", "nav_stress": "Estrés", "nav_pricing": "Precio",
    "title_tag": "Vela — Estrés y Batería para Apple Watch. Sin suscripción. Nunca.",
    "meta_desc": "Vela mide tu estrés y tu Batería en el Apple Watch contra tu propia línea base de HRV: cómo estás ahora, cuánto te ha cargado el sueño y en qué se te va la energía durante el día. Todo se calcula en el reloj. Sin suscripción, nunca.",
    "eyebrow1": "Estrés y Batería para Apple Watch",
    "h1": "Tu energía y tu calma no son <em>la media</em> de nadie.",
    "h1_plain": "Tu energía y tu calma no son la media de nadie.",
    "hero_p": "Vela lee tu variabilidad de ritmo cardíaco (SDNN) en el Apple Watch y la compara con tu propia línea base, no con un umbral de población. Con eso te dice cuánta energía te queda hoy, tu Batería, y cómo estás ahora, tu estrés. Todo el cálculo ocurre en el reloj. Nada pasa por nuestros servidores, porque no los tenemos.",
    "badge_alt": "Descargar en el App Store",
    "story_eyebrow": "Sobre el nombre", "story_h2": "Por qué “Vela”",
    "story_p": "“Vela” también es la vela de un barco — del latín velum. Un velero no lucha contra el viento: lo lee y ajusta el rumbo. Esa es la idea detrás de la app. En lugar de compararte con un estándar externo, Vela lee tu propia línea base personal y te ayuda a entender tus propios patrones. El estrés y el cansancio no se combaten: se leen, y se ajusta el rumbo.",
    "baseline_eyebrow": "Por qué el promedio no sirve",
    "baseline_h2": "25&nbsp;ms de HRV puede ser alto para ti y bajo para otra persona.",
    "baseline_p": "El HRV varía enormemente entre personas. Un umbral de población trata a todo el mundo igual — y por eso casi siempre se equivoca. Vela construye tu propia línea base a partir de tu historial real: si ya tienes datos de HRV en tu Apple Watch, puede empezar desde el primer día; si eres nuevo, tarda entre 7 y 14 días en asentarse. Y vale para las dos cosas: tu estrés se mide contra tu HRV de siempre, y lo que te carga una noche también.",
    "legend1": "Umbral genérico de población", "legend2": "Muestras individuales", "legend3": "Tu línea base personal",
    "principles_eyebrow": "Cómo funciona", "principles_h2": "Cuatro decisiones, tomadas para no cambiar de idea.",
    "principles": [
      ("On-device", "Todo el cálculo ocurre en tu Watch.", "HealthKit entrega los datos, el reloj hace el resto. Ni tu HRV, ni tu sueño, ni tu actividad salen de tu dispositivo hacia un servidor de Vela."),
      ("Tu iCloud, no el nuestro", "La sincronización usa tu propia cuenta de iCloud", "vía CloudKit. Vela no aloja tus datos en ningún sitio — no puede, porque no tiene dónde."),
      ("Sin rastreo", "Sin analítica, sin anuncios, sin SDK de terceros.", "Vela no sabe quién eres ni cuándo abres la app: lo único que sale del reloj va a tu propio iCloud."),
      ("Accesible de serie", "VoiceOver, Dynamic Type, Reduce Motion", "y 12 idiomas: castellano, català, euskara, galego, English, français, Deutsch, italiano, português, čeština, ελληνικά y 日本語."),
    ],
    "battery_eyebrow": "Batería · Nuevo en Vela 2.0",
    "battery_p": "Se carga solo mientras duermes, también con una siesta o con el sueño de día tras un turno de noche, y se gasta con el estrés, la actividad, los entrenos y las horas despierto. Si un día se te ha hecho largo, la Batería te enseña por qué.",
    "battery_tour": [
      ("Tu carga", "Cuánto te ha cargado la noche y de dónde sale: lo que has dormido y tu HRV durante el sueño frente a tu media.", "Pantalla de Vela con la carga de la noche: hasta 80, 27 puntos más durmiendo, 7 h 15 min de sueño y el HRV del sueño un 9 % por encima de la media."),
      ("La curva del día", "Cómo ha subido mientras dormías y cómo baja desde que te levantas, con cada entreno marcado a su hora.", "Curva de batería del día: recarga en verde durante la noche hasta 80 y descarga en azul durante el día hasta 47, con dos entrenos marcados."),
      ("En qué se ha ido", "Lo gastado desde que te despertaste, separado en estrés y actividad, entrenos y horas despierto. Describe lo que ha pasado, sin darte consejos.", "Desglose del gasto de hoy: 33 puntos desde que te despertaste, 7 por estrés y actividad, 12 por una hora de entreno y 14 por las horas de vigilia."),
    ],
    "tier_free": "Gratis", "tier_pro": "Pro",
    "stress_eyebrow": "Estrés", "stress_h2": "Un score, un estado, una tendencia.",
    "stress_p": "Tu nivel de estrés de ahora, el día hora a hora y qué significa cada rango. El color y la etiqueta de texto siempre van juntos, también pensado para quienes no distinguen bien los colores. Todo el estrés es gratis.",
    "pricing_eyebrow": "Precio", "pricing_h2": "Gratis para empezar. Pro, una sola vez.",
    "pricing_p": "Sin cuotas mensuales ni anuales. Vela Pro se paga una vez y es tuyo.",
    "free_sub": "Para todos",
    "free_items": [
      "Tu nivel de estrés en tiempo real, con su estado y su explicación",
      "El día de hoy hora a hora y el histórico de estrés",
      "Análisis semanales y avisos de estrés alto",
      "La carga de cada noche y de dónde sale",
      "Complicaciones de estrés y de la carga de la noche",
    ],
    "pro_sub": "Compra única",
    "pro_items": [
      "La Batería en directo, a lo largo del día",
      "La curva del día, con la recarga de la noche y cada entreno",
      "En qué se ha ido: estrés y actividad, entrenos y horas despierto",
      "Histórico de batería por mes, semana y día",
      "Complicaciones con la Batería en directo y las barras por hora de hoy",
    ],
    "tour_eyebrow": "Recorrido rápido", "tour_h2": "Tres pantallas, cada una con un único trabajo.",
    "tour": [
      ("Score actual", "Un número, un estado, calculado enteramente en el reloj — sin esperar a que nada sincronice.", "Pantalla principal de Vela mostrando un nivel de estrés de 34, estado Bajo, calculado en el momento."),
      ("Tendencia", "Cada lectura del día, comparada contra tu propia línea discontinua — no contra la de nadie más.", "Gráfico de tendencia con la media de estrés del día y las lecturas de cada hora, comparadas contra la línea base personal."),
      ("Rangos explicados", "Nada de cifras crípticas: cada rango dice qué significa y qué esperar de él.", "Pantalla de explicación de los rangos de estrés: Normal entre 40 y 69, Alto entre 70 y 100."),
    ],
    "onboarding_eyebrow": "Así empiezas", "onboarding_h2": "Te pedimos permiso antes de medir nada.",
    "onboarding_p": "Vela te pide acceso a tus datos de salud de forma explícita, no en la letra pequeña, y te dice para qué usa cada uno. Y si eres nuevo midiendo HRV, te dice cuánto falta para tener una línea base fiable — sin fingir que el primer día ya sabe quién eres.",
    "onboarding_alt": "Dos pasos de la bienvenida de Vela en Apple Watch: la pantalla de bienvenida y la petición de acceso a los datos de salud, que explica para qué se usa cada uno.",
    "closing_eyebrow": "Descárgala hoy", "closing_h2": "Sin suscripción. <em>Nunca.</em>",
    "closing_p": "Vela es gratis en el App Store para Apple Watch, con Vela Pro como compra única.",
    "footer_support": "Soporte", "footer_privacy": "Privacidad", "footer_contact": "Contacto",
  },
}

L["en"] = {
  "lang_label": "Language", "back": "← Back to support", "back_home": "← Back to Vela", "rights": "All rights reserved",
  "support_title": "Vela HRV — Support",
  "about_h": "About the app",
  "about_p1": "Vela measures your stress level using heart rate variability (HRV) directly from your Apple Watch. All processing happens on your device — your data never leaves your Apple Watch or your private iCloud.",
  "about_p2": "During the first few days, Vela builds your personal baseline so every reading makes sense for your body, not for a statistical average.",
  "faq_h": "Frequently asked questions",
  "faq": [
    ("Which Apple Watch do I need?", "Vela requires Apple Watch with watchOS 26 or later. It works as a standalone app — your iPhone doesn't need to be nearby to take a measurement."),
    ("Why does it take a few days to show my score?", "Vela needs to learn your personal HRV before it can calculate a meaningful score. During the first 7–14 days it builds your baseline — from then on, every reading reflects your actual state."),
    ("Where is my data stored?", "Your data syncs privately through your own iCloud. Vela has no servers of its own — we never send or store your data outside your account."),
    ("What permissions does Vela need?", "Vela requests read-only access to HealthKit: heart rate variability for your stress score, and sleep, steps, active energy, workouts and heart rate for your Battery. This is data your Apple Watch already collects automatically. If you want, it also asks for permission to send you notifications for stress alerts."),
  ],
  "contact_h": "Contact & support",
  "contact_p": "Have a question, found a bug, or want to share feedback? Reach out directly.",
  "privacy": {
    "title_tag": "Vela HRV — Privacy Policy", "title": "Privacy Policy",
    "updated": "Last updated: November 2026",
    "highlight": "Vela does not collect, transmit, or store any personal data on external servers. Everything stays on your device and your private iCloud.",
    "sections": [
      ("What data Vela uses", [
        "Vela reads data from Apple HealthKit, read-only: heart rate variability (HRV) to calculate your personal stress score, and sleep, steps, active energy, workouts, heart rate and resting heart rate to calculate your Battery — how much sleep charges it and what drains it during the day. Your Apple Watch already collects this data automatically. Vela never writes to HealthKit.",
        "Vela also stores the readings it calculates — your stress score history, your personal HRV baseline, the raw HRV samples used to calculate it, and your Battery levels."]),
      ("Where your data lives", [
        "All data is stored locally on your Apple Watch and synced privately through your own iCloud account using Apple's CloudKit framework. Vela has no servers. No data ever passes through systems owned or operated by Vela.",
        "Only you can access your data. Not us, not third parties."]),
      ("Third parties", [
        "Vela does not share any data with third parties. We do not use analytics services, advertising SDKs, or any external tracking tools."]),
      ("Health data", [
        "Vela accesses health data solely to provide its core functionality — measuring and tracking your stress level and your Battery. Health data is never used for advertising or sold to any party."]),
      ("Purchases", [
        "Vela Pro is a one-time in-app purchase processed by Apple through the App Store. Vela never receives your payment details: the app only checks on your device, through Apple's StoreKit, whether Vela Pro is unlocked."]),
      ("Children", [
        "Vela is not designed specifically for children. Because it does not collect data from anyone, it does not collect data from children either."]),
      ("Changes to this policy", [
        "If this privacy policy changes, the updated version will be published at this URL with a new date. Continued use of the app after changes constitutes acceptance of the updated policy."]),
    ],
    "contact_h": "Contact",
    "contact_pre": "Questions about this privacy policy? Reach out at ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Accessibility", "title": "Accessibility",
    "updated": "Last updated: July 2026",
    "highlight": "Vela is designed to be fully usable without sight: every screen works with VoiceOver, and no information is ever conveyed by color alone.",
    "approach_h": "Our approach",
    "approach_p": "Vela measures stress through heart rate variability on Apple Watch. Understanding your own body should not depend on how you see, so accessibility is treated as a core feature: the guiding principle is that a blind user can check their stress level, explore their history, read their weekly insights and configure the app completely on their own.",
    "supported_h": "Supported on Apple Watch",
    "items": [
      ("VoiceOver.", "Every element has a meaningful label, value and hint. Charts are exposed as Audio Graphs, so stress history can be explored by sound with the Digital Crown."),
      ("Larger text.", "The interface uses Dynamic Type throughout. Compact displays, such as the stress score ring, offer the Large Content Viewer."),
      ("Dark interface.", "Vela's interface is dark by design on every screen, with no bright flashes."),
      ("Differentiate without color.", "Stress levels are always reinforced with a number and a word — never color alone. Charts add zone lines when “Differentiate Without Color” is enabled."),
      ("Sufficient contrast.", "All text meets the WCAG AA contrast ratio (4.5:1 or better) against the dark background."),
      ("Reduced motion.", "Animations are disabled or replaced with static alternatives when “Reduce Motion” is on. Vela also honors Reduce Transparency and Bold Text."),
    ],
    "no_media": "Vela contains no audio or video content, so captions and audio descriptions do not apply.",
    "verify_h": "How we verify it",
    "verify_p": "Every screen runs through Apple's automated accessibility audits — checking labels, contrast, tap target sizes and text scaling — as part of the app's test suite, alongside manual VoiceOver review. These checks run again whenever the interface changes, so accessibility does not regress silently between versions.",
    "feedback_h": "Feedback",
    "feedback_pre": "If anything in Vela is hard to use with assistive technology, that is a bug. Please write to ",
    "feedback_post": " — accessibility reports are prioritized for the next release.",
  },
  "landing": {
    "nav_cta": "Download",
    "title_tag": "Vela — HRV for Apple Watch. No subscription. Ever.",
    "meta_desc": "Vela measures your heart rate variability (HRV/SDNN) on Apple Watch and builds your own personal baseline. Everything is processed on the watch. Syncs with your iCloud. No subscription, ever.",
    "eyebrow1": "HRV for Apple Watch",
    "h1": "Your calm isn't <em>anyone else's average</em>.",
    "hero_p": "Vela measures your heart rate variability (SDNN) directly on your Apple Watch and builds a baseline that's yours — not a generic population threshold. All the computation happens on the watch. Nothing ever passes through our servers, because we don't have any.",
    "badge_alt": "Download on the App Store",
    "story_eyebrow": "About the name", "story_h2": "Why “Vela”",
    "story_p": "“Vela” is also the Spanish word for a boat's sail — from the Latin velum. A sailboat doesn't fight the wind: it reads it and adjusts course. That's the idea behind the app. Instead of comparing you to an external standard, Vela reads your own personal baseline and helps you understand your own patterns. Stress isn't something to fight — it's something to read and adjust to.",
    "baseline_eyebrow": "Why the average doesn't work",
    "baseline_h2": "25&nbsp;ms of HRV can be high for you and low for someone else.",
    "baseline_p": "HRV varies enormously between people. A population threshold treats everyone the same — which is exactly why it's almost always wrong. Vela builds your own baseline from your real history: if you already have HRV data on your Apple Watch, it can start from day one; if you're new, it takes 7–14 days to settle.",
    "legend1": "Generic population threshold", "legend2": "Individual samples", "legend3": "Your personal baseline",
    "principles_eyebrow": "How it works", "principles_h2": "Four decisions, made to not change our minds.",
    "principles": [
      ("On-device", "All the computation happens on your Watch.", "HealthKit provides the data, the watch does the rest. No HRV data ever leaves your device toward a Vela server."),
      ("Your iCloud, not ours", "Syncing uses your own iCloud account", "via CloudKit. Vela doesn't host your data anywhere — it can't, because it has nowhere to."),
      ("No subscription. Ever.", "No monthly or yearly fees.", "Vela is free. Vela Pro is a one-time purchase: you pay once and it's yours — never a subscription."),
      ("Accessible by default", "VoiceOver, Dynamic Type, Reduce Motion", "and 12 languages: Spanish, Catalan, Basque, Galician, English, French, German, Italian, Portuguese, Czech, Greek, and Japanese."),
    ],
    "stress_h2": "One score, one state, one trend.",
    "tour_eyebrow": "Quick tour", "tour_h2": "Three screens, each with a single job.",
    "tour": [
      ("Current score", "One number, one state, computed entirely on the watch — no waiting for anything to sync.", "Vela's main screen showing a stress level of 34, Low status, calculated in the moment."),
      ("Trend", "Every reading of the day, compared against your own dashed line — not anyone else's.", "Trend chart with the day's average stress and hourly readings, compared against the personal baseline."),
      ("Ranges explained", "No cryptic numbers: every range says what it means and what to expect.", "Screen explaining the stress ranges: Normal between 40 and 69, High between 70 and 100."),
    ],
    "onboarding_eyebrow": "Getting started", "onboarding_h2": "We ask permission before measuring anything.",
    "onboarding_p": "Vela asks for access to your health data explicitly, not in the fine print, and tells you what it uses each piece for. And if you're new to measuring HRV, it tells you how long until you have a reliable baseline — without pretending it knows who you are on day one.",
    "onboarding_alt": "Two steps of Vela's onboarding on Apple Watch: the welcome screen and the request for access to health data, which explains what each one is used for.",
    "closing_eyebrow": "Download it today", "closing_h2": "No subscription. <em>Ever.</em>",
    "closing_p": "Vela is free on the App Store for Apple Watch, with Vela Pro as a one-time purchase.",
    "footer_support": "Support", "footer_privacy": "Privacy", "footer_contact": "Contact",
  },
}

L["ca"] = {
  "lang_label": "Idioma", "back": "← Torna al suport", "back_home": "← Torna a Vela", "rights": "Tots els drets reservats",
  "support_title": "Vela HRV — Suport",
  "about_h": "Sobre l'app",
  "about_p1": "Vela mesura el teu nivell d'estrès mitjançant la variabilitat de la freqüència cardíaca (HRV) directament des del teu Apple Watch. Tot el processament passa al teu dispositiu — les teves dades no surten del teu Apple Watch ni del teu iCloud privat.",
  "about_p2": "Durant els primers dies, Vela construeix la teva línia base personal perquè cada lectura tingui sentit per al teu cos, no per a una mitjana estadística.",
  "faq_h": "Preguntes freqüents",
  "faq": [
    ("Quin Apple Watch necessito?", "Vela requereix un Apple Watch amb watchOS 26 o superior. Funciona com a app independent — no cal tenir l'iPhone a prop per mesurar."),
    ("Per què triga uns dies a mostrar el meu score?", "Vela necessita conèixer la teva HRV personal abans de calcular un score amb sentit. Durant els primers 7–14 dies construeix la teva línia base — a partir d'aquí, cada lectura reflecteix el teu estat real."),
    ("On es guarden les meves dades?", "Les teves dades se sincronitzen de manera privada a través del teu propi iCloud. Vela no té servidors propis — mai enviem ni emmagatzemem les teves dades fora del teu compte."),
    ("Quins permisos necessita Vela?", "Vela sol·licita accés només de lectura a HealthKit: la variabilitat de la freqüència cardíaca per al teu score d'estrès, i la son, els passos, l'energia activa, els entrenaments i la freqüència cardíaca per a la teva Bateria. Són dades que el teu Apple Watch ja recull automàticament. Si vols, també et demana permís per enviar-te notificacions amb els avisos d'estrès."),
  ],
  "contact_h": "Contacte i suport",
  "contact_p": "Tens cap pregunta, has trobat un error o vols compartir feedback? Escriu-nos directament.",
  "privacy": {
    "title_tag": "Vela HRV — Política de privadesa", "title": "Política de privadesa",
    "updated": "Última actualització: novembre 2026",
    "highlight": "Vela no recull, transmet ni emmagatzema cap dada personal en servidors externs. Tot es queda al teu dispositiu i al teu iCloud privat.",
    "sections": [
      ("Quines dades fa servir Vela", [
        "Vela llegeix dades d'Apple HealthKit, només en mode lectura: la variabilitat de la freqüència cardíaca (HRV) per calcular el teu score d'estrès personal, i la son, els passos, l'energia activa, els entrenaments, la freqüència cardíaca i la freqüència cardíaca en repòs per calcular la teva Bateria — quant la carrega la son i què la gasta durant el dia. Aquestes dades ja les recull automàticament el teu Apple Watch. Vela mai no escriu a HealthKit.",
        "Vela també emmagatzema les lectures que calcula — l'historial del teu score d'estrès, la teva línia base d'HRV personal, les mostres d'HRV en brut utilitzades per calcular-la i els nivells de la teva Bateria."]),
      ("On viuen les teves dades", [
        "Totes les dades s'emmagatzemen localment al teu Apple Watch i se sincronitzen de manera privada a través del teu propi compte d'iCloud mitjançant el framework CloudKit d'Apple. Vela no té servidors. Cap dada passa mai per sistemes propietat de Vela.",
        "Només tu pots accedir a les teves dades. Ni nosaltres, ni tercers."]),
      ("Tercers", [
        "Vela no comparteix cap dada amb tercers. No fem servir serveis d'analítica, SDK publicitaris ni cap eina de seguiment externa."]),
      ("Dades de salut", [
        "Vela accedeix a les dades de salut únicament per oferir la seva funcionalitat principal — mesurar i fer el seguiment del teu nivell d'estrès i de la teva Bateria. Les dades de salut mai no s'utilitzen per a publicitat ni es venen a ningú."]),
      ("Compres", [
        "Vela Pro és una compra única dins de l'app que gestiona Apple a través de l'App Store. Vela mai no rep les teves dades de pagament: l'app només comprova al teu dispositiu, mitjançant StoreKit d'Apple, si Vela Pro està desbloquejat."]),
      ("Menors", [
        "Vela no està dissenyada específicament per a infants. Com que no recull dades de ningú, tampoc no en recull de menors."]),
      ("Canvis en aquesta política", [
        "Si aquesta política de privadesa canvia, la versió actualitzada es publicarà en aquesta URL amb una data nova. L'ús continuat de l'app després dels canvis constitueix l'acceptació de la política actualitzada."]),
    ],
    "contact_h": "Contacte",
    "contact_pre": "Tens preguntes sobre aquesta política de privadesa? Escriu a ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Accessibilitat", "title": "Accessibilitat",
    "updated": "Última actualització: juliol 2026",
    "highlight": "Vela està dissenyada per poder utilitzar-se completament sense veure la pantalla: totes les pantalles funcionen amb VoiceOver i cap informació depèn únicament del color.",
    "approach_h": "El nostre enfocament",
    "approach_p": "Vela mesura l'estrès a través de la variabilitat de la freqüència cardíaca a l'Apple Watch. Entendre el teu propi cos no hauria de dependre de com veus, així que l'accessibilitat es tracta com una funcionalitat central: el principi gu io és que una persona cega pugui consultar el seu nivell d'estrès, explorar el seu historial, llegir les seves anàlisis setmanals i configurar l'app de manera completament autònoma.",
    "supported_h": "Compatibilitat a l'Apple Watch",
    "items": [
      ("VoiceOver.", "Tots els elements tenen etiqueta, valor i descripció amb significat. Els gràfics s'exposen com a Audio Graphs: l'historial d'estrès es pot explorar mitjançant so amb la corona digital."),
      ("Text més gran.", "La interfície fa servir Dynamic Type a tota l'app. Els indicadors compactes, com l'anell de puntuació, ofereixen el visor de contingut ampliat."),
      ("Interfície fosca.", "La interfície de Vela és fosca per disseny a totes les pantalles, sense llampades brillants."),
      ("Diferenciar sense només color.", "Els nivells d'estrès es reforcen sempre amb una xifra i una paraula — mai només amb color. Els gràfics afegeixen línies de zona en activar «Diferenciar sense color»."),
      ("Contrast suficient.", "Tot el text compleix la ràtio de contrast WCAG AA (4,5:1 o superior) sobre el fons fosc."),
      ("Reduir el moviment.", "Les animacions es desactiven o se substitueixen per alternatives estàtiques amb «Reduir el moviment» activat. Vela també respecta Reduir la transparència i Text en negreta."),
    ],
    "no_media": "Vela no conté àudio ni vídeo, per la qual cosa els subtítols i les audiodescripcions no apliquen.",
    "verify_h": "Com ho verifiquem",
    "verify_p": "Totes les pantalles passen per les auditories automàtiques d'accessibilitat d'Apple — etiquetes, contrast, mida de les àrees tàctils i escalat del text — com a part de la bateria de tests de l'app, juntament amb la revisió manual amb VoiceOver. Aquestes comprovacions es repeteixen amb cada canvi d'interfície, de manera que l'accessibilitat no es degrada silenciosament entre versions.",
    "feedback_h": "Comentaris",
    "feedback_pre": "Si alguna cosa a Vela resulta difícil d'utilitzar amb tecnologia d'assistència, és un bug. Escriu-nos a ",
    "feedback_post": " — els informes d'accessibilitat es prioritzen per a la versió següent.",
  },
  "landing": {
    "nav_cta": "Descarrega",
    "title_tag": "Vela — HRV per a l'Apple Watch. Sense subscripció. Mai.",
    "meta_desc": "Vela mesura la teva variabilitat de la freqüència cardíaca (HRV/SDNN) a l'Apple Watch i construeix la teva pròpia línia base personal. Tot es processa al rellotge. Se sincronitza amb el teu iCloud. Sense subscripció, mai.",
    "eyebrow1": "HRV per a l'Apple Watch",
    "h1": "La teva calma no és <em>la mitjana</em> de ningú.",
    "hero_p": "Vela mesura la teva variabilitat de la freqüència cardíaca (SDNN) directament al teu Apple Watch i construeix una línia base pròpia — no un llindar genèric de població. Tot el càlcul passa al rellotge. Res no passa pels nostres servidors, perquè no en tenim.",
    "badge_alt": "Descarrega-la a l'App Store",
    "story_eyebrow": "Sobre el nom", "story_h2": "Per què «Vela»",
    "story_p": "«Vela» també és la vela d'un vaixell — del llatí velum. Un veler no lluita contra el vent: el llegeix i ajusta el rumb. Aquesta és la idea darrere de l'aplicació. En lloc de comparar-te amb un estàndard extern, Vela llegeix la teva pròpia línia base personal i t'ajuda a entendre els teus propis patrons. L'estrès no es combat: es llegeix i s'ajusta.",
    "baseline_eyebrow": "Per què el promig no serveix",
    "baseline_h2": "25&nbsp;ms d'HRV pot ser alt per a tu i baix per a una altra persona.",
    "baseline_p": "L'HRV varia enormement entre persones. Un llindar de població tracta tothom igual — i per això gairebé sempre s'equivoca. Vela construeix la teva pròpia línia base a partir del teu historial real: si ja tens dades d'HRV al teu Apple Watch, pot començar des del primer dia; si ets nou, triga entre 7 i 14 dies a assentar-se.",
    "legend1": "Llindar genèric de població", "legend2": "Mostres individuals", "legend3": "La teva línia base personal",
    "principles_eyebrow": "Com funciona", "principles_h2": "Quatre decisions, preses per no canviar d'opinió.",
    "principles": [
      ("On-device", "Tot el càlcul passa al teu Watch.", "HealthKit lliura les dades, el rellotge fa la resta. Cap dada d'HRV surt del teu dispositiu cap a un servidor de Vela."),
      ("El teu iCloud, no el nostre", "La sincronització fa servir el teu propi compte d'iCloud", "via CloudKit. Vela no allotja les teves dades enlloc — no pot, perquè no té on."),
      ("Sense subscripció. Mai.", "Sense quotes mensuals ni anuals.", "Vela és gratuïta. Vela Pro és una compra única: la pagues una vegada i és teva — mai una subscripció."),
      ("Accessible de sèrie", "VoiceOver, Dynamic Type, Reduce Motion", "i 12 idiomes: castellà, català, èuscar, gallec, English, français, Deutsch, italiano, português, čeština, ελληνικά i 日本語."),
    ],
    "stress_h2": "Un score, un estat, una tendència.",
    "tour_eyebrow": "Recorregut ràpid", "tour_h2": "Tres pantalles, cadascuna amb una única feina.",
    "tour": [
      ("Score actual", "Un número, un estat, calculat íntegrament al rellotge — sense esperar que res se sincronitzi.", "Pantalla principal de Vela mostrant un nivell d'estrès de 34, estat Baix, calculat en el moment."),
      ("Tendència", "Cada lectura del dia, comparada amb la teva pròpia línia discontínua — no amb la de ningú més.", "Gràfic de tendència amb la mitjana d'estrès del dia i les lectures de cada hora, comparades amb la línia base personal."),
      ("Rangs explicats", "Res de xifres críptiques: cada rang diu què significa i què esperar-ne.", "Pantalla d'explicació dels rangs d'estrès: Normal entre 40 i 69, Alt entre 70 i 100."),
    ],
    "onboarding_eyebrow": "Així comences", "onboarding_h2": "Et demanem permís abans de mesurar res.",
    "onboarding_p": "Vela et demana accés a les teves dades de salut de manera explícita, no en la lletra petita, i et diu per a què fa servir cadascuna. I si ets nou mesurant HRV, et diu quant falta per tenir una línia base fiable — sense fingir que el primer dia ja sap qui ets.",
    "onboarding_alt": "Dos passos de la benvinguda de Vela a l'Apple Watch: la pantalla de benvinguda i la petició d'accés a les dades de salut, que explica per a què es fa servir cadascuna.",
    "closing_eyebrow": "Descarrega-la avui", "closing_h2": "Sense subscripció. <em>Mai.</em>",
    "closing_p": "Vela és gratuïta a l'App Store per a l'Apple Watch, amb Vela Pro com a compra única.",
    "footer_support": "Suport", "footer_privacy": "Privadesa", "footer_contact": "Contacte",
  },
}

L["eu"] = {
  "lang_label": "Hizkuntza", "back": "← Itzuli laguntzara", "back_home": "← Itzuli Velara", "rights": "Eskubide guztiak erreserbatuta",
  "support_title": "Vela HRV — Laguntza",
  "about_h": "Aplikazioari buruz",
  "about_p1": "Velak zure estres-maila neurtzen du bihotz-maiztasunaren aldakortasuna (HRV) erabiliz, zuzenean zure Apple Watch-etik. Prozesamendu guztia zure gailuan gertatzen da — zure datuak ez dira inoiz ateratzen zure Apple Watch-etik edo zure iCloud pribatutik.",
  "about_p2": "Lehen egunetan, Velak zure oinarri-lerro pertsonala eraikitzen du, irakurketa bakoitzak zure gorputzarentzat zentzua izan dezan, ez batez besteko estatistiko batentzat.",
  "faq_h": "Ohiko galderak",
  "faq": [
    ("Zein Apple Watch behar dut?", "Velak Apple Watch bat behar du, watchOS 26 edo berriagoarekin. Aplikazio independente gisa dabil — ez duzu iPhonea gertu izan behar neurtzeko."),
    ("Zergatik behar ditu egun batzuk nire puntuazioa erakusteko?", "Velak zure HRV pertsonala ezagutu behar du zentzuzko puntuazio bat kalkulatu aurretik. Lehen 7–14 egunetan zure oinarri-lerroa eraikitzen du — hortik aurrera, irakurketa bakoitzak zure benetako egoera islatzen du."),
    ("Non gordetzen dira nire datuak?", "Zure datuak modu pribatuan sinkronizatzen dira zure iCloud propioaren bidez. Velak ez du zerbitzari propiorik — ez ditugu inoiz zure datuak zure kontutik kanpo bidaltzen edo gordetzen."),
    ("Zein baimen behar ditu Velak?", "Velak HealthKit-erako irakurtzeko sarbidea soilik eskatzen du: bihotz-maiztasunaren aldakortasuna zure estres-puntuaziorako, eta loa, urratsak, energia aktiboa, entrenamenduak eta bihotz-maiztasuna zure Bateriarako. Zure Apple Watch-ak dagoeneko automatikoki biltzen dituen datuak dira. Nahi baduzu, estres-abisuen jakinarazpenak bidaltzeko baimena ere eskatzen dizu."),
  ],
  "contact_h": "Kontaktua eta laguntza",
  "contact_p": "Galderaren bat duzu, errore bat aurkitu duzu edo feedbacka partekatu nahi duzu? Idatzi zuzenean.",
  "privacy": {
    "title_tag": "Vela HRV — Pribatutasun-politika", "title": "Pribatutasun-politika",
    "updated": "Azken eguneratzea: 2026ko azaroa",
    "highlight": "Velak ez du datu pertsonalik biltzen, transmititzen edo kanpoko zerbitzarietan gordetzen. Dena zure gailuan eta zure iCloud pribatuan geratzen da.",
    "sections": [
      ("Zein datu erabiltzen ditu Velak", [
        "Velak Apple HealthKit-eko datuak irakurtzen ditu, irakurtzeko moduan soilik: bihotz-maiztasunaren aldakortasuna (HRV) zure estres-puntuazio pertsonala kalkulatzeko, eta loa, urratsak, energia aktiboa, entrenamenduak, bihotz-maiztasuna eta atseden-egoerako bihotz-maiztasuna zure Bateria kalkulatzeko — loak zenbat kargatzen duen eta egunean zehar zerk husten duen. Datu horiek zure Apple Watch-ak automatikoki biltzen ditu dagoeneko. Velak ez du inoiz HealthKit-en idazten.",
        "Velak kalkulatzen dituen irakurketak ere gordetzen ditu — zure estres-puntuazioaren historiala, zure HRV oinarri-lerro pertsonala, hura kalkulatzeko erabilitako HRV lagin gordinak eta zure Bateriaren mailak."]),
      ("Non bizi dira zure datuak", [
        "Datu guztiak zure Apple Watch-ean gordetzen dira lokalki, eta modu pribatuan sinkronizatzen dira zure iCloud kontuaren bidez, Apple-ren CloudKit framework-a erabiliz. Velak ez du zerbitzaririk. Daturik ez da inoiz pasatzen Velaren jabetzako sistemetatik.",
        "Zuk bakarrik atzi ditzakezu zure datuak. Ez guk, ez hirugarrenek."]),
      ("Hirugarrenak", [
        "Velak ez du daturik partekatzen hirugarrenekin. Ez dugu analitika-zerbitzurik, publizitate-SDKrik edo kanpoko jarraipen-tresnarik erabiltzen."]),
      ("Osasun-datuak", [
        "Velak osasun-datuak bere oinarrizko funtzionaltasuna eskaintzeko bakarrik atzitzen ditu — zure estres-maila eta zure Bateria neurtzea eta jarraitzea. Osasun-datuak ez dira inoiz publizitaterako erabiltzen, ezta inori saltzen ere."]),
      ("Erosketak", [
        "Vela Pro aplikazio barneko erosketa bakarra da, eta Applek kudeatzen du App Store-aren bidez. Velak ez ditu inoiz zure ordainketa-datuak jasotzen: aplikazioak zure gailuan bakarrik egiaztatzen du, Appleren StoreKit-en bidez, Vela Pro desblokeatuta dagoen."]),
      ("Adingabeak", [
        "Vela ez dago berariaz haurrentzat diseinatuta. Inoren daturik biltzen ez duenez, ez du adingabeen daturik biltzen ere."]),
      ("Politika honen aldaketak", [
        "Pribatutasun-politika hau aldatzen bada, bertsio eguneratua URL honetan argitaratuko da data berri batekin. Aldaketen ondoren aplikazioa erabiltzen jarraitzeak politika eguneratua onartzea dakar."]),
    ],
    "contact_h": "Kontaktua",
    "contact_pre": "Galderarik baduzu pribatutasun-politika honi buruz? Idatzi hona: ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Irisgarritasuna", "title": "Irisgarritasuna",
    "updated": "Azken eguneratzea: 2026ko uztaila",
    "highlight": "Vela pantaila ikusi gabe erabat erabiltzeko diseinatuta dago: pantaila guztiek VoiceOver-ekin funtzionatzen dute, eta informaziorik ez dago inoiz kolorearen mende bakarrik.",
    "approach_h": "Gure ikuspegia",
    "approach_p": "Velak estresa neurtzen du bihotz-maiztasunaren aldakortasunaren bidez Apple Watch-ean. Zure gorputza ulertzea ez litzateke egon behar nola ikusten duzunaren mende; horregatik, irisgarritasuna oinarrizko funtzionaltasun gisa tratatzen da: printzipio gidaria da pertsona itsu batek bere estres-maila kontsultatu, bere historiala arakatu, bere asteko analisiak irakurri eta aplikazioa erabat modu autonomoan konfiguratu ahal izatea.",
    "supported_h": "Bateragarritasuna Apple Watch-ean",
    "items": [
      ("VoiceOver.", "Elementu guztiek etiketa, balio eta deskribapen esanguratsuak dituzte. Grafikoak Audio Graph gisa azaltzen dira: estres-historiala soinuaren bidez araka daiteke koroa digitalarekin."),
      ("Testu handiagoa.", "Interfazeak Dynamic Type erabiltzen du aplikazio osoan. Adierazle trinkoek, puntuazio-eraztunak adibidez, eduki handituaren ikustailea eskaintzen dute."),
      ("Interfaze iluna.", "Velaren interfazea iluna da diseinuz pantaila guztietan, distira-argirik gabe."),
      ("Bereizi kolorea ez den zerbaitekin.", "Estres-mailak beti indartzen dira zenbaki batekin eta hitz batekin — inoiz ez kolorearekin bakarrik. Grafikoek zona-lerroak gehitzen dituzte «Bereizi kolorerik gabe» aktibatzean."),
      ("Kontraste nahikoa.", "Testu guztiak WCAG AA kontraste-ratioa betetzen du (4,5:1 edo handiagoa) hondo ilunaren gainean."),
      ("Mugimendua murriztu.", "Animazioak desaktibatu egiten dira edo alternatiba estatikoekin ordezkatzen dira «Mugimendua murriztu» aktibatuta dagoenean. Velak Gardentasuna murriztu eta Testu lodia ere errespetatzen ditu."),
    ],
    "no_media": "Velak ez du audiorik edo bideorik, beraz azpitituluak eta audio-deskribapenak ez dira aplikagarriak.",
    "verify_h": "Nola egiaztatzen dugun",
    "verify_p": "Pantaila guztiek Apple-ren irisgarritasun-auditoria automatikoak pasatzen dituzte — etiketak, kontrastea, ukipen-eremuen tamaina eta testuaren eskalatzea — aplikazioaren test-multzoaren barruan, VoiceOver-ekin eskuzko berrikuspenarekin batera. Egiaztapen horiek interfaze-aldaketa bakoitzarekin errepikatzen dira, irisgarritasuna bertsioen artean isilean degrada ez dadin.",
    "feedback_h": "Iruzkinak",
    "feedback_pre": "Velan zerbait zaila bada laguntza-teknologiarekin erabiltzeko, bug bat da. Idatzi hona: ",
    "feedback_post": " — irisgarritasun-txostenak lehenesten dira hurrengo bertsiorako.",
  },
  "landing": {
    "nav_cta": "Deskargatu",
    "title_tag": "Vela — HRV Apple Watch-erako. Harpidetzarik gabe. Inoiz ez.",
    "meta_desc": "Velak zure bihotz-maiztasunaren aldakortasuna (HRV/SDNN) neurtzen du Apple Watch-en eta zure oinarri-lerro pertsonala eraikitzen du. Dena erlojuan prozesatzen da. Zure iCloudekin sinkronizatzen da. Harpidetzarik gabe, inoiz ez.",
    "eyebrow1": "HRV Apple Watch-erako",
    "h1": "Zure lasaitasuna ez da <em>inoren batez bestekoa</em>.",
    "hero_p": "Velak zure bihotz-maiztasunaren aldakortasuna (SDNN) neurtzen du zuzenean zure Apple Watch-en, eta zure oinarri-lerro propioa eraikitzen du — ez populazioaren atalase generiko bat. Kalkulu guztia erlojuan gertatzen da. Ezer ez da gure zerbitzarietatik pasatzen, ez baititugu.",
    "badge_alt": "Deskargatu App Store-n",
    "story_eyebrow": "Izenari buruz", "story_h2": "Zergatik «Vela»",
    "story_p": "«Vela» gaztelaniazko hitza da itsasontzi baten belarako — latinezko velum hitzetik dator. Belaontzi bat ez da haizearen aurka borrokatzen: irakurri egiten du eta norabidea doitzen du. Hori da aplikazioaren atzean dagoen ideia. Kanpoko estandar batekin alderatu beharrean, Velak zure oinarri-lerro pertsonala irakurtzen du eta zeure patroiak ulertzen laguntzen dizu. Estresa ez da borrokatzen: irakurri eta doitu egiten da.",
    "baseline_eyebrow": "Zergatik ez duen batez bestekoak balio",
    "baseline_h2": "25&nbsp;ms-ko HRV altua izan daiteke zuretzat eta baxua beste norbaitentzat.",
    "baseline_p": "HRV asko aldatzen da pertsonen artean. Populazio-atalase batek denak berdin tratatzen ditu — eta horregatik huts egiten du ia beti. Velak zure oinarri-lerro propioa eraikitzen du zure benetako historialetik abiatuta: dagoeneko HRV daturik baduzu Apple Watch-en, lehen egunetik has daiteke; berria bazara, 7-14 egun behar ditu finkatzeko.",
    "legend1": "Populazioaren atalase generikoa", "legend2": "Banakako laginak", "legend3": "Zure oinarri-lerro pertsonala",
    "principles_eyebrow": "Nola funtzionatzen duen", "principles_h2": "Lau erabaki, iritziz ez aldatzeko hartuak.",
    "principles": [
      ("On-device", "Kalkulu guztia zure Watch-ean gertatzen da.", "HealthKitek datuak ematen ditu, erlojuak gainerakoa egiten du. HRV daturik ez da inoiz zure gailutik ateratzen Velaren zerbitzari batera."),
      ("Zure iCloud, ez gurea", "Sinkronizazioak zure iCloud kontu propioa erabiltzen du", "CloudKit bidez. Velak ez ditu zure datuak inon gordetzen — ezin du, ez baitu non."),
      ("Harpidetzarik gabe. Inoiz ez.", "Hileroko edo urteroko kuotarik gabe.", "Vela doakoa da. Vela Pro erosketa bakarra da: behin ordaintzen duzu eta zurea da — inoiz ez harpidetza bat."),
      ("Berez irisgarria", "VoiceOver, Dynamic Type, Reduce Motion", "eta 12 hizkuntza: gaztelania, katalana, euskara, galiziera, English, français, Deutsch, italiano, português, čeština, ελληνικά eta 日本語."),
    ],
    "stress_h2": "Puntuazio bat, egoera bat, joera bat.",
    "tour_eyebrow": "Bira azkarra", "tour_h2": "Hiru pantaila, bakoitza lan bakar batekin.",
    "tour": [
      ("Uneko puntuazioa", "Zenbaki bat, egoera bat, erlojuan bertan kalkulatua — ezer sinkronizatzeko itxaron gabe.", "Velaren pantaila nagusia, 34ko estres-maila erakusten duena, Baxua egoera, unean bertan kalkulatua."),
      ("Joera", "Eguneko irakurketa bakoitza, zure marra etenarekin alderatuta — ez beste inorenarekin.", "Joera-grafikoa eguneko estres-batez bestekoarekin eta orduroko irakurketekin, oinarri-lerro pertsonalarekin alderatuta."),
      ("Tarteak azalduta", "Zifra kriptikorik ez: tarte bakoitzak esan nahi duena eta zer espero eskaintzen du.", "Estres-tarteak azaltzen dituen pantaila: Normal 40 eta 69 artean, Altu 70 eta 100 artean."),
    ],
    "onboarding_eyebrow": "Horrela hasten zara", "onboarding_h2": "Baimena eskatzen dizugu ezer neurtu aurretik.",
    "onboarding_p": "Velak zure osasun-datuetarako sarbidea modu esplizituan eskatzen du, ez letra txikian, eta bakoitza zertarako erabiltzen duen esaten dizu. Eta HRV neurtzen berria bazara, oinarri-lerro fidagarri bat izateko zenbat falta den esaten dizu — lehen egunetik nor zaren jakingo balu bezala itxuratu gabe.",
    "onboarding_alt": "Velaren ongietorriko bi urrats Apple Watch-ean: ongietorri-pantaila eta osasun-datuetarako sarbide-eskaera, bakoitza zertarako erabiltzen den azaltzen duena.",
    "closing_eyebrow": "Deskargatu gaur", "closing_h2": "Harpidetzarik gabe. <em>Inoiz ez.</em>",
    "closing_p": "Vela doakoa da App Store-n Apple Watch-erako, eta Vela Pro erosketa bakarra da.",
    "footer_support": "Laguntza", "footer_privacy": "Pribatutasuna", "footer_contact": "Kontaktua",
  },
}

L["gl"] = {
  "lang_label": "Idioma", "back": "← Volver ao soporte", "back_home": "← Volver a Vela", "rights": "Todos os dereitos reservados",
  "support_title": "Vela HRV — Soporte",
  "about_h": "Sobre a app",
  "about_p1": "Vela mide o teu nivel de estrés usando a variabilidade da frecuencia cardíaca (HRV) directamente desde o teu Apple Watch. Todo o procesamento ocorre no teu dispositivo — os teus datos non saen do teu Apple Watch nin do teu iCloud privado.",
  "about_p2": "Durante os primeiros días, Vela constrúe a túa liña base persoal para que cada lectura teña sentido para o teu corpo, non para unha media estatística.",
  "faq_h": "Preguntas frecuentes",
  "faq": [
    ("Que Apple Watch necesito?", "Vela require un Apple Watch con watchOS 26 ou superior. Funciona como app independente — non precisa o iPhone preto para medir."),
    ("Por que tarda uns días en amosar a miña puntuación?", "Vela necesita coñecer a túa HRV persoal antes de calcular unha puntuación con sentido. Durante os primeiros 7–14 días constrúe a túa liña base — a partir de aí, cada lectura reflicte o teu estado real."),
    ("Onde se gardan os meus datos?", "Os teus datos sincronízanse de forma privada a través do teu propio iCloud. Vela non ten servidores propios — nunca enviamos nin almacenamos os teus datos fóra da túa conta."),
    ("Que permisos necesita Vela?", "Vela solicita acceso só de lectura a HealthKit: a variabilidade da frecuencia cardíaca para a túa puntuación de estrés, e o sono, os pasos, a enerxía activa, os adestramentos e a frecuencia cardíaca para a túa Batería. Son datos que o teu Apple Watch xa recolle automaticamente. Se queres, tamén che pide permiso para enviarche notificacións cos avisos de estrés."),
  ],
  "contact_h": "Contacto e soporte",
  "contact_p": "Tes algunha pregunta, atopaches un erro ou queres compartir feedback? Escríbenos directamente.",
  "privacy": {
    "title_tag": "Vela HRV — Política de privacidade", "title": "Política de privacidade",
    "updated": "Última actualización: novembro 2026",
    "highlight": "Vela non recolle, transmite nin almacena ningún dato persoal en servidores externos. Todo queda no teu dispositivo e no teu iCloud privado.",
    "sections": [
      ("Que datos usa Vela", [
        "Vela le datos de Apple HealthKit, só en modo lectura: a variabilidade da frecuencia cardíaca (HRV) para calcular a túa puntuación de estrés persoal, e o sono, os pasos, a enerxía activa, os adestramentos, a frecuencia cardíaca e a frecuencia cardíaca en repouso para calcular a túa Batería — canto a carga o sono e que a gasta durante o día. Estes datos xa os recolle automaticamente o teu Apple Watch. Vela nunca escribe en HealthKit.",
        "Vela tamén almacena as lecturas que calcula — o historial da túa puntuación de estrés, a túa liña base de HRV persoal, as mostras de HRV en bruto usadas para calculala e os niveis da túa Batería."]),
      ("Onde viven os teus datos", [
        "Todos os datos almacénanse localmente no teu Apple Watch e sincronízanse de forma privada a través da túa propia conta de iCloud mediante o framework CloudKit de Apple. Vela non ten servidores. Ningún dato pasa nunca por sistemas propiedade de Vela.",
        "Só ti podes acceder aos teus datos. Nin nós, nin terceiros."]),
      ("Terceiros", [
        "Vela non comparte ningún dato con terceiros. Non usamos servizos de analítica, SDK publicitarios nin ningunha ferramenta de seguimento externa."]),
      ("Datos de saúde", [
        "Vela accede aos datos de saúde unicamente para ofrecer a súa funcionalidade principal — medir e seguir o teu nivel de estrés e a túa Batería. Os datos de saúde nunca se usan para publicidade nin se venden a ninguén."]),
      ("Compras", [
        "Vela Pro é unha compra única dentro da app que xestiona Apple a través da App Store. Vela nunca recibe os teus datos de pagamento: a app só comproba no teu dispositivo, mediante StoreKit de Apple, se Vela Pro está desbloqueado."]),
      ("Menores", [
        "Vela non está deseñada especificamente para nenos. Como non recolle datos de ninguén, tampouco recolle datos de menores."]),
      ("Cambios nesta política", [
        "Se esta política de privacidade cambia, a versión actualizada publicarase nesta URL cunha data nova. O uso continuado da app despois dos cambios constitúe a aceptación da política actualizada."]),
    ],
    "contact_h": "Contacto",
    "contact_pre": "Tes preguntas sobre esta política de privacidade? Escribe a ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Accesibilidade", "title": "Accesibilidade",
    "updated": "Última actualización: xullo 2026",
    "highlight": "Vela está deseñada para poder usarse por completo sen ver a pantalla: todas as pantallas funcionan con VoiceOver e ningunha información depende unicamente da cor.",
    "approach_h": "O noso enfoque",
    "approach_p": "Vela mide o estrés a través da variabilidade da frecuencia cardíaca no Apple Watch. Entender o teu propio corpo non debería depender de como ves, así que a accesibilidade trátase como unha funcionalidade central: o principio reitor é que unha persoa cega poida consultar o seu nivel de estrés, explorar o seu historial, ler as súas análises semanais e configurar a app de forma completamente autónoma.",
    "supported_h": "Compatibilidade no Apple Watch",
    "items": [
      ("VoiceOver.", "Todos os elementos teñen etiqueta, valor e descrición con significado. As gráficas expóñense como Audio Graphs: o historial de estrés pode explorarse mediante son coa coroa dixital."),
      ("Texto máis grande.", "A interface usa Dynamic Type en toda a app. Os indicadores compactos, como o anel de puntuación, ofrecen o visor de contido ampliado."),
      ("Interface escura.", "A interface de Vela é escura por deseño en todas as pantallas, sen escintileos brillantes."),
      ("Diferenciar non só coa cor.", "Os niveis de estrés refórzanse sempre cunha cifra e unha palabra — nunca só con cor. As gráficas engaden liñas de zona ao activar «Diferenciar sen cor»."),
      ("Contraste suficiente.", "Todo o texto cumpre a ratio de contraste WCAG AA (4,5:1 ou superior) sobre o fondo escuro."),
      ("Reducir o movemento.", "As animacións desactívanse ou substitúense por alternativas estáticas con «Reducir o movemento» activado. Vela tamén respecta Reducir a transparencia e Texto en grosa."),
    ],
    "no_media": "Vela non contén audio nin vídeo, polo que os subtítulos e as audiodescricións non aplican.",
    "verify_h": "Como o verificamos",
    "verify_p": "Todas as pantallas pasan polas auditorías automáticas de accesibilidade de Apple — etiquetas, contraste, tamaño das áreas táctiles e escalado do texto — como parte da batería de tests da app, xunto coa revisión manual con VoiceOver. Estas comprobacións repítense con cada cambio de interface, de xeito que a accesibilidade non se degrada silenciosamente entre versións.",
    "feedback_h": "Comentarios",
    "feedback_pre": "Se algo en Vela resulta difícil de usar con tecnoloxía de asistencia, é un bug. Escríbenos a ",
    "feedback_post": " — os informes de accesibilidade priorízanse para a seguinte versión.",
  },
  "landing": {
    "nav_cta": "Descargar",
    "title_tag": "Vela — HRV para Apple Watch. Sen subscrición. Nunca.",
    "meta_desc": "Vela mide a túa variabilidade da frecuencia cardíaca (HRV/SDNN) no Apple Watch e constrúe a túa propia liña base persoal. Todo se procesa no reloxo. Sincroniza co teu iCloud. Sen subscrición, nunca.",
    "eyebrow1": "HRV para Apple Watch",
    "h1": "A túa calma non é <em>a media</em> de ninguén.",
    "hero_p": "Vela mide a túa variabilidade da frecuencia cardíaca (SDNN) directamente no teu Apple Watch e constrúe unha liña base propia — non un limiar xenérico de poboación. Todo o cálculo ocorre no reloxo. Nada pasa polos nosos servidores, porque non os temos.",
    "badge_alt": "Descárgao na App Store",
    "story_eyebrow": "Sobre o nome", "story_h2": "Por que «Vela»",
    "story_p": "«Vela» tamén é a vela dun barco — do latín velum. Un veleiro non loita contra o vento: lee o vento e axusta o rumbo. Esa é a idea detrás da aplicación. No canto de compararte cun estándar externo, Vela le a túa propia liña base persoal e axúdache a comprender os teus propios patróns. O estrés non se combate: lese e axústase.",
    "baseline_eyebrow": "Por que a media non serve",
    "baseline_h2": "25&nbsp;ms de HRV pode ser alto para ti e baixo para outra persoa.",
    "baseline_p": "A HRV varía enormemente entre persoas. Un limiar de poboación trata a todos igual — e por iso case sempre falla. Vela constrúe a túa propia liña base a partir do teu historial real: se xa tes datos de HRV no teu Apple Watch, pode empezar dende o primeiro día; se es novo, tarda entre 7 e 14 días en asentarse.",
    "legend1": "Limiar xenérico de poboación", "legend2": "Mostras individuais", "legend3": "A túa liña base persoal",
    "principles_eyebrow": "Como funciona", "principles_h2": "Catro decisións, tomadas para non cambiar de opinión.",
    "principles": [
      ("On-device", "Todo o cálculo ocorre no teu Watch.", "HealthKit entrega os datos, o reloxo fai o resto. Ningún dato de HRV sae do teu dispositivo cara a un servidor de Vela."),
      ("O teu iCloud, non o noso", "A sincronización usa a túa propia conta de iCloud", "vía CloudKit. Vela non aloxa os teus datos en ningures — non pode, porque non ten onde."),
      ("Sen subscrición. Nunca.", "Sen cotas mensuais nin anuais.", "Vela é gratis. Vela Pro é unha compra única: págala unha vez e é túa — nunca unha subscrición."),
      ("Accesible de serie", "VoiceOver, Dynamic Type, Reduce Motion", "e 12 idiomas: castelán, catalán, éuscaro, galego, English, français, Deutsch, italiano, português, čeština, ελληνικά e 日本語."),
    ],
    "stress_h2": "Unha puntuación, un estado, unha tendencia.",
    "tour_eyebrow": "Percorrido rápido", "tour_h2": "Tres pantallas, cada unha cun único traballo.",
    "tour": [
      ("Puntuación actual", "Un número, un estado, calculado enteiramente no reloxo — sen esperar a que nada sincronice.", "Pantalla principal de Vela mostrando un nivel de estrés de 34, estado Baixo, calculado no momento."),
      ("Tendencia", "Cada lectura do día, comparada coa túa propia liña discontinua — non coa de ninguén máis.", "Gráfico de tendencia coa media de estrés do día e as lecturas de cada hora, comparadas coa liña base persoal."),
      ("Rangos explicados", "Nada de cifras crípticas: cada rango di que significa e que esperar del.", "Pantalla de explicación dos rangos de estrés: Normal entre 40 e 69, Alto entre 70 e 100."),
    ],
    "onboarding_eyebrow": "Así comezas", "onboarding_h2": "Pedímosche permiso antes de medir nada.",
    "onboarding_p": "Vela pídeche acceso aos teus datos de saúde de forma explícita, non na letra pequena, e dille para que usa cada un. E se es novo medindo HRV, dicheche canto falta para ter unha liña base fiable — sen finxir que o primeiro día xa sabe quen es.",
    "onboarding_alt": "Dous pasos da benvida de Vela no Apple Watch: a pantalla de benvida e a petición de acceso aos datos de saúde, que explica para que se usa cada un.",
    "closing_eyebrow": "Descárgaa hoxe", "closing_h2": "Sen subscrición. <em>Nunca.</em>",
    "closing_p": "Vela é gratis na App Store para Apple Watch, con Vela Pro como compra única.",
    "footer_support": "Soporte", "footer_privacy": "Privacidade", "footer_contact": "Contacto",
  },
}

L["fr"] = {
  "lang_label": "Langue", "back": "← Retour à l'assistance", "back_home": "← Retour à Vela", "rights": "Tous droits réservés",
  "support_title": "Vela HRV — Assistance",
  "about_h": "À propos de l'app",
  "about_p1": "Vela mesure votre niveau de stress à partir de la variabilité de la fréquence cardiaque (VFC), directement depuis votre Apple Watch. Tout le traitement se fait sur votre appareil — vos données ne quittent jamais votre Apple Watch ni votre iCloud privé.",
  "about_p2": "Pendant les premiers jours, Vela construit votre référence personnelle pour que chaque mesure ait du sens pour votre corps, et non pour une moyenne statistique.",
  "faq_h": "Questions fréquentes",
  "faq": [
    ("De quelle Apple Watch ai-je besoin ?", "Vela nécessite une Apple Watch sous watchOS 26 ou ultérieur. Elle fonctionne de manière autonome — votre iPhone n'a pas besoin d'être à proximité pour prendre une mesure."),
    ("Pourquoi faut-il quelques jours avant de voir mon score ?", "Vela doit apprendre votre VFC personnelle avant de pouvoir calculer un score pertinent. Pendant les 7 à 14 premiers jours, elle construit votre référence — ensuite, chaque mesure reflète votre état réel."),
    ("Où sont stockées mes données ?", "Vos données se synchronisent de manière privée via votre propre iCloud. Vela n'a aucun serveur — nous n'envoyons ni ne stockons jamais vos données en dehors de votre compte."),
    ("Quelles autorisations Vela demande-t-elle ?", "Vela demande un accès en lecture seule à HealthKit : la variabilité de la fréquence cardiaque pour votre score de stress, et le sommeil, les pas, l'énergie active, les séances d'entraînement et la fréquence cardiaque pour votre Batterie. Ce sont des données que votre Apple Watch collecte déjà automatiquement. Si vous le souhaitez, elle demande aussi l'autorisation de vous envoyer des notifications pour les alertes de stress."),
  ],
  "contact_h": "Contact et assistance",
  "contact_p": "Une question, un bug ou un retour à partager ? Écrivez-nous directement.",
  "privacy": {
    "title_tag": "Vela HRV — Politique de confidentialité", "title": "Politique de confidentialité",
    "updated": "Dernière mise à jour : novembre 2026",
    "highlight": "Vela ne collecte, ne transmet et ne stocke aucune donnée personnelle sur des serveurs externes. Tout reste sur votre appareil et dans votre iCloud privé.",
    "sections": [
      ("Quelles données Vela utilise", [
        "Vela lit des données d'Apple HealthKit, en lecture seule : la variabilité de la fréquence cardiaque (VFC) pour calculer votre score de stress personnel, ainsi que le sommeil, les pas, l'énergie active, les séances d'entraînement, la fréquence cardiaque et la fréquence cardiaque au repos pour calculer votre Batterie — ce que le sommeil recharge et ce qui la vide au fil de la journée. Ces données sont déjà collectées automatiquement par votre Apple Watch. Vela n'écrit jamais dans HealthKit.",
        "Vela stocke également les mesures qu'elle calcule — l'historique de votre score de stress, votre référence VFC personnelle, les échantillons VFC bruts utilisés pour la calculer et les niveaux de votre Batterie."]),
      ("Où vivent vos données", [
        "Toutes les données sont stockées localement sur votre Apple Watch et synchronisées de manière privée via votre propre compte iCloud, grâce au framework CloudKit d'Apple. Vela n'a pas de serveurs. Aucune donnée ne transite jamais par des systèmes appartenant à Vela.",
        "Vous seul pouvez accéder à vos données. Ni nous, ni des tiers."]),
      ("Tiers", [
        "Vela ne partage aucune donnée avec des tiers. Nous n'utilisons aucun service d'analyse, aucun SDK publicitaire ni aucun outil de suivi externe."]),
      ("Données de santé", [
        "Vela accède aux données de santé uniquement pour offrir sa fonctionnalité principale — mesurer et suivre votre niveau de stress et votre Batterie. Les données de santé ne sont jamais utilisées à des fins publicitaires ni vendues à qui que ce soit."]),
      ("Achats", [
        "Vela Pro est un achat intégré unique, traité par Apple via l'App Store. Vela ne reçoit jamais vos données de paiement : l'app vérifie seulement sur votre appareil, via StoreKit d'Apple, si Vela Pro est débloqué."]),
      ("Enfants", [
        "Vela n'est pas conçue spécifiquement pour les enfants. Comme elle ne collecte les données de personne, elle ne collecte pas non plus celles des mineurs."]),
      ("Modifications de cette politique", [
        "Si cette politique de confidentialité change, la version mise à jour sera publiée à cette URL avec une nouvelle date. Continuer à utiliser l'app après les modifications vaut acceptation de la politique mise à jour."]),
    ],
    "contact_h": "Contact",
    "contact_pre": "Des questions sur cette politique de confidentialité ? Écrivez à ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Accessibilité", "title": "Accessibilité",
    "updated": "Dernière mise à jour : juillet 2026",
    "highlight": "Vela est conçue pour être entièrement utilisable sans voir l'écran : chaque écran fonctionne avec VoiceOver, et aucune information ne repose uniquement sur la couleur.",
    "approach_h": "Notre approche",
    "approach_p": "Vela mesure le stress à travers la variabilité de la fréquence cardiaque sur Apple Watch. Comprendre son propre corps ne devrait pas dépendre de la façon dont on voit ; l'accessibilité est donc traitée comme une fonctionnalité centrale : le principe directeur est qu'une personne aveugle puisse consulter son niveau de stress, explorer son historique, lire ses analyses hebdomadaires et configurer l'app en toute autonomie.",
    "supported_h": "Prise en charge sur Apple Watch",
    "items": [
      ("VoiceOver.", "Chaque élément a une étiquette, une valeur et une description pertinentes. Les graphiques sont exposés en Audio Graphs : l'historique de stress peut être exploré par le son avec la couronne digitale."),
      ("Texte plus grand.", "L'interface utilise Dynamic Type partout. Les affichages compacts, comme l'anneau de score, offrent le visualiseur de contenu agrandi."),
      ("Interface sombre.", "L'interface de Vela est sombre par conception sur tous les écrans, sans flashs lumineux."),
      ("Différencier sans la couleur.", "Les niveaux de stress sont toujours renforcés par un chiffre et un mot — jamais par la couleur seule. Les graphiques ajoutent des lignes de zone lorsque « Différencier sans couleur » est activé."),
      ("Contraste suffisant.", "Tout le texte respecte le ratio de contraste WCAG AA (4,5:1 ou mieux) sur le fond sombre."),
      ("Réduire les animations.", "Les animations sont désactivées ou remplacées par des alternatives statiques quand « Réduire les animations » est activé. Vela respecte aussi Réduire la transparence et Texte en gras."),
    ],
    "no_media": "Vela ne contient ni audio ni vidéo ; les sous-titres et l'audiodescription ne s'appliquent donc pas.",
    "verify_h": "Comment nous le vérifions",
    "verify_p": "Chaque écran passe par les audits d'accessibilité automatisés d'Apple — étiquettes, contraste, taille des zones tactiles et mise à l'échelle du texte — dans le cadre de la suite de tests de l'app, en complément d'une revue manuelle avec VoiceOver. Ces vérifications sont relancées à chaque changement d'interface, pour que l'accessibilité ne régresse pas silencieusement entre les versions.",
    "feedback_h": "Vos retours",
    "feedback_pre": "Si quelque chose dans Vela est difficile à utiliser avec une technologie d'assistance, c'est un bug. Écrivez à ",
    "feedback_post": " — les signalements d'accessibilité sont prioritaires pour la version suivante.",
  },
  "landing": {
    "nav_cta": "Télécharger",
    "title_tag": "Vela — VFC pour Apple Watch. Sans abonnement. Jamais.",
    "meta_desc": "Vela mesure votre variabilité de la fréquence cardiaque (VFC/SDNN) sur Apple Watch et construit votre propre référence personnelle. Tout est traité sur la montre. Se synchronise avec votre iCloud. Sans abonnement, jamais.",
    "eyebrow1": "VFC pour Apple Watch",
    "h1": "Votre calme n'est <em>la moyenne</em> de personne.",
    "hero_p": "Vela mesure votre variabilité de la fréquence cardiaque (SDNN) directement sur votre Apple Watch et construit une référence qui vous est propre — pas un seuil générique de population. Tout le calcul se fait sur la montre. Rien ne transite par nos serveurs, car nous n'en avons pas.",
    "badge_alt": "Télécharger dans l'App Store",
    "story_eyebrow": "À propos du nom", "story_h2": "Pourquoi « Vela »",
    "story_p": "« Vela » est le mot espagnol pour désigner la voile d'un bateau — du latin velum. Un voilier ne lutte pas contre le vent : il le lit et ajuste son cap. C'est l'idée qui sous-tend l'application. Plutôt que de vous comparer à une norme extérieure, Vela lit votre propre référence personnelle et vous aide à comprendre vos propres schémas. Le stress ne se combat pas : il se lit et s'ajuste.",
    "baseline_eyebrow": "Pourquoi la moyenne ne fonctionne pas",
    "baseline_h2": "25&nbsp;ms de VFC peut être élevé pour vous et bas pour quelqu'un d'autre.",
    "baseline_p": "La VFC varie énormément d'une personne à l'autre. Un seuil de population traite tout le monde de la même façon — et c'est précisément pour ça qu'il se trompe presque toujours. Vela construit votre propre référence à partir de votre historique réel : si vous avez déjà des données VFC sur votre Apple Watch, elle peut démarrer dès le premier jour ; si vous êtes nouveau, il faut 7 à 14 jours pour qu'elle se stabilise.",
    "legend1": "Seuil générique de population", "legend2": "Échantillons individuels", "legend3": "Votre référence personnelle",
    "principles_eyebrow": "Comment ça marche", "principles_h2": "Quatre décisions, prises pour ne pas changer d'avis.",
    "principles": [
      ("On-device", "Tout le calcul se fait sur votre Watch.", "HealthKit fournit les données, la montre fait le reste. Aucune donnée VFC ne quitte jamais votre appareil vers un serveur Vela."),
      ("Votre iCloud, pas le nôtre", "La synchronisation utilise votre propre compte iCloud", "via CloudKit. Vela n'héberge vos données nulle part — elle ne peut pas, faute d'endroit où les mettre."),
      ("Sans abonnement. Jamais.", "Aucun frais mensuel ni annuel.", "Vela est gratuite. Vela Pro est un achat unique : vous le payez une fois et il est à vous — jamais un abonnement."),
      ("Accessible par défaut", "VoiceOver, Dynamic Type, Reduce Motion", "et 12 langues : espagnol, catalan, basque, galicien, anglais, français, allemand, italien, portugais, tchèque, grec et japonais."),
    ],
    "stress_h2": "Un score, un état, une tendance.",
    "tour_eyebrow": "Visite rapide", "tour_h2": "Trois écrans, chacun avec un seul rôle.",
    "tour": [
      ("Score actuel", "Un chiffre, un état, calculé entièrement sur la montre — sans attendre la moindre synchronisation.", "Écran principal de Vela affichant un niveau de stress de 34, état Faible, calculé sur le moment."),
      ("Tendance", "Chaque mesure de la journée, comparée à votre propre ligne pointillée — pas à celle de quelqu'un d'autre.", "Graphique de tendance avec la moyenne de stress du jour et les mesures horaires, comparées à la référence personnelle."),
      ("Plages expliquées", "Fini les chiffres cryptiques : chaque plage indique ce qu'elle signifie et ce à quoi s'attendre.", "Écran expliquant les plages de stress : Normale entre 40 et 69, Élevée entre 70 et 100."),
    ],
    "onboarding_eyebrow": "Comment ça démarre", "onboarding_h2": "Nous demandons la permission avant de mesurer quoi que ce soit.",
    "onboarding_p": "Vela demande l'accès à vos données de santé de façon explicite, pas dans les petits caractères, et vous dit à quoi sert chacune. Et si vous débutez avec la mesure de la VFC, elle vous indique combien de temps il reste avant d'avoir une référence fiable — sans prétendre savoir qui vous êtes dès le premier jour.",
    "onboarding_alt": "Deux étapes de l'accueil de Vela sur Apple Watch : l'écran de bienvenue et la demande d'accès aux données de santé, qui explique à quoi sert chacune.",
    "closing_eyebrow": "Téléchargez-la aujourd'hui", "closing_h2": "Sans abonnement. <em>Jamais.</em>",
    "closing_p": "Vela est gratuite sur l'App Store pour Apple Watch, avec Vela Pro en achat unique.",
    "footer_support": "Assistance", "footer_privacy": "Confidentialité", "footer_contact": "Contact",
  },
}

L["de"] = {
  "lang_label": "Sprache", "back": "← Zurück zum Support", "back_home": "← Zurück zu Vela", "rights": "Alle Rechte vorbehalten",
  "support_title": "Vela HRV — Support",
  "about_h": "Über die App",
  "about_p1": "Vela misst dein Stressniveau anhand der Herzfrequenzvariabilität (HRV) direkt über deine Apple Watch. Die gesamte Verarbeitung findet auf deinem Gerät statt — deine Daten verlassen weder deine Apple Watch noch deine private iCloud.",
  "about_p2": "In den ersten Tagen erstellt Vela deine persönliche Baseline, damit jede Messung für deinen Körper Sinn ergibt — nicht für einen statistischen Durchschnitt.",
  "faq_h": "Häufige Fragen",
  "faq": [
    ("Welche Apple Watch brauche ich?", "Vela erfordert eine Apple Watch mit watchOS 26 oder neuer. Die App läuft eigenständig — dein iPhone muss für eine Messung nicht in der Nähe sein."),
    ("Warum dauert es ein paar Tage, bis mein Score erscheint?", "Vela muss zuerst deine persönliche HRV kennenlernen, um einen aussagekräftigen Score zu berechnen. In den ersten 7–14 Tagen entsteht deine Baseline — danach spiegelt jede Messung deinen tatsächlichen Zustand wider."),
    ("Wo werden meine Daten gespeichert?", "Deine Daten werden privat über deine eigene iCloud synchronisiert. Vela hat keine eigenen Server — wir senden oder speichern deine Daten niemals außerhalb deines Accounts."),
    ("Welche Berechtigungen braucht Vela?", "Vela bittet um reinen Lesezugriff auf HealthKit: die Herzfrequenzvariabilität für deinen Stress-Score sowie Schlaf, Schritte, aktive Energie, Trainings und Herzfrequenz für deine Batterie. Das sind Daten, die deine Apple Watch bereits automatisch erfasst. Wenn du möchtest, bittet Vela außerdem um die Erlaubnis, dir Mitteilungen für Stresshinweise zu senden."),
  ],
  "contact_h": "Kontakt & Support",
  "contact_p": "Du hast eine Frage, einen Fehler gefunden oder Feedback? Schreib uns direkt.",
  "privacy": {
    "title_tag": "Vela HRV — Datenschutzerklärung", "title": "Datenschutzerklärung",
    "updated": "Zuletzt aktualisiert: November 2026",
    "highlight": "Vela erhebt, überträgt und speichert keinerlei personenbezogene Daten auf externen Servern. Alles bleibt auf deinem Gerät und in deiner privaten iCloud.",
    "sections": [
      ("Welche Daten Vela nutzt", [
        "Vela liest Daten aus Apple HealthKit, ausschließlich lesend: die Herzfrequenzvariabilität (HRV), um deinen persönlichen Stress-Score zu berechnen, sowie Schlaf, Schritte, aktive Energie, Trainings, Herzfrequenz und Ruheherzfrequenz, um deine Batterie zu berechnen — wie viel der Schlaf auflädt und was sie im Laufe des Tages verbraucht. Diese Daten erfasst deine Apple Watch bereits automatisch. Vela schreibt nie in HealthKit.",
        "Vela speichert außerdem die berechneten Messungen — den Verlauf deines Stress-Scores, deine persönliche HRV-Baseline, die HRV-Rohdaten, aus denen sie berechnet wird, und die Stände deiner Batterie."]),
      ("Wo deine Daten liegen", [
        "Alle Daten werden lokal auf deiner Apple Watch gespeichert und privat über deinen eigenen iCloud-Account mit Apples CloudKit-Framework synchronisiert. Vela hat keine Server. Keine Daten laufen jemals über Systeme, die Vela gehören oder von Vela betrieben werden.",
        "Nur du kannst auf deine Daten zugreifen. Weder wir noch Dritte."]),
      ("Dritte", [
        "Vela teilt keine Daten mit Dritten. Wir verwenden keine Analysedienste, keine Werbe-SDKs und keine externen Tracking-Tools."]),
      ("Gesundheitsdaten", [
        "Vela greift auf Gesundheitsdaten ausschließlich zu, um seine Kernfunktion zu erfüllen — dein Stressniveau und deine Batterie zu messen und zu verfolgen. Gesundheitsdaten werden niemals für Werbung genutzt oder an Dritte verkauft."]),
      ("Käufe", [
        "Vela Pro ist ein einmaliger In-App-Kauf, den Apple über den App Store abwickelt. Vela erhält nie deine Zahlungsdaten: Die App prüft nur auf deinem Gerät über Apples StoreKit, ob Vela Pro freigeschaltet ist."]),
      ("Kinder", [
        "Vela ist nicht speziell für Kinder gedacht. Da Vela von niemandem Daten erhebt, erhebt es auch keine Daten von Minderjährigen."]),
      ("Änderungen an dieser Erklärung", [
        "Falls sich diese Datenschutzerklärung ändert, wird die aktualisierte Version unter dieser URL mit neuem Datum veröffentlicht. Die weitere Nutzung der App nach Änderungen gilt als Zustimmung zur aktualisierten Erklärung."]),
    ],
    "contact_h": "Kontakt",
    "contact_pre": "Fragen zu dieser Datenschutzerklärung? Schreib an ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Barrierefreiheit", "title": "Barrierefreiheit",
    "updated": "Zuletzt aktualisiert: Juli 2026",
    "highlight": "Vela ist so gestaltet, dass es vollständig ohne Blick auf das Display nutzbar ist: Jeder Bildschirm funktioniert mit VoiceOver, und keine Information wird jemals nur über Farbe vermittelt.",
    "approach_h": "Unser Ansatz",
    "approach_p": "Vela misst Stress über die Herzfrequenzvariabilität auf der Apple Watch. Den eigenen Körper zu verstehen sollte nicht davon abhängen, wie man sieht — deshalb wird Barrierefreiheit als Kernfunktion behandelt: Das Leitprinzip ist, dass eine blinde Person ihr Stressniveau prüfen, ihren Verlauf erkunden, ihre wöchentlichen Analysen lesen und die App vollständig eigenständig konfigurieren kann.",
    "supported_h": "Unterstützung auf der Apple Watch",
    "items": [
      ("VoiceOver.", "Jedes Element hat eine aussagekräftige Beschriftung, einen Wert und einen Hinweis. Diagramme sind als Audiodiagramme verfügbar: Der Stressverlauf lässt sich per Klang mit der Digital Crown erkunden."),
      ("Größerer Text.", "Die Oberfläche nutzt durchgehend Dynamic Type. Kompakte Anzeigen wie der Score-Ring bieten die vergrößerte Inhaltsanzeige."),
      ("Dunkle Oberfläche.", "Velas Oberfläche ist auf jedem Bildschirm bewusst dunkel gestaltet, ohne helle Blitze."),
      ("Ohne Farbe differenzieren.", "Stressniveaus werden immer durch eine Zahl und ein Wort verstärkt — niemals nur durch Farbe. Diagramme blenden Zonenlinien ein, wenn „Ohne Farben differenzieren“ aktiviert ist."),
      ("Ausreichender Kontrast.", "Sämtlicher Text erfüllt das WCAG-AA-Kontrastverhältnis (4,5:1 oder besser) auf dem dunklen Hintergrund."),
      ("Bewegung reduzieren.", "Animationen werden deaktiviert oder durch statische Alternativen ersetzt, wenn „Bewegung reduzieren“ aktiv ist. Vela respektiert auch „Transparenz reduzieren“ und „Fetter Text“."),
    ],
    "no_media": "Vela enthält weder Audio- noch Videoinhalte; Untertitel und Audiodeskriptionen sind daher nicht anwendbar.",
    "verify_h": "Wie wir das überprüfen",
    "verify_p": "Jeder Bildschirm durchläuft Apples automatisierte Barrierefreiheits-Audits — Beschriftungen, Kontrast, Größe der Berührungsflächen und Textskalierung — als Teil der Test-Suite der App, ergänzt durch manuelle VoiceOver-Prüfungen. Diese Checks laufen bei jeder Änderung der Oberfläche erneut, damit sich die Barrierefreiheit zwischen Versionen nicht unbemerkt verschlechtert.",
    "feedback_h": "Feedback",
    "feedback_pre": "Wenn etwas in Vela mit assistiven Technologien schwer zu bedienen ist, ist das ein Bug. Schreib an ",
    "feedback_post": " — Barrierefreiheits-Meldungen werden für das nächste Release priorisiert.",
  },
  "landing": {
    "nav_cta": "Herunterladen",
    "title_tag": "Vela — HRV für Apple Watch. Kein Abo. Niemals.",
    "meta_desc": "Vela misst deine Herzfrequenzvariabilität (HRV/SDNN) auf der Apple Watch und erstellt deine eigene persönliche Baseline. Alles wird auf der Uhr verarbeitet. Synchronisiert mit deiner iCloud. Kein Abo, niemals.",
    "eyebrow1": "HRV für Apple Watch",
    "h1": "Deine Ruhe ist <em>niemandes Durchschnitt</em>.",
    "hero_p": "Vela misst deine Herzfrequenzvariabilität (SDNN) direkt auf deiner Apple Watch und erstellt eine Baseline, die wirklich dir gehört — kein generischer Bevölkerungsschwellenwert. Die gesamte Berechnung läuft auf der Uhr. Nichts läuft über unsere Server, weil wir keine haben.",
    "badge_alt": "Laden im App Store",
    "story_eyebrow": "Über den Namen", "story_h2": "Warum „Vela“",
    "story_p": "„Vela“ ist das spanische Wort für das Segel eines Bootes — vom lateinischen velum. Ein Segelboot kämpft nicht gegen den Wind: Es liest ihn und passt den Kurs an. Das ist die Idee hinter der App. Statt dich mit einem externen Standard zu vergleichen, liest Vela deine eigene persönliche Baseline und hilft dir, deine eigenen Muster zu verstehen. Stress wird nicht bekämpft, sondern gelesen und angepasst.",
    "baseline_eyebrow": "Warum der Durchschnitt nicht funktioniert",
    "baseline_h2": "25&nbsp;ms HRV können für dich hoch und für jemand anderen niedrig sein.",
    "baseline_p": "HRV variiert enorm zwischen Menschen. Ein Bevölkerungsschwellenwert behandelt alle gleich — und liegt genau deshalb fast immer falsch. Vela erstellt deine eigene Baseline aus deiner echten Historie: Hast du bereits HRV-Daten auf deiner Apple Watch, kann sie ab Tag eins starten; bist du neu, dauert es 7–14 Tage, bis sie sich stabilisiert.",
    "legend1": "Generischer Bevölkerungsschwellenwert", "legend2": "Einzelne Messwerte", "legend3": "Deine persönliche Baseline",
    "principles_eyebrow": "So funktioniert's", "principles_h2": "Vier Entscheidungen, getroffen, um sie nicht mehr zu ändern.",
    "principles": [
      ("On-device", "Die gesamte Berechnung läuft auf deiner Watch.", "HealthKit liefert die Daten, die Uhr erledigt den Rest. Keine HRV-Daten verlassen jemals dein Gerät in Richtung eines Vela-Servers."),
      ("Deine iCloud, nicht unsere", "Die Synchronisierung nutzt dein eigenes iCloud-Konto", "über CloudKit. Vela speichert deine Daten nirgendwo — das kann es gar nicht, weil es keinen Ort dafür hat."),
      ("Kein Abo. Niemals.", "Keine monatlichen oder jährlichen Gebühren.", "Vela ist kostenlos. Vela Pro ist ein Einmalkauf: Du zahlst einmal, und es gehört dir — niemals ein Abo."),
      ("Barrierefrei von Haus aus", "VoiceOver, Dynamic Type, Reduce Motion", "und 12 Sprachen: Spanisch, Katalanisch, Baskisch, Galicisch, Englisch, Französisch, Deutsch, Italienisch, Portugiesisch, Tschechisch, Griechisch und Japanisch."),
    ],
    "stress_h2": "Ein Score, ein Zustand, ein Trend.",
    "tour_eyebrow": "Kurzer Rundgang", "tour_h2": "Drei Bildschirme, jeder mit genau einer Aufgabe.",
    "tour": [
      ("Aktueller Score", "Eine Zahl, ein Zustand, vollständig auf der Uhr berechnet — ohne auf eine Synchronisierung zu warten.", "Hauptbildschirm von Vela mit einem Stresslevel von 34, Status Niedrig, im Moment berechnet."),
      ("Trend", "Jede Messung des Tages, verglichen mit deiner eigenen gestrichelten Linie — mit niemand anderem.", "Trenddiagramm mit dem Tagesdurchschnitt des Stresses und stündlichen Messwerten, verglichen mit der persönlichen Baseline."),
      ("Bereiche erklärt", "Keine kryptischen Zahlen: Jeder Bereich sagt, was er bedeutet und was zu erwarten ist.", "Bildschirm, der die Stressbereiche erklärt: Normal zwischen 40 und 69, Hoch zwischen 70 und 100."),
    ],
    "onboarding_eyebrow": "So startest du", "onboarding_h2": "Wir fragen um Erlaubnis, bevor wir irgendetwas messen.",
    "onboarding_p": "Vela bittet ausdrücklich um Zugriff auf deine Gesundheitsdaten — nicht im Kleingedruckten — und sagt dir, wofür es welche Daten nutzt. Und wenn du neu im Messen von HRV bist, sagt dir Vela, wie lange es noch dauert, bis du eine verlässliche Baseline hast — ohne so zu tun, als würde es dich schon am ersten Tag kennen.",
    "onboarding_alt": "Zwei Schritte der Begrüßung von Vela auf der Apple Watch: der Willkommensbildschirm und die Anfrage nach Zugriff auf Gesundheitsdaten, die erklärt, wofür welche Daten genutzt werden.",
    "closing_eyebrow": "Heute herunterladen", "closing_h2": "Kein Abo. <em>Niemals.</em>",
    "closing_p": "Vela ist kostenlos im App Store für Apple Watch erhältlich, mit Vela Pro als Einmalkauf.",
    "footer_support": "Support", "footer_privacy": "Datenschutz", "footer_contact": "Kontakt",
  },
}

L["it"] = {
  "lang_label": "Lingua", "back": "← Torna al supporto", "back_home": "← Torna a Vela", "rights": "Tutti i diritti riservati",
  "support_title": "Vela HRV — Supporto",
  "about_h": "Informazioni sull'app",
  "about_p1": "Vela misura il tuo livello di stress usando la variabilità della frequenza cardiaca (HRV) direttamente dal tuo Apple Watch. Tutta l'elaborazione avviene sul tuo dispositivo — i tuoi dati non lasciano mai il tuo Apple Watch né il tuo iCloud privato.",
  "about_p2": "Durante i primi giorni, Vela costruisce la tua baseline personale perché ogni misurazione abbia senso per il tuo corpo, non per una media statistica.",
  "faq_h": "Domande frequenti",
  "faq": [
    ("Quale Apple Watch mi serve?", "Vela richiede un Apple Watch con watchOS 26 o successivo. Funziona come app indipendente — l'iPhone non deve essere nelle vicinanze per effettuare una misurazione."),
    ("Perché servono alcuni giorni prima di vedere il mio punteggio?", "Vela deve conoscere la tua HRV personale prima di calcolare un punteggio significativo. Nei primi 7–14 giorni costruisce la tua baseline — da lì in poi, ogni misurazione riflette il tuo stato reale."),
    ("Dove sono conservati i miei dati?", "I tuoi dati si sincronizzano in modo privato tramite il tuo iCloud. Vela non ha server propri — non inviamo né conserviamo mai i tuoi dati al di fuori del tuo account."),
    ("Quali permessi richiede Vela?", "Vela richiede l'accesso in sola lettura a HealthKit: la variabilità della frequenza cardiaca per il tuo punteggio di stress, e il sonno, i passi, l'energia attiva, gli allenamenti e la frequenza cardiaca per la tua Batteria. Sono dati che il tuo Apple Watch raccoglie già automaticamente. Se vuoi, chiede anche il permesso di inviarti notifiche per gli avvisi di stress."),
  ],
  "contact_h": "Contatti e supporto",
  "contact_p": "Hai una domanda, hai trovato un bug o vuoi condividere un feedback? Scrivici direttamente.",
  "privacy": {
    "title_tag": "Vela HRV — Informativa sulla privacy", "title": "Informativa sulla privacy",
    "updated": "Ultimo aggiornamento: novembre 2026",
    "highlight": "Vela non raccoglie, trasmette né conserva alcun dato personale su server esterni. Tutto resta sul tuo dispositivo e nel tuo iCloud privato.",
    "sections": [
      ("Quali dati usa Vela", [
        "Vela legge dati da Apple HealthKit, in sola lettura: la variabilità della frequenza cardiaca (HRV) per calcolare il tuo punteggio di stress personale, e il sonno, i passi, l'energia attiva, gli allenamenti, la frequenza cardiaca e la frequenza cardiaca a riposo per calcolare la tua Batteria — quanto la ricarica il sonno e cosa la consuma durante il giorno. Questi dati vengono già raccolti automaticamente dal tuo Apple Watch. Vela non scrive mai in HealthKit.",
        "Vela conserva anche le misurazioni che calcola — lo storico del tuo punteggio di stress, la tua baseline HRV personale, i campioni HRV grezzi usati per calcolarla e i livelli della tua Batteria."]),
      ("Dove vivono i tuoi dati", [
        "Tutti i dati sono conservati localmente sul tuo Apple Watch e sincronizzati in modo privato tramite il tuo account iCloud con il framework CloudKit di Apple. Vela non ha server. Nessun dato passa mai per sistemi di proprietà di Vela.",
        "Solo tu puoi accedere ai tuoi dati. Né noi, né terze parti."]),
      ("Terze parti", [
        "Vela non condivide alcun dato con terze parti. Non usiamo servizi di analisi, SDK pubblicitari né strumenti di tracciamento esterni."]),
      ("Dati sanitari", [
        "Vela accede ai dati sanitari esclusivamente per offrire la sua funzionalità principale — misurare e monitorare il tuo livello di stress e la tua Batteria. I dati sanitari non vengono mai usati per pubblicità né venduti a nessuno."]),
      ("Acquisti", [
        "Vela Pro è un acquisto in-app unico, gestito da Apple tramite l'App Store. Vela non riceve mai i tuoi dati di pagamento: l'app verifica solo sul tuo dispositivo, tramite StoreKit di Apple, se Vela Pro è sbloccato."]),
      ("Minori", [
        "Vela non è pensata specificamente per i bambini. Poiché non raccoglie dati di nessuno, non raccoglie nemmeno quelli dei minori."]),
      ("Modifiche a questa informativa", [
        "Se questa informativa sulla privacy cambia, la versione aggiornata sarà pubblicata a questo URL con una nuova data. L'uso continuato dell'app dopo le modifiche costituisce accettazione dell'informativa aggiornata."]),
    ],
    "contact_h": "Contatti",
    "contact_pre": "Domande su questa informativa? Scrivi a ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Accessibilità", "title": "Accessibilità",
    "updated": "Ultimo aggiornamento: luglio 2026",
    "highlight": "Vela è progettata per essere completamente utilizzabile senza guardare lo schermo: ogni schermata funziona con VoiceOver e nessuna informazione dipende mai soltanto dal colore.",
    "approach_h": "Il nostro approccio",
    "approach_p": "Vela misura lo stress attraverso la variabilità della frequenza cardiaca su Apple Watch. Capire il proprio corpo non dovrebbe dipendere da come si vede: per questo l'accessibilità è trattata come una funzionalità centrale. Il principio guida è che una persona cieca possa controllare il proprio livello di stress, esplorare lo storico, leggere le analisi settimanali e configurare l'app in totale autonomia.",
    "supported_h": "Supporto su Apple Watch",
    "items": [
      ("VoiceOver.", "Ogni elemento ha etichetta, valore e descrizione significativi. I grafici sono esposti come Audio Graph: lo storico dello stress può essere esplorato con il suono tramite la corona digitale."),
      ("Testo più grande.", "L'interfaccia usa Dynamic Type ovunque. Gli indicatori compatti, come l'anello del punteggio, offrono il visualizzatore di contenuti ingranditi."),
      ("Interfaccia scura.", "L'interfaccia di Vela è scura per design in ogni schermata, senza lampi luminosi."),
      ("Differenziare senza colore.", "I livelli di stress sono sempre rinforzati da un numero e una parola — mai solo dal colore. I grafici aggiungono linee di zona quando « Differenzia senza colore » è attivo."),
      ("Contrasto sufficiente.", "Tutto il testo rispetta il rapporto di contrasto WCAG AA (4,5:1 o superiore) sullo sfondo scuro."),
      ("Riduci movimento.", "Le animazioni vengono disattivate o sostituite con alternative statiche quando « Riduci movimento » è attivo. Vela rispetta anche Riduci trasparenza e Testo in grassetto."),
    ],
    "no_media": "Vela non contiene audio né video, quindi sottotitoli e audiodescrizioni non si applicano.",
    "verify_h": "Come lo verifichiamo",
    "verify_p": "Ogni schermata passa attraverso gli audit di accessibilità automatici di Apple — etichette, contrasto, dimensione delle aree tattili e ridimensionamento del testo — come parte della suite di test dell'app, insieme alla revisione manuale con VoiceOver. Questi controlli vengono ripetuti a ogni modifica dell'interfaccia, così l'accessibilità non regredisce silenziosamente tra le versioni.",
    "feedback_h": "Feedback",
    "feedback_pre": "Se qualcosa in Vela è difficile da usare con le tecnologie assistive, è un bug. Scrivi a ",
    "feedback_post": " — le segnalazioni di accessibilità hanno priorità per la versione successiva.",
  },
  "landing": {
    "nav_cta": "Scarica",
    "title_tag": "Vela — HRV per Apple Watch. Senza abbonamento. Mai.",
    "meta_desc": "Vela misura la tua variabilità della frequenza cardiaca (HRV/SDNN) su Apple Watch e costruisce la tua baseline personale. Tutto viene elaborato sull'orologio. Si sincronizza con il tuo iCloud. Senza abbonamento, mai.",
    "eyebrow1": "HRV per Apple Watch",
    "h1": "La tua calma non è <em>la media</em> di nessuno.",
    "hero_p": "Vela misura la tua variabilità della frequenza cardiaca (SDNN) direttamente sul tuo Apple Watch e costruisce una baseline tutta tua — non una soglia generica di popolazione. Tutto il calcolo avviene sull'orologio. Nulla passa dai nostri server, perché non ne abbiamo.",
    "badge_alt": "Scarica su App Store",
    "story_eyebrow": "Sul nome", "story_h2": "Perché «Vela»",
    "story_p": "«Vela» è anche la vela di una barca — dal latino velum. Una barca a vela non lotta contro il vento: lo legge e regola la rotta. È l'idea alla base dell'app. Invece di confrontarti con uno standard esterno, Vela legge la tua baseline personale e ti aiuta a capire i tuoi schemi. Lo stress non si combatte: si legge e si regola.",
    "baseline_eyebrow": "Perché la media non funziona",
    "baseline_h2": "25&nbsp;ms di HRV può essere alto per te e basso per un'altra persona.",
    "baseline_p": "L'HRV varia enormemente da persona a persona. Una soglia di popolazione tratta tutti allo stesso modo — ed è proprio per questo che quasi sempre sbaglia. Vela costruisce la tua baseline a partire dalla tua storia reale: se hai già dati HRV sul tuo Apple Watch, può partire dal primo giorno; se sei nuovo, ci vogliono 7–14 giorni per assestarsi.",
    "legend1": "Soglia generica di popolazione", "legend2": "Campioni individuali", "legend3": "La tua baseline personale",
    "principles_eyebrow": "Come funziona", "principles_h2": "Quattro decisioni, prese per non cambiare idea.",
    "principles": [
      ("On-device", "Tutto il calcolo avviene sul tuo Watch.", "HealthKit fornisce i dati, l'orologio fa il resto. Nessun dato HRV lascia mai il tuo dispositivo verso un server Vela."),
      ("Il tuo iCloud, non il nostro", "La sincronizzazione usa il tuo account iCloud", "tramite CloudKit. Vela non ospita i tuoi dati da nessuna parte — non può, perché non ha dove."),
      ("Senza abbonamento. Mai.", "Nessuna quota mensile o annuale.", "Vela è gratis. Vela Pro è un acquisto unico: lo paghi una volta ed è tuo — mai un abbonamento."),
      ("Accessibile di serie", "VoiceOver, Dynamic Type, Reduce Motion", "e 12 lingue: spagnolo, catalano, basco, galiziano, inglese, francese, tedesco, italiano, portoghese, ceco, greco e giapponese."),
    ],
    "stress_h2": "Un punteggio, uno stato, una tendenza.",
    "tour_eyebrow": "Tour rapido", "tour_h2": "Tre schermate, ognuna con un solo compito.",
    "tour": [
      ("Punteggio attuale", "Un numero, uno stato, calcolato interamente sull'orologio — senza aspettare alcuna sincronizzazione.", "Schermata principale di Vela con un livello di stress di 34, stato Basso, calcolato sul momento."),
      ("Tendenza", "Ogni rilevazione del giorno, confrontata con la tua linea tratteggiata — non con quella di nessun altro.", "Grafico della tendenza con la media di stress del giorno e le rilevazioni orarie, confrontate con la baseline personale."),
      ("Intervalli spiegati", "Niente numeri criptici: ogni intervallo dice cosa significa e cosa aspettarsi.", "Schermata che spiega gli intervalli di stress: Normale tra 40 e 69, Alto tra 70 e 100."),
    ],
    "onboarding_eyebrow": "Così inizi", "onboarding_h2": "Ti chiediamo il permesso prima di misurare qualsiasi cosa.",
    "onboarding_p": "Vela chiede l'accesso ai tuoi dati sanitari in modo esplicito, non nelle note in piccolo, e ti dice a cosa serve ciascuno. E se sei nuovo nella misurazione dell'HRV, ti dice quanto manca per avere una baseline affidabile — senza fingere di sapere già chi sei il primo giorno.",
    "onboarding_alt": "Due passaggi del benvenuto di Vela su Apple Watch: la schermata di benvenuto e la richiesta di accesso ai dati sanitari, che spiega a cosa serve ciascuno.",
    "closing_eyebrow": "Scaricala oggi", "closing_h2": "Senza abbonamento. <em>Mai.</em>",
    "closing_p": "Vela è gratis su App Store per Apple Watch, con Vela Pro come acquisto unico.",
    "footer_support": "Supporto", "footer_privacy": "Privacy", "footer_contact": "Contatti",
  },
}

L["pt"] = {
  "lang_label": "Idioma", "back": "← Voltar ao suporte", "back_home": "← Voltar à Vela", "rights": "Todos os direitos reservados",
  "support_title": "Vela HRV — Suporte",
  "about_h": "Sobre a app",
  "about_p1": "A Vela mede o seu nível de stress usando a variabilidade da frequência cardíaca (HRV) diretamente a partir do seu Apple Watch. Todo o processamento acontece no seu dispositivo — os seus dados nunca saem do seu Apple Watch nem do seu iCloud privado.",
  "about_p2": "Durante os primeiros dias, a Vela constrói a sua linha de base pessoal para que cada leitura faça sentido para o seu corpo, e não para uma média estatística.",
  "faq_h": "Perguntas frequentes",
  "faq": [
    ("De que Apple Watch preciso?", "A Vela requer um Apple Watch com watchOS 26 ou posterior. Funciona como app independente — o iPhone não precisa de estar por perto para fazer uma medição."),
    ("Porque demora alguns dias a mostrar a minha pontuação?", "A Vela precisa de conhecer a sua HRV pessoal antes de calcular uma pontuação com significado. Durante os primeiros 7–14 dias constrói a sua linha de base — a partir daí, cada leitura reflete o seu estado real."),
    ("Onde são guardados os meus dados?", "Os seus dados sincronizam-se de forma privada através do seu próprio iCloud. A Vela não tem servidores próprios — nunca enviamos nem guardamos os seus dados fora da sua conta."),
    ("Que permissões precisa a Vela?", "A Vela pede acesso apenas de leitura ao HealthKit: a variabilidade da frequência cardíaca para a sua pontuação de stress, e o sono, os passos, a energia ativa, os treinos e a frequência cardíaca para a sua Bateria. São dados que o seu Apple Watch já recolhe automaticamente. Se quiser, também pede permissão para lhe enviar notificações com os avisos de stress."),
  ],
  "contact_h": "Contacto e suporte",
  "contact_p": "Tem alguma pergunta, encontrou um erro ou quer partilhar feedback? Escreva-nos diretamente.",
  "privacy": {
    "title_tag": "Vela HRV — Política de privacidade", "title": "Política de privacidade",
    "updated": "Última atualização: novembro de 2026",
    "highlight": "A Vela não recolhe, transmite nem armazena quaisquer dados pessoais em servidores externos. Tudo fica no seu dispositivo e no seu iCloud privado.",
    "sections": [
      ("Que dados usa a Vela", [
        "A Vela lê dados do Apple HealthKit, apenas em modo de leitura: a variabilidade da frequência cardíaca (HRV) para calcular a sua pontuação de stress pessoal, e o sono, os passos, a energia ativa, os treinos, a frequência cardíaca e a frequência cardíaca em repouso para calcular a sua Bateria — quanto o sono a carrega e o que a gasta ao longo do dia. Estes dados já são recolhidos automaticamente pelo seu Apple Watch. A Vela nunca escreve no HealthKit.",
        "A Vela também guarda as leituras que calcula — o histórico da sua pontuação de stress, a sua linha de base de HRV pessoal, as amostras de HRV em bruto usadas para a calcular e os níveis da sua Bateria."]),
      ("Onde vivem os seus dados", [
        "Todos os dados são guardados localmente no seu Apple Watch e sincronizados de forma privada através da sua própria conta iCloud, com o framework CloudKit da Apple. A Vela não tem servidores. Nenhum dado passa alguma vez por sistemas detidos ou operados pela Vela.",
        "Só você pode aceder aos seus dados. Nem nós, nem terceiros."]),
      ("Terceiros", [
        "A Vela não partilha quaisquer dados com terceiros. Não usamos serviços de análise, SDK de publicidade nem ferramentas de rastreio externas."]),
      ("Dados de saúde", [
        "A Vela acede aos dados de saúde exclusivamente para oferecer a sua funcionalidade principal — medir e acompanhar o seu nível de stress e a sua Bateria. Os dados de saúde nunca são usados para publicidade nem vendidos a ninguém."]),
      ("Compras", [
        "O Vela Pro é uma compra única na app, processada pela Apple através da App Store. A Vela nunca recebe os seus dados de pagamento: a app apenas verifica no seu dispositivo, através do StoreKit da Apple, se o Vela Pro está desbloqueado."]),
      ("Crianças", [
        "A Vela não foi concebida especificamente para crianças. Como não recolhe dados de ninguém, também não recolhe dados de menores."]),
      ("Alterações a esta política", [
        "Se esta política de privacidade mudar, a versão atualizada será publicada neste URL com uma nova data. A utilização continuada da app após as alterações constitui aceitação da política atualizada."]),
    ],
    "contact_h": "Contacto",
    "contact_pre": "Tem perguntas sobre esta política de privacidade? Escreva para ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Acessibilidade", "title": "Acessibilidade",
    "updated": "Última atualização: julho de 2026",
    "highlight": "A Vela foi desenhada para poder ser usada por completo sem ver o ecrã: todos os ecrãs funcionam com o VoiceOver e nenhuma informação depende apenas da cor.",
    "approach_h": "A nossa abordagem",
    "approach_p": "A Vela mede o stress através da variabilidade da frequência cardíaca no Apple Watch. Compreender o próprio corpo não deveria depender de como se vê, por isso a acessibilidade é tratada como uma funcionalidade central: o princípio orientador é que uma pessoa cega possa consultar o seu nível de stress, explorar o histórico, ler as análises semanais e configurar a app de forma totalmente autónoma.",
    "supported_h": "Compatibilidade no Apple Watch",
    "items": [
      ("VoiceOver.", "Todos os elementos têm etiqueta, valor e descrição com significado. Os gráficos são expostos como Audio Graphs: o histórico de stress pode ser explorado por som com a coroa digital."),
      ("Texto maior.", "A interface usa Dynamic Type em toda a app. Os indicadores compactos, como o anel de pontuação, oferecem o visualizador de conteúdo ampliado."),
      ("Interface escura.", "A interface da Vela é escura por design em todos os ecrãs, sem flashes brilhantes."),
      ("Diferenciar sem ser só pela cor.", "Os níveis de stress são sempre reforçados com um número e uma palavra — nunca apenas com cor. Os gráficos acrescentam linhas de zona ao ativar «Diferenciar sem cor»."),
      ("Contraste suficiente.", "Todo o texto cumpre o rácio de contraste WCAG AA (4,5:1 ou superior) sobre o fundo escuro."),
      ("Reduzir movimento.", "As animações são desativadas ou substituídas por alternativas estáticas com «Reduzir movimento» ativado. A Vela também respeita Reduzir transparência e Texto a negrito."),
    ],
    "no_media": "A Vela não contém áudio nem vídeo, pelo que as legendas e as audiodescrições não se aplicam.",
    "verify_h": "Como o verificamos",
    "verify_p": "Todos os ecrãs passam pelas auditorias automáticas de acessibilidade da Apple — etiquetas, contraste, tamanho das áreas de toque e escalado do texto — como parte da bateria de testes da app, juntamente com revisão manual com o VoiceOver. Estas verificações repetem-se a cada alteração da interface, para que a acessibilidade não se degrade silenciosamente entre versões.",
    "feedback_h": "Comentários",
    "feedback_pre": "Se algo na Vela for difícil de usar com tecnologia de apoio, é um bug. Escreva para ",
    "feedback_post": " — os relatórios de acessibilidade têm prioridade para a versão seguinte.",
  },
  "landing": {
    "nav_cta": "Transferir",
    "title_tag": "Vela — HRV para Apple Watch. Sem subscrição. Nunca.",
    "meta_desc": "A Vela mede a sua variabilidade da frequência cardíaca (HRV/SDNN) no Apple Watch e constrói a sua própria linha de base pessoal. Tudo é processado no relógio. Sincroniza com o seu iCloud. Sem subscrição, nunca.",
    "eyebrow1": "HRV para Apple Watch",
    "h1": "A sua calma não é <em>a média</em> de ninguém.",
    "hero_p": "A Vela mede a sua variabilidade da frequência cardíaca (SDNN) diretamente no seu Apple Watch e constrói uma linha de base própria — não um limiar genérico de população. Todo o cálculo acontece no relógio. Nada passa pelos nossos servidores, porque não os temos.",
    "badge_alt": "Transferir da App Store",
    "story_eyebrow": "Sobre o nome", "story_h2": "Porquê «Vela»",
    "story_p": "«Vela» também é a vela de um barco — do latim velum. Um veleiro não luta contra o vento: lê-o e ajusta o rumo. Essa é a ideia por trás da aplicação. Em vez de impor um padrão externo, a Vela lê a sua própria linha de base pessoal e ajuda a perceber os seus próprios padrões. O stress não se combate: lê-se e ajusta-se.",
    "baseline_eyebrow": "Porque é que a média não serve",
    "baseline_h2": "25&nbsp;ms de HRV pode ser alto para si e baixo para outra pessoa.",
    "baseline_p": "A HRV varia enormemente entre pessoas. Um limiar de população trata todos da mesma forma — e é precisamente por isso que quase sempre falha. A Vela constrói a sua própria linha de base a partir do seu histórico real: se já tem dados de HRV no seu Apple Watch, pode começar desde o primeiro dia; se é novo, demora entre 7 e 14 dias a assentar.",
    "legend1": "Limiar genérico de população", "legend2": "Amostras individuais", "legend3": "A sua linha de base pessoal",
    "principles_eyebrow": "Como funciona", "principles_h2": "Quatro decisões, tomadas para não mudar de ideias.",
    "principles": [
      ("On-device", "Todo o cálculo acontece no seu Watch.", "O HealthKit fornece os dados, o relógio faz o resto. Nenhum dado de HRV sai do seu dispositivo em direção a um servidor da Vela."),
      ("O seu iCloud, não o nosso", "A sincronização usa a sua própria conta iCloud", "via CloudKit. A Vela não aloja os seus dados em lado nenhum — não pode, porque não tem onde."),
      ("Sem subscrição. Nunca.", "Sem quotas mensais nem anuais.", "A Vela é gratuita. O Vela Pro é uma compra única: paga uma vez e é seu — nunca uma subscrição."),
      ("Acessível por predefinição", "VoiceOver, Dynamic Type, Reduce Motion", "e 12 idiomas: castelhano, catalão, basco, galego, inglês, francês, alemão, italiano, português, checo, grego e japonês."),
    ],
    "stress_h2": "Uma pontuação, um estado, uma tendência.",
    "tour_eyebrow": "Percurso rápido", "tour_h2": "Três ecrãs, cada um com uma única função.",
    "tour": [
      ("Pontuação atual", "Um número, um estado, calculado inteiramente no relógio — sem esperar que nada sincronize.", "Ecrã principal da Vela a mostrar um nível de stress de 34, estado Baixo, calculado no momento."),
      ("Tendência", "Cada leitura do dia, comparada com a sua própria linha tracejada — não com a de mais ninguém.", "Gráfico de tendência com a média de stress do dia e as leituras de cada hora, comparadas com a linha de base pessoal."),
      ("Intervalos explicados", "Nada de números crípticos: cada intervalo diz o que significa e o que esperar.", "Ecrã a explicar os intervalos de stress: Normal entre 40 e 69, Alto entre 70 e 100."),
    ],
    "onboarding_eyebrow": "Assim começa", "onboarding_h2": "Pedimos permissão antes de medir seja o que for.",
    "onboarding_p": "A Vela pede acesso aos seus dados de saúde de forma explícita, não na letra pequena, e diz-lhe para que usa cada um. E se é novo a medir HRV, diz-lhe quanto falta para ter uma linha de base fiável — sem fingir que já sabe quem é no primeiro dia.",
    "onboarding_alt": "Dois passos das boas-vindas da Vela no Apple Watch: o ecrã de boas-vindas e o pedido de acesso aos dados de saúde, que explica para que serve cada um.",
    "closing_eyebrow": "Transfira-a hoje", "closing_h2": "Sem subscrição. <em>Nunca.</em>",
    "closing_p": "A Vela é gratuita na App Store para Apple Watch, com o Vela Pro como compra única.",
    "footer_support": "Suporte", "footer_privacy": "Privacidade", "footer_contact": "Contacto",
  },
}

L["cs"] = {
  "lang_label": "Jazyk", "back": "← Zpět na podporu", "back_home": "← Zpět na Vela", "rights": "Všechna práva vyhrazena",
  "support_title": "Vela HRV — Podpora",
  "about_h": "O aplikaci",
  "about_p1": "Vela měří vaši úroveň stresu pomocí variability srdečního tepu (HRV) přímo z vašich Apple Watch. Veškeré zpracování probíhá ve vašem zařízení — vaše data nikdy neopustí vaše Apple Watch ani váš soukromý iCloud.",
  "about_p2": "Během prvních dní si Vela vytvoří vaši osobní základní linii, aby každé měření dávalo smysl pro vaše tělo, ne pro statistický průměr.",
  "faq_h": "Časté dotazy",
  "faq": [
    ("Jaké Apple Watch potřebuji?", "Vela vyžaduje Apple Watch s watchOS 26 nebo novějším. Funguje jako samostatná aplikace — pro měření nemusíte mít iPhone poblíž."),
    ("Proč trvá několik dní, než se zobrazí moje skóre?", "Vela se nejdřív musí naučit vaše osobní HRV, než dokáže spočítat smysluplné skóre. Během prvních 7–14 dní si vytváří vaši základní linii — od té chvíle každé měření odráží váš skutečný stav."),
    ("Kde jsou uložena moje data?", "Vaše data se synchronizují soukromě přes váš vlastní iCloud. Vela nemá žádné vlastní servery — vaše data nikdy neodesíláme ani neukládáme mimo váš účet."),
    ("Jaká oprávnění Vela potřebuje?", "Vela žádá o přístup k HealthKitu pouze pro čtení: variabilitu srdečního tepu pro vaše skóre stresu a spánek, kroky, aktivní energii, tréninky a srdeční tep pro vaši Baterii. Jsou to data, která vaše Apple Watch už automaticky shromažďují. Pokud chcete, požádá také o povolení posílat vám oznámení s upozorněními na stres."),
  ],
  "contact_h": "Kontakt a podpora",
  "contact_p": "Máte dotaz, našli jste chybu nebo se chcete podělit o zpětnou vazbu? Napište nám přímo.",
  "privacy": {
    "title_tag": "Vela HRV — Zásady ochrany soukromí", "title": "Zásady ochrany soukromí",
    "updated": "Poslední aktualizace: listopad 2026",
    "highlight": "Vela neshromažďuje, nepřenáší ani neukládá žádné osobní údaje na externí servery. Vše zůstává ve vašem zařízení a ve vašem soukromém iCloudu.",
    "sections": [
      ("Jaká data Vela používá", [
        "Vela čte data z Apple HealthKitu, pouze pro čtení: variabilitu srdečního tepu (HRV), aby spočítala vaše osobní skóre stresu, a spánek, kroky, aktivní energii, tréninky, srdeční tep a klidový srdeční tep, aby spočítala vaši Baterii — kolik ji nabije spánek a co ji během dne vybíjí. Tato data už vaše Apple Watch shromažďují automaticky. Vela do HealthKitu nikdy nezapisuje.",
        "Vela také ukládá měření, která spočítá — historii vašeho skóre stresu, vaši osobní základní linii HRV, surové vzorky HRV použité k jejímu výpočtu a úrovně vaší Baterie."]),
      ("Kde vaše data žijí", [
        "Všechna data jsou uložena lokálně ve vašich Apple Watch a synchronizována soukromě přes váš vlastní účet iCloud pomocí frameworku CloudKit od Applu. Vela nemá žádné servery. Žádná data nikdy neprocházejí systémy, které vlastní nebo provozuje Vela.",
        "K vašim datům máte přístup jen vy. Ne my, ne třetí strany."]),
      ("Třetí strany", [
        "Vela nesdílí žádná data se třetími stranami. Nepoužíváme analytické služby, reklamní SDK ani žádné externí sledovací nástroje."]),
      ("Zdravotní data", [
        "Vela přistupuje ke zdravotním datům výhradně kvůli své hlavní funkci — měření a sledování vaší úrovně stresu a vaší Baterie. Zdravotní data se nikdy nepoužívají k reklamě ani se nikomu neprodávají."]),
      ("Nákupy", [
        "Vela Pro je jednorázový nákup v aplikaci, který zpracovává Apple prostřednictvím App Storu. Vela nikdy nedostává vaše platební údaje: aplikace pouze ve vašem zařízení ověří přes Apple StoreKit, zda je Vela Pro odemčená."]),
      ("Děti", [
        "Vela není navržena speciálně pro děti. Protože neshromažďuje data od nikoho, neshromažďuje je ani od nezletilých."]),
      ("Změny těchto zásad", [
        "Pokud se tyto zásady ochrany soukromí změní, aktualizovaná verze bude zveřejněna na této adrese URL s novým datem. Pokračováním v používání aplikace po změnách vyjadřujete souhlas s aktualizovanými zásadami."]),
    ],
    "contact_h": "Kontakt",
    "contact_pre": "Máte dotazy k těmto zásadám ochrany soukromí? Napište na ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Přístupnost", "title": "Přístupnost",
    "updated": "Poslední aktualizace: červenec 2026",
    "highlight": "Vela je navržena tak, aby byla plně použitelná i bez zraku: každá obrazovka funguje s VoiceOverem a žádná informace není nikdy sdělována pouze barvou.",
    "approach_h": "Náš přístup",
    "approach_p": "Vela měří stres prostřednictvím variability srdečního tepu na Apple Watch. Porozumění vlastnímu tělu by nemělo záviset na tom, jak vidíte, a proto je přístupnost považována za základní funkci: hlavní zásadou je, aby si nevidomý uživatel mohl zkontrolovat úroveň stresu, procházet svou historii, číst týdenní přehledy a nastavit aplikaci zcela samostatně.",
    "supported_h": "Podpora na Apple Watch",
    "items": [
      ("VoiceOver.", "Každý prvek má smysluplný popisek, hodnotu a nápovědu. Grafy jsou dostupné jako zvukové grafy (Audio Graphs), takže historii stresu lze prozkoumat sluchem pomocí Digital Crown."),
      ("Větší text.", "Rozhraní všude používá Dynamic Type. Kompaktní prvky, jako je prstenec skóre, nabízejí Prohlížeč velkého obsahu."),
      ("Tmavé rozhraní.", "Rozhraní Vely je záměrně tmavé na každé obrazovce, bez jasných záblesků."),
      ("Rozlišení bez barvy.", "Úrovně stresu jsou vždy doplněny číslem a slovem — nikdy jen barvou. Grafy přidávají linie pásem, když je zapnuto „Rozlišovat bez barvy“."),
      ("Dostatečný kontrast.", "Veškerý text splňuje kontrastní poměr WCAG AA (4,5:1 nebo lepší) na tmavém pozadí."),
      ("Omezení pohybu.", "Animace se vypnou nebo nahradí statickými alternativami, když je zapnuto „Omezit pohyb“. Vela také respektuje Omezit průhlednost a Tučný text."),
    ],
    "no_media": "Vela neobsahuje žádný zvuk ani video, takže titulky a zvukové popisy se neuplatňují.",
    "verify_h": "Jak to ověřujeme",
    "verify_p": "Každá obrazovka prochází automatickými audity přístupnosti od Applu — kontrola popisků, kontrastu, velikosti dotykových cílů a škálování textu — jako součást testovací sady aplikace, spolu s ruční kontrolou pomocí VoiceOveru. Tyto kontroly se spouští znovu při každé změně rozhraní, aby se přístupnost mezi verzemi tiše nezhoršila.",
    "feedback_h": "Zpětná vazba",
    "feedback_pre": "Pokud se něco ve Vele obtížně používá s asistivními technologiemi, je to chyba. Napište prosím na ",
    "feedback_post": " — hlášení o přístupnosti mají prioritu pro další vydání.",
  },
  "landing": {
    "nav_cta": "Stáhnout",
    "title_tag": "Vela — HRV pro Apple Watch. Žádné předplatné. Nikdy.",
    "meta_desc": "Vela měří vaši variabilitu srdečního tepu (HRV/SDNN) na Apple Watch a vytváří vaši vlastní osobní základní linii. Vše se zpracovává na hodinkách. Synchronizuje se s vaším iCloudem. Žádné předplatné, nikdy.",
    "eyebrow1": "HRV pro Apple Watch",
    "h1": "Váš klid není <em>ničí průměr</em>.",
    "hero_p": "Vela měří vaši variabilitu srdečního tepu (SDNN) přímo na vašich Apple Watch a vytváří základní linii, která patří vám — ne obecný populační práh. Veškerý výpočet probíhá na hodinkách. Nic nikdy neprochází našimi servery, protože žádné nemáme.",
    "badge_alt": "Stáhnout v App Store",
    "story_eyebrow": "O názvu", "story_h2": "Proč „Vela“",
    "story_p": "„Vela“ je španělsky také plachta lodi — z latinského velum. Plachetnice s větrem nebojuje: čte ho a upravuje kurz. To je myšlenka celé aplikace. Místo aby vás srovnávala s vnějším standardem, Vela čte vaši vlastní osobní základní linii a pomáhá vám pochopit vaše vlastní vzorce. Se stresem se nebojuje — čte se a přizpůsobuje.",
    "baseline_eyebrow": "Proč průměr nefunguje",
    "baseline_h2": "25&nbsp;ms HRV může být pro vás vysoká a pro někoho jiného nízká.",
    "baseline_p": "HRV se mezi lidmi enormně liší. Populační práh zachází se všemi stejně — a přesně proto se skoro vždy mýlí. Vela vytváří vaši vlastní základní linii z vaší skutečné historie: pokud už na Apple Watch data HRV máte, může začít hned první den; pokud jste noví, ustálí se za 7–14 dní.",
    "legend1": "Obecný populační práh", "legend2": "Jednotlivé vzorky", "legend3": "Vaše osobní základní linie",
    "principles_eyebrow": "Jak to funguje", "principles_h2": "Čtyři rozhodnutí, učiněná tak, abychom je neměnili.",
    "principles": [
      ("On-device", "Veškerý výpočet probíhá na vašich Watch.", "HealthKit poskytuje data, hodinky udělají zbytek. Žádná data HRV nikdy neopustí vaše zařízení směrem k serveru Vely."),
      ("Váš iCloud, ne náš", "Synchronizace používá váš vlastní účet iCloud", "přes CloudKit. Vela vaše data nikde nehostuje — nemůže, protože nemá kde."),
      ("Žádné předplatné. Nikdy.", "Žádné měsíční ani roční poplatky.", "Vela je zdarma. Vela Pro je jednorázový nákup: zaplatíte jednou a je vaše — nikdy ne předplatné."),
      ("Přístupná ve výchozím stavu", "VoiceOver, Dynamic Type, Reduce Motion", "a 12 jazyků: španělština, katalánština, baskičtina, galicijština, angličtina, francouzština, němčina, italština, portugalština, čeština, řečtina a japonština."),
    ],
    "stress_h2": "Jedno skóre, jeden stav, jeden trend.",
    "tour_eyebrow": "Rychlá prohlídka", "tour_h2": "Tři obrazovky, každá s jediným úkolem.",
    "tour": [
      ("Aktuální skóre", "Jedno číslo, jeden stav, spočítané kompletně na hodinkách — bez čekání na jakoukoli synchronizaci.", "Hlavní obrazovka Vela s úrovní stresu 34, stav Nízký, spočítanou v daném okamžiku."),
      ("Trend", "Každé měření dne, porovnané s vaší vlastní přerušovanou čárou — ne s ničí jinou.", "Graf trendu s denním průměrem stresu a hodinovými měřeními, porovnanými s osobní základní linií."),
      ("Vysvětlené rozsahy", "Žádná záhadná čísla: každý rozsah říká, co znamená a co čekat.", "Obrazovka vysvětlující rozsahy stresu: Normální mezi 40 a 69, Vysoký mezi 70 a 100."),
    ],
    "onboarding_eyebrow": "Jak začít", "onboarding_h2": "Než začneme cokoli měřit, požádáme o svolení.",
    "onboarding_p": "Vela žádá o přístup k vašim zdravotním datům výslovně, ne v drobném písmu, a řekne vám, k čemu které používá. A pokud s měřením HRV začínáte, řekne vám, jak dlouho potrvá, než budete mít spolehlivou základní linii — aniž by předstírala, že vás zná už první den.",
    "onboarding_alt": "Dva kroky úvodu Vela na Apple Watch: uvítací obrazovka a žádost o přístup ke zdravotním datům, která vysvětluje, k čemu se která používají.",
    "closing_eyebrow": "Stáhněte si ji dnes", "closing_h2": "Žádné předplatné. <em>Nikdy.</em>",
    "closing_p": "Vela je zdarma v App Store pro Apple Watch, s Vela Pro jako jednorázovým nákupem.",
    "footer_support": "Podpora", "footer_privacy": "Soukromí", "footer_contact": "Kontakt",
  },
}

L["el"] = {
  "lang_label": "Γλώσσα", "back": "← Επιστροφή στην υποστήριξη", "back_home": "← Επιστροφή στο Vela", "rights": "Με την επιφύλαξη παντός δικαιώματος",
  "support_title": "Vela HRV — Υποστήριξη",
  "about_h": "Σχετικά με την εφαρμογή",
  "about_p1": "Το Vela μετρά το επίπεδο άγχους σας χρησιμοποιώντας τη μεταβλητότητα του καρδιακού ρυθμού (HRV) απευθείας από το Apple Watch σας. Όλη η επεξεργασία γίνεται στη συσκευή σας — τα δεδομένα σας δεν φεύγουν ποτέ από το Apple Watch σας ή το ιδιωτικό σας iCloud.",
  "about_p2": "Τις πρώτες ημέρες, το Vela χτίζει το προσωπικό σας baseline ώστε κάθε μέτρηση να έχει νόημα για το σώμα σας, όχι για έναν στατιστικό μέσο όρο.",
  "faq_h": "Συχνές ερωτήσεις",
  "faq": [
    ("Ποιο Apple Watch χρειάζομαι;", "Το Vela απαιτεί Apple Watch με watchOS 26 ή νεότερο. Λειτουργεί ως αυτόνομη εφαρμογή — το iPhone σας δεν χρειάζεται να είναι κοντά για να γίνει μια μέτρηση."),
    ("Γιατί χρειάζονται μερικές ημέρες για να εμφανιστεί το σκορ μου;", "Το Vela πρέπει πρώτα να μάθει το προσωπικό σας HRV για να υπολογίσει ένα ουσιαστικό σκορ. Τις πρώτες 7–14 ημέρες χτίζει το baseline σας — από εκεί και πέρα, κάθε μέτρηση αντικατοπτρίζει την πραγματική σας κατάσταση."),
    ("Πού αποθηκεύονται τα δεδομένα μου;", "Τα δεδομένα σας συγχρονίζονται ιδιωτικά μέσω του δικού σας iCloud. Το Vela δεν έχει δικούς του διακομιστές — δεν στέλνουμε ούτε αποθηκεύουμε ποτέ τα δεδομένα σας εκτός του λογαριασμού σας."),
    ("Ποιες άδειες χρειάζεται το Vela;", "Το Vela ζητά πρόσβαση μόνο για ανάγνωση στο HealthKit: τη μεταβλητότητα καρδιακού ρυθμού για το σκορ άγχους σας, και τον ύπνο, τα βήματα, την ενεργή ενέργεια, τις προπονήσεις και τον καρδιακό ρυθμό για την Μπαταρία σας. Είναι δεδομένα που το Apple Watch σας συλλέγει ήδη αυτόματα. Αν θέλετε, ζητά επίσης άδεια να σας στέλνει ειδοποιήσεις για το άγχος."),
  ],
  "contact_h": "Επικοινωνία & υποστήριξη",
  "contact_p": "Έχετε μια ερώτηση, βρήκατε ένα σφάλμα ή θέλετε να μοιραστείτε σχόλια; Επικοινωνήστε απευθείας.",
  "privacy": {
    "title_tag": "Vela HRV — Πολιτική απορρήτου", "title": "Πολιτική απορρήτου",
    "updated": "Τελευταία ενημέρωση: Νοέμβριος 2026",
    "highlight": "Το Vela δεν συλλέγει, δεν μεταδίδει και δεν αποθηκεύει κανένα προσωπικό δεδομένο σε εξωτερικούς διακομιστές. Όλα παραμένουν στη συσκευή σας και στο ιδιωτικό σας iCloud.",
    "sections": [
      ("Ποια δεδομένα χρησιμοποιεί το Vela", [
        "Το Vela διαβάζει δεδομένα από το Apple HealthKit, μόνο για ανάγνωση: τη μεταβλητότητα καρδιακού ρυθμού (HRV) για να υπολογίσει το προσωπικό σας σκορ άγχους, καθώς και τον ύπνο, τα βήματα, την ενεργή ενέργεια, τις προπονήσεις, τον καρδιακό ρυθμό και τον καρδιακό ρυθμό ηρεμίας για να υπολογίσει την Μπαταρία σας — πόσο τη φορτίζει ο ύπνος και τι την αδειάζει μέσα στη μέρα. Αυτά τα δεδομένα συλλέγονται ήδη αυτόματα από το Apple Watch σας. Το Vela δεν γράφει ποτέ στο HealthKit.",
        "Το Vela αποθηκεύει επίσης τις μετρήσεις που υπολογίζει — το ιστορικό του σκορ άγχους σας, το προσωπικό σας baseline HRV, τα ακατέργαστα δείγματα HRV που χρησιμοποιούνται για τον υπολογισμό του και τα επίπεδα της Μπαταρίας σας."]),
      ("Πού βρίσκονται τα δεδομένα σας", [
        "Όλα τα δεδομένα αποθηκεύονται τοπικά στο Apple Watch σας και συγχρονίζονται ιδιωτικά μέσω του δικού σας λογαριασμού iCloud με το framework CloudKit της Apple. Το Vela δεν έχει διακομιστές. Κανένα δεδομένο δεν περνά ποτέ από συστήματα που ανήκουν ή λειτουργούν από το Vela.",
        "Μόνο εσείς έχετε πρόσβαση στα δεδομένα σας. Ούτε εμείς, ούτε τρίτοι."]),
      ("Τρίτα μέρη", [
        "Το Vela δεν μοιράζεται κανένα δεδομένο με τρίτους. Δεν χρησιμοποιούμε υπηρεσίες ανάλυσης, διαφημιστικά SDK ή οποιαδήποτε εξωτερικά εργαλεία παρακολούθησης."]),
      ("Δεδομένα υγείας", [
        "Το Vela αποκτά πρόσβαση σε δεδομένα υγείας αποκλειστικά για να παρέχει τη βασική του λειτουργία — τη μέτρηση και την παρακολούθηση του επιπέδου άγχους σας και της Μπαταρίας σας. Τα δεδομένα υγείας δεν χρησιμοποιούνται ποτέ για διαφήμιση ούτε πωλούνται σε κανέναν."]),
      ("Αγορές", [
        "Το Vela Pro είναι μια εφάπαξ αγορά εντός της εφαρμογής, την οποία διεκπεραιώνει η Apple μέσω του App Store. Το Vela δεν λαμβάνει ποτέ τα στοιχεία πληρωμής σας: η εφαρμογή ελέγχει μόνο στη συσκευή σας, μέσω του StoreKit της Apple, αν το Vela Pro είναι ξεκλείδωτο."]),
      ("Παιδιά", [
        "Το Vela δεν έχει σχεδιαστεί ειδικά για παιδιά. Αφού δεν συλλέγει δεδομένα από κανέναν, δεν συλλέγει ούτε από ανηλίκους."]),
      ("Αλλαγές σε αυτήν την πολιτική", [
        "Εάν αυτή η πολιτική απορρήτου αλλάξει, η ενημερωμένη έκδοση θα δημοσιευτεί σε αυτήν τη διεύθυνση URL με νέα ημερομηνία. Η συνεχής χρήση της εφαρμογής μετά τις αλλαγές συνιστά αποδοχή της ενημερωμένης πολιτικής."]),
    ],
    "contact_h": "Επικοινωνία",
    "contact_pre": "Ερωτήσεις σχετικά με αυτήν την πολιτική απορρήτου; Γράψτε στο ", "contact_post": ".",
  },
  "a11y": {
    "title_tag": "Vela HRV — Προσβασιμότητα", "title": "Προσβασιμότητα",
    "updated": "Τελευταία ενημέρωση: Ιούλιος 2026",
    "highlight": "Το Vela είναι σχεδιασμένο ώστε να μπορεί να χρησιμοποιηθεί πλήρως χωρίς όραση: κάθε οθόνη λειτουργεί με το VoiceOver και καμία πληροφορία δεν μεταδίδεται ποτέ μόνο με χρώμα.",
    "approach_h": "Η προσέγγισή μας",
    "approach_p": "Το Vela μετρά το άγχος μέσω της μεταβλητότητας του καρδιακού ρυθμού στο Apple Watch. Η κατανόηση του σώματός σας δεν θα έπρεπε να εξαρτάται από το πώς βλέπετε, γι’ αυτό η προσβασιμότητα αντιμετωπίζεται ως βασική λειτουργία: η κατευθυντήρια αρχή είναι ότι ένας τυφλός χρήστης μπορεί να ελέγξει το επίπεδο άγχους του, να εξερευνήσει το ιστορικό του, να διαβάσει τις εβδομαδιαίες αναλύσεις του και να ρυθμίσει την εφαρμογή εντελώς μόνος του.",
    "supported_h": "Υποστήριξη στο Apple Watch",
    "items": [
      ("VoiceOver.", "Κάθε στοιχείο έχει ουσιαστική ετικέτα, τιμή και υπόδειξη. Τα γραφήματα παρουσιάζονται ως Audio Graphs: το ιστορικό άγχους μπορεί να εξερευνηθεί με ήχο μέσω του Digital Crown."),
      ("Μεγαλύτερο κείμενο.", "Η διεπαφή χρησιμοποιεί Dynamic Type παντού. Οι συμπαγείς ενδείξεις, όπως ο δακτύλιος σκορ, προσφέρουν το πρόγραμμα προβολής μεγάλου περιεχομένου."),
      ("Σκούρα διεπαφή.", "Η διεπαφή του Vela είναι σκούρα εκ σχεδιασμού σε κάθε οθόνη, χωρίς έντονες αναλαμπές."),
      ("Διαφοροποίηση χωρίς χρώμα.", "Τα επίπεδα άγχους ενισχύονται πάντα με έναν αριθμό και μια λέξη — ποτέ μόνο με χρώμα. Τα γραφήματα προσθέτουν γραμμές ζωνών όταν είναι ενεργή η επιλογή «Διαφοροποίηση χωρίς χρώμα»."),
      ("Επαρκής αντίθεση.", "Όλο το κείμενο πληροί τον λόγο αντίθεσης WCAG AA (4,5:1 ή καλύτερο) πάνω στο σκούρο φόντο."),
      ("Μείωση κίνησης.", "Οι κινήσεις απενεργοποιούνται ή αντικαθίστανται από στατικές εναλλακτικές όταν είναι ενεργή η «Μείωση κίνησης». Το Vela σέβεται επίσης τη Μείωση διαφάνειας και το Έντονο κείμενο."),
    ],
    "no_media": "Το Vela δεν περιέχει ήχο ή βίντεο, επομένως οι υπότιτλοι και οι ηχητικές περιγραφές δεν ισχύουν.",
    "verify_h": "Πώς το επαληθεύουμε",
    "verify_p": "Κάθε οθόνη περνά από τους αυτοματοποιημένους ελέγχους προσβασιμότητας της Apple — έλεγχος ετικετών, αντίθεσης, μεγέθους περιοχών αφής και κλιμάκωσης κειμένου — ως μέρος της σουίτας δοκιμών της εφαρμογής, μαζί με χειροκίνητο έλεγχο με το VoiceOver. Αυτοί οι έλεγχοι εκτελούνται ξανά σε κάθε αλλαγή της διεπαφής, ώστε η προσβασιμότητα να μην υποβαθμίζεται σιωπηλά μεταξύ των εκδόσεων.",
    "feedback_h": "Σχόλια",
    "feedback_pre": "Αν κάτι στο Vela είναι δύσκολο να χρησιμοποιηθεί με υποστηρικτική τεχνολογία, αυτό είναι σφάλμα. Παρακαλούμε γράψτε στο ",
    "feedback_post": " — οι αναφορές προσβασιμότητας έχουν προτεραιότητα για την επόμενη έκδοση.",
  },
  "landing": {
    "nav_cta": "Λήψη",
    "title_tag": "Vela — HRV για Apple Watch. Χωρίς συνδρομή. Ποτέ.",
    "meta_desc": "Το Vela μετρά τη μεταβλητότητα του καρδιακού σας ρυθμού (HRV/SDNN) στο Apple Watch και χτίζει το δικό σας προσωπικό baseline. Όλα επεξεργάζονται στο ρολόι. Συγχρονίζεται με το iCloud σας. Χωρίς συνδρομή, ποτέ.",
    "eyebrow1": "HRV για Apple Watch",
    "h1": "Η ηρεμία σας δεν είναι <em>ο μέσος όρος κανενός</em>.",
    "hero_p": "Το Vela μετρά τη μεταβλητότητα του καρδιακού σας ρυθμού (SDNN) απευθείας στο Apple Watch σας και χτίζει ένα baseline που είναι δικό σας — όχι ένα γενικό όριο πληθυσμού. Όλος ο υπολογισμός γίνεται στο ρολόι. Τίποτα δεν περνά ποτέ από τους διακομιστές μας, γιατί δεν έχουμε.",
    "badge_alt": "Λήψη από το App Store",
    "story_eyebrow": "Σχετικά με το όνομα", "story_h2": "Γιατί «Vela»",
    "story_p": "«Vela» είναι επίσης η ισπανική λέξη για το πανί ενός σκάφους — από το λατινικό velum. Ένα ιστιοφόρο δεν παλεύει με τον άνεμο: τον διαβάζει και προσαρμόζει την πορεία του. Αυτή είναι η ιδέα πίσω από την εφαρμογή. Αντί να σας συγκρίνει με ένα εξωτερικό πρότυπο, το Vela διαβάζει το δικό σας προσωπικό baseline και σας βοηθά να κατανοήσετε τα δικά σας μοτίβα. Το άγχος δεν το πολεμάς — το διαβάζεις και προσαρμόζεσαι.",
    "baseline_eyebrow": "Γιατί ο μέσος όρος δεν λειτουργεί",
    "baseline_h2": "25&nbsp;ms HRV μπορεί να είναι υψηλά για εσάς και χαμηλά για κάποιον άλλον.",
    "baseline_p": "Το HRV διαφέρει τεράστια από άνθρωπο σε άνθρωπο. Ένα όριο πληθυσμού αντιμετωπίζει τους πάντες το ίδιο — και ακριβώς γι’ αυτό σχεδόν πάντα κάνει λάθος. Το Vela χτίζει το δικό σας baseline από το πραγματικό σας ιστορικό: αν έχετε ήδη δεδομένα HRV στο Apple Watch σας, μπορεί να ξεκινήσει από την πρώτη ημέρα· αν είστε νέος, χρειάζονται 7–14 ημέρες για να σταθεροποιηθεί.",
    "legend1": "Γενικό όριο πληθυσμού", "legend2": "Μεμονωμένα δείγματα", "legend3": "Το προσωπικό σας baseline",
    "principles_eyebrow": "Πώς λειτουργεί", "principles_h2": "Τέσσερις αποφάσεις, που πάρθηκαν για να μην τις αλλάξουμε.",
    "principles": [
      ("On-device", "Όλος ο υπολογισμός γίνεται στο Watch σας.", "Το HealthKit παρέχει τα δεδομένα, το ρολόι κάνει τα υπόλοιπα. Κανένα δεδομένο HRV δεν φεύγει ποτέ από τη συσκευή σας προς διακομιστή του Vela."),
      ("Το iCloud σας, όχι το δικό μας", "Ο συγχρονισμός χρησιμοποιεί τον δικό σας λογαριασμό iCloud", "μέσω CloudKit. Το Vela δεν φιλοξενεί τα δεδομένα σας πουθενά — δεν μπορεί, γιατί δεν έχει πού."),
      ("Χωρίς συνδρομή. Ποτέ.", "Χωρίς μηνιαίες ή ετήσιες χρεώσεις.", "Το Vela είναι δωρεάν. Το Vela Pro είναι εφάπαξ αγορά: το πληρώνετε μία φορά και είναι δικό σας — ποτέ συνδρομή."),
      ("Προσβάσιμο από προεπιλογή", "VoiceOver, Dynamic Type, Reduce Motion", "και 12 γλώσσες: ισπανικά, καταλανικά, βασκικά, γαλικιανά, αγγλικά, γαλλικά, γερμανικά, ιταλικά, πορτογαλικά, τσέχικα, ελληνικά και ιαπωνικά."),
    ],
    "stress_h2": "Ένα σκορ, μία κατάσταση, μία τάση.",
    "tour_eyebrow": "Γρήγορη περιήγηση", "tour_h2": "Τρεις οθόνες, καθεμία με μία μόνο δουλειά.",
    "tour": [
      ("Τρέχον σκορ", "Ένας αριθμός, μία κατάσταση, υπολογισμένα εξ ολοκλήρου στο ρολόι — χωρίς αναμονή για κανέναν συγχρονισμό.", "Η κύρια οθόνη του Vela με επίπεδο στρες 34, κατάσταση Χαμηλό, υπολογισμένο τη στιγμή εκείνη."),
      ("Τάση", "Κάθε μέτρηση της ημέρας, σε σύγκριση με τη δική σας διακεκομμένη γραμμή — όχι κανενός άλλου.", "Γράφημα τάσης με τον μέσο όρο άγχους της ημέρας και τις ωριαίες μετρήσεις, σε σύγκριση με το προσωπικό baseline."),
      ("Εξήγηση των εύρων", "Χωρίς κρυπτικούς αριθμούς: κάθε εύρος λέει τι σημαίνει και τι να περιμένετε.", "Οθόνη που εξηγεί τα εύρη άγχους: Φυσιολογικό μεταξύ 40 και 69, Υψηλό μεταξύ 70 και 100."),
    ],
    "onboarding_eyebrow": "Ξεκινώντας", "onboarding_h2": "Ζητάμε άδεια πριν μετρήσουμε οτιδήποτε.",
    "onboarding_p": "Το Vela ζητά πρόσβαση στα δεδομένα υγείας σας ρητά, όχι στα ψιλά γράμματα, και σας λέει για τι χρησιμοποιεί το καθένα. Και αν είστε νέος στη μέτρηση HRV, σας λέει πόσος χρόνος απομένει μέχρι να έχετε ένα αξιόπιστο baseline — χωρίς να προσποιείται ότι σας γνωρίζει από την πρώτη ημέρα.",
    "onboarding_alt": "Δύο βήματα της υποδοχής του Vela στο Apple Watch: η οθόνη καλωσορίσματος και το αίτημα πρόσβασης στα δεδομένα υγείας, που εξηγεί για τι χρησιμοποιείται το καθένα.",
    "closing_eyebrow": "Κατεβάστε το σήμερα", "closing_h2": "Χωρίς συνδρομή. <em>Ποτέ.</em>",
    "closing_p": "Το Vela είναι δωρεάν στο App Store για Apple Watch, με το Vela Pro ως εφάπαξ αγορά.",
    "footer_support": "Υποστήριξη", "footer_privacy": "Απόρρητο", "footer_contact": "Επικοινωνία",
  },
}

L["ja"] = {
  "lang_label": "言語", "back": "← サポートに戻る", "back_home": "← Vela に戻る", "rights": "無断複写・転載を禁じます",
  "support_title": "Vela HRV — サポート",
  "about_h": "アプリについて",
  "about_p1": "Vela は心拍変動（HRV）を使って、Apple Watch から直接ストレスレベルを測定します。すべての処理はデバイス上で行われ、データが Apple Watch やプライベートな iCloud の外に出ることはありません。",
  "about_p2": "最初の数日間で、Vela はあなた個人のベースラインを構築します。こうして、それぞれの測定値が統計的な平均ではなく、あなたの身体にとって意味を持つようになります。",
  "faq_h": "よくある質問",
  "faq": [
    ("どの Apple Watch が必要ですか？", "Vela には watchOS 26 以降の Apple Watch が必要です。単体で動作するため、測定に iPhone が近くにある必要はありません。"),
    ("スコアが表示されるまで数日かかるのはなぜですか？", "意味のあるスコアを算出するには、Vela がまずあなた個人の HRV を学習する必要があります。最初の 7〜14 日間でベースラインを構築し、それ以降は各測定値が実際の状態を反映します。"),
    ("データはどこに保存されますか？", "データはあなた自身の iCloud を通じてプライベートに同期されます。Vela は独自のサーバーを持たず、あなたのアカウントの外にデータを送信・保存することは一切ありません。"),
    ("Vela はどの権限を必要としますか？", "Vela は HealthKit への読み取り専用アクセスを求めます。ストレススコアのために心拍変動を、バッテリーのために睡眠・歩数・アクティブエネルギー・ワークアウト・心拍数を読み取ります。いずれも Apple Watch がすでに自動的に収集しているデータです。ご希望の場合は、ストレスの通知を送るための許可も求めます。"),
  ],
  "contact_h": "お問い合わせとサポート",
  "contact_p": "ご質問、不具合の報告、フィードバックの共有などがあれば、直接ご連絡ください。",
  "privacy": {
    "title_tag": "Vela HRV — プライバシーポリシー", "title": "プライバシーポリシー",
    "updated": "最終更新：2026年11月",
    "highlight": "Vela は個人データを外部サーバーで収集・送信・保存することは一切ありません。すべてはあなたのデバイスとプライベートな iCloud にとどまります。",
    "sections": [
      ("Vela が使用するデータ", [
        "Vela は Apple HealthKit のデータを読み取り専用で利用します。心拍変動（HRV）からあなた個人のストレススコアを、睡眠・歩数・アクティブエネルギー・ワークアウト・心拍数・安静時心拍数からバッテリー（睡眠でどれだけ充電され、日中に何で消費されたか）を算出します。これらのデータはすでに Apple Watch によって自動的に収集されています。Vela が HealthKit に書き込むことはありません。",
        "Vela は算出した測定値も保存します。ストレススコアの履歴、あなた個人の HRV ベースライン、ベースラインの算出に使われる HRV の生サンプル、そしてバッテリーのレベルです。"]),
      ("データの保存場所", [
        "すべてのデータは Apple Watch にローカルで保存され、Apple の CloudKit フレームワークを使ってあなた自身の iCloud アカウントを通じてプライベートに同期されます。Vela はサーバーを持ちません。Vela が所有・運用するシステムをデータが通過することは一切ありません。",
        "あなたのデータにアクセスできるのはあなただけです。私たちも第三者もアクセスできません。"]),
      ("第三者", [
        "Vela はいかなるデータも第三者と共有しません。分析サービス、広告 SDK、外部のトラッキングツールは一切使用していません。"]),
      ("健康データ", [
        "Vela が健康データにアクセスするのは、中核機能であるストレスレベルとバッテリーの測定と記録を提供するためだけです。健康データが広告に使われたり、いかなる相手にも販売されたりすることはありません。"]),
      ("購入", [
        "Vela Pro は買い切りのアプリ内課金で、App Store を通じて Apple が処理します。Vela があなたの支払い情報を受け取ることはありません。アプリはデバイス上で Apple の StoreKit を通じて、Vela Pro が解除されているかどうかを確認するだけです。"]),
      ("子ども", [
        "Vela は子ども向けに特別に設計されたアプリではありません。誰のデータも収集しないため、未成年者のデータも収集しません。"]),
      ("本ポリシーの変更", [
        "本プライバシーポリシーが変更された場合、更新版が新しい日付とともにこの URL で公開されます。変更後もアプリを継続して使用することは、更新されたポリシーへの同意とみなされます。"]),
    ],
    "contact_h": "お問い合わせ",
    "contact_pre": "本プライバシーポリシーについてのご質問は ", "contact_post": " までご連絡ください。",
  },
  "a11y": {
    "title_tag": "Vela HRV — アクセシビリティ", "title": "アクセシビリティ",
    "updated": "最終更新：2026年7月",
    "highlight": "Vela は画面を見なくても完全に使えるように設計されています。すべての画面が VoiceOver に対応し、色だけで情報を伝えることは一切ありません。",
    "approach_h": "私たちの考え方",
    "approach_p": "Vela は Apple Watch 上で心拍変動を通じてストレスを測定します。自分の身体を理解できるかどうかが、見え方によって左右されるべきではありません。だからこそアクセシビリティを中核機能として扱っています。指針となるのは、目の見えない利用者がストレスレベルを確認し、履歴を調べ、週ごとの分析を読み、アプリを完全に自力で設定できることです。",
    "supported_h": "Apple Watch での対応",
    "items": [
      ("VoiceOver。", "すべての要素に意味のあるラベル、値、ヒントが付いています。グラフは Audio Graph として提供され、Digital Crown を使って音でストレス履歴を探索できます。"),
      ("大きな文字。", "インターフェースは全体で Dynamic Type に対応しています。スコアリングのようなコンパクトな表示では、拡大コンテンツビューアを利用できます。"),
      ("ダークなインターフェース。", "Vela のインターフェースはすべての画面で意図的にダークに設計されており、まぶしい点滅はありません。"),
      ("色以外での区別。", "ストレスレベルは常に数値と語で補強され、色だけで示されることはありません。「色を使わずに区別」をオンにすると、グラフにゾーンの線が追加されます。"),
      ("十分なコントラスト。", "すべてのテキストが、ダークな背景に対して WCAG AA のコントラスト比（4.5:1 以上）を満たしています。"),
      ("視差効果を減らす。", "「視差効果を減らす」がオンのとき、アニメーションは無効化されるか、静的な代替に置き換えられます。Vela は「透明度を下げる」と「文字を太くする」にも対応します。"),
    ],
    "no_media": "Vela には音声や動画が含まれないため、字幕や音声解説は該当しません。",
    "verify_h": "検証方法",
    "verify_p": "すべての画面は、アプリのテストスイートの一部として Apple の自動アクセシビリティ監査（ラベル、コントラスト、タップ領域のサイズ、テキストの拡大縮小のチェック）を通過し、あわせて VoiceOver による手動レビューも行っています。これらのチェックはインターフェースが変わるたびに再実行され、バージョン間でアクセシビリティが静かに後退しないようにしています。",
    "feedback_h": "フィードバック",
    "feedback_pre": "Vela の中に支援技術で使いにくい箇所があれば、それはバグです。",
    "feedback_post": " までご連絡ください。アクセシビリティに関する報告は次のリリースで優先的に対応します。",
  },
  "landing": {
    "nav_cta": "ダウンロード",
    "title_tag": "Vela — Apple Watch 用 HRV。サブスクなし。ずっと。",
    "meta_desc": "Vela は Apple Watch で心拍変動（HRV/SDNN）を測定し、あなた自身の個人ベースラインを構築します。すべては時計上で処理されます。iCloud と同期します。サブスクリプションは、ずっとありません。",
    "eyebrow1": "Apple Watch 用 HRV",
    "h1": "あなたの穏やかさは、<em>誰かの平均</em>ではない。",
    "hero_p": "Vela は Apple Watch 上で直接あなたの心拍変動（SDNN）を測定し、一般的な集団のしきい値ではなく、あなただけのベースラインを構築します。すべての計算は時計上で行われます。私たちのサーバーを経由するものは何もありません。サーバーがないからです。",
    "badge_alt": "App Store でダウンロード",
    "story_eyebrow": "名前について", "story_h2": "なぜ「Vela」なのか",
    "story_p": "「Vela」はスペイン語で船の帆のことでもあり、ラテン語の velum に由来します。ヨットは風と戦いません。風を読み、針路を調整します。それがこのアプリの考え方です。外部の基準と比べるのではなく、Vela はあなた自身の個人ベースラインを読み取り、あなた自身のパターンを理解する手助けをします。ストレスは戦うものではなく、読み取って合わせていくものです。",
    "baseline_eyebrow": "なぜ平均では不十分なのか",
    "baseline_h2": "同じ 25&nbsp;ms の HRV でも、ある人には高く、別の人には低いことがあります。",
    "baseline_p": "HRV は人によって大きく異なります。集団のしきい値は誰もを同じように扱うため、ほとんどの場合それが外れる原因になります。Vela はあなたの実際の履歴からあなた自身のベースラインを構築します。Apple Watch にすでに HRV データがあれば初日から始められ、初めての場合は定まるまで 7〜14 日かかります。",
    "legend1": "一般的な集団のしきい値", "legend2": "個々のサンプル", "legend3": "あなたの個人ベースライン",
    "principles_eyebrow": "しくみ", "principles_h2": "考えを変えないために下した、4つの決定。",
    "principles": [
      ("On-device", "すべての計算は Watch 上で行われます。", "HealthKit がデータを提供し、残りは時計が処理します。HRV データが Vela のサーバーへ向けてデバイスの外に出ることはありません。"),
      ("私たちのではなく、あなたの iCloud", "同期にはあなた自身の iCloud アカウントを使います。", "CloudKit 経由です。Vela はあなたのデータをどこにも保管しません。保管する場所がないため、できないのです。"),
      ("サブスクなし。ずっと。", "月額も年額もありません。", "Vela は無料です。Vela Pro は買い切り：一度支払えばずっと使えます。サブスクリプションにはしません。"),
      ("はじめからアクセシブル", "VoiceOver、Dynamic Type、視差効果を減らす。", "対応言語は12：スペイン語、カタルーニャ語、バスク語、ガリシア語、英語、フランス語、ドイツ語、イタリア語、ポルトガル語、チェコ語、ギリシャ語、日本語。"),
    ],
    "stress_h2": "1つのスコア、1つの状態、1つのトレンド。",
    "tour_eyebrow": "クイックツアー", "tour_h2": "3つの画面、それぞれに役割は1つ。",
    "tour": [
      ("現在のスコア", "1つの数字、1つの状態。すべて時計上で計算され、同期を待つ必要はありません。", "ストレスレベル 34（低い）をその場で算出して表示する Vela のメイン画面。"),
      ("トレンド", "その日のすべての測定値を、他の誰でもない、あなた自身の破線と比較します。", "その日の平均ストレスと1時間ごとの測定値を、個人ベースラインと比較したトレンドチャート。"),
      ("範囲の説明", "分かりにくい数字はなし。どの範囲にも、意味と何を予期すべきかが書かれています。", "ストレスの範囲を説明する画面：正常は40〜69、高いは70〜100。"),
    ],
    "onboarding_eyebrow": "使い始める", "onboarding_h2": "何かを測定する前に、許可を求めます。",
    "onboarding_p": "Vela は細かい文字の中ではなく、はっきりと健康データへのアクセスを求め、それぞれを何に使うのかを伝えます。そして HRV の測定が初めてなら、信頼できるベースラインができるまでの日数を伝えます。初日からあなたを知っているふりはしません。",
    "onboarding_alt": "Apple Watch での Vela の初期設定の2つのステップ：ようこそ画面と、それぞれのデータを何に使うかを説明する健康データへのアクセスのリクエスト。",
    "closing_eyebrow": "今すぐダウンロード", "closing_h2": "サブスクなし。<em>ずっと。</em>",
    "closing_p": "Vela は Apple Watch 向けに App Store で無料、Vela Pro は買い切りで入手できます。",
    "footer_support": "サポート", "footer_privacy": "プライバシー", "footer_contact": "お問い合わせ",
  },
}

# ---------------------------------------------------------------- changelog
# Public changelog. Version history is derived from the app repo's version tags
# (1.0.0 … 1.3.1). A build in App Store review carries a "review" status and a build
# in public beta a "beta" status (see the Vela 2.0 block below); both show as
# not-yet-available for transparency.

_FOOTER_CHANGELOG = {
  "es": "Novedades", "en": "Changelog", "ca": "Novetats", "eu": "Berritasunak",
  "gl": "Novidades", "fr": "Nouveautés", "de": "Neuigkeiten", "it": "Novità",
  "pt": "Novidades", "cs": "Novinky", "el": "Νέα", "ja": "変更履歴",
}

CHANGELOG = {}

CHANGELOG["en"] = {
  "title_tag": "Vela HRV — Changelog", "title": "Changelog",
  "intro": "Every version of Vela, and what changed.",
  "status_review": "In review · App Store",
  "unreleased_note": "This build is with Apple for review and can't be downloaded yet.",
  "entries": [
    {"version": "1.3.1", "date": "15 September 2026", "status": "released", "changes": [
      "Fixed a bug where updating from an older version could temporarily leave the app without your data until it finished resyncing."]},
    {"version": "1.3.0", "date": "14 September 2026", "status": "released", "changes": [
      "New ring-style complication showing your stress score on your watch face.",
      "Three new languages — Czech, Greek and Japanese. Vela now speaks 12.",
      "Fixed repeated notifications when Vela catches up on older readings.",
      "Notifications can be turned off inside the app even when the system permission is on.",
      "The month view in History now refreshes when you reopen the app."]},
    {"version": "1.2.3", "date": "6 September 2026", "status": "released", "changes": [
      "Turn notifications on or off inside the app when the system permission is already granted."]},
    {"version": "1.2.2", "date": "23 August 2026", "status": "released", "changes": [
      "Dates now follow your language.",
      "Vela falls back to English on devices set to an unsupported language."]},
    {"version": "1.2.1", "date": "8 August 2026", "status": "released", "changes": [
      "Removed a weekly-analysis notification that fired right after opening the app.",
      "The baseline-building ring now appears on fresh installs."]},
    {"version": "1.2.0", "date": "8 July 2026", "status": "released", "changes": [
      "Seven more languages: Catalan, Basque, Galician, French, German, Italian and Portuguese.",
      "Full VoiceOver support across every screen.",
      "Dynamic Type, Reduce Transparency, Differentiate Without Color and the Large Content Viewer.",
      "Higher text contrast to meet WCAG AA."]},
    {"version": "1.1.1", "date": "16 June 2026", "status": "released", "changes": [
      "Fixed the weekly-insight notification not always being delivered."]},
    {"version": "1.1.0", "date": "26 May 2026", "status": "released", "changes": [
      "Weekly Insights: Vela spots patterns in your stress and explains them in plain words.",
      "Redesigned History with day, week and month drill-down.",
      "New HRV complication with a bar chart for your watch face.",
      "Overnight readings are recovered, so your history has fewer gaps."]},
    {"version": "1.0.0", "date": "26 April 2026", "status": "released", "changes": [
      "First release. On-device stress score from HRV on Apple Watch, your own baseline, trends and clear range explanations — no account, no servers, no subscription."]},
  ],
}

CHANGELOG["es"] = {
  "title_tag": "Vela HRV — Registro de cambios", "title": "Registro de cambios",
  "intro": "Todas las versiones de Vela y qué cambió en cada una.",
  "status_review": "En revisión · App Store",
  "unreleased_note": "Esta versión está en revisión por Apple y todavía no se puede descargar.",
  "entries": [
    {"version": "1.3.1", "date": "15 de septiembre de 2026", "status": "released", "changes": [
      "Corregido un fallo por el que actualizar desde una versión anterior podía dejar la app sin tus datos temporalmente hasta que terminaba de sincronizar."]},
    {"version": "1.3.0", "date": "14 de septiembre de 2026", "status": "released", "changes": [
      "Nueva complicación circular con tu puntuación de estrés en la esfera del reloj.",
      "Tres idiomas nuevos: checo, griego y japonés. Vela ya está en 12 idiomas.",
      "Corregidas las notificaciones repetidas cuando Vela recupera lecturas antiguas.",
      "Las notificaciones se pueden desactivar dentro de la app aunque el permiso del sistema esté activado.",
      "La vista de mes en el historial ahora se actualiza al volver a abrir la app."]},
    {"version": "1.2.3", "date": "6 de septiembre de 2026", "status": "released", "changes": [
      "Activa o desactiva las notificaciones dentro de la app cuando el permiso del sistema ya está concedido."]},
    {"version": "1.2.2", "date": "23 de agosto de 2026", "status": "released", "changes": [
      "Las fechas ahora siguen tu idioma.",
      "Vela usa el inglés en dispositivos con un idioma no compatible."]},
    {"version": "1.2.1", "date": "8 de agosto de 2026", "status": "released", "changes": [
      "Eliminada una notificación de análisis semanal que aparecía justo al abrir la app.",
      "El anillo de construcción de la línea base vuelve a aparecer en instalaciones nuevas."]},
    {"version": "1.2.0", "date": "8 de julio de 2026", "status": "released", "changes": [
      "Siete idiomas más: catalán, euskera, gallego, francés, alemán, italiano y portugués.",
      "Compatibilidad completa con VoiceOver en todas las pantallas.",
      "Dynamic Type, Reducir transparencia, Diferenciar sin color y el visor de contenido ampliado.",
      "Mayor contraste de texto para cumplir WCAG AA."]},
    {"version": "1.1.1", "date": "16 de junio de 2026", "status": "released", "changes": [
      "Corregido el envío poco fiable de la notificación de análisis semanal."]},
    {"version": "1.1.0", "date": "26 de mayo de 2026", "status": "released", "changes": [
      "Análisis semanales: Vela detecta patrones en tu estrés y te los explica con palabras claras.",
      "Historial rediseñado con navegación por día, semana y mes.",
      "Nueva complicación de HRV con gráfico de barras para la esfera del reloj.",
      "Se recuperan las lecturas nocturnas, así el historial tiene menos huecos."]},
    {"version": "1.0.0", "date": "26 de abril de 2026", "status": "released", "changes": [
      "Primera versión. Score de estrés a partir del HRV en el Apple Watch, tu propia línea base, tendencias y explicación clara de los rangos — sin cuenta, sin servidores, sin suscripción."]},
  ],
}

CHANGELOG["ca"] = {
  "title_tag": "Vela HRV — Registre de canvis", "title": "Registre de canvis",
  "intro": "Totes les versions de Vela i què va canviar a cadascuna.",
  "status_review": "En revisió · App Store",
  "unreleased_note": "Aquesta versió està en revisió per Apple i encara no es pot descarregar.",
  "entries": [
    {"version": "1.3.1", "date": "15 de setembre de 2026", "status": "released", "changes": [
      "Corregit un error pel qual actualitzar des d'una versió anterior podia deixar l'app sense les teves dades temporalment fins que acabava de sincronitzar-se."]},
    {"version": "1.3.0", "date": "14 de setembre de 2026", "status": "released", "changes": [
      "Nova complicació circular amb la teva puntuació d'estrès a l'esfera del rellotge.",
      "Tres idiomes nous: txec, grec i japonès. Vela ja està en 12 idiomes.",
      "Corregides les notificacions repetides quan Vela recupera lectures antigues.",
      "Les notificacions es poden desactivar dins de l'app encara que el permís del sistema estigui activat.",
      "La vista de mes a l'historial ara s'actualitza en tornar a obrir l'app."]},
    {"version": "1.2.3", "date": "6 de setembre de 2026", "status": "released", "changes": [
      "Activa o desactiva les notificacions dins de l'app quan el permís del sistema ja està concedit."]},
    {"version": "1.2.2", "date": "23 d'agost de 2026", "status": "released", "changes": [
      "Les dates ara segueixen el teu idioma.",
      "Vela fa servir l'anglès en dispositius amb un idioma no compatible."]},
    {"version": "1.2.1", "date": "8 d'agost de 2026", "status": "released", "changes": [
      "Eliminada una notificació d'anàlisi setmanal que apareixia just en obrir l'app.",
      "L'anell de construcció de la línia base torna a aparèixer en instal·lacions noves."]},
    {"version": "1.2.0", "date": "8 de juliol de 2026", "status": "released", "changes": [
      "Set idiomes més: català, èuscar, gallec, francès, alemany, italià i portuguès.",
      "Compatibilitat completa amb VoiceOver a totes les pantalles.",
      "Dynamic Type, Reduir la transparència, Diferenciar sense color i el visor de contingut ampliat.",
      "Més contrast de text per complir WCAG AA."]},
    {"version": "1.1.1", "date": "16 de juny de 2026", "status": "released", "changes": [
      "Corregit l'enviament poc fiable de la notificació d'anàlisi setmanal."]},
    {"version": "1.1.0", "date": "26 de maig de 2026", "status": "released", "changes": [
      "Anàlisis setmanals: Vela detecta patrons en el teu estrès i te'ls explica amb paraules clares.",
      "Historial redissenyat amb navegació per dia, setmana i mes.",
      "Nova complicació d'HRV amb gràfic de barres per a l'esfera del rellotge.",
      "Es recuperen les lectures nocturnes, així l'historial té menys buits."]},
    {"version": "1.0.0", "date": "26 d'abril de 2026", "status": "released", "changes": [
      "Primera versió. Score d'estrès a partir de l'HRV a l'Apple Watch, la teva pròpia línia base, tendències i explicació clara dels rangs — sense compte, sense servidors, sense subscripció."]},
  ],
}

CHANGELOG["eu"] = {
  "title_tag": "Vela HRV — Aldaketen erregistroa", "title": "Aldaketen erregistroa",
  "intro": "Velaren bertsio guztiak eta bakoitzean zer aldatu zen.",
  "status_review": "Berrikuspenean · App Store",
  "unreleased_note": "Bertsio hau Apple-k berrikusten ari da eta oraindik ezin da deskargatu.",
  "entries": [
    {"version": "1.3.1", "date": "2026ko irailaren 15a", "status": "released", "changes": [
      "Konpondu da akats bat: bertsio zaharrago batetik eguneratzean, aplikazioa aldi baterako datu gabe gera zitekeen berriro sinkronizatu arte."]},
    {"version": "1.3.0", "date": "2026ko irailaren 14a", "status": "released", "changes": [
      "Erlojuaren aurpegian zure estres-puntuazioa erakusten duen konplikazio biribil berria.",
      "Hiru hizkuntza berri: txekiera, greziera eta japoniera. Vela 12 hizkuntzatan dago orain.",
      "Konpondu dira jakinarazpen errepikatuak Velak irakurketa zaharrak berreskuratzean.",
      "Jakinarazpenak aplikaziotik desaktiba daitezke sistemaren baimena aktibatuta egon arren.",
      "Historialeko hilabete-ikuspegia orain eguneratu egiten da aplikazioa berriz irekitzean."]},
    {"version": "1.2.3", "date": "2026ko irailaren 6a", "status": "released", "changes": [
      "Aktibatu edo desaktibatu jakinarazpenak aplikaziotik sistemaren baimena jada emanda dagoenean."]},
    {"version": "1.2.2", "date": "2026ko abuztuaren 23a", "status": "released", "changes": [
      "Datek orain zure hizkuntza jarraitzen dute.",
      "Velak ingelesa erabiltzen du bateragarria ez den hizkuntza duten gailuetan."]},
    {"version": "1.2.1", "date": "2026ko abuztuaren 8a", "status": "released", "changes": [
      "Kendu da aplikazioa irekitzean berehala agertzen zen asteko analisiaren jakinarazpen bat.",
      "Oinarri-lerroa eraikitzeko eraztuna berriz agertzen da instalazio berrietan."]},
    {"version": "1.2.0", "date": "2026ko uztailaren 8a", "status": "released", "changes": [
      "Beste zazpi hizkuntza: katalana, euskara, galiziera, frantsesa, alemana, italiera eta portugesa.",
      "VoiceOver-en euskarri osoa pantaila guztietan.",
      "Dynamic Type, Gardentasuna murriztu, Bereizi kolorerik gabe eta eduki handituaren ikustailea.",
      "Testu-kontraste handiagoa WCAG AA betetzeko."]},
    {"version": "1.1.1", "date": "2026ko ekainaren 16a", "status": "released", "changes": [
      "Konpondu da asteko analisiaren jakinarazpena beti bidaltzen ez zena."]},
    {"version": "1.1.0", "date": "2026ko maiatzaren 26a", "status": "released", "changes": [
      "Asteko analisiak: Velak zure estresaren patroiak antzematen ditu eta hitz argiekin azaltzen dizkizu.",
      "Historial birdiseinatua egun, aste eta hilabeteko nabigazioarekin.",
      "HRV konplikazio berria barra-grafikoarekin erlojuaren esferarako.",
      "Gaueko irakurketak berreskuratzen dira, beraz historialak hutsune gutxiago ditu."]},
    {"version": "1.0.0", "date": "2026ko apirilaren 26a", "status": "released", "changes": [
      "Lehen bertsioa. Estres-puntuazioa HRVtik Apple Watch-en, zure oinarri-lerroa, joerak eta tarteen azalpen argia — konturik gabe, zerbitzaririk gabe, harpidetzarik gabe."]},
  ],
}

CHANGELOG["gl"] = {
  "title_tag": "Vela HRV — Rexistro de cambios", "title": "Rexistro de cambios",
  "intro": "Todas as versións de Vela e que cambiou en cada unha.",
  "status_review": "En revisión · App Store",
  "unreleased_note": "Esta versión está en revisión por Apple e aínda non se pode descargar.",
  "entries": [
    {"version": "1.3.1", "date": "15 de setembro de 2026", "status": "released", "changes": [
      "Corrixido un erro polo que actualizar desde unha versión anterior podía deixar a app sen os teus datos temporalmente ata que remataba de sincronizar."]},
    {"version": "1.3.0", "date": "14 de setembro de 2026", "status": "released", "changes": [
      "Nova complicación circular coa túa puntuación de estrés na esfera do reloxo.",
      "Tres idiomas novos: checo, grego e xaponés. Vela xa está en 12 idiomas.",
      "Corrixidas as notificacións repetidas cando Vela recupera lecturas antigas.",
      "As notificacións pódense desactivar dentro da app aínda que o permiso do sistema estea activado.",
      "A vista de mes no historial agora actualízase ao volver abrir a app."]},
    {"version": "1.2.3", "date": "6 de setembro de 2026", "status": "released", "changes": [
      "Activa ou desactiva as notificacións dentro da app cando o permiso do sistema xa está concedido."]},
    {"version": "1.2.2", "date": "23 de agosto de 2026", "status": "released", "changes": [
      "As datas agora seguen o teu idioma.",
      "Vela usa o inglés en dispositivos cun idioma non compatible."]},
    {"version": "1.2.1", "date": "8 de agosto de 2026", "status": "released", "changes": [
      "Eliminada unha notificación de análise semanal que aparecía xusto ao abrir a app.",
      "O anel de construción da liña base volve aparecer en instalacións novas."]},
    {"version": "1.2.0", "date": "8 de xullo de 2026", "status": "released", "changes": [
      "Sete idiomas máis: catalán, éuscaro, galego, francés, alemán, italiano e portugués.",
      "Compatibilidade completa con VoiceOver en todas as pantallas.",
      "Dynamic Type, Reducir a transparencia, Diferenciar sen cor e o visor de contido ampliado.",
      "Maior contraste de texto para cumprir WCAG AA."]},
    {"version": "1.1.1", "date": "16 de xuño de 2026", "status": "released", "changes": [
      "Corrixido o envío pouco fiable da notificación de análise semanal."]},
    {"version": "1.1.0", "date": "26 de maio de 2026", "status": "released", "changes": [
      "Análises semanais: Vela detecta patróns no teu estrés e explícachos con palabras claras.",
      "Historial redeseñado con navegación por día, semana e mes.",
      "Nova complicación de HRV con gráfico de barras para a esfera do reloxo.",
      "Recupéranse as lecturas nocturnas, así o historial ten menos ocos."]},
    {"version": "1.0.0", "date": "26 de abril de 2026", "status": "released", "changes": [
      "Primeira versión. Puntuación de estrés a partir do HRV no Apple Watch, a túa propia liña base, tendencias e explicación clara dos rangos — sen conta, sen servidores, sen subscrición."]},
  ],
}

CHANGELOG["fr"] = {
  "title_tag": "Vela HRV — Journal des modifications", "title": "Journal des modifications",
  "intro": "Toutes les versions de Vela et ce qui a changé dans chacune.",
  "status_review": "En cours d'examen · App Store",
  "unreleased_note": "Cette version est en cours d'examen par Apple et ne peut pas encore être téléchargée.",
  "entries": [
    {"version": "1.3.1", "date": "15 septembre 2026", "status": "released", "changes": [
      "Correction d'un bug où la mise à jour depuis une version antérieure pouvait temporairement priver l'app de vos données jusqu'à la fin de la resynchronisation."]},
    {"version": "1.3.0", "date": "14 septembre 2026", "status": "released", "changes": [
      "Nouvelle complication circulaire affichant votre score de stress sur le cadran de la montre.",
      "Trois nouvelles langues : tchèque, grec et japonais. Vela parle désormais 12 langues.",
      "Correction des notifications répétées quand Vela rattrape d'anciennes mesures.",
      "Les notifications peuvent être désactivées dans l'app même si l'autorisation système est active.",
      "La vue par mois de l'historique se rafraîchit désormais à la réouverture de l'app."]},
    {"version": "1.2.3", "date": "6 septembre 2026", "status": "released", "changes": [
      "Activez ou désactivez les notifications dans l'app quand l'autorisation système est déjà accordée."]},
    {"version": "1.2.2", "date": "23 août 2026", "status": "released", "changes": [
      "Les dates suivent désormais votre langue.",
      "Vela bascule en anglais sur les appareils réglés sur une langue non prise en charge."]},
    {"version": "1.2.1", "date": "8 août 2026", "status": "released", "changes": [
      "Suppression d'une notification d'analyse hebdomadaire qui apparaissait juste après l'ouverture de l'app.",
      "L'anneau de construction de la référence réapparaît sur les nouvelles installations."]},
    {"version": "1.2.0", "date": "8 juillet 2026", "status": "released", "changes": [
      "Sept langues de plus : catalan, basque, galicien, français, allemand, italien et portugais.",
      "Prise en charge complète de VoiceOver sur tous les écrans.",
      "Dynamic Type, Réduire la transparence, Différencier sans couleur et le visualiseur de contenu agrandi.",
      "Contraste du texte renforcé pour respecter WCAG AA."]},
    {"version": "1.1.1", "date": "16 juin 2026", "status": "released", "changes": [
      "Correction de la notification d'analyse hebdomadaire qui n'était pas toujours envoyée."]},
    {"version": "1.1.0", "date": "26 mai 2026", "status": "released", "changes": [
      "Analyses hebdomadaires : Vela repère des tendances dans votre stress et les explique simplement.",
      "Historique repensé avec navigation par jour, semaine et mois.",
      "Nouvelle complication VFC avec un graphique à barres pour votre cadran.",
      "Les mesures nocturnes sont récupérées, l'historique a donc moins de trous."]},
    {"version": "1.0.0", "date": "26 avril 2026", "status": "released", "changes": [
      "Première version. Score de stress à partir de la VFC sur Apple Watch, votre propre référence, tendances et explication claire des plages — sans compte, sans serveurs, sans abonnement."]},
  ],
}

CHANGELOG["de"] = {
  "title_tag": "Vela HRV — Änderungsprotokoll", "title": "Änderungsprotokoll",
  "intro": "Alle Versionen von Vela und was sich jeweils geändert hat.",
  "status_review": "In Prüfung · App Store",
  "unreleased_note": "Diese Version wird gerade von Apple geprüft und kann noch nicht geladen werden.",
  "entries": [
    {"version": "1.3.1", "date": "15. September 2026", "status": "released", "changes": [
      "Ein Fehler behoben, durch den ein Update von einer älteren Version die App vorübergehend ohne deine Daten zeigen konnte, bis die Synchronisierung abgeschlossen war."]},
    {"version": "1.3.0", "date": "14. September 2026", "status": "released", "changes": [
      "Neue runde Komplikation mit deinem Stresswert auf dem Zifferblatt.",
      "Drei neue Sprachen: Tschechisch, Griechisch und Japanisch. Vela spricht jetzt 12 Sprachen.",
      "Wiederholte Benachrichtigungen behoben, wenn Vela ältere Messwerte nachholt.",
      "Benachrichtigungen lassen sich in der App abschalten, auch wenn die Systemberechtigung aktiv ist.",
      "Die Monatsansicht im Verlauf aktualisiert sich jetzt beim erneuten Öffnen der App."]},
    {"version": "1.2.3", "date": "6. September 2026", "status": "released", "changes": [
      "Benachrichtigungen in der App ein- oder ausschalten, wenn die Systemberechtigung bereits erteilt ist."]},
    {"version": "1.2.2", "date": "23. August 2026", "status": "released", "changes": [
      "Datumsangaben folgen jetzt deiner Sprache.",
      "Vela wechselt zu Englisch auf Geräten mit nicht unterstützter Sprache."]},
    {"version": "1.2.1", "date": "8. August 2026", "status": "released", "changes": [
      "Eine Benachrichtigung zur Wochenanalyse entfernt, die direkt nach dem Öffnen der App erschien.",
      "Der Ring zum Aufbau der Baseline erscheint wieder bei Neuinstallationen."]},
    {"version": "1.2.0", "date": "8. Juli 2026", "status": "released", "changes": [
      "Sieben weitere Sprachen: Katalanisch, Baskisch, Galicisch, Französisch, Deutsch, Italienisch und Portugiesisch.",
      "Vollständige VoiceOver-Unterstützung auf jedem Bildschirm.",
      "Dynamic Type, Transparenz reduzieren, Ohne Farben differenzieren und die vergrößerte Inhaltsanzeige.",
      "Höherer Textkontrast zur Erfüllung von WCAG AA."]},
    {"version": "1.1.1", "date": "16. Juni 2026", "status": "released", "changes": [
      "Behoben, dass die Benachrichtigung zur Wochenanalyse nicht immer zugestellt wurde."]},
    {"version": "1.1.0", "date": "26. Mai 2026", "status": "released", "changes": [
      "Wochenanalysen: Vela erkennt Muster in deinem Stress und erklärt sie in klaren Worten.",
      "Neu gestalteter Verlauf mit Aufschlüsselung nach Tag, Woche und Monat.",
      "Neue HRV-Komplikation mit Balkendiagramm für dein Zifferblatt.",
      "Nächtliche Messwerte werden nachgetragen, dein Verlauf hat weniger Lücken."]},
    {"version": "1.0.0", "date": "26. April 2026", "status": "released", "changes": [
      "Erste Version. Stress-Score aus der HRV auf der Apple Watch, deine eigene Baseline, Trends und klare Erklärung der Bereiche — kein Account, keine Server, kein Abo."]},
  ],
}

CHANGELOG["it"] = {
  "title_tag": "Vela HRV — Registro delle modifiche", "title": "Registro delle modifiche",
  "intro": "Tutte le versioni di Vela e cosa è cambiato in ognuna.",
  "status_review": "In revisione · App Store",
  "unreleased_note": "Questa versione è in revisione da parte di Apple e non è ancora scaricabile.",
  "entries": [
    {"version": "1.3.1", "date": "15 settembre 2026", "status": "released", "changes": [
      "Corretto un bug per cui l'aggiornamento da una versione precedente poteva lasciare temporaneamente l'app senza i tuoi dati fino al termine della risincronizzazione."]},
    {"version": "1.3.0", "date": "14 settembre 2026", "status": "released", "changes": [
      "Nuova complicazione circolare con il tuo punteggio di stress sul quadrante.",
      "Tre nuove lingue: ceco, greco e giapponese. Vela ora parla 12 lingue.",
      "Corrette le notifiche ripetute quando Vela recupera letture più vecchie.",
      "Le notifiche si possono disattivare dall'app anche se il permesso di sistema è attivo.",
      "La vista per mese nello storico ora si aggiorna riaprendo l'app."]},
    {"version": "1.2.3", "date": "6 settembre 2026", "status": "released", "changes": [
      "Attiva o disattiva le notifiche dall'app quando il permesso di sistema è già concesso."]},
    {"version": "1.2.2", "date": "23 agosto 2026", "status": "released", "changes": [
      "Le date ora seguono la tua lingua.",
      "Vela passa all'inglese sui dispositivi impostati su una lingua non supportata."]},
    {"version": "1.2.1", "date": "8 agosto 2026", "status": "released", "changes": [
      "Rimossa una notifica di analisi settimanale che compariva subito dopo l'apertura dell'app.",
      "L'anello di costruzione della baseline ricompare sulle nuove installazioni."]},
    {"version": "1.2.0", "date": "8 luglio 2026", "status": "released", "changes": [
      "Altre sette lingue: catalano, basco, galiziano, francese, tedesco, italiano e portoghese.",
      "Supporto completo di VoiceOver in ogni schermata.",
      "Dynamic Type, Riduci trasparenza, Differenzia senza colore e il visualizzatore di contenuti ingranditi.",
      "Maggiore contrasto del testo per soddisfare WCAG AA."]},
    {"version": "1.1.1", "date": "16 giugno 2026", "status": "released", "changes": [
      "Corretta la notifica di analisi settimanale che non veniva sempre recapitata."]},
    {"version": "1.1.0", "date": "26 maggio 2026", "status": "released", "changes": [
      "Analisi settimanali: Vela individua schemi nel tuo stress e li spiega con parole semplici.",
      "Storico ridisegnato con navigazione per giorno, settimana e mese.",
      "Nuova complication HRV con grafico a barre per il quadrante.",
      "Le letture notturne vengono recuperate, così lo storico ha meno vuoti."]},
    {"version": "1.0.0", "date": "26 aprile 2026", "status": "released", "changes": [
      "Prima versione. Punteggio di stress dall'HRV su Apple Watch, la tua baseline, tendenze e spiegazione chiara degli intervalli — senza account, senza server, senza abbonamento."]},
  ],
}

CHANGELOG["pt"] = {
  "title_tag": "Vela HRV — Registo de alterações", "title": "Registo de alterações",
  "intro": "Todas as versões da Vela e o que mudou em cada uma.",
  "status_review": "Em revisão · App Store",
  "unreleased_note": "Esta versão está em revisão pela Apple e ainda não pode ser transferida.",
  "entries": [
    {"version": "1.3.1", "date": "15 de setembro de 2026", "status": "released", "changes": [
      "Corrigido um erro em que atualizar a partir de uma versão anterior podia deixar a app temporariamente sem os teus dados até terminar de sincronizar."]},
    {"version": "1.3.0", "date": "14 de setembro de 2026", "status": "released", "changes": [
      "Nova complicação circular com a tua pontuação de stress no mostrador do relógio.",
      "Três novos idiomas: checo, grego e japonês. A Vela já está em 12 idiomas.",
      "Corrigidas as notificações repetidas quando a Vela recupera leituras antigas.",
      "As notificações podem ser desativadas dentro da app mesmo com a permissão do sistema ativa.",
      "A vista por mês no histórico passa a atualizar ao reabrir a app."]},
    {"version": "1.2.3", "date": "6 de setembro de 2026", "status": "released", "changes": [
      "Ative ou desative as notificações dentro da app quando a permissão do sistema já está concedida."]},
    {"version": "1.2.2", "date": "23 de agosto de 2026", "status": "released", "changes": [
      "As datas passam a seguir o teu idioma.",
      "A Vela recorre ao inglês em dispositivos com um idioma não suportado."]},
    {"version": "1.2.1", "date": "8 de agosto de 2026", "status": "released", "changes": [
      "Removida uma notificação de análise semanal que surgia logo ao abrir a app.",
      "O anel de construção da linha de base volta a aparecer em instalações novas."]},
    {"version": "1.2.0", "date": "8 de julho de 2026", "status": "released", "changes": [
      "Mais sete idiomas: catalão, basco, galego, francês, alemão, italiano e português.",
      "Suporte completo de VoiceOver em todos os ecrãs.",
      "Dynamic Type, Reduzir transparência, Diferenciar sem cor e o visualizador de conteúdo ampliado.",
      "Maior contraste de texto para cumprir WCAG AA."]},
    {"version": "1.1.1", "date": "16 de junho de 2026", "status": "released", "changes": [
      "Corrigido o envio pouco fiável da notificação de análise semanal."]},
    {"version": "1.1.0", "date": "26 de maio de 2026", "status": "released", "changes": [
      "Análises semanais: a Vela deteta padrões no teu stress e explica-os por palavras simples.",
      "Histórico redesenhado com navegação por dia, semana e mês.",
      "Nova complicação de HRV com gráfico de barras para o mostrador.",
      "As leituras noturnas são recuperadas, por isso o histórico tem menos falhas."]},
    {"version": "1.0.0", "date": "26 de abril de 2026", "status": "released", "changes": [
      "Primeira versão. Pontuação de stress a partir do HRV no Apple Watch, a tua própria linha de base, tendências e explicação clara dos intervalos — sem conta, sem servidores, sem subscrição."]},
  ],
}

CHANGELOG["cs"] = {
  "title_tag": "Vela HRV — Seznam změn", "title": "Seznam změn",
  "intro": "Všechny verze Vely a co se v každé změnilo.",
  "status_review": "V kontrole · App Store",
  "unreleased_note": "Tato verze je v kontrole u Applu a zatím ji nelze stáhnout.",
  "entries": [
    {"version": "1.3.1", "date": "15. září 2026", "status": "released", "changes": [
      "Opravena chyba, kvůli které mohla aktualizace ze starší verze dočasně ponechat aplikaci bez tvých dat, dokud se znovu nesynchronizovala."]},
    {"version": "1.3.0", "date": "14. září 2026", "status": "released", "changes": [
      "Nová kruhová komplikace se skóre stresu na ciferníku hodinek.",
      "Tři nové jazyky: čeština, řečtina a japonština. Vela teď mluví 12 jazyky.",
      "Opraveny opakované notifikace, když Vela dohání starší měření.",
      "Notifikace lze vypnout přímo v aplikaci, i když je systémové oprávnění zapnuté.",
      "Měsíční přehled v historii se nyní obnoví po opětovném otevření aplikace."]},
    {"version": "1.2.3", "date": "6. září 2026", "status": "released", "changes": [
      "Zapněte nebo vypněte notifikace v aplikaci, když je systémové oprávnění už uděleno."]},
    {"version": "1.2.2", "date": "23. srpna 2026", "status": "released", "changes": [
      "Data se nyní řídí vaším jazykem.",
      "Vela se přepne do angličtiny na zařízeních s nepodporovaným jazykem."]},
    {"version": "1.2.1", "date": "8. srpna 2026", "status": "released", "changes": [
      "Odebrána notifikace týdenní analýzy, která se objevila hned po otevření aplikace.",
      "Prstenec budování základní linie se znovu zobrazuje u nových instalací."]},
    {"version": "1.2.0", "date": "8. července 2026", "status": "released", "changes": [
      "Dalších sedm jazyků: katalánština, baskičtina, galicijština, francouzština, němčina, italština a portugalština.",
      "Plná podpora VoiceOveru na každé obrazovce.",
      "Dynamic Type, Omezit průhlednost, Rozlišovat bez barvy a Prohlížeč velkého obsahu.",
      "Vyšší kontrast textu pro splnění WCAG AA."]},
    {"version": "1.1.1", "date": "16. června 2026", "status": "released", "changes": [
      "Opraveno nespolehlivé doručování notifikace týdenní analýzy."]},
    {"version": "1.1.0", "date": "26. května 2026", "status": "released", "changes": [
      "Týdenní přehledy: Vela odhalí vzorce ve vašem stresu a vysvětlí je srozumitelně.",
      "Přepracovaná historie s procházením po dnech, týdnech a měsících.",
      "Nová komplikace HRV se sloupcovým grafem pro ciferník.",
      "Noční měření se dopočítají, takže historie má méně mezer."]},
    {"version": "1.0.0", "date": "26. dubna 2026", "status": "released", "changes": [
      "První verze. Skóre stresu z HRV na Apple Watch, vaše vlastní základní linie, trendy a srozumitelné vysvětlení rozsahů — bez účtu, bez serverů, bez předplatného."]},
  ],
}

CHANGELOG["el"] = {
  "title_tag": "Vela HRV — Αρχείο αλλαγών", "title": "Αρχείο αλλαγών",
  "intro": "Όλες οι εκδόσεις του Vela και τι άλλαξε σε καθεμία.",
  "status_review": "Υπό έλεγχο · App Store",
  "unreleased_note": "Αυτή η έκδοση βρίσκεται υπό έλεγχο από την Apple και δεν είναι ακόμη διαθέσιμη για λήψη.",
  "entries": [
    {"version": "1.3.1", "date": "15 Σεπτεμβρίου 2026", "status": "released", "changes": [
      "Διορθώθηκε ένα σφάλμα όπου η ενημέρωση από παλαιότερη έκδοση μπορούσε να αφήσει προσωρινά την εφαρμογή χωρίς τα δεδομένα σας μέχρι να ολοκληρωθεί ο επανασυγχρονισμός."]},
    {"version": "1.3.0", "date": "14 Σεπτεμβρίου 2026", "status": "released", "changes": [
      "Νέα κυκλική επιπλοκή (complication) με τη βαθμολογία άγχους σας στο καντράν του ρολογιού.",
      "Τρεις νέες γλώσσες: τσέχικα, ελληνικά και ιαπωνικά. Το Vela μιλά πλέον 12 γλώσσες.",
      "Διορθώθηκαν οι επαναλαμβανόμενες ειδοποιήσεις όταν το Vela καλύπτει παλαιότερες μετρήσεις.",
      "Οι ειδοποιήσεις μπορούν να απενεργοποιηθούν μέσα στην εφαρμογή ακόμη κι αν η άδεια του συστήματος είναι ενεργή.",
      "Η προβολή μήνα στο ιστορικό ανανεώνεται πλέον όταν ανοίγετε ξανά την εφαρμογή."]},
    {"version": "1.2.3", "date": "6 Σεπτεμβρίου 2026", "status": "released", "changes": [
      "Ενεργοποιήστε ή απενεργοποιήστε τις ειδοποιήσεις μέσα στην εφαρμογή όταν η άδεια του συστήματος έχει ήδη δοθεί."]},
    {"version": "1.2.2", "date": "23 Αυγούστου 2026", "status": "released", "changes": [
      "Οι ημερομηνίες ακολουθούν πλέον τη γλώσσα σας.",
      "Το Vela επιστρέφει στα αγγλικά σε συσκευές με μη υποστηριζόμενη γλώσσα."]},
    {"version": "1.2.1", "date": "8 Αυγούστου 2026", "status": "released", "changes": [
      "Αφαιρέθηκε μια ειδοποίηση εβδομαδιαίας ανάλυσης που εμφανιζόταν αμέσως μετά το άνοιγμα της εφαρμογής.",
      "Ο δακτύλιος δημιουργίας baseline εμφανίζεται ξανά σε νέες εγκαταστάσεις."]},
    {"version": "1.2.0", "date": "8 Ιουλίου 2026", "status": "released", "changes": [
      "Άλλες επτά γλώσσες: καταλανικά, βασκικά, γαλικιανά, γαλλικά, γερμανικά, ιταλικά και πορτογαλικά.",
      "Πλήρης υποστήριξη VoiceOver σε κάθε οθόνη.",
      "Dynamic Type, Μείωση διαφάνειας, Διαφοροποίηση χωρίς χρώμα και πρόγραμμα προβολής μεγάλου περιεχομένου.",
      "Υψηλότερη αντίθεση κειμένου για συμμόρφωση με το WCAG AA."]},
    {"version": "1.1.1", "date": "16 Ιουνίου 2026", "status": "released", "changes": [
      "Διορθώθηκε η ειδοποίηση εβδομαδιαίας ανάλυσης που δεν παραδιδόταν πάντα."]},
    {"version": "1.1.0", "date": "26 Μαΐου 2026", "status": "released", "changes": [
      "Εβδομαδιαίες αναλύσεις: το Vela εντοπίζει μοτίβα στο άγχος σας και τα εξηγεί με απλά λόγια.",
      "Επανασχεδιασμένο ιστορικό με ανάλυση ανά ημέρα, εβδομάδα και μήνα.",
      "Νέο complication HRV με ραβδόγραμμα για το καντράν σας.",
      "Οι νυχτερινές μετρήσεις ανακτώνται, ώστε το ιστορικό να έχει λιγότερα κενά."]},
    {"version": "1.0.0", "date": "26 Απριλίου 2026", "status": "released", "changes": [
      "Πρώτη έκδοση. Σκορ άγχους από το HRV στο Apple Watch, το δικό σας baseline, τάσεις και σαφής εξήγηση των εύρων — χωρίς λογαριασμό, χωρίς διακομιστές, χωρίς συνδρομή."]},
  ],
}

CHANGELOG["ja"] = {
  "title_tag": "Vela HRV — 変更履歴", "title": "変更履歴",
  "intro": "Vela のすべてのバージョンと、それぞれの変更点。",
  "status_review": "審査中 · App Store",
  "unreleased_note": "このバージョンは現在 Apple の審査中で、まだダウンロードできません。",
  "entries": [
    {"version": "1.3.1", "date": "2026年9月15日", "status": "released", "changes": [
      "古いバージョンからのアップデート時に、再同期が終わるまで一時的にデータが表示されなくなる不具合を修正しました。"]},
    {"version": "1.3.0", "date": "2026年9月14日", "status": "released", "changes": [
      "文字盤に表示するストレススコアの新しい円形コンプリケーションを追加。",
      "3つの新しい言語（チェコ語、ギリシャ語、日本語）を追加。Vela は12言語に対応しました。",
      "過去の測定値を取り込む際に通知が繰り返される問題を修正。",
      "システムの許可がオンでも、アプリ内で通知をオフにできるようになりました。",
      "履歴の月表示が、アプリを開き直したときに更新されるようになりました。"]},
    {"version": "1.2.3", "date": "2026年9月6日", "status": "released", "changes": [
      "システムの許可がすでに与えられている場合に、アプリ内で通知のオン・オフを切り替えられます。"]},
    {"version": "1.2.2", "date": "2026年8月23日", "status": "released", "changes": [
      "日付が使用言語に合わせて表示されるようになりました。",
      "非対応の言語に設定されたデバイスでは、Vela は英語で表示されます。"]},
    {"version": "1.2.1", "date": "2026年8月8日", "status": "released", "changes": [
      "アプリを開いた直後に表示される週間分析の通知を削除。",
      "新規インストール時にベースライン構築リングが再び表示されるようになりました。"]},
    {"version": "1.2.0", "date": "2026年7月8日", "status": "released", "changes": [
      "さらに7言語を追加：カタルーニャ語、バスク語、ガリシア語、フランス語、ドイツ語、イタリア語、ポルトガル語。",
      "すべての画面で VoiceOver に完全対応。",
      "Dynamic Type、透明度を下げる、色を使わずに区別、拡大コンテンツビューアに対応。",
      "WCAG AA を満たすようテキストのコントラストを向上。"]},
    {"version": "1.1.1", "date": "2026年6月16日", "status": "released", "changes": [
      "週間分析の通知が常には届かない問題を修正。"]},
    {"version": "1.1.0", "date": "2026年5月26日", "status": "released", "changes": [
      "週間分析：Vela があなたのストレスのパターンを見つけ、分かりやすい言葉で説明します。",
      "履歴を刷新し、日・週・月で掘り下げられるように。",
      "文字盤用の棒グラフ付き HRV コンプリケーションを追加。",
      "夜間の測定値を補完し、履歴の欠けが少なくなりました。"]},
    {"version": "1.0.0", "date": "2026年4月26日", "status": "released", "changes": [
      "最初のリリース。Apple Watch 上で HRV からストレススコアを算出し、あなた自身のベースライン、トレンド、範囲の分かりやすい説明を提供します。アカウント不要、サーバーなし、サブスクなし。"]},
  ],
}

for _code, _cl in CHANGELOG.items():
    L[_code]["changelog"] = _cl
    L[_code]["landing"]["footer_changelog"] = _FOOTER_CHANGELOG[_code]

# ---------------------------------------------------------------- vela 2.0
# Vela 2.0 was released on 1 December 2026. Its changelog entry is "released" and the
# landing keeps a "New in 2.0" section right after the hero, pointing at the App Store,
# with the store's search banner for each language (eu and gl use the Spanish one: the
# store has no listing in those languages). The "beta" status, its badge and the
# TestFlight join note are no longer used by any entry but still work for a future beta.

TESTFLIGHT_URL = "https://testflight.apple.com/join/pJ3esgGy"
# Same banner as the App Store search asset, 2400x1600 JPEG. eu/gl fall back to es.
V2_IMAGE = {c: f"vela-2-battery-{'es' if c in ('eu', 'gl') else c}.jpg" for c in ORDER}

_V2 = {
  "en": {
    "date": "1 December 2026",
    "changes": [
      "Battery: an estimate of the energy you have left today, built on your own HRV baseline. Only sleep charges it, naps and daytime sleep after a night shift included.",
      "Free: your charge after each sleep, and what went into it: how long you slept and your HRV that night.",
      "Vela Pro, a one-time purchase with no subscription: the live battery, the day's curve, history, and what drained you most today.",
      "Three new complications: last night's charge for everyone, plus the live battery and today's hourly bars with Pro.",
      "Stress: on watches that record HRV often, the day's chart shows one bar per hour with its average and marks the peaks; your baseline gives every hour of the day the same weight; and the Health permission now explains each type of data Vela reads."],
    "status_beta": "Public beta · TestFlight",
    "beta_note": "This version is in public beta and not on the App Store yet. {link}Join the beta on TestFlight{end} to try it and help calibrate the battery.",
    "eyebrow": "New in Vela 2.0",
    "h2": "A battery for you, not for your watch.",
    "p": "Vela 2.0 adds Battery: it charges only while you sleep and drains with stress, activity, workouts and the hours you're awake, measured against your own HRV baseline. Each night's charge is free; Vela Pro, a one-time purchase, adds the day's curve, what drained your battery and the history.",
    "cta": "Download on the App Store",
    "zoom": "Tap the image to see it full size",
    "close": "Close",
    "alt": "Three Apple Watch Ultra running Vela: in the middle, the day's battery curve, at 44 now after charging to 80 overnight; on the sides, the stress level (34, low) and the battery level (44, medium).",
  },
  "es": {
    "date": "1 de diciembre de 2026",
    "changes": [
      "Batería: una estimación de la energía que te queda hoy, construida sobre tu propia línea base de HRV. Solo la carga el sueño, incluidas las siestas y el sueño de día tras un turno de noche.",
      "Gratis: tu carga después de cada sueño y de dónde sale: cuánto dormiste y tu HRV de esa noche.",
      "Vela Pro, compra única y sin suscripción: la batería en directo, la curva del día, el histórico y lo que más te ha gastado hoy.",
      "Tres complicaciones nuevas: la carga de la noche para todos, y con Pro la batería en directo y las barras por hora de hoy.",
      "Estrés: en los relojes que registran la HRV a menudo, el gráfico del día muestra una barra por hora con su media y marca los picos; tu línea base da el mismo peso a cada hora del día, y el permiso de Salud explica ahora cada tipo de dato que lee Vela."],
    "status_beta": "Beta pública · TestFlight",
    "beta_note": "Esta versión está en beta pública y todavía no está en la App Store. {link}Únete a la beta en TestFlight{end} para probarla y ayudar a calibrar la batería.",
    "eyebrow": "Nuevo en Vela 2.0",
    "h2": "Una batería para ti, no para tu reloj.",
    "p": "Vela 2.0 añade la Batería: se carga solo mientras duermes y se gasta con el estrés, la actividad, los entrenos y las horas despierto, medida contra tu propia línea base de HRV. La carga de cada noche es gratis; con Vela Pro, una compra única, ves la curva del día, en qué se ha ido la batería y el histórico.",
    "cta": "Descargar en el App Store",
    "zoom": "Toca la imagen para verla a tamaño completo",
    "close": "Cerrar",
    "alt": "Tres Apple Watch Ultra con Vela: en el centro, la curva de batería del día, a 44 ahora tras cargar hasta 80 por la noche; a los lados, el nivel de estrés (34, bajo) y la batería (44, media).",
  },
  "ca": {
    "date": "1 de desembre de 2026",
    "changes": [
      "Bateria: una estimació de l'energia que et queda avui, construïda sobre la teva pròpia línia base d'HRV. Només la carrega el son, incloses les migdiades i el son de dia després d'un torn de nit.",
      "Gratis: la teva càrrega després de cada son i d'on surt: quant vas dormir i la teva HRV d'aquella nit.",
      "Vela Pro, compra única i sense subscripció: la bateria en directe, la corba del dia, l'historial i el que més t'ha gastat avui.",
      "Tres complicacions noves: la càrrega de la nit per a tothom, i amb Pro la bateria en directe i les barres per hores d'avui.",
      "Estrès: als rellotges que registren l'HRV sovint, el gràfic del dia mostra una barra per hora amb la seva mitjana i marca els pics; la teva línia base dona el mateix pes a cada hora del dia, i el permís de Salut explica ara cada tipus de dada que llegeix Vela."],
    "status_beta": "Beta pública · TestFlight",
    "beta_note": "Aquesta versió és en beta pública i encara no és a l'App Store. {link}Uneix-te a la beta a TestFlight{end} per provar-la i ajudar a calibrar la bateria.",
    "eyebrow": "Novetat a Vela 2.0",
    "h2": "Una bateria per a tu, no per al teu rellotge.",
    "p": "Vela 2.0 afegeix la Bateria: es carrega només mentre dorms i es gasta amb l'estrès, l'activitat, els entrenaments i les hores despert, mesurada contra la teva pròpia línia base d'HRV. La càrrega de cada nit és gratuïta; amb Vela Pro, una compra única, veus la corba del dia, en què s'ha gastat la bateria i l'historial.",
    "cta": "Descarrega a l'App Store",
    "zoom": "Toca la imatge per veure-la a mida completa",
    "close": "Tanca",
    "alt": "Tres Apple Watch Ultra amb Vela: al centre, la corba de bateria del dia, a 44 ara després de carregar fins a 80 a la nit; als costats, el nivell d'estrès (34, baix) i el de bateria (44, mitjà).",
  },
  "eu": {
    "date": "2026ko abenduaren 1a",
    "changes": [
      "Bateria: gaur geratzen zaizun energiaren estimazioa, zure HRV oinarri-lerro pertsonalaren gainean eraikia. Loak bakarrik kargatzen du, siestak eta gaueko txandaren ondorengo eguneko loa barne.",
      "Doan: lo bakoitzaren ondorengo karga eta nondik datorren: zenbat lo egin zenuen eta gau horretako zure HRV.",
      "Vela Pro, behin ordaintzekoa eta harpidetzarik gabe: bateria zuzenean, eguneko kurba, historia eta gaur gehien gastatu dizuna.",
      "Hiru konplikazio berri: gaueko karga guztientzat, eta Pro-rekin bateria zuzenean eta gaurko orduko barrak.",
      "Estresa: HRV maiz erregistratzen duten erlojuetan, eguneko grafikoak barra bat erakusten du orduko, bere batezbestekoarekin, eta gailurrak markatzen ditu; zure oinarri-lerroak pisu bera ematen dio eguneko ordu bakoitzari, eta Osasuna baimenak orain azaltzen du Velak irakurtzen duen datu mota bakoitza."],
    "status_beta": "Beta publikoa · TestFlight",
    "beta_note": "Bertsio hau beta publikoan dago eta oraindik ez dago App Store-n. {link}Batu beta-ra TestFlight-en{end} probatzeko eta bateria kalibratzen laguntzeko.",
    "eyebrow": "Berria Vela 2.0n",
    "h2": "Zuretzako bateria bat, ez zure erlojuarentzat.",
    "p": "Vela 2.0k Bateria gehitzen du: lo zauden bitartean bakarrik kargatzen da, eta estresarekin, jarduerarekin, entrenamenduekin eta esna emandako orduekin husten da, zure HRV oinarri-lerroaren aurka neurtuta. Gau bakoitzeko karga doakoa da; Vela Pro-rekin, erosketa bakarra, eguneko kurba, bateria zertan joan den eta historia ikusten dituzu.",
    "cta": "Deskargatu App Store-n",
    "zoom": "Ukitu irudia tamaina osoan ikusteko",
    "close": "Itxi",
    "alt": "Hiru Apple Watch Ultra Velarekin: erdian, eguneko bateria-kurba, orain 44an, gauean 80ra kargatu ondoren; alboetan, estres-maila (34, baxua) eta bateria-maila (44, ertaina).",
  },
  "gl": {
    "date": "1 de decembro de 2026",
    "changes": [
      "Batería: unha estimación da enerxía que che queda hoxe, construída sobre a túa propia liña base de HRV. Só a carga o sono, incluídas as sestas e o sono de día despois dunha quenda de noite.",
      "De balde: a túa carga despois de cada sono e de onde sae: canto durmiches e a túa HRV desa noite.",
      "Vela Pro, compra única e sen subscrición: a batería en directo, a curva do día, o historial e o que máis che gastou hoxe.",
      "Tres complicacións novas: a carga da noite para todos, e con Pro a batería en directo e as barras por hora de hoxe.",
      "Estrés: nos reloxos que rexistran a HRV a miúdo, o gráfico do día mostra unha barra por hora coa súa media e marca os picos; a túa liña base dálle o mesmo peso a cada hora do día, e o permiso de Saúde explica agora cada tipo de dato que le Vela."],
    "status_beta": "Beta pública · TestFlight",
    "beta_note": "Esta versión está en beta pública e aínda non está na App Store. {link}Únete á beta en TestFlight{end} para probala e axudar a calibrar a batería.",
    "eyebrow": "Novo en Vela 2.0",
    "h2": "Unha batería para ti, non para o teu reloxo.",
    "p": "Vela 2.0 engade a Batería: cárgase só mentres dormes e gástase co estrés, a actividade, os adestramentos e as horas esperto, medida contra a túa propia liña base de HRV. A carga de cada noite é gratis; con Vela Pro, unha compra única, ves a curva do día, en que se foi a batería e o historial.",
    "cta": "Descargar na App Store",
    "zoom": "Toca a imaxe para vela a tamaño completo",
    "close": "Pechar",
    "alt": "Tres Apple Watch Ultra con Vela: no centro, a curva de batería do día, a 44 agora tras cargar ata 80 pola noite; aos lados, o nivel de estrés (34, baixo) e o de batería (44, medio).",
  },
  "fr": {
    "date": "1er décembre 2026",
    "changes": [
      "Batterie : une estimation de l'énergie qu'il vous reste aujourd'hui, calculée à partir de votre propre référence de VFC. Seul le sommeil la recharge, siestes et sommeil de jour après un poste de nuit compris.",
      "Gratuit : votre charge après chaque sommeil, et ce qui l'explique : combien de temps vous avez dormi et votre VFC cette nuit-là.",
      "Vela Pro, en achat unique et sans abonnement : la batterie en direct, la courbe de la journée, l'historique et ce qui vous a le plus fatigué aujourd'hui.",
      "Trois nouvelles complications : la charge de la nuit pour tous, et avec Pro la batterie en direct et les barres horaires du jour.",
      "Stress : sur les montres qui enregistrent souvent la VFC, le graphique du jour affiche une barre par heure avec sa moyenne et signale les pics ; votre référence donne le même poids à chaque heure de la journée, et l'autorisation Santé explique désormais chaque type de donnée que lit Vela."],
    "status_beta": "Bêta publique · TestFlight",
    "beta_note": "Cette version est en bêta publique et n'est pas encore sur l'App Store. {link}Rejoignez la bêta sur TestFlight{end} pour l'essayer et aider à calibrer la batterie.",
    "eyebrow": "Nouveau dans Vela 2.0",
    "h2": "Une batterie pour vous, pas pour votre montre.",
    "p": "Vela 2.0 ajoute la Batterie : elle se recharge uniquement pendant votre sommeil et se vide avec le stress, l'activité, les séances et les heures d'éveil, mesurée par rapport à votre propre référence VFC. La recharge de chaque nuit est gratuite ; avec Vela Pro, un achat unique, vous voyez la courbe de la journée, ce qui a vidé la batterie et l'historique.",
    "cta": "Télécharger dans l'App Store",
    "zoom": "Touchez l'image pour l'afficher en grand",
    "close": "Fermer",
    "alt": "Trois Apple Watch Ultra avec Vela : au centre, la courbe de batterie de la journée, à 44 maintenant après une recharge à 80 pendant la nuit ; sur les côtés, le niveau de stress (34, faible) et le niveau de batterie (44, moyen).",
  },
  "de": {
    "date": "1. Dezember 2026",
    "changes": [
      "Batterie: eine Schätzung, wie viel Energie dir heute noch bleibt, aufgebaut auf deiner eigenen HRV-Baseline. Nur Schlaf lädt sie auf, auch Nickerchen und Tagschlaf nach einer Nachtschicht.",
      "Kostenlos: deine Ladung nach jedem Schlaf und woraus sie sich ergibt: wie lange du geschlafen hast und deine HRV in dieser Nacht.",
      "Vela Pro, als Einmalkauf ohne Abo: die Live-Batterie, die Tageskurve, der Verlauf und was dich heute am meisten Energie gekostet hat.",
      "Drei neue Komplikationen: die Ladung der Nacht für alle, dazu mit Pro die Live-Batterie und die Stundenbalken von heute.",
      "Stress: Auf Uhren, die die HRV häufig messen, zeigt das Tagesdiagramm einen Balken pro Stunde mit ihrem Durchschnitt und markiert die Spitzen; deine Baseline gewichtet jede Stunde des Tages gleich, und die Health-Freigabe erklärt jetzt jede Datenart, die Vela liest."],
    "status_beta": "Öffentliche Beta · TestFlight",
    "beta_note": "Diese Version ist in der öffentlichen Beta und noch nicht im App Store. {link}Mach bei der Beta auf TestFlight mit{end}, um sie auszuprobieren und die Batterie mitzukalibrieren.",
    "eyebrow": "Neu in Vela 2.0",
    "h2": "Eine Batterie für dich, nicht für deine Uhr.",
    "p": "Vela 2.0 bringt die Batterie: Sie lädt sich nur im Schlaf auf und sinkt durch Stress, Aktivität, Trainings und die Stunden, in denen du wach bist, gemessen an deiner eigenen HRV-Baseline. Die Ladung jeder Nacht ist kostenlos; mit Vela Pro, einem Einmalkauf, siehst du die Tageskurve, was die Batterie verbraucht hat, und den Verlauf.",
    "cta": "Im App Store laden",
    "zoom": "Tippe auf das Bild, um es in voller Größe zu sehen",
    "close": "Schließen",
    "alt": "Drei Apple Watch Ultra mit Vela: in der Mitte die Batteriekurve des Tages, jetzt bei 44 nach einer Ladung auf 80 über Nacht; an den Seiten das Stresslevel (34, niedrig) und der Batteriestand (44, mittel).",
  },
  "it": {
    "date": "1 dicembre 2026",
    "changes": [
      "Batteria: una stima dell'energia che ti resta oggi, costruita sulla tua baseline di HRV. Solo il sonno la ricarica, compresi i pisolini e il sonno diurno dopo un turno di notte.",
      "Gratis: la tua carica dopo ogni sonno e da cosa dipende: quanto hai dormito e la tua HRV di quella notte.",
      "Vela Pro, acquisto unico e senza abbonamento: la batteria in tempo reale, la curva della giornata, lo storico e cosa ti ha consumato di più oggi.",
      "Tre nuove complicazioni: la carica della notte per tutti, e con Pro la batteria in tempo reale e le barre orarie di oggi.",
      "Stress: sugli orologi che registrano spesso l'HRV, il grafico del giorno mostra una barra per ora con la sua media e segna i picchi; la tua baseline dà lo stesso peso a ogni ora del giorno, e il permesso di Salute spiega ora ogni tipo di dato che Vela legge."],
    "status_beta": "Beta pubblica · TestFlight",
    "beta_note": "Questa versione è in beta pubblica e non è ancora sull'App Store. {link}Unisciti alla beta su TestFlight{end} per provarla e aiutare a calibrare la batteria.",
    "eyebrow": "Novità di Vela 2.0",
    "h2": "Una batteria per te, non per il tuo orologio.",
    "p": "Vela 2.0 aggiunge la Batteria: si ricarica solo mentre dormi e si consuma con lo stress, l'attività, gli allenamenti e le ore di veglia, misurata rispetto alla tua baseline HRV. La ricarica di ogni notte è gratis; con Vela Pro, un acquisto unico, vedi la curva della giornata, cosa ha consumato la batteria e lo storico.",
    "cta": "Scarica su App Store",
    "zoom": "Tocca l'immagine per vederla a grandezza intera",
    "close": "Chiudi",
    "alt": "Tre Apple Watch Ultra con Vela: al centro, la curva della batteria della giornata, ora a 44 dopo una ricarica fino a 80 durante la notte; ai lati, il livello di stress (34, basso) e il livello della batteria (44, medio).",
  },
  "pt": {
    "date": "1 de dezembro de 2026",
    "changes": [
      "Bateria: uma estimativa da energia que lhe resta hoje, construída sobre a sua própria linha de base de HRV. Só o sono a carrega, incluindo as sestas e o sono de dia depois de um turno da noite.",
      "Grátis: a sua carga depois de cada sono e de onde vem: quanto tempo dormiu e a sua HRV nessa noite.",
      "Vela Pro, compra única e sem subscrição: a bateria em direto, a curva do dia, o histórico e o que mais lhe gastou energia hoje.",
      "Três novas complicações: a carga da noite para todos e, com o Pro, a bateria em direto e as barras por hora de hoje.",
      "Stress: nos relógios que registam a HRV com frequência, o gráfico do dia mostra uma barra por hora com a sua média e assinala os picos; a sua linha de base dá o mesmo peso a cada hora do dia, e a permissão de Saúde explica agora cada tipo de dado que a Vela lê."],
    "status_beta": "Beta pública · TestFlight",
    "beta_note": "Esta versão está em beta pública e ainda não está na App Store. {link}Junte-se à beta no TestFlight{end} para a experimentar e ajudar a calibrar a bateria.",
    "eyebrow": "Novo na Vela 2.0",
    "h2": "Uma bateria para si, não para o seu relógio.",
    "p": "A Vela 2.0 acrescenta a Bateria: carrega só enquanto dorme e gasta-se com o stress, a atividade, os treinos e as horas acordado, medida contra a sua própria linha de base de HRV. A carga de cada noite é gratuita; com o Vela Pro, uma compra única, vê a curva do dia, o que gastou a bateria e o histórico.",
    "cta": "Descarregar na App Store",
    "zoom": "Toque na imagem para a ver em tamanho real",
    "close": "Fechar",
    "alt": "Três Apple Watch Ultra com a Vela: ao centro, a curva da bateria do dia, agora a 44 depois de carregar até 80 durante a noite; dos lados, o nível de stress (34, baixo) e o nível da bateria (44, médio).",
  },
  "cs": {
    "date": "1. prosince 2026",
    "changes": [
      "Baterie: odhad, kolik energie vám dnes zbývá, postavený na vaší vlastní základní linii HRV. Nabíjí ji jen spánek, včetně zdřímnutí a denního spánku po noční směně.",
      "Zdarma: vaše nabití po každém spánku a z čeho vychází: jak dlouho jste spali a vaše HRV té noci.",
      "Vela Pro, jednorázový nákup bez předplatného: baterie v reálném čase, křivka dne, historie a co vás dnes vyčerpalo nejvíc.",
      "Tři nové komplikace: noční nabití pro všechny, s Pro navíc baterie v reálném čase a dnešní hodinové sloupce.",
      "Stres: na hodinkách, které zaznamenávají HRV často, ukazuje graf dne jeden sloupec za hodinu s jejím průměrem a vyznačuje špičky; vaše základní linie dává každé hodině dne stejnou váhu a oprávnění pro Zdraví teď vysvětluje každý typ dat, který Vela čte."],
    "status_beta": "Veřejná beta · TestFlight",
    "beta_note": "Tato verze je ve veřejné betě a zatím není v App Storu. {link}Připojte se k betě v TestFlightu{end}, vyzkoušejte ji a pomozte kalibrovat baterii.",
    "eyebrow": "Novinka ve Vela 2.0",
    "h2": "Baterie pro vás, ne pro vaše hodinky.",
    "p": "Vela 2.0 přidává Baterii: nabíjí se jen ve spánku a vybíjí se stresem, aktivitou, tréninky a hodinami bdění, měřeno vůči vaší vlastní základní linii HRV. Nabití za každou noc je zdarma; s Vela Pro, jednorázovým nákupem, uvidíte křivku dne, co baterii vybilo, a historii.",
    "cta": "Stáhnout v App Store",
    "zoom": "Klepnutím na obrázek ho zobrazíte v plné velikosti",
    "close": "Zavřít",
    "alt": "Tři Apple Watch Ultra s Velou: uprostřed křivka baterie za den, teď na 44 po nočním nabití na 80; po stranách úroveň stresu (34, nízká) a stav baterie (44, střední).",
  },
  "el": {
    "date": "1 Δεκεμβρίου 2026",
    "changes": [
      "Μπαταρία: μια εκτίμηση της ενέργειας που σας απομένει σήμερα, με βάση το προσωπικό σας baseline HRV. Μόνο ο ύπνος τη φορτίζει, μαζί με τους υπνάκους και τον ημερήσιο ύπνο μετά από νυχτερινή βάρδια.",
      "Δωρεάν: η φόρτισή σας μετά από κάθε ύπνο και από τι προκύπτει: πόσο κοιμηθήκατε και το HRV σας εκείνη τη νύχτα.",
      "Vela Pro, εφάπαξ αγορά χωρίς συνδρομή: η μπαταρία σε πραγματικό χρόνο, η καμπύλη της ημέρας, το ιστορικό και τι σας κούρασε περισσότερο σήμερα.",
      "Τρεις νέες επιπλοκές (complications): η φόρτιση της νύχτας για όλους, και με το Pro η μπαταρία σε πραγματικό χρόνο και οι ωριαίες μπάρες της ημέρας.",
      "Στρες: στα ρολόγια που καταγράφουν συχνά το HRV, το γράφημα της ημέρας δείχνει μία μπάρα ανά ώρα με τον μέσο όρο της και σημειώνει τις κορυφές· το baseline σας δίνει το ίδιο βάρος σε κάθε ώρα της ημέρας, και η άδεια της Υγείας εξηγεί πλέον κάθε τύπο δεδομένων που διαβάζει το Vela."],
    "status_beta": "Δημόσια beta · TestFlight",
    "beta_note": "Αυτή η έκδοση βρίσκεται σε δημόσια beta και δεν είναι ακόμη στο App Store. {link}Μπείτε στη beta στο TestFlight{end} για να τη δοκιμάσετε και να βοηθήσετε στη βαθμονόμηση της μπαταρίας.",
    "eyebrow": "Νέο στο Vela 2.0",
    "h2": "Μια μπαταρία για εσάς, όχι για το ρολόι σας.",
    "p": "Το Vela 2.0 προσθέτει την Μπαταρία: φορτίζει μόνο όσο κοιμάστε και αδειάζει με το στρες, τη δραστηριότητα, τις προπονήσεις και τις ώρες που είστε ξύπνιοι, μετρημένη με βάση το δικό σας baseline HRV. Η φόρτιση κάθε νύχτας είναι δωρεάν· με το Vela Pro, μια εφάπαξ αγορά, βλέπετε την καμπύλη της ημέρας, τι άδειασε την μπαταρία και το ιστορικό.",
    "cta": "Λήψη από το App Store",
    "zoom": "Πατήστε την εικόνα για να τη δείτε σε πλήρες μέγεθος",
    "close": "Κλείσιμο",
    "alt": "Τρία Apple Watch Ultra με το Vela: στο κέντρο, η καμπύλη μπαταρίας της ημέρας, τώρα στο 44 μετά από φόρτιση έως το 80 τη νύχτα· στα πλάγια, το επίπεδο στρες (34, χαμηλό) και το επίπεδο μπαταρίας (44, μέτριο).",
  },
  "ja": {
    "date": "2026年12月1日",
    "changes": [
      "バッテリー：あなた自身の HRV ベースラインをもとに、今日残っているエネルギーを推定します。充電されるのは睡眠中だけで、昼寝や夜勤明けの日中の睡眠も含みます。",
      "無料：睡眠ごとの充電量と、その内訳（睡眠時間とその夜の HRV）を表示します。",
      "Vela Pro は買い切りで、サブスクリプションはありません。リアルタイムのバッテリー、1日のカーブ、履歴、今日いちばん消耗した原因を表示します。",
      "3つの新しいコンプリケーション：夜間の充電はすべての方に、リアルタイムのバッテリーと今日の時間別バーは Pro で。",
      "ストレス：HRV を頻繁に記録する Apple Watch では、1日のグラフが1時間ごとに平均の棒を表示し、ピークに印を付けます。ベースラインは1日のすべての時間を同じ重みで扱い、ヘルスケアのアクセス許可では Vela が読み取る各データの種類を説明するようになりました。"],
    "status_beta": "パブリックベータ · TestFlight",
    "beta_note": "このバージョンはパブリックベータ中で、まだ App Store では配信されていません。{link}TestFlight でベータに参加{end}して、バッテリーの調整にご協力ください。",
    "eyebrow": "Vela 2.0 の新機能",
    "h2": "時計のためではなく、あなたのためのバッテリー。",
    "p": "Vela 2.0 にはバッテリーが加わりました。充電されるのは眠っている間だけで、ストレス、活動量、ワークアウト、起きている時間で減っていきます。基準になるのは、あなた自身の HRV ベースラインです。毎晩の充電は無料、買い切りの Vela Pro では1日のカーブ、何がバッテリーを消費したか、履歴を確認できます。",
    "cta": "App Store でダウンロード",
    "zoom": "画像をタップすると拡大表示されます",
    "close": "閉じる",
    "alt": "Vela を表示した3台の Apple Watch Ultra：中央は1日のバッテリーカーブで、夜に80まで充電されて現在は44。左右はストレスレベル（34、低い）とバッテリー残量（44、中程度）。",
  },
}

_V2_LINK = f'<a href="{TESTFLIGHT_URL}" target="_blank" rel="noopener">'

for _code, _v in _V2.items():
    _cl = CHANGELOG[_code]
    _cl["status_beta"] = _v["status_beta"]
    _cl["beta_note"] = _v["beta_note"].format(link=_V2_LINK, end="</a>")
    _cl["entries"].insert(0, {"version": "2.0.0", "date": _v["date"], "status": "released", "changes": _v["changes"]})
    L[_code]["landing"]["v2"] = {k: _v[k] for k in ("eyebrow", "h2", "p", "cta", "alt", "zoom", "close")}

# Landing 2.0 (Battery, Stress, Pricing) for every language but Spanish, which lives inline in L["es"].
# "story" and "principles" replace one sentence / two cards of the 1.x copy; "baseline_extra" is appended.
_LANDING_2 = {
  "en": {
    "nav_battery": "Battery", "nav_stress": "Stress", "nav_pricing": "Pricing",
    "title_tag": "Vela — Stress and Battery for Apple Watch. No subscription. Ever.",
    "meta_desc": "Vela measures your stress and your Battery on Apple Watch against your own HRV baseline: how you are right now, how much sleep charged you and where your energy goes during the day. Everything is computed on the watch. No subscription, ever.",
    "eyebrow1": "Stress and Battery for Apple Watch",
    "h1": "Your energy and your calm aren't <em>anyone else's average</em>.",
    "hero_p": "Vela reads your heart rate variability (SDNN) on Apple Watch and compares it with your own baseline, not a population threshold. From that it tells you how much energy you have left today, your Battery, and how you are right now, your stress. All the computation happens on the watch. Nothing goes through our servers, because we don't have any.",
    "story": ("Stress isn't something to fight — it's something to read and adjust to.", "Stress and tiredness aren't something to fight: you read them and adjust course."),
    "baseline_extra": "And it works for both: your stress is measured against your usual HRV, and so is what a night charges you.",
    "p0_rest": "HealthKit provides the data, the watch does the rest. Neither your HRV, nor your sleep, nor your activity ever leaves your device toward a Vela server.",
    "p2": ("No tracking", "No analytics, no ads, no third-party SDKs.", "Vela doesn't know who you are or when you open the app: the only thing that leaves the watch goes to your own iCloud."),
    "battery_eyebrow": "Battery · New in Vela 2.0",
    "battery_p": "It charges only while you sleep, naps and daytime sleep after a night shift included, and drains with stress, activity, workouts and the hours you're awake. If a day has felt long, Battery shows you why.",
    "battery_tour": [
      ("Your charge", "How much the night charged you and where it came from: how long you slept and your HRV during sleep compared with your average.", "Vela screen with last night's charge: up to 80, 27 points gained asleep, 7 h 15 min of sleep and sleep HRV 9% above average."),
      ("The day's curve", "How it rose while you slept and how it drops from the moment you get up, with each workout marked at its time.", "The day's battery curve: green recharge overnight up to 80 and blue drain through the day down to 47, with two workouts marked."),
      ("Where it went", "What you've spent since you woke up, split into stress and activity, workouts and time awake. It describes what happened, without giving advice.", "Breakdown of today's spending: 33 points since waking up, 7 from stress and activity, 12 from an hour of workouts and 14 from time awake."),
    ],
    "tier_free": "Free", "tier_pro": "Pro",
    "stress_eyebrow": "Stress",
    "stress_p": "Your stress level right now, the day hour by hour and what each range means. Color and text label always go together, designed with color blindness in mind too. All of stress is free.",
    "pricing_eyebrow": "Pricing", "pricing_h2": "Free to start. Pro, just once.",
    "pricing_p": "No monthly or yearly fees. You pay for Vela Pro once and it's yours.",
    "free_sub": "For everyone",
    "free_items": ["Your stress level in real time, with its state and its explanation", "Today hour by hour and your stress history", "Weekly insights and high-stress alerts", "Each night's charge and where it came from", "Stress and night-charge complications"],
    "pro_sub": "One-time purchase",
    "pro_items": ["Live Battery, all through the day", "The day's curve, with the overnight recharge and every workout", "Where it went: stress and activity, workouts and time awake", "Battery history by month, week and day", "Complications with live Battery and today's hourly bars"],
  },
  "ca": {
    "nav_battery": "Bateria", "nav_stress": "Estrès", "nav_pricing": "Preu",
    "title_tag": "Vela — Estrès i Bateria per a l'Apple Watch. Sense subscripció. Mai.",
    "meta_desc": "Vela mesura el teu estrès i la teva Bateria a l'Apple Watch contra la teva pròpia línia base d'HRV: com estàs ara, quant t'ha carregat el son i en què se te'n va l'energia durant el dia. Tot es calcula al rellotge. Sense subscripció, mai.",
    "eyebrow1": "Estrès i Bateria per a l'Apple Watch",
    "h1": "La teva energia i la teva calma no són <em>la mitjana</em> de ningú.",
    "hero_p": "Vela llegeix la teva variabilitat del ritme cardíac (SDNN) a l'Apple Watch i la compara amb la teva pròpia línia base, no amb un llindar de població. Amb això et diu quanta energia et queda avui, la teva Bateria, i com estàs ara, el teu estrès. Tot el càlcul passa al rellotge. Res no passa pels nostres servidors, perquè no en tenim.",
    "story": ("L'estrès no es combat: es llegeix i s'ajusta.", "L'estrès i el cansament no es combaten: es llegeixen, i s'ajusta el rumb."),
    "baseline_extra": "I val per a les dues coses: el teu estrès es mesura contra la teva HRV de sempre, i el que et carrega una nit també.",
    "p0_rest": "HealthKit lliura les dades, el rellotge fa la resta. Ni la teva HRV, ni el teu son, ni la teva activitat surten del teu dispositiu cap a un servidor de Vela.",
    "p2": ("Sense rastreig", "Sense analítica, sense anuncis, sense SDK de tercers.", "Vela no sap qui ets ni quan obres l'app: l'únic que surt del rellotge va al teu propi iCloud."),
    "battery_eyebrow": "Bateria · Novetat a Vela 2.0",
    "battery_p": "Es carrega només mentre dorms, també amb una migdiada o amb el son de dia després d'un torn de nit, i es gasta amb l'estrès, l'activitat, els entrenaments i les hores despert. Si un dia se t'ha fet llarg, la Bateria t'ensenya per què.",
    "battery_tour": [
      ("La teva càrrega", "Quant t'ha carregat la nit i d'on surt: el que has dormit i la teva HRV durant el son davant de la teva mitjana.", "Pantalla de Vela amb la càrrega de la nit: fins a 80, 27 punts més dormint, 7 h 15 min de son i l'HRV del son un 9 % per sobre de la mitjana."),
      ("La corba del dia", "Com ha pujat mentre dormies i com baixa des que et lleves, amb cada entrenament marcat a la seva hora.", "Corba de bateria del dia: recàrrega en verd durant la nit fins a 80 i descàrrega en blau durant el dia fins a 47, amb dos entrenaments marcats."),
      ("En què s'ha gastat", "El que has gastat des que et vas despertar, separat en estrès i activitat, entrenaments i hores de vetlla. Descriu el que ha passat, sense donar-te consells.", "Desglossament de la despesa d'avui: 33 punts des que et vas despertar, 7 per estrès i activitat, 12 per una hora d'entrenament i 14 per les hores de vetlla."),
    ],
    "tier_free": "Gratis", "tier_pro": "Pro",
    "stress_eyebrow": "Estrès",
    "stress_p": "El teu nivell d'estrès d'ara, el dia hora a hora i què vol dir cada rang. El color i l'etiqueta de text sempre van junts, pensat també per a qui no distingeix bé els colors. Tot l'estrès és gratuït.",
    "pricing_eyebrow": "Preu", "pricing_h2": "Gratis per començar. Pro, una sola vegada.",
    "pricing_p": "Sense quotes mensuals ni anuals. Vela Pro es paga una vegada i és teu.",
    "free_sub": "Per a tothom",
    "free_items": ["El teu nivell d'estrès en temps real, amb el seu estat i la seva explicació", "El dia d'avui hora a hora i l'historial d'estrès", "Anàlisis setmanals i avisos d'estrès alt", "La càrrega de cada nit i d'on surt", "Complicacions d'estrès i de la càrrega de la nit"],
    "pro_sub": "Compra única",
    "pro_items": ["La Bateria en directe, al llarg del dia", "La corba del dia, amb la recàrrega de la nit i cada entrenament", "En què s'ha gastat: estrès i activitat, entrenaments i hores de vetlla", "Historial de bateria per mes, setmana i dia", "Complicacions amb la Bateria en directe i les barres per hores d'avui"],
  },
  "eu": {
    "nav_battery": "Bateria", "nav_stress": "Estresa", "nav_pricing": "Prezioa",
    "title_tag": "Vela — Estresa eta Bateria Apple Watch-erako. Harpidetzarik gabe. Inoiz ez.",
    "meta_desc": "Velak zure estresa eta zure Bateria neurtzen ditu Apple Watch-en, zure HRV oinarri-lerro propioaren aurka: nola zauden orain, loak zenbat kargatu zaituen eta egunean zehar zertan joaten zaizun energia. Dena erlojuan kalkulatzen da. Harpidetzarik gabe, inoiz ez.",
    "eyebrow1": "Estresa eta Bateria Apple Watch-erako",
    "h1": "Zure energia eta zure lasaitasuna ez dira <em>inoren batez bestekoa</em>.",
    "hero_p": "Velak zure bihotz-maiztasunaren aldakortasuna (SDNN) irakurtzen du Apple Watch-en eta zure oinarri-lerro propioarekin alderatzen du, ez populazio-atalase batekin. Horrekin esaten dizu gaur zenbat energia geratzen zaizun, zure Bateria, eta nola zauden orain, zure estresa. Kalkulu guztia erlojuan gertatzen da. Ezer ez da gure zerbitzarietatik pasatzen, ez baitugu halakorik.",
    "story": ("Estresa ez da borrokatzen: irakurri eta doitu egiten da.", "Estresa eta nekea ez dira borrokatzen: irakurri egiten dira, eta norabidea doitzen da."),
    "baseline_extra": "Eta bientzat balio du: zure estresa zure ohiko HRVaren aurka neurtzen da, eta gau batek kargatzen dizuna ere bai.",
    "p0_rest": "HealthKitek datuak ematen ditu, erlojuak gainerakoa egiten du. Ez zure HRVa, ez zure loa, ez zure jarduera ez dira inoiz zure gailutik ateratzen Velaren zerbitzari batera.",
    "p2": ("Jarraipenik gabe", "Analitikarik, iragarkirik eta hirugarrenen SDKrik gabe.", "Velak ez daki nor zaren ezta noiz irekitzen duzun aplikazioa ere: erlojutik ateratzen den gauza bakarra zure iCloud-era doa."),
    "battery_eyebrow": "Bateria · Berria Vela 2.0n",
    "battery_p": "Lo zauden bitartean bakarrik kargatzen da, siesta batekin edo gaueko txandaren ondorengo eguneko loarekin ere bai, eta estresarekin, jarduerarekin, entrenamenduekin eta esna emandako orduekin gastatzen da. Egun bat luze egin bazaizu, Bateriak zergatik erakusten dizu.",
    "battery_tour": [
      ("Zure karga", "Gauak zenbat kargatu zaituen eta nondik datorren: zenbat lo egin duzun eta loaldiko zure HRVa zure batez bestekoarekin alderatuta.", "Velaren pantaila gaueko kargarekin: 80ra arte, lotan 27 puntu gehiago, 7 h 15 min lo eta loaldiko HRVa batez bestekoa baino % 9 gorago."),
      ("Eguneko kurba", "Lo zeundela nola igo den eta jaikitzen zarenetik nola jaisten den, entrenamendu bakoitza bere orduan markatuta.", "Eguneko bateria-kurba: gauean berdez birkarga 80ra arte eta egunean zehar urdinez deskarga 47ra arte, bi entrenamendu markatuta."),
      ("Zertan joan den", "Esnatu zinenetik gastatutakoa, estresa eta jarduera, entrenamenduak eta esna emandako orduak bereizita. Gertatutakoa deskribatzen du, aholkurik eman gabe.", "Gaurko gastuaren xehapena: 33 puntu esnatu zinenetik, 7 estres eta jarduerarengatik, 12 entrenamendu-ordu batengatik eta 14 esna emandako orduengatik."),
    ],
    "tier_free": "Doan", "tier_pro": "Pro",
    "stress_eyebrow": "Estresa",
    "stress_p": "Zure oraingo estres-maila, eguna orduz ordu eta tarte bakoitzak zer esan nahi duen. Kolorea eta testu-etiketa beti batera doaz, kolore-itsutasuna kontuan hartuta ere. Estres guztia doakoa da.",
    "pricing_eyebrow": "Prezioa", "pricing_h2": "Doan hasteko. Pro, behin bakarrik.",
    "pricing_p": "Hileroko edo urteroko kuotarik gabe. Vela Pro behin ordaintzen da eta zurea da.",
    "free_sub": "Guztientzat",
    "free_items": ["Zure estres-maila denbora errealean, bere egoera eta azalpenarekin", "Gaurko eguna orduz ordu eta estresaren historia", "Asteko analisiak eta estres altuko abisuak", "Gau bakoitzeko karga eta nondik datorren", "Estresaren eta gaueko kargaren konplikazioak"],
    "pro_sub": "Erosketa bakarra",
    "pro_items": ["Bateria zuzenean, egun osoan zehar", "Eguneko kurba, gaueko birkargarekin eta entrenamendu bakoitzarekin", "Zertan joan den: estresa eta jarduera, entrenamenduak eta esna emandako orduak", "Bateriaren historia hilabete, aste eta egunaka", "Konplikazioak Bateria zuzenean eta gaurko orduko barrekin"],
  },
  "gl": {
    "nav_battery": "Batería", "nav_stress": "Estrés", "nav_pricing": "Prezo",
    "title_tag": "Vela — Estrés e Batería para Apple Watch. Sen subscrición. Nunca.",
    "meta_desc": "Vela mide o teu estrés e a túa Batería no Apple Watch contra a túa propia liña base de HRV: como estás agora, canto te cargou o sono e en que se che vai a enerxía durante o día. Todo se calcula no reloxo. Sen subscrición, nunca.",
    "eyebrow1": "Estrés e Batería para Apple Watch",
    "h1": "A túa enerxía e a túa calma non son <em>a media</em> de ninguén.",
    "hero_p": "Vela le a túa variabilidade do ritmo cardíaco (SDNN) no Apple Watch e compáraa coa túa propia liña base, non cun limiar de poboación. Con iso dicche canta enerxía che queda hoxe, a túa Batería, e como estás agora, o teu estrés. Todo o cálculo ocorre no reloxo. Nada pasa polos nosos servidores, porque non os temos.",
    "story": ("O estrés non se combate: lese e axústase.", "O estrés e o cansazo non se combaten: lense, e axústase o rumbo."),
    "baseline_extra": "E vale para as dúas cousas: o teu estrés mídese contra a túa HRV de sempre, e o que te carga unha noite tamén.",
    "p0_rest": "HealthKit entrega os datos, o reloxo fai o resto. Nin a túa HRV, nin o teu sono, nin a túa actividade saen do teu dispositivo cara a un servidor de Vela.",
    "p2": ("Sen rastrexo", "Sen analítica, sen anuncios, sen SDK de terceiros.", "Vela non sabe quen es nin cando abres a app: o único que sae do reloxo vai ao teu propio iCloud."),
    "battery_eyebrow": "Batería · Novo en Vela 2.0",
    "battery_p": "Cárgase só mentres dormes, tamén cunha sesta ou co sono de día despois dunha quenda de noite, e gástase co estrés, a actividade, os adestramentos e as horas esperto. Se un día se che fixo longo, a Batería ensínache por que.",
    "battery_tour": [
      ("A túa carga", "Canto te cargou a noite e de onde sae: o que durmiches e a túa HRV durante o sono fronte á túa media.", "Pantalla de Vela coa carga da noite: ata 80, 27 puntos máis durmindo, 7 h 15 min de sono e a HRV do sono un 9 % por riba da media."),
      ("A curva do día", "Como subiu mentres durmías e como baixa desde que te levantas, con cada adestramento marcado á súa hora.", "Curva de batería do día: recarga en verde durante a noite ata 80 e descarga en azul durante o día ata 47, con dous adestramentos marcados."),
      ("En que se foi", "O gastado desde que espertaches, separado en estrés e actividade, adestramentos e horas de vixilia. Describe o que pasou, sen darche consellos.", "Desglose do gasto de hoxe: 33 puntos desde que espertaches, 7 por estrés e actividade, 12 por unha hora de adestramento e 14 polas horas de vixilia."),
    ],
    "tier_free": "De balde", "tier_pro": "Pro",
    "stress_eyebrow": "Estrés",
    "stress_p": "O teu nivel de estrés de agora, o día hora a hora e que significa cada rango. A cor e a etiqueta de texto van sempre xuntas, pensado tamén para quen non distingue ben as cores. Todo o estrés é de balde.",
    "pricing_eyebrow": "Prezo", "pricing_h2": "De balde para empezar. Pro, unha soa vez.",
    "pricing_p": "Sen cotas mensuais nin anuais. Vela Pro págase unha vez e é teu.",
    "free_sub": "Para todos",
    "free_items": ["O teu nivel de estrés en tempo real, co seu estado e a súa explicación", "O día de hoxe hora a hora e o historial de estrés", "Análises semanais e avisos de estrés alto", "A carga de cada noite e de onde sae", "Complicacións de estrés e da carga da noite"],
    "pro_sub": "Compra única",
    "pro_items": ["A Batería en directo, ao longo do día", "A curva do día, coa recarga da noite e cada adestramento", "En que se foi: estrés e actividade, adestramentos e horas de vixilia", "Historial de batería por mes, semana e día", "Complicacións coa Batería en directo e as barras por hora de hoxe"],
  },
  "fr": {
    "nav_battery": "Batterie", "nav_stress": "Stress", "nav_pricing": "Prix",
    "title_tag": "Vela — Stress et Batterie pour Apple Watch. Sans abonnement. Jamais.",
    "meta_desc": "Vela mesure votre stress et votre Batterie sur Apple Watch par rapport à votre propre référence de VFC : comment vous allez maintenant, combien le sommeil vous a rechargé et où part votre énergie pendant la journée. Tout est calculé sur la montre. Sans abonnement, jamais.",
    "eyebrow1": "Stress et Batterie pour Apple Watch",
    "h1": "Votre énergie et votre calme ne sont <em>la moyenne</em> de personne.",
    "hero_p": "Vela lit votre variabilité de la fréquence cardiaque (SDNN) sur l'Apple Watch et la compare à votre propre référence, pas à un seuil de population. Elle vous dit ainsi combien d'énergie il vous reste aujourd'hui, votre Batterie, et comment vous allez maintenant, votre stress. Tout le calcul se fait sur la montre. Rien ne passe par nos serveurs, parce que nous n'en avons pas.",
    "story": ("Le stress ne se combat pas : il se lit et s'ajuste.", "Le stress et la fatigue ne se combattent pas : ils se lisent, et on ajuste le cap."),
    "baseline_extra": "Et cela vaut pour les deux : votre stress se mesure par rapport à votre VFC habituelle, et ce qu'une nuit vous recharge aussi.",
    "p0_rest": "HealthKit fournit les données, la montre fait le reste. Ni votre VFC, ni votre sommeil, ni votre activité ne quittent votre appareil vers un serveur Vela.",
    "p2": ("Sans pistage", "Pas d'analytique, pas de publicité, pas de SDK tiers.", "Vela ne sait pas qui vous êtes ni quand vous ouvrez l'app : la seule chose qui quitte la montre va dans votre propre iCloud."),
    "battery_eyebrow": "Batterie · Nouveau dans Vela 2.0",
    "battery_p": "Elle se recharge uniquement pendant votre sommeil, siestes et sommeil de jour après un poste de nuit compris, et se vide avec le stress, l'activité, les séances et les heures d'éveil. Si une journée vous a paru longue, la Batterie vous montre pourquoi.",
    "battery_tour": [
      ("Votre recharge", "Combien la nuit vous a rechargé et d'où ça vient : combien de temps vous avez dormi et votre VFC pendant le sommeil par rapport à votre moyenne.", "Écran de Vela avec la recharge de la nuit : jusqu'à 80, 27 points gagnés en dormant, 7 h 15 min de sommeil et une VFC pendant le sommeil 9 % au-dessus de la moyenne."),
      ("La courbe de la journée", "Comment elle est montée pendant votre sommeil et comment elle baisse depuis votre lever, avec chaque séance marquée à son heure.", "Courbe de batterie de la journée : recharge en vert pendant la nuit jusqu'à 80, décharge en bleu pendant la journée jusqu'à 47, avec deux séances marquées."),
      ("Où elle est passée", "Ce que vous avez dépensé depuis votre réveil, réparti entre stress et activité, séances et heures d'éveil. Elle décrit ce qui s'est passé, sans vous donner de conseils.", "Détail de la dépense du jour : 33 points depuis le réveil, 7 pour le stress et l'activité, 12 pour une heure de séance et 14 pour les heures d'éveil."),
    ],
    "tier_free": "Gratuit", "tier_pro": "Pro",
    "stress_eyebrow": "Stress",
    "stress_p": "Votre niveau de stress maintenant, la journée heure par heure et ce que signifie chaque plage. La couleur et l'étiquette textuelle vont toujours ensemble, pensé aussi pour les personnes daltoniennes. Tout le stress est gratuit.",
    "pricing_eyebrow": "Prix", "pricing_h2": "Gratuit pour commencer. Pro, une seule fois.",
    "pricing_p": "Aucun frais mensuel ni annuel. Vela Pro se paie une fois et il est à vous.",
    "free_sub": "Pour tous",
    "free_items": ["Votre niveau de stress en temps réel, avec son état et son explication", "La journée heure par heure et l'historique du stress", "Analyses hebdomadaires et alertes de stress élevé", "La recharge de chaque nuit et d'où elle vient", "Complications du stress et de la recharge de la nuit"],
    "pro_sub": "Achat unique",
    "pro_items": ["La Batterie en direct, tout au long de la journée", "La courbe de la journée, avec la recharge de la nuit et chaque séance", "Où elle est passée : stress et activité, séances et heures d'éveil", "Historique de la batterie par mois, semaine et jour", "Complications avec la Batterie en direct et les barres horaires du jour"],
  },
  "de": {
    "nav_battery": "Batterie", "nav_stress": "Stress", "nav_pricing": "Preis",
    "title_tag": "Vela — Stress und Batterie für die Apple Watch. Kein Abo. Niemals.",
    "meta_desc": "Vela misst deinen Stress und deine Batterie auf der Apple Watch an deiner eigenen HRV-Baseline: wie es dir gerade geht, wie viel dich der Schlaf aufgeladen hat und wofür deine Energie über den Tag draufgeht. Alles wird auf der Uhr berechnet. Kein Abo, niemals.",
    "eyebrow1": "Stress und Batterie für die Apple Watch",
    "h1": "Deine Energie und deine Ruhe sind <em>niemandes Durchschnitt</em>.",
    "hero_p": "Vela liest deine Herzfrequenzvariabilität (SDNN) auf der Apple Watch und vergleicht sie mit deiner eigenen Baseline, nicht mit einem Bevölkerungsschwellenwert. Daraus sagt sie dir, wie viel Energie dir heute bleibt, deine Batterie, und wie es dir gerade geht, dein Stress. Die gesamte Berechnung läuft auf der Uhr. Nichts läuft über unsere Server, denn wir haben keine.",
    "story": ("Stress wird nicht bekämpft, sondern gelesen und angepasst.", "Stress und Müdigkeit werden nicht bekämpft: Man liest sie und passt den Kurs an."),
    "baseline_extra": "Und das gilt für beides: Dein Stress wird an deiner gewohnten HRV gemessen, und das, was dich eine Nacht auflädt, auch.",
    "p0_rest": "HealthKit liefert die Daten, die Uhr erledigt den Rest. Weder deine HRV noch dein Schlaf noch deine Aktivität verlassen jemals dein Gerät in Richtung eines Vela-Servers.",
    "p2": ("Kein Tracking", "Keine Analytics, keine Werbung, keine Drittanbieter-SDKs.", "Vela weiß nicht, wer du bist oder wann du die App öffnest: Das Einzige, was die Uhr verlässt, geht in deine eigene iCloud."),
    "battery_eyebrow": "Batterie · Neu in Vela 2.0",
    "battery_p": "Sie lädt sich nur im Schlaf auf, auch bei einem Nickerchen oder beim Tagschlaf nach einer Nachtschicht, und sinkt durch Stress, Aktivität, Trainings und die Stunden, die du wach bist. Wenn sich ein Tag lang angefühlt hat, zeigt dir die Batterie, warum.",
    "battery_tour": [
      ("Deine Ladung", "Wie viel dich die Nacht aufgeladen hat und woher das kommt: wie lange du geschlafen hast und deine HRV im Schlaf im Vergleich zu deinem Durchschnitt.", "Vela-Bildschirm mit der Ladung der Nacht: bis 80, 27 Punkte im Schlaf dazu, 7 Std. 15 Min. Schlaf und eine HRV im Schlaf 9 % über dem Durchschnitt."),
      ("Die Tageskurve", "Wie sie im Schlaf gestiegen ist und wie sie seit dem Aufstehen sinkt, mit jedem Training zu seiner Uhrzeit markiert.", "Batteriekurve des Tages: grüne Aufladung in der Nacht bis 80 und blaue Entladung über den Tag bis 47, mit zwei markierten Trainings."),
      ("Wofür sie draufging", "Was du seit dem Aufwachen verbraucht hast, aufgeteilt in Stress und Aktivität, Trainings und Wachzeit. Sie beschreibt, was passiert ist, ohne dir Ratschläge zu geben.", "Aufschlüsselung des heutigen Verbrauchs: 33 Punkte seit dem Aufwachen, 7 durch Stress und Aktivität, 12 durch eine Stunde Training und 14 durch die Wachzeit."),
    ],
    "tier_free": "Kostenlos", "tier_pro": "Pro",
    "stress_eyebrow": "Stress",
    "stress_p": "Dein Stresslevel gerade jetzt, der Tag Stunde für Stunde und was jeder Bereich bedeutet. Farbe und Textlabel gehören immer zusammen, auch für Menschen mit Farbsehschwäche gedacht. Alles rund um Stress ist kostenlos.",
    "pricing_eyebrow": "Preis", "pricing_h2": "Kostenlos zum Start. Pro, nur einmal.",
    "pricing_p": "Keine monatlichen oder jährlichen Gebühren. Vela Pro zahlst du einmal, und es gehört dir.",
    "free_sub": "Für alle",
    "free_items": ["Dein Stresslevel in Echtzeit, mit Zustand und Erklärung", "Der heutige Tag Stunde für Stunde und dein Stressverlauf", "Wöchentliche Analysen und Hinweise bei hohem Stress", "Die Ladung jeder Nacht und woher sie kommt", "Komplikationen für Stress und die Ladung der Nacht"],
    "pro_sub": "Einmalkauf",
    "pro_items": ["Die Live-Batterie, den ganzen Tag über", "Die Tageskurve, mit der Aufladung der Nacht und jedem Training", "Wofür sie draufging: Stress und Aktivität, Trainings und Wachzeit", "Batterieverlauf nach Monat, Woche und Tag", "Komplikationen mit der Live-Batterie und den Stundenbalken von heute"],
  },
  "it": {
    "nav_battery": "Batteria", "nav_stress": "Stress", "nav_pricing": "Prezzo",
    "title_tag": "Vela — Stress e Batteria per Apple Watch. Senza abbonamento. Mai.",
    "meta_desc": "Vela misura il tuo stress e la tua Batteria su Apple Watch rispetto alla tua baseline HRV: come stai adesso, quanto ti ha ricaricato il sonno e dove se ne va la tua energia durante la giornata. Tutto viene calcolato sull'orologio. Senza abbonamento, mai.",
    "eyebrow1": "Stress e Batteria per Apple Watch",
    "h1": "La tua energia e la tua calma non sono <em>la media</em> di nessuno.",
    "hero_p": "Vela legge la tua variabilità della frequenza cardiaca (SDNN) su Apple Watch e la confronta con la tua baseline, non con una soglia di popolazione. Così ti dice quanta energia ti resta oggi, la tua Batteria, e come stai adesso, il tuo stress. Tutto il calcolo avviene sull'orologio. Niente passa dai nostri server, perché non ne abbiamo.",
    "story": ("Lo stress non si combatte: si legge e si regola.", "Lo stress e la stanchezza non si combattono: si leggono, e si regola la rotta."),
    "baseline_extra": "E vale per entrambi: il tuo stress si misura rispetto alla tua HRV abituale, e anche quanto ti ricarica una notte.",
    "p0_rest": "HealthKit fornisce i dati, l'orologio fa il resto. Né la tua HRV, né il tuo sonno, né la tua attività lasciano mai il tuo dispositivo verso un server Vela.",
    "p2": ("Nessun tracciamento", "Niente analytics, niente pubblicità, niente SDK di terze parti.", "Vela non sa chi sei né quando apri l'app: l'unica cosa che lascia l'orologio va nel tuo iCloud."),
    "battery_eyebrow": "Batteria · Novità di Vela 2.0",
    "battery_p": "Si ricarica solo mentre dormi, anche con un pisolino o con il sonno diurno dopo un turno di notte, e si consuma con lo stress, l'attività, gli allenamenti e le ore di veglia. Se una giornata ti è sembrata lunga, la Batteria ti mostra perché.",
    "battery_tour": [
      ("La tua ricarica", "Quanto ti ha ricaricato la notte e da cosa dipende: quanto hai dormito e la tua HRV durante il sonno rispetto alla tua media.", "Schermata di Vela con la ricarica della notte: fino a 80, 27 punti guadagnati dormendo, 7 h 15 min di sonno e HRV nel sonno del 9% sopra la media."),
      ("La curva della giornata", "Come è salita mentre dormivi e come scende da quando ti alzi, con ogni allenamento segnato alla sua ora.", "Curva della batteria della giornata: ricarica in verde durante la notte fino a 80 e scarica in blu durante il giorno fino a 47, con due allenamenti segnati."),
      ("Dove è andata", "Quanto hai consumato da quando ti sei svegliato, diviso tra stress e attività, allenamenti e ore di veglia. Descrive cosa è successo, senza darti consigli.", "Dettaglio del consumo di oggi: 33 punti dal risveglio, 7 per stress e attività, 12 per un'ora di allenamento e 14 per le ore di veglia."),
    ],
    "tier_free": "Gratis", "tier_pro": "Pro",
    "stress_eyebrow": "Stress",
    "stress_p": "Il tuo livello di stress adesso, la giornata ora per ora e cosa significa ogni intervallo. Colore ed etichetta testuale vanno sempre insieme, pensato anche per chi non distingue bene i colori. Tutto lo stress è gratis.",
    "pricing_eyebrow": "Prezzo", "pricing_h2": "Gratis per iniziare. Pro, una volta sola.",
    "pricing_p": "Nessuna quota mensile o annuale. Vela Pro si paga una volta ed è tuo.",
    "free_sub": "Per tutti",
    "free_items": ["Il tuo livello di stress in tempo reale, con il suo stato e la sua spiegazione", "La giornata ora per ora e lo storico dello stress", "Analisi settimanali e avvisi di stress alto", "La ricarica di ogni notte e da cosa dipende", "Complicazioni dello stress e della ricarica notturna"],
    "pro_sub": "Acquisto unico",
    "pro_items": ["La Batteria in tempo reale, per tutta la giornata", "La curva della giornata, con la ricarica notturna e ogni allenamento", "Dove è andata: stress e attività, allenamenti e ore di veglia", "Storico della batteria per mese, settimana e giorno", "Complicazioni con la Batteria in tempo reale e le barre orarie di oggi"],
  },
  "pt": {
    "nav_battery": "Bateria", "nav_stress": "Stress", "nav_pricing": "Preço",
    "title_tag": "Vela — Stress e Bateria para Apple Watch. Sem subscrição. Nunca.",
    "meta_desc": "A Vela mede o seu stress e a sua Bateria no Apple Watch contra a sua própria linha de base de HRV: como está agora, quanto o sono o carregou e onde se gasta a sua energia ao longo do dia. Tudo é calculado no relógio. Sem subscrição, nunca.",
    "eyebrow1": "Stress e Bateria para Apple Watch",
    "h1": "A sua energia e a sua calma não são <em>a média</em> de ninguém.",
    "hero_p": "A Vela lê a sua variabilidade da frequência cardíaca (SDNN) no Apple Watch e compara-a com a sua própria linha de base, não com um limiar de população. Com isso diz-lhe quanta energia lhe resta hoje, a sua Bateria, e como está agora, o seu stress. Todo o cálculo acontece no relógio. Nada passa pelos nossos servidores, porque não os temos.",
    "story": ("O stress não se combate: lê-se e ajusta-se.", "O stress e o cansaço não se combatem: leem-se, e ajusta-se o rumo."),
    "baseline_extra": "E vale para as duas coisas: o seu stress é medido contra a sua HRV habitual, e o que uma noite lhe carrega também.",
    "p0_rest": "O HealthKit fornece os dados, o relógio faz o resto. Nem a sua HRV, nem o seu sono, nem a sua atividade saem do seu dispositivo em direção a um servidor da Vela.",
    "p2": ("Sem rastreio", "Sem análises, sem anúncios, sem SDK de terceiros.", "A Vela não sabe quem é nem quando abre a app: a única coisa que sai do relógio vai para o seu próprio iCloud."),
    "battery_eyebrow": "Bateria · Novo na Vela 2.0",
    "battery_p": "Carrega só enquanto dorme, também com uma sesta ou com o sono de dia depois de um turno da noite, e gasta-se com o stress, a atividade, os treinos e as horas acordado. Se um dia lhe pareceu longo, a Bateria mostra-lhe porquê.",
    "battery_tour": [
      ("A sua carga", "Quanto a noite o carregou e de onde vem: quanto dormiu e a sua HRV durante o sono face à sua média.", "Ecrã da Vela com a carga da noite: até 80, mais 27 pontos a dormir, 7 h 15 min de sono e a HRV do sono 9% acima da média."),
      ("A curva do dia", "Como subiu enquanto dormia e como desce desde que se levanta, com cada treino marcado à sua hora.", "Curva da bateria do dia: recarga a verde durante a noite até 80 e descarga a azul durante o dia até 47, com dois treinos marcados."),
      ("Onde se gastou", "O que gastou desde que acordou, separado em stress e atividade, treinos e horas de vigília. Descreve o que aconteceu, sem lhe dar conselhos.", "Detalhe do gasto de hoje: 33 pontos desde que acordou, 7 por stress e atividade, 12 por uma hora de treino e 14 pelas horas de vigília."),
    ],
    "tier_free": "Grátis", "tier_pro": "Pro",
    "stress_eyebrow": "Stress",
    "stress_p": "O seu nível de stress agora, o dia hora a hora e o que significa cada intervalo. A cor e a etiqueta de texto andam sempre juntas, pensado também para quem não distingue bem as cores. Todo o stress é gratuito.",
    "pricing_eyebrow": "Preço", "pricing_h2": "Grátis para começar. Pro, uma só vez.",
    "pricing_p": "Sem quotas mensais nem anuais. O Vela Pro paga-se uma vez e é seu.",
    "free_sub": "Para todos",
    "free_items": ["O seu nível de stress em tempo real, com o seu estado e a sua explicação", "O dia de hoje hora a hora e o histórico de stress", "Análises semanais e avisos de stress alto", "A carga de cada noite e de onde vem", "Complicações de stress e da carga da noite"],
    "pro_sub": "Compra única",
    "pro_items": ["A Bateria em direto, ao longo do dia", "A curva do dia, com a recarga da noite e cada treino", "Onde se gastou: stress e atividade, treinos e horas de vigília", "Histórico da bateria por mês, semana e dia", "Complicações com a Bateria em direto e as barras por hora de hoje"],
  },
  "cs": {
    "nav_battery": "Baterie", "nav_stress": "Stres", "nav_pricing": "Cena",
    "title_tag": "Vela — Stres a Baterie pro Apple Watch. Žádné předplatné. Nikdy.",
    "meta_desc": "Vela měří váš stres a vaši Baterii na Apple Watch vůči vaší vlastní základní linii HRV: jak na tom jste právě teď, kolik vás nabil spánek a kam během dne mizí vaše energie. Vše se počítá v hodinkách. Žádné předplatné, nikdy.",
    "eyebrow1": "Stres a Baterie pro Apple Watch",
    "h1": "Vaše energie a váš klid nejsou <em>ničí průměr</em>.",
    "hero_p": "Vela čte variabilitu vaší srdeční frekvence (SDNN) na Apple Watch a porovnává ji s vaší vlastní základní linií, ne s populačním prahem. Z toho vám řekne, kolik energie vám dnes zbývá, vaši Baterii, a jak na tom jste právě teď, váš stres. Veškerý výpočet probíhá v hodinkách. Nic neprochází našimi servery, protože žádné nemáme.",
    "story": ("Se stresem se nebojuje — čte se a přizpůsobuje.", "Se stresem a únavou se nebojuje: čtou se a upravuje se kurz."),
    "baseline_extra": "A platí to pro obojí: váš stres se měří vůči vaší obvyklé HRV, a to, kolik vás nabije noc, také.",
    "p0_rest": "HealthKit poskytuje data, hodinky udělají zbytek. Vaše HRV, váš spánek ani vaše aktivita nikdy neopustí vaše zařízení směrem k serveru Vely.",
    "p2": ("Žádné sledování", "Žádná analytika, žádné reklamy, žádná SDK třetích stran.", "Vela neví, kdo jste, ani kdy aplikaci otevíráte: jediné, co opouští hodinky, jde do vašeho vlastního iCloudu."),
    "battery_eyebrow": "Baterie · Novinka ve Vela 2.0",
    "battery_p": "Nabíjí se jen ve spánku, včetně zdřímnutí a denního spánku po noční směně, a vybíjí se stresem, aktivitou, tréninky a hodinami v bdělém stavu. Pokud vám den připadal dlouhý, Baterie vám ukáže proč.",
    "battery_tour": [
      ("Vaše nabití", "Kolik vás nabila noc a z čeho to vychází: jak dlouho jste spali a vaše HRV ve spánku ve srovnání s vaším průměrem.", "Obrazovka Vely s nočním nabitím: na 80, o 27 bodů víc ve spánku, 7 h 15 min spánku a HRV ve spánku o 9 % nad průměrem."),
      ("Křivka dne", "Jak stoupala, zatímco jste spali, a jak klesá od chvíle, kdy vstanete, s každým tréninkem vyznačeným v jeho čase.", "Křivka baterie za den: zelené nabíjení v noci až na 80 a modré vybíjení během dne až na 47, se dvěma vyznačenými tréninky."),
      ("Kam se poděla", "Co jste spotřebovali od probuzení, rozdělené na stres a aktivitu, tréninky a čas v bdělém stavu. Popisuje, co se stalo, bez rad.", "Rozpis dnešní spotřeby: 33 bodů od probuzení, 7 za stres a aktivitu, 12 za hodinu tréninku a 14 za čas v bdělém stavu."),
    ],
    "tier_free": "Zdarma", "tier_pro": "Pro",
    "stress_eyebrow": "Stres",
    "stress_p": "Vaše aktuální úroveň stresu, den hodinu po hodině a co znamená každý rozsah. Barva a textový popisek jdou vždy spolu, navrženo i s ohledem na barvoslepost. Vše kolem stresu je zdarma.",
    "pricing_eyebrow": "Cena", "pricing_h2": "Zdarma na začátek. Pro jen jednou.",
    "pricing_p": "Žádné měsíční ani roční poplatky. Vela Pro zaplatíte jednou a je vaše.",
    "free_sub": "Pro všechny",
    "free_items": ["Vaše úroveň stresu v reálném čase, se stavem a vysvětlením", "Dnešní den hodinu po hodině a historie stresu", "Týdenní analýzy a upozornění na vysoký stres", "Nabití za každou noc a z čeho vychází", "Komplikace se stresem a nočním nabitím"],
    "pro_sub": "Jednorázový nákup",
    "pro_items": ["Baterie v reálném čase, po celý den", "Křivka dne s nočním nabíjením a každým tréninkem", "Kam se poděla: stres a aktivita, tréninky a čas v bdělém stavu", "Historie baterie po měsících, týdnech a dnech", "Komplikace s Baterií v reálném čase a dnešními hodinovými sloupci"],
  },
  "el": {
    "nav_battery": "Μπαταρία", "nav_stress": "Στρες", "nav_pricing": "Τιμή",
    "title_tag": "Vela — Στρες και Μπαταρία για Apple Watch. Χωρίς συνδρομή. Ποτέ.",
    "meta_desc": "Το Vela μετρά το στρες και την Μπαταρία σας στο Apple Watch με βάση το δικό σας baseline HRV: πώς είστε τώρα, πόσο σας φόρτισε ο ύπνος και πού πηγαίνει η ενέργειά σας μέσα στη μέρα. Όλα υπολογίζονται στο ρολόι. Χωρίς συνδρομή, ποτέ.",
    "eyebrow1": "Στρες και Μπαταρία για Apple Watch",
    "h1": "Η ενέργεια και η ηρεμία σας δεν είναι <em>ο μέσος όρος κανενός</em>.",
    "hero_p": "Το Vela διαβάζει τη μεταβλητότητα του καρδιακού σας ρυθμού (SDNN) στο Apple Watch και τη συγκρίνει με το δικό σας baseline, όχι με ένα όριο πληθυσμού. Έτσι σας λέει πόση ενέργεια σας μένει σήμερα, την Μπαταρία σας, και πώς είστε τώρα, το στρες σας. Όλος ο υπολογισμός γίνεται στο ρολόι. Τίποτα δεν περνά από τους διακομιστές μας, γιατί δεν έχουμε.",
    "story": ("Το άγχος δεν το πολεμάς — το διαβάζεις και προσαρμόζεσαι.", "Το άγχος και την κούραση δεν τα πολεμάς: τα διαβάζεις και προσαρμόζεις την πορεία."),
    "baseline_extra": "Και ισχύει και για τα δύο: το στρες σας μετριέται με βάση το συνηθισμένο σας HRV, και το πόσο σας φορτίζει μια νύχτα επίσης.",
    "p0_rest": "Το HealthKit παρέχει τα δεδομένα, το ρολόι κάνει τα υπόλοιπα. Ούτε το HRV, ούτε ο ύπνος, ούτε η δραστηριότητά σας φεύγουν ποτέ από τη συσκευή σας προς διακομιστή του Vela.",
    "p2": ("Χωρίς παρακολούθηση", "Χωρίς analytics, χωρίς διαφημίσεις, χωρίς SDK τρίτων.", "Το Vela δεν ξέρει ποιος είστε ούτε πότε ανοίγετε την εφαρμογή: το μόνο που φεύγει από το ρολόι πηγαίνει στο δικό σας iCloud."),
    "battery_eyebrow": "Μπαταρία · Νέο στο Vela 2.0",
    "battery_p": "Φορτίζει μόνο όσο κοιμάστε, και με έναν υπνάκο ή με τον ημερήσιο ύπνο μετά από νυχτερινή βάρδια, και αδειάζει με το στρες, τη δραστηριότητα, τις προπονήσεις και τις ώρες που είστε ξύπνιοι. Αν μια μέρα σας φάνηκε μεγάλη, η Μπαταρία σας δείχνει γιατί.",
    "battery_tour": [
      ("Η φόρτισή σας", "Πόσο σας φόρτισε η νύχτα και από πού προκύπτει: πόσο κοιμηθήκατε και το HRV σας στον ύπνο σε σύγκριση με τον μέσο όρο σας.", "Οθόνη του Vela με τη φόρτιση της νύχτας: έως το 80, 27 μονάδες παραπάνω στον ύπνο, 7 ώ. 15 λ. ύπνου και HRV στον ύπνο 9% πάνω από τον μέσο όρο."),
      ("Η καμπύλη της ημέρας", "Πώς ανέβηκε όσο κοιμόσασταν και πώς πέφτει από τη στιγμή που σηκώνεστε, με κάθε προπόνηση σημειωμένη στην ώρα της.", "Καμπύλη μπαταρίας της ημέρας: πράσινη επαναφόρτιση τη νύχτα έως το 80 και μπλε αποφόρτιση μέσα στη μέρα έως το 47, με δύο προπονήσεις σημειωμένες."),
      ("Πού πήγε", "Τι ξοδέψατε από τότε που ξυπνήσατε, χωρισμένο σε στρες και δραστηριότητα, προπονήσεις και ώρες εγρήγορσης. Περιγράφει τι έγινε, χωρίς συμβουλές.", "Ανάλυση της σημερινής κατανάλωσης: 33 μονάδες από το ξύπνημα, 7 από στρες και δραστηριότητα, 12 από μία ώρα προπόνησης και 14 από τις ώρες εγρήγορσης."),
    ],
    "tier_free": "Δωρεάν", "tier_pro": "Pro",
    "stress_eyebrow": "Στρες",
    "stress_p": "Το επίπεδο στρες σας τώρα, η μέρα ώρα με την ώρα και τι σημαίνει κάθε εύρος. Το χρώμα και η ετικέτα κειμένου πάνε πάντα μαζί, σχεδιασμένο και με γνώμονα την αχρωματοψία. Όλο το στρες είναι δωρεάν.",
    "pricing_eyebrow": "Τιμή", "pricing_h2": "Δωρεάν για να ξεκινήσετε. Pro, μία φορά.",
    "pricing_p": "Χωρίς μηνιαίες ή ετήσιες χρεώσεις. Το Vela Pro το πληρώνετε μία φορά και είναι δικό σας.",
    "free_sub": "Για όλους",
    "free_items": ["Το επίπεδο στρες σας σε πραγματικό χρόνο, με την κατάστασή του και την εξήγησή του", "Η σημερινή μέρα ώρα με την ώρα και το ιστορικό στρες", "Εβδομαδιαίες αναλύσεις και ειδοποιήσεις υψηλού στρες", "Η φόρτιση κάθε νύχτας και από πού προκύπτει", "Επιπλοκές (complications) στρες και νυχτερινής φόρτισης"],
    "pro_sub": "Εφάπαξ αγορά",
    "pro_items": ["Η Μπαταρία σε πραγματικό χρόνο, όλη τη μέρα", "Η καμπύλη της ημέρας, με τη νυχτερινή επαναφόρτιση και κάθε προπόνηση", "Πού πήγε: στρες και δραστηριότητα, προπονήσεις και ώρες εγρήγορσης", "Ιστορικό μπαταρίας ανά μήνα, εβδομάδα και ημέρα", "Επιπλοκές με την Μπαταρία σε πραγματικό χρόνο και τις σημερινές ωριαίες μπάρες"],
  },
  "ja": {
    "nav_battery": "バッテリー", "nav_stress": "ストレス", "nav_pricing": "価格",
    "title_tag": "Vela — Apple Watch 用ストレスとバッテリー。サブスクなし。ずっと。",
    "meta_desc": "Vela は Apple Watch で、あなた自身の HRV ベースラインを基準にストレスとバッテリーを測ります。いまの状態、睡眠でどれだけ充電されたか、日中にエネルギーが何に使われたか。計算はすべて時計の中で行われます。サブスクなし、ずっと。",
    "eyebrow1": "Apple Watch 用ストレスとバッテリー",
    "h1": "あなたのエネルギーと穏やかさは、<em>誰かの平均</em>ではない。",
    "hero_p": "Vela は Apple Watch で心拍変動（SDNN）を読み取り、集団のしきい値ではなく、あなた自身のベースラインと比べます。そこから、今日残っているエネルギー（バッテリー）と、いまの状態（ストレス）を伝えます。計算はすべて時計の中で行われます。私たちのサーバーを通るものは何もありません。そもそもサーバーを持っていないからです。",
    "story": ("ストレスは戦うものではなく、読み取って合わせていくものです。", "ストレスも疲れも、戦うものではありません。読み取って、針路を合わせていくものです。"),
    "baseline_extra": "これはどちらにも当てはまります。ストレスはふだんの HRV を基準に測られ、ひと晩でどれだけ充電されるかも同じです。",
    "p0_rest": "HealthKit がデータを提供し、残りは時計が処理します。HRV も睡眠も活動量も、Vela のサーバーへ向けてデバイスの外に出ることはありません。",
    "p2": ("トラッキングなし", "解析ツールも広告も、サードパーティの SDK もありません。", "Vela はあなたが誰なのか、いつアプリを開いたのかを知りません。時計の外に出るのは、あなた自身の iCloud へのデータだけです。"),
    "battery_eyebrow": "バッテリー · Vela 2.0 の新機能",
    "battery_p": "充電されるのは眠っている間だけで、昼寝や夜勤明けの日中の睡眠も含みます。ストレス、活動量、ワークアウト、起きている時間で減っていきます。長く感じた一日には、その理由をバッテリーが見せてくれます。",
    "battery_tour": [
      ("充電", "ひと晩でどれだけ充電されたか、その内訳：睡眠時間と、ふだんの平均と比べた睡眠中の HRV。", "夜間の充電を表示した Vela の画面：80 まで充電、睡眠中に +27、睡眠時間 7 時間 15 分、睡眠中の HRV は平均より 9% 高い。"),
      ("1日のカーブ", "眠っている間にどう上がり、起きてからどう下がっていくか。ワークアウトはその時刻に印が付きます。", "1日のバッテリーカーブ：夜間は緑の充電で 80 まで、日中は青の消費で 47 まで。ワークアウトが2回記録されている。"),
      ("何に使ったか", "起きてから消費した分を、ストレスと活動、ワークアウト、起きていた時間に分けて表示します。起きたことを説明するだけで、アドバイスはしません。", "今日の消費の内訳：起きてから 33、ストレスと活動で 7、1時間のワークアウトで 12、起きていた時間で 14。"),
    ],
    "tier_free": "無料", "tier_pro": "Pro",
    "stress_eyebrow": "ストレス",
    "stress_p": "いまのストレスレベル、1日の時間ごとの推移、各範囲の意味。色とテキストのラベルは常にセットで表示され、色覚特性にも配慮しています。ストレス機能はすべて無料です。",
    "pricing_eyebrow": "価格", "pricing_h2": "無料で始められて、Pro は一度きり。",
    "pricing_p": "月額も年額もありません。Vela Pro は一度支払えば、ずっとあなたのものです。",
    "free_sub": "すべての方に",
    "free_items": ["リアルタイムのストレスレベルと、その状態・説明", "今日の時間ごとの推移とストレスの履歴", "週ごとの分析と高ストレスの通知", "毎晩の充電量とその内訳", "ストレスと夜間の充電のコンプリケーション"],
    "pro_sub": "買い切り",
    "pro_items": ["1日を通したリアルタイムのバッテリー", "夜間の充電とワークアウトを含む1日のカーブ", "何に使ったか：ストレスと活動、ワークアウト、起きていた時間", "月・週・日ごとのバッテリー履歴", "リアルタイムのバッテリーと今日の時間別バーを表示するコンプリケーション"],
  },
}

for _code, _n in _LANDING_2.items():
    _l = L[_code]["landing"]
    _old, _new = _n["story"]
    assert _l["story_p"].count(_old) == 1, (_code, "story")
    _l["story_p"] = _l["story_p"].replace(_old, _new)
    _l["baseline_p"] = _l["baseline_p"] + " " + _n["baseline_extra"]
    _tag, _strong, _ = _l["principles"][0]
    _l["principles"][0] = (_tag, _strong, _n["p0_rest"])
    _l["principles"][2] = _n["p2"]
    _l["h1_plain"] = re.sub(r"<[^>]+>", "", _n["h1"])
    for _k, _val in _n.items():
        if _k not in ("story", "baseline_extra", "p0_rest", "p2"):
            _l[_k] = _val

# ---------------------------------------------------------------------------
# Wellness, not medicine (2.0). A tester asked why the site shows no health
# certification. Vela is a wellness app, not a medical device (EU MDR 2017/745), so
# it can't carry a medical CE mark, and it collects no data, so a privacy seal has
# nothing to certify. A fifth principle says so on the landing page and links to two
# FAQ entries that explain it. Answers use {legal} and {appstore}; the principle, {faq}.
_TRUST = {
  "es": {
    "principles_h2": "Cinco decisiones, tomadas para no cambiar de idea.",
    "principle": ("Bienestar, no medicina", "Vela no es un producto sanitario.",
                  "No diagnostica ni trata ninguna enfermedad: te ayuda a leer tus propios patrones. Por eso no lleva marcado CE ni sellos sanitarios (<a href=\"{faq}\">te contamos por qué</a>)."),
    "faq": [
      ("¿Vela es un producto sanitario? ¿Por qué no lleva marcado CE ni ningún sello sanitario?",
       "No, y es a propósito. Vela es una app de bienestar: compara tu estrés y tu energía con tu propia media, pero no diagnostica, trata, previene ni vigila ninguna enfermedad. En la Unión Europea, el marcado CE sanitario es solo para los productos sanitarios (Reglamento (UE) 2017/745), así que una app de bienestar no puede llevarlo sin engañar a quien la usa. Si algo de lo que ves te preocupa, coméntalo con un profesional sanitario.",
       "medical"),
      ("¿Por qué no tiene un sello de privacidad? ¿Cómo sé qué pasa con mis datos?",
       "Un sello de privacidad certifica cómo una empresa trata los datos que recoge, y Vela no recoge ninguno: no hay cuenta, ni servidores, ni analítica, ni SDK de terceros. Tus datos se quedan en tu reloj y en tu propio iCloud, donde solo entras tú, y así lo declara la etiqueta de privacidad de la <a href=\"{appstore}\">ficha del App Store</a>. Puedes quitarle a Vela el acceso a tus datos de salud cuando quieras, desde la app Salud o los Ajustes del reloj. Detrás de Vela hay una persona, con su nombre y su dirección en el <a href=\"{legal}\">aviso legal</a>.",
       "privacy-seal"),
    ],
  },
  "en": {
    "principles_h2": "Five decisions, made to not change our minds.",
    "principle": ("Wellness, not medicine", "Vela is not a medical device.",
                  "It doesn't diagnose or treat any condition: it helps you read your own patterns. So it carries no CE medical marking or health certification (<a href=\"{faq}\">here's why</a>)."),
    "faq": [
      ("Is Vela a medical device? Why doesn't it have a CE mark or any health certification?",
       "No, and that's deliberate. Vela is a wellness app: it compares your stress and your energy with your own average, but it doesn't diagnose, treat, prevent or monitor any disease. In the European Union, the medical CE mark is only for medical devices (Regulation (EU) 2017/745), so a wellness app can't carry one without misleading the people who use it. If anything you see worries you, talk to a healthcare professional.",
       "medical"),
      ("Why doesn't it have a privacy seal? How do I know what happens to my data?",
       "A privacy seal certifies how a company handles the data it collects, and Vela collects none: there's no account, no servers, no analytics and no third-party SDKs. Your data stays on your watch and in your own iCloud, where only you can get in, and that's what the privacy label on the <a href=\"{appstore}\">App Store listing</a> declares. You can remove Vela's access to your health data at any time, from the Health app or your watch's Settings. Behind Vela there's a person, whose name and address are in the <a href=\"{legal}\">legal notice</a>.",
       "privacy-seal"),
    ],
  },
  "ca": {
    "principles_h2": "Cinc decisions, preses per no canviar d'opinió.",
    "principle": ("Benestar, no medicina", "Vela no és un producte sanitari.",
                  "No diagnostica ni tracta cap malaltia: t'ajuda a llegir els teus propis patrons. Per això no porta marcatge CE ni segells sanitaris (<a href=\"{faq}\">t'expliquem per què</a>)."),
    "faq": [
      ("Vela és un producte sanitari? Per què no porta marcatge CE ni cap segell sanitari?",
       "No, i és a propòsit. Vela és una app de benestar: compara el teu estrès i la teva energia amb la teva pròpia mitjana, però no diagnostica, tracta, prevé ni vigila cap malaltia. A la Unió Europea, el marcatge CE sanitari és només per als productes sanitaris (Reglament (UE) 2017/745), així que una app de benestar no el pot portar sense enganyar qui la fa servir. Si alguna cosa del que veus et preocupa, parla'n amb un professional sanitari.",
       "medical"),
      ("Per què no té cap segell de privadesa? Com sé què passa amb les meves dades?",
       "Un segell de privadesa certifica com una empresa tracta les dades que recull, i Vela no en recull cap: no hi ha compte, ni servidors, ni analítica, ni SDK de tercers. Les teves dades es queden al teu rellotge i al teu propi iCloud, on només hi entres tu, i així ho declara l'etiqueta de privadesa de la <a href=\"{appstore}\">fitxa de l'App Store</a>. Pots treure a Vela l'accés a les teves dades de salut quan vulguis, des de l'app Salut o la Configuració del rellotge. Darrere de Vela hi ha una persona, amb el seu nom i la seva adreça a l'<a href=\"{legal}\">avís legal</a>.",
       "privacy-seal"),
    ],
  },
  "eu": {
    "principles_h2": "Bost erabaki, iritziz ez aldatzeko hartuak.",
    "principle": ("Ongizatea, ez medikuntza", "Vela ez da produktu sanitario bat.",
                  "Ez du gaixotasunik diagnostikatzen ez tratatzen: zure ereduak irakurtzen laguntzen dizu. Horregatik ez darama CE marka sanitariorik ez osasun-zigilurik (<a href=\"{faq}\">zergatik azaltzen dizugu</a>)."),
    "faq": [
      ("Vela produktu sanitario bat al da? Zergatik ez darama CE markarik ez osasun-zigilurik?",
       "Ez, eta nahita da. Vela ongizaterako aplikazio bat da: zure estresa eta energia zure batez bestekoarekin alderatzen ditu, baina ez du gaixotasunik diagnostikatzen, tratatzen, prebenitzen ez zaintzen. Europar Batasunean, CE marka sanitarioa produktu sanitarioentzat bakarrik da ((EB) 2017/745 Erregelamendua); beraz, ongizaterako aplikazio batek ezin du eraman, erabiltzen duena engainatu gabe. Ikusten duzun zerbaitek kezkatzen bazaitu, hitz egin osasun-profesional batekin.",
       "medical"),
      ("Zergatik ez du pribatutasun-zigilurik? Nola jakin zer gertatzen den nire datuekin?",
       "Pribatutasun-zigilu batek ziurtatzen du enpresa batek nola tratatzen dituen biltzen dituen datuak, eta Velak ez du bat ere biltzen: ez dago konturik, ez zerbitzaririk, ez analitikarik, ez hirugarrenen SDKrik. Zure datuak zure erlojuan eta zure iCloud-ean geratzen dira, eta zuk bakarrik sar zaitezke bertara; hala adierazten du <a href=\"{appstore}\">App Storeko fitxako</a> pribatutasun-etiketak. Nahi duzunean ken diezaiokezu Velari zure osasun-datuetarako sarbidea, Osasuna aplikaziotik edo erlojuaren Ezarpenetatik. Velaren atzean pertsona bat dago, eta haren izena eta helbidea <a href=\"{legal}\">lege-oharrean</a> daude.",
       "privacy-seal"),
    ],
  },
  "gl": {
    "principles_h2": "Cinco decisións, tomadas para non cambiar de opinión.",
    "principle": ("Benestar, non medicina", "Vela non é un produto sanitario.",
                  "Non diagnostica nin trata ningunha enfermidade: axúdache a ler os teus propios patróns. Por iso non leva marcado CE nin selos sanitarios (<a href=\"{faq}\">contámosche por que</a>)."),
    "faq": [
      ("Vela é un produto sanitario? Por que non leva marcado CE nin ningún selo sanitario?",
       "Non, e é a propósito. Vela é unha app de benestar: compara o teu estrés e a túa enerxía coa túa propia media, pero non diagnostica, trata, prevén nin vixía ningunha enfermidade. Na Unión Europea, o marcado CE sanitario é só para os produtos sanitarios (Regulamento (UE) 2017/745), así que unha app de benestar non pode levalo sen enganar a quen a usa. Se algo do que ves te preocupa, coméntao cun profesional sanitario.",
       "medical"),
      ("Por que non ten un selo de privacidade? Como sei que pasa cos meus datos?",
       "Un selo de privacidade certifica como unha empresa trata os datos que recolle, e Vela non recolle ningún: non hai conta, nin servidores, nin analítica, nin SDK de terceiros. Os teus datos quedan no teu reloxo e no teu propio iCloud, onde só entras ti, e así o declara a etiqueta de privacidade da <a href=\"{appstore}\">ficha da App Store</a>. Podes quitarlle a Vela o acceso aos teus datos de saúde cando queiras, desde a app Saúde ou os Axustes do reloxo. Detrás de Vela hai unha persoa, co seu nome e o seu enderezo no <a href=\"{legal}\">aviso legal</a>.",
       "privacy-seal"),
    ],
  },
  "fr": {
    "principles_h2": "Cinq décisions, prises pour ne pas changer d'avis.",
    "principle": ("Bien-être, pas médecine", "Vela n'est pas un dispositif médical.",
                  "Elle ne diagnostique ni ne traite aucune maladie : elle vous aide à lire vos propres tendances. C'est pourquoi elle ne porte ni marquage CE médical ni certification de santé (<a href=\"{faq}\">on vous explique pourquoi</a>)."),
    "faq": [
      ("Vela est-elle un dispositif médical ? Pourquoi n'a-t-elle ni marquage CE ni certification de santé ?",
       "Non, et c'est voulu. Vela est une app de bien-être : elle compare votre stress et votre énergie avec votre propre moyenne, mais elle ne diagnostique, ne traite, ne prévient ni ne surveille aucune maladie. Dans l'Union européenne, le marquage CE médical est réservé aux dispositifs médicaux (règlement (UE) 2017/745) : une app de bien-être ne peut donc pas le porter sans tromper ceux qui l'utilisent. Si quelque chose vous inquiète, parlez-en à un professionnel de santé.",
       "medical"),
      ("Pourquoi n'a-t-elle pas de label de confidentialité ? Comment savoir ce que deviennent mes données ?",
       "Un label de confidentialité certifie la façon dont une entreprise traite les données qu'elle collecte, et Vela n'en collecte aucune : pas de compte, pas de serveurs, pas d'analytique, pas de SDK tiers. Vos données restent sur votre montre et dans votre propre iCloud, auquel vous seul avez accès, et c'est ce que déclare l'étiquette de confidentialité de la <a href=\"{appstore}\">fiche App Store</a>. Vous pouvez retirer à Vela l'accès à vos données de santé à tout moment, depuis l'app Santé ou les Réglages de la montre. Derrière Vela, il y a une personne, dont le nom et l'adresse figurent dans les <a href=\"{legal}\">mentions légales</a>.",
       "privacy-seal"),
    ],
  },
  "de": {
    "principles_h2": "Fünf Entscheidungen, getroffen, um sie nicht mehr zu ändern.",
    "principle": ("Wellness, keine Medizin", "Vela ist kein Medizinprodukt.",
                  "Die App stellt keine Diagnosen und behandelt keine Krankheiten: Sie hilft dir, deine eigenen Muster zu lesen. Deshalb trägt sie weder eine CE-Kennzeichnung als Medizinprodukt noch ein Gesundheitssiegel (<a href=\"{faq}\">warum, erklären wir hier</a>)."),
    "faq": [
      ("Ist Vela ein Medizinprodukt? Warum hat die App keine CE-Kennzeichnung und kein Gesundheitssiegel?",
       "Nein, und das ist Absicht. Vela ist eine Wellness-App: Sie vergleicht deinen Stress und deine Energie mit deinem eigenen Durchschnitt, erkennt, behandelt, verhindert oder überwacht aber keine Krankheiten. In der Europäischen Union ist die CE-Kennzeichnung nach der Medizinprodukteverordnung (EU) 2017/745 Medizinprodukten vorbehalten; eine Wellness-App darf sie also nicht tragen, ohne ihre Nutzer in die Irre zu führen. Wenn dich etwas beunruhigt, das du siehst, sprich mit einer Ärztin oder einem Arzt.",
       "medical"),
      ("Warum gibt es kein Datenschutzsiegel? Woher weiß ich, was mit meinen Daten passiert?",
       "Ein Datenschutzsiegel bescheinigt, wie ein Unternehmen mit den Daten umgeht, die es erhebt, und Vela erhebt keine: kein Konto, keine Server, keine Analyse, keine SDKs von Drittanbietern. Deine Daten bleiben auf deiner Uhr und in deiner eigenen iCloud, auf die nur du Zugriff hast, und genau das gibt das Datenschutzetikett im <a href=\"{appstore}\">App Store</a> an. Du kannst Vela den Zugriff auf deine Gesundheitsdaten jederzeit entziehen, in der Health-App oder in den Einstellungen der Uhr. Hinter Vela steht ein Mensch, mit Name und Adresse im <a href=\"{legal}\">Impressum</a>.",
       "privacy-seal"),
    ],
  },
  "it": {
    "principles_h2": "Cinque decisioni, prese per non cambiare idea.",
    "principle": ("Benessere, non medicina", "Vela non è un dispositivo medico.",
                  "Non diagnostica né cura alcuna malattia: ti aiuta a leggere i tuoi schemi. Per questo non ha marcatura CE medica né certificazioni sanitarie (<a href=\"{faq}\">ti spieghiamo perché</a>)."),
    "faq": [
      ("Vela è un dispositivo medico? Perché non ha la marcatura CE né certificazioni sanitarie?",
       "No, ed è voluto. Vela è un'app per il benessere: confronta il tuo stress e la tua energia con la tua media, ma non diagnostica, cura, previene né monitora alcuna malattia. Nell'Unione europea la marcatura CE medica è riservata ai dispositivi medici (regolamento (UE) 2017/745), quindi un'app per il benessere non può averla senza ingannare chi la usa. Se qualcosa di ciò che vedi ti preoccupa, parlane con un professionista sanitario.",
       "medical"),
      ("Perché non ha un sigillo di privacy? Come so cosa succede ai miei dati?",
       "Un sigillo di privacy certifica come un'azienda tratta i dati che raccoglie, e Vela non ne raccoglie nessuno: niente account, niente server, niente analisi, niente SDK di terze parti. I tuoi dati restano sul tuo orologio e nel tuo iCloud, a cui accedi solo tu, ed è quello che dichiara l'etichetta della privacy della <a href=\"{appstore}\">scheda dell'App Store</a>. Puoi togliere a Vela l'accesso ai tuoi dati sanitari quando vuoi, dall'app Salute o dalle Impostazioni dell'orologio. Dietro Vela c'è una persona, con nome e indirizzo nelle <a href=\"{legal}\">note legali</a>.",
       "privacy-seal"),
    ],
  },
  "pt": {
    "principles_h2": "Cinco decisões, tomadas para não mudar de ideias.",
    "principle": ("Bem-estar, não medicina", "A Vela não é um dispositivo médico.",
                  "Não diagnostica nem trata nenhuma doença: ajuda-o a ler os seus próprios padrões. Por isso não tem marcação CE médica nem selos de saúde (<a href=\"{faq}\">explicamos porquê</a>)."),
    "faq": [
      ("A Vela é um dispositivo médico? Porque não tem marcação CE nem nenhum selo de saúde?",
       "Não, e é de propósito. A Vela é uma app de bem-estar: compara o seu stress e a sua energia com a sua própria média, mas não diagnostica, trata, previne nem monitoriza nenhuma doença. Na União Europeia, a marcação CE médica é só para dispositivos médicos (Regulamento (UE) 2017/745), por isso uma app de bem-estar não a pode ter sem enganar quem a usa. Se algo do que vê o preocupa, fale com um profissional de saúde.",
       "medical"),
      ("Porque não tem um selo de privacidade? Como sei o que acontece aos meus dados?",
       "Um selo de privacidade certifica como uma empresa trata os dados que recolhe, e a Vela não recolhe nenhum: não há conta, nem servidores, nem analítica, nem SDK de terceiros. Os seus dados ficam no seu relógio e no seu próprio iCloud, a que só você tem acesso, e é isso que declara a etiqueta de privacidade da <a href=\"{appstore}\">página da App Store</a>. Pode retirar à Vela o acesso aos seus dados de saúde quando quiser, na app Saúde ou nas Definições do relógio. Por trás da Vela há uma pessoa, com o nome e a morada no <a href=\"{legal}\">aviso legal</a>.",
       "privacy-seal"),
    ],
  },
  "cs": {
    "principles_h2": "Pět rozhodnutí, učiněných tak, abychom je neměnili.",
    "principle": ("Wellness, ne medicína", "Vela není zdravotnický prostředek.",
                  "Nestanovuje diagnózy ani neléčí žádné onemocnění: pomáhá vám číst vaše vlastní vzorce. Proto nemá zdravotnické označení CE ani žádnou zdravotní certifikaci (<a href=\"{faq}\">vysvětlujeme proč</a>)."),
    "faq": [
      ("Je Vela zdravotnický prostředek? Proč nemá označení CE ani žádnou zdravotní certifikaci?",
       "Není, a je to záměr. Vela je wellness aplikace: porovnává váš stres a energii s vaším vlastním průměrem, ale žádné onemocnění nediagnostikuje, neléčí, nepředchází mu ani ho nesleduje. V Evropské unii je zdravotnické označení CE určeno jen zdravotnickým prostředkům (nařízení (EU) 2017/745), takže wellness aplikace ho nesmí nést, aniž by klamala své uživatele. Pokud vás něco z toho, co vidíte, znepokojuje, poraďte se se zdravotníkem.",
       "medical"),
      ("Proč nemá pečeť ochrany soukromí? Jak poznám, co se děje s mými daty?",
       "Pečeť ochrany soukromí potvrzuje, jak firma zachází s daty, která shromažďuje, a Vela žádná neshromažďuje: žádný účet, žádné servery, žádná analytika, žádná SDK třetích stran. Vaše data zůstávají v hodinkách a ve vašem vlastním iCloudu, kam máte přístup jen vy, a právě to uvádí štítek soukromí na <a href=\"{appstore}\">stránce v App Storu</a>. Přístup Vely k vašim zdravotním datům můžete kdykoli odebrat v aplikaci Zdraví nebo v Nastavení hodinek. Za Velou stojí člověk, jehož jméno a adresu najdete v <a href=\"{legal}\">právních informacích</a>.",
       "privacy-seal"),
    ],
  },
  "el": {
    "principles_h2": "Πέντε αποφάσεις, που πάρθηκαν για να μην τις αλλάξουμε.",
    "principle": ("Ευεξία, όχι ιατρική", "Το Vela δεν είναι ιατροτεχνολογικό προϊόν.",
                  "Δεν κάνει διάγνωση ούτε θεραπεύει καμία πάθηση: σας βοηθά να διαβάζετε τα δικά σας μοτίβα. Γι' αυτό δεν φέρει ιατρική σήμανση CE ούτε πιστοποίηση υγείας (<a href=\"{faq}\">σας εξηγούμε γιατί</a>)."),
    "faq": [
      ("Είναι το Vela ιατροτεχνολογικό προϊόν; Γιατί δεν έχει σήμανση CE ούτε πιστοποίηση υγείας;",
       "Όχι, και αυτό είναι σκόπιμο. Το Vela είναι εφαρμογή ευεξίας: συγκρίνει το στρες και την ενέργειά σας με τον δικό σας μέσο όρο, αλλά δεν διαγιγνώσκει, δεν θεραπεύει, δεν προλαμβάνει ούτε παρακολουθεί καμία ασθένεια. Στην Ευρωπαϊκή Ένωση, η ιατρική σήμανση CE προορίζεται μόνο για ιατροτεχνολογικά προϊόντα (Κανονισμός (ΕΕ) 2017/745), οπότε μια εφαρμογή ευεξίας δεν μπορεί να τη φέρει χωρίς να παραπλανά όσους τη χρησιμοποιούν. Αν κάτι από όσα βλέπετε σας ανησυχεί, μιλήστε με έναν επαγγελματία υγείας.",
       "medical"),
      ("Γιατί δεν έχει σφραγίδα απορρήτου; Πώς ξέρω τι γίνεται με τα δεδομένα μου;",
       "Μια σφραγίδα απορρήτου πιστοποιεί πώς μια εταιρεία χειρίζεται τα δεδομένα που συλλέγει, και το Vela δεν συλλέγει κανένα: δεν υπάρχει λογαριασμός, ούτε διακομιστές, ούτε αναλυτικά εργαλεία, ούτε SDK τρίτων. Τα δεδομένα σας μένουν στο ρολόι σας και στο δικό σας iCloud, όπου έχετε πρόσβαση μόνο εσείς, και αυτό δηλώνει η ετικέτα απορρήτου στη <a href=\"{appstore}\">σελίδα του App Store</a>. Μπορείτε να αφαιρέσετε από το Vela την πρόσβαση στα δεδομένα υγείας σας όποτε θέλετε, από την εφαρμογή Υγεία ή τις Ρυθμίσεις του ρολογιού. Πίσω από το Vela υπάρχει ένας άνθρωπος, με όνομα και διεύθυνση στις <a href=\"{legal}\">νομικές πληροφορίες</a>.",
       "privacy-seal"),
    ],
  },
  "ja": {
    "principles_h2": "考えを変えないために下した、5つの決定。",
    "principle": ("ウェルネスであり、医療ではない", "Velaは医療機器ではありません。",
                  "病気の診断や治療は行わず、あなた自身のパターンを読み取る手助けをします。そのため、医療機器としてのCEマークや健康関連の認証はありません（<a href=\"{faq}\">理由はこちら</a>）。"),
    "faq": [
      ("Velaは医療機器ですか？なぜCEマークや健康関連の認証がないのですか？",
       "いいえ、意図的にそうしています。Velaはウェルネスアプリです。ストレスとエネルギーをあなた自身の平均と比べますが、病気の診断・治療・予防・監視は行いません。EUでは医療用のCEマークは医療機器のためのもの（規則 (EU) 2017/745）なので、ウェルネスアプリがそれを付ければ利用者を誤解させることになります。表示された内容が気になる場合は、医療の専門家にご相談ください。",
       "medical"),
      ("なぜプライバシー認証マークがないのですか？データがどう扱われるかはどうすれば分かりますか？",
       "プライバシー認証マークは、企業が収集したデータをどう扱うかを証明するものですが、Velaはデータを一切収集しません。アカウントもサーバーも分析ツールも、他社のSDKもありません。データはあなたのApple Watchとあなた自身のiCloudにだけ保存され、アクセスできるのはあなただけです。<a href=\"{appstore}\">App Storeのページ</a>のプライバシーラベルにもそう記載されています。ヘルスケアデータへのVelaのアクセスは、ヘルスケアAppまたはApple Watchの設定からいつでも取り消せます。Velaは一人の個人が開発しており、氏名と住所は<a href=\"{legal}\">法的情報</a>に記載しています。",
       "privacy-seal"),
    ],
  },
}

assert set(_TRUST) == set(ORDER), set(ORDER) ^ set(_TRUST)
for _code, _n in _TRUST.items():
    _l = L[_code]["landing"]
    assert len(_l["principles"]) == 4, (_code, "principles")
    _l["principles"].append(_n["principle"])
    _l["principles_h2"] = _n["principles_h2"]
    L[_code]["faq"].extend(_n["faq"])

# ------------------------------------------------------------ generation

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  {path.relative_to(SITE)}")


# ---------------------------------------------------------------------------
# Aviso legal (LSSI, Ley 34/2002, art. 10). Los datos del titular son los mismos
# que se declaran como comerciante en App Store Connect (DSA): si cambian allí,
# cambiarlos aquí también.
OWNER = {
    "name": "Xavier Camps Novi",
    "nif": "46992142Z",
    "address": "Calle José Salarrulla, 24, 22520 Fraga (Huesca)",
}

LEGAL = {
  "es": {
    "footer": "Aviso legal", "title": "Aviso legal", "title_tag": "Vela HRV — Aviso legal",
    "updated": "Última actualización: noviembre 2026",
    "highlight": "En cumplimiento de la Ley 34/2002, de servicios de la sociedad de la información y de comercio electrónico (LSSI), estos son los datos del titular de este sitio web y de la app Vela HRV.",
    "owner_h": "Titular", "name": "Nombre", "nif": "NIF", "address": "Dirección", "email": "Correo electrónico", "country": "España",
    "sections": [
      ("Objeto", ["Este sitio web presenta la app Vela HRV para Apple Watch y ofrece su soporte, su política de privacidad y su historial de versiones. La app se distribuye únicamente a través del App Store de Apple, que gestiona las descargas y la compra de Vela Pro."]),
      ("Propiedad intelectual", ["Los textos, las imágenes, el diseño y la marca Vela de este sitio pertenecen a su titular. Apple, Apple Watch, App Store y HealthKit son marcas de Apple Inc."]),
      ("Responsabilidad", ["Vela es una app de bienestar, no un dispositivo médico, y no ofrece diagnósticos. La información de la app y de este sitio no sustituye el consejo de un profesional sanitario."]),
      ("Legislación aplicable", ["Este aviso legal se rige por la legislación española."]),
    ],
  },
  "en": {
    "footer": "Legal notice", "title": "Legal notice", "title_tag": "Vela HRV — Legal notice",
    "updated": "Last updated: November 2026",
    "highlight": "In compliance with Spanish Law 34/2002 on information society services and electronic commerce (LSSI), these are the details of the owner of this website and of the Vela HRV app.",
    "owner_h": "Owner", "name": "Name", "nif": "Tax ID (NIF)", "address": "Address", "email": "Email", "country": "Spain",
    "sections": [
      ("Purpose", ["This website presents the Vela HRV app for Apple Watch and provides its support, privacy policy and version history. The app is distributed only through Apple's App Store, which handles downloads and the purchase of Vela Pro."]),
      ("Intellectual property", ["The texts, images, design and the Vela brand on this site belong to its owner. Apple, Apple Watch, App Store and HealthKit are trademarks of Apple Inc."]),
      ("Liability", ["Vela is a wellness app, not a medical device, and does not provide diagnoses. The information in the app and on this site is not a substitute for advice from a healthcare professional."]),
      ("Governing law", ["This legal notice is governed by Spanish law."]),
    ],
  },
  "ca": {
    "footer": "Avís legal", "title": "Avís legal", "title_tag": "Vela HRV — Avís legal",
    "updated": "Última actualització: novembre 2026",
    "highlight": "En compliment de la Llei 34/2002, de serveis de la societat de la informació i de comerç electrònic (LSSI), aquestes són les dades del titular d'aquest lloc web i de l'app Vela HRV.",
    "owner_h": "Titular", "name": "Nom", "nif": "NIF", "address": "Adreça", "email": "Correu electrònic", "country": "Espanya",
    "sections": [
      ("Objecte", ["Aquest lloc web presenta l'app Vela HRV per a Apple Watch i n'ofereix el suport, la política de privadesa i l'historial de versions. L'app es distribueix únicament a través de l'App Store d'Apple, que gestiona les descàrregues i la compra de Vela Pro."]),
      ("Propietat intel·lectual", ["Els textos, les imatges, el disseny i la marca Vela d'aquest lloc pertanyen al seu titular. Apple, Apple Watch, App Store i HealthKit són marques d'Apple Inc."]),
      ("Responsabilitat", ["Vela és una app de benestar, no un dispositiu mèdic, i no ofereix diagnòstics. La informació de l'app i d'aquest lloc no substitueix el consell d'un professional sanitari."]),
      ("Legislació aplicable", ["Aquest avís legal es regeix per la legislació espanyola."]),
    ],
  },
  "eu": {
    "footer": "Lege-oharra", "title": "Lege-oharra", "title_tag": "Vela HRV — Lege-oharra",
    "updated": "Azken eguneratzea: 2026ko azaroa",
    "highlight": "Informazioaren gizartearen zerbitzuei eta merkataritza elektronikoari buruzko 34/2002 Legea (LSSI) betez, hauek dira webgune honen eta Vela HRV aplikazioaren titularraren datuak.",
    "owner_h": "Titularra", "name": "Izena", "nif": "IFZ (NIF)", "address": "Helbidea", "email": "Helbide elektronikoa", "country": "Espainia",
    "sections": [
      ("Xedea", ["Webgune honek Apple Watch-erako Vela HRV aplikazioa aurkezten du, eta haren laguntza, pribatutasun-politika eta bertsioen historia eskaintzen ditu. Aplikazioa Appleren App Store-aren bidez soilik banatzen da, eta hark kudeatzen ditu deskargak eta Vela Pro-ren erosketa."]),
      ("Jabetza intelektuala", ["Webgune honetako testuak, irudiak, diseinua eta Vela marka bere titularrarenak dira. Apple, Apple Watch, App Store eta HealthKit Apple Inc.-en markak dira."]),
      ("Erantzukizuna", ["Vela ongizaterako aplikazio bat da, ez gailu mediko bat, eta ez du diagnostikorik ematen. Aplikazioko eta webgune honetako informazioak ez du osasun-profesional baten aholkua ordezten."]),
      ("Legeria aplikagarria", ["Lege-ohar hau Espainiako legeriak arautzen du."]),
    ],
  },
  "gl": {
    "footer": "Aviso legal", "title": "Aviso legal", "title_tag": "Vela HRV — Aviso legal",
    "updated": "Última actualización: novembro 2026",
    "highlight": "En cumprimento da Lei 34/2002, de servizos da sociedade da información e de comercio electrónico (LSSI), estes son os datos do titular deste sitio web e da app Vela HRV.",
    "owner_h": "Titular", "name": "Nome", "nif": "NIF", "address": "Enderezo", "email": "Correo electrónico", "country": "España",
    "sections": [
      ("Obxecto", ["Este sitio web presenta a app Vela HRV para Apple Watch e ofrece o seu soporte, a súa política de privacidade e o seu historial de versións. A app distribúese unicamente a través da App Store de Apple, que xestiona as descargas e a compra de Vela Pro."]),
      ("Propiedade intelectual", ["Os textos, as imaxes, o deseño e a marca Vela deste sitio pertencen ao seu titular. Apple, Apple Watch, App Store e HealthKit son marcas de Apple Inc."]),
      ("Responsabilidade", ["Vela é unha app de benestar, non un dispositivo médico, e non ofrece diagnósticos. A información da app e deste sitio non substitúe o consello dun profesional sanitario."]),
      ("Lexislación aplicable", ["Este aviso legal réxese pola lexislación española."]),
    ],
  },
  "fr": {
    "footer": "Mentions légales", "title": "Mentions légales", "title_tag": "Vela HRV — Mentions légales",
    "updated": "Dernière mise à jour : novembre 2026",
    "highlight": "Conformément à la loi espagnole 34/2002 sur les services de la société de l'information et le commerce électronique (LSSI), voici les informations sur le titulaire de ce site et de l'app Vela HRV.",
    "owner_h": "Titulaire", "name": "Nom", "nif": "Identifiant fiscal (NIF)", "address": "Adresse", "email": "E-mail", "country": "Espagne",
    "sections": [
      ("Objet", ["Ce site présente l'app Vela HRV pour Apple Watch et propose son assistance, sa politique de confidentialité et l'historique de ses versions. L'app est distribuée uniquement via l'App Store d'Apple, qui gère les téléchargements et l'achat de Vela Pro."]),
      ("Propriété intellectuelle", ["Les textes, les images, le design et la marque Vela de ce site appartiennent à son titulaire. Apple, Apple Watch, App Store et HealthKit sont des marques d'Apple Inc."]),
      ("Responsabilité", ["Vela est une app de bien-être, pas un dispositif médical, et ne pose aucun diagnostic. Les informations de l'app et de ce site ne remplacent pas l'avis d'un professionnel de santé."]),
      ("Droit applicable", ["Les présentes mentions légales sont régies par le droit espagnol."]),
    ],
  },
  "de": {
    "footer": "Impressum", "title": "Impressum", "title_tag": "Vela HRV — Impressum",
    "updated": "Zuletzt aktualisiert: November 2026",
    "highlight": "Gemäß dem spanischen Gesetz 34/2002 über Dienste der Informationsgesellschaft und den elektronischen Geschäftsverkehr (LSSI) sind dies die Angaben zum Inhaber dieser Website und der App Vela HRV.",
    "owner_h": "Inhaber", "name": "Name", "nif": "Steuernummer (NIF)", "address": "Anschrift", "email": "E-Mail", "country": "Spanien",
    "sections": [
      ("Zweck", ["Diese Website stellt die App Vela HRV für die Apple Watch vor und bietet Support, Datenschutzerklärung und Versionsverlauf. Die App wird ausschließlich über den App Store von Apple vertrieben, der die Downloads und den Kauf von Vela Pro abwickelt."]),
      ("Urheberrecht", ["Die Texte, Bilder, das Design und die Marke Vela auf dieser Website gehören ihrem Inhaber. Apple, Apple Watch, App Store und HealthKit sind Marken von Apple Inc."]),
      ("Haftung", ["Vela ist eine Wellness-App, kein Medizinprodukt, und stellt keine Diagnosen. Die Informationen in der App und auf dieser Website ersetzen nicht den Rat medizinischer Fachleute."]),
      ("Anwendbares Recht", ["Dieses Impressum unterliegt spanischem Recht."]),
    ],
  },
  "it": {
    "footer": "Note legali", "title": "Note legali", "title_tag": "Vela HRV — Note legali",
    "updated": "Ultimo aggiornamento: novembre 2026",
    "highlight": "In conformità con la legge spagnola 34/2002 sui servizi della società dell'informazione e sul commercio elettronico (LSSI), questi sono i dati del titolare di questo sito e dell'app Vela HRV.",
    "owner_h": "Titolare", "name": "Nome", "nif": "Codice fiscale (NIF)", "address": "Indirizzo", "email": "E-mail", "country": "Spagna",
    "sections": [
      ("Oggetto", ["Questo sito presenta l'app Vela HRV per Apple Watch e ne offre il supporto, l'informativa sulla privacy e lo storico delle versioni. L'app è distribuita esclusivamente tramite l'App Store di Apple, che gestisce i download e l'acquisto di Vela Pro."]),
      ("Proprietà intellettuale", ["I testi, le immagini, il design e il marchio Vela di questo sito appartengono al suo titolare. Apple, Apple Watch, App Store e HealthKit sono marchi di Apple Inc."]),
      ("Responsabilità", ["Vela è un'app per il benessere, non un dispositivo medico, e non fornisce diagnosi. Le informazioni dell'app e di questo sito non sostituiscono il parere di un professionista sanitario."]),
      ("Legge applicabile", ["Le presenti note legali sono regolate dalla legge spagnola."]),
    ],
  },
  "pt": {
    "footer": "Aviso legal", "title": "Aviso legal", "title_tag": "Vela HRV — Aviso legal",
    "updated": "Última atualização: novembro de 2026",
    "highlight": "Em cumprimento da lei espanhola 34/2002, de serviços da sociedade da informação e de comércio eletrónico (LSSI), estes são os dados do titular deste site e da app Vela HRV.",
    "owner_h": "Titular", "name": "Nome", "nif": "NIF", "address": "Morada", "email": "E-mail", "country": "Espanha",
    "sections": [
      ("Objeto", ["Este site apresenta a app Vela HRV para Apple Watch e oferece o seu suporte, a sua política de privacidade e o seu histórico de versões. A app é distribuída apenas através da App Store da Apple, que gere as transferências e a compra do Vela Pro."]),
      ("Propriedade intelectual", ["Os textos, as imagens, o design e a marca Vela deste site pertencem ao seu titular. Apple, Apple Watch, App Store e HealthKit são marcas da Apple Inc."]),
      ("Responsabilidade", ["A Vela é uma app de bem-estar, não um dispositivo médico, e não faz diagnósticos. A informação da app e deste site não substitui o conselho de um profissional de saúde."]),
      ("Lei aplicável", ["Este aviso legal rege-se pela lei espanhola."]),
    ],
  },
  "cs": {
    "footer": "Právní informace", "title": "Právní informace", "title_tag": "Vela HRV — Právní informace",
    "updated": "Poslední aktualizace: listopad 2026",
    "highlight": "V souladu se španělským zákonem 34/2002 o službách informační společnosti a elektronickém obchodu (LSSI) uvádíme údaje o provozovateli tohoto webu a aplikace Vela HRV.",
    "owner_h": "Provozovatel", "name": "Jméno", "nif": "Daňové identifikační číslo (NIF)", "address": "Adresa", "email": "E-mail", "country": "Španělsko",
    "sections": [
      ("Účel", ["Tento web představuje aplikaci Vela HRV pro Apple Watch a nabízí její podporu, zásady ochrany soukromí a historii verzí. Aplikace se distribuuje výhradně přes App Store společnosti Apple, který zajišťuje stahování i nákup Vela Pro."]),
      ("Duševní vlastnictví", ["Texty, obrázky, design a značka Vela na tomto webu patří jeho provozovateli. Apple, Apple Watch, App Store a HealthKit jsou ochranné známky společnosti Apple Inc."]),
      ("Odpovědnost", ["Vela je wellness aplikace, nikoli zdravotnický prostředek, a nestanovuje diagnózy. Informace v aplikaci a na tomto webu nenahrazují radu zdravotnického odborníka."]),
      ("Rozhodné právo", ["Tyto právní informace se řídí španělským právem."]),
    ],
  },
  "el": {
    "footer": "Νομικές πληροφορίες", "title": "Νομικές πληροφορίες", "title_tag": "Vela HRV — Νομικές πληροφορίες",
    "updated": "Τελευταία ενημέρωση: Νοέμβριος 2026",
    "highlight": "Σύμφωνα με τον ισπανικό νόμο 34/2002 για τις υπηρεσίες της κοινωνίας της πληροφορίας και το ηλεκτρονικό εμπόριο (LSSI), αυτά είναι τα στοιχεία του κατόχου αυτού του ιστότοπου και της εφαρμογής Vela HRV.",
    "owner_h": "Κάτοχος", "name": "Όνομα", "nif": "Αριθμός φορολογικού μητρώου (NIF)", "address": "Διεύθυνση", "email": "Email", "country": "Ισπανία",
    "sections": [
      ("Σκοπός", ["Αυτός ο ιστότοπος παρουσιάζει την εφαρμογή Vela HRV για Apple Watch και προσφέρει την υποστήριξή της, την πολιτική απορρήτου και το ιστορικό εκδόσεων. Η εφαρμογή διανέμεται αποκλειστικά μέσω του App Store της Apple, που διαχειρίζεται τις λήψεις και την αγορά του Vela Pro."]),
      ("Πνευματική ιδιοκτησία", ["Τα κείμενα, οι εικόνες, ο σχεδιασμός και το σήμα Vela αυτού του ιστότοπου ανήκουν στον κάτοχό του. Τα Apple, Apple Watch, App Store και HealthKit είναι εμπορικά σήματα της Apple Inc."]),
      ("Ευθύνη", ["Το Vela είναι εφαρμογή ευεξίας, όχι ιατροτεχνολογικό προϊόν, και δεν κάνει διαγνώσεις. Οι πληροφορίες της εφαρμογής και αυτού του ιστότοπου δεν αντικαθιστούν τη συμβουλή επαγγελματία υγείας."]),
      ("Εφαρμοστέο δίκαιο", ["Οι παρούσες νομικές πληροφορίες διέπονται από το ισπανικό δίκαιο."]),
    ],
  },
  "ja": {
    "footer": "法的情報", "title": "法的情報", "title_tag": "Vela HRV — 法的情報",
    "updated": "最終更新：2026年11月",
    "highlight": "スペインの情報社会サービスおよび電子商取引に関する法律（Ley 34/2002、LSSI）に基づき、本サイトおよびアプリ Vela HRV の運営者情報を記載します。",
    "owner_h": "運営者", "name": "氏名", "nif": "納税者番号（NIF）", "address": "住所", "email": "メール", "country": "スペイン",
    "sections": [
      ("目的", ["本サイトは Apple Watch 用アプリ Vela HRV を紹介し、サポート、プライバシーポリシー、バージョン履歴を提供します。アプリは Apple の App Store のみで配信され、ダウンロードと Vela Pro の購入は App Store が処理します。"]),
      ("知的財産", ["本サイトの文章、画像、デザイン、および Vela のブランドは運営者に帰属します。Apple、Apple Watch、App Store、HealthKit は Apple Inc. の商標です。"]),
      ("免責", ["Vela はウェルネスアプリであり、医療機器ではなく、診断を行うものではありません。アプリおよび本サイトの情報は、医療専門家の助言に代わるものではありません。"]),
      ("準拠法", ["本法的情報はスペイン法に準拠します。"]),
    ],
  },
}

def render_legal(code, t):
    g = LEGAL[code]
    rows = [(g["name"], OWNER["name"]), (g["nif"], OWNER["nif"]),
            (g["address"], f'{OWNER["address"]}, {g["country"]}'),
            (g["email"], f'<a class="contact-link" href="mailto:{MAIL}">{MAIL}</a>')]
    owner = "".join(f"<p><strong>{k}:</strong> {v}</p>" for k, v in rows)
    sections = "\n".join(
        f"""    <div class="fade-in">
      <section>
        <h2>{h}</h2>
        {"".join(f'<p>{x}</p>' for x in ps)}
      </section>
    </div>"""
        for h, ps in g["sections"])
    return HEAD.format(lang=code, title=g["title_tag"], css=SUB_CSS,
                       seo=seo_head(code, "legal", g["title_tag"], g["highlight"])) + f"""<body>
  <div class="container">
    <header>
      <a class="back-link" href="{path_for(code, 'landing')}">{t['back_home']}</a>
      <h1 class="page-title">{g['title']}</h1>
      <p class="page-meta">{g['updated']}</p>
    </header>

    <div class="highlight-card fade-in">
      <p>{g['highlight']}</p>
    </div>

    <div class="divider"></div>

    <div class="fade-in">
      <section>
        <h2>{g['owner_h']}</h2>
        {owner}
      </section>
    </div>
{sections}

{footer(t, 'legal', code)}
  </div>
</body>
</html>
"""

def render_sitemap() -> str:
    """One <url> per locale x page, each carrying the full hreflang alternate
    cluster (+ x-default) so crawlers can resolve the whole translation set
    from a single sitemap entry, per Google's hreflang-in-sitemap format."""
    urls = []
    for page in PAGES:
        for code in ORDER:
            alternates = "\n".join(
                f'    <xhtml:link rel="alternate" hreflang="{HREFLANG_TAG[c]}" href="{abs_url(c, page)}"/>'
                for c in ORDER)
            alternates += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(DEFAULT_LOCALE, page)}"/>'
            urls.append(f"""  <url>
    <loc>{abs_url(code, page)}</loc>
    <lastmod>{BUILD_DATE}</lastmod>
{alternates}
  </url>""")
    body = "\n".join(urls)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{body}
</urlset>
'''

def render_robots() -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""

def main():
    print("Generando páginas del sitio (12 idiomas x 6 páginas):")
    for code in ORDER:
        t = L[code]
        write(out_path(code, "landing"), render_landing(code, t))
        write(out_path(code, "support"), render_support(code, t))
        write(out_path(code, "privacy"), render_privacy(code, t))
        write(out_path(code, "accessibility"), render_a11y(code, t))
        write(out_path(code, "changelog"), render_changelog(code, t))
        write(out_path(code, "legal"), render_legal(code, t))
    write(SITE / "sitemap.xml", render_sitemap())
    write(SITE / "robots.txt", render_robots())

if __name__ == "__main__":
    main()
