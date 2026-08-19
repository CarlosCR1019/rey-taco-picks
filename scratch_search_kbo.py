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
    
    script_search_kbo = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    
    // Find search input or search button
    var searchInput = shadow.querySelector('input[type="text"], input[class*="Search"], input[placeholder*="Buscar"], input[placeholder*="Search"]');
    if (!searchInput) {
        var searchBtn = shadow.querySelector('[class*="SearchIcon"], [class*="SearchButton"], [class*="EventSearch"]');
        if (searchBtn) {
            searchBtn.click();
            searchInput = shadow.querySelector('input');
        }
    }
    
    if (searchInput) {
        searchInput.focus();
        searchInput.value = 'KBO';
        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
        searchInput.dispatchEvent(new Event('change', { bubbles: true }));
        return "Typed KBO in search input";
    }
    return "Search input not found";
    """
    res = driver.execute_script(script_search_kbo)
    print(f"Search KBO: {res}")
    time.sleep(3)
    
    script_search_results = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return [];
    var all = Array.from(shadow.querySelectorAll('*'));
    var res = [];
    all.forEach(n => {
        var t = (n.textContent || '').trim();
        if (n.children.length === 0 && (t.includes('Tigers') || t.includes('Twins') || t.includes('Lions') || t.includes('Dinos') || t.includes('Wiz') || t.includes('KBO') || t.includes('Bears') || t.includes('Landers') || t.includes('Eagles') || t.includes('Giants') || t.includes('Heroes'))) {
            res.push({
                text: t,
                cls: n.getAttribute('class') || '',
                tag: n.tagName
            });
        }
    });
    return res;
    """
    items = driver.execute_script(script_search_results)
    print(f"Resultados de búsqueda KBO ({len(items)}):")
    for it in items[:15]:
        print(it)

finally:
    driver.quit()
