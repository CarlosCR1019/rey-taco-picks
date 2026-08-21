import os
import sys
import json
import base64
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyDHqhOn-Bt9_QrFJLg_yuPAzVa0Nx4T7vQ"

print("🎨 Conectando a la API oficial de Google Gemini Imagen 3...")

url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={API_KEY}"

prompt = """Luxury sports betting daily results infographic poster for 'REY TACO PICKS' in vertical 9:16 format.
Top header: Beautiful golden shield logo of a taco wearing a royal crown with gold filigree corner ornaments.
Title banner: 'REPORTE DE RESULTADOS | JORNADA DE CHAMPIONS LEAGUE' with gold embossed lettering.
Main KPI box: 'TOTAL DE LA JORNADA: 3 / 4 ACIERTOS' with a large glowing 3D metallic golden checkmark.
Winning panel: 3 sleek dark gold cards side-by-side with match names, green checkmarks and green 'GANADO' pills.
Variance panel: One dark red card with 'PERDIDA' and 'NOTAS DEL REY' box.
Bottom button: Glowing gold metallic 3D button '+EV DETECTADO: SISTEMA FUNCIONANDO'.
Footer text: 'UNETE AL CANAL VIP: t.me/ReyTacoPicks' in clean bold typography.
Background: Dark luxury casino tables with blurred gold poker chips, subtle upward stock market lines, 8k resolution, photorealistic metallic gold reflections, octane 3D render."""

payload = {
    "instances": [
        {"prompt": prompt}
    ],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "9:16",
        "outputMimeType": "image/jpeg"
    }
}

try:
    r = requests.post(url, json=payload, timeout=60)
    print("HTTP Status:", r.status_code)
    
    if r.status_code == 200:
        data = r.json()
        predictions = data.get("predictions", [])
        if predictions:
            b64_img = predictions[0].get("bytesBase64Encoded")
            img_bytes = base64.b64decode(b64_img)
            output_file = "gemini_results_report.jpg"
            with open(output_file, "wb") as f:
                f.write(img_bytes)
            print(f"🎉 ¡Imagen generada con éxito por Google Gemini Imagen 3! Guardada en: {output_file} ({len(img_bytes)} bytes)")
        else:
            print("Respuesta sin predicciones:", data)
    else:
        print("Error en Gemini API:", r.text)
except Exception as e:
    print("Excepción conectando a Gemini:", e)
