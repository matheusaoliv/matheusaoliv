"""Gera hero.svg: o topo do perfil, no estilo aura do GitSkins com toque de terminal.

Nome com degradê, cargo sendo digitado com cursor, status "aberto a
oportunidades" pulsando, chips da stack e um monograma com órbitas à direita.
Edite os textos abaixo e rode `python scripts/make_hero_svg.py`.
"""
from svgkit import ACCENT, BLUE, BRIGHT, MUTED, PURPLE, SANS, TEXT, card, esc, write

NAME = "Matheus Oliveira"
KICKER = "RECRUITER SIGNAL BRIEF · @matheusaoliv"
ROLE = "full-stack developer · web + mobile · civic tech"
TAGLINE = "Practical, high-impact products, with a focus on UX and solid engineering."
STATUS = "Open to new opportunities"
LOCATION = "Nova Iguaçu, RJ · Brazil"
CHIPS = [
    ("TypeScript", "#3178c6"),
    ("React", "#61dafb"),
    ("Node.js", "#5fa04e"),
    ("React Native", PURPLE),
    ("Flutter", "#54c5f8"),
    ("PostgreSQL", "#5b8fd6"),
]
MONOGRAM = "MO"

WIDTH, HEIGHT = 860, 330
X0 = 58
PROMPT_FS = 15
CHAR_W = PROMPT_FS * 0.6  # textLength força essa largura em qualquer fonte mono


