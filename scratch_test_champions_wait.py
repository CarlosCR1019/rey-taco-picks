import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_events_from_page, es_partido_futuro_valido, click_category

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    script_click = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var allNodes = Array.from(shadow.querySelectorAll('*'));
    var target = allNodes.find(n => n.children.length === 0 && (
        n.textContent.trim().toLowerCase() === 'uefa champions league' ||
        n.textContent.trim().toLowerCase() === 'champions league' ||
        n.textContent.trim().toLowerCase().includes('champions')
    ));
    if (target) {
        target.click();
        if (target.parentElement) target.parentElement.click();
        return true;
    }
    return false;
    """
    clicked = driver.execute_script(script_click)
    print(f"Click en Champions: {clicked}")
    time.sleep(3)
    
    for i in range(5):
        evts = extract_events_from_page(driver)
        print(f"Intento {i+1}: {len(evts)} eventos encontrados")
        if evts:
            for e in evts:
                es_val, h_limpio = es_partido_futuro_valido(e.get('horario', 'Hoy'))
                print(f" - {e.get('partido')} | Raw: '{e.get('horario')}' -> Valido: {es_val} ({h_limpio}) | Cuotas: {e.get('cuotas')}")
            break
        time.sleep(2)
finally:
    driver.quit()
