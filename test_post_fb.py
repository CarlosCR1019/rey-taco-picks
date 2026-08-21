import urllib.request
import urllib.parse
import json
import requests

page_id = "1311611272037375"
page_token = "EAGMJ4QmnNEIBSeRYZBHNWeBRoPhaanZBCrnhlYLqFOWHe2PJXo02G7GJG6ZAHCg8JbMymvdYZBgaTrKuvk1VgyTzLy88BMHiUYynaeki8GYcBmXzFeFsQmTtgosIVStd2hgEnStWONrQlhNwY4N0TxAZBQz9VZBpZAZABVffwenzTUWVJeFqsCmZBjbioCKNlavxEz5RptcQ1TVJ8ms2XDNxfFx5fShyoZCXQhkb2xQTpcGjanvCspyq6dMmsZD"

msg = """🌮👑 ¡PRONÓSTICOS DEPORTIVOS DE HOY CON IA! 👑🌮

Aquí tienes los 3 picks destacados del día con valor matemático (+EV) y ventaja estadística calculada por nuestros modelos.

📊 Consulta los análisis completos, el Parlay del Día y las cuotas en vivo en nuestra plataforma:
👉 https://reytacopicks.com

#ReyTacoPicks #LigaMX #ChampionsLeague #MLB #ApuestasDeportivas #PronosticosGratis #ParlayIA"""

url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

with open("banner_hoy.png", "rb") as img_file:
    payload = {
        "message": msg,
        "access_token": page_token
    }
    files = {"source": img_file}
    r = requests.post(url, data=payload, files=files, timeout=30)
    print("Post Response:", r.json())
