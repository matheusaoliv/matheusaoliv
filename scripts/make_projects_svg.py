"""Gera projects/<slug>.svg: um card animado por projeto em destaque.

Os melhores projetos ficam em repositórios privados, que o GitSkins não
enxerga; por isso os cards são feitos aqui, com descrição e stack escritos à
mão. Cada card é um SVG separado para poder virar link no README (site no ar
quando existe). Edite PROJECTS e rode `python scripts/make_projects_svg.py`.
"""
from svgkit import ACCENT, BLUE, BRIGHT, MUTED, PURPLE, ROOT, SANS, TEXT, card, esc, write

PROJECTS = [
    {
        "slug": "nexto",
        "repo": "matheusaoliv/NEXTO",
        "name": "NEXTO",
        "kicker": "AI · URBAN MOBILITY",
        "accent": PURPLE,
        "desc": "AI super-app for city life: rides, food delivery, P2P marketplace, "
                "digital wallet and smart home, run by an autonomous assistant.",
        "highlight": "local LLM agent · voice in/out · vector memory",
        "stack": ["React", "TypeScript", "FastAPI", "Ollama", "pgvector"],
        "live": None,
    },
    {
        "slug": "financial-dashboard",
        "repo": "matheusaoliv/financial-dashboard",
        "name": "Financial Dashboard",
        "kicker": "FINTECH · SECURITY",
        "accent": ACCENT,
        "desc": "Personal finance dashboard built security-first: encrypted "
                "sensitive data, token rotation and full audit trail.",
        "highlight": "AES-256-GCM · Argon2id · rate limiting · LGPD",
        "stack": ["Next.js", "NestJS", "Prisma", "PostgreSQL"],
        "live": "financial-dashboard-web-omega.vercel.app",
    },
    {
        "slug": "gymnutri-ai",
        "repo": "matheusaoliv/GymNutri-AI",
        "name": "GymNutri-AI",
        "kicker": "HEALTH · AI COACH",
        "accent": "#f78166",
        "desc": "Personal trainer and nutritionist powered by AI: workouts, meals "
                "and macros, progress, sleep and mood in one mobile-first app.",
        "highlight": "AI coach on your own data · 350+ exercises",
        "stack": ["Next.js 15", "TypeScript", "Supabase", "OpenAI"],
        "live": None,
    },
    {
        "slug": "bike-hub",
        "repo": "matheusaoliv/bicicletario-smart-hub-2.0",
        "name": "Bicicletário Smart Hub 2.0",
        "kicker": "MOBILITY · CIVIC TECH",
        "accent": BLUE,
        "desc": "Smart bike-parking network linked to Rio's metro and train lines, "
                "with live map, rewards and CO₂ savings per ride.",
        "highlight": "134 stations · MetrôRio + SuperVia · gamified",
        "stack": ["React", "Leaflet", "Express", "PostgreSQL", "WebSocket"],
        "live": None,
    },
    {
        "slug": "portal-japeri",
        "repo": "matheusaoliv/Portal-Japeri",
        "name": "Portal Japeri",
        "kicker": "GOVTECH · UNOFFICIAL DEMO",
        "accent": "#2ad5ef",
        "desc": "Japeri's city services in one place: plain-language search, "
                "4-step online requests and protocol tracking.",
        "highlight": "web + PWA + Android/iPhone · WCAG 2.1 AA",
        "stack": ["JavaScript", "PWA", "Capacitor"],
        "live": "portal-japeri.vercel.app",
    },
    {
        "slug": "apuraja",
        "repo": "matheusaoliv/apuraja",
        "name": "ApuraJá",
        "kicker": "DATA · ELECTIONS 2026",
        "accent": "#e3b341",
        "desc": "Live results of Brazil's 2026 runoff straight from official TSE "
                "data, with maps of all 5,570 cities and a projection.",
        "highlight": "no backend · updates every 15 s · Android app",
        "stack": ["React", "TypeScript", "D3-geo", "Capacitor"],
        "live": "apuracao-2026-alpha.vercel.app",
    },
]

WIDTH, HEIGHT = 430, 256
M = 12  # faixa de aura em volta do painel
PW, PH = WIDTH - 2 * M, HEIGHT - 2 * M
PAD = 20
DESC_CHARS = 54  # quebra de linha aproximada para 13px sem serifa


