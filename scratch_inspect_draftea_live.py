import undetected_chromedriver as uc
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
driver = uc.Chrome(options=options, version_main=151)

try:
    driver.get("https://www.draftea.mx/")
    time.sleep(8)
    print("Page title:", driver.title)
    print("Current URL:", driver.current_url)
    
    # Extract links and buttons
    elements = driver.find_elements("tag name", "a")
    print(f"Total links encontrados: {len(elements)}")
    for el in elements[:15]:
        href = el.get_attribute("href") or ""
        txt = (el.text or "").strip()
        if txt or "props" in href or "app" in href or "juego" in href:
            print(f" - [{txt}] -> {href}")
finally:
    driver.quit()
