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
    
    script_kbo = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    
    // 1. Encontrar Beisbol o KBO o Corea del Sur
    var kboBtn = all.find(n => {
        var t = (n.textContent || '').trim().toLowerCase();
        return (t === 'kbo' || t === 'kbo league' || t === 'corea del sur' || t === 'corea') && n.children.length === 0;
    });
    if (kboBtn) {
        var el = kboBtn;
        while (el && el !== shadow && el.tagName !== 'BUTTON' && el.tagName !== 'A' && !(el.getAttribute('class')||'').includes('Box') && !(el.getAttribute('class')||'').includes('Item')) {
            el = el.parentElement;
        }
        if (el) {
            el.click();
            return "Clicked KBO: " + (el.getAttribute('class') || el.tagName);
        }
        kboBtn.click();
        return "Clicked KBO direct";
    }
    
    // Si no esta en primer nivel, buscar Beisbol primero
    var beisbol = all.find(n => {
        var t = (n.textContent || '').trim().toLowerCase();
        return (t === 'béisbol' || t === 'beisbol') && n.children.length === 0;
    });
    if (beisbol) {
        beisbol.click();
        return "Clicked Beisbol";
    }
    return "Not found";
    """
    res = driver.execute_script(script_kbo)
    print(f"Paso 1 KBO: {res}")
    time.sleep(4)
    
    # Si dio clic en Beisbol, buscar ahora Corea del Sur / KBO
    script_kbo_sub = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    var kboBtn = all.find(n => {
        var t = (n.textContent || '').trim().toLowerCase();
        return (t === 'kbo' || t === 'kbo league' || t === 'corea del sur' || t === 'corea') && n.children.length === 0;
    });
    if (kboBtn) {
        var el = kboBtn;
        while (el && el !== shadow && el.tagName !== 'BUTTON' && el.tagName !== 'A' && !(el.getAttribute('class')||'').includes('Box') && !(el.getAttribute('class')||'').includes('Item')) {
            el = el.parentElement;
        }
        if (el) {
            el.click();
            return "Clicked KBO sub: " + (el.getAttribute('class') || el.tagName);
        }
        kboBtn.click();
        return "Clicked KBO direct";
    }
    return "KBO sub not found";
    """
    res2 = driver.execute_script(script_kbo_sub)
    print(f"Paso 2 KBO: {res2}")
    time.sleep(4)
    
    evts = extract_events_from_page(driver)
    print(f"Total eventos extraídos de KBO ({len(evts)}):")
    for e in evts:
        es_val, h_limpio = es_partido_futuro_valido(e.get('horario', 'Hoy'))
        print(f" - ⚾ KBO: {e.get('local')} vs {e.get('visitante')} | {e.get('horario')} (Valido: {es_val}, {h_limpio}) | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
