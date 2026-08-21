import os
import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

sys.stdout.reconfigure(encoding='utf-8')

def renderizar_infografia_resultados(output_path="infografia_resultados.png"):
    template_path = os.path.join(os.path.dirname(__file__), "report_template.html")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=600,1050")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--force-device-scale-factor=1")

    driver = uc.Chrome(version_main=151, options=options)
    try:
        driver.get(f"file:///{os.path.abspath(template_path).replace(chr(92), '/')}")
        time.sleep(1.5)
        
        element = driver.find_element(By.ID, "infographic-root")
        element.screenshot(output_path)
        print(f"🎉 ¡Infografía de Resultados Calidad Estudio Generada!: {output_path}")
    finally:
        driver.quit()

    return output_path

if __name__ == "__main__":
    renderizar_infografia_resultados()
