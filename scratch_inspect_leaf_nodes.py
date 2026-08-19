import undetected_chromedriver as uc
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
driver = uc.Chrome(options=options, version_main=151)

try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    script = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('*'));
    var results = [];
    all.forEach(n => {
        if (n.children.length === 0) {
            var t = (n.textContent || '').trim();
            if (t.length > 2 && t.length < 50) {
                results.push(n.tagName + ' | ' + n.className + ' | ' + t);
            }
        }
    });
    return results;
    """
    res = driver.execute_script(script)
    print(f"Total leaf nodes: {len(res) if res else 0}")
    for r in (res or [])[:60]:
        print("  ", r)
finally:
    driver.quit()
