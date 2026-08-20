import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
vip_id = os.getenv("TELEGRAM_VIP_CHANNEL_ID") or "-1003845930328"
free_id = os.getenv("TELEGRAM_FREE_CHANNEL_ID") or "-1004387927424"

print("Probando envío de notificación de confirmación...")
url = f"https://api.telegram.org/bot{token}/sendMessage"

for target, nombre in [(chat_id, "Privado Carlos"), (vip_id, "Canal VIP"), (free_id, "Canal FREE")]:
    try:
        data = json.dumps({
            "chat_id": target,
            "text": f"🌮👑 *Rey Taco Picks Bot* ⚡\n\n✅ Reporte de las 04:00 PM (Ejecutado a las 04:25 PM): Cartelera vespertina y nocturna activa en la web.\n🌐 https://reytacopicks.com",
            "parse_mode": "Markdown"
        }).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f" - {nombre} ({target}): Status {r.getcode()}")
    except Exception as e:
        print(f" - Error enviando a {nombre} ({target}): {e}")
