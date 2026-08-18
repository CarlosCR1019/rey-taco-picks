import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "5912533842"

reply_url = f"https://api.telegram.org/bot{token}/sendMessage"
reply_payload = {
    "chat_id": chat_id,
    "text": "🌮 *¡REY TACO PICKS - MENSAJE RECIBIDO!* 👑\n\nCarlos, tu captura ha sido recibida correctamente.\nTu sitio web oficial ya está en vivo en: https://reytacopicks.com 🚀🟢"
}
try:
    req = urllib.request.Request(reply_url, data=json.dumps(reply_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Telegram reply sent, status:", resp.status)
except Exception as e:
    print(f"Error: {e}")
