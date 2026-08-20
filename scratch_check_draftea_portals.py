import socket
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

domains = [
    "draftea.com", "www.draftea.com",
    "draftea.mx", "www.draftea.mx",
    "app.draftea.com", "play.draftea.com",
    "web.draftea.com", "game.draftea.com",
    "lobby.draftea.com", "fantasy.draftea.com",
    "m.draftea.com", "mobile.draftea.com",
    "auth.draftea.com", "login.draftea.com",
    "sports.draftea.com", "props.draftea.com"
]

print("🔍 Comprobando dominios web activos de Draftea:")
for d in domains:
    try:
        ip = socket.gethostbyname(d)
        try:
            r = requests.get(f"https://{d}", timeout=4, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
            print(f"✅ https://{d:22} -> IP: {ip:15} | Status: {r.status_code} | Final: {r.url[:40]} | Title: {r.text[:60].replace(chr(10), '')}")
        except Exception as e:
            print(f"⚠️ https://{d:22} -> IP: {ip:15} | Error HTTP: {e}")
    except Exception:
        pass
