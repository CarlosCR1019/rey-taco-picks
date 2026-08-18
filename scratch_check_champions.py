import os
import urllib.request
import json
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
key = os.getenv("ODDS_API_KEY")

print("Consultando partidos de UEFA Champions League en The Odds API...")
url = f"https://api.the-odds-api.com/v4/sports/soccer_uefa_champs_league/odds/?apiKey={key}&regions=us,eu&markets=h2h,totals,spreads"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total partidos de Champions encontrados: {len(data)}")
        for m in data:
            commence = m.get('commence_time')
            dt = datetime.fromisoformat(commence.replace('Z', '+00:00')) - timedelta(hours=6)
            print(f"🏟️ {m.get('home_team')} vs {m.get('away_team')} | Horario CDMX: {dt.strftime('%d/%m %H:%M hrs')}")
            for b in m.get('bookmakers', [])[:1]:
                for mkt in b.get('markets', []):
                    outs = [o.get('name') + ' @ ' + str(o.get('price')) for o in mkt.get('outcomes', [])]
                    print(f"   [{mkt.get('key')}]: {outs}")
except Exception as e:
    print(f"Error: {e}")
