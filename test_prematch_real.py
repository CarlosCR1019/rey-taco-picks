import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)

    # Click Decimal format
    script_dec = """
    function getShadow() {
        var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
        if (host && host.shadowRoot) return host.shadowRoot;
        var all = document.querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
            if (all[i].shadowRoot) return all[i].shadowRoot;
        }
        return null;
    }
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var decimalBtn = all.find(n => n.textContent && n.textContent.trim().toLowerCase() === 'decimal' && n.children.length === 0);
    if(decimalBtn) { decimalBtn.click(); return true; }
    return false;
    """
    driver.execute_script(script_dec)
    time.sleep(2)

    # Robust pre-match extractor
    script_parse = """
    function getShadow() {
        var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
        if (host && host.shadowRoot) return host.shadowRoot;
        var all = document.querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
            if (all[i].shadowRoot) return all[i].shadowRoot;
        }
        return null;
    }
    var shadow = getShadow();
    if (!shadow) return [];
    var containers = shadow.querySelectorAll('div[class*="EventBoxContainer"]');
    var result = [];

    containers.forEach(function(c) {
        try {
            var rawText = c.innerText.trim();
            var lines = rawText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            
            // Si tiene minutos de juego activos (ej: 24:19, 71:40, Descanso, 1ª mitad)
            var esEnJuegoAhora = lines.some(l => /^(\\d{1,2}:\\d{2}|descanso|1[ª°]\\s*mitad|2[ª°]\\s*mitad)$/i.test(l));
            if (esEnJuegoAhora) return;

            // Buscar fecha y hora (ej: 16/08 • 12:00 o 16 de ago. 17:00)
            var horario = "Hoy";
            var dateLine = lines.find(l => /\\d{1,2}[\\/\\-]\\d{1,2}|\\d{1,2}\\s+de\\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)/i.test(l));
            var timeLine = lines.find(l => /^\\d{1,2}:\\d{2}$/.test(l));

            if (dateLine) {
                horario = dateLine;
            } else if (timeLine) {
                horario = "Hoy " + timeLine + " hrs";
            }

            // Extraer nombres de equipos
            // En Altenar, los nombres suelen ser líneas con letras sin números ni signos de momio
            var teamCandidates = lines.filter(l => {
                if (l.length < 3 || l.length > 35) return false;
                if (/^(sgp|en vivo|live|hoy|mañana|resultado final|tiempo regular)$/i.test(l)) return false;
                if (/^[\\+\\-]?\\d+(\\.\\d+)?$/.test(l)) return false;
                if (/^\\d{1,2}[\\/\\:]\\d{1,2}/.test(l)) return false;
                if (/liga|copa|premier|women|femenil|tournament|champions/i.test(l) && !l.includes('Pumas') && !l.includes('América') && !l.includes('Chivas') && !l.includes('Santos')) return false;
                return true;
            });

            if (teamCandidates.length >= 2) {
                var local = teamCandidates[0];
                var visitante = teamCandidates[1];

                // Extraer cuotas
                var oddsElements = c.querySelectorAll('button[class*="OddBoxButton-"], div[class*="OddBox-"]');
                var cuotas = [];
                oddsElements.forEach(function(o) {
                    var val = o.innerText.trim();
                    if (val) cuotas.push(val.replace('\\n', ' '));
                });

                result.push({
                    local: local,
                    visitante: visitante,
                    partido: local + " vs " + visitante,
                    horario: horario,
                    cuotas: cuotas,
                    texto_completo: rawText.replace(/\\n+/g, ' | ')
                });
            }
        } catch(e) {}
    });
    return result;
    """
    matches = driver.execute_script(script_parse)
    print(f"\n==========================================")
    print(f"🔥 PARTIDOS PRE-MATCH 100% REALES EXTRAÍDOS ({len(matches)}):")
    print(f"==========================================")
    for m in matches:
        print(f"👉 [{m['horario']}] {m['partido']} | Cuotas: {m['cuotas'][:4]}")
finally:
    driver.quit()
