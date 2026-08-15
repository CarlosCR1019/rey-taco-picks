import os
import json
import sys
import time
import urllib.request
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

TICKETS_DIR = os.path.join("..", "frontend", "public", "tickets")
os.makedirs(TICKETS_DIR, exist_ok=True)

# ============================================================
#  TELEGRAM PHOTO LISTENER
#  Escucha mensajes enviados al bot. Cuando el admin envía
#  una foto, la descarga, la guarda, y opcionalmente la
#  reenvía al canal público como "Ticket Ganador".
# ============================================================

OFFSET_FILE = os.path.join(os.path.dirname(__file__), ".telegram_offset")

def get_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def get_updates(offset=0):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=30"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode())
            return data.get('result', [])
    except Exception as e:
        print(f"Error obteniendo updates: {e}")
        return []

def download_photo(file_id, save_path):
    """Descarga una foto de Telegram usando el file_id."""
    try:
        # Obtener file_path
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            file_path = data['result']['file_path']
        
        # Descargar archivo
        download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        urllib.request.urlretrieve(download_url, save_path)
        return True
    except Exception as e:
        print(f"Error descargando foto: {e}")
        return False

def reenviar_a_canal(file_id, caption=""):
    """Reenvía la foto al canal público con caption."""
    if not CHANNEL_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        data = json.dumps({
            "chat_id": CHANNEL_ID,
            "photo": file_id,
            "caption": caption or "🏆 ¡Ticket Ganador! Otra victoria más para Rey Taco Picks 👑🌮"
        }).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
        print("   📢 Foto reenviada al canal público.")
    except Exception as e:
        print(f"   ⚠️ Error reenviando al canal: {e}")

def responder(chat_id, texto):
    """Envía una respuesta al chat."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": texto}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
    except:
        pass

def procesar_foto(update):
    """Procesa una foto recibida del admin."""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    caption = message.get('caption', '')
    photos = message.get('photo', [])
    
    if not photos:
        return
    
    # Tomar la foto de mayor resolución (última en el array)
    best_photo = photos[-1]
    file_id = best_photo['file_id']
    
    # Generar nombre único
    timestamp = int(time.time())
    filename = f"ticket_{timestamp}.jpg"
    save_path = os.path.join(TICKETS_DIR, filename)
    
    print(f"\n📸 Foto recibida de chat {chat_id}")
    
    if download_photo(file_id, save_path):
        print(f"   ✅ Guardada: {save_path}")
        
        # Guardar referencia en Supabase
        if supabase:
            try:
                supabase.table("tickets_ganadores").insert({
                    "archivo": filename,
                    "caption": caption or "Ticket Ganador",
                    "file_id": file_id
                }).execute()
                print("   ✅ Registrado en Supabase.")
            except Exception as e:
                print(f"   ⚠️ Error en Supabase (tabla puede no existir): {e}")
        
        # Reenviar al canal público
        reenviar_a_canal(file_id, caption)
        
        # Responder al admin
        responder(chat_id, f"✅ ¡Ticket guardado y publicado!\nArchivo: {filename}")
    else:
        responder(chat_id, "❌ Error al descargar la foto. Intenta de nuevo.")

def main():
    print("="*60)
    print("📸  REY TACO PICKS — Listener de Tickets Ganadores")
    print("="*60)
    print(f"Bot Token: ...{TELEGRAM_TOKEN[-8:]}")
    print(f"Canal: {CHANNEL_ID or 'No configurado'}")
    print(f"Carpeta: {os.path.abspath(TICKETS_DIR)}")
    print("\nEsperando fotos... (Envía una foto al bot para guardarla)")
    print("Presiona Ctrl+C para detener.\n")
    
    offset = get_offset()
    
    while True:
        try:
            updates = get_updates(offset)
            
            for update in updates:
                offset = update['update_id'] + 1
                save_offset(offset)
                
                message = update.get('message', {})
                
                # Si es una foto, procesarla
                if 'photo' in message:
                    procesar_foto(update)
                
                # Comandos de texto
                elif 'text' in message:
                    texto = message['text'].lower().strip()
                    chat_id = message['chat']['id']
                    
                    if texto == '/start':
                        responder(chat_id, 
                            "👑 ¡Bienvenido a Rey Taco Picks!\n\n"
                            "📸 Envíame fotos de tickets ganadores y las publicaré automáticamente.\n\n"
                            "Comandos:\n"
                            "/tickets - Ver cuántos tickets guardados\n"
                            "/start - Este mensaje"
                        )
                    elif texto == '/tickets':
                        archivos = os.listdir(TICKETS_DIR)
                        fotos = [f for f in archivos if f.endswith(('.jpg', '.png', '.jpeg'))]
                        responder(chat_id, f"📸 Tickets guardados: {len(fotos)}")
                    
        except KeyboardInterrupt:
            print("\n🛑 Listener detenido.")
            break
        except Exception as e:
            print(f"Error en loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
