import time
import json
import sys
import undetected_chromedriver as uc

sys.stdout.reconfigure(encoding='utf-8')

print("🕵️ Abriendo Playdoit para auditar el DOM de Altenar en vivo (version_main=151)...")
options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    # 1. Asegurar formato Decimal
    driver.execute_script("""
    try {
        var labels = Array.from(document.querySelectorAll('label, span, div, button'));
        var dec = labels.find(el => el.innerText && el.innerText.trim().toLowerCase() === 'decimal');
        if(dec) dec.click();
    } catch(e){}
    """)
    time.sleep(2)
    
    # 2. Explorar Altenar Shadow DOM
    script_inspect = """
    try {
        var host = document.querySelector('div#altenar > div') || document.querySelector('asb-sports-app, asb-app, altenar-app');
        if (!host || !host.shadowRoot) return { error: "No shadowRoot found", hostFound: !!host };
        var shadow = host.shadowRoot;
        
        // Obtener botones de deportes / categorías
        var catBtns = Array.from(shadow.querySelectorAll('[class*="SportItem"], [class*="categoryItem"], [class*="MenuNode"], [class*="SportButton"], div[class*="TreeItem"], [class*="Header"], [class*="Title"]')).map(b => ({
            text: b.innerText ? b.innerText.replace(/\\n/g, ' | ') : '',
            className: b.className
        })).filter(x => x.text && x.text.length > 2);
        
        // Obtener eventos visibles
        var events = Array.from(shadow.querySelectorAll('div[class*="EventBoxContainer"], div[class*="EventContainer"], div[class*="EventRow"], div[class*="MatchRow"]')).map(e => {
            var text = e.innerText;
            var comps = Array.from(e.querySelectorAll('[class*="CompetitorName"], [class*="Competitors"], [class*="NameContainer"], [class*="EventName"]')).map(c => c.innerText.trim());
            var odds = Array.from(e.querySelectorAll('[class*="OddButton"], [class*="Price"], [class*="OddValue"], [class*="selection"], [class*="Odds"]')).map(o => o.innerText.trim());
            return {
                text: text ? text.replace(/\\n/g, ' -- ') : '',
                competitors: comps,
                odds: odds
            };
        });
        
        return {
            categoriesFound: catBtns.slice(0, 30),
            eventsCount: events.length,
            eventsSample: events.slice(0, 10)
        };
    } catch(e) {
        return { error: e.toString() };
    }
    """
    
    res = driver.execute_script(script_inspect)
    print("\n📊 RESULTADOS DE INSPECCIÓN PLAYDOIT:")
    print(json.dumps(res, indent=2, ensure_ascii=False))

finally:
    driver.quit()
