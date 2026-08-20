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
    
    # Clic en UEFA Europa League
    script = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var el = all.find(n => (n.textContent||'').trim().toLowerCase() === 'uefa europa league' && n.children.length === 0);
    if (el) {
        (el.parentElement || el).click();
        el.click();
        return true;
    }
    return false;
    """
    clicked = driver.execute_script(script)
    print("Clic en Europa League:", clicked)
    time.sleep(4)
    
    events = extract_events_from_page(driver)
    print(f"Total eventos encontrados en UEFA Europa League: {len(events)}")
    for ev in events:
        print(f" -> {ev.get('local')} vs {ev.get('visitante')} | Horario: {ev.get('horario')} | Cuotas: {ev.get('cuotas')}")
finally:
    driver.quit()
