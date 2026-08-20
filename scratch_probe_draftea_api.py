import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

base = "https://api.draftea.com"

endpoints = [
    "/v1/sports", "/v1/tournaments", "/v1/props", "/v1/games",
    "/v1/matches", "/v1/players", "/v1/categories", "/v1/events",
    "/v1/pickem", "/v1/player-props", "/v1/contests", "/v1/lobbies",
    "/v2/sports", "/v2/tournaments", "/v2/props", "/v2/games",
    "/api/v1/sports", "/api/v1/tournaments", "/api/v1/props",
    "/graphql", "/health", "/status", "/version"
]

headers = {
    "User-Agent": "Draftea/5.0 (Android; es-MX)",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print(f"📡 Probando endpoints en {base}:")
for ep in endpoints:
    url = base + ep
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f" -> {ep:25} | Status: {r.status_code} | Body: {r.text[:120]}")
    except Exception as e:
        print(f" -> {ep:25} | Error: {e}")
