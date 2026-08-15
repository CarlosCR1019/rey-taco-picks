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
def get_chrome_version():
    """Detecta la versión mayor de Google Chrome instalada en el sistema (Linux / Windows / Mac)."""
    # 1. En Linux / Mac / CLI (GitHub Actions usa Ubuntu)
    try:
        import subprocess
        for cmd in ["google-chrome --version", "google-chrome-stable --version", "chromium --version", "chromium-browser --version", "chrome --version"]:
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
                match = re.search(r'(\d+)\.\d+\.\d+', output)
                if match:
                    return int(match.group(1))
            except Exception:
                continue
    except Exception:
        pass

    # 2. En Windows (Registro de Windows)
    try:
        import winreg
        for root in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                key = winreg.OpenKey(root, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return int(version.split('.')[0])
            except Exception:
                pass
    except Exception:
        pass

    # 3. Fallback inteligente en CI / GitHub Actions
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        return 151

    return None

def get_chrome_driver():
    def make_options():
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
        return options, is_ci

    opts, is_ci = make_options()
    if is_ci:
        print("   ☁️ Modo NUBE detectado (headless)")
    else:
        print("   🖥️ Modo LOCAL detectado (con ventana)")

    chrome_ver = get_chrome_version()
    if chrome_ver:
        print(f"   🌐 Google Chrome v{chrome_ver} detectado")
        try:
            fresh_opts, _ = make_options()
            return uc.Chrome(options=fresh_opts, version_main=chrome_ver)
        except Exception as e:
            print(f"   ⚠️ Intentando inicialización estándar: {e}")

    try:
        fresh_opts, _ = make_options()
        return uc.Chrome(options=fresh_opts)
    except Exception:
        fresh_opts, _ = make_options()
        return uc.Chrome(options=fresh_opts, version_main=None)

# ============================================================
#  UTILIDADES DE NAVEGACIÓN (Shadow DOM de Altenar)
# ============================================================
def get_shadow_script():
    return """
    function getShadow() {
        var host = document.querySelector('div#altenar > div');
        if (host && host.shadowRoot) return host.shadowRoot;
        var all = document.querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
            if (all[i].shadowRoot) return all[i].shadowRoot;
        }
        return null;
    }
    """

def click_tab_hoy(driver):
    """Hace clic en la pestaña 'Hoy' para filtrar solo eventos del día."""
    script = get_shadow_script() + """
    try {
        var shadow = getShadow();
        if(!shadow) return false;
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
    script = get_shadow_script() + """
    try {
        var shadow = getShadow();
        if(!shadow) return false;
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
    script = get_shadow_script() + f"""
    try {{
        var shadow = getShadow();
        if(!shadow) return false;
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
    """Extrae los eventos visibles de la página actual del Shadow DOM filtrando estrictamente hoy y mañana con su horario."""
    script = get_shadow_script() + """
    var shadow = getShadow();
    if(!shadow) return [];
    var containers = shadow.querySelectorAll('div[class*="EventBoxContainer"]');
    var result = [];
    
    // Obtener días actuales para filtrar fechas lejanas
    var hoy = new Date();
    var diaHoy = hoy.getDate();
    var diaManana = (new Date(hoy.getTime() + 24*60*60*1000)).getDate();
    var diaPasado = (new Date(hoy.getTime() + 48*60*60*1000)).getDate();
    var diasValidos = [diaHoy, diaManana, diaPasado];

    containers.forEach(c => {
        try {
            var fullText = c.innerText.toLowerCase();
            
            // Si el contenedor o su sección indica fechas lejanas (más de 2 días), descartar
            var esFuturoLejano = false;
            var matchFecha = fullText.match(/(\d{1,2})\s*(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)/);
            if (matchFecha) {
                var diaNum = parseInt(matchFecha[1]);
                if (!diasValidos.includes(diaNum)) {
                    esFuturoLejano = true;
                }
            }

            if (esFuturoLejano) return;

            // Extraer hora/fecha del partido
            var timeEl = c.querySelector('div[class*="EventTime-"], div[class*="Time-"], span[class*="Time-"], div[class*="LiveIndicator"]');
            var horarioStr = "Hoy";
            if (timeEl && timeEl.innerText.trim()) {
                horarioStr = timeEl.innerText.trim();
            } else if (fullText.includes("en vivo") || fullText.includes("live")) {
                horarioStr = "En Vivo 🔴";
            } else {
                var matchHora = c.innerText.match(/(\d{1,2}:\d{2})/);
                if (matchHora) {
                    horarioStr = "Hoy " + matchHora[1] + " hrs";
                }
            }

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
                    horario: horarioStr,
                    texto: c.innerText
                });
            }
        } catch(e) {}
    });
    return result;
    """
    return driver.execute_script(script) or []

def obtener_eventos_odds_api():
    """Fallback inteligente: Si Playdoit no responde o está en mantenimiento, obtiene partidos de HOY y MAÑANA de The Odds API con fecha/hora CDMX."""
    if not ODDS_API_KEY:
        return []
    
    print("\n🌐 Conectando satélite The Odds API (Liga MX, MLB, La Liga, MLS, Premier)...")
    sports = ['soccer_mexico_ligamx', 'baseball_mlb', 'soccer_spain_la_liga', 'soccer_usa_mls', 'soccer_epl']
    eventos_api = []
    
    # Límites de tiempo: máximo 36 horas desde este instante
    from datetime import datetime, timezone, timedelta
    now_utc = datetime.now(timezone.utc)
    max_time_utc = now_utc + timedelta(hours=36)
    
    for s in sports:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{s}/odds/?apiKey={ODDS_API_KEY}&regions=us,eu&markets=h2h"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                for match in data:
                    commence_str = match.get('commence_time')
                    horario_str = "Hoy"
                    if commence_str:
                        try:
                            match_dt = datetime.fromisoformat(commence_str.replace('Z', '+00:00'))
                            if match_dt > max_time_utc:
                                continue # Descartar partidos de fechas lejanas
                            
                            # Convertir a hora de México (UTC-6)
                            cdmx_dt = match_dt - timedelta(hours=6)
                            hoy_cdmx = (now_utc - timedelta(hours=6)).date()
                            if cdmx_dt.date() == hoy_cdmx:
                                horario_str = f"Hoy {cdmx_dt.strftime('%H:%M')} hrs"
                            elif cdmx_dt.date() == hoy_cdmx + timedelta(days=1):
                                horario_str = f"Mañana {cdmx_dt.strftime('%H:%M')} hrs"
                            else:
                                horario_str = cdmx_dt.strftime("%d/%m %H:%M hrs")
                        except Exception:
                            horario_str = "Hoy"

                    home = match.get('home_team')
                    away = match.get('away_team')
                    cuotas = []
                    for bookmaker in match.get('bookmakers', []):
                        for market in bookmaker.get('markets', []):
                            if market.get('key') == 'h2h':
                                outcomes = market.get('outcomes', [])
                                if len(outcomes) >= 2 and not cuotas:
                                    cuotas = [str(o.get('price')) for o in outcomes]
                    
                    nombre = f"{home} vs {away}"
                    if not any(x["partido"] == nombre for x in eventos_api):
                        deporte_cat = "Liga MX" if "ligamx" in s else ("MLB" if "baseball" in s else ("La Liga" if "spain" in s else "Fútbol"))
                        eventos_api.append({
                            "categoria": deporte_cat,
                            "partido": nombre,
                            "local": home,
                            "visitante": away,
                            "horario": horario_str,
                            "cuotas_superficie": cuotas[:3] if cuotas else ["1.85", "3.20", "2.10"],
                            "info_texto": f"{deporte_cat}: {home} vs {away}. Horario: {horario_str}. Cuotas: {', '.join(cuotas) if cuotas else '1.85, 3.20'}"
                        })
        except Exception as e:
            print(f"   ⚠️ Error en {s}: {e}")
            
    print(f"   ✅ {len(eventos_api)} partidos reales de HOY/MAÑANA listos para análisis.")
    return eventos_api

# ============================================================
#  FASE 1: ESCÁNER RADAR DE SUPERFICIE
# ============================================================
def fase1_escaneo_superficie(driver):
    print("\n" + "="*60)
    print("🕵️  FASE 1: ESCÁNER RADAR DE SUPERFICIE (Solo Hoy y Mañana)")
    print("="*60)
    
    partidos_data = []
    try:
        driver.get("https://www.playdoit.mx/es/")
        time.sleep(8)
        
        # Configuración inicial
        click_decimal_toggle(driver)
        click_tab_hoy(driver)
        
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
                time.sleep(2)
                click_tab_hoy(driver) # Asegurar que solo vemos Hoy al entrar a cada categoría
                time.sleep(1)
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
    except Exception as e:
        print(f"   ⚠️ Nota en escáner Playdoit: {e}")
    
    if not partidos_data:
        print("   ℹ️ Escáner de superficie Playdoit no detectó partidos activos de hoy. Activando satélite The Odds API...")
        partidos_data = obtener_eventos_odds_api()
        
    print(f"\n   📊 Total eventos únicos de HOY/MAÑANA para análisis: {len(partidos_data)}")
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
    Catálogo de {len(catalogo)} eventos deportivos. 
    REGLA CRÍTICA DE TIEMPO (CERO TOLERANCIA):
    - Selecciona ÚNICAMENTE partidos que se jueguen HOY O MAÑANA a más tardar.
    - PROHIBIDO rotundo elegir partidos de fechas futuras (próxima semana o meses siguientes).
    
    Selecciona EXACTAMENTE 15 partidos con mayor potencial, asegurando MÁXIMA DIVERSIDAD DEPORTIVA:
    - Incluir MLB (Béisbol de hoy), Fútbol Internacional (La Liga, Premier, Champions, Libertadores) y Liga MX que jueguen HOY o MAÑANA.
    - Si no hay juegos de NFL hoy o mañana, NO selecciones NFL.
    
    {json.dumps(catalogo)}
    
    Devuelve SOLO un JSON array de strings con los nombres exactos de los partidos.
    Ejemplo: ["New York Yankees vs Boston Red Sox", "Real Madrid vs Osasuna", "América vs Monterrey"]
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
#  FASE 4: INMERSIÓN QUIRÚRGICA (Insights, Córners, Crear Apuesta)
# ============================================================
def fase4_inmersion(driver, objetivos, partidos_data):
    print("\n" + "="*60)
    print("🎯  FASE 4: INMERSIÓN QUIRÚRGICA (Insights + Mercados Profundos)")
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
        click_decimal_toggle(driver)
        
        # Clic en categoría
        click_category(driver, base['categoria'])
        time.sleep(3)
        
        # Clic en el partido específico dentro del Shadow DOM
        script_click = f"""
        try {{
            var host = Array.from(document.querySelectorAll('*')).find(el => el.shadowRoot);
            if (!host) return false;
            var shadow = host.shadowRoot;
            var names = shadow.querySelectorAll('div[class*="CompetitorName-"], [class*="CompetitorsContainer"]');
            var match = Array.from(names).find(n => n.innerText && n.innerText.toLowerCase().includes("{base['local'].lower()}"));
            if(match) {{ 
                match.click(); 
                if (match.parentElement) match.parentElement.click();
                return true; 
            }}
            return false;
        }} catch(e) {{ return false; }}
        """
        
        if driver.execute_script(script_click):
            time.sleep(4)
            
            # PASO A: Extraer Pestaña 'Insights' (Rachas, Tendencias Estadísticas y Desajustes)
            script_extract_insights = """
            try {
                var host = Array.from(document.querySelectorAll('*')).find(el => el.shadowRoot);
                if (!host) return "";
                var shadow = host.shadowRoot;
                
                // Clic en pestaña 'Insights' si existe
                var insightsBtn = Array.from(shadow.querySelectorAll('button, [role="tab"]')).find(function(b) {
                    return b.innerText && b.innerText.trim().toLowerCase() === 'insights';
                });
                
                if (insightsBtn) {
                    insightsBtn.click();
                }
                
                var cards = Array.from(shadow.querySelectorAll('[class*="EventDetailsMarketBoxRoot"], [class*="MarketBoxContainer"] > div'));
                var insightsList = [];
                
                cards.forEach(function(card) {
                    var textEls = Array.from(card.querySelectorAll('div, p, span')).filter(function(el) {
                        var txt = el.innerText ? el.innerText.trim() : '';
                        return (txt.includes('últimos') || txt.includes('partidos') || txt.includes('concedido') || txt.includes('ganado') || txt.includes('perdido') || txt.includes('convertido')) && el.children.length === 0;
                    });
                    
                    var buttons = Array.from(card.querySelectorAll('button')).map(function(b) {
                        return b.innerText.trim().replace(/\\n+/g, ' ');
                    });
                    
                    if (textEls.length > 0 && buttons.length > 0) {
                        insightsList.push("💡 TENDENCIA INSIGHT: " + textEls.map(function(t) { return t.innerText.trim(); }).join(" ") + " [Cuotas: " + buttons.join(" | ") + "]");
                    }
                });
                
                return insightsList.join("\\n");
            } catch(e) { return ""; }
            """
            
            insights_texto = driver.execute_script(script_extract_insights) or ""
            if insights_texto:
                print(f"      👁️ {len(insights_texto.splitlines())} Insights estadísticos y rachas capturadas.")
            
            # PASO B: Clic en 'Todas' o 'Crear Apuesta' para extraer mercados profundos
            script_extract_deep_markets = """
            try {
                var host = Array.from(document.querySelectorAll('*')).find(el => el.shadowRoot);
                if (!host) return "";
                var shadow = host.shadowRoot;
                
                // Regresar a 'Todas' o 'Principal' para capturar Córners, Remates y Hándicaps
                var todasBtn = Array.from(shadow.querySelectorAll('button, [role="tab"]')).find(function(b) {
                    return b.innerText && (b.innerText.trim().toLowerCase() === 'todas' || b.innerText.trim().toLowerCase() === 'principal');
                });
                if (todasBtn) { todasBtn.click(); }
                
                var marketBoxes = Array.from(shadow.querySelectorAll('[class*="EventDetailsMarketBoxRoot"], [class*="EventDetailsMarketBoxContainer"]'));
                var marketSummary = [];
                
                marketBoxes.forEach(function(box) {
                    var nameEl = box.querySelector('[class*="EventDetailsMarketName"], [class*="MarketName"]');
                    var marketName = nameEl ? nameEl.innerText.trim() : "";
                    if (!marketName) return;
                    
                    var oddButtons = Array.from(box.querySelectorAll('button, [class*="OddBoxButton"]'));
                    var oddsList = oddButtons.map(function(btn) {
                        return btn.innerText.replace(/\\n+/g, ' ').trim();
                    }).filter(Boolean);
                    
                    if (oddsList.length > 0) {
                        marketSummary.push("▶ MERCADO [" + marketName + "]: " + oddsList.join(" | "));
                    }
                });
                
                return marketSummary.join("\\n");
            } catch(e) { return ""; }
            """
            
            mercados_texto = driver.execute_script(script_extract_deep_markets) or ""
            
            contenido_completo = ""
            if insights_texto:
                contenido_completo += "--- TENDENCIAS INSIGHTS DE PLAYDOIT ---\n" + insights_texto + "\n\n"
            if mercados_texto:
                contenido_completo += "--- MERCADOS PROFUNDOS & CÓRNERS ---\n" + mercados_texto
            
            datos_profundos.append({
                "categoria": base['categoria'],
                "partido": obj,
                "cuotas_superficie": base.get('cuotas_superficie', []),
                "mercados_profundos": contenido_completo[:7000]
            })
            print(f"      ✅ {len(contenido_completo[:7000])} caracteres de Insights + Mercados extraídos.")
        else:
            print(f"      ⚠️ No se pudo entrar al partido, usando cuotas de superficie.")
            datos_profundos.append(base)
    
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
    # Busca valor matemático (+EV), córners, combos y estadísticas.
    # -------------------------------------------------------------
    print("   🤖 [IA 1: Alpha Quant] Analizando mercados profundos (Córners, Combos, Props, Totales)...")
    prompt_quant = f"""
