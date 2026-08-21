import requests
import os

page_id = "1311611272037375"
page_token = "EAGMJ4QmnNEIBSWAiGqNKTYT3vuhTX4add90vX8zZARYJZBhpGKP1z4zDraTDySa6eIZBeNIEGA3Fa0kOiUEsa2IZCtQxa5dXVSwuFGcu1DWM59DoHZAc8BzFeSUY4KDZCd8NwJZCn76JE84ztS1pYGZARcLci4hyA7myzXZCrkGx9KG5fq809uJleG8Hpil7uuqBayusu9o6cTeLf92nihYFG6jCeZB0AUuPg9rLMhfzLmvC1XEE9tf8ouD6Xc"

msg = """👑 REY TACO PICKS OFICIAL 🌮

🎯 Pronósticos Deportivos con Inteligencia Artificial & Valor Matemático (+EV).

Aquí tienes los 3 picks del día analizados por nuestros modelos predictivos.

📊 Consulta el análisis completo, momios y el Parlay del Día en nuestra plataforma:
👉 https://reytacopicks.com

#ReyTacoPicks #LigaMX #ChampionsLeague #MLB #ApuestasDeportivas #PronosticosGratis #ParlayIA"""

url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

banner_path = os.path.join(os.path.dirname(__file__), "backend", "banner_hoy.png") if os.path.exists("backend/banner_hoy.png") else "banner_hoy.png"

with open(banner_path, "rb") as img_file:
    payload = {
        "message": msg,
        "access_token": page_token
    }
    files = {"source": img_file}
    r = requests.post(url, data=payload, files=files, timeout=30)
    print("Post Response:", r.json())
