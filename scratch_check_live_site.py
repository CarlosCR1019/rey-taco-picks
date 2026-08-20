import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

r = requests.get("https://reytacopicks.com", headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"})
print(f"Status: {r.status_code}")
html = r.text

if "platform-tabs" in html or "Draftea" in html:
    print("Contiene texto de tabs en el HTML.")
else:
    print("HTML limpio.")

# Find scripts
import re
js_links = re.findall(r'src=["\'](/assets/[^"\']+)["\']', html)
print(f"Scripts cargados en https://reytacopicks.com: {js_links}")

for js in js_links:
    r_js = requests.get(f"https://reytacopicks.com{js}", headers={"User-Agent": "Mozilla/5.0"})
    print(f"JS {js}: {len(r_js.text)} bytes")
    if "Draftea Fantasy" in r_js.text:
        print(" -> Todavía tiene texto viejo de Draftea (Render desplegando...)")
    else:
        print(" -> ¡JS 100% LIMPIO SIN DRAFTEA!")
