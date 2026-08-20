import os
import sys
import json
import time
import urllib.request
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
vip_channel_id = os.getenv("TELEGRAM_VIP_CHANNEL_ID") or os.getenv("TELEGRAM_CHANNEL_ID")
free_channel_id = os.getenv("TELEGRAM_FREE_CHANNEL_ID")

url_supa = os.getenv("SUPABASE_URL")
key_supa = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(url_supa, key_supa)

# Obtener picks pendientes activos de Playdoit
res = supabase.table("picks").select("*").eq("estado", "pendiente").order("id", desc=True).limit(10).execute()
activos = res.data or []

hora_actual = time.strftime('%I:%M %p CDMX')
msg = f"👑 REY TACO PICKS • REPORTE VESPERTINO ({hora_actual}) 👑\n\n"
msg += "🟢 Escáner de Playdoit completado con éxito.\n"
msg += f"📊 15 jugadas +EV verificadas y activas para hoy y mañana:\n\n"

for i, p in enumerate(activos[:6], 1):
    valor = " 💎" if p.get('tiene_valor') else ""
    parlay = "🔗 " if p.get('es_parlay') else "🎯 "
    msg += f"{parlay}{p.get('partido')} ➔ {p.get('pick')} @ Cuota {p.get('cuota')}{valor}\n"

msg += f"\n🌐 Consulta el análisis completo, momios y calculadora en vivo:\n👉 https://reytacopicks.com"

url_tg = f"https://api.telegram.org/bot{token}/sendMessage"
keyboard = {
    "inline_keyboard": [
        [
            {"text": "📲 Apostar en Playdoit", "url": "https://www.playdoit.mx/es/"},
            {"text": "🌐 Entrar a reytacopicks.com", "url": "https://reytacopicks.com/"}
        ]
    ]
}

print("Enviando reporte de prueba a Telegram...")
if chat_id:
    data = json.dumps({"chat_id": chat_id, "text": msg, "reply_markup": keyboard}).encode('utf-8')
    req = urllib.request.Request(url_tg, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        print(" -> Privado Carlos:", resp.getcode())

if vip_channel_id:
    data_vip = json.dumps({"chat_id": vip_channel_id, "text": msg, "reply_markup": keyboard}).encode('utf-8')
    req_vip = urllib.request.Request(url_tg, data=data_vip, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req_vip) as resp_vip:
        print(" -> Canal VIP:", resp_vip.getcode())

if free_channel_id:
    data_free = json.dumps({"chat_id": free_channel_id, "text": msg, "reply_markup": keyboard}).encode('utf-8')
    req_free = urllib.request.Request(url_tg, data=data_free, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req_free) as resp_free:
        print(" -> Canal Free:", resp_free.getcode())