def main():
    typed_x = X0 + 2 * CHAR_W
    n = len(ROLE)
    type_begin, type_dur = 0.9, round(n * 0.04, 2)
    type_end = type_begin + type_dur
    steps = ";".join(f"{k * CHAR_W:.1f}" for k in range(n)) + ";900"
    cursor_xs = ";".join(f"{typed_x + k * CHAR_W:.1f}" for k in range(n + 1))

    chips, x = [], X0
    for i, (name, color) in enumerate(CHIPS):
        w = len(name) * 6.9 + 34
        chips.append(
            f'<g class="rise" style="animation-delay:{type_end + 0.45 + i * 0.08:.2f}s">'
            f'<rect x="{x:.1f}" y="254" width="{w:.1f}" height="27" rx="13.5" fill="#ffffff" fill-opacity=".045" '
            f'stroke="{BLUE}" stroke-opacity=".35"/>'
            f'<circle cx="{x + 14:.1f}" cy="267.5" r="4" fill="{color}"/>'
            f'<text x="{x + 24:.1f}" y="272" font-family="{SANS}" font-size="12.5" font-weight="600" fill="{TEXT}">{esc(name)}</text></g>'
        )
        x += w + 8

    cx, cy = 718, 160
    css = """
.rise { animation: rise .7s cubic-bezier(.2,.75,.3,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(10px); } }
.fade { animation: fade .8s ease-out both; }
@keyframes fade { from { opacity: 0; } }
.ring { animation: ring 8s ease-in-out infinite; }
.ring-b { animation: ring 10s ease-in-out infinite 1.6s; }
@keyframes ring { 50% { stroke-opacity: .34; } }
"""
    defs = f"""
<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{X0 + 440}" y2="0">
<stop offset="0" stop-color="{BRIGHT}"/><stop offset=".55" stop-color="#a5d6ff"/><stop offset="1" stop-color="#d2a8ff"/></linearGradient>
<linearGradient id="mono" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{BLUE}"/><stop offset=".5" stop-color="{ACCENT}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>
<clipPath id="typed"><rect x="{typed_x:.1f}" y="140" width="0" height="26">
<animate attributeName="width" values="{steps}" calcMode="discrete" begin="{type_begin}s" dur="{type_dur}s" fill="freeze"/>
</rect></clipPath>"""

    body = f"""
<rect x="24" y="24" width="{WIDTH - 48}" height="{HEIGHT - 48}" rx="18" fill="#080a0e" fill-opacity=".55" stroke="{BLUE}" stroke-opacity=".48"/>

<text class="fade" x="{X0}" y="68" font-size="12" letter-spacing="2.4" fill="{BLUE}">{esc(KICKER)}</text>
<text class="rise" x="{X0 - 2}" y="122" font-family="{SANS}" font-size="46" font-weight="800" letter-spacing="-1.2" fill="url(#ink)" style="animation-delay:.15s">{esc(NAME)}</text>

<text class="fade" x="{X0}" y="158" font-size="{PROMPT_FS}" fill="{ACCENT}" style="animation-delay:.6s">$</text>
<text clip-path="url(#typed)" x="{typed_x:.1f}" y="158" font-size="{PROMPT_FS}" fill="{TEXT}" textLength="{n * CHAR_W:.1f}" lengthAdjust="spacing" xml:space="preserve">{esc(ROLE)}</text>
<rect x="{typed_x:.1f}" y="145" width="{CHAR_W:.1f}" height="17" fill="{ACCENT}">
<animate attributeName="x" values="{cursor_xs}" calcMode="discrete" begin="{type_begin}s" dur="{type_dur}s" fill="freeze"/>
<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/>
</rect>

<text class="rise" x="{X0}" y="194" font-family="{SANS}" font-size="15.5" fill="{MUTED}" style="animation-delay:{type_end + 0.05:.2f}s">{esc(TAGLINE)}</text>

<g class="rise" style="animation-delay:{type_end + 0.25:.2f}s">
<rect x="{X0}" y="210" width="{len(STATUS) * 7 + 44:.0f}" height="28" rx="14" fill="{ACCENT}" fill-opacity=".1" stroke="{ACCENT}" stroke-opacity=".45"/>
<circle cx="{X0 + 16}" cy="224" r="4" fill="{ACCENT}"/>
<circle cx="{X0 + 16}" cy="224" r="4" fill="none" stroke="{ACCENT}">
<animate attributeName="r" values="4;11" dur="1.8s" repeatCount="indefinite"/>
<animate attributeName="stroke-opacity" values=".8;0" dur="1.8s" repeatCount="indefinite"/>
</circle>
<text x="{X0 + 28}" y="228.5" font-family="{SANS}" font-size="13" font-weight="600" fill="{BRIGHT}">{esc(STATUS)}</text>
<text x="{X0 + len(STATUS) * 7 + 58:.0f}" y="228.5" font-size="12.5" fill="{MUTED}">{esc(LOCATION)}</text>
</g>

{"".join(chips)}

<g class="fade" style="animation-delay:.3s">
<circle class="ring" cx="{cx}" cy="{cy}" r="88" fill="none" stroke="{BRIGHT}" stroke-opacity=".12"/>
<circle class="ring-b" cx="{cx}" cy="{cy}" r="62" fill="none" stroke="{BRIGHT}" stroke-opacity=".2"/>
<circle cx="{cx}" cy="{cy}" r="40" fill="#080a0e" fill-opacity=".7" stroke="url(#mono)" stroke-width="2"/>
<text x="{cx}" y="{cy + 10}" font-family="{SANS}" font-size="28" font-weight="800" letter-spacing="-.5" text-anchor="middle" fill="url(#mono)">{esc(MONOGRAM)}</text>
<g><circle cx="{cx + 62}" cy="{cy}" r="4.5" fill="{BLUE}"/>
<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="12s" repeatCount="indefinite"/></g>
<g><circle cx="{cx - 88}" cy="{cy}" r="3.5" fill="{ACCENT}"/>
<animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="18s" repeatCount="indefinite"/></g>
</g>"""

    label = f"{NAME}: {ROLE}. {TAGLINE} {STATUS}. Stack: " + ", ".join(c for c, _ in CHIPS)
    write("hero.svg", card(WIDTH, HEIGHT, label, body, css, defs))


if __name__ == "__main__":
    main()
