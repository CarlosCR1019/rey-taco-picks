import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_events_from_page, es_partido_futuro_valido, click_category

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    # 1. Sin filtro Hoy (o quitando filtro Hoy para explorar torneos futuros)
    clicked = click_category(driver, "UEFA Champions League")
    print(f"Click en UEFA Champions League: {clicked}")
    time.sleep(4)
    
    evts = extract_events_from_page(driver)
    print(f"Total eventos extraídos de Champions sin filtro Hoy: {len(evts)}")
    for e in evts:
        es_val, h_limpio = es_partido_futuro_valido(e.get('horario', 'Hoy'))
        print(f" - {e.get('partido')} [{e.get('horario')}] -> Valido: {es_val} ({h_limpio}) | Cuotas: {e.get('cuotas')}")
finally:
    driver.quit()
