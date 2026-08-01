#!/usr/bin/env python3
"""Generates every page of the vela-app site — landing (home), support, privacy
and accessibility — for all 9 locales (en, es, ca, eu, gl, fr, de, it, pt) from
a single content dictionary. Run from anywhere; SITE is the repo root
(tools/..). The site is served from the domain root (see CNAME), so URLs have
no path prefix: EN lives at the root, other locales under /<code>/."""

from pathlib import Path

SITE = Path(__file__).parent.parent
MAIL = "xaviercampsnovi@gmail.com"
ORDER = ["es", "en", "ca", "eu", "gl", "fr", "de", "it", "pt"]
APPSTORE_URL = "https://apps.apple.com/app/vela-hrv/id6762096428"
TOUR_IMAGES = ["watch-shot-score.png", "watch-shot-trend.png", "watch-shot-explain.png"]

def path_for(code: str, page: str) -> str:
    """page is one of: landing, support, privacy, accessibility."""
    base = "/" if code == "en" else f"/{code}/"
    return base if page == "landing" else f"{base}{page}/"

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

  /* ---------- HERO ---------- */
  .hero{
    padding:88px 0 64px;
    position:relative;
  }
  .hero-grid{
    display:grid;
    grid-template-columns:1.05fr 0.95fr;
    gap:56px;
    align-items:center;
  }
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

  .wave-panel{
    background:var(--bg-deep);
    border:1px solid var(--hairline);
    border-radius:20px;
    padding:22px 20px 18px;
  }
  .wave-panel-head{
    display:flex; justify-content:space-between; align-items:baseline;
    font-family:var(--mono); font-size:11px; color:var(--text-3);
    letter-spacing:0.06em; margin-bottom:10px;
  }
  .wave-panel-head span:last-child{ color:var(--teal); }
  canvas#hero-wave{
    width:100%; height:180px; display:block;
  }
  .wave-readout{
    display:flex; justify-content:space-between;
    margin-top:14px;
    font-family:var(--mono);
    font-size:12px;
    color:var(--text-3);
  }
  .wave-readout b{ color:var(--text-1); font-weight:500; }

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

  /* ---------- WATCH SHOWCASE ---------- */
  .shot-card{
    display:block;
  }
  .shot-card img{ width:100%; height:auto; display:block; }

  .watch-showcase{ max-width:720px; margin:0 auto; }

  .tour-grid{
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:28px;
  }
  .tour-item .shot-card{ margin-bottom:20px; }
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
    .hero-grid{ grid-template-columns:1fr; }
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
<meta name="description" content="{desc}">
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
      <p>© 2026 Vela HRV · {t['rights']}</p>
      {lang_row(page, code, t['lang_label'])}
    </footer>"""

def render_support(code, t):
    faqs = "\n\n".join(
        f'''        <div class="faq-item">
          <h3>{q}</h3>
          <p>{a}</p>
        </div>'''
        for q, a in t["faq"])
    return HEAD.format(lang=code, title=t["support_title"], css=SUPPORT_CSS) + f"""<body>
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
    return HEAD.format(lang=code, title=p["title_tag"], css=SUB_CSS) + f"""<body>
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
    return HEAD.format(lang=code, title=a["title_tag"], css=SUB_CSS) + f"""<body>
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

