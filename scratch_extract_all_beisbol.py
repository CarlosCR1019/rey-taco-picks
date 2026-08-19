import undetected_chromedriver as uc
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_events_from_page, click_category

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    click_category(driver, "Béisbol")
    time.sleep(4)
    
    evts = extract_events_from_page(driver)
    print(f"Total eventos encontrados al hacer clic en Béisbol ({len(evts)}):")
    for e in evts:
        print(f" ⚾ {e.get('local')} vs {e.get('visitante')} | Horario: {e.get('horario')} | Cuotas: {e.get('cuotas')}")

finally:
    driver.quit()
