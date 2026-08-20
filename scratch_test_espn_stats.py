import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Test fetching team/player statistics for Liga MX and Champions League from ESPN API
urls = [
    ("Liga MX Teams", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams"),
    ("Liga MX América Roster/Stats", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/227/roster"),
    ("Champions League Leaders/Stats", "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/statistics")
]

for name, u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            print(f"✅ {name}: Status {r.getcode()} | Keys: {list(data.keys())}")
            if "team" in data and "athletes" in data:
                print(f"   Jugadores encontrados en {name}: {len(data['athletes'])}")
                for ath_group in data['athletes'][:2]:
                    for p in ath_group.get('items', [])[:2]:
                        print(f"    - {p.get('displayName')} ({p.get('position', {}).get('name')})")
    except Exception as e:
        print(f"❌ {name}: {e}")
