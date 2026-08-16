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

    script_click = """
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

    var btn = shadow.querySelector('[class*="OddsFormatBoxOptionName"], [class*="OddsFormat"]');
    if (btn) {
        btn.click();
        if (btn.parentElement) btn.parentElement.click();
        return 'CLICKED_FORMAT_BUTTON';
    }
    return 'NOT_FOUND';
    """
    res1 = driver.execute_script(script_click)
    print("Step 1 click:", res1)
    time.sleep(1)

    script_select_decimal = """
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
    var all = Array.from(shadow.querySelectorAll('*'));
    var dec = all.find(n => n.children.length === 0 && n.textContent.trim().toLowerCase() === 'decimal');
    if (dec) {
        dec.click();
        if (dec.parentElement) dec.parentElement.click();
        return 'CLICKED_DECIMAL';
    }
    return 'DECIMAL_OPTION_NOT_FOUND';
    """
    res2 = driver.execute_script(script_select_decimal)
    print("Step 2 select decimal:", res2)
    time.sleep(2)

    # Check new odds
    script_check = """
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
    var odds = shadow.querySelectorAll('button[class*="OddBoxButton-"], div[class*="OddBox-"]');
    var list = [];
    odds.forEach(o => {
        var txt = o.innerText.trim();
        if (txt) list.push(txt.replace('\\n', ' '));
    });
    return list.slice(0, 15);
    """
    new_odds = driver.execute_script(script_check)
    print("\nOdds on page after switching to Decimal:")
    for o in new_odds:
        print("  ->", o)
finally:
    driver.quit()
