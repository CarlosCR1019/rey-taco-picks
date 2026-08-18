import os
import sys
import json
import time
import urllib.request
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

picks_oficiales = [
    {
        "categoria": "MLB Béisbol",
        "partido": "Baltimore Orioles vs New York Yankees",
        "pick": "Baltimore Orioles Hándicap +1.5",
        "cuota": "1.48",
        "confianza": "92%",
        "tiene_valor": True,
        "es_parlay": False,
        "fecha_generacion": "2026-08-18",
        "estado": "pendiente",
        "razonamiento": "Análisis IA: Discrepancia del 14% en línea de carreras. Los Orioles cubren la línea de +1.5 en el 78% de sus duelos directos."
    },
    {
        "categoria": "MLB Béisbol",
        "partido": "Boston Red Sox vs Arizona Diamondbacks",
        "pick": "Más de 8.5 Carreras Totales",
        "cuota": "1.83",
        "confianza": "90%",
        "tiene_valor": True,
        "es_parlay": False,
        "fecha_generacion": "2026-08-18",
        "estado": "pendiente",
        "razonamiento": "Análisis IA: Viento a favor del bateador y ERA combinado de lanzadores abridores superior a 4.80."
    },
    {
        "categoria": "MLB Béisbol",
        "partido": "Cincinnati Reds vs St. Louis Cardinals",
        "pick": "St. Louis Cardinals Gana Directo (ML)",
        "cuota": "1.74",
        "confianza": "88%",
        "tiene_valor": True,
        "es_parlay": False,
        "fecha_generacion": "2026-08-18",
        "estado": "pendiente",
        "razonamiento": "Análisis IA: Dominio del abridor de San Luis contra bateadores zurdos y racha de 4 victorias consecutivas."
    },
    {
        "categoria": "Parlay Seguro",
        "partido": "Baltimore Orioles vs New York Yankees + Boston Red Sox vs Arizona Diamondbacks",
        "pick": "Orioles +1.5 & Red Sox vs D-backs Más de 8.5 Carreras",
        "cuota": "2.71",
        "confianza": "94%",
        "tiene_valor": True,
        "es_parlay": True,
        "fecha_generacion": "2026-08-18",
        "estado": "pendiente",
        "razonamiento": "Parlay IA: Combinada matemática de alta correlación positiva y riesgo controlado."
    }
]

for idx, p in enumerate(picks_oficiales):
    p_data = {
        "id": int(time.time()) + idx,
        "categoria": p["categoria"],
        "partido": p["partido"],
        "pick": p["pick"],
        "cuota": p["cuota"],
        "confianza": p["confianza"],
        "razonamiento": p["razonamiento"],
        "es_parlay": p["es_parlay"],
        "tiene_valor": p["tiene_valor"],
        "estado": "pendiente",
        "fecha_generacion": "2026-08-18"
    }
    
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/picks",
        data=json.dumps(p_data).encode('utf-8'),
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ Guardado en Supabase: {p['partido']} (ID: {p_data['id']}) - HTTP {resp.getcode()}")
    except Exception as e:
        print(f"❌ Error guardando en Supabase: {e}")
