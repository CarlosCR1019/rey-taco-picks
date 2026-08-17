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

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)

    # Click Decimal
    script_dec = """
    var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
    if (host && host.shadowRoot) {
        var btn = host.shadowRoot.querySelector('[class*="OddsFormatBoxOptionName"], [class*="OddsFormat"]');
        if (btn) {
            btn.click();
            setTimeout(function() {
                var all = Array.from(host.shadowRoot.querySelectorAll('*'));
                var dec = all.find(n => n.children.length === 0 && n.textContent.trim().toLowerCase() === 'decimal');
                if (dec) dec.click();
            }, 500);
        }
    }
    """
    driver.execute_script(script_dec)
    time.sleep(2)

    # Click 'Hoy' filter
    script_hoy = """
    var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
    if (host && host.shadowRoot) {
        var all = Array.from(host.shadowRoot.querySelectorAll('*'));
        var hoyTab = all.find(n => n.children.length === 0 && n.textContent.trim().toLowerCase() === 'hoy');
        if (hoyTab) {
            hoyTab.click();
            if (hoyTab.parentElement) hoyTab.parentElement.click();
            return true;
        }
    }
    return false;
    """
    clicked_hoy = driver.execute_script(script_hoy)
    print(f"Click pestaña 'Hoy': {clicked_hoy}")
    time.sleep(3)

    # Extract all event containers on screen
    script_extract = """
    var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
    if (!host || !host.shadowRoot) return [];
    var shadow = host.shadowRoot;

    var containers = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
    return containers.map(c => {
        var textLines = c.innerText.split('\\n').map(l => l.trim()).filter(Boolean);
        var buttons = Array.from(c.querySelectorAll('button, [class*="OddBoxButton"]')).map(b => b.innerText.replace(/\\n+/g, ' ').trim());
        return {
            raw: textLines,
            buttons: buttons
        };
    });
    """
    raw_events = driver.execute_script(script_extract)
    print(f"\nEventos crudos en pantalla de Playdoit con filtro 'Hoy': {len(raw_events)}")
    
    for ev in raw_events:
        lines = ev['raw']
        full_text = " ".join(lines)
        
        # Ignorar esports/virtual
        if re.search(r'e-f[uú]tbol|esports|virtual|cyber|gt\s*sports|2x4\s*min', full_text, re.IGNORECASE):
            continue
            
        print(f"  -> {lines}")

finally:
    driver.quit()
