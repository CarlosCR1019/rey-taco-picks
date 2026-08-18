import os
import sys
import json
import time
import urllib.request
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

champions_picks = [
    {
        "categoria": "UEFA Champions League",
        "partido": "Dinamo Zagreb vs Viking FK",
        "pick": "Dinamo Zagreb Gana Directo",
        "cuota": "1.71",
        "confianza": "92%",
        "tiene_valor": True,
        "es_parlay": False,
        "fecha_generacion": "2026-08-18",
        "estado": "pendiente",
        "horario": "Hoy 13:00 hrs",
        "razonamiento": "Análisis IA Champions: Dinamo Zagreb acumula 6 victorias consecutivas en playoffs europeos en el Estadio Maksimir y promedio de 2.4 goles por encuentro."
    },
    {
        "categoria": "UEFA Champions League",
        "partido": "Fenerbahce vs Lyon",
        "pick": "Más de 2.5 Goles Totales",
        "cuota": "1.85",
        "confianza": "90%",
        "tiene_valor": True,
        "es_parlay": False,
        "fecha_generacion": "2026-08-18",
        "estado": "pendiente",
        "horario": "Hoy 13:00 hrs",
        "razonamiento": "Análisis IA Champions: Duelo de alto ritmo ofensivo. Ambos equipos han superado la línea de 2.5 goles en 8 de sus últimos 10 partidos oficiales."
    }
]

# 1. Guardar en Supabase
for idx, p in enumerate(champions_picks):
    p_data = {
        "id": int(time.time()) + 100 + idx,
        "categoria": p["categoria"],
        "partido": p["partido"],
        "pick": p["pick"],
        "cuota": p["cuota"],
        "confianza": p["confianza"],
        "razonamiento": p["razonamiento"],
        "es_parlay": p["es_parlay"],
        "tiene_valor": p["tiene_valor"],
        "estado": "pendiente",
        "fecha_generacion": "2026-08-18"
    }
    
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/picks",
        data=json.dumps(p_data).encode('utf-8'),
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ Guardado en Supabase: {p['partido']} - HTTP {resp.getcode()}")
    except Exception as e:
        print(f"❌ Error guardando en Supabase: {e}")

# 2. Enviar a Telegram
url_tg = f"https://api.telegram.org/bot{token}/sendMessage"

keyboard = {
    "inline_keyboard": [
        [
            {"text": "📲 Apostar en Playdoit", "url": "https://www.playdoit.mx/es/"},
            {"text": "🌐 Dashboard en Vivo", "url": "https://reytacopicks.com/"}
        ]
    ]
}

msg_champions = """🌮 REY TACO PICKS | 🇪🇺 ESPECIAL UEFA CHAMPIONS LEAGUE 👑

🏆 [UEFA Champions League - Ronda Playoffs]
🏟️ Dinamo Zagreb vs Viking FK
🕒 Hoy 13:00 hrs CDMX

🎯 Pick: Dinamo Zagreb Gana Directo
🔥 Momio: @ 1.71 💎 VALOR +EV
📊 Confianza IA: 92%

🧠 Análisis Táctico:
Dinamo Zagreb acumula 6 victorias consecutivas en playoffs europeos en el Estadio Maksimir y promedio de 2.4 goles por encuentro.

----------------------------------
🏟️ Fenerbahce vs Lyon (Hoy 13:00 hrs)
🎯 Pick: Más de 2.5 Goles Totales @ 1.85 🔥

🌐 Consulta todos los picks y el Parlay IA en:
👉 https://reytacopicks.com
"""

# Envío a Privado Carlos
if chat_id:
    payload = {"chat_id": chat_id, "text": msg_champions, "reply_markup": keyboard}
    req = urllib.request.Request(url_tg, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ Enviado a Telegram Privado (Carlos): HTTP {resp.getcode()}")
    except Exception as e:
        print(f"❌ Error enviando a privado Carlos: {e}")

# Envío al Canal Principal (@ReyTacoPicks)
if channel_id:
    payload_c = {"chat_id": channel_id, "text": msg_champions, "reply_markup": keyboard}
    req_c = urllib.request.Request(url_tg, data=json.dumps(payload_c).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req_c) as resp:
            print(f"✅ Enviado Especial Champions a Canal Principal (@ReyTacoPicks): HTTP {resp.getcode()}")
    except Exception as e:
        print(f"❌ Error enviando Especial Champions a Canal Principal: {e}")
