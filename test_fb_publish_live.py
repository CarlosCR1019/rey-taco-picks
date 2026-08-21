import requests
import json

page_id = "1311611272037375"
page_token = "EAGMJ4QmnNEIBSWAiGqNKTYT3vuhTX4add90vX8zZARYJZBhpGKP1z4zDraTDySa6eIZBeNIEGA3Fa0kOiUEsa2IZCtQxa5dXVSwuFGcu1DWM59DoHZAc8BzFeSUY4KDZCd8NwJZCn76JE84ztS1pYGZARcLci4hyA7myzXZCrkGx9KG5fq809uJleG8Hpil7uuqBayusu9o6cTeLf92nihYFG6jCeZB0AUuPg9rLMhfzLmvC1XEE9tf8ouD6Xc"

msg = """🌮👑 ¡PRONÓSTICOS DEPORTIVOS DE HOY CON INTELIGENCIA ARTIFICIAL! 👑🌮

Aquí tienes los 3 picks del día con valor matemático (+EV) y ventaja estadística analizados por nuestros modelos.

📊 Consulta los análisis completos, momios y el Parlay del Día en nuestra plataforma:
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
