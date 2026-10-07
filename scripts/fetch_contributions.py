"""Baixa o calendário de contribuições e salva data/contributions.json.

1. Com o secret PROFILE_TOKEN: API GraphQL como o próprio dono do token, que
   inclui as contribuições em repositórios privados.
2. Sem ele: o HTML público em github.com/users/<usuario>/contributions.
3. Se o GitHub mudar a marcação: GraphQL com o GITHUB_TOKEN do Actions.
Se tudo falhar, sai com erro para o workflow não sobrescrever o gráfico bom.
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

from svgkit import ROOT

USER = os.environ.get("GH_USER", "matheusaoliv")
OUT = ROOT / "data" / "contributions.json"
HEADERS = {"User-Agent": f"{USER}-profile-readme", "Accept": "text/html"}


def from_html():
    url = f"https://github.com/users/{USER}/contributions"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # A contagem de cada dia fica no <tool-tip for="id-da-célula">.
    tips = {t["for"]: t.get_text(" ", strip=True) for t in soup.select("tool-tip[for]")}
    days = []
    for td in soup.select("td[data-date]"):
        level = int(td.get("data-level") or 0)
        if td.get("data-count") is not None:  # marcação antiga
            count = int(td["data-count"])
        else:
            m = re.search(r"([\d,.]+)\s+contributions?", tips.get(td.get("id"), ""))
            count = int(re.sub(r"\D", "", m.group(1))) if m else 0
        days.append({"date": td["data-date"], "count": count, "level": level})

    if days and not any(d["count"] for d in days) and any(d["level"] for d in days):
        raise RuntimeError("células com nível > 0 mas contagem 0: marcação mudou")
    return days


def from_graphql(token, viewer=False):
    """`viewer=True` consulta o dono do token (vê as contribuições privadas)."""
    calendar = "contributionsCollection { contributionCalendar { weeks { contributionDays { date contributionCount } } } }"
    if viewer:
        query, variables, key = f"{{ viewer {{ {calendar} }} }}", {}, "viewer"
    else:
        query = f"query($login: String!) {{ user(login: $login) {{ {calendar} }} }}"
        variables, key = {"login": USER}, "user"
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body:
        raise RuntimeError(body["errors"])
    weeks = body["data"][key]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [
        {"date": d["date"], "count": d["contributionCount"], "level": 0}
        for w in weeks for d in w["contributionDays"]
    ]


def streaks(days):
    """Sequência atual (hoje sem contribuição ainda não quebra) e a maior."""
    counts = [d["count"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    tail = counts[:-1] if counts and not counts[-1] else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def main():
    days, source = [], None
    attempts = []
    if os.environ.get("PROFILE_TOKEN"):
        attempts.append(("token", lambda: from_graphql(os.environ["PROFILE_TOKEN"], viewer=True)))
    attempts.append(("html", from_html))
    if os.environ.get("GITHUB_TOKEN"):
        attempts.append(("graphql", lambda: from_graphql(os.environ["GITHUB_TOKEN"])))
    for name, fetch in attempts:
        try:
            days, source = fetch(), name
        except Exception as err:  # noqa: BLE001 - qualquer falha tenta a próxima fonte
            print(f"aviso: fonte {name} falhou ({err})", file=sys.stderr)
        if days:
            break
    if not days:
        sys.exit("erro: nenhum dia de contribuição encontrado")

    days.sort(key=lambda d: d["date"])
    # Garante dias corridos (sem buracos) entre o primeiro e o último.
    by_date = {d["date"]: d for d in days}
    start, end = date.fromisoformat(days[0]["date"]), date.fromisoformat(days[-1]["date"])
    days = []
    for i in range((end - start).days + 1):
        iso = (start + timedelta(days=i)).isoformat()
        days.append(by_date.get(iso, {"date": iso, "count": 0, "level": 0}))

    months = defaultdict(int)
    for d in days:
        months[d["date"][:7]] += d["count"]
    best = max(days, key=lambda d: d["count"])
    current, longest = streaks(days)

    data = {
        "user": USER,
        "source": source,
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "active_days": sum(1 for d in days if d["count"]),
        "months": dict(sorted(months.items())),
        "days": days,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"ok: {len(days)} dias, {data['total']} contribuições ({source})")


if __name__ == "__main__":
    main()
