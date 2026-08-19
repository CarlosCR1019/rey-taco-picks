import undetected_chromedriver as uc
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_events_from_page

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
driver = uc.Chrome(options=options, version_main=151)

try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    # 1. Clic directo en UEFA Champions League
    script_champ = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var node = all.find(n => (n.textContent||'').trim().toLowerCase() === 'uefa champions league');
    if (node) {
        node.click();
        if (node.parentElement) node.parentElement.click();
        return true;
    }
    return false;
    """
    res = driver.execute_script(script_champ)
    print("Clic Champions:", res)
    time.sleep(3)
    evts = extract_events_from_page(driver)
    print(f"Eventos Champions extraídos: {len(evts)}")
    for e in evts:
        print("  🇪🇺", e.get('local'), "vs", e.get('visitante'), e.get('horario'), e.get('cuotas'))
        
    # 2. Clic directo en MLB
    script_mlb = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var node = all.find(n => (n.textContent||'').trim().toLowerCase() === 'mlb');
    if (node) {
        node.click();
        if (node.parentElement) node.parentElement.click();
        return true;
    }
    return false;
    """
    res_mlb = driver.execute_script(script_mlb)
    print("Clic MLB:", res_mlb)
    time.sleep(3)
    evts_mlb = extract_events_from_page(driver)
    print(f"Eventos MLB extraídos: {len(evts_mlb)}")
    for e in evts_mlb[:4]:
        print("  ⚾", e.get('local'), "vs", e.get('visitante'), e.get('horario'), e.get('cuotas'))

finally:
    driver.quit()
