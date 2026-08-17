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

def es_partido_futuro_valido_clean(horario_str):
    try:
        limite_maximo = ahora + timedelta(hours=30)
        
        # 1. Fecha + Hora (ej: "17/08 • 19:00" o "17/08 21:00")
        match_fecha_hora = re.search(r'(\d{1,2})[/.-](\d{1,2})\s*(?:•|\s+)?\s*(\d{1,2}):(\d{2})', horario_str)
        if match_fecha_hora:
            dia = int(match_fecha_hora.group(1))
            mes = int(match_fecha_hora.group(2))
            hora = int(match_fecha_hora.group(3))
            minuto = int(match_fecha_hora.group(4))
            
            if hora >= 24 or minuto >= 60 or mes > 12 or dia > 31:
                return False, f"Formato inválido ({dia}/{mes} {hora}:{minuto})"
                
            anio = ahora.year
            fecha_partido = datetime(anio, mes, dia, hora, minuto, tzinfo=ahora.tzinfo)
            
            if fecha_partido <= (ahora + timedelta(minutes=5)):
                return False, f"Ya inició/terminó ({dia:02d}/{mes:02d} {hora:02d}:{minuto:02d})"
            if fecha_partido > limite_maximo:
                return False, f"Descartado fecha lejana ({dia:02d}/{mes:02d} no es de hoy)"
                
            return True, f"{dia:02d}/{mes:02d} • {hora:02d}:{minuto:02d}"

        # 2. Solo Fecha ej: "17/08"
        match_solo_fecha = re.search(r'(\d{1,2})[/.-](\d{1,2})', horario_str)
        if match_solo_fecha:
            dia = int(match_solo_fecha.group(1))
            mes = int(match_solo_fecha.group(2))
            if mes > 12 or dia > 31:
                return False, "Fecha inválida"
            if (dia == ahora.day and mes == ahora.month) or (dia == (ahora + timedelta(days=1)).day and mes == (ahora + timedelta(days=1)).month):
                return True, f"{dia:02d}/{mes:02d} • Hoy"
            else:
                return False, f"Descartado fecha lejana ({dia:02d}/{mes:02d})"

        # 3. Solo Hora (ej: "Hoy • 19:00" o "Mañana • 21:00")
        match_hora = re.search(r'(\d{1,2}):(\d{2})', horario_str)
        if match_hora:
            hora = int(match_hora.group(1))
            minuto = int(match_hora.group(2))
            
            if hora >= 24 or minuto >= 60:
                return False, f"Hora inválida ({hora}:{minuto})"
                
            if "mañana" in horario_str.lower():
                return True, f"Mañana • {hora:02d}:{minuto:02d}"
            
            fecha_partido = datetime(ahora.year, ahora.month, ahora.day, hora, minuto, tzinfo=ahora.tzinfo)
            if fecha_partido <= (ahora + timedelta(minutes=5)):
                return False, f"Ya inició/terminó (Hoy {hora:02d}:{minuto:02d})"
            return True, f"Hoy • {hora:02d}:{minuto:02d}"

        return False, "Sin horario específico confirmado"
    except Exception as e:
        return False, f"Error validación: {e}"

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
        // Descartar en vivo
        if (/en vivo|live|descanso|1[ª°]\\s*mitad|2[ª°]\\s*mitad|e-fútbol|esports|virtual/i.test(rawText)) {
            return null;
        }

        var lines = rawText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        
        var horario = "Hoy";
        var fullDateTimeLine = lines.find(l => /\\d{1,2}[\\/\\-]\\d{1,2}.*\\d{1,2}:\\d{2}/.test(l));
        var dateLine = lines.find(l => /\\d{1,2}[\\/\\-]\\d{1,2}/.test(l));
        var timeLine = lines.find(l => /^(?:0?[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/.test(l));

        if (fullDateTimeLine) horario = fullDateTimeLine;
        else if (dateLine && timeLine) horario = dateLine + " • " + timeLine;
        else if (dateLine) horario = dateLine;
        else if (timeLine) horario = "Hoy • " + timeLine;

        var teamCandidates = lines.filter(l => {
            if (l.length < 3 || l.length > 35) return false;
            if (/^(sgp|en vivo|live|hoy|mañana|resultado final|tiempo regular)$/i.test(l)) return false;
            if (/^[\\+\\-]?\\d+(\\.\\d+)?$/.test(l)) return false;
            if (/^\\d{1,2}[\\/\\:]\\d{1,2}/.test(l)) return false;
            if (/liga|copa|premier|women|femenil|tournament|champions/i.test(l) && !l.includes('Pumas') && !l.includes('América') && !l.includes('Chivas') && !l.includes('Santos')) return false;
            return true;
        });

        var local = teamCandidates[0] || "";
        var visitante = teamCandidates[1] || "";

        return {
            partido: local + " vs " + visitante,
            horario: horario
        };
    }).filter(Boolean);
    """
    results = driver.execute_script(script_extract)
    print(f"Eventos pre-match válidos encontrados en cartelera: {len(results)}")
    for r in results:
        val, msg = es_partido_futuro_valido_clean(r['horario'])
        if val:
            print(f"  ✅ {r['partido']} | Horario: {r['horario']} -> {msg}")
        else:
            print(f"  ❌ {r['partido']} | {msg}")

finally:
    driver.quit()
