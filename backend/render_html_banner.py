import os
import sys
import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def renderizar_banner_estudio(picks=None, output_path="banner_hoy.png"):
    """
    Renderiza un banner gráfico HD (1080x1080) con calidad de estudio EA Sports / ESPN
    capturando el elemento #banner-root para un encuadre perfecto.
    """
    if not picks:
        json_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "picks.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                picks = json.load(f)
        else:
            picks = []

    free_picks = [p for p in picks if not p.get('es_parlay')][:3]
    if not free_picks:
        free_picks = [
            {"categoria": "LIGA MX", "partido": "Tigres UANL vs Atlante FC", "pick": "Más de 2.5 Goles Totales", "cuota": "1.67", "confianza": "92%", "horario": "Hoy • 21:00 hrs"},
            {"categoria": "LIGA MX", "partido": "Juarez vs America", "pick": "Más de 2.5 Goles Totales", "cuota": "1.74", "confianza": "90%", "horario": "Hoy • 19:00 hrs"},
            {"categoria": "MLB BÉISBOL", "partido": "WAS Nationals vs TEX Rangers", "pick": "Más de 7.5 Carreras Totales", "cuota": "1.95", "confianza": "91%", "horario": "Hoy • 18:05 hrs"}
        ]

    # Construir HTML dinámico para las 3 tarjetas
    cards_html = ""
    for i, p in enumerate(free_picks):
        hot_class = "hot" if i == 0 else ""
        cat = p.get('categoria', 'DEPORTES').upper()
        partido = p.get('partido', 'Partido')
        pick_txt = p.get('pick', 'Selección')
        cuota = p.get('cuota', '1.75')
        conf = p.get('confianza', '90%')
        horario = p.get('horario', 'Hoy')
        
        cards_html += f"""
        <div class="pick-card {hot_class}">
          <div class="card-left">
            <div class="meta-tags">
              <span class="tag-sport">{cat}</span>
              <span class="tag-time">{horario}</span>
            </div>
            <div class="match-title">{partido}</div>
            <div class="pick-selection">🎯 {pick_txt}</div>
          </div>
          <div class="card-right">
            <div class="odds-box">
              <div class="odds-label">Momio</div>
              <div class="odds-val">{cuota}</div>
            </div>
            <span class="conf-badge">🔥 {conf} Confianza</span>
          </div>
        </div>
        """

    fecha_actual = datetime.now().strftime("%d DE AGOSTO, %Y • CDMX")
    
    template_path = os.path.join(os.path.dirname(__file__), "banner_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Inyectar las tarjetas
    html_content = html_content.replace('<!-- Inject dynamically -->', cards_html)
    html_content = html_content.replace('ANÁLISIS MATEMÁTICO &amp; INTELIGENCIA ARTIFICIAL', f'ANÁLISIS MATEMÁTICO • {fecha_actual}')

    temp_html_path = os.path.join(os.path.dirname(__file__), "temp_banner.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("📸 Renderizando banner HD con Headless Chrome...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1080,1080")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--force-device-scale-factor=1")

    driver = uc.Chrome(version_main=151, options=options)
    try:
        driver.get(f"file:///{os.path.abspath(temp_html_path).replace(chr(92), '/')}")
        time.sleep(1.8) # Esperar fuentes de Google
        
        banner_element = driver.find_element(By.ID, "banner-root")
        banner_element.screenshot(output_path)
        print(f"🎉 ¡Banner HD de Calidad Estudio Generado!: {output_path}")
    finally:
        driver.quit()

    return output_path

if __name__ == "__main__":
    renderizar_banner_estudio()
