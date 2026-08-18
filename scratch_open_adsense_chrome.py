import undetected_chromedriver as uc
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("🚀 Abriendo Google Chrome con AdSense y Playdoit Afiliados...")
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options, version_main=151)
try:
    print("🌐 Abriendo pestaña 1: Google AdSense...")
    driver.get("https://adsense.google.com/start/")
    time.sleep(3)
    
    print("🌐 Abriendo pestaña 2: Playdoit México...")
    driver.execute_script("window.open('https://www.playdoit.mx/es/', '_blank');")
    time.sleep(2)
    
    print("🌐 Abriendo pestaña 3: Tu sitio web oficial...")
    driver.execute_script("window.open('https://reytacopicks.com', '_blank');")
    time.sleep(2)
    
    print("✅ Pestañas abiertas en la pantalla del usuario.")
    print("Esperando 120 segundos para que el usuario pueda interactuar...")
    time.sleep(120)
finally:
    driver.quit()
