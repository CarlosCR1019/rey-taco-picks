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
    
    # 1. Clic en Liga MX o Fútbol
    s_ligamx = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var el = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase() === 'liga mx');
    if (el) { (el.parentElement || el).click(); el.click(); return true; }
    return false;
    """
    clicked_l = driver.execute_script(s_ligamx)
    print("Clic en Liga MX:", clicked_l)
    time.sleep(4)
    
    # 2. Clic en el primer partido disponible
    s_click_match = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return "No shadow";
    var all = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
    if (all.length > 0) {
        var match = all[0];
        var text = match.innerText;
        var clickEl = match.querySelector('div[class*="Competitors"], div[class*="NameContainer"]') || match;
        clickEl.click();
        return text;
    }
    return "No match found";
    """
    match_info = driver.execute_script(s_click_match)
    print("Partido abierto:", match_info.replace('\n', ' | ')[:150])
    time.sleep(4)
    
    # 3. Buscar y hacer clic en 'Especiales por jugador' o 'Jugador'
    s_click_player_tab = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var tab = all.find(n => n.children.length === 0 && (
        (n.textContent||'').trim().toLowerCase().includes('especiales por jugador') ||
        (n.textContent||'').trim().toLowerCase() === 'jugador' ||
        (n.textContent||'').trim().toLowerCase().includes('jugadores') ||
        (n.textContent||'').trim().toLowerCase().includes('crear apuesta')
    ));
    if (tab) {
        (tab.parentElement || tab).click();
        tab.click();
        return tab.textContent.trim();
    }
    return false;
    """
    player_tab_clicked = driver.execute_script(s_click_player_tab)
    print("Pestaña de jugador clickeada:", player_tab_clicked)
    time.sleep(4)
    
    # 4. Extraer todos los mercados, jugadores y cuotas literales mostrados en pantalla
    s_extract_players = get_shadow_script() + """
    var shadow = getShadow();
    if (!shadow) return [];
    var boxes = Array.from(shadow.querySelectorAll('[class*="MarketBox"], [class*="EventDetailsMarketBox"], [class*="MarketContainer"]'));
    var results = [];
    boxes.forEach(function(box) {
        var titleEl = box.querySelector('[class*="MarketName"], [class*="Title"], [class*="HeaderMarket"]');
        var title = titleEl ? titleEl.innerText.trim() : box.innerText.split('\\n')[0];
        var buttons = Array.from(box.querySelectorAll('button, [class*="OddBoxButton"], [class*="SelectionButton"]'));
        var selections = buttons.map(b => b.innerText.replace(/\\n+/g, ' ').trim()).filter(Boolean);
        if (selections.length > 0) {
            results.push({
                mercado: title,
                selecciones: selections.slice(0, 15)
            });
        }
    });
    return results;
    """
    markets = driver.execute_script(s_extract_players)
    print(f"\nTotal mercados/jugadores encontrados en Playdoit ({len(markets)}):")
    for m in markets[:10]:
        print(f" 🎯 Mercado: {m.get('mercado')}")
        print(f"    Selecciones / Jugadores: {m.get('selecciones')}")

finally:
    driver.quit()
