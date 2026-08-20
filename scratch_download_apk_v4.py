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

driver = uc.Chrome(version_main=151, options=options)
try:
    driver.get("https://draftea.en.uptodown.com/android/download")
    time.sleep(4)
    print(f"Título: {driver.title}")
    
    # Try finding the download button and clicking with JS
    btn = driver.find_element(By.ID, "detail-download-button")
    print(f"Botón de descarga encontrado: {btn.text[:30]}")
    driver.execute_script("arguments[0].click();", btn)
    print("Clic JS realizado con éxito. Esperando 25 segundos para la descarga completa...")
    
    for i in range(25):
        time.sleep(1)
        files = [f for f in os.listdir(download_dir) if f.endswith(".apk") or f.endswith(".xapk") or f.endswith(".zip")]
        if files:
            print(f"Progreso segundo {i+1}: {files}")
    
    final_files = [f for f in os.listdir(download_dir) if f.endswith(".apk") or f.endswith(".xapk")]
    print(f"\n🎉 Archivos descargados finales: {final_files}")
finally:
    try:
        driver.quit()
    except Exception:
        pass
