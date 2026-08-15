import os
import json
import time
import sys
import re
from datetime import datetime, date
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import urllib.request
from groq import Groq
from dotenv import load_dotenv
from supabase import create_client, Client

# Forzar codificación UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

if not GROQ_API_KEY:
    print("⚠️ ADVERTENCIA: No se encontró GROQ_API_KEY en el archivo .env")

# Configurar Supabase
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("⚠️ ADVERTENCIA: No se encontraron credenciales de Supabase.")

# ============================================================
#  FASE 0: CONFIGURACIÓN DEL NAVEGADOR
# ============================================================
def get_chrome_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    
    # Modo headless para la nube (GitHub Actions / CI)
    is_ci = os.getenv("CI") or os.getenv("GITHUB_ACTIONS")
    if is_ci:
        options.add_argument("--headless=new")
        print("   ☁️ Modo NUBE detectado (headless)")
    else:
        print("   🖥️ Modo LOCAL detectado (con ventana)")
    
    try:
        driver = uc.Chrome(options=options)
    except Exception:
        driver = uc.Chrome(options=options, version_main=None)
    return driver

# ============================================================
#  UTILIDADES DE NAVEGACIÓN (Shadow DOM de Altenar)
# ============================================================
def click_tab_hoy(driver):
    """Hace clic en la pestaña 'Hoy' para filtrar solo eventos del día."""
    script = """
    try {
        var host = document.querySelector('div#altenar > div');
        if(!host || !host.shadowRoot) return false;
        var shadow = host.shadowRoot;
        var tabs = Array.from(shadow.querySelectorAll('*'));
        var hoyTab = tabs.find(n => n.textContent.trim() === 'Hoy' && n.children.length === 0);
        if(hoyTab) { hoyTab.click(); return true; }
        return false;
    } catch(e) { return false; }
    """
    result = driver.execute_script(script)
    if result:
        print("   ✅ Filtro 'Hoy' activado.")
    time.sleep(3)

def click_decimal_toggle(driver):
    """Cambia el formato de cuotas a Decimal en la barra lateral."""
    script = """
    try {
        var host = document.querySelector('div#altenar > div');
        if(!host || !host.shadowRoot) return false;
        var shadow = host.shadowRoot;
        var all = Array.from(shadow.querySelectorAll('*'));
        var decimalBtn = all.find(n => n.textContent.trim() === 'Decimal' && n.children.length === 0);
        if(decimalBtn) { decimalBtn.click(); return true; }
        return false;
    } catch(e) { return false; }
    """
    result = driver.execute_script(script)
    if result:
        print("   ✅ Formato de cuotas cambiado a DECIMAL.")
    time.sleep(2)

def click_category(driver, category):
    """Hace clic en una categoría del menú lateral."""
    script = f"""
    try {{
        var shadow = document.querySelector('div#altenar > div').shadowRoot;
        var allNodes = Array.from(shadow.querySelectorAll('*'));
        var target = allNodes.find(n => n.children.length === 0 && n.textContent.trim().toLowerCase() === '{category.lower()}');
        if(target) {{
            target.click();
            if(target.parentElement) target.parentElement.click();
            return true;
        }}
        return false;
    }} catch(e) {{ return false; }}
    """
    return driver.execute_script(script)

def extract_events_from_page(driver):
    """Extrae los eventos visibles de la página actual del Shadow DOM."""
    script = """
    var host = document.querySelector('div#altenar > div');
    if(!host || !host.shadowRoot) return [];
    var shadow = host.shadowRoot;
    var containers = shadow.querySelectorAll('div[class*="EventBoxContainer"]');
    var result = [];
    containers.forEach(c => {
        try {
            var names = c.querySelectorAll('div[class*="CompetitorName-"]');
            var odds = c.querySelectorAll('button[class*="OddBoxButton-"]');
            if(names.length >= 2) {
                var oddsData = [];
                odds.forEach(o => {
                    var val = o.querySelector('div[class*="OddValue-"]');
                    if(val) oddsData.push(val.innerText.trim());
                });
                result.push({
                    local: names[0].innerText.trim(),
                    visitante: names[1].innerText.trim(),
                    cuotas: oddsData,
                    texto: c.innerText
                });
            }
        } catch(e) {}
    });
    return result;
    """
    return driver.execute_script(script) or []

