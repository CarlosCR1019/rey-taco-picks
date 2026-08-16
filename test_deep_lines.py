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

    # 1. Switch to Decimal
    script_decimal = """
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
        setTimeout(function() {
            var all = Array.from(shadow.querySelectorAll('*'));
            var dec = all.find(n => n.children.length === 0 && n.textContent.trim().toLowerCase() === 'decimal');
            if (dec) { dec.click(); if (dec.parentElement) dec.parentElement.click(); }
        }, 500);
        return true;
    }
    return false;
    """
    driver.execute_script(script_decimal)
    time.sleep(2)

    # 2. Find and click into Pumas UNAM vs Queretaro
    script_click_pumas = """
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

    var containers = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
    var pumasContainer = containers.find(c => /pumas/i.test(c.innerText) && /quer[eé]taro/i.test(c.innerText));
    if (pumasContainer) {
        var clickTarget = pumasContainer.querySelector('div[class*="EventName"], div[class*="Competitors"], div[class*="NameContainer"]') || pumasContainer;
        clickTarget.click();
        return 'CLICKED_PUMAS';
    }
    return 'PUMAS_NOT_FOUND';
    """
    res_click = driver.execute_script(script_click_pumas)
    print("Click Pumas:", res_click)
    time.sleep(4)

    # 3. Look for subtabs in match details view
    script_subtabs = """
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

    var allElements = Array.from(shadow.querySelectorAll('*'));
    var tabs = allElements.filter(el => {
        var txt = el.textContent.trim().toLowerCase();
        return el.children.length === 0 && (txt.includes('tiros esquina') || txt.includes('córners') || txt.includes('esquinas') || txt.includes('goles') || txt.includes('tarjetas') || txt.includes('crear apuesta') || txt.includes('jugador'));
    });

    var tabInfo = tabs.map(t => ({text: t.textContent.trim(), tag: t.tagName, class: t.className}));
    return tabInfo;
    """
    subtabs_found = driver.execute_script(script_subtabs)
    print("\nSubtabs found inside match:", json.dumps(subtabs_found, indent=2))

    # 4. Click 'Tiros esquina' tab
    script_click_corners = """
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
    var cornerTab = all.find(n => n.textContent && /tiros\s*esquina|córners/i.test(n.textContent.trim()) && n.children.length === 0);
    if (cornerTab) {
        cornerTab.click();
        if (cornerTab.parentElement) cornerTab.parentElement.click();
        return 'CLICKED_CORNERS_TAB';
    }
    return 'CORNERS_TAB_NOT_FOUND';
    """
    res_corners = driver.execute_script(script_click_corners)
    print("Click Corners Tab:", res_corners)
    time.sleep(3)

    # 5. Extract all market boxes and button odds
    script_extract_all = """
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

    var marketBoxes = Array.from(shadow.querySelectorAll('[class*="MarketBox"], [class*="EventDetailsMarketBox"]'));
    var result = [];

    marketBoxes.forEach(function(box) {
        var titleEl = box.querySelector('[class*="MarketName"], [class*="Title"], [class*="HeaderMarket"]');
        var title = titleEl ? titleEl.innerText.trim() : box.innerText.split('\\n')[0];
        
        var buttons = Array.from(box.querySelectorAll('button, [class*="OddBoxButton"], [class*="SelectionButton"]'));
        var odds = buttons.map(b => b.innerText.replace(/\\n+/g, ' ').trim()).filter(Boolean);
        
        if (odds.length > 0) {
            result.push({market: title, odds: odds});
        }
    });

    if (result.length === 0) {
        // Fallback: extract all buttons on screen
        var allButtons = Array.from(shadow.querySelectorAll('button[class*="OddBoxButton-"], div[class*="OddBox-"]'));
        var fallbackOdds = allButtons.map(b => b.innerText.replace(/\\n+/g, ' ').trim());
        result.push({market: 'TODOS_LOS_BOTONES', odds: fallbackOdds});
    }

    return result;
    """
    markets = driver.execute_script(script_extract_all)
    print("\nExtracted Markets from Playdoit:")
    print(json.dumps(markets, indent=2))

finally:
    driver.quit()
