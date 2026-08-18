import os
import sys
import json
import time
import urllib.request
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")

url = f"https://api.telegram.org/bot{token}/getUpdates"
print("Consultando updates de Telegram...")
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        updates = data.get('result', [])
        print(f"Total updates en Telegram: {len(updates)}")
        downloaded = []
        for u in updates:
            msg = u.get('message', {})
            photo = msg.get('photo')
            chat_id = msg.get('chat', {}).get('id')
            update_id = u.get('update_id')
            
            if photo:
                best_photo = photo[-1]
                file_id = best_photo.get('file_id')
                file_url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
                with urllib.request.urlopen(file_url, timeout=10) as fresp:
                    fdata = json.loads(fresp.read().decode())
                    file_path = fdata.get('result', {}).get('file_path')
                    
                filename = f"ticket_today_{update_id}.jpg"
                local_path = os.path.join("frontend", "public", "tickets", filename)
                img_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
                urllib.request.urlretrieve(img_url, local_path)
                print(f"Descargado: {filename} ({os.path.getsize(local_path)} bytes)")
                downloaded.append(filename)
                
                # Responder confirmación en Telegram
                if chat_id:
                    reply_url = f"https://api.telegram.org/bot{token}/sendMessage"
                    reply_payload = {
                        "chat_id": chat_id,
                        "text": f"🏆 ¡Ticket Ganador Recibido! 🌮👑\n\nTu captura `{filename}` ha sido verificada y agregada al Muro de Victorias en https://reytacopicks.com.\n¡Felicidades por el verde! 🟢🚀"
                    }
                    try:
                        req = urllib.request.Request(reply_url, data=json.dumps(reply_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                        urllib.request.urlopen(req)
                    except:
                        pass
        print(f"Total fotos descargadas ahora: {len(downloaded)}")
except Exception as e:
    print(f"Error: {e}")
