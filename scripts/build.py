#!/usr/bin/env python3
"""Builds every SVG in assets/ for the clackes profile README.

Edit the COPY section, then run:  python3 scripts/build.py
The script refuses to build if a line of text would overflow its card.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

# ── palette ────────────────────────────────────────────────────────────────
# Neutrals and the blue→cyan accent come from albertovergani.com.
# Violet, magenta, green, gold and coral come from the reference art.
BG, SURF, SURF2, LINE = "#0a0a0f", "#121216", "#18181b", "#27272a"
TEXT, MUTED, DIM = "#e4e4e7", "#a1a1aa", "#5c5c66"
BLUE, CYAN = "#3b82f6", "#22d3ee"   # portfolio accent
VIOLET = "#a78bfa"                  # the aura
MAGENTA = "#e879f9"                 # the aura's hot core
GREEN = "#3ecf8e"                   # hair and coat
GOLD = "#d6a64f"                    # sword guards
CORAL = "#e8826a"                   # skin tones, used sparingly

SANS = "Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"
JP = "'Hiragino Mincho ProN','Yu Mincho','Noto Serif JP','Noto Serif CJK JP',serif"

LANG = {"Swift": "#f05138", "Go": "#00add8", "Python": "#3572a5", "TypeScript": "#3178c6",
        "JavaScript": "#f1e05a", "Monkey C": "#8d6748", "Java": "#b07219", "Shell": "#89e051"}


# ═════════════════════════════════════════════════════════════════════════
# COPY
# ═════════════════════════════════════════════════════════════════════════
KICKER = "Developer  ·  AI tooling  ·  Automation  ·  SUPSI"
TAGLINE = "Apps, bots, watch faces and AI tooling. Mostly things I needed myself."

ABOUT_TITLE = "Most of it started as my own problem."
ABOUT = ("Student at SUPSI. I write Discord bots, scrapers and monitors, Garmin watch faces, "
         "web apps, a macOS toolkit and MCP servers for my own AI workflow. "
         "I also make short-form video for Instagram and TikTok.")
STATS = [("30+", "projects", VIOLET), ("8", "languages", BLUE),
         ("5", "platforms, from browser to wrist", GREEN)]

NOW = [("Shipping", "Tsukumo & Falconia", VIOLET), ("Building", "AI tooling", MAGENTA),
       ("Studying", "at SUPSI", GOLD), ("Open to", "freelance & internships", GREEN)]

PUBLIC = [  # file, tag, title, text, language, accent
    ("tsukumo", "macOS  ·  open source", "Tsukumo",
     "Dynamic Island, window snapping, Alt-Tab, menu bar manager and system monitor in one native app for Apple Silicon.",
     "Swift", VIOLET),
    ("falconia", "AI  ·  self-hosted", "Falconia",
     "Every artifact your AI agents produce, stored in one place your team owns. Works with any agent. Apache-2.0.",
     "Go", MAGENTA),
    ("reiatsu", "Garmin  ·  relay", "Reiatsu Relay",
     "The backend for a Garmin watch face that shows how much of my Claude plan is left, and when it resets.",
     "Python", GREEN),
    ("bin", "iOS  ·  offline", "Bin",
     "Swipe through your camera roll: keep or delete, one photo at a time. No network, no cache.",
     "TypeScript", BLUE),
]

PRIVATE = [  # skills distilled from private work: no project names, no project content
    ("priv-ai", "AI & agents", VIOLET, [
        ("MCP servers", "Remote and local, used by several AI clients at once."),
        ("LLM APIs", "Anthropic, OpenAI and Gemini behind one streaming gateway."),
        ("Sandboxing", "Running untrusted, generated code in zero-trust iframes."),
    ]),
    ("priv-bots", "Automation & bots", MAGENTA, [
        ("Discord bots", "Slash commands, context menus, role-gated workflows."),
        ("Headless scraping", "Plain HTTP and JWT auth, no browser, built to run 24/7."),
        ("Notifications", "Discord webhooks, Telegram and email, with deduplication."),
    ]),
    ("priv-health", "Wearables & data", GREEN, [
        ("Connect IQ", "Watch faces, widgets and glances in Monkey C."),
        ("Sensor data", "Accelerometer and heart rate, synced in the background."),
        ("Speech", "Whisper transcription of short audio clips."),
    ]),
    ("priv-apps", "Apps & infrastructure", BLUE, [
        ("Full-stack web", "Next.js, FastAPI and Flask apps, installable as PWAs."),
        ("Data", "SQLite with Drizzle, Postgres, and plain JSON snapshots."),
        ("Self-hosting", "Docker on a home NAS, nothing exposed to the internet."),
    ]),
]

ARSENAL = [("Languages", ["Swift", "TypeScript", "Python", "Go", "JavaScript", "Monkey C", "Java", "Shell"]),
           ("Platforms", ["Web · PWA", "macOS", "iOS", "Garmin Connect IQ", "Discord", "Docker · NAS"]),
           ("Stack", ["Next.js", "FastAPI", "Flask", "SQLite", "Postgres", "MCP", "Whisper", "Tailwind"])]

CLOSE_TITLE = "Have something worth building? Write me."
CLOSE_SUB = "Freelance work, internships and side projects."


# ═════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════
def tw(s, size, mono=False, bold=False, ls=0):
    """Conservative text-width estimate, used to keep everything inside its box."""
    k = 0.61 if mono else (0.6 if bold else 0.51)
    return len(s) * (size * k + ls)


def guard(s, size, maxw, **kw):
    w = tw(s, size, **kw)
    assert w <= maxw, f"text too wide ({w:.0f}>{maxw:.0f}): {s!r}"
    return s


def wrap(text, size, maxw, bold=False):
    lines, cur = [], ""
    for word in text.split():
        nxt = f"{cur} {word}".strip()
        if tw(nxt, size, bold=bold) > maxw and cur:
            lines.append(cur)
            cur = word
        else:
            cur = nxt
    return lines + [cur]


def t(x, y, s, size=15, fill=TEXT, font=SANS, weight=400, ls=0, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" letter-spacing="{ls}" text-anchor="{anchor}">{escape(s)}</text>')


def kicker(x, y, s, fill=MUTED, size=11):
    return t(x, y, s.upper(), size, fill, MONO, 500, 2.4)


_gid = [0]


def card(x, y, w, h, inner="", accent=None, r=14):
    top = ""
    if accent:
        _gid[0] += 1
        gid = f"top{_gid[0]}"
        top = (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}"/>'
               f'<stop offset=".55" stop-color="{accent}" stop-opacity=".15"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>'
               f'<path d="M{r} .75 H{w - r}" stroke="url(#{gid})" stroke-width="1.5"/>')
    return (f'<g transform="translate({x},{y})"><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" '
            f'fill="{SURF}" stroke="{LINE}"/>{top}{inner}</g>')


DEFS = f"""
<linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{TEXT}"/><stop offset=".5" stop-color="{TEXT}"/>
  <stop offset=".8" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/>
