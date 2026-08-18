import urllib.request
import json
import sys
import os
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")

test_handles = [
    "@ReyTacoPicks",
    "@ReyTacoPicksFree",
    "@ReyTacoPicks_Free",
    "@ReyTacoFree",
    "@reytacopicksfree",
    "@reytaco_picks",
    "@ReyTacoPicksGratis"
]

for h in test_handles:
    url = f"https://api.telegram.org/bot{token}/getChat?chat_id={h}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"ENCONTRADO: {h} -> Título: {data.get('result', {}).get('title')} | ID: {data.get('result', {}).get('id')}")
    except Exception as e:
        print(f"No encontrado o sin permisos: {h}")
