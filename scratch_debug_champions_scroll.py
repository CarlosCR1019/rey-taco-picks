import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_events_from_page, es_partido_futuro_valido

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    script_click = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    var champBox = all.find(n => (n.className || '').includes('TopLeagueBox') && (n.textContent || '').includes('Champions'));
    if (!champBox) {
        champBox = all.find(n => (n.textContent || '').trim().toLowerCase() === 'uefa champions league' && n.children.length === 0);
    }
    if (champBox) {
        champBox.click();
        if (champBox.parentElement) champBox.parentElement.click();
        return "Clicked: " + champBox.textContent.trim();
    }
    return "Not found";
    """
    res = driver.execute_script(script_click)
    print(f"Click en Champions: {res}")
    
    for wait_sec in range(6):
        time.sleep(1.5)
        # Scroll to trigger any lazy loading
        driver.execute_script(get_shadow_script() + "var s = getShadow(); if(s) { var c = s.querySelector('div[class*=\"Content\"], div[class*=\"Event\"]'); if(c) c.scrollTop += 200; }")
        evts = extract_events_from_page(driver)
        print(f"Segundo {wait_sec*1.5 + 1.5}: {len(evts)} eventos encontrados")
        if evts:
            for e in evts:
                es_val, h_limpio = es_partido_futuro_valido(e.get('horario', 'Hoy'))
                print(f"  🏆 {e.get('partido')} | Horario: {h_limpio} (Valido: {es_val}) | Cuotas: {e.get('cuotas')}")
            break

finally:
    driver.quit()
