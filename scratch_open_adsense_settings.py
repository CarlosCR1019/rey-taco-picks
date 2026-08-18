import undetected_chromedriver as uc
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("🚀 Abriendo directamente la página de ID de Cuenta en Google AdSense...")
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options, version_main=151)
try:
    driver.get("https://adsense.google.com/adsense/u/0/account/settings")
    time.sleep(4)
    print("✅ Página de Configuración / ID de Cuenta abierta en Chrome.")
    time.sleep(120)
finally:
    driver.quit()
