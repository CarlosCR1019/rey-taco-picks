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
        
        # 1. Fecha y hora: 16/08 • 08:00 o 16/08 17:00
        match_fecha_hora = re.search(r'(\d{1,2})[/.-](\d{1,2})\s*(?:•|\s+)?\s*(\d{1,2}):(\d{2})', horario_str)
        if match_fecha_hora:
            dia = int(match_fecha_hora.group(1))
            mes = int(match_fecha_hora.group(2))
            hora = int(match_fecha_hora.group(3))
            minuto = int(match_fecha_hora.group(4))
            
            anio = ahora.year
            fecha_partido = datetime(anio, mes, dia, hora, minuto, tzinfo=ahora.tzinfo if hasattr(ahora, 'tzinfo') and ahora.tzinfo else None)
            
            if fecha_partido <= (ahora + timedelta(minutes=5)):
                return False, f"DESCARTADO: Ya inició/terminó ({dia:02d}/{mes:02d} {hora:02d}:{minuto:02d} vs Hora CDMX {ahora.strftime('%H:%M')})"
            return True, f"VÁLIDO: {dia:02d}/{mes:02d} • {hora:02d}:{minuto:02d}"

        # 2. Solo hora
        match_hora = re.search(r'(\d{1,2}):(\d{2})', horario_str)
        if match_hora:
            hora = int(match_hora.group(1))
            minuto = int(match_hora.group(2))
            
            if "mañana" in horario_str.lower() or "tomorrow" in horario_str.lower():
                return True, f"VÁLIDO: Mañana {hora:02d}:{minuto:02d}"
            
            fecha_partido = datetime(ahora.year, ahora.month, ahora.day, hora, minuto, tzinfo=ahora.tzinfo if hasattr(ahora, 'tzinfo') and ahora.tzinfo else None)
            if fecha_partido <= (ahora + timedelta(minutes=5)):
                return False, f"DESCARTADO: Ya inició/terminó ({hora:02d}:{minuto:02d} vs Hora CDMX {ahora.strftime('%H:%M')})"
            return True, f"VÁLIDO: Hoy {hora:02d}:{minuto:02d}"
            
        return True, "SIN_HORA"
    except Exception as e:
        return True, str(e)

test_cases = [
    "16/08 • 08:00",
    "16/08 • 09:00",
    "16/08 • 12:00",
    "16/08 • 17:00",
    "16/08 • 19:10",
    "16/08 • 21:00",
    "17/08 • 19:00"
]

print(f"HORA ACTUAL DE CDMX: {datetime.now(zoneinfo.ZoneInfo('America/Mexico_City')).strftime('%Y-%m-%d %H:%M:%S')}\n")
for tc in test_cases:
    valido, razon = es_partido_futuro_valido(tc)
    print(f"  [{tc}] -> Valido: {valido} | {razon}")
