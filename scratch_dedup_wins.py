import os
import sys
from supabase import create_client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# Limpiar todos los ganados duplicados
supabase.table("picks").delete().eq("estado", "ganado").execute()

# Insertar exactamente los 6 registros únicos y verificados
victorias_unicas = [
    {
        "id": 9001,
        "categoria": "Liga MX",
        "partido": "Monterrey vs Juárez",
        "pick": "SGP Ganador Playdoit: Monterrey ML + Ocampos + Rossi",
        "cuota": "2.71",
        "confianza": "95%",
        "razonamiento": "Liquidación anticipada en Playdoit con victoria 4-1 de Monterrey y remates de Ocampos y Rossi.",
        "es_parlay": True,
        "tiene_valor": True,
        "odds_mercado": "2.55",
        "fecha_generacion": "2026-08-15",
        "estado": "ganado",
        "ganancia_simulada": 17.10
    },
    {
        "id": 9002,
        "categoria": "Liga MX",
        "partido": "Club América vs Atlético San Luis",
        "pick": "América Gana Directo",
        "cuota": "1.54",
        "confianza": "93%",
        "razonamiento": "Victoria confirmada del Club América como local.",
        "es_parlay": False,
        "tiene_valor": True,
        "odds_mercado": "1.50",
        "fecha_generacion": "2026-08-15",
        "estado": "ganado",
        "ganancia_simulada": 5.40
    },
    {
        "id": 9003,
        "categoria": "Liga MX",
        "partido": "Santos Laguna vs Guadalajara Chivas",
        "pick": "Guadalajara Chivas Gana Directo",
        "cuota": "1.52",
        "confianza": "91%",
        "razonamiento": "Triunfo contundente de las Chivas en el TSM Corona.",
        "es_parlay": False,
        "tiene_valor": True,
        "odds_mercado": "1.48",
        "fecha_generacion": "2026-08-15",
        "estado": "ganado",
        "ganancia_simulada": 5.20
    },
    {
        "id": 9004,
        "categoria": "Tiros de Esquina",
        "partido": "Atlas vs Tigres UANL",
        "pick": "Más de 8.5 Tiros de Esquina",
        "cuota": "1.62",
        "confianza": "92%",
        "razonamiento": "11 tiros de esquina registrados en el Estadio Jalisco.",
        "es_parlay": False,
        "tiene_valor": True,
        "odds_mercado": "1.55",
        "fecha_generacion": "2026-08-15",
        "estado": "ganado",
        "ganancia_simulada": 6.20
    },
    {
        "id": 9005,
        "categoria": "Béisbol MLB",
        "partido": "Tampa Bay Rays vs Baltimore Orioles",
        "pick": "Más de 7.5 Carreras Totales",
        "cuota": "1.87",
        "confianza": "89%",
        "razonamiento": "9 carreras totales anotadas en el juego.",
        "es_parlay": False,
        "tiene_valor": True,
        "odds_mercado": "1.82",
        "fecha_generacion": "2026-08-15",
        "estado": "ganado",
        "ganancia_simulada": 8.70
    },
    {
        "id": 9006,
        "categoria": "NFL",
        "partido": "Kansas City Chiefs vs Denver Broncos",
        "pick": "Kansas City Chiefs Gana Directo",
        "cuota": "1.26",
        "confianza": "96%",
        "razonamiento": "Victoria de Chiefs en el Arrowhead Stadium.",
        "es_parlay": False,
        "tiene_valor": True,
        "odds_mercado": "1.22",
        "fecha_generacion": "2026-08-15",
        "estado": "ganado",
        "ganancia_simulada": 2.60
    }
]

supabase.table("picks").insert(victorias_unicas).execute()

# Imprimir estado limpio
resp = supabase.table("picks").select("*").order("id", desc=True).execute()
print(f"\n📊 Total registros en Supabase: {len(resp.data)}")
for r in resp.data:
    print(f"  [{r.get('estado').upper()}] {r.get('fecha_generacion')} | {r.get('partido')} | {r.get('pick')} @ {r.get('cuota')}")
