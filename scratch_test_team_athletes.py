import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/227"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
data = r.json()
print("Keys in team endpoint:", list(data.keys()))
team = data.get("team", {})
print("Team name:", team.get("displayName"))
athletes = team.get("athletes", [])
print(f"Athletes length in team: {len(athletes)}")
for a in athletes[:5]:
    print(a.get("fullName"), a.get("position", {}).get("displayName"))
