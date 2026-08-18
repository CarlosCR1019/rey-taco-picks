import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")

channels = [
    "@ReyTacoPicks",
    "@ReyTacoPicksFree",
    "-100234567890" # possible numeric id
]

for ch in ["@ReyTacoPicks", "@ReyTacoPicksFree"]:
    url = f"https://api.telegram.org/bot{token}/getChat?chat_id={ch}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"\n✅ {ch} ENCONTRADO:")
            print(f"   Título: {data.get('result', {}).get('title')}")
            print(f"   Tipo: {data.get('result', {}).get('type')}")
            print(f"   ID numérico: {data.get('result', {}).get('id')}")
            print(f"   Username: @{data.get('result', {}).get('username')}")
    except urllib.error.HTTPError as e:
        print(f"\n❌ {ch}: HTTP ERROR {e.code} - {e.read().decode()}")
    except Exception as e:
        print(f"\n❌ {ch}: ERROR - {e}")
