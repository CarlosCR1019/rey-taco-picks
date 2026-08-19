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
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var target = all.find(n => {
        var txt = (n.textContent || '').trim().toLowerCase();
        return (txt === 'uefa champions league' || txt === 'champions league' || txt.includes('champions league')) && n.children.length === 0;
    });
    if (target) {
        var el = target;
        while (el && el !== shadow && el.tagName !== 'BUTTON' && el.tagName !== 'A' && !(el.getAttribute('class')||'').includes('Box') && !(el.getAttribute('class')||'').includes('Item')) {
            el = el.parentElement;
        }
        if (el) {
            el.click();
            return "Clicked: " + (el.getAttribute('class') || el.tagName);
        }
        target.click();
        return "Clicked target";
    }
    return "Not found";
    """
    res = driver.execute_script(script_click)
    print(f"Click resultado: {res}")
    time.sleep(3)
    
    evts = []
    for _ in range(5):
        evts = extract_events_from_page(driver)
        if evts: break
        time.sleep(1)
        
    print(f"Total eventos de Champions extraídos: {len(evts)}")
    for e in evts:
        es_val, h_limpio = es_partido_futuro_valido(e.get('horario', 'Hoy'))
        print(f"  🏆 {e.get('partido')} | Horario: {h_limpio} (Valido: {es_val}) | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
