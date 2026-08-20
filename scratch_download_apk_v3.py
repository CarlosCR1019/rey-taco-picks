import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("🚀 Iniciando Chrome (version_main=151) para descargar APK de Draftea...")
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

driver = uc.Chrome(version_main=151, options=options)
try:
    driver.get("https://draftea.en.uptodown.com/android/download")
    time.sleep(4)
    print(f"Título: {driver.title}")
    btn = driver.find_element(By.ID, "detail-download-button")
    print(f"Botón de descarga: {btn.text}")
    btn.click()
    print("Clic realizado. Esperando 15s para descarga...")
    time.sleep(15)
    
    files = [f for f in os.listdir(download_dir) if f.endswith(".apk") or f.endswith(".xapk") or f.endswith(".crdownload")]
    print(f"Archivos descargados: {files}")
finally:
    try:
        driver.quit()
    except Exception:
        pass
