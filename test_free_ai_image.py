import urllib.request
import urllib.parse
import os
from PIL import Image, ImageDraw, ImageFont

print("Probando API gratuita de IA (Pollinations.ai / FLUX)...")

prompt = "hyperrealistic cinematic empty modern soccer football stadium at night with golden stadium lights, dramatic dark atmospheric volumetric smoke, 8k ultra detailed sports background"
encoded_prompt = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&model=flux&nologo=true"

ai_bg_path = "ai_bg_test.jpg"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    print("Descargando imagen generada por IA...")
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(ai_bg_path, "wb") as f:
            f.write(resp.read())
    print(f"✅ ¡Fondo con IA generado exitosamente! ({os.path.getsize(ai_bg_path)} bytes)")
except Exception as e:
    print(f"❌ Error generando imagen IA: {e}")
