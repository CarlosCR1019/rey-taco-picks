import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=151)
try:
    print("🌐 Abriendo Playdoit...")
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)

    # 1. Cambiar a Decimal
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

    # 2. Obtener la lista de todos los partidos con sus selectores y URLs/EventIDs
    script_get_events = """
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

    var containers = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
    return containers.map((c, idx) => {
        var names = Array.from(c.querySelectorAll('div[class*="CompetitorName-"], div[class*="NameContainer-"], span[class*="Name-"]')).map(n => n.innerText.trim());
        var raw = c.innerText.split('\\n').map(l => l.trim()).filter(Boolean);
        return {
            index: idx,
            names: names,
            summary: raw.slice(0, 5)
        };
    });
    """
    events = driver.execute_script(script_get_events)
    print("Eventos encontrados en pantalla:", len(events))
    for e in events[:10]:
        print("  ->", e)

    # 3. Probar clic confiable en Necaxa vs Club Leon
    print("\nAbriendo específicamente Necaxa vs Club Leon...")
    script_open_necaxa = """
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
    var target = containers.find(c => /necaxa/i.test(c.innerText) && /le[oó]n/i.test(c.innerText));
    if (!target) return 'NECAXA_NOT_IN_VIEW';

    // Clic en el nombre del equipo o en el área de competidores
    var clickNode = target.querySelector('div[class*="CompetitorsContainer"], div[class*="NameContainer"], div[class*="EventName"]') || target;
    
    // Disparar eventos nativos de mouse
    ['mousedown', 'click', 'mouseup'].forEach(evtType => {
        clickNode.dispatchEvent(new MouseEvent(evtType, { bubbles: true, cancelable: true, view: window }));
    });

    return 'CLICKED_NECAXA_DISPATCH';
    """
    res_necaxa = driver.execute_script(script_open_necaxa)
    print("Resultado clic Necaxa:", res_necaxa)
    time.sleep(4)

    # 4. Verificar qué partido está abierto actualmente en pantalla
    script_verify_current = """
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

    // Obtener título o nombres en la cabecera del partido abierto
    var headerNames = Array.from(shadow.querySelectorAll('[class*="HeaderCompetitorName"], [class*="EventDetailsHeader"] [class*="CompetitorName"]')).map(n => n.innerText.trim());
    
    // Clic en Tiros de esquina
    var tabs = Array.from(shadow.querySelectorAll('button, [class*="TabItem"], [role="tab"]'));
    var cornerTab = tabs.find(t => /tiros\s*esquina/i.test(t.innerText));
    if (cornerTab) {
        cornerTab.click();
    }

    return {
        partido_abierto_en_cabecera: headerNames,
        texto_cabecera: shadow.querySelector('[class*="EventDetailsHeader"]')?.innerText?.substring(0, 150)
    };
    """
    header_info = driver.execute_script(script_verify_current)
    print("\nInformación del partido abierto en cabecera:", json.dumps(header_info, indent=2))
    time.sleep(2)

    # 5. Extraer las líneas de Tiros de Esquina de Necaxa vs León
    script_extract_corners = """
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

    var boxes = Array.from(shadow.querySelectorAll('[class*="MarketBox"], [class*="EventDetailsMarketBox"]'));
    var results = [];

    boxes.forEach(box => {
        var titleEl = box.querySelector('[class*="MarketName"], [class*="Title"], [class*="HeaderMarket"]');
        var title = titleEl ? titleEl.innerText.trim() : box.innerText.split('\\n')[0];
        
        var buttons = Array.from(box.querySelectorAll('button, [class*="OddBoxButton"], [class*="SelectionButton"]'));
        var odds = buttons.map(b => b.innerText.replace(/\\n+/g, ' ').trim()).filter(Boolean);
        
        if (odds.length > 0) {
            results.push({mercado: title, cuotas: odds});
        }
    });

    return results;
    """
    necaxa_corners = driver.execute_script(script_extract_corners)
    print("\nLíneas extraídas de Necaxa vs León:")
    print(json.dumps(necaxa_corners, indent=2))

finally:
    driver.quit()
