"""Conta seus repositórios (públicos e privados) e salva data/profile.json.

O GitSkins e a página pública só enxergam repositórios públicos. Com o secret
PROFILE_TOKEN (token fine-grained, só leitura, com acesso a todos os
repositórios) a API GraphQL devolve o total real. Sem o token, ou se ele não
enxergar os privados, o arquivo atual é mantido para não piorar os números.
"""
import json
import os
import sys

import requests

from svgkit import ROOT

OUT = ROOT / "data" / "profile.json"
QUERY = """{ viewer { login createdAt
  all: repositories(ownerAffiliations: OWNER) { totalCount }
  public: repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
  private: repositories(ownerAffiliations: OWNER, privacy: PRIVATE) { totalCount } } }"""


def main():
    token = os.environ.get("PROFILE_TOKEN")
    if not token:
        print("sem PROFILE_TOKEN: mantendo data/profile.json")
        return
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body:
        sys.exit(f"erro na API: {body['errors']}")
    v = body["data"]["viewer"]

    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if v["private"]["totalCount"] == 0 and old.get("repos_private", 0) > 0:
        print("aviso: o token não enxerga repositórios privados; mantendo data/profile.json")
        print("dica: no token, escolha 'All repositories' em Repository access")
        return

    data = {
        "login": v["login"],
        "created_at": v["createdAt"][:10],
        "repos_total": v["all"]["totalCount"],
        "repos_public": v["public"]["totalCount"],
        "repos_private": v["private"]["totalCount"],
        "source": "token",
    }
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"ok: {data['repos_total']} repositórios ({data['repos_private']} privados)")


if __name__ == "__main__":
    main()
