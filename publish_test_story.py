import requests
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

page_id = "1311611272037375"
page_token = "EAGMJ4QmnNEIBSWAiGqNKTYT3vuhTX4add90vX8zZARYJZBhpGKP1z4zDraTDySa6eIZBeNIEGA3Fa0kOiUEsa2IZCtQxa5dXVSwuFGcu1DWM59DoHZAc8BzFeSUY4KDZCd8NwJZCn76JE84ztS1pYGZARcLci4hyA7myzXZCrkGx9KG5fq809uJleG8Hpil7uuqBayusu9o6cTeLf92nihYFG6jCeZB0AUuPg9rLMhfzLmvC1XEE9tf8ouD6Xc"

msg = """👑 REY TACO PICKS 🌮 | REPORTE DE RESULTADOS DE LA JORNADA 📊

🏆 3 / 4 ACIERTOS COBRADOS EN PLAYDOIT CON VALOR MATEMÁTICO (+EV).

✅ Tigres UANL vs Atlante FC (Más de 2.5 Goles) @ 1.67 ➔ GANADO ✔️
✅ Juarez vs America (Más de 2.5 Goles) @ 1.74 ➔ GANADO ✔️
✅ WAS Nationals vs Rangers (Más de 7.5 Carreras) @ 1.95 ➔ GANADO ✔️

👉 Únete al VIP y consulta la cartera completa en:
🌐 https://reytacopicks.com
📲 Telegram: t.me/ReyTacoPicks

#ReyTacoPicks #LigaMX #ChampionsLeague #MLB #ApuestasDeportivas #PronosticosGanadores"""

img_path = "C:/Users/carlo/.gemini/antigravity/brain/cf2a58fd-07f3-4e6a-82a0-32088909339c/gemini_imagen3_results_1787277549556.jpg"

url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

with open(img_path, "rb") as img_file:
    payload = {
        "message": msg,
        "access_token": page_token
    }
    files = {"photo": img_file}
    r = requests.post(url, data=payload, files=files, timeout=30)
    print("Facebook & Instagram Post Status:", r.status_code, r.json())