</linearGradient>
<radialGradient id="auraV"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".24"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="auraM"><stop offset="0" stop-color="{MAGENTA}" stop-opacity=".15"/><stop offset="1" stop-color="{MAGENTA}" stop-opacity="0"/></radialGradient>
<radialGradient id="auraG"><stop offset="0" stop-color="{GREEN}" stop-opacity=".13"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<radialGradient id="auraB"><stop offset="0" stop-color="{BLUE}" stop-opacity=".14"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{VIOLET}"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".8"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
</linearGradient>
"""


def svg(name, w, h, body, label, defs=""):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
         f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title><defs>{DEFS}{defs}</defs>{body}</svg>\n')
    (OUT / name).write_text(s)


# ═════════════════════════════════════════════════════════════════════════
# ASSETS
# ═════════════════════════════════════════════════════════════════════════
def header():
    W, H = 1000, 300
    extra = """<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".045"/></pattern>
    <radialGradient id="fade" cx=".72" cy=".35" r=".7"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <mask id="gm"><rect width="1000" height="300" fill="url(#fade)"/></mask>
    <clipPath id="hc"><rect width="1000" height="300" rx="16"/></clipPath>"""
    blades = ""
    for i, (col, delay) in enumerate([(VIOLET, 0), (GREEN, .35), (GOLD, .7)]):
        x0 = 600 + i * 44
        d = f"M{x0} 312 L{x0 + 270} -12"
        blades += f'<path d="{d}" stroke="{col}" stroke-opacity=".32" stroke-width="1.2"/>'
        blades += (f'<path d="{d}" stroke="{col}" stroke-width="2" stroke-linecap="round" '
                   f'stroke-dasharray="70 560" stroke-dashoffset="70">'
                   f'<animate attributeName="stroke-dashoffset" values="70;70;-490;-490" '
                   f'keyTimes="0;{.05 + delay / 7:.3f};{.35 + delay / 7:.3f};1" dur="7s" repeatCount="indefinite"/></path>')
    body = f"""<g clip-path="url(#hc)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gm)"/>
  <circle cx="790" cy="110" r="330" fill="url(#auraV)"/>
  <circle cx="700" cy="40" r="220" fill="url(#auraM)"><animate attributeName="r" values="220;250;220" dur="8s" repeatCount="indefinite"/></circle>
  <circle cx="1000" cy="320" r="260" fill="url(#auraG)"/>
  <circle cx="0" cy="300" r="280" fill="url(#auraB)"/>
  <g fill="none">{blades}</g>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="15.5" fill="none" stroke="{LINE}"/>
{kicker(60, 78, guard(KICKER, 12, 600, mono=True, ls=2.4), MUTED, 12)}
{t(54, 186, "clackes", 108, "url(#name)", SANS, 800, -4)}
{t(60, 232, "Alberto Vergani", 22, TEXT, SANS, 600)}
{t(60, 262, guard(TAGLINE, 16.5, 640), 16.5, MUTED)}
<g font-family="{JP}" font-size="24" fill="{DIM}" text-anchor="middle">
  <text x="950" y="66">三</text><text x="950" y="100">刀</text><text x="950" y="134">流</text>
