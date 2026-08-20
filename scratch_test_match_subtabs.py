import undetected_chromedriver as uc
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_deep_event_markets

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
driver = uc.Chrome(options=options, version_main=151)

try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    # Click Liga MX
    s_ligamx = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var el = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase() === 'liga mx');
    if (el) { (el.parentElement || el).click(); el.click(); return true; }
    return false;
    """
    driver.execute_script(s_ligamx)
    time.sleep(4)
    
    # Click on first match
    s_click_match = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var matchEl = all.find(n => (n.textContent||'').includes('vs') && n.children.length === 0);
    if (matchEl) {
        (matchEl.parentElement || matchEl).click();
        matchEl.click();
        return true;
    }
    return false;
    """
    clicked_m = driver.execute_script(s_click_match)
    print("Clic en partido de Liga MX:", clicked_m)
    time.sleep(4)
    
    # Check tabs inside match
    s_tabs = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return [];
    var all = Array.from(shadow.querySelectorAll('*'));
    var tabs = all.filter(n => n.children.length === 0 && (n.textContent||'').trim().length > 2 && (n.textContent||'').trim().length < 30);
    return tabs.map(t => (t.textContent||'').trim()).slice(0, 30);
    """
    tabs_found = driver.execute_script(s_tabs)
    print(f"Pestañas y sub-mercados detectados dentro del partido:")
    for t in set(tabs_found):
        if any(w in t.lower() for w in ['jugador', 'remate', 'esquina', 'tarjeta', 'gol', 'combo', 'crear apuesta', 'insights', 'estadísticas']):
            print(f"  👉 [{t}]")

finally:
    driver.quit()
