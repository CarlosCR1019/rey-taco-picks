import os
import json
import time
import urllib.request
from dotenv import load_dotenv

load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")

url = f"https://api.telegram.org/bot{token}/getUpdates"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        updates = data.get('result', [])
        for u in updates:
            msg = u.get('message', {})
            chat_id = msg.get('chat', {}).get('id')
            photo = msg.get('photo')
            update_id = u.get('update_id')
            if photo and chat_id:
                # Obtener la foto de mayor resolucion
                best_photo = photo[-1]
                file_id = best_photo.get('file_id')
                
                # Obtener url de descarga
                file_url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
                with urllib.request.urlopen(file_url, timeout=10) as fresp:
                    fdata = json.loads(fresp.read().decode())
                    file_path = fdata.get('result', {}).get('file_path')
                    
                # Descargar
                img_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
                filename = f"ticket_{int(time.time())}.jpg"
                local_path = os.path.join("frontend", "public", "tickets", filename)
                urllib.request.urlretrieve(img_url, local_path)
                print(f"✅ Foto descargada: {filename} ({os.path.getsize(local_path)} bytes)")
                
                # Agregar al manifest.json
                manifest_path = os.path.join("frontend", "public", "tickets", "manifest.json")
                manifest = []
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest = json.load(mf)
                if filename not in manifest:
                    manifest.insert(0, filename)
                    with open(manifest_path, "w", encoding="utf-8") as mf:
                        json.dump(manifest, mf, indent=2)
                        
                # Responder a Carlos en Telegram
                reply_url = f"https://api.telegram.org/bot{token}/sendMessage"
                reply_payload = {
                    "chat_id": chat_id,
                    "text": "🏆 ¡Ticket Ganador Recibido! 🌮👑\n\nTu captura ha sido verificada y agregada al Muro de Victorias en https://reytacopicks.com.\n¡Muchas felicidades por el verde! 🟢🚀"
                }
                req = urllib.request.Request(reply_url, data=json.dumps(reply_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req)
                print(f"✅ Mensaje de recibido enviado a chat {chat_id}")
                
                # Agradecer offset
                ack_url = f"https://api.telegram.org/bot{token}/getUpdates?offset={update_id + 1}"
                urllib.request.urlopen(ack_url)
except Exception as e:
    print(f"Error: {e}")
