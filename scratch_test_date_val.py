import re
from datetime import datetime, timedelta
import zoneinfo

def es_partido_futuro_valido(horario_str):
    try:
        try:
            tz = zoneinfo.ZoneInfo("America/Mexico_City")
            ahora = datetime.now(tz)
        except Exception:
            ahora = datetime.utcnow() - timedelta(hours=6)
        
        limite_maximo = ahora + timedelta(hours=30)
        
        match_fecha_hora = re.search(r'(\d{1,2})[/.-](\d{1,2})\s*(?:•|\s+)?\s*(\d{1,2}):(\d{2})', horario_str)
        if match_fecha_hora:
            dia = int(match_fecha_hora.group(1))
            mes = int(match_fecha_hora.group(2))
            hora = int(match_fecha_hora.group(3))
            minuto = int(match_fecha_hora.group(4))
            
            if hora >= 24 or minuto >= 60 or mes > 12 or dia > 31:
                return False, f"Formato inválido ({dia}/{mes} {hora}:{minuto})"
            
            anio = ahora.year
            fecha_partido = datetime(anio, mes, dia, hora, minuto, tzinfo=ahora.tzinfo if hasattr(ahora, 'tzinfo') and ahora.tzinfo else None)
            
            if fecha_partido <= (ahora + timedelta(minutes=5)):
                return False, f"Ya inició/terminó ({dia:02d}/{mes:02d} {hora:02d}:{minuto:02d}) vs ahora ({ahora})"
                
            if fecha_partido > limite_maximo:
                return False, f"Descartado fecha lejana ({dia:02d}/{mes:02d} no es de hoy)"
                
            return True, f"{dia:02d}/{mes:02d} • {hora:02d}:{minuto:02d}"

        return False, "No match"
    except Exception as e:
        return False, str(e)

test_cases = [
    "18/08 13:00 hrs",
    "18/08 16:40 hrs",
    "18/08 17:10 hrs",
    "18/08 18:40 hrs",
    "19/08 13:00 hrs",
    "21/08 13:00 hrs"
]

for t in test_cases:
    val, res = es_partido_futuro_valido(t)
    print(f"'{t}' -> {val} ({res})")
