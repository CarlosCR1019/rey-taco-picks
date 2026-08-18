import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")

url = f"https://api.telegram.org/bot{token}/getUpdates"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print("Últimos updates recibidos por el bot:")
    for u in data.get('result', []):
        msg = u.get('message') or u.get('channel_post') or u.get('my_chat_member')
        chat = msg.get('chat') if msg else None
        if chat:
            print(f"Chat Type: {chat.get('type')} | ID: {chat.get('id')} | Title: {chat.get('title')} | Username: {chat.get('username')}")