Eres "Alpha Quant", la IA líder en análisis cuantitativo y micro-estadísticas para apuestas deportivas de élite.
Analiza los siguientes partidos y mercados especiales:

{memoria}
{market_context}
DATOS DE PARTIDOS Y MERCADOS:
{datos_partidos_str}

REGLAS ESTRICTAS DE TAXONOMÍA DEPORTIVA (CERO TOLERANCIA A ERRORES):
1. FÚTBOL (Soccer / Liga MX / La Liga / Champions / Premier):
   - Mercados válidos: Tiros de Esquina (Córners ej. "Más de 8.5 Córners"), Ambos Anotan (BTTS), Over/Under Goles (ej. "Más de 2.5 Goles"), 1X2 / Doble Oportunidad, Hándicap Asiático, Tarjetas.
   - NUNCA uses términos de béisbol o americano en fútbol.
2. BÉISBOL (MLB):
   - Mercados válidos: Over/Under Carreras (ej. "Más de 8.5 Carreras"), Carreras en 1er Inning (ej. "Sin Carreras en el 1er Inning - NRFI" o "Más de 0.5 Carreras 1er Inning"), Ponches del Pitcher (ej. "Más de 6.5 Ponches"), Moneyline (-1.5 Run Line).
   - ¡PROHIBIDO ROTUNDAMENTE usar "Córners", "Goles" o "Tiros de esquina" en Béisbol! En béisbol son CARRERAS, HITS y PONCHES.
