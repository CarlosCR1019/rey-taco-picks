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
    
    script_click_kbo_robust = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    
    // 1. Buscar KBO directo en TopLeagues o pantalla
    var direct = all.find(n => {
        if (n.children.length > 0) return false;
        var t = (n.textContent || '').trim().toLowerCase();
        return t === 'kbo' || t === 'kbo league' || t === 'corea del sur';
    });
    
    if (direct) {
        var el = direct;
        while (el && el !== shadow && el.tagName !== 'BUTTON' && el.tagName !== 'A' && !(el.getAttribute('class')||'').includes('Box') && !(el.getAttribute('class')||'').includes('Item')) {
            el = el.parentElement;
        }
        (el || direct).click();
        return "Clicked direct KBO";
    }
    
    // 2. Si no, hacer clic en Béisbol en el menú lateral
    var beisbol = all.find(n => {
        if (n.children.length > 0) return false;
        var t = (n.textContent || '').trim().toLowerCase();
        return (t === 'béisbol' || t === 'beisbol');
    });
    
    if (beisbol) {
        var elB = beisbol;
        while (elB && elB !== shadow && elB.tagName !== 'BUTTON' && !(elB.getAttribute('class')||'').includes('SportMenuItem')) {
            elB = elB.parentElement;
        }
        (elB || beisbol).click();
        return "Clicked Beisbol first";
    }
    return "Not found";
    """
    res = driver.execute_script(script_click_kbo_robust)
    print(f"Resultado paso 1: {res}")
    time.sleep(3)
    
    if "Beisbol" in str(res):
        script_sub_kbo = get_shadow_script() + """
        var shadow = getShadow();
        if (!shadow) return false;
        var all = Array.from(shadow.querySelectorAll('*'));
        var kbo = all.find(n => {
            if (n.children.length > 0) return false;
            var t = (n.textContent || '').trim().toLowerCase();
            return t === 'kbo' || t === 'kbo league' || t === 'corea del sur' || t === 'corea';
        });
        if (kbo) {
            var el = kbo;
            while (el && el !== shadow && el.tagName !== 'BUTTON' && !(el.getAttribute('class')||'').includes('Box') && !(el.getAttribute('class')||'').includes('Item') && !(el.getAttribute('class')||'').includes('Category')) {
                el = el.parentElement;
            }
            (el || kbo).click();
            return "Clicked KBO sub!";
        }
        return "Sub KBO not found";
        """
        res2 = driver.execute_script(script_sub_kbo)
        print(f"Resultado paso 2: {res2}")
        time.sleep(3)
        
    evts = extract_events_from_page(driver)
    print(f"Total eventos encontrados ({len(evts)}):")
    for e in evts:
        es_val, h_limpio = es_partido_futuro_valido(e.get('horario', 'Hoy'))
        print(f" - ⚾ {e.get('local')} vs {e.get('visitante')} | {e.get('horario')} (Valido: {es_val}, {h_limpio}) | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
