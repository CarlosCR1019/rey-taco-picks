import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Let's inspect an event from ESPN to get the real player names
url = "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/scoreboard"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
data = r.json()

events = data.get("events", [])
print(f"Events in Liga MX: {len(events)}")

for ev in events:
    ev_id = ev.get("id")
    ev_name = ev.get("name")
    print(f"\n--- Partido: {ev_name} (ID: {ev_id}) ---")
    
    # Check summary or roster
    summary_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/summary?event={ev_id}"
    try:
        r_sum = requests.get(summary_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        if r_sum.status_code == 200:
            sum_data = r_sum.json()
            rosters = sum_data.get("rosters", [])
            print(f"Rosters count: {len(rosters)}")
            for team_roster in rosters:
                team_name = team_roster.get("team", {}).get("displayName")
                starters = team_roster.get("roster", [])
                player_names = [p.get("athlete", {}).get("displayName") for p in starters if p.get("starter")]
                if not player_names:
                    player_names = [p.get("athlete", {}).get("displayName") for p in starters[:5]]
                print(f" -> Equipo: {team_name} | Jugadores: {player_names[:5]}")
                
            # Check leaders / key players if no roster
            if not rosters:
                leaders = sum_data.get("leaders", [])
                print(f"Leaders: {leaders}")
    except Exception as e:
        print(f"Error fetching summary: {e}")
