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
    
    script_full_kbo = get_shadow_script() + """
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
    driver.execute_script(script_full_kbo)
    time.sleep(2)
    
    script_step2 = get_shadow_script() + """
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
    driver.execute_script(script_step2)
    time.sleep(2)
    
    script_step3 = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    var kbo = all.find(n => {
        var t = (n.textContent||'').trim().toLowerCase();
        return (t === 'kbo' || t === 'kbo league') && n.children.length === 0;
    });
    if (kbo) {
        kbo.click();
        if (kbo.parentElement) kbo.parentElement.click();
        return "Clicked KBO child";
    }
    return "KBO child not found";
    """
    res3 = driver.execute_script(script_step3)
    print(f"Paso 3: {res3}")
    time.sleep(3)
    
    evts = extract_events_from_page(driver)
    print(f"Total eventos KBO extraídos: {len(evts)}")
    for e in evts:
        print(f" ⚾ KBO: {e.get('local')} vs {e.get('visitante')} | {e.get('horario')} | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
