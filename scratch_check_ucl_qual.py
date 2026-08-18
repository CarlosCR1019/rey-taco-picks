import os
import urllib.request
import json
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
key = os.getenv("ODDS_API_KEY")

url = f"https://api.the-odds-api.com/v4/sports/soccer_uefa_champs_league_qualification/odds/?apiKey={key}&regions=us,eu&markets=h2h,totals,spreads"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total partidos de Champions Qualification: {len(data)}")
        for m in data:
            commence = m.get('commence_time')
            dt = datetime.fromisoformat(commence.replace('Z', '+00:00')) - timedelta(hours=6)
            print(f"\n🏟️ {m.get('home_team')} vs {m.get('away_team')} | Horario CDMX: {dt.strftime('%d/%m %H:%M hrs')}")
            for b in m.get('bookmakers', [])[:1]:
                for mkt in b.get('markets', []):
                    outs = [f"{o.get('name')} ({o.get('point', '')}) @ {o.get('price')}".strip() for o in mkt.get('outcomes', [])]
                    print(f"   [{mkt.get('key').upper()}]: {', '.join(outs)}")
except Exception as e:
    print(f"Error: {e}")
