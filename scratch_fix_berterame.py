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

# Eliminar picks antiguos con Canales
supabase.table("picks").delete().like("partido", "%Canales%").execute()
supabase.table("picks").delete().like("categoria", "%Draftea%").execute()

real_draftea_props = [
    {
        "id": int(time.time()) + 201,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Henry Martín (América vs Juárez)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.50",
        "confianza": "92%",
        "razonamiento": "Henry Martín lidera la ofensiva del América con 2.3 tiros a puerta/partido. Con la regla BANCA+ de Draftea, los remates del suplente también te pagan el boleto.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 202,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Germán Berterame (Monterrey vs León)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.58",
        "confianza": "90%",
        "razonamiento": "Germán Berterame es el delantero centro titular y goleador de Rayados con 2.8 remates/juego. Cubierto 90 minutos con sustitución activa.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 203,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Dúo Liga MX: Henry Martín + Germán Berterame",
        "pick": "Henry Martín (+0.5 Remates) & Germán Berterame (+0.5 Remates)",
        "cuota": "2.37",
        "confianza": "89%",
        "razonamiento": "Dúo de alto valor esperado (+EV) en Draftea combinando a los dos delanteros centros titulares más letales de la jornada de Liga MX.",
        "es_parlay": True,
        "tiene_valor": True,
        "estado": "pendiente"
    }
]

for p in real_draftea_props:
    supabase.table("picks").insert(p).execute()

# Actualizar picks.json completo
resp = supabase.table("picks").select("*").eq("estado", "pendiente").order("id", desc=True).execute()
with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(resp.data, f, ensure_ascii=False, indent=2)

print(f"✅ Supabase y picks.json actualizados con {len(resp.data)} picks vigentes (Berterame y Henry Martín).")
