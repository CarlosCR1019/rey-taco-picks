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

picks = [
    {
        "id": int(time.time()) + 1,
        "categoria": "UEFA Champions League",
        "liga": "UEFA Champions League",
        "partido": "Dinamo Zagreb vs Qarabag FK",
        "pick": "Dinamo Zagreb Gana Directo",
        "cuota": "1.83",
        "confianza": "90%",
        "razonamiento": "Fuerte localía y experiencia en fase eliminatoria de Champions League.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 2,
        "categoria": "UEFA Champions League",
        "liga": "UEFA Champions League",
        "partido": "Bodø/Glimt vs Red Star Belgrade",
        "pick": "Bodø/Glimt Gana Directo",
        "cuota": "1.70",
        "confianza": "88%",
        "razonamiento": "Condición de cancha sintética ártica y alto volumen ofensivo de Bodø/Glimt.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 3,
        "categoria": "Liga MX",
        "liga": "Liga MX",
        "partido": "Juarez vs America",
        "pick": "América Gana Directo",
        "cuota": "1.78",
        "confianza": "87%",
        "razonamiento": "Dominio histórico de las Águilas y profundidad de plantilla superior en Liga MX.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 4,
        "categoria": "KBO",
        "liga": "KBO",
        "partido": "Kia Tigers vs Kiwoom Heroes",
        "pick": "Kia Tigers Gana Directo",
        "cuota": "1.48",
        "confianza": "92%",
        "razonamiento": "Líder de la liga coreana con ventaja contundente en pitcheo abridor y bateo.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 5,
        "categoria": "KBO",
        "liga": "KBO",
        "partido": "LG Twins vs SSG Landers",
        "pick": "LG Twins Gana Directo",
        "cuota": "1.62",
        "confianza": "89%",
        "razonamiento": "Rotación sólida y ofensiva oportuna en series interligas de KBO.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 6,
        "categoria": "MLB",
        "liga": "MLB",
        "partido": "DET Tigers vs PIT Pirates",
        "pick": "DET Tigers Gana Directo",
        "cuota": "1.75",
        "confianza": "86%",
        "razonamiento": "Mejor WHIP de abridores y efectividad de bullpen en últimos 5 juegos.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 7,
        "categoria": "MLB",
        "liga": "MLB",
        "partido": "SD Padres vs NY Mets",
        "pick": "Más de 8.5 Carreras Totales",
        "cuota": "1.87",
        "confianza": "85%",
        "razonamiento": "Tendencia over en duelos diurnos con condiciones de viento favorables.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 8,
        "categoria": "Parlays +EV",
        "liga": "Parlays +EV",
        "partido": "Dinamo Zagreb vs Qarabag FK + Kia Tigers vs Kiwoom Heroes",
        "pick": "Dinamo Zagreb Gana & Kia Tigers Gana",
        "cuota": "2.71",
        "confianza": "85%",
        "razonamiento": "Combinada cruzada de alta probabilidad matemática +EV (Champions + KBO).",
        "es_parlay": True,
        "tiene_valor": True,
        "estado": "pendiente"
    }
]

# 1. Limpiar pendientes obsoletos
supabase.table("picks").delete().eq("estado", "pendiente").execute()

# 2. Insertar picks actualizados
for p in picks:
    supabase.table("picks").insert(p).execute()

# 3. Guardar en picks.json local
with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(picks, f, ensure_ascii=False, indent=2)

print(f"✅ {len(picks)} picks de cartera balanceada subidos a Supabase y guardados en picks.json.")