3. FÚTBOL AMERICANO (NFL):
   - Mercados válidos: Spread / Hándicap (ej. "-3.5"), Over/Under Puntos Totales (ej. "Más de 44.5 Puntos"), Player Props (ej. "Anotador de Touchdown", "Más de 75.5 Yardas").
   - ¡PROHIBIDO usar "Goles" o "Córners" en NFL! En americano son PUNTOS, TOUCHDOWNS y YARDAS.

REGLAS DE PARLAYS ESTRATÉGICOS:
- "Parlay Seguro": 2 selecciones de altísima probabilidad con cuota combinada 2.10 - 2.80.
- "Parlay Estadístico Córners/Props": 2 selecciones de micro-estadísticas (Córners de fútbol o Ponches/Carreras de MLB) cuota 2.70 - 3.80.
- "Parlay Rompe-Bancas (+EV)": 3 selecciones de alto valor combinado (cuota 4.50 - 7.50).

Devuelve tu catálogo cuantitativo con las justificaciones matemáticas respetando estrictamente la terminología de cada deporte.
"""
    try:
        resp_quant = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_quant}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        ).choices[0].message.content.strip()
        print("   ✅ [Alpha Quant] Propuestas de córners, combos y parlays generadas.")
    except Exception as e:
        print(f"   ⚠️ Error en IA Quant: {e}")
        resp_quant = "Análisis quant no disponible."

    # -------------------------------------------------------------
    # RONDA 2: IA AUDITORA DE RIESGO ("Risk Auditor" - Llama 3.1)
    # Audita trampas, líneas infladas de córners y correlación de parlays.
    # -------------------------------------------------------------
    print("   🛡️ [IA 2: Risk Auditor] Auditando riesgo en córners, combos y combinaciones de parlays...")
    prompt_auditor = f"""
