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
    
    # Clic en UEFA Champions League
    s_champ = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var node = all.find(n => (n.textContent||'').trim().toLowerCase() === 'uefa champions league' && n.children.length === 0);
    if (node) {
        (node.parentElement || node).click();
        node.click();
        return true;
    }
    return false;
    """
    clicked = driver.execute_script(s_champ)
    print("Clic Champions:", clicked)
    time.sleep(4)
    
    evts = extract_events_from_page(driver)
    print(f"Total eventos encontrados en Champions: {len(evts)}")
    for e in evts:
        print(f"  🏆 {e.get('local')} vs {e.get('visitante')} | Fecha/Horario: {e.get('horario')} | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
