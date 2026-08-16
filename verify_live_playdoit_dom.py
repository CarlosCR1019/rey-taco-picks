import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=151)
try:
    print("🌐 Conectando a Playdoit en vivo...")
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)

    # 1. Cambiar a formato Decimal en vivo
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

    # 2. Lista de partidos a inspeccionar en profundidad que NO estaban en capturas
    partidos_a_probar = [
        {"nombre": "Santos Laguna vs Guadalajara Chivas", "busqueda": "santos"},
        {"nombre": "Xolos de Tijuana vs Cruz Azul", "busqueda": "tijuana"},
        {"nombre": "Necaxa vs Club Leon", "busqueda": "necaxa"}
    ]

    reporte_extraccion = {}

    for p in partidos_a_probar:
        print(f"\n🔍 Inspeccionando en vivo en Playdoit: {p['nombre']}...")
        
        # Clic en el partido
        script_click = f"""
        function getShadow() {{
            var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
            if (host && host.shadowRoot) return host.shadowRoot;
            var all = document.querySelectorAll('*');
            for (var i = 0; i < all.length; i++) {{
                if (all[i].shadowRoot) return all[i].shadowRoot;
            }}
            return null;
        }}
        var shadow = getShadow();
        if (!shadow) return 'NO_SHADOW';

        var containers = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"]'));
        var targetContainer = containers.find(c => c.innerText.toLowerCase().includes("{p['busqueda']}"));
        if (targetContainer) {{
            var clickEl = targetContainer.querySelector('div[class*="Competitors"], div[class*="EventName"], [class*="CompetitorName"]') || targetContainer;
            clickEl.click();
            return 'CLICKED_MATCH';
        }}
        return 'NOT_FOUND_IN_VIEW';
        """
        res_click = driver.execute_script(script_click)
        print(f"  -> Clic en partido: {res_click}")
        time.sleep(3)

        if res_click == 'CLICKED_MATCH':
            # Extraer todas las pestañas disponibles dentro de este partido
            script_extract_tabs_and_markets = """
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
            if (!shadow) return {tabs: [], markets: []};

            // Detectar pestañas
            var tabNodes = Array.from(shadow.querySelectorAll('button, [class*="TabItem"], [role="tab"]')).filter(b => b.innerText && b.innerText.trim().length > 0 && b.innerText.trim().length < 30);
            var tabs = tabNodes.map(t => t.innerText.trim()).filter((v, i, a) => a.indexOf(v) === i);

            // Clic en 'Tiros esquina' si existe
            var cornerTab = tabNodes.find(t => /tiros\s*esquina|córners/i.test(t.innerText));
            if (cornerTab) {
                cornerTab.click();
            }

            var boxes = Array.from(shadow.querySelectorAll('[class*="MarketBox"], [class*="EventDetailsMarketBox"]'));
            var marketsData = [];

            boxes.forEach(function(box) {
                var titleEl = box.querySelector('[class*="MarketName"], [class*="Title"], [class*="HeaderMarket"]');
                var title = titleEl ? titleEl.innerText.trim() : box.innerText.split('\\n')[0];
                var buttons = Array.from(box.querySelectorAll('button, [class*="OddBoxButton"]'));
                var odds = buttons.map(b => b.innerText.replace(/\\n+/g, ' ').trim()).filter(Boolean);
                if (odds.length > 0) {
                    marketsData.push({mercado: title, cuotas_botones: odds});
                }
            });

            return {tabs: tabs, markets: marketsData};
            """
            data_partido = driver.execute_script(script_extract_tabs_and_markets)
            reporte_extraccion[p['nombre']] = data_partido
            print(f"  -> Pestañas detectadas en Playdoit: {data_partido.get('tabs', [])[:6]}")
            print(f"  -> Mercados extraídos: {len(data_partido.get('markets', []))}")
            for m in data_partido.get('markets', [])[:3]:
                print(f"     📊 [{m['mercado']}]: {m['cuotas_botones'][:6]}")

            # Regresar al listado general
            script_back = """
            var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
            if (host && host.shadowRoot) {
                var backBtn = host.shadowRoot.querySelector('button[class*="BackButton"], [class*="HeaderBack"]');
                if (backBtn) backBtn.click();
            }
            """
            driver.execute_script(script_back)
            time.sleep(2)

    print("\n============================================================")
    print("✅ REPORTE COMPLETO DE LÍNEAS EXTRAÍDAS EN VIVO DESDE EL DOM:")
    print("============================================================")
    print(json.dumps(reporte_extraccion, indent=2))

finally:
    driver.quit()
