import time
import json
import sys
import undetected_chromedriver as uc

sys.stdout.reconfigure(encoding='utf-8')

print("🧪 Probando extractor corregido de Playdoit (sin filtro destructivo de 'EN VIVO')...")
options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    script_fix = """
    try {
        var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
        if (!host || !host.shadowRoot) return [];
        var shadow = host.shadowRoot;
        
        var containers = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
        var result = [];
        
        containers.forEach(function(c) {
            var rawText = c.innerText.trim();
            // Descartar solo si realmente tiene marcador en vivo (ej '1 - 0' o minuto de juego '15\\'')
            if (/\\b\\d+\\s*-\\s*\\d+\\b|1[ª°]\\s*mitad|2[ª°]\\s*mitad|e-fútbol|esports|virtual|cyber/i.test(rawText)) {
                // Verificar si tiene hora futura
                if (!/\\d{1,2}:\\d{2}/.test(rawText)) return;
            }
            
            var lines = rawText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            
            // Extraer hora
            var timeLine = lines.find(l => /^(?:0?[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/.test(l)) || "Hoy";
            var dateLine = lines.find(l => /\\d{1,2}[\\/\\-]\\d{1,2}/.test(l)) || "18/08";
            
            // Extraer equipos de los contenedores de competidores
            var compEls = Array.from(c.querySelectorAll('[class*="CompetitorName"], [class*="Competitors"], [class*="NameContainer"], [class*="EventName"]'));
            var teamNames = compEls.map(el => el.innerText.trim()).filter(t => t.length >= 3);
            
            var local = teamNames[0] || "";
            var vis = teamNames[1] || "";
            
            if (!local || !vis) {
                // Fallback por líneas
                var candidates = lines.filter(l => {
                    if (l.length < 3 || l.length > 35) return false;
                    if (/^(sgp|en vivo|live|hoy|mañana|resultado final|tiempo regular|hándicap|totales|ganador)$/i.test(l)) return false;
                    if (/^[\\+\\-]?\\d+(\\.\\d+)?$/.test(l)) return false;
                    if (/^\\d{1,2}[\\/\\:]\\d{1,2}/.test(l)) return false;
                    if (/champions|league|copa|mlb|premier|laliga|liga/i.test(l)) return false;
                    return true;
                });
                if (candidates.length >= 2) {
                    local = candidates[0];
                    vis = candidates[1];
                }
            }
            
            // Extraer cuotas decimales o americanas
            var oddsEls = Array.from(c.querySelectorAll('[class*="OddButton"], [class*="Price"], [class*="OddValue"], [class*="selection"], [class*="Odds"]'));
            var odds = oddsEls.map(o => o.innerText.trim()).filter(o => o.length > 0);
            
            if (local && vis) {
                result.push({
                    partido: local + " vs " + vis,
                    local: local,
                    visitante: vis,
                    horario: dateLine + " " + timeLine + " hrs",
                    cuotas: odds,
                    raw_sample: lines.slice(0, 8).join(' | ')
                });
            }
        });
        
        return result;
    } catch(e) {
        return [{ error: e.toString() }];
    }
    """
    
    events = driver.execute_script(script_fix)
    print(f"✅ Total partidos extraídos directamente de Playdoit: {len(events)}")
    for e in events[:15]:
        print(f"🏟️ {e.get('partido')} | {e.get('horario')} | Cuotas Playdoit: {e.get('cuotas')}")

finally:
    driver.quit()
