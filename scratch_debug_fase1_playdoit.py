import undetected_chromedriver as uc
import time
import json
import re
import sys
from datetime import datetime, timedelta
import zoneinfo

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, es_partido_futuro_valido, extract_events_from_page

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    events = extract_events_from_page(driver)
    print(f"Total eventos extraídos de Playdoit: {len(events)}")
    
    partidos_validos = []
    for e in events:
        h = e.get('horario', 'Hoy')
        es_val, h_limpio = es_partido_futuro_valido(h)
        print(f"- {e.get('partido')} | Horario raw: '{h}' -> Valido: {es_val} ({h_limpio})")
        if es_val:
            partidos_validos.append(e)
            
    print(f"\nTotal partidos validos que pasaron el filtro: {len(partidos_validos)}")
finally:
    driver.quit()
