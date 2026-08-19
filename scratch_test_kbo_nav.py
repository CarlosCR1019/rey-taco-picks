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
    
    script_expand = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    
    // 1. Clic en Béisbol
    var all = Array.from(shadow.querySelectorAll('*'));
    var beisbol = all.find(n => {
        var t = (n.textContent || '').trim().toLowerCase();
        return (t === 'béisbol' || t === 'beisbol') && n.children.length === 0;
    });
    if (beisbol) {
        var el = beisbol;
        while (el && el !== shadow && !el.className.includes('SportMenuItem') && el.tagName !== 'BUTTON') {
            el = el.parentElement;
        }
        (el || beisbol).click();
        return "Clicked Béisbol container";
    }
    return "Beisbol not found";
    """
    res1 = driver.execute_script(script_expand)
    print(f"Res 1: {res1}")
    time.sleep(3)
    
    script_find_kbo = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    
    // Buscar Corea del Sur o KBO
    var kbo = all.find(n => {
        var t = (n.textContent || '').trim().toLowerCase();
        return (t === 'kbo' || t === 'kbo league' || t === 'corea del sur') && n.children.length === 0;
    });
    if (kbo) {
        var el = kbo;
        while (el && el !== shadow && !el.className.includes('SportMenuItem') && !el.className.includes('Category') && el.tagName !== 'BUTTON') {
            el = el.parentElement;
        }
        (el || kbo).click();
        return "Clicked KBO element: " + kbo.textContent;
    }
    return "KBO not found in list: " + all.filter(n => n.children.length === 0 && n.textContent.trim().length > 0).map(n => n.textContent.trim()).slice(0, 30).join(" | ");
    """
    res2 = driver.execute_script(script_find_kbo)
    print(f"Res 2: {res2}")
    time.sleep(3)
    
    evts = extract_events_from_page(driver)
    print(f"Total eventos encontrados: {len(evts)}")
    for e in evts:
        print(f" - {e.get('local')} vs {e.get('visitante')} | {e.get('horario')} | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
