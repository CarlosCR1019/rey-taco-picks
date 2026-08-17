import undetected_chromedriver as uc
import time
import json
import re
import sys
from datetime import datetime, timedelta
import zoneinfo

sys.stdout.reconfigure(encoding='utf-8')

tz = zoneinfo.ZoneInfo("America/Mexico_City")
ahora = datetime.now(tz)
print(f"Hora actual en CDMX: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")

def es_partido_futuro_valido_debug(horario_str):
    limite_maximo = ahora + timedelta(hours=30)
    
    match_fecha_hora = re.search(r'(\d{1,2})[/.-](\d{1,2})\s*(?:•|\s+)?\s*(\d{1,2}):(\d{2})', horario_str)
    if match_fecha_hora:
        dia = int(match_fecha_hora.group(1))
        mes = int(match_fecha_hora.group(2))
        hora = int(match_fecha_hora.group(3))
        minuto = int(match_fecha_hora.group(4))
        
        anio = ahora.year
        fecha_partido = datetime(anio, mes, dia, hora, minuto, tzinfo=ahora.tzinfo)
        
        if fecha_partido <= (ahora + timedelta(minutes=5)):
            return False, f"Ya inició/terminó ({dia:02d}/{mes:02d} {hora:02d}:{minuto:02d})"
            
        if fecha_partido > limite_maximo:
            return False, f"Descartado fecha lejana ({dia:02d}/{mes:02d} no es de hoy)"
            
        return True, f"{dia:02d}/{mes:02d} • {hora:02d}:{minuto:02d}"

    match_solo_fecha = re.search(r'(\d{1,2})[/.-](\d{1,2})', horario_str)
    if match_solo_fecha:
        dia = int(match_solo_fecha.group(1))
        mes = int(match_solo_fecha.group(2))
        if (dia == ahora.day and mes == ahora.month) or (dia == (ahora + timedelta(days=1)).day and mes == (ahora + timedelta(days=1)).month):
            return True, f"{dia:02d}/{mes:02d} • Hoy"
        else:
            return False, f"Descartado fecha lejana ({dia:02d}/{mes:02d})"

    match_hora = re.search(r'(\d{1,2}):(\d{2})', horario_str)
    if match_hora:
        hora = int(match_hora.group(1))
        minuto = int(match_hora.group(2))
        
        if "mañana" in horario_str.lower():
            return True, f"Mañana • {hora:02d}:{minuto:02d}"
        
        fecha_partido = datetime(ahora.year, ahora.month, ahora.day, hora, minuto, tzinfo=ahora.tzinfo)
        if fecha_partido <= (ahora + timedelta(minutes=5)):
            return False, f"Ya inició/terminó (Hoy {hora:02d}:{minuto:02d})"
        return True, f"Hoy • {hora:02d}:{minuto:02d}"
        
    return False, f"Sin horario reconocible: '{horario_str}'"

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)

    script_extract = """
    var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
    if (!host || !host.shadowRoot) return [];
    var shadow = host.shadowRoot;

    // Click hoy tab
    var all = Array.from(shadow.querySelectorAll('*'));
    var hoyTab = all.find(n => n.children.length === 0 && n.textContent.trim().toLowerCase() === 'hoy');
    if (hoyTab) hoyTab.click();

    var containers = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
    return containers.map(c => {
        var rawText = c.innerText.trim();
        var lines = rawText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        
        var horario = "Hoy";
        var fullDateTimeLine = lines.find(l => /\\d{1,2}[\\/\\-]\\d{1,2}.*\\d{1,2}:\\d{2}/.test(l));
        var dateLine = lines.find(l => /\\d{1,2}[\\/\\-]\\d{1,2}/.test(l));
        var timeLine = lines.find(l => /^\\d{1,2}:\\d{2}$/.test(l));

        if (fullDateTimeLine) horario = fullDateTimeLine;
        else if (dateLine && timeLine) horario = dateLine + " • " + timeLine;
        else if (dateLine) horario = dateLine;
        else if (timeLine) horario = "Hoy • " + timeLine;

        return {
            lines: lines,
            horario: horario
        };
    });
    """
    results = driver.execute_script(script_extract)
    print(f"Eventos encontrados: {len(results)}")
    for r in results:
        val, msg = es_partido_futuro_valido_debug(r['horario'])
        print(f"Líneas: {r['lines'][:4]} | Horario extraído: '{r['horario']}' -> Valido: {val} ({msg})")

finally:
    driver.quit()
