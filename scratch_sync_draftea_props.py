import os
import sys
import json
import time
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Read existing picks from Supabase
resp = supabase.table("picks").select("*").eq("estado", "pendiente").execute()
current_picks = resp.data or []
print(f"Picks pendientes actuales: {len(current_picks)}")

draftea_props = [
    {
        "id": int(time.time()) + 101,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Henry Martín (América vs Juárez)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.50",
        "confianza": "92%",
        "razonamiento": "Henry Martín promedia 2.1 tiros a puerta/partido. Con la regla BANCA+ de Draftea, los remates del suplente también te pagan el boleto.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 102,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Sergio Canales (Monterrey vs León)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.62",
        "confianza": "89%",
        "razonamiento": "Eje ofensivo de Rayados con 2.4 remates/juego y tiros libres directos. Cubierto 90 minutos con sustitución activa.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 103,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Dúo Liga MX: Henry Martín + Sergio Canales",
        "pick": "Henry Martín (+0.5 Remates) & Sergio Canales (+0.5 Remates)",
        "cuota": "2.43",
        "confianza": "88%",
        "razonamiento": "Dúo de alto valor esperado (+EV) en la app de Draftea combinando a los delanteros de mayor volumen de tiro.",
        "es_parlay": True,
        "tiene_valor": True,
        "estado": "pendiente"
    }
]

for dp in draftea_props:
    if not any(p.get('partido') == dp['partido'] for p in current_picks):
        supabase.table("picks").insert(dp).execute()
        current_picks.append(dp)

# Update local picks.json
with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(current_picks, f, ensure_ascii=False, indent=2)

print(f"✅ Supabase y picks.json actualizados con {len(current_picks)} picks totales (Playdoit + Draftea).")
