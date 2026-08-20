import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("🚀 Iniciando Chrome para descargar APK de Draftea...")
options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

download_dir = os.path.abspath(".")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = uc.Chrome(options=options)
try:
    driver.get("https://draftea.en.uptodown.com/android/download")
    time.sleep(4)
    print(f"Título de la página: {driver.title}")
    
    # Click download button
    btn = driver.find_element(By.ID, "detail-download-button")
    print(f"Botón encontrado: {btn.text}")
    btn.click()
    print("Botón clickeado. Esperando inicio de descarga...")
    time.sleep(12)
    
    # Check downloaded files
    files = os.listdir(download_dir)
    apk_files = [f for f in files if f.endswith(".apk") or f.endswith(".xapk") or f.endswith(".crdownload")]
    print(f"Archivos encontrados en descarga: {apk_files}")
finally:
    driver.quit()