Eres "Risk Auditor", auditor senior de gestión de riesgo en apuestas deportivas.
Revisa las propuestas de Alpha Quant:

PROPUESTAS DE ALPHA QUANT:
{resp_quant}

DATOS REALES:
{datos_partidos_str}

TAREA DE AUDITORÍA:
1. Verifica que la taxonomía deportiva sea 100% precisa (Córners y Goles SOLO en Fútbol; Carreras y Ponches SOLO en Béisbol; Puntos y Yardas SOLO en NFL). Rechaza cualquier propuesta que confunda deportes.
2. Evalúa si las líneas de Tiros de Esquina, Totales y Combos son realistas según el estilo de juego de los equipos.
3. Audita los Parlays: Asegúrate de que las selecciones combinadas tengan correlación positiva o bajo riesgo de cruzarse.
4. Si un pick o combinación es arriesgado, sugiere un ajuste más inteligente.

Devuelve tu dictamen de aprobación y ajustes recomendados.
"""
    try:
        resp_auditor = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_auditor}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        ).choices[0].message.content.strip()
        print("   ✅ [Risk Auditor] Auditoría de riesgo y correlación completada.")
    except Exception as e:
        print(f"   ⚠️ Error en IA Auditor: {e}")
        resp_auditor = "Auditoría no disponible."

    # -------------------------------------------------------------
    # RONDA 3: IA JUEZ SUPREMO ("Chief Arbiter" - Llama 3.3 70B)
    # Emite la selección definitiva multideporte + Tiros de Esquina + 2 Parlays.
    # -------------------------------------------------------------
    print("   ⚖️ [IA 3: Chief Arbiter] Emitiendo cartera definitiva (Córners, Combos y Parlays Múltiples)...")
    prompt_juez = f"""
