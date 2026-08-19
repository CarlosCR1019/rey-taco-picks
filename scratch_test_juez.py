import os
import sys
import json
import re
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from groq import Groq

load_dotenv("backend/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

sample_partidos = [
    {"categoria": "UEFA Champions League", "partido": "Dinamo Zagreb vs Qarabag FK", "local": "Dinamo Zagreb", "visitante": "Qarabag FK", "horario": "19/08 • 13:00", "cuotas_superficie": ["1.83", "3.80", "4.20"]},
    {"categoria": "UEFA Champions League", "partido": "Bodø/Glimt vs Red Star Belgrade", "local": "Bodø/Glimt", "visitante": "Red Star Belgrade", "horario": "19/08 • 13:00", "cuotas_superficie": ["1.70", "4.10", "4.50"]},
    {"categoria": "KBO", "partido": "Kia Tigers vs Kiwoom Heroes", "local": "Kia Tigers", "visitante": "Kiwoom Heroes", "horario": "19/08 • 04:30", "cuotas_superficie": ["1.48", "2.60"]},
    {"categoria": "KBO", "partido": "LG Twins vs SSG Landers", "local": "LG Twins", "visitante": "SSG Landers", "horario": "19/08 • 04:30", "cuotas_superficie": ["1.62", "2.30"]},
    {"categoria": "MLB", "partido": "DET Tigers vs PIT Pirates", "local": "DET Tigers", "visitante": "PIT Pirates", "horario": "19/08 • 10:35", "cuotas_superficie": ["1.75", "2.10"]},
    {"categoria": "MLB", "partido": "SD Padres vs NY Mets", "local": "SD Padres", "visitante": "NY Mets", "horario": "19/08 • 11:10", "cuotas_superficie": ["1.87", "1.95"]}
]

prompt = f"""
Eres el "Chief Odds Arbiter" de Rey Taco Picks. Emite la cartera oficial del día.
DATOS REALES:
{json.dumps(sample_partidos, ensure_ascii=False, indent=2)}

Devuelve ÚNICAMENTE un JSON array con 5 selecciones (1 Champions, 1 KBO, 1 MLB y 1 Parlay cruzado):
[
    {{
        "categoria": "UEFA Champions League",
        "partido": "Dinamo Zagreb vs Qarabag FK",
        "horario": "19/08 • 13:00",
        "pick": "Dinamo Zagreb Gana Directo",
        "cuota": "1.83",
        "confianza": "90%",
        "razonamiento": "Dominio local en eliminatoria previa.",
        "es_parlay": false,
        "tiene_valor": true
    }}
]
"""

for model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "groq/compound-mini"]:
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.1
        )
        txt = resp.choices[0].message.content.strip()
        print(f"\n--- RESPUESTA {model} ---")
        print(txt[:300])
        # Parse JSON
        clean = re.sub(r'```(?:json)?', '', txt).strip()
        idx1 = clean.find('[')
        idx2 = clean.rfind(']')
        if idx1 != -1 and idx2 != -1:
            data = json.loads(clean[idx1:idx2+1])
            print(f"✅ Parsed {len(data)} picks successfully!")
        else:
            print("❌ Could not find [ ] array")
    except Exception as e:
        print(f"Error {model}: {e}")
