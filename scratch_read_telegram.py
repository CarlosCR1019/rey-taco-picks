import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")

url = f"https://api.telegram.org/bot{token}/getUpdates"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        updates = data.get('result', [])
        print(f"Total updates pendientes en Telegram: {len(updates)}")
        for u in updates[-5:]:
            msg = u.get('message', {})
            sender = msg.get('from', {}).get('username') or msg.get('from', {}).get('first_name')
            text = msg.get('text')
            photo = msg.get('photo')
            print(f" - From: {sender} | Text: {text} | Photo: {bool(photo)}")
except Exception as e:
    print(f"Error: {e}")
