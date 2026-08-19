import requests

try:
    r = requests.get("http://127.0.0.1:9222/json")
    tabs = r.json()
    print("Tabs abiertos en Chrome:")
    for t in tabs:
        print(f" - [{t.get('title')}] -> {t.get('url')}")
except Exception as e:
    print(f"Error: {e}")
