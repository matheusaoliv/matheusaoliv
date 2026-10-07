"""Gera info-card.svg: painel no estilo `neofetch` com quem eu sou e minha stack.

Edite INFO abaixo e rode `python scripts/make_info_card.py`. O workflow diário
também roda este script para manter o "Uptime" (tempo de GitHub) em dia.
As linhas entram em sequência, deslizando e aparecendo, e o cursor do prompt
fica piscando no final.
"""
from datetime import date

from svgkit import ACCENT, MUTED, TEXT, TITLE_H, esc, window, write

USER, HOST = "matheus", "github"
GITHUB_SINCE = date(2022, 6, 9)

INFO = [
    ("Name", "Matheus de Andrade Oliveira"),
    ("Role", "Full-Stack Developer"),
    ("Now", "Japeri City Hall · public sector"),
    ("Location", "Nova Iguaçu, RJ – Brazil"),
    ("Education", "Computer Science · Estácio"),
    ("Uptime", None),  # calculado a partir de GITHUB_SINCE
    ("Web", "TypeScript · React · Node.js"),
    ("Mobile", "React Native · Flutter · Kotlin"),
    ("Data", "PostgreSQL · MySQL · MongoDB"),
    ("Cloud", "AWS · Azure · Docker"),
    ("Projects", "SERI Smart Parking · Bike Parking"),
]

# Paleta ANSI do tema escuro do GitHub, como os blocos de cor do neofetch.
BLOCKS = ["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4"]

WIDTH, HEIGHT = 490, 400
PAD_X = 26
VALUE_X = 120
LINE_H = 20
FIRST_Y = TITLE_H + 30


def uptime(today=None):
    today = today or date.today()
    months = (today.year - GITHUB_SINCE.year) * 12 + today.month - GITHUB_SINCE.month
    if today.day < GITHUB_SINCE.day:
        months -= 1
    years, months = divmod(months, 12)
    parts = [f"{years} {'year' if years == 1 else 'years'}"] if years else []
    if months:
        parts.append(f"{months} {'month' if months == 1 else 'months'}")
    return ", ".join(parts or ["under a month"]) + " on GitHub"


def main():
    handle = f"{USER}@{HOST}"
    lines = [
        f'<tspan fill="{ACCENT}" font-weight="700">{USER}</tspan>@'
        f'<tspan fill="{ACCENT}" font-weight="700">{HOST}</tspan>',
        f'<tspan fill="{MUTED}">{"-" * len(handle)}</tspan>',
    ]
    for key, value in INFO:
        value = uptime() if value is None else value
        lines.append(
            f'<tspan fill="{ACCENT}" font-weight="700">{esc(key)}:</tspan>'
            f'<tspan x="{VALUE_X}">{esc(value)}</tspan>'
        )

    body = []
    for i, line in enumerate(lines):
        body.append(
            f'<text class="ln" x="{PAD_X}" y="{FIRST_Y + i * LINE_H}" '
            f'style="animation-delay:{0.3 + i * 0.11:.2f}s">{line}</text>'
        )

    y = FIRST_Y + len(lines) * LINE_H
    end = 0.3 + len(lines) * 0.11
    blocks = "".join(
        f'<rect x="{PAD_X + i * 24}" y="{y - 4}" width="24" height="14" fill="{c}"/>'
        for i, c in enumerate(BLOCKS)
    )
    body.append(f'<g class="ln" style="animation-delay:{end:.2f}s">{blocks}</g>')

    y += LINE_H + 16
    body.append(
        f'<text class="ln" x="{PAD_X}" y="{y}" style="animation-delay:{end + 0.15:.2f}s">'
        f'<tspan fill="{ACCENT}">{handle}</tspan> <tspan fill="#58a6ff">~</tspan> $ '
        f'<tspan class="cur" fill="{TEXT}" style="animation-delay:{end + 0.6:.2f}s">█</tspan></text>'
    )

    css = f"""
.ln {{ font-size: 13px; fill: {TEXT}; white-space: pre; animation: slide .45s ease-out both; }}
@keyframes slide {{ from {{ opacity: 0; transform: translateX(-8px); }} }}
.cur {{ animation: blink 1.1s step-end infinite; }}
@keyframes blink {{ 50% {{ fill-opacity: 0; }} }}
"""
    label = "neofetch-style card: " + "; ".join(
        f"{k}: {uptime() if v is None else v}" for k, v in INFO
    )
    write("info-card.svg", window(WIDTH, HEIGHT, f"{handle}: ~ — neofetch", label, "\n".join(body), css))


if __name__ == "__main__":
    main()