# ============================================================
#  FASE 1: ESCÁNER RADAR DE SUPERFICIE
# ============================================================
def fase1_escaneo_superficie(driver):
    print("\n" + "="*60)
    print("🕵️  FASE 1: ESCÁNER RADAR DE SUPERFICIE")
    print("="*60)
    
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    # Configuración inicial
    click_decimal_toggle(driver)
    click_tab_hoy(driver)
    
    partidos_data = []
    categorias = [
        # Fútbol
        'PLAY BOOSTS', 'Liga MX', 'Leagues Cup', 'UEFA Champions League',
        'UEFA Europa League', 'UEFA Conference League', 'La Liga',
        'Copa Italia', 'Copa Libertadores', 'Copa Sudamericana',
        'Primeira Liga', 'Liga MX Femenil', 'Liga de Expansión MX',
        'Liga Profesional', 'Brasileiro Serie A', 'Primera A',
        # Deportes USA
        'MLB', 'MLS', 'NFL', 'NFL, Pretemporada',
        # México extra
        'Liga Mexicana de Beisbol',
        # Combate
        'Boxeo', 'MMA',
        # Otros
        'Tenis', 'E-sports +'
    ]
    
    for cat in categorias:
        print(f"   Explorando: {cat}...", end=" ")
        if click_category(driver, cat):
            time.sleep(3)
            eventos = extract_events_from_page(driver)
            nuevos = 0
            for e in eventos:
                nombre = f"{e['local']} vs {e['visitante']}"
                if not any(x["partido"] == nombre for x in partidos_data):
                    partidos_data.append({
                        "categoria": cat,
                        "partido": nombre,
                        "local": e['local'],
                        "visitante": e['visitante'],
                        "cuotas_superficie": e['cuotas'][:3] if e['cuotas'] else [],
                        "info_texto": e['texto'][:500]
                    })
                    nuevos += 1
            print(f"✅ {nuevos} nuevos" if nuevos else "⏭️ sin nuevos")
        else:
            print("⚠️ no encontrada")
    
    print(f"\n   📊 Total eventos únicos: {len(partidos_data)}")
    return partidos_data

# ============================================================
#  FASE 2: COMPARACIÓN CON MERCADO (The Odds API)
# ============================================================
def fase2_comparacion_mercado(partidos_data):
    print("\n" + "="*60)
    print("📈  FASE 2: COMPARACIÓN CON CUOTAS DEL MERCADO")
    print("="*60)
    
    if not ODDS_API_KEY:
        print("   ⚠️ No hay ODDS_API_KEY. Saltando comparación de mercado.")
        print("   ℹ️ Para activar esta función, agrega ODDS_API_KEY en tu .env")
        return {}
    
    try:
        # Obtener cuotas de fútbol (soccer) y otros deportes
        sports_map = {
            'soccer': ['Liga MX', 'La Liga', 'UEFA Champions League', 'Copa Italia', 'MLS'],
            'americanfootball_nfl': ['NFL'],
            'baseball_mlb': ['MLB']
        }
        
        market_odds = {}
        
        for sport_key, categorias in sports_map.items():
            url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h&oddsFormat=decimal"
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    for game in data:
                        home = game.get('home_team', '')
                        away = game.get('away_team', '')
                        
                        # Calcular cuota promedio del mercado
                        all_home_odds = []
                        all_away_odds = []
                        for bm in game.get('bookmakers', []):
                            for market in bm.get('markets', []):
                                for outcome in market.get('outcomes', []):
                                    if outcome['name'] == home:
                                        all_home_odds.append(outcome['price'])
                                    elif outcome['name'] == away:
                                        all_away_odds.append(outcome['price'])
                        
                        if all_home_odds:
                            market_odds[home.lower()] = round(sum(all_home_odds) / len(all_home_odds), 2)
                        if all_away_odds:
                            market_odds[away.lower()] = round(sum(all_away_odds) / len(all_away_odds), 2)
                
                print(f"   ✅ {sport_key}: {len(data)} eventos del mercado global.")
            except Exception as e:
                print(f"   ⚠️ Error consultando {sport_key}: {e}")
        
        print(f"   📊 {len(market_odds)} cuotas de referencia del mercado obtenidas.")
        return market_odds
        
    except Exception as e:
        print(f"   ❌ Error general en comparación de mercado: {e}")
        return {}

