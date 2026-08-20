import undetected_chromedriver as uc
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
driver = uc.Chrome(options=options, version_main=151)

try:
    driver.get("https://app.draftea.mx/")
    time.sleep(8)
    print("Page title:", driver.title)
    print("Current URL:", driver.current_url)
    
    # Extract text on screen
    body_text = driver.find_element("tag name", "body").text
    print(f"Body text preview (first 1000 chars):\n{body_text[:1000]}")
finally:
    driver.quit()
