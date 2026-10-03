#!/usr/bin/env python3
"""Render the animated SVGs for the GitHub profile README (dark and light).

GitHub serves README images through a proxy that strips scripts, so everything here
is plain SVG: CSS keyframes and SMIL (<animateMotion>) only. Numbers come from
data/metrics.json so the art and the facts are updated separately.

Usage: python3 scripts/render.py   → writes assets/*.svg
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

THEMES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "line": "#30363d", "text": "#e6edf3",
        "muted": "#8b949e", "green": "#3fb950", "blue": "#58a6ff", "violet": "#bc8cff",
        "amber": "#d29922", "red": "#f85149",
    },
    "light": {
        "bg": "#ffffff", "panel": "#f6f8fa", "line": "#d0d7de", "text": "#1f2328",
        "muted": "#656d76", "green": "#1a7f37", "blue": "#0969da", "violet": "#8250df",
        "amber": "#9a6700", "red": "#cf222e",
    },
}

# The 25 organisations, grouped by what they do. Colour = role in the system.
GROUPS = [
    ("governance", "violet", ["montesquieu", "securities"]),
    ("knowledge", "blue", ["researches", "strategies", "datas", "patents", "invests"]),
    ("factories", "green", ["seeds", "b2b-apps", "b2c-apps", "b2a-apps", "native-apps",
                            "inner-apps", "games", "oss", "contract-devs", "ec"]),
    ("media", "amber", ["brandings", "tubes", "books", "musics"]),
    ("platform", "muted", ["packages", "artifacts", "inc"]),
]


def apply(svg: str, t: dict) -> str:
    """Fill {colour} tokens. Not str.format: the CSS in <style> uses braces."""
    for key, value in t.items():
        svg = svg.replace("{" + key + "}", value)
    return svg


def font(size: int, weight: int = 400, fill: str = "text") -> str:
    return (f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{{{fill}}}"')


def hero(t: dict) -> str:
    """Name on the left, the organisation as a living network on the right."""
    w, h = 1200, 420
    cx, cy = 880, 210
    nodes: list[tuple[str, str, float, float]] = []
    total = sum(len(g[2]) for g in GROUPS)
    i = 0
    for _, colour, names in GROUPS:
        for name in names:
            a = -math.pi / 2 + 2 * math.pi * i / total
            r = 150
            nodes.append((name, colour, cx + r * math.cos(a), cy + r * math.sin(a)))
            i += 1

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
             f'role="img" aria-label="Keitaro Kaneko — Phixi, an AI-native company of 25 organisations">',
             "<style>",
             "@keyframes breathe{0%,100%{opacity:.55}50%{opacity:1}}",
             "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}",
             ".n{animation:breathe 4s ease-in-out infinite}",
             ".t{animation:rise .9s ease-out both}",
             "@media (prefers-reduced-motion:reduce){.n,.t{animation:none}}",
             "</style>",
             f'<rect width="{w}" height="{h}" rx="16" fill="{{bg}}"/>']

    # Edges: research → hub → factories; governance watches everything (dashed).
    for k, (name, colour, x, y) in enumerate(nodes):
        dash = ' stroke-dasharray="3 5"' if colour == "violet" else ""
        parts.append(f'<path id="e{k}" d="M{cx},{cy} L{x:.1f},{y:.1f}" stroke="{{line}}" stroke-width="1"{dash}/>')
    # Cross-links between neighbours make the mesh visible.
    for k in range(len(nodes)):
        x1, y1 = nodes[k][2], nodes[k][3]
        x2, y2 = nodes[(k + 3) % len(nodes)][2], nodes[(k + 3) % len(nodes)][3]
        parts.append(f'<path d="M{x1:.1f},{y1:.1f} Q{cx},{cy} {x2:.1f},{y2:.1f}" fill="none" '
                     f'stroke="{{line}}" stroke-width=".6" opacity=".5"/>')
    # Pulses travel out from the hub and back, staggered.
    for k, (_, colour, _, _) in enumerate(nodes):
        dur = 2.6 + (k % 5) * 0.35
        parts.append(f'<circle r="2.6" fill="{{{colour}}}"><animateMotion dur="{dur:.2f}s" '
                     f'begin="{(k * 0.23) % 3:.2f}s" repeatCount="indefinite" keyPoints="0;1;0" '
                     f'keyTimes="0;.5;1" calcMode="linear"><mpath href="#e{k}" xlink:href="#e{k}"/></animateMotion></circle>')
    for k, (name, colour, x, y) in enumerate(nodes):
        parts.append(f'<g class="n" style="animation-delay:{(k * 0.17) % 4:.2f}s">'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{{{colour}}}"/></g>')
        # Label sits outside the ring along the radius, so neighbours never collide.
        ang = math.atan2(y - cy, x - cx)
        lx, ly = x + 13 * math.cos(ang), y + 13 * math.sin(ang) + 4
        c = math.cos(ang)
        anchor = "start" if c > 0.25 else ("end" if c < -0.25 else "middle")
        if anchor == "middle":
            ly += 6 if math.sin(ang) > 0 else -4
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" {font(11, 400, "muted")}>{name}</text>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="22" fill="{{panel}}" stroke="{{green}}" stroke-width="2"/>')
    parts.append(f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" {font(13, 700)}>hub</text>')

    parts += [
        f'<g class="t"><text x="64" y="150" {font(44, 700)}>Keitaro Kaneko</text></g>',
        f'<g class="t" style="animation-delay:.15s"><text x="64" y="190" {font(18, 500, "muted")}>Founder &amp; CEO, Phixi Inc.</text></g>',
        f'<g class="t" style="animation-delay:.3s"><text x="64" y="248" {font(22, 600)}>Systems of AI, by AI, for people.</text></g>',
        f'<g class="t" style="animation-delay:.45s"><text x="64" y="284" {font(14, 400, "muted")}>A company run as 25 organisations of agents —</text>'
        f'<text x="64" y="304" {font(14, 400, "muted")}>governed, audited and shipped as code.</text></g>',
    ]
    # Legend
    lx = 64
    for label, colour in [("governance", "violet"), ("knowledge", "blue"), ("factories", "green"), ("media", "amber"), ("platform", "muted")]:
        parts.append(f'<circle cx="{lx}" cy="352" r="4" fill="{{{colour}}}"/><text x="{lx + 9}" y="356" {font(11, 400, "muted")}>{label}</text>')
        lx += 22 + len(label) * 6.6
    parts.append("</svg>")
    return apply("\n".join(parts), t)


def system(t: dict) -> str:
    """The operating loop, with the separation of powers and the security loop around it."""
    w, h = 1200, 470
    stages = [("Research", "markets · platforms", "blue"), ("Brain", "evaluate · prioritise", "text"),
              ("Factories", "apps · media · OSS", "green"), ("Gates", "rules · security · human", "violet"),
              ("Production", "SLOs · incidents", "amber")]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
             f'role="img" aria-label="How Phixi runs: research, brain, factories, gates, production, with oversight and a security loop">',
             "<style>@keyframes flow{to{stroke-dashoffset:-24}}.f{stroke-dasharray:6 6;animation:flow 1.2s linear infinite}"
             "@keyframes glow{0%,100%{opacity:.35}50%{opacity:.9}}.g{animation:glow 3s ease-in-out infinite}"
             "@media (prefers-reduced-motion:reduce){.f,.g{animation:none}}</style>",
             f'<rect width="{w}" height="{h}" rx="16" fill="{{bg}}"/>',
             f'<text x="48" y="52" {font(13, 600, "muted")}>HOW IT RUNS</text>']
    bx, by, bw, bh, gap = 48, 170, 196, 92, 32
    centres = []
    for k, (title, sub, colour) in enumerate(stages):
        x = bx + k * (bw + gap)
        centres.append((x, x + bw))
        parts.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="{{panel}}" stroke="{{{colour}}}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x + 18}" y="{by + 40}" {font(18, 700)}>{title}</text>')
        parts.append(f'<text x="{x + 18}" y="{by + 66}" {font(12, 400, "muted")}>{sub}</text>')
        if k < len(stages) - 1:
            parts.append(f'<path class="f" d="M{x + bw + 4},{by + bh / 2} H{x + bw + gap - 4}" stroke="{{green}}" stroke-width="2"/>')
    # Feedback: production → brain (below)
    x_prod_mid = (centres[4][0] + centres[4][1]) / 2
    x_brain_mid = (centres[1][0] + centres[1][1]) / 2
    parts.append(f'<path class="f" d="M{x_prod_mid},{by + bh + 4} V{by + bh + 60} H{x_brain_mid} V{by + bh + 4}" fill="none" stroke="{{amber}}" stroke-width="2"/>')
    parts.append(f'<text x="{(x_prod_mid + x_brain_mid) / 2}" y="{by + bh + 82}" text-anchor="middle" {font(12, 400, "muted")}>metrics · incidents · lessons written back into the pipeline</text>')
    # Oversight band (above)
    oy = 82
    parts.append(f'<rect class="g" x="48" y="{oy}" width="{w - 96}" height="56" rx="12" fill="none" stroke="{{violet}}" stroke-width="1.5" stroke-dasharray="4 6"/>')
    parts.append(f'<text x="70" y="{oy + 34}" {font(14, 600)}>Separation of powers</text>')
    branches = ["Legislature — writes the rules", "Executive — audits every org", "Judiciary — rules on changes", "Final say — a human"]
    sx = 290
    for b in branches:
        parts.append(f'<text x="{sx}" y="{oy + 34}" {font(12, 400, "muted")}>{b}</text>')
        sx += 215
    for x0, x1 in centres:
        parts.append(f'<path d="M{(x0 + x1) / 2},{oy + 56} V{by}" stroke="{{violet}}" stroke-width="1" stroke-dasharray="2 5" opacity=".7"/>')
    # Security loop (bottom right)
    sy = by + bh + 120
    parts.append(f'<rect x="{centres[2][0]}" y="{sy}" width="{centres[4][1] - centres[2][0]}" height="44" rx="10" fill="{{panel}}" stroke="{{red}}" stroke-width="1.2"/>')
    parts.append(f'<text x="{centres[2][0] + 18}" y="{sy + 28}" {font(13, 600)}>Security loop</text>')
    parts.append(f'<text x="{centres[2][0] + 140}" y="{sy + 28}" {font(12, 400, "muted")}>threat intel → attack → verify → one fix hardens every app</text>')
    parts.append(f'<text x="48" y="{sy + 28}" {font(12, 400, "muted")}>Every arrow is a workflow,</text>')
    parts.append(f'<text x="48" y="{sy + 46}" {font(12, 400, "muted")}>not a meeting.</text>')
    parts.append("</svg>")
    return apply("\n".join(parts), t)


def metrics(t: dict, m: dict) -> str:
    tiles = m["tiles"]
    w, h = 1200, 210
    cols = len(tiles)
    tw = (w - 96 - (cols - 1) * 16) / cols
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
             f'role="img" aria-label="Operating metrics as of {m["as_of"]}">',
             "<style>@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
             ".k{animation:up .8s ease-out both}@media (prefers-reduced-motion:reduce){.k{animation:none}}</style>",
             f'<rect width="{w}" height="{h}" rx="16" fill="{{bg}}"/>',
             f'<text x="48" y="42" {font(13, 600, "muted")}>OPERATING AT SCALE</text>',
             f'<text x="{w - 48}" y="42" text-anchor="end" {font(11, 400, "muted")}>as of {m["as_of"]}</text>']
    for k, tile in enumerate(tiles):
        x = 48 + k * (tw + 16)
        parts.append(f'<g class="k" style="animation-delay:{k * 0.12:.2f}s">'
                     f'<rect x="{x:.1f}" y="62" width="{tw:.1f}" height="118" rx="12" fill="{{panel}}" stroke="{{line}}"/>'
                     f'<text x="{x + 18:.1f}" y="114" {font(34, 700, tile.get("colour", "text"))}>{tile["value"]}</text>'
                     f'<text x="{x + 18:.1f}" y="142" {font(12, 600)}>{tile["label"]}</text>'
                     f'<text x="{x + 18:.1f}" y="161" {font(11, 400, "muted")}>{tile["note"]}</text></g>')
    parts.append("</svg>")
    return apply("\n".join(parts), t)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    m = json.loads((ROOT / "data" / "metrics.json").read_text())
    for name, t in THEMES.items():
        (ASSETS / f"hero-{name}.svg").write_text(hero(t))
        (ASSETS / f"system-{name}.svg").write_text(system(t))
        (ASSETS / f"metrics-{name}.svg").write_text(metrics(t, m))
    print("rendered", sorted(p.name for p in ASSETS.glob("*.svg")))


if __name__ == "__main__":
    main()
