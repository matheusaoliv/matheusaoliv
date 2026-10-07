"""Visual compartilhado pelos SVGs do perfil.

O GitHub remove <script> e quase todo CSS do README, mas renderiza SVGs
embutidos via <img> e executa as animações (CSS e SMIL) que estão *dentro*
deles. Por isso toda a animação mora nos arquivos .svg gerados aqui.

Estilo: a "aura" dos cards do GitSkins (fundo escuro com brilhos azul, verde e
roxo e um painel interno com borda azul) com uma janela de terminal dentro,
para tudo no README parecer da mesma família.
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

# Imagens carregadas via <img> não podem baixar fontes externas: usamos a
# melhor fonte disponível no sistema de quem está visitando.
FONT = ("'SFMono-Regular', ui-monospace, Menlo, Consolas, "
        "'Liberation Mono', 'DejaVu Sans Mono', monospace")
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

BG = "#0d1117"
TEXT = "#c9d1d9"
BRIGHT = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#39d353"
BLUE = "#58a6ff"
PURPLE = "#a371f7"

TITLE_H = 32
RADIUS = 14
MARGIN = 22  # faixa de aura em volta do painel

# Quem pede menos movimento no sistema vê direto o quadro final.
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

AURA_CSS = """
.orb-a { animation: float-a 9s ease-in-out infinite; }
.orb-b { animation: float-b 11s ease-in-out infinite 1.1s; }
.orb-c { animation: float-c 13s ease-in-out infinite .6s; }
@keyframes float-a { 50% { transform: translate(26px, -16px); opacity: .85; } }
@keyframes float-b { 50% { transform: translate(-22px, 16px); opacity: .7; } }
@keyframes float-c { 50% { transform: translate(16px, -10px); opacity: .6; } }
"""


def esc(text):
    return escape(str(text), {'"': "&quot;"})


def aura(width, height):
    """Fundo arredondado com três brilhos que flutuam devagar."""
    defs = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{BG}"/><stop offset=".54" stop-color="#161b22"/><stop offset="1" stop-color="{BG}"/>
</linearGradient>""" + "".join(
        f"""
<radialGradient id="orb{i}"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/>
<stop offset=".58" stop-color="{c}" stop-opacity=".16"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>"""
        for i, (c, o) in enumerate([(BLUE, .6), (ACCENT, .42), (PURPLE, .6)])
    )
    w, h = width, height
    body = f"""
<rect width="{w}" height="{h}" rx="20" fill="url(#bg)"/>
<ellipse class="orb-a" cx="{w * .16:.0f}" cy="{h * .16:.0f}" rx="{w * .28:.0f}" ry="{h * .5:.0f}" fill="url(#orb0)" opacity=".7"/>
<ellipse class="orb-b" cx="{w * .8:.0f}" cy="{h * .2:.0f}" rx="{w * .3:.0f}" ry="{h * .45:.0f}" fill="url(#orb1)" opacity=".6"/>
<ellipse class="orb-c" cx="{w * .55:.0f}" cy="{h * .96:.0f}" rx="{w * .38:.0f}" ry="{h * .36:.0f}" fill="url(#orb2)" opacity=".5"/>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="none" stroke="{BLUE}" stroke-opacity=".28"/>"""
    return defs, body


def card(width, height, label, body, css="", defs=""):
    """SVG solto com fundo de aura; `body` usa coordenadas do SVG inteiro."""
    aura_defs, aura_body = aura(width, height)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">
<title id="t">{esc(label)}</title>
<style>
svg {{ font-family: {FONT}; }}
{AURA_CSS}
{css}
{REDUCED_MOTION}
</style>
<defs>{aura_defs}
{defs}
</defs>
<clipPath id="card"><rect width="{width}" height="{height}" rx="20"/></clipPath>
<g clip-path="url(#card)">{aura_body}
{body}
</g>
</svg>
"""


def window(width, height, title, label, body, css="", defs=""):
    """Janela de terminal (width x height) dentro de um card de aura.

    `body` usa coordenadas da janela; o SVG final ganha MARGIN em cada lado.
    """
    panel = f"""
<g transform="translate({MARGIN} {MARGIN})">
<clipPath id="win"><rect width="{width}" height="{height}" rx="{RADIUS}"/></clipPath>
<g clip-path="url(#win)">
<rect width="{width}" height="{height}" fill="#080a0e" fill-opacity=".62"/>
<rect width="{width}" height="{TITLE_H}" fill="#ffffff" fill-opacity=".035"/>
<line x1="0" y1="{TITLE_H}.5" x2="{width}" y2="{TITLE_H}.5" stroke="{BLUE}" stroke-opacity=".22"/>
<circle cx="18" cy="16" r="6" fill="#ff5f57"/>
<circle cx="38" cy="16" r="6" fill="#febc2e"/>
<circle cx="58" cy="16" r="6" fill="#28c840"/>
<text x="{width / 2:g}" y="20.5" fill="{MUTED}" font-size="12" text-anchor="middle">{esc(title)}</text>
{body}
</g>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="{RADIUS}" fill="none" stroke="{BLUE}" stroke-opacity=".5"/>
</g>"""
    return card(width + 2 * MARGIN, height + 2 * MARGIN, label, panel, css, defs)


def write(name, svg):
    path = ROOT / name
    path.write_text(svg, encoding="utf-8")
    print(f"ok: {path.relative_to(ROOT)} ({len(svg.encode()) / 1024:.1f} KB)")
