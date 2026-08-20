import requests
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# Search for direct APK download links for com.draftea
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

sources = [
    "https://draftea.en.uptodown.com/android/download",
    "https://apkpure.net/es/draftea/com.draftea/download",
    "https://apkcombo.com/es/draftea/com.draftea/download/apk"
]

print("🔍 Buscando enlace de descarga directa del APK de Draftea...")
for s in sources:
    try:
        r = requests.get(s, headers=headers, timeout=8)
        print(f" -> {s[:45]}... | Status: {r.status_code} | Length: {len(r.text)}")
    except Exception as e:
        print(f" -> Error en {s}: {e}")
