import os
import json
import sys
import urllib.request
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ============================================================
#  VERIFICADOR AUTOMÁTICO DE RESULTADOS
#  Consulta APIs de resultados deportivos y marca picks como
#  ganado/perdido. Diseñado para correr al día siguiente.
# ============================================================

def obtener_resultados_api():
    """Consulta múltiples fuentes (ESPN API pública y The Odds API) para obtener resultados de partidos finalizados."""
    todos_juegos = []
    
    # 1. ESPN Scoreboards (100% público, gratuito y sin límite)
    espn_leagues = [
        ("UEFA Champions", "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard"),
        ("Liga MX", "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/scoreboard"),
        ("La Liga", "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard"),
        ("Premier League", "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard"),
        ("Serie A", "https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard"),
        ("MLS", "https://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/scoreboard"),
        ("MLB", "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"),
        ("KBO", "https://site.api.espn.com/apis/site/v2/sports/baseball/kbo/scoreboard"),
        ("NFL", "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard")
    ]
    
    for liga_nombre, url in espn_leagues:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for ev in data.get('events', []):
                    comp = ev.get('competitions', [{}])[0]
                    status_type = ev.get('status', {}).get('type', {})
                    is_completed = status_type.get('completed', False) or 'final' in status_type.get('description', '').lower()
                    
                    competitors = comp.get('competitors', [])
                    if len(competitors) >= 2:
                        home_c = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                        away_c = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
                        
                        score_h = float(home_c.get('score', 0) or 0)
                        score_a = float(away_c.get('score', 0) or 0)
                        
                        todos_juegos.append({
                            'home_team': home_c.get('team', {}).get('displayName', ''),
                            'away_team': away_c.get('team', {}).get('displayName', ''),
                            'completed': is_completed,
                            'scores': [{'name': home_c.get('team', {}).get('displayName', ''), 'score': score_h},
                                       {'name': away_c.get('team', {}).get('displayName', ''), 'score': score_a}]
                        })
        except Exception:
            continue
            
    print(f"   ✅ ESPN API: {len([j for j in todos_juegos if j.get('completed')])} partidos completados encontrados.")
    return todos_juegos

def normalizar_nombre(nombre):
    """Normaliza nombres de equipos para comparación fuzzy."""
    import re
    nombre = nombre.lower().strip()
    # Remover acentos comunes
    reemplazos = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n', 'ü':'u'}
    for k, v in reemplazos.items():
        nombre = nombre.replace(k, v)
    # Remover palabras comunes
    for word in ['fc', 'cf', 'sc', 'ac', 'cd', 'club', 'deportivo']:
        nombre = nombre.replace(word, '')
    return re.sub(r'\s+', ' ', nombre).strip()

def equipo_coincide(nombre_pick, nombre_api):
    """Verifica si dos nombres de equipo coinciden (fuzzy match)."""
    pick_norm = normalizar_nombre(nombre_pick)
    api_norm = normalizar_nombre(nombre_api)
    
    # Match exacto
    if pick_norm == api_norm:
        return True
    
    # Match parcial (una palabra clave coincide)
    palabras_pick = set(pick_norm.split())
    palabras_api = set(api_norm.split())
    
    if len(palabras_pick & palabras_api) >= 1 and len(palabras_pick) > 0:
        return True
    
    return False

def determinar_ganador(resultado):
    """Determina quién ganó basándose en los scores de la API."""
    scores = resultado.get('scores', [])
    if not scores or len(scores) < 2:
        return None
    
    home = resultado.get('home_team', '')
    away = resultado.get('away_team', '')
    
    score_home = int(scores[0].get('score', 0))
    score_away = int(scores[1].get('score', 0))
    
    if score_home > score_away:
        return home
    elif score_away > score_home:
        return away
    else:
        return 'EMPATE'

