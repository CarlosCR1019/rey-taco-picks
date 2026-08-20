import urllib.request
import json

urls = [
    "https://draftea.com/api/v1/tournaments",
    "https://api.draftea.com/v1/props",
    "https://api.draftea.com/v1/players",
    "https://draftea.mx/api/v1/props",
    "https://app.draftea.com/"
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            print(f"✅ {u}: Status {resp.getcode()} - Length {len(resp.read())}")
    except Exception as e:
        print(f"❌ {u}: {e}")
