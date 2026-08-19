import json
import re

def extract_json_array(text):
    text = re.sub(r'```(?:json)?', '', text).strip()
    try:
        idx1 = text.find('[')
        idx2 = text.rfind(']')
        if idx1 != -1 and idx2 != -1:
            return json.loads(text[idx1:idx2+1])
    except Exception:
        pass
    
    picks = []
    for m in re.finditer(r'\{[^{}]*\}', text, re.DOTALL):
        try:
            obj = json.loads(m.group(0))
            if 'pick' in obj or 'partido' in obj:
                picks.append(obj)
        except Exception:
            pass
    return picks

sample_malformed = """
Aquí está la cartera de picks:
[
  {
    "categoria": "MLB",
    "partido": "Baltimore Orioles vs New York Yankees",
    "horario": "Hoy 17:05 hrs",
    "pick": "Baltimore Orioles Hándicap +1.5",
    "cuota": "1.48",
    "confianza": "92%",
    "razonamiento": "Ventaja en pitcheo",
    "es_parlay": false,
    "tiene_valor": true
  }
]
Nota: Estos picks son válidos para hoy.
"""

parsed = extract_json_array(sample_malformed)
print(f"Picks parseados con éxito: {len(parsed)}")
print(parsed[0].get('partido'))
