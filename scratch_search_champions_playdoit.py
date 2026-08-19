import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, es_partido_futuro_valido, extract_events_from_page, click_categoria

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    # Check all sport/league menu items inside Altenar shadow DOM
    script = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return ["No shadow root"];
    var allElements = Array.from(shadow.querySelectorAll('*'));
    var textItems = allElements
        .filter(el => el.children.length === 0 && el.textContent.trim().length > 2 && el.textContent.trim().length < 40)
        .map(el => el.textContent.trim());
    return Array.from(new Set(textItems));
    """
    items = driver.execute_script(script)
    print(f"Total text items in Altenar: {len(items)}")
    champs = [it for it in items if any(k in it.lower() for k in ['champ', 'uefa', 'europa', 'bodo', 'celtic', 'zagreb', 'fenerbahce', 'dinamo', 'slovan', 'celje', 'lask', 'malmo', 'galatasaray'])]
    print("Menciones de Champions / Equipos encontrados en Playdoit:")
    for c in champs:
        print(f" - {c}")
        
    # Test clicking 'Champions' or 'UEFA'
    for test_cat in ['Champions League', 'UEFA Champions League', 'Liga de Campeones', 'UEFA']:
        clicked = click_categoria(driver, test_cat)
        print(f"Click en '{test_cat}': {clicked}")
        if clicked:
            time.sleep(4)
            evts = extract_events_from_page(driver)
            print(f"Eventos en '{test_cat}': {len(evts)}")
            for e in evts[:5]:
                print(f"  * {e.get('partido')} [{e.get('horario')}] Cuotas: {e.get('cuotas')}")
            break
finally:
    driver.quit()
