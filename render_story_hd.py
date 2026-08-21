import os
import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

sys.stdout.reconfigure(encoding='utf-8')

template_path = os.path.join(os.path.dirname(__file__), "backend", "report_story_9_16.html")
output_path = "report_story_hd.png"

options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1080,1920")
options.add_argument("--hide-scrollbars")
options.add_argument("--force-device-scale-factor=1")

driver = uc.Chrome(version_main=151, options=options)
try:
    driver.set_window_size(1080, 1920)
    driver.get(f"file:///{os.path.abspath(template_path).replace(chr(92), '/')}")
    time.sleep(2)
    
    element = driver.find_element(By.ID, "story-root")
    element.screenshot(output_path)
    print(f"🎉 ¡Reporte 9:16 HD Generado!: {output_path}")
finally:
    driver.quit()
