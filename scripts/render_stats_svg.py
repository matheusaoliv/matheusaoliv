"""Gera stats.svg: o "Profile Signal" com repositórios públicos + privados.

Lê data/profile.json (fetch_profile_stats.py), data/contributions.json
(fetch_contributions.py) e a lista de projetos em destaque. Quatro blocos:
repositórios, contribuições do último ano, demos no ar e tempo de GitHub.
"""
import json
from datetime import date

from make_projects_svg import PROJECTS
from svgkit import ACCENT, BLUE, BRIGHT, MUTED, PURPLE, ROOT, SANS, card, esc, write

WIDTH, HEIGHT = 860, 282
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
TILE_Y, TILE_H, GAP = 104, 134, 14
TILES_X, TILES_W = 42, WIDTH - 84
TW = (TILES_W - 3 * GAP) / 4
INNER = TW - 36  # largura útil dentro do bloco


def tile(i, label, value, unit, color, visual, caption):
    x = TILES_X + i * (TW + GAP)
    unit_svg = f'<tspan font-size="16" font-weight="600" fill="{MUTED}"> {esc(unit)}</tspan>' if unit else ""
    return f"""
<g transform="translate({x:.1f} {TILE_Y})"><g class="rise" style="animation-delay:{0.2 + i * 0.1:.2f}s">
<rect width="{TW:.1f}" height="{TILE_H}" rx="14" fill="#080a0e" fill-opacity=".5" stroke="{BLUE}" stroke-opacity=".45"/>
<text x="18" y="28" font-size="11" font-weight="700" letter-spacing="1.4" fill="{MUTED}">{esc(label)}</text>
<text x="17" y="70" font-family="{SANS}" font-size="36" font-weight="800" letter-spacing="-.8" fill="{color}">{esc(value)}{unit_svg}</text>
{visual}
<text x="18" y="{TILE_H - 14}" font-family="{SANS}" font-size="11.5" fill="{MUTED}">{esc(caption)}</text>
</g></g>"""


def main():
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    contrib = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))

    # Repositórios: barra dividida entre públicos e privados.
    total, public = profile["repos_total"], profile["repos_public"]
    private = profile["repos_private"]
    pub_w = INNER * public / total if total else 0
    repos_visual = f"""
<rect x="18" y="86" width="{INNER:.1f}" height="8" rx="4" fill="#ffffff" fill-opacity=".08"/>
<g class="grow" style="animation-delay:.5s">
<rect x="18" y="86" width="{INNER:.1f}" height="8" rx="4" fill="{PURPLE}"/>
<rect x="18" y="86" width="{pub_w:.1f}" height="8" rx="4" fill="{BLUE}"/></g>"""

    # Contribuições: total do último ano e barrinhas dos últimos 12 meses.
    months = list(contrib["months"].items())[-12:]
    peak = max((v for _, v in months), default=0) or 1
    bw = (INNER - 11 * 3) / 12
    bars = []
    for i, (_, v) in enumerate(months):
        h = max(2, 22 * v / peak)
        fill = ACCENT if v else "#ffffff"
        opacity = .35 + .65 * v / peak if v else .1
        bars.append(
            f'<rect class="up" style="animation-delay:{0.6 + i * 0.04:.2f}s" x="{18 + i * (bw + 3):.1f}" '
            f'y="{104 - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="1.5" fill="{fill}" fill-opacity="{opacity:.2f}"/>'
        )
    scope = "incl. private" if contrib.get("source") == "token" else "public only"

    # Demos no ar entre os projetos em destaque.
    live = sum(1 for p in PROJECTS if p["live"])
    dots = []
    for i, p in enumerate(PROJECTS):
        cx = 24 + i * 17
        if p["live"]:
            dots.append(f'<circle cx="{cx}" cy="95" r="5" fill="#2ad5ef"/>')
        else:
            dots.append(f'<circle cx="{cx}" cy="95" r="4.5" fill="none" stroke="{MUTED}" stroke-opacity=".6"/>')

    # Tempo de GitHub: linha do tempo com um traço por ano.
    since = date.fromisoformat(profile["created_at"])
    today = date.fromisoformat(contrib["days"][-1]["date"])
    years = (today - since).days / 365.25
    ticks = "".join(
        f'<line x1="{18 + INNER * y / years:.1f}" y1="91" x2="{18 + INNER * y / years:.1f}" y2="99" stroke="{PURPLE}" stroke-opacity=".7"/>'
        for y in range(1, int(years) + 1)
    )
    timeline = f"""
<line x1="18" y1="95" x2="{18 + INNER:.1f}" y2="95" stroke="#ffffff" stroke-opacity=".12" stroke-width="2"/>
<line class="grow" style="animation-delay:.8s" x1="18" y1="95" x2="{18 + INNER:.1f}" y2="95" stroke="{PURPLE}" stroke-width="2"/>
{ticks}<circle cx="18" cy="95" r="3.5" fill="{PURPLE}"/>
<circle cx="{18 + INNER:.1f}" cy="95" r="4" fill="{PURPLE}"/>
<circle cx="{18 + INNER:.1f}" cy="95" r="4" fill="none" stroke="{PURPLE}">
<animate attributeName="r" values="4;10" dur="1.8s" repeatCount="indefinite"/>
<animate attributeName="stroke-opacity" values=".8;0" dur="1.8s" repeatCount="indefinite"/></circle>"""

    updated = f"{MONTHS[today.month - 1]} {today.day}, {today.year}"
    tiles = (
        tile(0, "REPOSITORIES", f"{total}", "", BLUE, repos_visual, f"{public} public · {private} private")
        + tile(1, "CONTRIBUTIONS", f"{contrib['total']:,}", "", ACCENT, "".join(bars), f"past year · {scope}")
        + tile(2, "LIVE DEMOS", f"{live}", "", "#2ad5ef", "".join(dots), f"{live} of {len(PROJECTS)} featured projects")
        + tile(3, "ON GITHUB", f"{int(years)}", "yrs", PURPLE, timeline, f"since {MONTHS[since.month - 1]} {since.year}")
    )
    css = """
.rise { animation: rise .6s cubic-bezier(.2,.75,.3,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(8px); } }
.grow { transform-box: fill-box; transform-origin: left; animation: grow 1.1s cubic-bezier(.2,.75,.3,1) both; }
@keyframes grow { from { transform: scaleX(0); } }
.up { transform-box: fill-box; transform-origin: bottom; animation: up .7s cubic-bezier(.2,.75,.3,1) both; }
@keyframes up { from { transform: scaleY(0); } }
"""
    body = f"""
<rect x="22" y="22" width="{WIDTH - 44}" height="{HEIGHT - 44}" rx="18" fill="#080a0e" fill-opacity=".55" stroke="{BLUE}" stroke-opacity=".48"/>
<g class="rise">
<text x="46" y="66" font-family="{SANS}" font-size="26" font-weight="800" letter-spacing="-.5" fill="{BRIGHT}">Profile Signal</text>
<text x="48" y="88" font-size="11.5" letter-spacing=".6" fill="{MUTED}">public + private repositories · updated {updated}</text>
</g>
{tiles}"""
    label = (f"Profile Signal: {total} repositories ({public} public, {private} private), "
             f"{contrib['total']} contributions in the last 12 months, {live} live demos, "
             f"{int(years)} years on GitHub")
    write("stats.svg", card(WIDTH, HEIGHT, label, body, css))


if __name__ == "__main__":
    main()
