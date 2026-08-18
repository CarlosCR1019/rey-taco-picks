import undetected_chromedriver as uc
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("🚀 Abriendo edición de perfil de Instagram en Chrome...")
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options, version_main=151)
try:
    print("🌐 Abriendo https://www.instagram.com/accounts/edit/...")
    driver.get("https://www.instagram.com/accounts/edit/")
    time.sleep(3)
    
    print("🌐 Abriendo vinculación en Facebook...")
    driver.execute_script("window.open('https://www.facebook.com/pages/?category=your_pages', '_blank');")
    time.sleep(2)
    
    print("✅ Pestañas abiertas en la pantalla del usuario.")
    time.sleep(120)
finally:
    driver.quit()
