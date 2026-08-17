import undetected_chromedriver as uc
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options, version_main=151)
try:
    print("🌐 Consultando Porkbun para 'reytacopicks.com'...")
    driver.get("https://porkbun.com/checkout/search?q=reytacopicks.com")
    time.sleep(4)
    text_porkbun = driver.execute_script("return document.body.innerText;")
    
    print("\n🌐 Consultando Namecheap para 'reytacopicks.com'...")
    driver.get("https://www.namecheap.com/domains/registration/results/?domain=reytacopicks.com")
    time.sleep(4)
    text_namecheap = driver.execute_script("return document.body.innerText;")
    
    print("\n🌐 Consultando Hostinger México para 'reytacopicks.com'...")
    driver.get("https://www.hostinger.mx/buscador-de-dominios")
    time.sleep(3)
    
    # Procesar resultados
    print("\n" + "="*50)
    print("📊 RESULTADOS EN VIVO DE DISPONIBILIDAD Y PRECIO:")
    print("="*50)
    
    # Porkbun
    for line in text_porkbun.split('\n'):
        if 'reytacopicks.com' in line.lower() or ('$' in line and ('com' in line.lower() or 'year' in line.lower() or 'renews' in line.lower())):
            if len(line.strip()) < 80:
                print(f"🐷 Porkbun: {line.strip()}")
                
    # Namecheap
    for line in text_namecheap.split('\n'):
        if 'reytacopicks.com' in line.lower() or ('$' in line and ('com' in line.lower() or 'retail' in line.lower() or 'year' in line.lower())):
            if len(line.strip()) < 80:
                print(f"🛡️ Namecheap: {line.strip()}")
                
finally:
    driver.quit()
