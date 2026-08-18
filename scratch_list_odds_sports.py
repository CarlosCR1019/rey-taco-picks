import os
import urllib.request
import json
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
key = os.getenv("ODDS_API_KEY")

url = f"https://api.the-odds-api.com/v4/sports/?apiKey={key}"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print("Ligas de fútbol activas en The Odds API:")
        for s in data:
            if s.get('active'):
                print(f" - Key: {s.get('key')} | Title: {s.get('title')} | Group: {s.get('group')}")
except Exception as e:
    print(f"Error: {e}")
