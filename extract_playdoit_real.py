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

    # Click Decimal format
    script_dec = """
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
    var all = Array.from(shadow.querySelectorAll('*'));
    var decimalBtn = all.find(n => n.textContent && n.textContent.trim().toLowerCase() === 'decimal' && n.children.length === 0);
    if(decimalBtn) { decimalBtn.click(); return true; }
    return false;
    """
    driver.execute_script(script_dec)
    time.sleep(2)

    # Extract all events on screen
    script_events = """
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
    if (!shadow) return [];
    var containers = shadow.querySelectorAll('div[class*="EventBoxContainer"]');
    var res = [];
    containers.forEach(function(c) {
        var txt = c.innerText.trim();
        if (txt) {
            res.push(txt.split('\\n'));
        }
    });
    return res;
    """
    events = driver.execute_script(script_events)
    print(f"\n==========================================")
    print(f"🎯 PARTIDOS REALES EN VIVO EN PLAYDOIT ({len(events)} encontrados):")
    print(f"==========================================")
    for idx, lines in enumerate(events, 1):
        clean_lines = [l.strip() for l in lines if l.strip()]
        print(f"[{idx}] " + " | ".join(clean_lines[:8]))
finally:
    driver.quit()
