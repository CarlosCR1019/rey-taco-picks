import undetected_chromedriver as uc
import time
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
driver = uc.Chrome(options=options, version_main=151)

try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    # 1. Switch to Decimal Odds
    s_dec = get_shadow_script() + """
    var shadow = getShadow();
    if(!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var dec = all.find(n => (n.textContent||'').trim().toLowerCase() === 'decimal' && n.children.length === 0);
    if (dec) { dec.click(); return true; }
    return false;
    """
    driver.execute_script(s_dec)
    time.sleep(2)
    
    # 2. Get all top categories and click Liga MX
    s_ligamx = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var el = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase() === 'liga mx');
    if (el) { (el.parentElement || el).click(); el.click(); return true; }
    return false;
    """
    driver.execute_script(s_ligamx)
    time.sleep(4)
    
    # 3. Get all event boxes in Liga MX
    s_events = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return [];
    var all = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
    return all.map(function(box, index) {
        return {
            index: index,
            text: box.innerText.replace(/\\n+/g, ' | ')
        };
    });
    """
    events = driver.execute_script(s_events)
    print(f"Total partidos de Liga MX visibles en pantalla ({len(events)}):")
    for ev in events:
        print(f" -> [{ev['index']}] {ev['text'][:150]}")
    
    # 4. Click into each match and dump all player props
    for ev in events[:4]:
        idx = ev['index']
        print(f"\n==================================================")
        print(f"INSPECCIONANDO A FONDO PARTIDO [{idx}]...")
        print(f"==================================================")
        
        # Click match by index
        s_click_idx = get_shadow_script() + f"""
        var shadow = getShadow();
        if (!shadow) return false;
        var all = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
        if (all[{idx}]) {{
            var clickEl = all[{idx}].querySelector('div[class*="Competitors"], div[class*="NameContainer"]') || all[{idx}];
            ['mousedown', 'click', 'mouseup'].forEach(evt => {{
                clickEl.dispatchEvent(new MouseEvent(evt, {{ bubbles: true, cancelable: true, view: window }}));
            }});
            return true;
        }}
        return false;
        """
        driver.execute_script(s_click_idx)
        time.sleep(4)
        
        # Get all sub-tabs inside the event view
        s_get_tabs = get_shadow_script() + """
        var shadow = getShadow();
        if (!shadow) return [];
        var all = Array.from(shadow.querySelectorAll('*'));
        var tabs = all.filter(n => n.children.length === 0 && (n.textContent||'').trim().length > 2 && (n.textContent||'').trim().length < 35);
        return Array.from(new Set(tabs.map(t => (t.textContent||'').trim())));
        """
        subtabs = driver.execute_script(s_get_tabs)
        print(f"Sub-pestañas disponibles: {subtabs[:20]}")
        
        # Click each player / props / corners / combo sub-tab
        for tab_target in ['especiales por jugador', 'jugador', 'jugadores', 'tiros esquina', 'crear apuesta', 'goles', 'insights']:
            s_click_tab = get_shadow_script() + f"""
            var shadow = getShadow();
            if (!shadow) return false;
            var all = Array.from(shadow.querySelectorAll('*'));
            var target = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase().includes('{tab_target}'));
            if (target) {{
                target.click();
                if (target.parentElement) target.parentElement.click();
                return target.textContent.trim();
            }}
            return false;
            """
            tab_clicked = driver.execute_script(s_click_tab)
            if tab_clicked:
                print(f"   👉 Clic en pestaña: [{tab_clicked}]")
                time.sleep(2.5)
                
                # Extract all markets & selections inside this tab
                s_extract_boxes = get_shadow_script() + """
                var shadow = getShadow();
                if (!shadow) return [];
                var boxes = Array.from(shadow.querySelectorAll('[class*="MarketBox"], [class*="EventDetailsMarketBox"], [class*="MarketContainer"]'));
                var res = [];
                boxes.forEach(function(box) {
                    var titleEl = box.querySelector('[class*="MarketName"], [class*="Title"], [class*="HeaderMarket"]');
                    var title = titleEl ? titleEl.innerText.trim() : box.innerText.split('\\n')[0];
                    var buttons = Array.from(box.querySelectorAll('button, [class*="OddBoxButton"], [class*="SelectionButton"]'));
                    var odds = buttons.map(b => b.innerText.replace(/\\n+/g, ' ').trim()).filter(Boolean);
                    if (odds.length > 0) {
                        res.push({
                            mercado: title,
                            cuotas: odds
                        });
                    }
                });
                return res;
                """
                boxes_data = driver.execute_script(s_extract_boxes)
                for b in boxes_data:
                    print(f"      🎯 Mercado: {b['mercado']}")
                    for o in b['cuotas'][:8]:
                        print(f"         • {o}")
        
        # Go back to Liga MX list
        driver.execute_script(s_ligamx)
        time.sleep(3)

finally:
    driver.quit()