# ============================================================
#  FASE 3: FILTRO INTELIGENTE (Top 15 por Groq)
# ============================================================
def fase3_filtro_inteligente(partidos_data):
    print("\n" + "="*60)
    print("🧠  FASE 3: FILTRO INTELIGENTE (Groq selecciona Top 15 Multideporte)")
    print("="*60)
    
    if not partidos_data:
        return []
    
    client = Groq(api_key=GROQ_API_KEY)
    catalogo = [{"cat": p['categoria'], "partido": p['partido'], "cuotas": p.get('cuotas_superficie', [])} for p in partidos_data]
    
    prompt = f"""
    Catálogo de {len(catalogo)} eventos deportivos de hoy. 
    Selecciona EXACTAMENTE 15 partidos con mayor potencial, asegurando MÁXIMA DIVERSIDAD DEPORTIVA:
    - Obligatorio incluir partidos de MLB (Béisbol), NFL (Americano), Fútbol Internacional (Champions, La Liga, Premier, Libertadores) y Liga MX.
    - NO elijas solo fútbol mexicano. Si hay tenis, boxeo, MMA o MLB, DEBES incluirlos.
    
    {json.dumps(catalogo)}
    
    Devuelve SOLO un JSON array de strings con los nombres exactos de los partidos.
    Ejemplo: ["New York Yankees vs Boston Red Sox", "Real Madrid vs Osasuna", "América vs Monterrey", "Kansas City Chiefs vs Detroit Lions"]
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        ).choices[0].message.content.strip()
        
        inicio = response.find('[')
        fin = response.rfind(']') + 1
        objetivos = json.loads(response[inicio:fin])
        print(f"   ✅ Groq seleccionó {len(objetivos)} objetivos para inmersión multideporte.")
        for i, obj in enumerate(objetivos, 1):
            print(f"      {i}. {obj}")
        return objetivos
    except Exception as e:
        print(f"   ⚠️ Error en filtro: {e}. Usando los primeros 15.")
        return [p['partido'] for p in partidos_data[:15]]

# ============================================================
#  FASE 4: INMERSIÓN QUIRÚRGICA (Entrar a cada partido)
# ============================================================
def fase4_inmersion(driver, objetivos, partidos_data):
    print("\n" + "="*60)
    print("🎯  FASE 4: INMERSIÓN QUIRÚRGICA (Mercados Profundos)")
    print("="*60)
    
    datos_profundos = []
    
    for i, obj in enumerate(objetivos, 1):
        base = next((p for p in partidos_data if p['partido'] == obj), None)
        if not base:
            continue
        
        print(f"\n   [{i}/{len(objetivos)}] Infiltrando: {obj}")
        
        driver.get("https://www.playdoit.mx/es/")
        time.sleep(5)
        click_tab_hoy(driver)
        
        # Clic en categoría
        click_category(driver, base['categoria'])
        time.sleep(3)
        
        # Clic en el partido específico
        script_click = f"""
        try {{
            var shadow = document.querySelector('div#altenar > div').shadowRoot;
            var names = shadow.querySelectorAll('div[class*="CompetitorName-"]');
            var match = Array.from(names).find(n => n.innerText.includes("{base['local']}"));
            if(match) {{ match.click(); return true; }}
            return false;
        }} catch(e) {{ return false; }}
        """
        
        if driver.execute_script(script_click):
            time.sleep(4)
            
            # Extraer todo el contenido profundo
            script_deep = """
            try {
                var shadow = document.querySelector('div#altenar > div').shadowRoot;
                return shadow.innerText || "";
            } catch(e) { return ""; }
            """
            texto = driver.execute_script(script_deep) or ""
            
            datos_profundos.append({
                "categoria": base['categoria'],
                "partido": obj,
                "cuotas_superficie": base.get('cuotas_superficie', []),
                "mercados_profundos": texto[:5000]
            })
            print(f"      ✅ {len(texto[:5000])} caracteres de mercados extraídos.")
        else:
            print(f"      ⚠️ No se pudo entrar al partido.")
    
    print(f"\n   📊 Inmersión completada: {len(datos_profundos)} partidos analizados a fondo.")
    return datos_profundos

# ============================================================
#  FASE 5: MEMORIA HISTÓRICA
# ============================================================
def fase5_memoria_historica():
    print("\n" + "="*60)
    print("📚  FASE 5: RECUPERANDO MEMORIA HISTÓRICA")
    print("="*60)
    
    if not supabase:
        return "Sin conexión a base de datos."
    
    try:
        res = supabase.table("picks").select("categoria, partido, pick, cuota, estado, fecha_generacion").order("id", desc=True).limit(30).execute()
        picks = res.data
        
        if not picks:
            print("   ℹ️ Sin historial previo. Primera ejecución.")
            return "Sin historial previo. Esta es la primera ejecución del sistema."
        
        ganados = sum(1 for p in picks if p.get('estado') == 'ganado')
        perdidos = sum(1 for p in picks if p.get('estado') == 'perdido')
        pendientes = sum(1 for p in picks if p.get('estado', 'pendiente') == 'pendiente')
        
        memoria = f"""RESUMEN DE RENDIMIENTO:
