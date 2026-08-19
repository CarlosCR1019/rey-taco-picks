import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("ODDS_API_KEY")

url = f"https://api.the-odds-api.com/v4/sports?apiKey={api_key}"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"API Key es válida! Deportes disponibles: {len(data)}")
        headers = dict(resp.headers)
        print(f"Requests remaining: {headers.get('x-requests-remaining')}")
except Exception as e:
    print(f"Error con API Key ({api_key}): {e}")
