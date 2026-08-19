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
    
    # 1. Extraer Champions League
    print("\n--- EXTRAYENDO CHAMPIONS LEAGUE ---")
    script_champ = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var target = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase().includes('champions league'));
    if (target) {
        var el = target;
        while (el && el !== shadow && el.tagName !== 'BUTTON' && el.tagName !== 'A' && !(el.getAttribute('class')||'').includes('Box') && !(el.getAttribute('class')||'').includes('Item')) {
            el = el.parentElement;
        }
        (el || target).click();
        return true;
    }
    return false;
    """
    driver.execute_script(script_champ)
    time.sleep(3)
    evts_champ = extract_events_from_page(driver)
    print(f"Total Champions: {len(evts_champ)}")
    for e in evts_champ:
        print(f" 🇪🇺 {e.get('local')} vs {e.get('visitante')} | {e.get('horario')} | {e.get('cuotas')}")
        
    # 2. Extraer KBO
    print("\n--- EXTRAYENDO KBO ---")
    script_beis = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var beis = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase() === 'béisbol');
    if (beis) {
        var el = beis;
        while (el && el !== shadow && !el.className.includes('SportMenuItem') && el.tagName !== 'BUTTON') el = el.parentElement;
        (el || beis).click();
        return true;
    }
    return false;
    """
    driver.execute_script(script_beis)
    time.sleep(2)
    
    script_kbo = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var kbo = all.find(n => n.children.length === 0 && ((n.textContent||'').trim().toLowerCase() === 'corea del sur' || (n.textContent||'').trim().toLowerCase() === 'kbo'));
    if (kbo) {
        var el = kbo;
        while (el && el !== shadow && !el.className.includes('SportMenuItem') && !el.className.includes('Category') && el.tagName !== 'BUTTON') el = el.parentElement;
        (el || kbo).click();
        return true;
    }
    return false;
    """
    driver.execute_script(script_kbo)
    time.sleep(2)
    
    script_kbo_league = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var kbo = all.find(n => n.children.length === 0 && ((n.textContent||'').trim().toLowerCase() === 'kbo' || (n.textContent||'').trim().toLowerCase() === 'kbo league'));
    if (kbo) {
        var el = kbo;
        while (el && el !== shadow && !el.className.includes('Championship') && !el.className.includes('SportMenuItem') && el.tagName !== 'BUTTON') el = el.parentElement;
        (el || kbo).click();
        return true;
    }
    return false;
    """
    driver.execute_script(script_kbo_league)
    time.sleep(3)
    
    evts_kbo = extract_events_from_page(driver)
    print(f"Total KBO: {len(evts_kbo)}")
    for e in evts_kbo:
        print(f" 🇰🇷 {e.get('local')} vs {e.get('visitante')} | {e.get('horario')} | {e.get('cuotas')}")

finally:
    driver.quit()
