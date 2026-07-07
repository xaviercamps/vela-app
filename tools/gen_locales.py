#!/usr/bin/env python3
"""Generates the vela-app site pages for the 7 new locales (ca, eu, gl, fr, de,
it, pt) from the ES/EN masters, and retrofits a footer language switcher into
the 6 existing pages. Run from anywhere; SITE is the repo root (tools/..)."""

import re
from pathlib import Path

SITE = Path(__file__).parent.parent
MAIL = "xaviercampsnovi@gmail.com"
ORDER = ["es", "en", "ca", "eu", "gl", "fr", "de", "it", "pt"]

def path_for(code: str, page: str) -> str:
    base = "/vela-app/" if code == "en" else f"/vela-app/{code}/"
    return base if page == "home" else f"{base}{page}/"

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

HOME_CSS = """    :root {
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

def footer(t, page, code):
    return f"""    <footer>
      <p>© 2026 Vela HRV · {t['rights']}</p>
      {lang_row(page, code, t['lang_label'])}
    </footer>"""

def render_home(code, t):
    faqs = "\n\n".join(
        f'''        <div class="faq-item">
          <h3>{q}</h3>
          <p>{a}</p>
        </div>'''
        for q, a in t["faq"])
    return HEAD.format(lang=code, title=t["home_title"], css=HOME_CSS) + f"""<body>
  <div class="container">
    <header>
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

{footer(t, 'home', code)}
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
      <a class="back-link" href="{path_for(code, 'home')}">{t['back']}</a>
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
      <a class="back-link" href="{path_for(code, 'home')}">{t['back']}</a>
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

# ---------------------------------------------------------------- content

L = {}

L["ca"] = {
  "lang_label": "Idioma", "back": "← Torna al suport", "rights": "Tots els drets reservats",
  "home_title": "Vela HRV — Suport",
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
    "approach_p": "Vela mesura l'estrès a través de la variabilitat de la freqüència cardíaca a l'Apple Watch. Entendre el teu propi cos no hauria de dependre de com veus, així que l'accessibilitat es tracta com una funcionalitat central: el principi rector és que una persona cega pugui consultar el seu nivell d'estrès, explorar el seu historial, llegir les seves anàlisis setmanals i configurar l'app de manera completament autònoma.",
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
}

L["eu"] = {
  "lang_label": "Hizkuntza", "back": "← Itzuli laguntzara", "rights": "Eskubide guztiak erreserbatuta",
  "home_title": "Vela HRV — Laguntza",
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
}

L["gl"] = {
  "lang_label": "Idioma", "back": "← Volver ao soporte", "rights": "Todos os dereitos reservados",
  "home_title": "Vela HRV — Soporte",
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
}

L["fr"] = {
  "lang_label": "Langue", "back": "← Retour à l'assistance", "rights": "Tous droits réservés",
  "home_title": "Vela HRV — Assistance",
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
}

L["de"] = {
  "lang_label": "Sprache", "back": "← Zurück zum Support", "rights": "Alle Rechte vorbehalten",
  "home_title": "Vela HRV — Support",
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
}

L["it"] = {
  "lang_label": "Lingua", "back": "← Torna al supporto", "rights": "Tutti i diritti riservati",
  "home_title": "Vela HRV — Supporto",
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
}

L["pt"] = {
  "lang_label": "Idioma", "back": "← Voltar ao suporte", "rights": "Todos os direitos reservados",
  "home_title": "Vela HRV — Suporte",
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
}

# ------------------------------------------------------------ generation

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  {path.relative_to(SITE)}")

def retrofit(path: Path, page: str, code: str, aria: str):
    """Adds the lang-row CSS + footer nav to an existing page."""
    html = path.read_text(encoding="utf-8")
    if "lang-row" in html:
        return
    html = html.replace("    .fade-in {", LANG_ROW_CSS + "    .fade-in {", 1)
    nav = lang_row(page, code, aria)
    html = re.sub(r"(<footer>\s*<p>©[^<]*</p>)", r"\1\n      " + nav, html, count=1)
    path.write_text(html, encoding="utf-8")
    print(f"  retrofit: {path.relative_to(SITE)}")

def main():
    print("Generando páginas nuevas:")
    for code, t in L.items():
        write(SITE / code / "index.html", render_home(code, t))
        write(SITE / code / "privacy" / "index.html", render_privacy(code, t))
        write(SITE / code / "accessibility" / "index.html", render_a11y(code, t))

    print("Retrofit del selector de idioma en páginas existentes:")
    retrofit(SITE / "index.html", "home", "en", "Language")
    retrofit(SITE / "privacy" / "index.html", "privacy", "en", "Language")
    retrofit(SITE / "accessibility" / "index.html", "accessibility", "en", "Language")
    retrofit(SITE / "es" / "index.html", "home", "es", "Idioma")
    retrofit(SITE / "es" / "privacy" / "index.html", "privacy", "es", "Idioma")
    retrofit(SITE / "es" / "accessibility" / "index.html", "accessibility", "es", "Idioma")

if __name__ == "__main__":
    main()
