import socket
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

subdomains = [
    "api.draftea.com", "api.draftea.mx",
    "gateway.draftea.com", "gateway.draftea.mx",
    "prod-api.draftea.com", "prod.draftea.com",
    "core.draftea.com", "backend.draftea.com",
    "mobile-api.draftea.com", "app-api.draftea.com",
    "services.draftea.com", "server.draftea.com",
    "graphql.draftea.com", "rest.draftea.com",
    "sports.draftea.com", "props.draftea.com",
    "feed.draftea.com", "data.draftea.com"
]

print("🔍 Escaneando resolución DNS y HTTP de subdominios Draftea:")
live_hosts = []
for sub in subdomains:
    try:
        ip = socket.gethostbyname(sub)
        print(f"✅ DNS Encontrado: {sub} -> IP: {ip}")
        live_hosts.append(sub)
    except Exception:
        pass

print(f"\nTotal hosts activos encontrados: {len(live_hosts)}")
for h in live_hosts:
    for proto in ["https://"]:
        url = f"{proto}{h}"
        try:
            r = requests.get(url, timeout=5, headers={"User-Agent": "DrafteaApp/Android"})
            print(f" -> {url}: Status {r.status_code} | Server: {r.headers.get('Server', 'Unknown')} | Body: {r.text[:100]}")
        except Exception as e:
            print(f" -> {url}: {e}")
