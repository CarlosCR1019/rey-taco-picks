import requests
import json
import base64

API_KEY = "AIzaSyDHqhOn-Bt9_QrFJLg_yuPAzVa0Nx4T7vQ"

model = "gemini-2.5-flash-image"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"

prompt = """Generate a luxury 3D sports betting results infographic poster for 'REY TACO PICKS' in vertical 9:16 format.
- Beautiful golden shield logo of a taco wearing a crown at top with gold corner filigree.
- Title: 'REPORTE DE RESULTADOS | JORNADA DE CHAMPIONS LEAGUE' in gold embossed letters.
- Main score: 'TOTAL DE LA JORNADA: 3 / 4 ACIERTOS' with a shiny 3D golden checkmark.
- 3 winning match cards with green 'GANADO' badges.
- 1 variance loss card with 'NOTAS DEL REY'.
- Bottom gold glowing button: '+EV DETECTADO: SISTEMA FUNCIONANDO'.
- Footer: 't.me/ReyTacoPicks'.
- Background: Dark luxury casino tables with blurred gold poker chips, octane 3D render, 8k ultra detailed."""

payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ],
    "generationConfig": {
        "responseModalities": ["IMAGE", "TEXT"]
    }
}

try:
    r = requests.post(url, json=payload, timeout=60)
    print("HTTP Status:", r.status_code)
    
    if r.status_code == 200:
        data = r.json()
        # Look for image part
        candidates = data.get("candidates", [])
        for cand in candidates:
            parts = cand.get("content", {}).get("parts", [])
            for p in parts:
                inline_data = p.get("inlineData") or p.get("inline_data")
                if inline_data:
                    mime = inline_data.get("mimeType", "image/png")
                    b64 = inline_data.get("data")
                    img_bytes = base64.b64decode(b64)
                    with open("gemini_direct_output.png", "wb") as f:
                        f.write(img_bytes)
                    print(f"🎉 ¡Imagen generada exitosamente con Gemini API! Guardada en: gemini_direct_output.png ({len(img_bytes)} bytes)")
                elif "text" in p:
                    print("Respuesta de texto de Gemini:", p["text"])
    else:
        print("Error en Gemini API:", r.text)
except Exception as e:
    print("Excepción:", e)