</g>
<rect x="947" y="148" width="6" height="6" fill="{GOLD}" transform="rotate(45 950 151)"/>
<g transform="translate(806,238)">
  <rect x=".5" y=".5" width="153" height="33" rx="16.5" fill="{SURF}" fill-opacity=".85" stroke="{LINE}"/>
  <circle cx="20" cy="17" r="4" fill="{GREEN}"/>
  <circle cx="20" cy="17" r="4" fill="none" stroke="{GREEN}">
    <animate attributeName="r" values="4;10" dur="2.2s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values=".8;0" dur="2.2s" repeatCount="indefinite"/>
  </circle>
  {t(34, 22, "Open to work", 14, TEXT, SANS, 500)}
</g>"""
    svg("header.svg", W, H, body, f"clackes — Alberto Vergani. {TAGLINE} Open to work.", extra)


def chip(name, label, icon):
    w = int(48 + tw(label, 14, bold=True) + 18)
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="39" rx="20" fill="{SURF}" stroke="{LINE}"/>'
            f'<g transform="translate(16,10)">{icon}</g>{t(44, 25, label, 14, TEXT, SANS, 600)}')
    svg(name, w, 40, body, label)


GLOBE = (f'<circle cx="10" cy="10" r="8.5" fill="none" stroke="{CYAN}" stroke-width="1.5"/>'
         f'<ellipse cx="10" cy="10" rx="3.6" ry="8.5" fill="none" stroke="{CYAN}" stroke-width="1.5"/>'
         f'<path d="M1.5 10h17" stroke="{CYAN}" stroke-width="1.5"/>')
LINKEDIN = (f'<rect x="1" y="1" width="18" height="18" rx="4" fill="{BLUE}"/>'
            f'<rect x="4.6" y="8" width="2.6" height="7.6" fill="#fff"/><circle cx="5.9" cy="5.2" r="1.5" fill="#fff"/>'
            f'<path d="M9.4 8h2.5v1.1c.5-.8 1.4-1.3 2.6-1.3 2 0 2.8 1.3 2.8 3.4v4.4h-2.6v-3.9c0-1-.3-1.7-1.3-1.7s-1.5.7-1.5 1.7v3.9H9.4z" fill="#fff"/>')


def intro():
    about = kicker(32, 44, "About", VIOLET)
    y = 80
    for l in wrap(ABOUT_TITLE, 22, 540, bold=True):
        about += t(32, y, guard(l, 22, 548, bold=True), 22, TEXT, SANS, 700, -.4)
        y += 28
    y += 8
    for l in wrap(ABOUT, 15, 540):
        about += t(32, y, l, 15, MUTED)
        y += 23
    H = int(y + 6)
    right, rh = "", H / 3
    for i, (n, lab, col) in enumerate(STATS):
        y0 = i * rh
        if i:
            right += f'<path d="M24 {y0:.1f} H346" stroke="{LINE}"/>'
        right += t(28, f"{y0 + rh / 2 + 11:.1f}", n, 32, col, SANS, 700, -1)
        nx = 28 + tw(n, 32, bold=True) + 8
        right += t(f"{nx:.1f}", f"{y0 + rh / 2 + 9:.1f}", guard(lab, 13.5, 342 - nx), 13.5, MUTED)
    body = card(0, 0, 610, H, about, VIOLET) + card(630, 0, 370, H, right, BLUE)
    svg("intro.svg", 1000, H, body, f"{ABOUT_TITLE} {ABOUT}")


def now():
    inner = ""
    for i, (k, v, c) in enumerate(NOW):
        x = 28 + i * 243
        if i:
            inner += f'<path d="M{x - 18} 22 V66" stroke="{LINE}"/>'
        inner += f'<circle cx="{x + 3}" cy="34" r="3" fill="{c}"/>'
        inner += kicker(x + 14, 38, k, MUTED, 10.5)
        inner += t(x, 62, guard(v, 15, 215, bold=True), 15, TEXT, SANS, 600)
    svg("now.svg", 1000, 88, card(0, 0, 1000, 88, inner),
        "Now: " + ", ".join(f"{k.lower()} {v}" for k, v, _ in NOW) + ".")


def section(name, num, title, aside, light=False):
    fg, sub, ln = (("#1f2328", "#6e7781", "#d0d7de") if light else (TEXT, DIM, LINE))
    body = (t(0, 30, num, 13, GOLD, MONO, 500, 1) + t(36, 31, title, 24, fg, SANS, 700, -.4)
            + t(1000, 30, aside, 12, sub, MONO, 400, 1.5, "end")
            + f'<path d="M0 50.5 H1000" stroke="{ln}"/><path d="M0 50.5 H260" stroke="url(#rule)" stroke-width="1.5"/>')
    svg(f"sec-{name}{'-light' if light else ''}.svg", 1000, 56, body, title)


def glyph(kind, c):
    return {
        "tsukumo": f'<rect x="1" y="5" width="30" height="22" rx="3.5" fill="none" stroke="{c}" stroke-width="1.4"/>'
                   f'<rect x="10" y="8" width="12" height="4" rx="2" fill="{c}"/>'
                   f'<rect x="5" y="15" width="10" height="8" rx="1.5" fill="none" stroke="{c}" stroke-opacity=".6"/>'
                   f'<rect x="17" y="15" width="10" height="8" rx="1.5" fill="none" stroke="{c}" stroke-opacity=".6"/>',
        "falconia": f'<g fill="none" stroke="{c}" stroke-width="1.4" stroke-linejoin="round">'
                    f'<path d="M16 4 L30 11 L16 18 L2 11 Z"/><path d="M2 17 L16 24 L30 17" stroke-opacity=".6"/>'
                    f'<path d="M2 23 L16 30 L30 23" stroke-opacity=".3"/></g>',
        "reiatsu": f'<g fill="none" stroke="{c}" stroke-width="1.4"><rect x="10" y="0" width="12" height="5" rx="1.5" stroke-opacity=".5"/>'
                   f'<rect x="10" y="27" width="12" height="5" rx="1.5" stroke-opacity=".5"/><circle cx="16" cy="16" r="11"/></g>'
                   f'<path d="M16 7 A9 9 0 1 1 8.2 20.5" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/>',
        "bin": f'<g fill="none" stroke-width="1.4"><rect x="2" y="5" width="18" height="24" rx="3" stroke="{DIM}"/>'
               f'<rect x="12" y="2" width="18" height="24" rx="3" stroke="{c}" fill="{SURF}" transform="rotate(12 21 14)"/></g>',
        "lock": f'<g fill="none" stroke="{c}" stroke-width="1.6"><rect x="6" y="14" width="20" height="15" rx="3"/>'
                f'<path d="M10.5 14 V10 a5.5 5.5 0 0 1 11 0 V14"/></g><circle cx="16" cy="21.5" r="2" fill="{c}"/>',
    }[kind]


def public_card(f, tag, title, text, lang, c):
    W, H = 490, 214
    inner = kicker(28, 42, tag, c, 10.5)
    inner += t(27, 80, guard(title, 26, 380, bold=True), 26, TEXT, SANS, 700, -.6)
    y = 110
    for l in wrap(text, 14.5, 430):
        inner += t(28, y, l, 14.5, MUTED)
        y += 22
    assert y - 22 <= H - 56, (title, y)
    inner += f'<path d="M28 {H - 44} H{W - 28}" stroke="{LINE}"/>'
    inner += f'<circle cx="33" cy="{H - 22}" r="4.5" fill="{LANG[lang]}"/>' + t(44, H - 17.5, lang, 12.5, MUTED, MONO)
    repo = {"tsukumo": "Tsukumo", "falconia": "falconia", "reiatsu": "reiatsu-relay", "bin": "bin-app"}[f]
    inner += t(W - 28, H - 17.5, f"github.com/clackes/{repo}", 12, DIM, MONO, 400, 0, "end")
    inner += f'<g transform="translate({W - 60},24)">{glyph(f, c)}</g>'
    svg(f"{f}.svg", W, H, card(0, 0, W, H, inner, c), f"{title}: {text}")


def private_card(f, tag, c, items, H=None):
    W = 490
    inner = kicker(28, 42, tag, c, 10.5)
    inner += f'<g transform="translate({W - 46},28) scale(.56)">{glyph("lock", DIM)}</g>'
    y = 62
    for i, (name, line) in enumerate(items):
        if i:
            inner += f'<path d="M28 {y - 6} H{W - 28}" stroke="{LINE}" stroke-dasharray="2 4"/>'
        inner += f'<rect x="28" y="{y + 9}" width="3" height="14" rx="1.5" fill="{c}"/>'
        inner += t(40, y + 21, guard(name, 16, 420, bold=True), 16, TEXT, SANS, 600)
        yy = y + 43
        lines = wrap(line, 13.5, 440)
        assert len(lines) == 1, (name, lines)
        for l in lines:
            inner += t(40, yy, l, 13.5, MUTED)
            yy += 19
        y = yy + 12
    need = y + 6
    if H is None:
        return need
    svg(f"{f}.svg", W, H, card(0, 0, W, H, inner, c),
        f"{tag}: " + "; ".join(f"{n} — {l}" for n, l in items))


def arsenal(light=False):
    body, y, c = "", 0, 0
    accents = [VIOLET, MAGENTA, GREEN, BLUE, GOLD, CYAN]
    for lab, items in ARSENAL:
        body += kicker(0, y + 24, lab, "#6e7781" if light else DIM, 11)
        x = 130
        for s in items:
            w = 30 + tw(s, 13.5, bold=True) + 16
            body += f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1:.0f}" height="35" rx="10" fill="{SURF}" stroke="{LINE}"/>'
            if s in LANG:
                body += f'<circle cx="{x + 16}" cy="{y + 18}" r="4" fill="{LANG[s]}"/>'
            else:
                col = accents[c % len(accents)]
                c += 1
                body += (f'<rect x="{x + 12.5}" y="{y + 14.5}" width="7" height="7" rx="1" fill="{col}" '
                         f'transform="rotate(45 {x + 16} {y + 18})"/>')
            body += t(x + 30, y + 22.5, s, 13.5, TEXT, SANS, 500)
            x += w + 8
        assert x <= 1008, (lab, x)
        y += 50
    svg(f"arsenal{'-light' if light else ''}.svg", 1000, y - 14, body,
        " · ".join(", ".join(i) for _, i in ARSENAL))


def closing():
    W, H = 1000, 190
    body = f"""<clipPath id="cc"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="{BG}"/>