- Total picks recientes: {len(picks)}
- Ganados: {ganados} | Perdidos: {perdidos} | Pendientes: {pendientes}
- Win Rate: {round(ganados/(ganados+perdidos)*100, 1) if (ganados+perdidos) > 0 else 0}%

PICKS RECIENTES:
"""
        for p in picks[:15]:
            estado = p.get('estado', 'pendiente')
            emoji = '✅' if estado == 'ganado' else '❌' if estado == 'perdido' else '⏳'
            memoria += f"  {emoji} {p.get('partido')} → {p.get('pick')} @ {p.get('cuota')} [{estado}]\n"
        
        print(f"   ✅ Memoria cargada: {len(picks)} picks, {ganados}W-{perdidos}L")
        return memoria
    except Exception as e:
        print(f"   ⚠️ Error leyendo historial: {e}")
        return "Error leyendo historial."

# ============================================================
#  FASE 6: ANÁLISIS FINAL — DEBATE Y CONSENSO MULTI-IA
# ============================================================
def fase6_analisis_final(datos_profundos, memoria, market_odds):
    print("\n" + "="*60)
    print("🧠⚡  FASE 6: DEBATE Y CONSENSO MULTI-IA (Quant vs Auditor vs Juez)")
    print("="*60)
    
    if not GROQ_API_KEY or not datos_profundos:
        return []
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Contexto de mercado global
    market_context = ""
    if market_odds:
        market_context = f"""
CUOTAS PROMEDIO DEL MERCADO GLOBAL (15+ casas de apuestas):
{json.dumps(market_odds, indent=2)}
"""

    datos_partidos_str = json.dumps(datos_profundos, indent=2)

    # -------------------------------------------------------------
    # RONDA 1: IA CUANTITATIVA ("Alpha Quant" - Llama 3.3 70B)
    # Busca valor matemático (+EV), desajustes y estadísticas.
    # -------------------------------------------------------------
    print("   🤖 [IA 1: Alpha Quant] Analizando cuotas y ventajas matemáticas...")
    prompt_quant = f"""
Eres "Alpha Quant", una IA experta en modelos matemáticos y valor esperado (+EV) en apuestas deportivas.
Analiza la siguiente información de partidos y cuotas:

{memoria}
{market_context}
DATOS DE PARTIDOS:
{datos_partidos_str}

TAREA: Propón una lista de 8 a 10 posibles apuestas con ventaja matemática.
Requisitos:
- Diversidad: Incluye MLB (Béisbol), NFL (Americano), Fútbol Internacional (Champions, La Liga) y Liga MX.
- Mercados variados: No solo "Gana". Usa Totales (Over/Under), Hándicaps y Ambos Anotan.
- Justifica matemáticamente cada propuesta.

Devuelve tu reporte analítico estructurado por partido.
"""
    try:
        resp_quant = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_quant}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        ).choices[0].message.content.strip()
        print("   ✅ [Alpha Quant] Propuestas iniciales generadas.")
    except Exception as e:
        print(f"   ⚠️ Error en IA Quant: {e}")
        resp_quant = "Análisis quant no disponible."

    # -------------------------------------------------------------
    # RONDA 2: IA AUDITORA DE RIESGO ("Risk Auditor" - Llama 3.1)
    # Busca trampas, refuta selecciones dudosas y ajusta mercados.
    # -------------------------------------------------------------
    print("   🛡️ [IA 2: Risk Auditor] Auditando riesgos, trampas y debilidades tácticas...")
    prompt_auditor = f"""
