import requests
import re
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://draftea.en.uptodown.com/android"
}

r = requests.get("https://draftea.en.uptodown.com/android/download", headers=headers)
html = r.text

# Find data-url in download button
matches = re.findall(r'data-url=["\'](.*?)["\']', html)
print(f"Data URLs found: {matches}")

# Also check for direct href
download_urls = re.findall(r'href=["\'](https://dw\.uptodown\.com/[^"\']+)["\']', html)
print(f"Download URLs: {download_urls}")

target_url = None
if matches:
    target_url = matches[0]
elif download_urls:
    target_url = download_urls[0]

if target_url:
    print(f"📥 Descargando APK desde: {target_url}...")
    headers["Referer"] = "https://draftea.en.uptodown.com/android/download"
    r_dl = requests.get(target_url, headers=headers, stream=True, timeout=30)
    print(f"Status: {r_dl.status_code} | Content-Type: {r_dl.headers.get('Content-Type')} | Size: {r_dl.headers.get('Content-Length')}")
    
    if r_dl.status_code == 200:
        filename = "draftea_app.apk"
        with open(filename, "wb") as f:
            for chunk in r_dl.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        size_mb = os.path.getsize(filename) / (1024*1024)
        print(f"✅ APK descargado exitosamente: {filename} ({size_mb:.2f} MB)")
else:
    print("No se encontró URL directa inmediata. Inspeccionando estructura de la página...")
    button_matches = re.findall(r'<button[^>]+id=["\']detail-download-button["\'][^>]*>(.*?)</button>', html, re.DOTALL)
    print(f"Button matches: {button_matches}")
