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
    
    script = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return ["No shadow"];
    var nodes = Array.from(shadow.querySelectorAll('*'));
    var leagueNames = [];
    nodes.forEach(n => {
        if (n.children.length === 0) {
            var t = n.textContent.trim();
            if (t.length > 3 && t.length < 50) {
                leagueNames.push(t);
            }
        }
    });
    return Array.from(new Set(leagueNames));
    """
    all_texts = driver.execute_script(script)
    print(f"Total textos encontrados en shadow DOM: {len(all_texts)}")
    
    interesting = [t for t in all_texts if any(w in t.lower() for w in ['uefa', 'champ', 'europa', 'liga', 'copa', 'futbol', 'fútbol', 'conmebol', 'libertadores', 'sudamericana', 'internacional'])]
    print("Categorías / Ligas de fútbol detectadas en Playdoit:")
    for it in interesting[:30]:
        print(f" -> {it}")
        
finally:
    driver.quit()