Eres "Risk Auditor", una IA crítica y contrarian especializada en gestión de riesgo en apuestas deportivas.
Tu misión es DEBATIR, CUESTIONAR y DESTRUIR las apuestas dudosas propuestas por Alpha Quant.

PROPUESTAS DE ALPHA QUANT:
{resp_quant}

DATOS REALES DE LOS PARTIDOS:
{datos_partidos_str}

TAREA:
1. Identifica cuáles de las propuestas de Alpha Quant son "trampas de las casas de apuestas", tienen cuotas engañosas, o riesgo innecesario.
2. Para cada una, decide: [APROBAR], [RECHAZAR] o [MODIFICAR MERCADO] (ej. sugerir Over/Under o Hándicap en vez de Moneyline).
3. Selecciona únicamente las que consideres de RIESGO CONTROLADO Y ALTA PROBABILIDAD REAL.

Devuelve tu dictamen crítico fundamentado.
"""
    try:
        resp_auditor = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_auditor}],
            model="llama-3.1-8b-instant",
            temperature=0.2
        ).choices[0].message.content.strip()
        print("   ✅ [Risk Auditor] Auditoría y debate completados.")
    except Exception as e:
        print(f"   ⚠️ Error en IA Auditor: {e}")
        resp_auditor = "Auditoría no disponible."

    # -------------------------------------------------------------
    # RONDA 3: IA JUEZ SUPREMO ("Chief Arbiter" - Llama 3.3 70B)
    # Sintetiza el debate y emite el consenso final en JSON.
    # -------------------------------------------------------------
    print("   ⚖️ [IA 3: Chief Arbiter] Sintetizando debate y emitiendo consenso definitivo...")
    prompt_juez = f"""
Eres el "Chief Odds Arbiter" de Rey Taco Picks. Tu trabajo es emitir el veredicto definitivo tras evaluar el debate entre Alpha Quant y Risk Auditor.

DEBATE DE LOS EXPERTOS:
--- PROPUESTAS QUANT ---
{resp_quant}

--- AUDITORÍA DE RIESGO ---
{resp_auditor}

--- DATOS DE MERCADO GLOBAL ---
{market_context}

TAREA: Genera la selección final de 6 a 8 picks que obtuvieron CONSENSO UNÁNIME de alta convicción.

REGLAS ESTRICTAS:
1. Cuotas EXCLUSIVAMENTE en formato DECIMAL (ej. 1.85, 2.15, 1.90).
2. DIVERSIDAD: Combina MLB/Béisbol, NFL, Fútbol Internacional y Liga MX.
3. MERCADOS: Usa los mercados refinados tras el debate (Totales Over/Under, Hándicaps, Props, Ambos Anotan o Moneylines seguros).
4. El último objeto DEBE ser un "Parlay" combinando 2-3 de los mejores picks con cuota multiplicada. "es_parlay": true.
5. Marca "tiene_valor": true cuando la cuota de Playdoit sea ventajosa vs mercado global.
6. En "razonamiento", resume la conclusión del debate entre el análisis cuántico y el control de riesgo.

