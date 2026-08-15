import os
import time
import json
import undetected_chromedriver as uc
from groq import Groq
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

def get_chrome_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    
    driver = uc.Chrome(options=options, version_main=151)
    return driver

def get_pending_picks():
    # Obtener picks que no tengan estado "finalizado"
    response = supabase.table('picks').select('*').neq('estado', 'finalizado').execute()
    return response.data

def extract_live_text(driver):
    print("Navegando a la sección En Vivo...")
    driver.get("https://www.playdoit.mx/es/live")
    time.sleep(10) # Esperar a que carguen los websockets de resultados en vivo
    
    try:
        # Extraer todo el texto visible de los contenedores de eventos dentro del Shadow DOM
        script = """
        var host = document.querySelector('div#altenar > div');
        if(!host || !host.shadowRoot) return "";
        var shadow = host.shadowRoot;
        
        var containers = shadow.querySelectorAll('div[class*="EventBoxContainer"]');
        var text = "";
        containers.forEach(c => {
            text += c.innerText + "\\n---\\n";
        });
        return text;
        """
        raw_text = driver.execute_script(script)
        return raw_text
    except Exception as e:
        print(f"Error extrayendo texto en vivo: {e}")
        return ""

def update_scores_with_ai(raw_text, pending_picks):
    if not pending_picks or not raw_text:
        return

    print("Analizando resultados en vivo con Groq...")
    
    prompt = f"""
    Eres un analizador de resultados deportivos en tiempo real.
    Aquí tienes el texto crudo extraído de una página de apuestas en vivo:
    ---
    {raw_text[:8000]} # Limitamos para no exceder tokens
    ---
    
    Y aquí están los picks que estamos rastreando:
    {json.dumps(pending_picks, indent=2)}
    
    Tu tarea es buscar en el texto crudo si alguno de estos eventos se está jugando ahora mismo y cuál es su marcador actual.
    Si encuentras el marcador, devuelve un JSON array con las actualizaciones.
    Si no encuentras nada sobre un partido, ignóralo.
    
    Formato EXACTO de respuesta JSON:
    [
      {{
        "id": <id_del_pick>,
        "marcador": "América 2 - 1 Chivas (Min 75')",
        "estado": "live",
        "resultado_apuesta": "pendiente",
        "ganancia_simulada": 0
      }}
    ]
    
    CRÍTICO: Si el evento ya terminó, cambia "estado" a "finalizado". Luego, EVALÚA matemáticamente si el "pick" que dimos resultó GANADOR o PERDEDOR basado en el marcador final.
    - Si fue GANADOR: "resultado_apuesta": "ganada", "ganancia_simulada": (10 * cuota_del_pick) - 10
    - Si fue PERDEDOR: "resultado_apuesta": "perdida", "ganancia_simulada": -10
    - Si fue EMPATE (Push): "resultado_apuesta": "reembolso", "ganancia_simulada": 0
    - Muestra el marcador final en "marcador".
    """

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Solo devuelves JSON puro, sin markdown."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        inicio = response_text.find('[')
        fin = response_text.rfind(']') + 1
        
        if inicio != -1 and fin != 0:
            clean_json = response_text[inicio:fin]
            updates = json.loads(clean_json)
        else:
            updates = json.loads(response_text)
        
        # Subir actualizaciones a Supabase
        for update in updates:
            update_data = {
                'marcador': update.get('marcador'),
                'estado': update.get('estado')
            }
            if update.get('estado') == 'finalizado':
                update_data['resultado_apuesta'] = update.get('resultado_apuesta', 'pendiente')
                update_data['ganancia_simulada'] = update.get('ganancia_simulada', 0)
                
            supabase.table('picks').update(update_data).eq('id', update['id']).execute()
            print(f"Actualizado Pick ID {update['id']} -> {update.get('marcador')} | Resultado: {update_data.get('resultado_apuesta', 'live')}")
            
    except Exception as e:
        print(f"Error en el análisis de Groq para Live Tracker: {e}")

def main():
    print("Iniciando Live Tracker...")
    picks = get_pending_picks()
    if not picks:
        print("No hay picks pendientes por rastrear.")
        return
        
    driver = None
    try:
        driver = get_chrome_driver()
        raw_text = extract_live_text(driver)
        update_scores_with_ai(raw_text, picks)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
