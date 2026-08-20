import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

base = "https://api.draftea.com"

# Stages and GraphQL paths
paths = [
    "/prod", "/prod/graphql", "/prod/v1", "/prod/props",
    "/production", "/production/graphql",
    "/v1/graphql", "/v2/graphql", "/api/graphql",
    "/draftea-api", "/mobile", "/mobile/v1",
    "/app", "/app/v1", "/core", "/core/v1"
]

headers = {
    "User-Agent": "Draftea/5.16 (Android; Linux; es-MX)",
    "Content-Type": "application/json",
    "Accept": "*/*"
}

graphql_query = {
    "query": "{ __schema { types { name } } }"
}

print("🔍 Probando etapas (stages) y GraphQL en api.draftea.com:")
for p in paths:
    url = base + p
    try:
        r = requests.post(url, json=graphql_query, headers=headers, timeout=4)
        if r.status_code != 404:
            print(f"🌟 POST {p:25} -> Status: {r.status_code} | Body: {r.text[:150]}")
        else:
            # Check GET
            r_get = requests.get(url, headers=headers, timeout=4)
            if r_get.status_code != 404:
                print(f"🌟 GET  {p:25} -> Status: {r_get.status_code} | Body: {r_get.text[:150]}")
    except Exception as e:
        pass

print("Test finalizado.")
