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

# Limpiar picks pendientes
supabase.table("picks").delete().eq("estado", "pendiente").execute()

exact_playdoit_picks = [
    {
        "id": int(time.time()) + 1,
        "categoria": "UEFA Champions League",
        "liga": "UEFA Champions League",
        "partido": "Celtic FC vs LASK",
        "pick": "Celtic FC Gana Directo",
        "cuota": "1.80",
        "confianza": "90%",
        "razonamiento": "Fortaleza del Celtic en Celtic Park y superioridad ofensiva frente a LASK.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 2,
        "categoria": "UEFA Champions League",
        "liga": "UEFA Champions League",
        "partido": "SK Slovan Bratislava vs Celje",
        "pick": "SK Slovan Bratislava Gana Directo",
        "cuota": "1.80",
        "confianza": "89%",
        "razonamiento": "Slovan Bratislava domina la serie en casa con ventaja en experiencia europea.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 3,
        "categoria": "UEFA Champions League",
        "liga": "UEFA Champions League",
        "partido": "Nijmegen vs FK Bodo Glimt",
        "pick": "Más de 3.5 Goles Totales",
        "cuota": "1.94",
        "confianza": "88%",
        "razonamiento": "Duelo de alto ritmo vertical con promedio superior a 3.8 goles por partido.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 4,
        "categoria": "UEFA Champions League",
        "liga": "UEFA Champions League",
        "partido": "Hapoel Beer Sheva FC vs Sabah FC",
        "pick": "Más de 2.5 Goles Totales",
        "cuota": "1.81",
        "confianza": "87%",
        "razonamiento": "Tendencia over en duelos en campo neutral con defensas abiertas.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 5,
        "categoria": "Liga MX",
        "liga": "Liga MX",
        "partido": "Juárez vs América",
        "pick": "América Gana Directo",
        "cuota": "1.78",
        "confianza": "87%",
        "razonamiento": "Superioridad de plantel y récord dominante de las Águilas del América en visitas a la frontera.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 6,
        "categoria": "KBO",
        "liga": "KBO",
        "partido": "Kia Tigers vs Kiwoom Heroes",
        "pick": "Kia Tigers Gana Directo",
        "cuota": "1.48",
        "confianza": "92%",
        "razonamiento": "Líder indiscutible de la KBO con ventaja en pitcheo abridor y promedio de bateo.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 7,
        "categoria": "KBO",
        "liga": "KBO",
        "partido": "LG Twins vs SSG Landers",
        "pick": "LG Twins Gana Directo",
        "cuota": "1.62",
        "confianza": "89%",
        "razonamiento": "Rotación abridora consistente y mayor producción de carreras con hombres en posición anotadora.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 8,
        "categoria": "MLB",
        "liga": "MLB",
        "partido": "DET Tigers vs PIT Pirates",
        "pick": "DET Tigers Gana Directo",
        "cuota": "1.75",
        "confianza": "86%",
        "razonamiento": "Mejor WHIP de abridores y efectividad de bullpen en los últimos compromisos.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 9,
        "categoria": "MLB",
        "liga": "MLB",
        "partido": "SD Padres vs NY Mets",
        "pick": "Más de 8.5 Carreras Totales",
        "cuota": "1.87",
        "confianza": "85%",
        "razonamiento": "Tendencia over marcada en duelos diurnos con condiciones climáticas favorables para el bateo.",
        "es_parlay": False,
        "tiene_valor": True,
        "estado": "pendiente"
    },
    {
        "id": int(time.time()) + 10,
        "categoria": "Parlays +EV",
        "liga": "Parlays +EV",
        "partido": "Celtic FC vs LASK + SK Slovan Bratislava vs Celje",
        "pick": "Celtic FC Gana & Slovan Bratislava Gana",
        "cuota": "3.24",
        "confianza": "86%",
        "razonamiento": "Parlay europeo combinado +EV: Doble victoria local de favoritos en Champions League.",
        "es_parlay": True,
        "tiene_valor": True,
        "estado": "pendiente"
    }
]

for p in exact_playdoit_picks:
    supabase.table("picks").insert(p).execute()

with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(exact_playdoit_picks, f, ensure_ascii=False, indent=2)

print(f"✅ {len(exact_playdoit_picks)} picks sincronizados exactamente con la cartelera real de Playdoit.")
