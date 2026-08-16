import undetected_chromedriver as uc
import time
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

print("Iniciando Chrome para inspeccionar Playdoit...")
driver = uc.Chrome(options=options)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(12)

    # Click en Futbol o Liga MX
    script = """
    function getShadow() {
        var host = document.querySelector('asb-sports-app, asb-app, altenar-app');
        if (!host) {
            var all = document.querySelectorAll('*');
            for (var i = 0; i < all.length; i++) {
                if (all[i].shadowRoot) { host = all[i]; break; }
            }
        }
        return host ? host.shadowRoot : null;
    }
    var shadow = getShadow();
    if (!shadow) return 'NO_SHADOW';
    
    // Extraer todos los contenedores de eventos
    var containers = shadow.querySelectorAll('div[class*="EventBoxContainer"]');
    var list = [];
    containers.forEach(function(c) {
        var text = c.innerText.trim();
        if (text) {
            list.push(text);
        }
    });
    return list;
    """
    
    events = driver.execute_script(script)
    print(f"Total eventos encontrados en Playdoit: {len(events) if isinstance(events, list) else events}")
    if isinstance(events, list):
        for i, ev in enumerate(events[:25], 1):
            lineas = ev.split("\n")
            print(f"\n[{i}] ------------------------------------")
            print(f"    {' | '.join(lineas[:6])}")
finally:
    driver.quit()
