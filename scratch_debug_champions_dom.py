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
    
    script_find = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    
    var all = Array.from(shadow.querySelectorAll('*'));
    var champs = all.filter(n => (n.textContent || '').toLowerCase().includes('champions') && n.children.length === 0);
    var details = [];
    champs.forEach(c => {
        details.push({
            tag: c.tagName,
            text: c.textContent.trim(),
            className: c.className,
            parentClass: c.parentElement ? c.parentElement.className : '',
            parentTag: c.parentElement ? c.parentElement.tagName : ''
        });
    });
    return details;
    """
    res = driver.execute_script(script_find)
    print(f"Nodos de Champions encontrados: {len(res)}")
    for r in res:
        print(r)
        
    # Now let's try clicking on the deepest clickable parent
    script_click = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var champNode = all.find(n => n.textContent.trim().toLowerCase() === 'uefa champions league' && n.children.length === 0);
    if (!champNode) {
        champNode = all.find(n => n.textContent.trim().toLowerCase().includes('champions league') && n.children.length === 0);
    }
    if (champNode) {
        var clickable = champNode;
        while (clickable && clickable !== shadow && clickable.tagName !== 'BUTTON' && clickable.tagName !== 'A' && !clickable.onclick && !clickable.className.includes('Item') && !clickable.className.includes('Button')) {
            clickable = clickable.parentElement;
        }
        if (clickable) {
            clickable.click();
            return "Clicked element: " + clickable.tagName + " class: " + clickable.className;
        } else {
            champNode.click();
            return "Clicked leaf node";
        }
    }
    return "Not found";
    """
    click_res = driver.execute_script(script_click)
    print(f"Resultado click: {click_res}")
    time.sleep(4)
    
    evts = extract_events_from_page(driver)
    print(f"Eventos en pantalla: {len(evts)}")
    for e in evts[:5]:
        print(f" * {e.get('partido')} | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
