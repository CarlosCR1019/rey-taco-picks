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
                elif 'text' in message:
                    # Comandos de texto
                    raw_text = message.get('text', '').strip()
                    texto = raw_text.lower()
                    chat_id = message['chat']['id']
                    
                    if texto == '/start':
                        responder(chat_id, 
                            "👑 ¡Bienvenido a Rey Taco Picks Bot!\n\n"
                            "📸 Envíame fotos de tickets ganadores y las publicaré en el canal y en la web.\n\n"
                            "👑 COMANDOS DE ADMINISTRADOR:\n"
                            "• /vip correo@ejemplo.com ➔ Activa el VIP a un cliente en Supabase\n"
                            "• /quitarvip correo@ejemplo.com ➔ Revoca el VIP\n"
                            "• /usuarios ➔ Ver lista de clientes registrados\n"
                            "• /tickets ➔ Ver cuántos tickets hay guardados"
                        )
                    elif texto.startswith('/vip ') or (texto.startswith('vip ') and '@' in texto):
                        partes = raw_text.split()
                        if len(partes) >= 2:
                            target_email = partes[1].strip()
                            if supabase:
                                try:
                                    # Update profile is_premium
                                    res = supabase.table("profiles").update({"is_premium": True}).eq("email", target_email).execute()
                                    if res.data and len(res.data) > 0:
                                        responder(chat_id, f"✅ ¡ACCESO VIP ACTIVADO!\n\nEl correo {target_email} ahora tiene acceso completo a todos los picks en la web.")
                                    else:
                                        # Si no existe en profiles, intentar crearlo
                                        import uuid
                                        supabase.table("profiles").insert({"id": str(uuid.uuid4()), "email": target_email, "is_premium": True}).execute()
                                        responder(chat_id, f"✅ ¡ACCESO VIP ACTIVADO!\n\nSe creó el registro y se activó VIP para {target_email}.")
                                    print(f"   👑 VIP activado para: {target_email}")
                                except Exception as e:
                                    responder(chat_id, f"⚠️ Error al actualizar Supabase: {e}")
                            else:
                                responder(chat_id, "❌ Error: No hay conexión a Supabase.")
                        else:
                            responder(chat_id, "Uso: /vip correo@ejemplo.com")

                    elif texto.startswith('/quitarvip '):
                        partes = raw_text.split()
                        if len(partes) >= 2:
                            target_email = partes[1].strip()
                            if supabase:
                                try:
                                    supabase.table("profiles").update({"is_premium": False}).eq("email", target_email).execute()
                                    responder(chat_id, f"🚫 Acceso VIP revocado para {target_email}.")
                                except Exception as e:
                                    responder(chat_id, f"⚠️ Error: {e}")
                            else:
                                responder(chat_id, "❌ Error: Sin conexión a Supabase.")

                    elif texto == '/usuarios':
                        if supabase:
                            try:
                                res = supabase.table("profiles").select("email, is_premium").limit(20).execute()
                                if res.data:
                                    msg_users = "📋 USUARIOS REGISTRADOS:\n\n"
                                    for u in res.data:
                                        vip_icon = "👑 VIP" if u.get('is_premium') else "⚪ Free"
                                        msg_users += f"• {u.get('email', 'Sin correo')} ➔ {vip_icon}\n"
                                    responder(chat_id, msg_users)
                                else:
                                    responder(chat_id, "No hay usuarios registrados aún.")
                            except Exception as e:
                                responder(chat_id, f"Error consultando usuarios: {e}")
                        else:
                            responder(chat_id, "Sin conexión a Supabase.")

                    elif texto == '/tickets':
                        archivos = os.listdir(TICKETS_DIR)
                        fotos = [f for f in archivos if f.endswith(('.jpg', '.png', '.jpeg'))]
                        responder(chat_id, f"📸 Tickets guardados: {len(fotos)}")

                    else:
                        # 🤖 ASISTENTE IA DE ATENCIÓN AL CLIENTE 24/7 (Groq)
                        groq_key = os.getenv("GROQ_API_KEY")
                        if groq_key:
                            try:
                                from groq import Groq
                                ai_client = Groq(api_key=groq_key)
                                prompt_soporte = f"""
Eres "TacoBot", el asistente oficial de atención a clientes y soporte de Rey Taco Picks.
Un usuario en Telegram te ha enviado este mensaje:
"{raw_text}"

INFORMACIÓN OFICIAL DEL SERVICIO:
- Suscripción VIP: Acceso completo a picks +EV, Córners, Hándicaps y 3 Parlays diarios en https://rey-taco-picks-web.onrender.com y en Telegram.
- PAGO POR TRANSFERENCIA SPEI (BBVA México):
  • Banco: BBVA México
  • Titular: Carlos Alberto Gutierrez Ramirez
  • Cuenta CLABE: 012 180 01522813375 9
  • Concepto: Su correo electrónico
- CONTACTO DIRECTO WHATSAPP:
  • WhatsApp oficial de Carlos: +52 56 3933 1102 (https://wa.me/525639331102)
- FACTURACIÓN: Factura global disponible para todas las suscripciones.

INSTRUCCIONES DE RESPUESTA:
- Responde en español con tono amable, profesional y entusiasta (usa emojis acordes 🌮👑).
- Si preguntan por pagos, cuentas o cómo suscribirse, proporciona los datos de BBVA y el WhatsApp de Carlos.
- Si preguntan por términos de apuestas (Hándicap, Córners, Over/Under), explícaselos de forma sencilla y clara.
- Mantén la respuesta concisa y directa (máximo 2 párrafos).
"""
                                chat_completion = ai_client.chat.completions.create(
                                    messages=[{"role": "user", "content": prompt_soporte}],
                                    model="llama-3.1-8b-instant",
                                    temperature=0.3
                                )
                                respuesta_ia = chat_completion.choices[0].message.content.strip()
                                responder(chat_id, respuesta_ia)
                            except Exception as e:
                                print(f"   ⚠️ Error en respuesta IA: {e}")
                                responder(chat_id, "👑 ¡Hola! Para suscribirte al VIP o dudas de pagos por SPEI, puedes contactar a Carlos en WhatsApp: 5639331102 (https://wa.me/525639331102) o revisar https://rey-taco-picks-web.onrender.com 🌮")
                        else:
                            responder(chat_id, "👑 ¡Hola! Para suscribirte al VIP o dudas de pagos por SPEI, puedes contactar a Carlos en WhatsApp: 5639331102 (https://wa.me/525639331102) 🌮")
                    
        except KeyboardInterrupt:
            print("\n🛑 Listener detenido.")
            break
        except Exception as e:
            print(f"Error en loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
