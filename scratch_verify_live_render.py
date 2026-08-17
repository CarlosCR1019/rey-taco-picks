import urllib.request
import re

url = "https://rey-taco-picks-web.onrender.com/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8')
    print("HTML Length:", len(html))
    js_match = re.search(r'src="(/assets/[^"]+\.js)"', html)
    if js_match:
        js_url = "https://rey-taco-picks-web.onrender.com" + js_match.group(1)
        print("JS Asset URL:", js_url)
        with urllib.request.urlopen(js_url, timeout=10) as js_resp:
            js_content = js_resp.read().decode('utf-8')
            print("JS Length:", len(js_content))
            print("Contains 'initDailyVerseBanner':", 'initDailyVerseBanner' in js_content or 'daily-verse' in js_content)
            print("Contains 'dailyVerse':", 'Salmo' in js_content or 'daily_verse' in js_content)
            print("Contains eq('estado', 'pendiente'):", "estado" in js_content and "pendiente" in js_content)
            print("Contains 'VERDE COBRADO':", 'VERDE COBRADO' in js_content)
