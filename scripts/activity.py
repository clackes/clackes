#!/usr/bin/env python3
"""Draws assets/activity.svg from the last 12 months of GitHub contributions.

Needs a token in GITHUB_TOKEN (the Actions token is enough).
Run locally with:  GITHUB_TOKEN=$(gh auth token) python3 scripts/activity.py
"""
import json
import os
import urllib.request
from datetime import date
from math import sqrt
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "clackes")
OUT = Path(__file__).resolve().parent.parent / "assets" / "activity.svg"

BG, SURF, LINE = "#0a0a0f", "#121216", "#27272a"
TEXT, MUTED, DIM = "#e4e4e7", "#a1a1aa", "#5c5c66"
VIOLET, MAGENTA, CYAN, GREEN, GOLD = "#a78bfa", "#e879f9", "#22d3ee", "#3ecf8e", "#d6a64f"
SANS = "Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "profile-activity"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(date.fromisoformat(d["date"]), d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    return cal["totalContributions"], cal["weeks"], days


def t(x, y, s, size, fill, font=SANS, weight=400, ls=0, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" letter-spacing="{ls}" text-anchor="{anchor}">{s}</text>')


def build(total, weeks, days):
    W, H = 1000, 300
    sums = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    top = max(sums) or 1
    best_i = sums.index(top)

    # streaks
    longest = cur = 0
    for _, n in days:
        cur = cur + 1 if n else 0
        longest = max(longest, cur)
    current = 0
    for _, n in reversed(days[:-1] if days and days[-1][1] == 0 else days):
        if not n:
            break
        current += 1
    by_wd = [0] * 7
    for d, n in days:
        by_wd[d.weekday()] += n
    busiest = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"][by_wd.index(max(by_wd))]

    body = [f'<clipPath id="ac"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
            f'<g clip-path="url(#ac)"><rect width="{W}" height="{H}" fill="{SURF}"/>',
            f'<circle cx="{W - 120}" cy="{H + 40}" r="300" fill="url(#glow)"/></g>',
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{LINE}"/>']

    # headline numbers
    body.append(t(32, 44, "LAST 12 MONTHS", 11, VIOLET, MONO, 500, 2.4))
    body.append(t(30, 92, f"{total:,}".replace(",", "."), 44, TEXT, SANS, 800, -1.5))
    body.append(t(32 + len(f"{total:,}") * 24.5 + 12, 90, "contributions", 15, MUTED))
    stats = [("Current streak", f"{current} days", GREEN), ("Longest streak", f"{longest} days", MAGENTA),
             ("Best week", f"{top}", GOLD), ("Busiest on", busiest, CYAN)]
    x = W - 32
    for label, value, c in reversed(stats):
        w = max(len(label) * 8.2, len(value) * 9.6) + 8
        body.append(t(x, 50, label.upper(), 10, DIM, MONO, 500, 1.6, "end"))
        body.append(t(x, 76, value, 17, TEXT, SANS, 700, -.3, "end"))
        body.append(f'<circle cx="{x - len(label) * 8.2 - 8:.1f}" cy="46.5" r="3" fill="{c}"/>')
        x -= w + 28

    # bars
    x0, x1, base, hmax = 32, W - 32, 248, 128
    n = len(sums)
    step = (x1 - x0) / n
    bw = step * .62
    body.append(f'<path d="M{x0} {base + .5} H{x1}" stroke="{LINE}"/>')
    for i, s in enumerate(sums):
        k = sqrt(s / top)
        h = max(3, k * hmax)
        bx = x0 + i * step + (step - bw) / 2
        fill = GOLD if i == best_i and s else ("url(#bars)" if s else LINE)
        op = 1 if s else .9
        delay = i * .018
        body.append(
            f'<rect x="{bx:.1f}" y="{base - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="{min(bw / 2, 3):.1f}" fill="{fill}" fill-opacity="{op}">'
            f'<animate attributeName="height" from="0" to="{h:.1f}" begin="{delay:.2f}s" dur=".6s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>'
            f'<animate attributeName="y" from="{base}" to="{base - h:.1f}" begin="{delay:.2f}s" dur=".6s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>'
            f'</rect>')

    # month ticks
    seen = None
    for i, w in enumerate(weeks):
        d0 = date.fromisoformat(w["contributionDays"][0]["date"])
        if d0.month != seen and d0.day <= 7 and i < n - 1:
            seen = d0.month
            body.append(t(f"{x0 + i * step + 1:.1f}", base + 24, d0.strftime("%b").upper(), 10, DIM, MONO, 500, 1.2))

    # one blade that sweeps across the bars
    body.append(
        f'<g opacity=".85"><path d="M-120 {base + 6} L-60 {base - hmax - 26}" stroke="url(#blade)" stroke-width="2" stroke-linecap="round"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{W + 140} 0;{W + 140} 0" keyTimes="0;.45;1" dur="9s" begin="1.5s" repeatCount="indefinite"/></g>')

    defs = (f'<radialGradient id="glow"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".16"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="bars" gradientUnits="userSpaceOnUse" x1="0" y1="248" x2="0" y2="120">'
            f'<stop offset="0" stop-color="{VIOLET}"/><stop offset=".55" stop-color="{MAGENTA}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>'
            f'<linearGradient id="blade" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>')
    label = f"{total} contributions in the last 12 months. Longest streak {longest} days, best week {top}, busiest on {busiest}."
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="{label}"><title>{label}</title><defs>{defs}</defs>{"".join(body)}</svg>\n')
    OUT.write_text(svg)
    print(label)


if __name__ == "__main__":
    build(*fetch())