Devuelve ÚNICAMENTE un JSON array válido con este formato:
[
    {{
        "categoria": "Béisbol",
        "partido": "New York Yankees vs Boston Red Sox",
        "pick": "Over 8.5 Carreras",
        "cuota": "1.90",
        "confianza": "91%",
        "razonamiento": "Consenso IA: Viento a favor y rotación débil. Auditor aprobó total de carreras sobre moneyline.",
        "es_parlay": false,
        "tiene_valor": true,
        "odds_mercado": "1.82"
    }}
]
"""
    try:
        resp_final = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Devuelves únicamente JSON puro sin bloques markdown ni texto extra."},
                {"role": "user", "content": prompt_juez}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.15
        ).choices[0].message.content.strip()

        inicio = resp_final.find('[')
        fin = resp_final.rfind(']') + 1
        picks = json.loads(resp_final[inicio:fin])
        
        print(f"\n   🏆 CONSENSO ALCANZADO: {len(picks)} picks aprobados por el comité de IAs:")
        for p in picks:
            valor = " 💎 VALOR" if p.get('tiene_valor') else ""
            parlay = " 🔗 PARLAY" if p.get('es_parlay') else ""
            print(f"      → [{p.get('categoria')}] {p.get('partido')} | {p.get('pick')} @ {p.get('cuota')}{valor}{parlay}")
        
        return picks
    except Exception as e:
        print(f"   ❌ Error en síntesis de debate: {e}")
        return []

# ============================================================
#  FASE 7: GUARDADO Y NOTIFICACIONES
# ============================================================
def fase7_guardar_y_notificar(picks):
    print("\n" + "="*60)
    print("💾  FASE 7: GUARDANDO Y NOTIFICANDO")
    print("="*60)
    
    if not picks:
        print("   ❌ No hay picks para guardar.")
        return
    
    hoy = date.today().isoformat()
    
    # Agregar metadatos
    base_id = int(time.time())
    for idx, pick in enumerate(picks):
        pick['id'] = base_id + idx
        pick['fecha_generacion'] = hoy
        pick['estado'] = 'pendiente'
        if 'ganancia_simulada' not in pick:
            pick['ganancia_simulada'] = 0
    
    if supabase:
        # NO borramos los viejos - los preservamos para historial
        # Solo marcamos los de hoy como los actuales
        try:
            print(f"   💾 Subiendo {len(picks)} picks frescos a Supabase...")
            supabase.table("picks").insert(picks).execute()
            print("   ✅ Picks subidos exitosamente.")
        except Exception as e:
            print(f"   ❌ Error Supabase: {e}")
            _guardar_local(picks)
    else:
        _guardar_local(picks)
    
    # Telegram
    _enviar_telegram(picks)

def _guardar_local(picks):
    output_path = os.path.join("..", "frontend", "public", "picks.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(picks, f, indent=4, ensure_ascii=False)
    print(f"   📁 Picks guardados en local: {output_path}")

def _enviar_telegram(picks):
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            return

        mensaje = "👑 REY TACO PICKS 5.0 👑\n\n"
        for p in picks:
            valor = " 💎VALOR" if p.get('tiene_valor') else ""
            parlay = "🔗 PARLAY: " if p.get('es_parlay') else ""
            mensaje += f"{parlay}{p.get('categoria', '')}\n"
            mensaje += f"  {p.get('partido', '')}\n"
            mensaje += f"  Pick: {p.get('pick', '')} @ {p.get('cuota', '')}{valor}\n"
            mensaje += f"  Confianza: {p.get('confianza', '')}\n\n"
        
        mensaje += "Revisa la web para el analisis completo."

        # Enviar al chat privado
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": mensaje}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            if resp.getcode() == 200:
                print("   📱 ✅ Telegram (privado) enviado.")
        
        # Enviar al canal público (si está configurado)
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        if channel_id:
            data_ch = json.dumps({"chat_id": channel_id, "text": mensaje}).encode('utf-8')
            req_ch = urllib.request.Request(url, data=data_ch, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req_ch) as resp_ch:
                if resp_ch.getcode() == 200:
                    print("   📢 ✅ Telegram (canal) enviado.")
    except Exception as e:
        print(f"   📱 ❌ Error Telegram: {e}")

# ============================================================
#  MAIN: ORQUESTADOR DE FASES
# ============================================================
def main():
    print("\n" + "="*60)
    print("🌮  REY TACO PICKS BOT v5.0  🌮")
    print("   Arquitectura: Escáner → Mercado → Filtro → Inmersión → Memoria → IA → Picks")
    print("="*60)
    
    driver = None
    try:
        driver = get_chrome_driver()
        
        # Fase 1: Radar
        partidos = fase1_escaneo_superficie(driver)
        if not partidos:
            print("\n❌ No se encontraron partidos. Abortando.")
            return
        
        # Fase 2: Cuotas del mercado global
        market_odds = fase2_comparacion_mercado(partidos)
        
        # Fase 3: Filtro Inteligente
        objetivos = fase3_filtro_inteligente(partidos)
        
        # Fase 4: Inmersión Quirúrgica
        datos_profundos = fase4_inmersion(driver, objetivos, partidos)
        
        # Fase 5: Memoria Histórica
        memoria = fase5_memoria_historica()
        
        # Fase 6: Análisis Final
        picks = fase6_analisis_final(datos_profundos, memoria, market_odds)
        
        # Fase 7: Guardar y Notificar
        fase7_guardar_y_notificar(picks)
        
        print("\n" + "="*60)
        print("✅  MISIÓN COMPLETADA. Revisa tu página web.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
            print("🔒 Navegador cerrado.")

if __name__ == "__main__":
    main()