def render_landing(code, t):
    L = t["landing"]
    principles = "\n".join(
        f'''        <div class="principle">
          <span class="tag">{tag}</span>
          <p><strong>{strong}</strong> {rest}</p>
        </div>'''
        for tag, strong, rest in L["principles"])
    tour = "\n".join(
        f'''        <div class="tour-item">
          <div class="shot-card">
            <img src="/assets/{img}" alt="{alt}">
          </div>
          <span class="tag">{tag}</span>
          <p>{p}</p>
        </div>'''
        for (tag, p, alt), img in zip(L["tour"], TOUR_IMAGES))
    return LANDING_HEAD.format(lang=code, title=L["title_tag"], desc=L["meta_desc"], css=LANDING_CSS) + f"""<body>

<header>
  <nav>
    <a class="brand" href="#top">
      <img src="/assets/icon-1024.png" alt="">
      vela
    </a>
    <a class="nav-cta" href="{APPSTORE_URL}" target="_blank" rel="noopener">{L['nav_cta']}</a>
  </nav>
</header>

<main id="top">

  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">{L['eyebrow1']}</p>
        <h1>{L['h1']}</h1>
        <p>{L['hero_p']}</p>
        <div class="cta-row">
          <a class="badge-link" href="{APPSTORE_URL}" target="_blank" rel="noopener">
            <img class="badge-appstore" src="/assets/app-store-badge-white.svg" alt="{L['badge_alt']}">
          </a>
        </div>
      </div>
      <div class="wave-panel">
        <div class="wave-panel-head">
          <span>{L['wave_kicker']}</span>
          <span>{L['wave_state']}</span>
        </div>
        <canvas id="hero-wave" width="480" height="180"></canvas>
        <div class="wave-readout">
          <span>{L['wave_left']}</span>
          <span>{L['wave_right_html']}</span>
        </div>
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

  <section>
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['showcase_eyebrow']}</p>
        <h2>{L['showcase_h2']}</h2>
        <p>{L['showcase_p']}</p>
      </div>
      <div class="watch-showcase">
        <div class="shot-card">
          <img src="/assets/watch-mockup-combined.png" alt="{L['showcase_alt']}">
        </div>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{L['tour_eyebrow']}</p>
        <h2>{L['tour_h2']}</h2>
      </div>
      <div class="tour-grid">
{tour}
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
        <div class="shot-card">
          <img src="/assets/watch-onboarding.png" alt="{L['onboarding_alt']}">
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
      <a href="{path_for(code, 'privacy')}">{L['footer_privacy']}</a>
      <a href="mailto:{MAIL}">{L['footer_contact']}</a>
    </div>
  </div>
  <div class="wrap">
    {lang_row('landing', code, t['lang_label'])}
  </div>
</footer>

<script>
(function(){{
  var canvas = document.getElementById('hero-wave');
  var ctx = canvas.getContext('2d');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W, H, dpr = Math.min(window.devicePixelRatio || 1, 2);

  function resize(){{
    var rect = canvas.getBoundingClientRect();
    W = rect.width; H = rect.height;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }}
  window.addEventListener('resize', resize);
  resize();

  var t = 0;
  var noise = 1;

  function drawWave(offsetY, amp, freq, phase, color, glow, lineWidth){{
    ctx.beginPath();
    for(var x=0; x<=W; x+=4){{
      var n = reduceMotion ? 0 : (Math.random()-0.5) * noise * 6;
      var y = offsetY + Math.sin((x*freq) + phase) * amp + n;
      if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }}
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    if(glow){{
      ctx.shadowColor = color;
      ctx.shadowBlur = 8;
    }} else {{
      ctx.shadowBlur = 0;
    }}
    ctx.stroke();
  }}

  function frame(){{
    ctx.clearRect(0,0,W,H);
    t += 0.02;
    if(!reduceMotion && noise > 0){{ noise = Math.max(0, noise - 0.0018); }}

    ctx.beginPath();
    ctx.setLineDash([6,7]);
    ctx.moveTo(0, H*0.5);
    ctx.lineTo(W, H*0.5);
    ctx.strokeStyle = 'rgba(245,248,252,0.18)';
    ctx.lineWidth = 1;
    ctx.shadowBlur = 0;
    ctx.stroke();
    ctx.setLineDash([]);

    drawWave(H*0.5, H*0.22, 0.045, t, '#3DCFCF', true, 2.4);

    if(!reduceMotion){{
      requestAnimationFrame(frame);
    }}
  }}

  if(reduceMotion){{
    noise = 0;
    frame();
  }} else {{
    requestAnimationFrame(frame);
  }}
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
    ("¿Qué permisos necesita Vela?", "Vela solicita acceso a HealthKit para leer los datos de variabilidad de frecuencia cardíaca que tu Apple Watch ya recoge automáticamente."),
  ],
  "contact_h": "Contacto y soporte",
  "contact_p": "¿Tienes alguna pregunta, has encontrado un error o quieres compartir feedback? Escríbenos directamente.",
  "privacy": {
    "title_tag": "Vela HRV — Política de Privacidad", "title": "Política de Privacidad",
    "updated": "Última actualización: abril 2026",
    "highlight": "Vela no recopila, transmite ni almacena ningún dato personal en servidores externos. Todo permanece en tu dispositivo y en tu iCloud privado.",
    "sections": [
      ("Qué datos utiliza Vela", [
        "Vela lee datos de variabilidad de frecuencia cardíaca (HRV) de Apple HealthKit para calcular tu score de estrés personal. Estos datos ya los recoge automáticamente tu Apple Watch.",
        "Vela también almacena las lecturas que calcula: tu historial de score de estrés, tu baseline personal de HRV y las muestras de HRV usadas para el cálculo del baseline."]),
      ("Dónde viven tus datos", [
        "Todos los datos se almacenan localmente en tu Apple Watch y se sincronizan de forma privada a través de tu propia cuenta de iCloud usando el framework CloudKit de Apple. Vela no tiene servidores. Ningún dato pasa nunca por sistemas propiedad de Vela.",
        "Solo tú puedes acceder a tus datos. Ni nosotros ni terceros."]),
      ("Terceros", [
        "Vela no comparte ningún dato con terceros. No utilizamos servicios de analítica, SDKs publicitarios ni herramientas de seguimiento externas."]),
      ("Datos de salud", [
        "Vela accede a datos de salud únicamente para proporcionar su funcionalidad principal: medir y hacer seguimiento de tu nivel de estrés. Los datos de salud nunca se usan con fines publicitarios ni se venden a ninguna parte."]),
      ("Menores", [
        "Vela no está dirigida a menores de 13 años y no recopila datos de ellos de forma consciente."]),
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
    "title_tag": "Vela — HRV para Apple Watch. Sin suscripción. Nunca.",
    "meta_desc": "Vela mide tu variabilidad de ritmo cardíaco (HRV/SDNN) en Apple Watch y construye tu propia línea base personal. Todo se procesa en el reloj. Sincroniza con tu iCloud. Sin suscripción, nunca.",
    "eyebrow1": "HRV para Apple Watch",
    "h1": "Tu calma no es <em>la media</em> de nadie.",
    "hero_p": "Vela mide tu variabilidad de ritmo cardíaco (SDNN) directamente en tu Apple Watch y construye una línea base propia — no un umbral genérico de población. Todo el cálculo ocurre en el reloj. Nada pasa por nuestros servidores, porque no los tenemos.",
    "badge_alt": "Descargar en el App Store",
    "wave_kicker": "SDNN · TIEMPO REAL", "wave_state": "EN REPOSO",
    "wave_left": "ruido de población", "wave_right_html": "<b>tu línea base</b> se asienta",
    "baseline_eyebrow": "Por qué el promedio no sirve",
    "baseline_h2": "25&nbsp;ms de HRV puede ser alto para ti y bajo para otra persona.",
    "baseline_p": "El HRV varía enormemente entre personas. Un umbral de población trata a todo el mundo igual — y por eso casi siempre se equivoca. Vela construye tu propia línea base a partir de tu historial real: si ya tienes datos de HRV en tu Apple Watch, puede empezar desde el primer día; si eres nuevo, tarda entre 7 y 14 días en asentarse.",
    "legend1": "Umbral genérico de población", "legend2": "Muestras individuales", "legend3": "Tu línea base personal",
    "principles_eyebrow": "Cómo funciona", "principles_h2": "Cuatro decisiones, tomadas para no cambiar de idea.",
    "principles": [
      ("On-device", "Todo el cálculo ocurre en tu Watch.", "HealthKit entrega los datos, el reloj hace el resto. Ningún dato de HRV sale de tu dispositivo hacia un servidor de Vela."),
      ("Tu iCloud, no el nuestro", "La sincronización usa tu propia cuenta de iCloud", "vía CloudKit. Vela no aloja tus datos en ningún sitio — no puede, porque no tiene dónde."),
      ("Sin suscripción. Nunca.", "Sin cuotas mensuales ni anuales.", "Vela es gratis hoy. En el futuro habrá una versión Pro de pago único — nunca una suscripción."),
      ("Accesible de serie", "VoiceOver, Dynamic Type, Reduce Motion", "y 9 idiomas: castellano, català, euskara, galego, English, français, Deutsch, italiano y português."),
    ],
    "showcase_eyebrow": "En tu muñeca", "showcase_h2": "Un score, un estado, una tendencia.",
    "showcase_p": "El color y la etiqueta de texto siempre van juntos — también pensado para quienes no distinguen bien los colores. Cada score se explica: qué rango es “Normal”, cuándo pasa a “Alto” y por qué.",
    "showcase_alt": "Tres pantallas de Vela en Apple Watch Ultra: score de estrés actual con estado Normal, tendencia semanal con la media del día, y pantalla de explicación de los rangos Normal y Alto.",
    "tour_eyebrow": "Recorrido rápido", "tour_h2": "Tres pantallas, cada una con un único trabajo.",
    "tour": [
      ("Score actual", "Un número, un estado, calculado enteramente en el reloj — sin esperar a que nada sincronice.", "Pantalla principal de Vela mostrando un score de estrés de 68, estado Normal, calculado en el momento."),
      ("Tendencia", "Cada lectura del día, comparada contra tu propia línea discontinua — no contra la de nadie más.", "Gráfico de tendencia con la media de estrés del día y las lecturas de cada hora, comparadas contra la línea base personal."),
      ("Rangos explicados", "Nada de cifras crípticas: cada rango dice qué significa y qué esperar de él.", "Pantalla de explicación de los rangos de estrés: Normal entre 40 y 69, Alto entre 70 y 100."),
    ],
    "onboarding_eyebrow": "Así empiezas", "onboarding_h2": "Te pedimos permiso antes de medir nada.",
    "onboarding_p": "Vela pide acceso a tu HRV de forma explícita, no en la letra pequeña. Y si eres nuevo midiendo HRV, te dice cuánto falta para tener una línea base fiable — sin fingir que el primer día ya sabe quién eres.",
    "onboarding_alt": "Flujo de bienvenida de Vela en Apple Watch: pantalla de bienvenida, solicitud explícita de acceso a los datos de variabilidad cardíaca, y pantalla de construcción de la línea base con 7 días restantes.",
    "closing_eyebrow": "Descárgala hoy", "closing_h2": "Sin suscripción. <em>Nunca.</em>",
    "closing_p": "Vela está disponible gratis en el App Store para Apple Watch.",
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
    ("What permissions does Vela need?", "Vela requests access to HealthKit to read the heart rate variability data that your Apple Watch already collects automatically."),
  ],
  "contact_h": "Contact & support",
  "contact_p": "Have a question, found a bug, or want to share feedback? Reach out directly.",
  "privacy": {
    "title_tag": "Vela HRV — Privacy Policy", "title": "Privacy Policy",
    "updated": "Last updated: April 2026",
    "highlight": "Vela does not collect, transmit, or store any personal data on external servers. Everything stays on your device and your private iCloud.",
    "sections": [
      ("What data Vela uses", [
        "Vela reads heart rate variability (HRV) data from Apple HealthKit to calculate your personal stress score. This data is already collected automatically by your Apple Watch.",
        "Vela also stores the readings it calculates — your stress score history, your personal HRV baseline, and raw HRV samples used for baseline calculation."]),
      ("Where your data lives", [
        "All data is stored locally on your Apple Watch and synced privately through your own iCloud account using Apple's CloudKit framework. Vela has no servers. No data ever passes through systems owned or operated by Vela.",
        "Only you can access your data. Not us, not third parties."]),
      ("Third parties", [
        "Vela does not share any data with third parties. We do not use analytics services, advertising SDKs, or any external tracking tools."]),
      ("Health data", [
        "Vela accesses health data solely to provide its core functionality — measuring and tracking your stress level. Health data is never used for advertising or sold to any party."]),
      ("Children", [
        "Vela is not directed at children under the age of 13 and does not knowingly collect data from them."]),
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
    "wave_kicker": "SDNN · LIVE", "wave_state": "AT REST",
    "wave_left": "population noise", "wave_right_html": "<b>your baseline</b> settles",
    "baseline_eyebrow": "Why the average doesn't work",
    "baseline_h2": "25&nbsp;ms of HRV can be high for you and low for someone else.",
    "baseline_p": "HRV varies enormously between people. A population threshold treats everyone the same — which is exactly why it's almost always wrong. Vela builds your own baseline from your real history: if you already have HRV data on your Apple Watch, it can start from day one; if you're new, it takes 7–14 days to settle.",
    "legend1": "Generic population threshold", "legend2": "Individual samples", "legend3": "Your personal baseline",
    "principles_eyebrow": "How it works", "principles_h2": "Four decisions, made to not change our minds.",
    "principles": [
      ("On-device", "All the computation happens on your Watch.", "HealthKit provides the data, the watch does the rest. No HRV data ever leaves your device toward a Vela server."),
      ("Your iCloud, not ours", "Syncing uses your own iCloud account", "via CloudKit. Vela doesn't host your data anywhere — it can't, because it has nowhere to."),
      ("No subscription. Ever.", "No monthly or yearly fees.", "Vela is free today. In the future there will be a paid Pro version — never a subscription."),
      ("Accessible by default", "VoiceOver, Dynamic Type, Reduce Motion", "and 9 languages: Spanish, Catalan, Basque, Galician, English, French, German, Italian, and Portuguese."),
    ],
    "showcase_eyebrow": "On your wrist", "showcase_h2": "One score, one state, one trend.",
    "showcase_p": "Color and text label always go together — designed with color blindness in mind too. Every score is explained: which range counts as “Normal”, when it becomes “High”, and why.",
    "showcase_alt": "Three Vela screens on Apple Watch Ultra: current stress score with Normal status, weekly trend with the day's average, and a screen explaining the Normal and High ranges.",
    "tour_eyebrow": "Quick tour", "tour_h2": "Three screens, each with a single job.",
    "tour": [
      ("Current score", "One number, one state, computed entirely on the watch — no waiting for anything to sync.", "Vela's main screen showing a stress score of 68, Normal status, calculated in the moment."),
      ("Trend", "Every reading of the day, compared against your own dashed line — not anyone else's.", "Trend chart with the day's average stress and hourly readings, compared against the personal baseline."),
      ("Ranges explained", "No cryptic numbers: every range says what it means and what to expect.", "Screen explaining the stress ranges: Normal between 40 and 69, High between 70 and 100."),
    ],
    "onboarding_eyebrow": "Getting started", "onboarding_h2": "We ask permission before measuring anything.",
    "onboarding_p": "Vela asks for access to your HRV explicitly, not in the fine print. And if you're new to measuring HRV, it tells you how long until you have a reliable baseline — without pretending it knows who you are on day one.",
    "onboarding_alt": "Vela's onboarding flow on Apple Watch: a welcome screen, an explicit request for access to heart rate variability data, and a baseline-building screen showing 7 days remaining.",
    "closing_eyebrow": "Download it today", "closing_h2": "No subscription. <em>Ever.</em>",
    "closing_p": "Vela is available for free on the App Store for Apple Watch.",
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
    ("Quins permisos necessita Vela?", "Vela sol·licita accés a HealthKit per llegir les dades de variabilitat de la freqüència cardíaca que el teu Apple Watch ja recull automàticament."),
  ],
  "contact_h": "Contacte i suport",
  "contact_p": "Tens cap pregunta, has trobat un error o vols compartir feedback? Escriu-nos directament.",
  "privacy": {
    "title_tag": "Vela HRV — Política de privadesa", "title": "Política de privadesa",
    "updated": "Última actualització: abril 2026",
    "highlight": "Vela no recull, transmet ni emmagatzema cap dada personal en servidors externs. Tot es queda al teu dispositiu i al teu iCloud privat.",
    "sections": [
      ("Quines dades fa servir Vela", [
        "Vela llegeix dades de variabilitat de la freqüència cardíaca (HRV) d'Apple HealthKit per calcular el teu score d'estrès personal. Aquestes dades ja les recull automàticament el teu Apple Watch.",
        "Vela també emmagatzema les lectures que calcula — l'historial del teu score d'estrès, la teva línia base d'HRV personal i les mostres d'HRV en brut utilitzades per calcular-la."]),
      ("On viuen les teves dades", [
        "Totes les dades s'emmagatzemen localment al teu Apple Watch i se sincronitzen de manera privada a través del teu propi compte d'iCloud mitjançant el framework CloudKit d'Apple. Vela no té servidors. Cap dada passa mai per sistemes propietat de Vela.",
        "Només tu pots accedir a les teves dades. Ni nosaltres, ni tercers."]),
      ("Tercers", [
        "Vela no comparteix cap dada amb tercers. No fem servir serveis d'analítica, SDK publicitaris ni cap eina de seguiment externa."]),
      ("Dades de salut", [
        "Vela accedeix a les dades de salut únicament per oferir la seva funcionalitat principal — mesurar i fer el seguiment del teu nivell d'estrès. Les dades de salut mai no s'utilitzen per a publicitat ni es venen a ningú."]),
      ("Menors", [
        "Vela no està dirigida a menors de 13 anys i no recull deliberadament dades seves."]),
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
    "wave_kicker": "SDNN · EN TEMPS REAL", "wave_state": "EN REPÒS",
    "wave_left": "soroll de població", "wave_right_html": "<b>la teva línia base</b> s'assenta",
    "baseline_eyebrow": "Per què el promig no serveix",
    "baseline_h2": "25&nbsp;ms d'HRV pot ser alt per a tu i baix per a una altra persona.",
    "baseline_p": "L'HRV varia enormement entre persones. Un llindar de població tracta tothom igual — i per això gairebé sempre s'equivoca. Vela construeix la teva pròpia línia base a partir del teu historial real: si ja tens dades d'HRV al teu Apple Watch, pot començar des del primer dia; si ets nou, triga entre 7 i 14 dies a assentar-se.",
    "legend1": "Llindar genèric de població", "legend2": "Mostres individuals", "legend3": "La teva línia base personal",
    "principles_eyebrow": "Com funciona", "principles_h2": "Quatre decisions, preses per no canviar d'opinió.",
    "principles": [
      ("On-device", "Tot el càlcul passa al teu Watch.", "HealthKit lliura les dades, el rellotge fa la resta. Cap dada d'HRV surt del teu dispositiu cap a un servidor de Vela."),
      ("El teu iCloud, no el nostre", "La sincronització fa servir el teu propi compte d'iCloud", "via CloudKit. Vela no allotja les teves dades enlloc — no pot, perquè no té on."),
      ("Sense subscripció. Mai.", "Sense quotes mensuals ni anuals.", "Vela és gratuïta avui. En el futur hi haurà una versió Pro de pagament únic — mai una subscripció."),
      ("Accessible de sèrie", "VoiceOver, Dynamic Type, Reduce Motion", "i 9 idiomes: castellà, català, èuscar, gallec, English, français, Deutsch, italiano i português."),
    ],
    "showcase_eyebrow": "Al teu canell", "showcase_h2": "Un score, un estat, una tendència.",
    "showcase_p": "El color i l'etiqueta de text sempre van junts — pensat també per a qui no distingeix bé els colors. Cada score s'explica: quin rang és «Normal», quan passa a «Alt» i per què.",
    "showcase_alt": "Tres pantalles de Vela a l'Apple Watch Ultra: score d'estrès actual amb estat Normal, tendència setmanal amb la mitjana del dia, i pantalla d'explicació dels rangs Normal i Alt.",
    "tour_eyebrow": "Recorregut ràpid", "tour_h2": "Tres pantalles, cadascuna amb una única feina.",
    "tour": [
      ("Score actual", "Un número, un estat, calculat íntegrament al rellotge — sense esperar que res se sincronitzi.", "Pantalla principal de Vela mostrant un score d'estrès de 68, estat Normal, calculat en el moment."),
      ("Tendència", "Cada lectura del dia, comparada amb la teva pròpia línia discontínua — no amb la de ningú més.", "Gràfic de tendència amb la mitjana d'estrès del dia i les lectures de cada hora, comparades amb la línia base personal."),
      ("Rangs explicats", "Res de xifres críptiques: cada rang diu què significa i què esperar-ne.", "Pantalla d'explicació dels rangs d'estrès: Normal entre 40 i 69, Alt entre 70 i 100."),
    ],
    "onboarding_eyebrow": "Així comences", "onboarding_h2": "Et demanem permís abans de mesurar res.",
    "onboarding_p": "Vela demana accés al teu HRV de manera explícita, no en la lletra petita. I si ets nou mesurant HRV, et diu quant falta per tenir una línia base fiable — sense fingir que el primer dia ja sap qui ets.",
    "onboarding_alt": "Flux de benvinguda de Vela a l'Apple Watch: pantalla de benvinguda, sol·licitud explícita d'accés a les dades de variabilitat cardíaca, i pantalla de construcció de la línia base amb 7 dies restants.",
    "closing_eyebrow": "Descarrega-la avui", "closing_h2": "Sense subscripció. <em>Mai.</em>",
    "closing_p": "Vela està disponible gratis a l'App Store per a l'Apple Watch.",
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
    ("Zein baimen behar ditu Velak?", "Velak HealthKit-erako sarbidea eskatzen du, zure Apple Watch-ak dagoeneko automatikoki biltzen dituen bihotz-maiztasunaren aldakortasunaren datuak irakurtzeko."),
  ],
  "contact_h": "Kontaktua eta laguntza",
  "contact_p": "Galderaren bat duzu, errore bat aurkitu duzu edo feedbacka partekatu nahi duzu? Idatzi zuzenean.",
  "privacy": {
    "title_tag": "Vela HRV — Pribatutasun-politika", "title": "Pribatutasun-politika",
    "updated": "Azken eguneratzea: 2026ko apirila",
    "highlight": "Velak ez du datu pertsonalik biltzen, transmititzen edo kanpoko zerbitzarietan gordetzen. Dena zure gailuan eta zure iCloud pribatuan geratzen da.",
    "sections": [
      ("Zein datu erabiltzen ditu Velak", [
        "Velak bihotz-maiztasunaren aldakortasunaren (HRV) datuak irakurtzen ditu Apple HealthKit-etik, zure estres-puntuazio pertsonala kalkulatzeko. Datu horiek zure Apple Watch-ak automatikoki biltzen ditu dagoeneko.",
        "Velak kalkulatzen dituen irakurketak ere gordetzen ditu — zure estres-puntuazioaren historiala, zure HRV oinarri-lerro pertsonala eta hura kalkulatzeko erabilitako HRV lagin gordinak."]),
      ("Non bizi dira zure datuak", [
        "Datu guztiak zure Apple Watch-ean gordetzen dira lokalki, eta modu pribatuan sinkronizatzen dira zure iCloud kontuaren bidez, Apple-ren CloudKit framework-a erabiliz. Velak ez du zerbitzaririk. Daturik ez da inoiz pasatzen Velaren jabetzako sistemetatik.",
        "Zuk bakarrik atzi ditzakezu zure datuak. Ez guk, ez hirugarrenek."]),
      ("Hirugarrenak", [
        "Velak ez du daturik partekatzen hirugarrenekin. Ez dugu analitika-zerbitzurik, publizitate-SDKrik edo kanpoko jarraipen-tresnarik erabiltzen."]),
      ("Osasun-datuak", [
        "Velak osasun-datuak bere oinarrizko funtzionaltasuna eskaintzeko bakarrik atzitzen ditu — zure estres-maila neurtzea eta jarraitzea. Osasun-datuak ez dira inoiz publizitaterako erabiltzen, ezta inori saltzen ere."]),
      ("Adingabeak", [
        "Vela ez dago 13 urtetik beherakoei zuzenduta, eta ez du haien daturik nahita biltzen."]),
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
    "wave_kicker": "SDNN · ZUZENEAN", "wave_state": "ATSEDENEAN",
    "wave_left": "populazioaren zarata", "wave_right_html": "<b>zure oinarri-lerroa</b> finkatzen",
    "baseline_eyebrow": "Zergatik ez duen batez bestekoak balio",
    "baseline_h2": "25&nbsp;ms-ko HRV altua izan daiteke zuretzat eta baxua beste norbaitentzat.",
    "baseline_p": "HRV asko aldatzen da pertsonen artean. Populazio-atalase batek denak berdin tratatzen ditu — eta horregatik huts egiten du ia beti. Velak zure oinarri-lerro propioa eraikitzen du zure benetako historialetik abiatuta: dagoeneko HRV daturik baduzu Apple Watch-en, lehen egunetik has daiteke; berria bazara, 7-14 egun behar ditu finkatzeko.",
    "legend1": "Populazioaren atalase generikoa", "legend2": "Banakako laginak", "legend3": "Zure oinarri-lerro pertsonala",
    "principles_eyebrow": "Nola funtzionatzen duen", "principles_h2": "Lau erabaki, iritziz ez aldatzeko hartuak.",
    "principles": [
      ("On-device", "Kalkulu guztia zure Watch-ean gertatzen da.", "HealthKitek datuak ematen ditu, erlojuak gainerakoa egiten du. HRV daturik ez da inoiz zure gailutik ateratzen Velaren zerbitzari batera."),
      ("Zure iCloud, ez gurea", "Sinkronizazioak zure iCloud kontu propioa erabiltzen du", "CloudKit bidez. Velak ez ditu zure datuak inon gordetzen — ezin du, ez baitu non."),
      ("Harpidetzarik gabe. Inoiz ez.", "Hileroko edo urteroko kuotarik gabe.", "Vela gaur doakoa da. Etorkizunean ordainpeko Pro bertsio bat egongo da — inoiz ez harpidetza bat."),
      ("Berez irisgarria", "VoiceOver, Dynamic Type, Reduce Motion", "eta 9 hizkuntza: gaztelania, katalana, euskara, galiziera, English, français, Deutsch, italiano eta português."),
    ],
    "showcase_eyebrow": "Zure eskumuturrean", "showcase_h2": "Puntuazio bat, egoera bat, joera bat.",
    "showcase_p": "Kolorea eta testu-etiketa beti batera doaz — kolore-itsutasuna kontuan hartuta ere. Puntuazio bakoitza azaltzen da: zein tarte den «Normal», noiz bihurtzen den «Altu» eta zergatik.",
    "showcase_alt": "Velaren hiru pantaila Apple Watch Ultran: uneko estres-puntuazioa Normal egoerarekin, asteko joera egunaren batez bestekoarekin, eta Normal eta Altu tarteak azaltzen dituen pantaila.",
    "tour_eyebrow": "Bira azkarra", "tour_h2": "Hiru pantaila, bakoitza lan bakar batekin.",
    "tour": [
      ("Uneko puntuazioa", "Zenbaki bat, egoera bat, erlojuan bertan kalkulatua — ezer sinkronizatzeko itxaron gabe.", "Velaren pantaila nagusia, 68ko estres-puntuazioa eta Normal egoera erakusten, unean kalkulatua."),
      ("Joera", "Eguneko irakurketa bakoitza, zure marra etenarekin alderatuta — ez beste inorenarekin.", "Joera-grafikoa eguneko estres-batez bestekoarekin eta orduroko irakurketekin, oinarri-lerro pertsonalarekin alderatuta."),
      ("Tarteak azalduta", "Zifra kriptikorik ez: tarte bakoitzak esan nahi duena eta zer espero eskaintzen du.", "Estres-tarteak azaltzen dituen pantaila: Normal 40 eta 69 artean, Altu 70 eta 100 artean."),
    ],
    "onboarding_eyebrow": "Horrela hasten zara", "onboarding_h2": "Baimena eskatzen dizugu ezer neurtu aurretik.",
    "onboarding_p": "Velak zure HRVrako sarbidea modu esplizituan eskatzen du, ez letra txikian. Eta HRV neurtzen berria bazara, oinarri-lerro fidagarri bat izateko zenbat falta den esaten dizu — lehen egunetik nor zaren jakingo balu bezala itxuratu gabe.",
    "onboarding_alt": "Velaren ongietorri-fluxua Apple Watch-en: ongietorri-pantaila, bihotz-maiztasunaren aldakortasun-datuetarako sarbidearen eskaera esplizitua, eta 7 egun falta direla erakusten duen oinarri-lerroa eraikitzeko pantaila.",
    "closing_eyebrow": "Deskargatu gaur", "closing_h2": "Harpidetzarik gabe. <em>Inoiz ez.</em>",
    "closing_p": "Vela doan dago eskuragarri App Store-n, Apple Watch-erako.",
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
    ("Que permisos necesita Vela?", "Vela solicita acceso a HealthKit para ler os datos de variabilidade da frecuencia cardíaca que o teu Apple Watch xa recolle automaticamente."),
  ],
  "contact_h": "Contacto e soporte",
  "contact_p": "Tes algunha pregunta, atopaches un erro ou queres compartir feedback? Escríbenos directamente.",
  "privacy": {
    "title_tag": "Vela HRV — Política de privacidade", "title": "Política de privacidade",
    "updated": "Última actualización: abril 2026",
    "highlight": "Vela non recolle, transmite nin almacena ningún dato persoal en servidores externos. Todo queda no teu dispositivo e no teu iCloud privado.",
    "sections": [
      ("Que datos usa Vela", [
        "Vela le datos de variabilidade da frecuencia cardíaca (HRV) de Apple HealthKit para calcular a túa puntuación de estrés persoal. Estes datos xa os recolle automaticamente o teu Apple Watch.",
        "Vela tamén almacena as lecturas que calcula — o historial da túa puntuación de estrés, a túa liña base de HRV persoal e as mostras de HRV en bruto usadas para calculala."]),
      ("Onde viven os teus datos", [
        "Todos os datos almacénanse localmente no teu Apple Watch e sincronízanse de forma privada a través da túa propia conta de iCloud mediante o framework CloudKit de Apple. Vela non ten servidores. Ningún dato pasa nunca por sistemas propiedade de Vela.",
        "Só ti podes acceder aos teus datos. Nin nós, nin terceiros."]),
      ("Terceiros", [
        "Vela non comparte ningún dato con terceiros. Non usamos servizos de analítica, SDK publicitarios nin ningunha ferramenta de seguimento externa."]),
      ("Datos de saúde", [
        "Vela accede aos datos de saúde unicamente para ofrecer a súa funcionalidade principal — medir e seguir o teu nivel de estrés. Os datos de saúde nunca se usan para publicidade nin se venden a ninguén."]),
      ("Menores", [
        "Vela non está dirixida a menores de 13 anos e non recolle deliberadamente datos deles."]),
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
    "wave_kicker": "SDNN · EN TEMPO REAL", "wave_state": "EN REPOUSO",
    "wave_left": "ruído de poboación", "wave_right_html": "<b>a túa liña base</b> aséntase",
    "baseline_eyebrow": "Por que a media non serve",
    "baseline_h2": "25&nbsp;ms de HRV pode ser alto para ti e baixo para outra persoa.",
    "baseline_p": "A HRV varía enormemente entre persoas. Un limiar de poboación trata a todos igual — e por iso case sempre falla. Vela constrúe a túa propia liña base a partir do teu historial real: se xa tes datos de HRV no teu Apple Watch, pode empezar dende o primeiro día; se es novo, tarda entre 7 e 14 días en asentarse.",
    "legend1": "Limiar xenérico de poboación", "legend2": "Mostras individuais", "legend3": "A túa liña base persoal",
    "principles_eyebrow": "Como funciona", "principles_h2": "Catro decisións, tomadas para non cambiar de opinión.",
    "principles": [
      ("On-device", "Todo o cálculo ocorre no teu Watch.", "HealthKit entrega os datos, o reloxo fai o resto. Ningún dato de HRV sae do teu dispositivo cara a un servidor de Vela."),
      ("O teu iCloud, non o noso", "A sincronización usa a túa propia conta de iCloud", "vía CloudKit. Vela non aloxa os teus datos en ningures — non pode, porque non ten onde."),
      ("Sen subscrición. Nunca.", "Sen cotas mensuais nin anuais.", "Vela é gratis hoxe. No futuro haberá unha versión Pro de pago único — nunca unha subscrición."),
      ("Accesible de serie", "VoiceOver, Dynamic Type, Reduce Motion", "e 9 idiomas: castelán, catalán, éuscaro, galego, English, français, Deutsch, italiano e português."),
    ],
    "showcase_eyebrow": "No teu pulso", "showcase_h2": "Unha puntuación, un estado, unha tendencia.",
    "showcase_p": "A cor e a etiqueta de texto van sempre xuntas — pensado tamén para quen non distingue ben as cores. Cada puntuación explícase: que rango é «Normal», cando pasa a «Alto» e por que.",
    "showcase_alt": "Tres pantallas de Vela no Apple Watch Ultra: puntuación de estrés actual con estado Normal, tendencia semanal coa media do día, e pantalla de explicación dos rangos Normal e Alto.",
    "tour_eyebrow": "Percorrido rápido", "tour_h2": "Tres pantallas, cada unha cun único traballo.",
    "tour": [
      ("Puntuación actual", "Un número, un estado, calculado enteiramente no reloxo — sen esperar a que nada sincronice.", "Pantalla principal de Vela amosando unha puntuación de estrés de 68, estado Normal, calculado no momento."),
      ("Tendencia", "Cada lectura do día, comparada coa túa propia liña discontinua — non coa de ninguén máis.", "Gráfico de tendencia coa media de estrés do día e as lecturas de cada hora, comparadas coa liña base persoal."),
      ("Rangos explicados", "Nada de cifras crípticas: cada rango di que significa e que esperar del.", "Pantalla de explicación dos rangos de estrés: Normal entre 40 e 69, Alto entre 70 e 100."),
    ],
    "onboarding_eyebrow": "Así comezas", "onboarding_h2": "Pedímosche permiso antes de medir nada.",
    "onboarding_p": "Vela pide acceso á túa HRV de forma explícita, non na letra pequena. E se es novo medindo HRV, dicheche canto falta para ter unha liña base fiable — sen finxir que o primeiro día xa sabe quen es.",
    "onboarding_alt": "Fluxo de benvida de Vela no Apple Watch: pantalla de benvida, solicitude explícita de acceso aos datos de variabilidade cardíaca, e pantalla de construción da liña base con 7 días restantes.",
    "closing_eyebrow": "Descárgaa hoxe", "closing_h2": "Sen subscrición. <em>Nunca.</em>",
    "closing_p": "Vela está dispoñible gratis na App Store para Apple Watch.",
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
    ("Quelles autorisations Vela demande-t-elle ?", "Vela demande l'accès à HealthKit pour lire les données de variabilité de la fréquence cardiaque que votre Apple Watch collecte déjà automatiquement."),
  ],
  "contact_h": "Contact et assistance",
  "contact_p": "Une question, un bug ou un retour à partager ? Écrivez-nous directement.",
  "privacy": {
    "title_tag": "Vela HRV — Politique de confidentialité", "title": "Politique de confidentialité",
    "updated": "Dernière mise à jour : avril 2026",
    "highlight": "Vela ne collecte, ne transmet et ne stocke aucune donnée personnelle sur des serveurs externes. Tout reste sur votre appareil et dans votre iCloud privé.",
    "sections": [
      ("Quelles données Vela utilise", [
        "Vela lit les données de variabilité de la fréquence cardiaque (VFC) d'Apple HealthKit pour calculer votre score de stress personnel. Ces données sont déjà collectées automatiquement par votre Apple Watch.",
        "Vela stocke également les mesures qu'elle calcule — l'historique de votre score de stress, votre référence VFC personnelle et les échantillons VFC bruts utilisés pour la calculer."]),
      ("Où vivent vos données", [
        "Toutes les données sont stockées localement sur votre Apple Watch et synchronisées de manière privée via votre propre compte iCloud, grâce au framework CloudKit d'Apple. Vela n'a pas de serveurs. Aucune donnée ne transite jamais par des systèmes appartenant à Vela.",
        "Vous seul pouvez accéder à vos données. Ni nous, ni des tiers."]),
      ("Tiers", [
        "Vela ne partage aucune donnée avec des tiers. Nous n'utilisons aucun service d'analyse, aucun SDK publicitaire ni aucun outil de suivi externe."]),
      ("Données de santé", [
        "Vela accède aux données de santé uniquement pour offrir sa fonctionnalité principale — mesurer et suivre votre niveau de stress. Les données de santé ne sont jamais utilisées à des fins publicitaires ni vendues à qui que ce soit."]),
      ("Enfants", [
        "Vela ne s'adresse pas aux enfants de moins de 13 ans et ne collecte pas sciemment leurs données."]),
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
    "wave_kicker": "VFC · EN DIRECT", "wave_state": "AU REPOS",
    "wave_left": "bruit de population", "wave_right_html": "<b>votre référence</b> se stabilise",
    "baseline_eyebrow": "Pourquoi la moyenne ne fonctionne pas",
    "baseline_h2": "25&nbsp;ms de VFC peut être élevé pour vous et bas pour quelqu'un d'autre.",
    "baseline_p": "La VFC varie énormément d'une personne à l'autre. Un seuil de population traite tout le monde de la même façon — et c'est précisément pour ça qu'il se trompe presque toujours. Vela construit votre propre référence à partir de votre historique réel : si vous avez déjà des données VFC sur votre Apple Watch, elle peut démarrer dès le premier jour ; si vous êtes nouveau, il faut 7 à 14 jours pour qu'elle se stabilise.",
    "legend1": "Seuil générique de population", "legend2": "Échantillons individuels", "legend3": "Votre référence personnelle",
    "principles_eyebrow": "Comment ça marche", "principles_h2": "Quatre décisions, prises pour ne pas changer d'avis.",
    "principles": [
      ("On-device", "Tout le calcul se fait sur votre Watch.", "HealthKit fournit les données, la montre fait le reste. Aucune donnée VFC ne quitte jamais votre appareil vers un serveur Vela."),
      ("Votre iCloud, pas le nôtre", "La synchronisation utilise votre propre compte iCloud", "via CloudKit. Vela n'héberge vos données nulle part — elle ne peut pas, faute d'endroit où les mettre."),
      ("Sans abonnement. Jamais.", "Aucun frais mensuel ni annuel.", "Vela est gratuite aujourd'hui. Une version Pro à paiement unique arrivera plus tard — jamais un abonnement."),
      ("Accessible par défaut", "VoiceOver, Dynamic Type, Reduce Motion", "et 9 langues : espagnol, catalan, basque, galicien, anglais, français, allemand, italien et portugais."),
    ],
    "showcase_eyebrow": "À votre poignet", "showcase_h2": "Un score, un état, une tendance.",
    "showcase_p": "La couleur et l'étiquette textuelle vont toujours ensemble — pensé aussi pour les personnes daltoniennes. Chaque score est expliqué : quelle plage est « Normale », quand elle devient « Élevée », et pourquoi.",
    "showcase_alt": "Trois écrans de Vela sur Apple Watch Ultra : score de stress actuel avec statut Normal, tendance hebdomadaire avec la moyenne du jour, et un écran expliquant les plages Normale et Élevée.",
    "tour_eyebrow": "Visite rapide", "tour_h2": "Trois écrans, chacun avec un seul rôle.",
    "tour": [
      ("Score actuel", "Un chiffre, un état, calculé entièrement sur la montre — sans attendre la moindre synchronisation.", "Écran principal de Vela affichant un score de stress de 68, statut Normal, calculé à l'instant."),
      ("Tendance", "Chaque mesure de la journée, comparée à votre propre ligne pointillée — pas à celle de quelqu'un d'autre.", "Graphique de tendance avec la moyenne de stress du jour et les mesures horaires, comparées à la référence personnelle."),
      ("Plages expliquées", "Fini les chiffres cryptiques : chaque plage indique ce qu'elle signifie et ce à quoi s'attendre.", "Écran expliquant les plages de stress : Normale entre 40 et 69, Élevée entre 70 et 100."),
    ],
    "onboarding_eyebrow": "Comment ça démarre", "onboarding_h2": "Nous demandons la permission avant de mesurer quoi que ce soit.",
    "onboarding_p": "Vela demande l'accès à votre VFC de façon explicite, pas dans les petits caractères. Et si vous débutez avec la mesure de la VFC, elle vous indique combien de temps il reste avant d'avoir une référence fiable — sans prétendre savoir qui vous êtes dès le premier jour.",
    "onboarding_alt": "Parcours d'accueil de Vela sur Apple Watch : écran de bienvenue, demande explicite d'accès aux données de variabilité de la fréquence cardiaque, et écran de construction de la référence indiquant 7 jours restants.",
    "closing_eyebrow": "Téléchargez-la aujourd'hui", "closing_h2": "Sans abonnement. <em>Jamais.</em>",
    "closing_p": "Vela est disponible gratuitement sur l'App Store pour Apple Watch.",
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
    ("Welche Berechtigungen braucht Vela?", "Vela bittet um Zugriff auf HealthKit, um die Herzfrequenzvariabilitätsdaten zu lesen, die deine Apple Watch bereits automatisch erfasst."),
  ],
  "contact_h": "Kontakt & Support",
  "contact_p": "Du hast eine Frage, einen Fehler gefunden oder Feedback? Schreib uns direkt.",
  "privacy": {
    "title_tag": "Vela HRV — Datenschutzerklärung", "title": "Datenschutzerklärung",
    "updated": "Zuletzt aktualisiert: April 2026",
    "highlight": "Vela erhebt, überträgt und speichert keinerlei personenbezogene Daten auf externen Servern. Alles bleibt auf deinem Gerät und in deiner privaten iCloud.",
    "sections": [
      ("Welche Daten Vela nutzt", [
        "Vela liest Herzfrequenzvariabilitätsdaten (HRV) aus Apple HealthKit, um deinen persönlichen Stress-Score zu berechnen. Diese Daten erfasst deine Apple Watch bereits automatisch.",
        "Vela speichert außerdem die berechneten Messungen — den Verlauf deines Stress-Scores, deine persönliche HRV-Baseline und die HRV-Rohdaten, aus denen sie berechnet wird."]),
      ("Wo deine Daten liegen", [
        "Alle Daten werden lokal auf deiner Apple Watch gespeichert und privat über deinen eigenen iCloud-Account mit Apples CloudKit-Framework synchronisiert. Vela hat keine Server. Keine Daten laufen jemals über Systeme, die Vela gehören oder von Vela betrieben werden.",
        "Nur du kannst auf deine Daten zugreifen. Weder wir noch Dritte."]),
      ("Dritte", [
        "Vela teilt keine Daten mit Dritten. Wir verwenden keine Analysedienste, keine Werbe-SDKs und keine externen Tracking-Tools."]),
      ("Gesundheitsdaten", [
        "Vela greift auf Gesundheitsdaten ausschließlich zu, um seine Kernfunktion zu erfüllen — dein Stressniveau zu messen und zu verfolgen. Gesundheitsdaten werden niemals für Werbung genutzt oder an Dritte verkauft."]),
      ("Kinder", [
        "Vela richtet sich nicht an Kinder unter 13 Jahren und erhebt wissentlich keine Daten von ihnen."]),
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
    "wave_kicker": "SDNN · LIVE", "wave_state": "IN RUHE",
    "wave_left": "Bevölkerungsrauschen", "wave_right_html": "<b>deine Baseline</b> stabilisiert sich",
    "baseline_eyebrow": "Warum der Durchschnitt nicht funktioniert",
    "baseline_h2": "25&nbsp;ms HRV können für dich hoch und für jemand anderen niedrig sein.",
    "baseline_p": "HRV variiert enorm zwischen Menschen. Ein Bevölkerungsschwellenwert behandelt alle gleich — und liegt genau deshalb fast immer falsch. Vela erstellt deine eigene Baseline aus deiner echten Historie: Hast du bereits HRV-Daten auf deiner Apple Watch, kann sie ab Tag eins starten; bist du neu, dauert es 7–14 Tage, bis sie sich stabilisiert.",
    "legend1": "Generischer Bevölkerungsschwellenwert", "legend2": "Einzelne Messwerte", "legend3": "Deine persönliche Baseline",
    "principles_eyebrow": "So funktioniert's", "principles_h2": "Vier Entscheidungen, getroffen, um sie nicht mehr zu ändern.",
    "principles": [
      ("On-device", "Die gesamte Berechnung läuft auf deiner Watch.", "HealthKit liefert die Daten, die Uhr erledigt den Rest. Keine HRV-Daten verlassen jemals dein Gerät in Richtung eines Vela-Servers."),
      ("Deine iCloud, nicht unsere", "Die Synchronisierung nutzt dein eigenes iCloud-Konto", "über CloudKit. Vela speichert deine Daten nirgendwo — das kann es gar nicht, weil es keinen Ort dafür hat."),
      ("Kein Abo. Niemals.", "Keine monatlichen oder jährlichen Gebühren.", "Vela ist heute kostenlos. In Zukunft wird es eine kostenpflichtige Pro-Version mit Einmalzahlung geben — niemals ein Abo."),
      ("Barrierefrei von Haus aus", "VoiceOver, Dynamic Type, Reduce Motion", "und 9 Sprachen: Spanisch, Katalanisch, Baskisch, Galicisch, Englisch, Französisch, Deutsch, Italienisch und Portugiesisch."),
    ],
    "showcase_eyebrow": "An deinem Handgelenk", "showcase_h2": "Ein Score, ein Zustand, ein Trend.",
    "showcase_p": "Farbe und Textlabel gehören immer zusammen — auch für Menschen mit Farbsehschwäche gedacht. Jeder Score wird erklärt: welcher Bereich „Normal“ ist, wann er zu „Hoch“ wird, und warum.",
    "showcase_alt": "Drei Vela-Bildschirme auf der Apple Watch Ultra: aktueller Stress-Score mit Status Normal, Wochentrend mit Tagesdurchschnitt, und ein Bildschirm, der die Bereiche Normal und Hoch erklärt.",
    "tour_eyebrow": "Kurzer Rundgang", "tour_h2": "Drei Bildschirme, jeder mit genau einer Aufgabe.",
    "tour": [
      ("Aktueller Score", "Eine Zahl, ein Zustand, vollständig auf der Uhr berechnet — ohne auf eine Synchronisierung zu warten.", "Velas Hauptbildschirm mit einem Stress-Score von 68, Status Normal, im Moment berechnet."),
      ("Trend", "Jede Messung des Tages, verglichen mit deiner eigenen gestrichelten Linie — mit niemand anderem.", "Trenddiagramm mit dem Tagesdurchschnitt des Stresses und stündlichen Messwerten, verglichen mit der persönlichen Baseline."),
      ("Bereiche erklärt", "Keine kryptischen Zahlen: Jeder Bereich sagt, was er bedeutet und was zu erwarten ist.", "Bildschirm, der die Stressbereiche erklärt: Normal zwischen 40 und 69, Hoch zwischen 70 und 100."),
    ],
    "onboarding_eyebrow": "So startest du", "onboarding_h2": "Wir fragen um Erlaubnis, bevor wir irgendetwas messen.",
    "onboarding_p": "Vela bittet ausdrücklich um Zugriff auf deine HRV — nicht im Kleingedruckten. Und wenn du neu im Messen von HRV bist, sagt dir Vela, wie lange es noch dauert, bis du eine verlässliche Baseline hast — ohne so zu tun, als würde es dich schon am ersten Tag kennen.",
    "onboarding_alt": "Velas Onboarding-Ablauf auf der Apple Watch: ein Willkommensbildschirm, eine ausdrückliche Zugriffsanfrage für Herzfrequenzvariabilitätsdaten und ein Bildschirm zum Aufbau der Baseline mit noch 7 verbleibenden Tagen.",
    "closing_eyebrow": "Heute herunterladen", "closing_h2": "Kein Abo. <em>Niemals.</em>",
    "closing_p": "Vela ist kostenlos im App Store für Apple Watch erhältlich.",
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
    ("Quali permessi richiede Vela?", "Vela richiede l'accesso a HealthKit per leggere i dati di variabilità della frequenza cardiaca che il tuo Apple Watch raccoglie già automaticamente."),
  ],
  "contact_h": "Contatti e supporto",
  "contact_p": "Hai una domanda, hai trovato un bug o vuoi condividere un feedback? Scrivici direttamente.",
  "privacy": {
    "title_tag": "Vela HRV — Informativa sulla privacy", "title": "Informativa sulla privacy",
    "updated": "Ultimo aggiornamento: aprile 2026",
    "highlight": "Vela non raccoglie, trasmette né conserva alcun dato personale su server esterni. Tutto resta sul tuo dispositivo e nel tuo iCloud privato.",
    "sections": [
      ("Quali dati usa Vela", [
        "Vela legge i dati di variabilità della frequenza cardiaca (HRV) da Apple HealthKit per calcolare il tuo punteggio di stress personale. Questi dati vengono già raccolti automaticamente dal tuo Apple Watch.",
        "Vela conserva anche le misurazioni che calcola — lo storico del tuo punteggio di stress, la tua baseline HRV personale e i campioni HRV grezzi usati per calcolarla."]),
      ("Dove vivono i tuoi dati", [
        "Tutti i dati sono conservati localmente sul tuo Apple Watch e sincronizzati in modo privato tramite il tuo account iCloud con il framework CloudKit di Apple. Vela non ha server. Nessun dato passa mai per sistemi di proprietà di Vela.",
        "Solo tu puoi accedere ai tuoi dati. Né noi, né terze parti."]),
      ("Terze parti", [
        "Vela non condivide alcun dato con terze parti. Non usiamo servizi di analisi, SDK pubblicitari né strumenti di tracciamento esterni."]),
      ("Dati sanitari", [
        "Vela accede ai dati sanitari esclusivamente per offrire la sua funzionalità principale — misurare e monitorare il tuo livello di stress. I dati sanitari non vengono mai usati per pubblicità né venduti a nessuno."]),
      ("Minori", [
        "Vela non è rivolta a minori di 13 anni e non raccoglie consapevolmente i loro dati."]),
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
    "wave_kicker": "SDNN · IN TEMPO REALE", "wave_state": "A RIPOSO",
    "wave_left": "rumore di popolazione", "wave_right_html": "<b>la tua baseline</b> si assesta",
    "baseline_eyebrow": "Perché la media non funziona",
    "baseline_h2": "25&nbsp;ms di HRV può essere alto per te e basso per un'altra persona.",
    "baseline_p": "L'HRV varia enormemente da persona a persona. Una soglia di popolazione tratta tutti allo stesso modo — ed è proprio per questo che quasi sempre sbaglia. Vela costruisce la tua baseline a partire dalla tua storia reale: se hai già dati HRV sul tuo Apple Watch, può partire dal primo giorno; se sei nuovo, ci vogliono 7–14 giorni per assestarsi.",
    "legend1": "Soglia generica di popolazione", "legend2": "Campioni individuali", "legend3": "La tua baseline personale",
    "principles_eyebrow": "Come funziona", "principles_h2": "Quattro decisioni, prese per non cambiare idea.",
    "principles": [
      ("On-device", "Tutto il calcolo avviene sul tuo Watch.", "HealthKit fornisce i dati, l'orologio fa il resto. Nessun dato HRV lascia mai il tuo dispositivo verso un server Vela."),
      ("Il tuo iCloud, non il nostro", "La sincronizzazione usa il tuo account iCloud", "tramite CloudKit. Vela non ospita i tuoi dati da nessuna parte — non può, perché non ha dove."),
      ("Senza abbonamento. Mai.", "Nessuna quota mensile o annuale.", "Vela è gratis oggi. In futuro ci sarà una versione Pro a pagamento unico — mai un abbonamento."),
      ("Accessibile di serie", "VoiceOver, Dynamic Type, Reduce Motion", "e 9 lingue: spagnolo, catalano, basco, galiziano, inglese, francese, tedesco, italiano e portoghese."),
    ],
    "showcase_eyebrow": "Al tuo polso", "showcase_h2": "Un punteggio, uno stato, una tendenza.",
    "showcase_p": "Colore ed etichetta testuale vanno sempre insieme — pensato anche per chi non distingue bene i colori. Ogni punteggio è spiegato: quale intervallo è «Normale», quando diventa «Alto» e perché.",
    "showcase_alt": "Tre schermate di Vela su Apple Watch Ultra: punteggio di stress attuale con stato Normale, tendenza settimanale con la media del giorno, e una schermata che spiega gli intervalli Normale e Alto.",
    "tour_eyebrow": "Tour rapido", "tour_h2": "Tre schermate, ognuna con un solo compito.",
    "tour": [
      ("Punteggio attuale", "Un numero, uno stato, calcolato interamente sull'orologio — senza aspettare alcuna sincronizzazione.", "Schermata principale di Vela con un punteggio di stress di 68, stato Normale, calcolato al momento."),
      ("Tendenza", "Ogni rilevazione del giorno, confrontata con la tua linea tratteggiata — non con quella di nessun altro.", "Grafico della tendenza con la media di stress del giorno e le rilevazioni orarie, confrontate con la baseline personale."),
      ("Intervalli spiegati", "Niente numeri criptici: ogni intervallo dice cosa significa e cosa aspettarsi.", "Schermata che spiega gli intervalli di stress: Normale tra 40 e 69, Alto tra 70 e 100."),
    ],
    "onboarding_eyebrow": "Così inizi", "onboarding_h2": "Ti chiediamo il permesso prima di misurare qualsiasi cosa.",
    "onboarding_p": "Vela chiede l'accesso alla tua HRV in modo esplicito, non nelle note in piccolo. E se sei nuovo nella misurazione dell'HRV, ti dice quanto manca per avere una baseline affidabile — senza fingere di sapere già chi sei il primo giorno.",
    "onboarding_alt": "Flusso di benvenuto di Vela su Apple Watch: schermata di benvenuto, richiesta esplicita di accesso ai dati di variabilità della frequenza cardiaca, e schermata di costruzione della baseline con 7 giorni rimanenti.",
    "closing_eyebrow": "Scaricala oggi", "closing_h2": "Senza abbonamento. <em>Mai.</em>",
    "closing_p": "Vela è disponibile gratuitamente su App Store per Apple Watch.",
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
    ("Que permissões precisa a Vela?", "A Vela pede acesso ao HealthKit para ler os dados de variabilidade da frequência cardíaca que o seu Apple Watch já recolhe automaticamente."),
  ],
  "contact_h": "Contacto e suporte",
  "contact_p": "Tem alguma pergunta, encontrou um erro ou quer partilhar feedback? Escreva-nos diretamente.",
  "privacy": {
    "title_tag": "Vela HRV — Política de privacidade", "title": "Política de privacidade",
    "updated": "Última atualização: abril de 2026",
    "highlight": "A Vela não recolhe, transmite nem armazena quaisquer dados pessoais em servidores externos. Tudo fica no seu dispositivo e no seu iCloud privado.",
    "sections": [
      ("Que dados usa a Vela", [
        "A Vela lê dados de variabilidade da frequência cardíaca (HRV) do Apple HealthKit para calcular a sua pontuação de stress pessoal. Estes dados já são recolhidos automaticamente pelo seu Apple Watch.",
        "A Vela também guarda as leituras que calcula — o histórico da sua pontuação de stress, a sua linha de base de HRV pessoal e as amostras de HRV em bruto usadas para a calcular."]),
      ("Onde vivem os seus dados", [
        "Todos os dados são guardados localmente no seu Apple Watch e sincronizados de forma privada através da sua própria conta iCloud, com o framework CloudKit da Apple. A Vela não tem servidores. Nenhum dado passa alguma vez por sistemas detidos ou operados pela Vela.",
        "Só você pode aceder aos seus dados. Nem nós, nem terceiros."]),
      ("Terceiros", [
        "A Vela não partilha quaisquer dados com terceiros. Não usamos serviços de análise, SDK de publicidade nem ferramentas de rastreio externas."]),
      ("Dados de saúde", [
        "A Vela acede aos dados de saúde exclusivamente para oferecer a sua funcionalidade principal — medir e acompanhar o seu nível de stress. Os dados de saúde nunca são usados para publicidade nem vendidos a ninguém."]),
      ("Crianças", [
        "A Vela não se destina a crianças com menos de 13 anos e não recolhe conscientemente dados delas."]),
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
    "wave_kicker": "SDNN · EM TEMPO REAL", "wave_state": "EM REPOUSO",
    "wave_left": "ruído de população", "wave_right_html": "<b>a sua linha de base</b> assenta",
    "baseline_eyebrow": "Porque é que a média não serve",
    "baseline_h2": "25&nbsp;ms de HRV pode ser alto para si e baixo para outra pessoa.",
    "baseline_p": "A HRV varia enormemente entre pessoas. Um limiar de população trata todos da mesma forma — e é precisamente por isso que quase sempre falha. A Vela constrói a sua própria linha de base a partir do seu histórico real: se já tem dados de HRV no seu Apple Watch, pode começar desde o primeiro dia; se é novo, demora entre 7 e 14 dias a assentar.",
    "legend1": "Limiar genérico de população", "legend2": "Amostras individuais", "legend3": "A sua linha de base pessoal",
    "principles_eyebrow": "Como funciona", "principles_h2": "Quatro decisões, tomadas para não mudar de ideias.",
    "principles": [
      ("On-device", "Todo o cálculo acontece no seu Watch.", "O HealthKit fornece os dados, o relógio faz o resto. Nenhum dado de HRV sai do seu dispositivo em direção a um servidor da Vela."),
      ("O seu iCloud, não o nosso", "A sincronização usa a sua própria conta iCloud", "via CloudKit. A Vela não aloja os seus dados em lado nenhum — não pode, porque não tem onde."),
      ("Sem subscrição. Nunca.", "Sem quotas mensais nem anuais.", "A Vela é gratuita hoje. No futuro haverá uma versão Pro de pagamento único — nunca uma subscrição."),
      ("Acessível por predefinição", "VoiceOver, Dynamic Type, Reduce Motion", "e 9 idiomas: castelhano, catalão, basco, galego, inglês, francês, alemão, italiano e português."),
    ],
    "showcase_eyebrow": "No seu pulso", "showcase_h2": "Uma pontuação, um estado, uma tendência.",
    "showcase_p": "A cor e a etiqueta de texto andam sempre juntas — pensado também para quem não distingue bem as cores. Cada pontuação é explicada: que intervalo é «Normal», quando passa a «Alto» e porquê.",
    "showcase_alt": "Três ecrãs da Vela no Apple Watch Ultra: pontuação de stress atual com estado Normal, tendência semanal com a média do dia, e um ecrã a explicar os intervalos Normal e Alto.",
    "tour_eyebrow": "Percurso rápido", "tour_h2": "Três ecrãs, cada um com uma única função.",
    "tour": [
      ("Pontuação atual", "Um número, um estado, calculado inteiramente no relógio — sem esperar que nada sincronize.", "Ecrã principal da Vela a mostrar uma pontuação de stress de 68, estado Normal, calculado no momento."),
      ("Tendência", "Cada leitura do dia, comparada com a sua própria linha tracejada — não com a de mais ninguém.", "Gráfico de tendência com a média de stress do dia e as leituras de cada hora, comparadas com a linha de base pessoal."),
      ("Intervalos explicados", "Nada de números crípticos: cada intervalo diz o que significa e o que esperar.", "Ecrã a explicar os intervalos de stress: Normal entre 40 e 69, Alto entre 70 e 100."),
    ],
    "onboarding_eyebrow": "Assim começa", "onboarding_h2": "Pedimos permissão antes de medir seja o que for.",
    "onboarding_p": "A Vela pede acesso à sua HRV de forma explícita, não na letra pequena. E se é novo a medir HRV, diz-lhe quanto falta para ter uma linha de base fiável — sem fingir que já sabe quem é no primeiro dia.",
    "onboarding_alt": "Fluxo de boas-vindas da Vela no Apple Watch: ecrã de boas-vindas, pedido explícito de acesso aos dados de variabilidade da frequência cardíaca, e ecrã de construção da linha de base com 7 dias restantes.",
    "closing_eyebrow": "Transfira-a hoje", "closing_h2": "Sem subscrição. <em>Nunca.</em>",
    "closing_p": "A Vela está disponível gratuitamente na App Store para Apple Watch.",
    "footer_support": "Suporte", "footer_privacy": "Privacidade", "footer_contact": "Contacto",
  },
}

# ------------------------------------------------------------ generation

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  {path.relative_to(SITE)}")

def main():
    print("Generando páginas del sitio (9 idiomas x 4 páginas):")
    for code in ORDER:
        t = L[code]
        write(out_path(code, "landing"), render_landing(code, t))
        write(out_path(code, "support"), render_support(code, t))
        write(out_path(code, "privacy"), render_privacy(code, t))
        write(out_path(code, "accessibility"), render_a11y(code, t))

if __name__ == "__main__":
    main()
