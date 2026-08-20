import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check ESPN team roster API
teams = [
    ("León", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/227/roster"),
    ("Tigres", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/231/roster"),
    ("América", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/222/roster"),
    ("Monterrey", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/229/roster"),
    ("Juarez", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/17852/roster"),
    ("Toluca", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/teams/232/roster")
]

for team_name, url in teams:
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            athletes = data.get("athletes", [])
            for group in athletes:
                pos = group.get("position")
                items = group.get("items", [])
                names = [a.get("displayName") for a in items]
                print(f"[{team_name}] {pos}: {names[:6]}")
    except Exception as e:
        print(f"Error {team_name}: {e}")
