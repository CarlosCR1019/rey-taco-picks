import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/227/roster"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
data = r.json()

athletes = data.get("athletes", [])
for pos_group in athletes:
    items = pos_group.get("items", [])
    for it in items[:3]:
        print(f"Item: {it.get('fullName') or it.get('displayName') or it.get('name')} | Pos: {it.get('position', {}).get('name')}")
