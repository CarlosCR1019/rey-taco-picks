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
    if (!shadow) return ["No shadow found"];
    var all = Array.from(shadow.querySelectorAll('*'));
    var europaNodes = all.filter(n => (n.textContent||'').toLowerCase().includes('europa') && n.children.length === 0);
    return europaNodes.map(n => ({
        tag: n.tagName,
        text: (n.textContent||'').trim(),
        parentTag: n.parentElement ? n.parentElement.tagName : '',
        parentClass: n.parentElement ? n.parentElement.className : ''
    }));
    """
    res = driver.execute_script(script)
    print("Nodos con 'Europa' en Playdoit:")
    for r in res:
        print(" ->", r)
finally:
    driver.quit()