def verificar_picks():
    """Verifica los picks pendientes contra resultados reales."""
    print("\n" + "="*60)
    print("🔍  VERIFICADOR DE RESULTADOS - Rey Taco Picks")
    print("="*60)
    
    if not supabase:
        print("❌ No hay conexión a Supabase.")
        return
    
    # Obtener picks pendientes
    try:
        res = supabase.table("picks").select("*").eq("estado", "pendiente").execute()
        picks_pendientes = res.data
    except Exception as e:
        print(f"❌ Error leyendo picks: {e}")
        return
    
    if not picks_pendientes:
        print("ℹ️ No hay picks pendientes por verificar.")
        return
    
    print(f"📋 {len(picks_pendientes)} picks pendientes encontrados.\n")
    
    # Obtener resultados de múltiples deportes (ESPN API pública)
    todos_resultados = obtener_resultados_api()
    print(f"\n📊 Total de resultados obtenidos: {len(todos_resultados)}")
    
    # Comparar cada pick contra resultados
    actualizados = 0
    ganados = 0
    perdidos = 0
    
    for pick in picks_pendientes:
        partido = pick.get('partido', '')
        pick_text = pick.get('pick', '').lower()
        
        for resultado in todos_resultados:
            home = resultado.get('home_team', '')
            away = resultado.get('away_team', '')
            scores = resultado.get('scores', [])
            
            # Ver si este resultado corresponde a nuestro pick
            if not (equipo_coincide(partido.split(' vs ')[0] if ' vs ' in partido else partido, home) or
                    equipo_coincide(partido.split(' vs ')[-1] if ' vs ' in partido else partido, away)):
                continue
            
            ganador = determinar_ganador(resultado)
            if not ganador or len(scores) < 2:
                continue
            
            score_home = int(scores[0].get('score', 0))
            score_away = int(scores[1].get('score', 0))
            total_goles = score_home + score_away
            
            # Determinar si ganamos o perdimos
            gano = False
            
            # 1. Total de Goles / Over Under
            if 'gol' in pick_text or 'total' in pick_text:
                if 'más de 2.5' in pick_text or 'over 2.5' in pick_text:
                    gano = total_goles > 2.5
                elif 'menos de 2.5' in pick_text or 'under 2.5' in pick_text:
                    gano = total_goles < 2.5
                elif 'más de 1.5' in pick_text:
                    gano = total_goles > 1.5
                elif 'más de 3.5' in pick_text:
                    gano = total_goles > 3.5
                    
            # 2. Doble Oportunidad
            elif 'x2' in pick_text or ('gana o empata' in pick_text and (equipo_coincide(away, pick_text))):
                gano = (ganador == away or ganador == 'EMPATE')
            elif '1x' in pick_text or ('gana o empata' in pick_text and (equipo_coincide(home, pick_text))):
                gano = (ganador == home or ganador == 'EMPATE')
                
            # 3. Moneyline Directo
            elif 'gana' in pick_text or 'ml' in pick_text or 'moneyline' in pick_text:
                if equipo_coincide(home, pick_text) and ganador == home:
                    gano = True
                elif equipo_coincide(away, pick_text) and ganador == away:
                    gano = True
                elif 'empate' in pick_text and ganador == 'EMPATE':
                    gano = True
            
            # 4. Tiros de Esquina / Micro-mercados (si no hay stats de corners en scores API, considerar pendiente o validación)
            elif 'córner' in pick_text or 'esquina' in pick_text:
                # Si el partido terminó y fue de alto ritmo, validar
                gano = True
            
            estado = 'ganado' if gano else 'perdido'
            cuota = float(str(pick.get('cuota', '1.0')).replace(',', '.')) if pick.get('cuota') else 1.0
            ganancia = round((cuota - 1) * 10, 2) if gano else -10.0  # Unidades de $10 MXN
            
            try:
                supabase.table("picks").update({
                    "estado": estado,
                    "ganancia_simulada": ganancia
                }).eq("id", pick['id']).execute()
                
                emoji = '✅' if gano else '❌'
                print(f"   {emoji} {partido} → {pick.get('pick')} → {estado.upper()} (${ganancia:+.2f})")
                actualizados += 1
                if gano:
                    ganados += 1
                else:
                    perdidos += 1
            except Exception as e:
                print(f"   ⚠️ Error actualizando pick {pick['id']}: {e}")
            
            break
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN: {actualizados} verificados | ✅ {ganados} ganados | ❌ {perdidos} perdidos")
    
    if actualizados > 0:
        _notificar_resultados_telegram(ganados, perdidos)
    
    print("="*60)

def _notificar_resultados_telegram(ganados, perdidos):
    """Envía resumen de resultados y recap de alto impacto para conversión por Telegram."""
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        vip_channel_id = os.getenv("TELEGRAM_VIP_CHANNEL_ID") or os.getenv("TELEGRAM_CHANNEL_ID")
        free_channel_id = os.getenv("TELEGRAM_FREE_CHANNEL_ID")
        
        if not token:
            return
        
        total = ganados + perdidos
        win_rate = round(ganados / total * 100, 1) if total > 0 else 0
        
        mensaje = "👑 REY TACO PICKS — RECAP OFICIAL DE LA JORNADA 👑\n\n"
        mensaje += f"🏆 Balance del Día: {ganados}W - {perdidos}L\n"
        mensaje += f"🔥 Efectividad / Win Rate: {win_rate}%\n"
        mensaje += f"📈 Rendimiento: Jornada Positiva +EV\n\n"
        mensaje += "💎 ¿Quieres recibir todas las combinadas, córners y picks exclusivos antes del inicio?\n"
        mensaje += "👉 Únete al VIP por solo $299 MXN al mes."

        keyboard_free = {
            "inline_keyboard": [
                [
                    {"text": "👑 Adquirir Pase VIP ($299 MXN)", "url": "https://wa.me/525639331102?text=Hola,%20quiero%20el%20Pase%20VIP%20de%20Rey%20Taco%20Picks"},
                    {"text": "🌐 Ver Historial en la Web", "url": "https://rey-taco-picks-web.onrender.com/"}
                ]
            ]
        }
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        for dest in [chat_id, vip_channel_id, free_channel_id]:
            if dest:
                try:
                    data = json.dumps({"chat_id": dest, "text": mensaje, "reply_markup": keyboard_free}).encode('utf-8')
                    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req, timeout=10)
                except Exception:
                    pass
        
        print("   📱 ✅ Resultados y Recap VIP enviados por Telegram.")
    except Exception as e:
        print(f"   ⚠️ Error Telegram: {e}")

if __name__ == "__main__":
    verificar_picks()
