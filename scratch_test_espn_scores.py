import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    ("UEFA Champions", "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard"),
    ("MLB", "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"),
    ("Liga MX", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/scoreboard")
]

for name, u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            events = data.get('events', [])
            print(f"OK {name}: {len(events)} eventos encontrados en ESPN API pública.")
            for e in events[:2]:
                print(f"   - {e.get('name')} | Status: {e.get('status', {}).get('type', {}).get('description')}")
    except Exception as ex:
        print(f"FAIL {name}: {ex}")
