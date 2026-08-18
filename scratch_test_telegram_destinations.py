import os
import urllib.request
import json
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
vip_channel_id = os.getenv("TELEGRAM_VIP_CHANNEL_ID")
free_channel_id = os.getenv("TELEGRAM_FREE_CHANNEL_ID")

print("=== VERIFICACIÓN DE DESTINOS TELEGRAM ===")
print(f"Token: {token[:10]}... (len: {len(token) if token else 0})")
print(f"Chat ID (Carlos): {chat_id}")
print(f"Channel ID: {channel_id}")
print(f"VIP Channel ID: {vip_channel_id}")
print(f"Free Channel ID: {free_channel_id}")

destinos = [
    ("Privado Carlos", chat_id),
    ("Canal Principal", channel_id),
    ("Canal VIP", vip_channel_id),
    ("Canal FREE", free_channel_id)
]

for nombre, cid in destinos:
    if not cid:
        print(f"\n⚠️ {nombre}: NO CONFIGURADO (None o vacío)")
        continue
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": cid,
        "text": f"🌮 Test de Conexión en vivo - {nombre} 👑\n\nSi puedes leer este mensaje, la conexión está 100% activa.\nTimestamp: {os.path.basename(__file__)}"
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_data = json.loads(resp.read().decode())
            print(f"\n✅ {nombre} ({cid}): EXITO (HTTP {resp.getcode()})")
            print(f"   Mensaje ID: {res_data.get('result', {}).get('message_id')}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"\n❌ {nombre} ({cid}): HTTP ERROR {e.code} - {err_body}")
    except Exception as e:
        print(f"\n❌ {nombre} ({cid}): ERROR - {e}")