Eres el "Chief Odds Arbiter" de Rey Taco Picks. Emite la cartera oficial del día tras evaluar el debate.

DEBATE DE LOS EXPERTOS:
--- ALPHA QUANT ---
{resp_quant}

--- AUDITORÍA DE RIESGO ---
{resp_auditor}

--- CUOTAS DE MERCADO GLOBAL ---
{market_context}

ESTRUCTURA OBLIGATORIA DE LA CARTERA (Total 7 a 9 objetos en JSON):
0. REGLA TEMPORAL CRÍTICA: TODOS LOS PICKS DEBEN SER EXCLUSIVAMENTE PARA PARTIDOS PROGRAMADOS PARA HOY O MAÑANA A MÁS TARDAR. PROHIBIDO seleccionar partidos de la próxima semana.
1. PICKS DE TIROS DE ESQUINA (Córners): SOLO PUEDEN SER DE PARTIDOS DE FÚTBOL (Liga MX, La Liga, Premier, Champions, etc.). Ejemplo: "Tigres vs Atlas | Más de 8.5 Córners". ¡NUNCA EN BÉISBOL!
2. PICKS DE BÉISBOL (MLB): Deben usar "Carreras" (Runs), "Ponches" (Strikeouts), "Hits" o "Moneyline". Ejemplo: "Astros vs Mariners | Más de 8.5 Carreras" o "Más de 0.5 Carreras en 1er Inning". ¡NUNCA "GOLES" O "CÓRNERS"!
3. PICKS DE FÚTBOL AMERICANO (NFL): Deben usar "Yardas", "Touchdowns", "Puntos" o "Spread" (SOLO si el partido se juega HOY o MAÑANA; si no hay partidos de NFL hoy/mañana, NO incluyas NFL).
4. DEBE HABER AL MENOS 2 PARLAYS DISTINTOS AL FINAL:
   - Parlay 1 ("Parlay Seguro"): 2 selecciones de altísima probabilidad con cuota combinada 2.10 - 2.80. Marcar "es_parlay": true.
   - Parlay 2 ("Parlay Estadístico Córners/Props" o "Parlay Bomba"): 2-3 selecciones con cuota combinada 3.20 - 6.50. Marcar "es_parlay": true.