<circle cx="380" cy="250" r="320" fill="url(#auraV)"/><circle cx="660" cy="250" r="280" fill="url(#auraB)"/>
<g fill="none" stroke-width="1.2" stroke-opacity=".35"><path d="M40 190 L150 0" stroke="{VIOLET}"/><path d="M74 190 L184 0" stroke="{GREEN}"/><path d="M108 190 L218 0" stroke="{GOLD}"/></g></g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="15.5" fill="none" stroke="{LINE}"/>
{t(500, 80, guard(CLOSE_TITLE, 30, 760, bold=True), 30, TEXT, SANS, 700, -.8, "middle")}
{t(500, 112, CLOSE_SUB, 16, MUTED, SANS, 400, 0, "middle")}
{t(500, 150, "albertovergani.com   ·   linkedin.com/in/alberto-vergani", 12.5, DIM, MONO, 400, .5, "middle")}
{t(958, 168, "三刀流", 15, DIM, JP, 400, 2, "end")}"""
    svg("closing.svg", W, H, body, f"{CLOSE_TITLE} {CLOSE_SUB}")


if __name__ == "__main__":
    for f in OUT.glob("*.svg"):
        f.unlink()
    header()
    chip("chip-site.svg", "albertovergani.com", GLOBE)
    chip("chip-linkedin.svg", "LinkedIn", LINKEDIN)
    intro()
    now()
    for light in (False, True):
        section("work", "01", "Selected work", "/ public repos", light)
        section("private", "02", "Under the hood", "/ learned in private repos", light)
        section("arsenal", "03", "Arsenal", "/ what I build with", light)
        section("activity", "04", "Activity", "/ contributions", light)
        arsenal(light)
    for p in PUBLIC:
        public_card(*p)
    # cards in the same row share a height so the grid lines up
    hs = [private_card(*p) for p in PRIVATE]
    rows = [max(hs[0], hs[1]), max(hs[2], hs[3])]
    for i, p in enumerate(PRIVATE):
        private_card(*p, H=int(rows[i // 2]))
    closing()
    print("built", len(list(OUT.glob("*.svg"))), "files")
