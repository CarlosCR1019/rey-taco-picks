import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    script_inspect_tree = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    
    // Find all SportMenuItems
    var items = all.filter(n => {
        var cls = n.getAttribute('class') || '';
        return cls.includes('SportMenuItem') || cls.includes('SportMenuCategory') || cls.includes('SportMenuChampionship');
    });
    
    var res = [];
    items.forEach(it => {
        var txt = (it.textContent || '').trim();
        var cls = it.getAttribute('class') || '';
        if (txt && txt.length < 50) {
            res.push({ text: txt, cls: cls });
        }
    });
    return res;
    """
    tree = driver.execute_script(script_inspect_tree)
    print(f"Total items en menú de deportes: {len(tree)}")
    for t in tree[:40]:
        print(f" - {t['text']} [{t['cls']}]")
finally:
    driver.quit()