5. Cuotas EXCLUSIVAMENTE en formato DECIMAL (ej. 1.85, 2.30, 3.40).
6. "categoria": "Tiros de Esquina" (SOLO fútbol), "Fútbol", "Béisbol", "Fútbol Americano", "Parlay Seguro", "Parlay Bomba", etc.

Devuelve ÚNICAMENTE un JSON array válido con este formato:
[
    {{
        "categoria": "Tiros de Esquina",
        "partido": "Tigres UANL vs Atlas",
        "horario": "Hoy 19:00 hrs",
        "pick": "Más de 8.5 Tiros de Esquina",
        "cuota": "1.85",
        "confianza": "90%",
        "razonamiento": "Consenso IA: Equipos con alto juego por bandas (promedio combinado de 11.2 córners por partido).",
        "es_parlay": false,
        "tiene_valor": true,
        "odds_mercado": "1.78"
    }},
    {{
        "categoria": "Béisbol",
        "partido": "Houston Astros vs Seattle Mariners",
        "horario": "Hoy 18:10 hrs",
        "pick": "Más de 8.5 Carreras Totales",
        "cuota": "1.90",
        "confianza": "85%",
        "razonamiento": "Condiciones de bateo favorables y efectividad alta de los relevistas.",
        "es_parlay": false,
        "tiene_valor": true,
        "odds_mercado": "1.85"
    }},
    {{
        "categoria": "Parlay Seguro",
        "partido": "América + NY Yankees",
        "horario": "Hoy 19:00 hrs / 18:05 hrs",
        "pick": "América Gana o Empata & Yankees Gana Directo",
        "cuota": "2.45",
        "confianza": "93%",
        "razonamiento": "Combinada de alta probabilidad aprobada por ambos analistas.",
        "es_parlay": true,
        "tiene_valor": true,
        "odds_mercado": "2.30"
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
        
        print(f"\n   🏆 CARTERA APROBADA ({len(picks)} selecciones de alta credibilidad):")
        for p in picks:
            valor = " 💎 VALOR" if p.get('tiene_valor') else ""
            parlay = " 🔗 PARLAY" if p.get('es_parlay') else ""
            horario = f" [{p.get('horario')}]" if p.get('horario') else ""
            print(f"      → [{p.get('categoria')}]{horario} {p.get('partido')} | {p.get('pick')} @ {p.get('cuota')}{valor}{parlay}")
        
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

def formatear_pick_canal(p, numero=1, total=1):
    valor = " 💎 VALOR +EV" if p.get('tiene_valor') else ""
    es_parlay = p.get('es_parlay')
    categoria = p.get('categoria', 'Deportes')
    partido = p.get('partido', '')
    pick_text = p.get('pick', '')
    cuota = p.get('cuota', '')
    confianza = p.get('confianza', '')
    razonamiento = p.get('razonamiento', '')
    odds_mkt = f" (Mercado: {p.get('odds_mercado')})" if p.get('odds_mercado') else ""
    horario_str = f"🕒 Horario: {p.get('horario', 'Hoy')}\n" if p.get('horario') else "🕒 Horario: Hoy (CDMX)\n"
    
    if es_parlay:
        header = f"👑 REY TACO PICKS 👑\n🔗 COMBINADA / PARLAY DESTACADO [{numero}/{total}]"
    elif "esquina" in categoria.lower() or "córner" in categoria.lower():
        header = f"👑 REY TACO PICKS 👑\n⛳ ANÁLISIS DE TIROS DE ESQUINA [{numero}/{total}]"
    elif "béisbol" in categoria.lower() or "mlb" in categoria.lower():
        header = f"👑 REY TACO PICKS 👑\n⚾ ANÁLISIS MLB / BÉISBOL [{numero}/{total}]"
    elif "americano" in categoria.lower() or "nfl" in categoria.lower():
        header = f"👑 REY TACO PICKS 👑\n🏈 ANÁLISIS NFL / AMERICANO [{numero}/{total}]"
    else:
        header = f"👑 REY TACO PICKS 👑\n⚽ ANÁLISIS DEL DÍA [{numero}/{total}]"
        
    msg = f"{header}\n\n"
    msg += f"🏟️ Evento: {partido}\n"
    msg += horario_str
    msg += f"🎯 Selección: {pick_text}\n"
    msg += f"📊 Cuota: {cuota}{odds_mkt}{valor}\n"
    msg += f"🔥 Confianza: {confianza}\n\n"
    
    if razonamiento:
        msg += f"🧠 Análisis Alpha (IA):\n{razonamiento}\n\n"
        
    msg += "🌐 Desbloquea la cartera completa y calculadora en vivo:\n👉 https://rey-taco-picks-web.onrender.com"
    return msg

def _enviar_telegram(picks):
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        vip_channel_id = os.getenv("TELEGRAM_VIP_CHANNEL_ID") or os.getenv("TELEGRAM_CHANNEL_ID")
        free_channel_id = os.getenv("TELEGRAM_FREE_CHANNEL_ID")
        
        if not token:
            return

        # 1. Enviar el reporte COMPLETO con todos los picks a Carlos (Privado)
        mensaje_completo = "👑 REY TACO PICKS VIP (CARTERA COMPLETA) 👑\n\n"
        for p in picks:
            valor = " 💎VALOR +EV" if p.get('tiene_valor') else ""
            parlay = "🔗 PARLAY: " if p.get('es_parlay') else ""
            horario = f"  🕒 {p.get('horario', 'Hoy')}\n" if p.get('horario') else ""
            mensaje_completo += f"{parlay}{p.get('categoria', '')}\n"
            mensaje_completo += f"  {p.get('partido', '')}\n"
            mensaje_completo += horario
            mensaje_completo += f"  Pick: {p.get('pick', '')} @ {p.get('cuota', '')}{valor}\n"
            mensaje_completo += f"  Confianza: {p.get('confianza', '')}\n\n"
        
        mensaje_completo += "🌐 Cartera completa en vivo: https://rey-taco-picks-web.onrender.com"

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        # Envío a Carlos
        if chat_id:
            data = json.dumps({"chat_id": chat_id, "text": mensaje_completo}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as resp:
                if resp.getcode() == 200:
                    print("   📱 ✅ Telegram (privado Carlos) enviado.")

        # 2. Envío INMEDIATO al CANAL VIP
        if vip_channel_id:
            data_vip = json.dumps({"chat_id": vip_channel_id, "text": mensaje_completo}).encode('utf-8')
            req_vip = urllib.request.Request(url, data=data_vip, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req_vip) as resp_vip:
                if resp_vip.getcode() == 200:
                    print("   👑 ✅ Telegram (Canal VIP) enviado con cartera completa.")

        # 3. Envío al CANAL FREE (Pick Estrella Inmediato + Cola Espaciada)
        if free_channel_id and picks:
            # A) Pick #1 Gratuito
            pick_1_msg = formatear_pick_canal(picks[0], numero=1, total=len(picks))
            data_free = json.dumps({"chat_id": free_channel_id, "text": pick_1_msg}).encode('utf-8')
            req_free = urllib.request.Request(url, data=data_free, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req_free) as resp_free:
                if resp_free.getcode() == 200:
                    print(f"   📢 ✅ Telegram (Canal FREE - Pick #1) enviado: {picks[0].get('partido')}")

            # B) Programar los picks restantes espaciados cada 75 min para el Canal Free
            queue_file = os.path.join(os.path.dirname(__file__), "channel_queue.json")
            queue = []
            now = time.time()
            intervalo_segundos = 75 * 60
            
            for i, p in enumerate(picks[1:], 2):
                prog_time = now + ((i - 1) * intervalo_segundos)
                queue.append({
                    "pick_id": p.get('id'),
                    "partido": p.get('partido'),
                    "timestamp_programado": prog_time,
                    "fecha_legible": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(prog_time)),
                    "mensaje": formatear_pick_canal(p, numero=i, total=len(picks)),
                    "enviado": False
                })
                
            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
            print(f"   ⏳ {len(queue)} picks programados en cola para publicarse espaciados en Canal FREE.")

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
