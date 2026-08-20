import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import zipfile
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

download_dir = os.path.abspath("./apk_download")
os.makedirs(download_dir, exist_ok=True)

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False
}
options.add_experimental_option("prefs", prefs)

driver = uc.Chrome(version_main=151, options=options)

try:
    print("Abriendo página de descarga de Draftea...")
    driver.get("https://draftea.en.uptodown.com/android/download")
    time.sleep(3)
    
    btn = driver.find_element(By.ID, "detail-download-button")
    driver.execute_script("arguments[0].click();", btn)
    print("Botón clickeado. Navegando al flujo de descarga...")
    time.sleep(5)
    
    # Check if there is a restart download link on post-download page
    links = driver.find_elements(By.TAG_NAME, "a")
    for l in links:
        href = l.get_attribute("href")
        if href and "dw.uptodown.net" in href:
            print(f"Clickeando enlace directo: {href}")
            driver.execute_script("arguments[0].click();", l)
            break
            
    print("Esperando descarga (30 segundos)...")
    for i in range(30):
        time.sleep(1)
        files = os.listdir(download_dir)
        if any(f.endswith(".apk") or f.endswith(".xapk") for f in files) and not any(f.endswith(".crdownload") for f in files):
            print(f"✅ ¡Descarga terminada en segundo {i+1}! Archivos: {files}")
            break
        elif files:
            print(f"Descargando ({i+1}s): {files}")
            
finally:
    try:
        driver.quit()
    except Exception:
        pass

# Check if downloaded
files = os.listdir(download_dir)
print(f"Archivos finales en {download_dir}: {files}")
