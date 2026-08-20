import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r = requests.get("https://www.draftea.mx/", headers=headers)
html = r.text

print(f"HTML downloaded: {len(html)} chars")

# Find all script src
scripts = re.findall(r'<script[^>]+src=["\'](.*?)["\']', html)
print(f"Total scripts found in HTML: {len(scripts)}")

js_urls = []
for s in scripts:
    if s.startswith("/"):
        js_urls.append("https://www.draftea.mx" + s)
    elif s.startswith("http"):
        js_urls.append(s)

api_candidates = set()

# Search in HTML directly
found_apis = re.findall(r'https?://[a-zA-Z0-9.-]*draftea[a-zA-Z0-9.-]*\.[a-z]{2,}(?:/[a-zA-Z0-9_.-]*)*', html)
api_candidates.update(found_apis)

for js in js_urls:
    try:
        r_js = requests.get(js, headers=headers, timeout=8)
        content = r_js.text
        print(f"Inspecting JS: {js[:60]}... ({len(content)} bytes)")
        
        # Search for endpoints
        matches = re.findall(r'https?://[a-zA-Z0-9.-]*draftea[a-zA-Z0-9.-]*\.[a-z]{2,}(?:/[a-zA-Z0-9_.-]*)*', content)
        api_candidates.update(matches)
        
        # Search for /api/ or graphql
        api_paths = re.findall(r'["\'](/(?:api|v1|v2|graphql|props|tournaments)/[a-zA-Z0-9_/-]*)["\']', content)
        for p in api_paths:
            api_candidates.add(p)
    except Exception as e:
        print(f"Error reading {js}: {e}")

print("\n🎯 Endpoints y Dominios de Draftea Descubiertos:")
for c in sorted(api_candidates):
    print(" -", c)
