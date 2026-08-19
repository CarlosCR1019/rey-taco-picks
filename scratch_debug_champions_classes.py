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
    
    script_click = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var target = all.find(n => {
        var txt = (n.textContent || '').trim().toLowerCase();
        return (txt === 'uefa champions league' || txt === 'champions league' || txt.includes('champions league')) && n.children.length === 0;
    });
    if (target) {
        var el = target;
        while (el && el !== shadow && el.tagName !== 'BUTTON' && el.tagName !== 'A' && !(el.getAttribute('class')||'').includes('Box') && !(el.getAttribute('class')||'').includes('Item')) {
            el = el.parentElement;
        }
        if (el) {
            el.click();
            return "Clicked: " + (el.getAttribute('class') || el.tagName);
        }
        target.click();
        return "Clicked target";
    }
    return "Not found";
    """
    res = driver.execute_script(script_click)
    print(f"Click: {res}")
    time.sleep(5)
    
    script_inspect = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return ["No shadow"];
    var all = Array.from(shadow.querySelectorAll('*'));
    var cardClasses = [];
    all.forEach(el => {
        var cls = el.getAttribute('class') || '';
        if (cls.includes('Event') || cls.includes('Match') || cls.includes('Row') || cls.includes('Odd')) {
            cardClasses.push(cls);
        }
    });
    return Array.from(new Set(cardClasses));
    """
    classes = driver.execute_script(script_inspect)
    print("Clases de eventos encontradas tras click en Champions:")
    for c in classes[:25]:
        print(f" - {c}")
        
    script_text = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    return shadow.innerText;
    """
    txt = driver.execute_script(script_text)
    print(f"\nTexto en pantalla tras click (primeros 500 chars):\n{txt[:500]}")

finally:
    driver.quit()
