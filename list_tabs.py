import urllib.request
import json

try:
    with urllib.request.urlopen("http://127.0.0.1:9222/json/list", timeout=5) as resp:
        tabs = json.loads(resp.read().decode())
        print(f"Total open tabs: {len(tabs)}")
        for t in tabs:
            print(f" - [{t.get('type')}] {t.get('title')} -> {t.get('url')}")
except Exception as e:
    print(f"Error connecting to DevTools: {e}")
