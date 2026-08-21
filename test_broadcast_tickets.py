import urllib.request
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

token = "8684914807:AAHjNX6cz_sn1EUZVl0wt4v5iYWzJ8JU5UE"
vip_channel = "-1003845930328"
free_channel = "-1004387927424"

caption = """🏆 ¡TICKET GANADOR COBRADO EN PLAYDOIT! 👑🌮

✅ Victoria asegurada con nuestra estrategia de Inteligencia Artificial.
📊 El rendimiento verificado sigue sumando en verde.

👉 Únete al VIP para recibir todas las combinadas y córners: https://reytacopicks.com"""

sample_ticket = "frontend/public/tickets/ticket_1787030886.jpg"

print("📢 Probando reenvío de ticket ganador a AMBOS canales...")

for cid in [vip_channel, free_channel]:
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {
        "chat_id": cid,
        "caption": caption
    }
    # Enviar con multipart o URL
    with open(sample_ticket, "rb") as img:
        import requests
        r = requests.post(url, data={"chat_id": cid, "caption": caption}, files={"photo": img}, timeout=20)
        print(f"Canal {cid} -> Status: {r.status_code}, Ok: {r.json().get('ok')}")

print("✅ ¡Prueba de ticket completada en ambos canales!")
