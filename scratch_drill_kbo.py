import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_events_from_page

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    script_kbo_drill = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    
    // 1. Clic en Beisbol
    var beisbol = all.find(n => (n.textContent||'').trim().toLowerCase() === 'béisbol' && n.children.length === 0);
    if (beisbol) {
        var el = beisbol;
        while (el && el !== shadow && !el.className.includes('SportMenuItem')) el = el.parentElement;
        (el || beisbol).click();
    }
    return "Clicked Beisbol";
    """
    driver.execute_script(script_kbo_drill)
    time.sleep(2)
    
    script_corea = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    var corea = all.find(n => (n.textContent||'').trim().toLowerCase() === 'corea del sur' && n.children.length === 0);
    if (corea) {
        var el = corea;
        while (el && el !== shadow && !el.className.includes('SportMenuItem') && !el.className.includes('Category')) el = el.parentElement;
        (el || corea).click();
        return "Clicked Corea del Sur";
    }
    return "Corea not found";
    """
    res_c = driver.execute_script(script_corea)
    print(f"Paso Corea: {res_c}")
    time.sleep(2)
    
    script_kbo_champ = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    var kbo = all.find(n => {
        var t = (n.textContent||'').trim().toLowerCase();
        return (t === 'kbo' || t === 'kbo league') && n.children.length === 0;
    });
    if (kbo) {
        var el = kbo;
        while (el && el !== shadow && !el.className.includes('Championship') && !el.className.includes('SportMenuItem') && el.tagName !== 'BUTTON') el = el.parentElement;
        (el || kbo).click();
        return "Clicked KBO Championship!";
    }
    return "KBO Champ not found in: " + all.filter(n => n.children.length === 0 && n.textContent.trim().length > 0).map(n => n.textContent.trim()).slice(0, 30).join(" | ");
    """
    res_k = driver.execute_script(script_kbo_champ)
    print(f"Paso KBO: {res_k}")
    time.sleep(3)
    
    evts = extract_events_from_page(driver)
    print(f"Total eventos KBO extraídos: {len(evts)}")
    for e in evts:
        print(f" ⚾ KBO: {e.get('local')} vs {e.get('visitante')} | {e.get('horario')} | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
