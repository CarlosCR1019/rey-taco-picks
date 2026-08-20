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

# Limpiar picks obsoletos de Draftea
supabase.table("picks").delete().like("categoria", "%Draftea%").execute()

draftea_remates_props = [
    {
        "id": int(time.time()) + 501,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Juan Francisco Brunetta (Tigres vs Atlante)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.48",
        "confianza": "94%",
        "razonamiento": "Brunetta es el motor ofensivo de Tigres con 2.7 tiros totales y 1.4 a puerta por partido. Al activar BANCA+ en Draftea, los tiros del sustituto también te cobran el pick.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 502,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Jordi Cortizo (Club León vs Monterrey)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.58",
        "confianza": "91%",
        "razonamiento": "Jordi Cortizo llega como generador de juego en León con alta frecuencia de disparo de media distancia. Cubierto los 90 minutos en Draftea con la casilla BANCA+.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 503,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Diber Cambindo (Club León vs Monterrey)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.52",
        "confianza": "92%",
        "razonamiento": "Delantero centro de área en León con promedio de 2.2 remates por encuentro. Con BANCA+ en Draftea, el reemplazo suma a la línea.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 504,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Oscar Estupiñán (Juárez vs América)",
        "pick": "Más de 0.5 Remates a Puerta (BANCA+)",
        "cuota": "1.65",
        "confianza": "89%",
        "razonamiento": "Referente de ataque de Bravos de Juárez promediando 1.9 disparos a portería. Cubierto al 100% en Draftea con la función de relevo.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 505,
        "categoria": "Draftea BANCA+",
        "liga": "Liga MX",
        "partido": "Dúo BANCA+ Draftea: Brunetta + Cortizo",
        "pick": "Brunetta (+0.5 Remates) & Cortizo (+0.5 Remates)",
        "cuota": "3.00",
        "confianza": "90%",
        "razonamiento": "Dúo estelar para meter en la app de Draftea con BANCA+ activado: combina a los dos creadores de juego con mayor volumen de tiro de la jornada.",
        "es_parlay": True,
        "tiene_valor": True,
        "estado": "pendiente"
    }
]

for p in draftea_remates_props:
    supabase.table("picks").insert(p).execute()

# Actualizar picks.json completo
resp = supabase.table("picks").select("*").eq("estado", "pendiente").order("id", desc=True).execute()
with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(resp.data, f, ensure_ascii=False, indent=2)

print(f"✅ Supabase y picks.json actualizados con {len(resp.data)} picks oficiales de Remates a Puerta (Draftea BANCA+).")
