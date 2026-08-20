import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
options.add_argument("--headless=new")
driver = uc.Chrome(version_main=151, options=options)

try:
    driver.get("https://draftea.en.uptodown.com/android/download")
    time.sleep(3)
    btn = driver.find_element(By.ID, "detail-download-button")
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(4)
    print(f"URL post-click: {driver.current_url}")
    print(f"Título post-click: {driver.title}")
    
    # Check for direct download link on post-download page
    links = driver.find_elements(By.TAG_NAME, "a")
    for l in links:
        href = l.get_attribute("href")
        if href and ("dw.uptodown.com" in href or "download" in href or ".apk" in href):
            print("Enlace encontrado:", href)
finally:
    driver.quit()
