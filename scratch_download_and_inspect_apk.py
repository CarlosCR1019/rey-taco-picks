import requests
import re
import sys
import os
import zipfile
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://draftea.en.uptodown.com/android/download"
}

post_url = "https://draftea.en.uptodown.com/android/post-download/1155940599"
print(f"Buscando enlace directo en {post_url}...")
r = requests.get(post_url, headers=headers)
html = r.text

direct_links = re.findall(r'href=["\'](https://dw\.uptodown\.net/dwn/[^"\']+)["\']', html)
if not direct_links:
    direct_links = re.findall(r'data-url=["\'](https://dw\.uptodown\.net/dwn/[^"\']+)["\']', html)

print(f"Direct links found: {len(direct_links)}")
if direct_links:
    dl_url = direct_links[0]
    print(f"📥 Descargando APK desde: {dl_url[:60]}...")
    headers["Referer"] = post_url
    r_apk = requests.get(dl_url, headers=headers, stream=True, timeout=60)
    print(f"Status: {r_apk.status_code} | Size: {r_apk.headers.get('Content-Length')}")
    
    if r_apk.status_code == 200:
        filename = "draftea_app.apk"
        with open(filename, "wb") as f:
            for chunk in r_apk.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        print(f"🎉 APK Descargado exitosamente: {filename} ({os.path.getsize(filename)/(1024*1024):.2f} MB)")
        
        # Unzip / Inspect APK internal files
        print("\n🔍 Inspeccionando archivos internos del APK de Draftea...")
        with zipfile.ZipFile(filename, 'r') as z:
            namelist = z.namelist()
            print(f"Total archivos en el APK: {len(namelist)}")
            
            # Look for JS bundles, assets, webviews
            interesting = [n for n in namelist if 'bundle' in n or 'assets' in n or 'config' in n or 'json' in n or 'xml' in n]
            print(f"Archivos de interés encontrados: {len(interesting)}")
            for item in interesting[:15]:
                print(" -", item)
