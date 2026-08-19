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
    var all = Array.from(shadow.querySelectorAll('*'));
    var kboMatches = all.filter(n => {
        var t = (n.textContent || '').toLowerCase();
        return t.includes('kbo') || t.includes('corea') || t.includes('korea') || t.includes('doosan') || t.includes('kia') || t.includes('lg twins') || t.includes('ssg') || t.includes('hanwha') || t.includes('nc dinos') || t.includes('lotte') || t.includes('kt wiz') || t.includes('kiwoom') || t.includes('samsung lions');
    });
    var res = [];
    kboMatches.forEach(k => {
        if (k.children.length === 0) {
            res.push({
                text: k.textContent.trim(),
                tag: k.tagName,
                cls: k.getAttribute('class') || ''
            });
        }
    });
    return res;
    """
    results = driver.execute_script(script)
    print(f"Total menciones KBO/Béisbol Coreano encontradas: {len(results)}")
    for r in results[:20]:
        print(r)
finally:
    driver.quit()
