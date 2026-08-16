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

    script = """
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
    if (!shadow) return 'NO_SHADOW';

    var selects = shadow.querySelectorAll('select, [class*="OddsFormat"], [class*="Dropdown"], [class*="Select"], [class*="format"]');
    var selectInfo = [];
    selects.forEach(function(s) {
        selectInfo.push({tag: s.tagName, text: s.innerText, html: s.outerHTML.substring(0, 150)});
    });

    var allNodes = Array.from(shadow.querySelectorAll('*'));
    var oddsFormats = allNodes.filter(function(n) {
        return n.children.length === 0 && /decimal|americano|fraccionario|fracci/i.test(n.textContent.trim());
    });
    var nodesInfo = oddsFormats.map(function(n) {
        return {tag: n.tagName, text: n.textContent.trim(), class: n.className};
    });

    return {selects: selectInfo, nodes: nodesInfo};
    """
    res = driver.execute_script(script)
    print("SELECTS:", json.dumps(res.get("selects", []), indent=2))
    print("NODES:", json.dumps(res.get("nodes", []), indent=2))
finally:
    driver.quit()