def wrap(text, width):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def badge(p):
    """Pílula no canto: 'live demo' pulsando ou 'private' com cadeado."""
    if p["live"]:
        w = 84
        x = PW - 14 - w
        return f"""
<rect x="{x}" y="9" width="{w}" height="20" rx="10" fill="{ACCENT}" fill-opacity=".12" stroke="{ACCENT}" stroke-opacity=".5"/>
<circle cx="{x + 12}" cy="19" r="3" fill="{ACCENT}"/>
<circle cx="{x + 12}" cy="19" r="3" fill="none" stroke="{ACCENT}">
<animate attributeName="r" values="3;8" dur="1.8s" repeatCount="indefinite"/>
<animate attributeName="stroke-opacity" values=".8;0" dur="1.8s" repeatCount="indefinite"/></circle>
<text x="{x + 22}" y="23" font-family="{SANS}" font-size="11" font-weight="700" fill="{ACCENT}">live demo</text>"""
    w = 70
    x = PW - 14 - w
    return f"""
<rect x="{x}" y="9" width="{w}" height="20" rx="10" fill="#ffffff" fill-opacity=".05" stroke="{MUTED}" stroke-opacity=".45"/>
<path d="M{x + 10.5} 18 v-2.2 a2.7 2.7 0 0 1 5.4 0 v2.2" fill="none" stroke="{MUTED}" stroke-width="1.3"/>
<rect x="{x + 9}" y="18" width="8.4" height="6.2" rx="1.4" fill="{MUTED}"/>
<text x="{x + 23}" y="23" font-family="{SANS}" font-size="11" font-weight="700" fill="{MUTED}">private</text>"""


def chips(stack, y, delay):
    out, x = [], PAD
    for i, name in enumerate(stack):
        w = len(name) * 6.4 + 22
        if x + w > PW - PAD:
            break
        out.append(
            f'<g class="rise" style="animation-delay:{delay + i * 0.07:.2f}s">'
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="23" rx="11.5" fill="#ffffff" fill-opacity=".045" '
            f'stroke="{BLUE}" stroke-opacity=".32"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + 15.5}" font-family="{SANS}" font-size="11.5" font-weight="600" '
            f'fill="{TEXT}" text-anchor="middle">{esc(name)}</text></g>'
        )
        x += w + 6
    return "".join(out)


def render(p):
    desc = wrap(p["desc"], DESC_CHARS)[:3]
    desc_svg = "".join(
        f'<text x="{PAD}" y="{110 + i * 18}" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(line)}</text>'
        for i, line in enumerate(desc)
    )
    css = """
.rise { animation: rise .6s cubic-bezier(.2,.75,.3,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(8px); } }
"""
    defs = f"""
<linearGradient id="title" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{BRIGHT}"/><stop offset="1" stop-color="{p["accent"]}"/></linearGradient>"""
    body = f"""
<g transform="translate({M} {M})">
<rect width="{PW}" height="{PH}" rx="16" fill="#080a0e" fill-opacity=".6" stroke="{BLUE}" stroke-opacity=".48"/>
<line x1="0" y1="38.5" x2="{PW}" y2="38.5" stroke="{BLUE}" stroke-opacity=".22"/>
<circle cx="{PAD}" cy="19" r="3" fill="{p["accent"]}"/>
<text x="{PAD + 10}" y="23" font-size="11" fill="{MUTED}">{esc(p["repo"])}</text>
{badge(p)}
<g class="rise" style="animation-delay:.1s">
<text x="{PAD}" y="62" font-size="10.5" letter-spacing="1.6" fill="{p["accent"]}">{esc(p["kicker"])}</text>
<text x="{PAD - 1}" y="88" font-family="{SANS}" font-size="22" font-weight="800" letter-spacing="-.4" fill="url(#title)">{esc(p["name"])}</text>
</g>
<g class="rise" style="animation-delay:.25s">{desc_svg}</g>
<g class="rise" style="animation-delay:.4s">
<text x="{PAD}" y="{110 + len(desc) * 18 + 8}" font-size="11.5" fill="{TEXT}"><tspan fill="{p["accent"]}">▸ </tspan>{esc(p["highlight"])}</text>
</g>
{chips(p["stack"], PH - PAD - 23, .55)}
</g>"""
    label = f'{p["name"]} ({p["kicker"].lower()}): {p["desc"]} Stack: {", ".join(p["stack"])}.'
    label += f' Live at {p["live"]}.' if p["live"] else " Private repository."
    return card(WIDTH, HEIGHT, label, body, css, defs)


def main():
    (ROOT / "projects").mkdir(exist_ok=True)
    for p in PROJECTS:
        write(f'projects/{p["slug"]}.svg', render(p))


if __name__ == "__main__":
    main()
