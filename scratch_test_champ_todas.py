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
    
    # 1. Asegurar pestaña 'Todas' o '24h' para no filtrar partidos de Champions
    script_period = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var todas = all.find(n => (n.textContent||'').trim().toLowerCase() === 'todas' && n.tagName === 'BUTTON');
    if (todas) {
        todas.click();
        return true;
    }
    return false;
    """
    driver.execute_script(script_period)
    time.sleep(2)
    
    # 2. Clic en UEFA Champions League
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
    driver.execute_script(script_champ)
    time.sleep(4)
    evts_champ = extract_events_from_page(driver)
    print(f"Total Champions: {len(evts_champ)}")
    for e in evts_champ:
        print("  🇪🇺", e.get('local'), "vs", e.get('visitante'), e.get('horario'), e.get('cuotas'))

finally:
    driver.quit()
