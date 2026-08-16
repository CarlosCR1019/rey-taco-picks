import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)

    # Click format button
    script_step1 = """
    function getShadow() {
        var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
        if (host && host.shadowRoot) return host.shadowRoot;
        var all = document.querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
            if (all[i].shadowRoot) return all[i].shadowRoot;
        }
        return null;
    }
    var shadow = getShadow();
    if (!shadow) return false;
    var btn = shadow.querySelector('[class*="OddsFormatBoxOptionName"], [class*="OddsFormat"]');
    if (btn) {
        btn.click();
        if (btn.parentElement) btn.parentElement.click();
        return true;
    }
    return false;
    """
    driver.execute_script(script_step1)
    time.sleep(1.5)

    # Inspect all elements in document and shadow DOM
    script_inspect = """
    function getShadow() {
        var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
        if (host && host.shadowRoot) return host.shadowRoot;
        var all = document.querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
            if (all[i].shadowRoot) return all[i].shadowRoot;
        }
        return null;
    }
    var shadow = getShadow();
    var results = [];
    
    // Look in shadow
    if (shadow) {
        var shadowNodes = Array.from(shadow.querySelectorAll('*')).filter(n => n.children.length === 0 && n.textContent.trim().length > 0);
        shadowNodes.forEach(n => {
            if (/decimal|frac|amer/i.test(n.textContent)) {
                results.push({source: 'shadow', tag: n.tagName, text: n.textContent.trim(), class: n.className});
            }
        });
    }
    
    // Look in main document body
    var docNodes = Array.from(document.querySelectorAll('*')).filter(n => n.children.length === 0 && n.textContent.trim().length > 0);
    docNodes.forEach(n => {
        if (/decimal|frac|amer/i.test(n.textContent)) {
            results.push({source: 'doc', tag: n.tagName, text: n.textContent.trim(), class: n.className});
        }
    });

    return results;
    """
    res = driver.execute_script(script_inspect)
    print("MATCHING FORMAT OPTIONS FOUND:")
    print(json.dumps(res, indent=2))
finally:
    driver.quit()
