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
    
    # Click on Béisbol in sport menu
    script_click = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    var beisbolTab = all.find(n => {
        var t = (n.textContent || '').trim().toLowerCase();
        return (t === 'béisbol' || t === 'beisbol' || t === 'baseball') && n.children.length === 0;
    });
    if (beisbolTab) {
        beisbolTab.click();
        if (beisbolTab.parentElement) beisbolTab.parentElement.click();
        return "Clicked Beisbol";
    }
    return "Not found";
    """
    res = driver.execute_script(script_click)
    print(f"Click en Béisbol: {res}")
    time.sleep(4)
    
    # Check all leagues or subcategories visible in Béisbol
    script_sub = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return [];
    var all = Array.from(shadow.querySelectorAll('*'));
    var items = [];
    all.forEach(n => {
        if (n.children.length === 0) {
            var t = (n.textContent || '').trim();
            if (t.length > 2 && t.length < 40) {
                items.push(t);
            }
        }
    });
    return Array.from(new Set(items));
    """
    sub_items = driver.execute_script(script_sub)
    print(f"Items encontrados en Béisbol ({len(sub_items)}):")
    for it in sub_items:
        if any(w in it.lower() for w in ['kbo', 'corea', 'korea', 'npb', 'japon', 'japón', 'lmb', 'mlb', 'tigers', 'twins', 'bears', 'lions', 'giants', 'dinos', 'wiz', 'landeros', 'heroes']):
            print(f" -> {it}")
            
finally:
    driver.quit()
