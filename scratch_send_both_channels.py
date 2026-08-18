import os
import urllib.request
import json
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
token = os.getenv("TELEGRAM_BOT_TOKEN")

vip_id = "-1003845930328" # @ReyTacoPicks (Rey Taco Picks Vip)
free_id = "-1004387927424" # @ReyTacoPicksFree (Rey Taco Picks)

print("🚀 Probando envío directo a ambos canales...")

# 1. Enviar al Canal FREE (@ReyTacoPicksFree)
msg_free = """🌮 REY TACO PICKS | PRONÓSTICO GRATUITO DEL DÍA 👑

⚾ [MLB Béisbol]
🏟️ Baltimore Orioles vs New York Yankees
🕒 Hoy 17:05 hrs CDMX

🎯 Pick Oficial: Baltimore Orioles Hándicap +1.5
🔥 Momio Playdoit: @ 1.48 💎 VALOR +EV
📊 Confianza IA: 92%

🧠 Análisis Táctico:
Discrepancia del 14% en línea de carreras. Los Orioles cubren la línea de +1.5 en el 78% de sus duelos directos ante abridores diestros.

--------------------------------------------------
🏆 [Especial UEFA Champions League - Hoy 13:00 hrs]
🏟️ Dinamo Zagreb vs Viking FK
👉 Pick: Dinamo Zagreb Gana Directo @ 1.71 💎

🔒 Accede a todos los picks exclusivos y al Parlay Bomba en el Canal VIP:
👉 Únete aquí: @carlosds1017 o en https://reytacopicks.com
"""

keyboard_free = {
    "inline_keyboard": [
        [
            {"text": "👑 Pase VIP ($299 MXN)", "url": "https://wa.me/525639331102?text=Hola,%20quiero%20el%20Pase%20VIP%20de%20Rey%20Taco%20Picks"},
            {"text": "📲 Apostar en Playdoit", "url": "https://www.playdoit.mx/es/"}
        ],
        [
            {"text": "🌐 Ver Todos los Picks en la Web", "url": "https://reytacopicks.com/"}
        ]
    ]
}

url_tg = f"https://api.telegram.org/bot{token}/sendMessage"

# Send Free
payload_f = {"chat_id": free_id, "text": msg_free, "reply_markup": keyboard_free}
req_f = urllib.request.Request(url_tg, data=json.dumps(payload_f).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req_f) as resp:
        print(f"✅ Canal FREE (@ReyTacoPicksFree - {free_id}): HTTP {resp.getcode()}")
except Exception as e:
    print(f"❌ Error canal FREE: {e}")

# Send VIP
msg_vip = """👑 REY TACO PICKS VIP - CARTERA COMPLETA 🌮

⚾ Baltimore Orioles vs New York Yankees -> Orioles +1.5 @ 1.48 💎
⚾ Boston Red Sox vs Arizona Diamondbacks -> Más de 8.5 Carreras @ 1.83 💎
⚾ Cincinnati Reds vs St. Louis Cardinals -> St. Louis Cardinals ML @ 1.74
🇪🇺 Dinamo Zagreb vs Viking FK -> Dinamo Zagreb ML @ 1.71 💎
🇪🇺 Fenerbahce vs Lyon -> Más de 2.5 Goles @ 1.85 🔥
🚀 Parlay Seguro MLB -> Orioles +1.5 & Red Sox Over 8.5 @ 2.71 🔗

🌐 Plataforma Oficial: https://reytacopicks.com
"""

keyboard_vip = {
    "inline_keyboard": [
        [
            {"text": "📲 Apostar en Playdoit", "url": "https://www.playdoit.mx/es/"},
            {"text": "🌐 Dashboard en Vivo", "url": "https://reytacopicks.com/"}
        ]
    ]
}

payload_v = {"chat_id": vip_id, "text": msg_vip, "reply_markup": keyboard_vip}
req_v = urllib.request.Request(url_tg, data=json.dumps(payload_v).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req_v) as resp:
        print(f"✅ Canal VIP (@ReyTacoPicks - {vip_id}): HTTP {resp.getcode()}")
except Exception as e:
    print(f"❌ Error canal VIP: {e}")
