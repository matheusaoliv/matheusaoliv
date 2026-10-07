"""Gera contrib-heatmap.svg a partir de data/contributions.json.

Grade de 53 semanas x 7 dias; os quadradinhos descem em diagonal ao carregar
a página e congelam no estado final (sem loop).
"""
import json
import math
from bisect import bisect_right
from datetime import date, timedelta

from svgkit import ACCENT, MUTED, ROOT, TEXT, TITLE_H, esc, window, write

# vazio -> mais forte (nível 5 é o neon do topo)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
WEEKDAYS = {1: "Mon", 3: "Wed", 5: "Fri"}

WIDTH = 860
CELL, GAP = 11, 3
PITCH = CELL + GAP
LABEL_W = 28


def fmt(n):
    return f"{n:,}"


def en_date(iso):
    d = date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


def plural(n, one, many):
    return f"{fmt(n)} {one if n == 1 else many}"


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    days = data["days"][-371:]  # no máximo 53 semanas

    nonzero = sorted(d["count"] for d in days if d["count"])

    def level(count):
        if not count:
            return 0
        return max(1, min(5, math.ceil(bisect_right(nonzero, count) / len(nonzero) * 5)))

    # Colunas começam no domingo, como no GitHub.
    first = date.fromisoformat(days[0]["date"])
    sunday = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = (date.fromisoformat(days[-1]["date"]) - sunday).days // 7 + 1

    grid_w = weeks * PITCH - GAP
    x0 = (WIDTH - LABEL_W - grid_w) / 2 + LABEL_W
    head_y = TITLE_H + 26
    month_y = head_y + 26
    y0 = month_y + 8
    grid_bottom = y0 + 7 * PITCH - GAP
    foot_y = grid_bottom + 24
    height = foot_y + 22

    cells, delays = [], set()
    month_marks = []
    for d in days:
        day = date.fromisoformat(d["date"])
        col = (day - sunday).days // 7
        row = (day.weekday() + 1) % 7
        if day.day == 1 or not month_marks:
            month_marks.append((col if day.day == 1 else 0, day.month))
        delays.add(col + row)
        cells.append(
            f'<rect class="c d{col + row}" x="{x0 + col * PITCH:g}" y="{y0 + row * PITCH:g}" '
            f'width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[level(d["count"])]}"/>'
        )

    # Rótulo do mês na coluna em que ele começa; descarta o primeiro se colar no próximo.
    if len(month_marks) > 1 and month_marks[1][0] - month_marks[0][0] < 3:
        month_marks.pop(0)
    months = "".join(
        f'<text x="{x0 + col * PITCH:g}" y="{month_y}">{MONTHS[m - 1]}</text>'
        for col, m in month_marks
    )
    weekdays = "".join(
        f'<text x="{x0 - 8:g}" y="{y0 + r * PITCH + CELL - 1.5:g}" text-anchor="end">{name}</text>'
        for r, name in WEEKDAYS.items()
    )

    legend_x = x0 + grid_w - 34 - 6 * PITCH + GAP
    legend = "".join(
        f'<rect x="{legend_x + i * PITCH:g}" y="{foot_y - CELL + 1}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    best = data["best_day"]
    stats = [
        ("current streak", plural(data["current_streak"], "day", "days")),
        ("longest streak", plural(data["longest_streak"], "day", "days")),
    ]
    if best["count"]:
        stats.append(("best day", f'{fmt(best["count"])} on {en_date(best["date"])}'))
    stats_svg = '<tspan fill="#484f58">  ·  </tspan>'.join(
        f'{esc(k)} <tspan fill="{ACCENT}">{esc(v)}</tspan>' for k, v in stats
    )

    total = data["total"]
    css = """
.c { animation: drop .55s cubic-bezier(.2,.75,.3,1) both; }
@keyframes drop { from { opacity: 0; transform: translateY(-12px); } }
.f { animation: fade .7s ease-out both; }
@keyframes fade { from { opacity: 0; } }
""" + "\n".join(f".d{k} {{ animation-delay: {0.25 + k * 0.022:.3f}s; }}" for k in sorted(delays))

    end = 0.25 + max(delays) * 0.022 + 0.3
    body = f"""
<text class="f" x="{x0:g}" y="{head_y}" fill="{TEXT}" font-size="14" font-weight="600" style="animation-delay:.1s"><tspan fill="{ACCENT}">{fmt(total)}</tspan> {"contribution" if total == 1 else "contributions"} in the last year</text>
<text class="f" x="{x0 + grid_w:g}" y="{head_y}" fill="{MUTED}" font-size="11" text-anchor="end" style="animation-delay:.1s">updated {en_date(days[-1]["date"])}</text>
<g class="f" fill="{MUTED}" font-size="10.5" style="animation-delay:.2s">{months}{weekdays}</g>
{"".join(cells)}
<g class="f" style="animation-delay:{end:.2f}s">
<text x="{x0:g}" y="{foot_y}" fill="{MUTED}" font-size="11.5">{stats_svg}</text>
<text x="{legend_x - 8:g}" y="{foot_y}" fill="{MUTED}" font-size="10.5" text-anchor="end">Less</text>
{legend}
<text x="{x0 + grid_w:g}" y="{foot_y}" fill="{MUTED}" font-size="10.5" text-anchor="end">More</text>
</g>"""

    label = f"{fmt(total)} GitHub contributions in the last year"
    write("contrib-heatmap.svg", window(WIDTH, height, "matheus@github: ~/contributions", label, body, css))


if __name__ == "__main__":
    main()
