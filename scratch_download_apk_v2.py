import requests
import re
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

r = session.get("https://draftea.en.uptodown.com/android/download")
html = r.text

button = re.search(r'<button[^>]+id="detail-download-button"[^>]+data-url="([^"]+)"', html)
if button:
    post_url = button.group(1)
    if not post_url.startswith("http"):
        post_url = "https://draftea.en.uptodown.com" + post_url
    print(f"Boton de descarga: {post_url}")
    
    # Send post/get to get the real file
    r_file = session.post(post_url, headers={"Referer": "https://draftea.en.uptodown.com/android/download"}, allow_redirects=True, stream=True)
    print(f"Status descarga: {r_file.status_code} | URL: {r_file.url}")
    
    if r_file.status_code == 200:
        filename = "draftea_app.apk"
        with open(filename, "wb") as f:
            for chunk in r_file.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        print(f"✅ Archivo guardado: {filename} ({os.path.getsize(filename)/(1024*1024):.2f} MB)")
else:
    print("No se encontró el botón con data-url.")
    # Search all data-urls
    for m in re.finditer(r'data-url="([^"]+)"', html):
        print("data-url:", m.group(1))
