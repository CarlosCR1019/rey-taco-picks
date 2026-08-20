import requests
import zipfile
import re
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Download the direct APK
url = "https://dw.uptodown.net/dwn/B-15f-c-oT2yG1-0s9-q2eG7x_v6wNfG1qY31hX-3nZ7v_Q21rZ-8_bT9/com.draftea-5.15.8.apk"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://draftea.en.uptodown.com/android/post-download/1155940599"
}

print(f"Descargando APK oficial desde: {url}...")
r = requests.get(url, headers=headers, stream=True, timeout=60)
print(f"Status: {r.status_code} | Headers: {dict(r.headers)}")

if r.status_code == 200:
    filename = "com.draftea.apk"
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    size_mb = os.path.getsize(filename) / (1024*1024)
    print(f"🎉 APK Guardado: {filename} ({size_mb:.2f} MB)")
    
    # Inspeccionar contenido
    with zipfile.ZipFile(filename, 'r') as z:
        namelist = z.namelist()
        print(f"Total archivos internos: {len(namelist)}")
        
        # Buscar index.android.bundle (React Native) o libapp.so (Flutter)
        bundles = [n for n in namelist if 'index.android.bundle' in n or 'bundle' in n or 'assets' in n]
        print(f"Bundles y Assets encontrados ({len(bundles)}):")
        for b in bundles[:20]:
            print(" -", b)
            
        if 'assets/index.android.bundle' in namelist:
            print("\n🌟 ¡ES UNA APLICACIÓN REACT NATIVE! Extrayendo index.android.bundle...")
            bundle_content = z.read('assets/index.android.bundle').decode('utf-8', errors='ignore')
            print(f"Tamaño del bundle JS: {len(bundle_content)} caracteres")
            
            # Buscar URLs y Endpoints dentro del bundle
            urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-z]{2,}(?:/[a-zA-Z0-9_.-]*)*', bundle_content)
            draftea_urls = set([u for u in urls if 'draftea' in u or 'api' in u or 'props' in u or 'graphql' in u])
            print(f"\n🎯 Endpoints de Draftea encontrados en el código fuente:")
            for u in sorted(draftea_urls):
                print(" ->", u)
else:
    print("El enlace expiró o requirió cookies.")
