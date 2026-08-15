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

def obtener_resultados_api(sport_key='soccer'):
    """Consulta The Odds API para resultados recientes (scores)."""
    if not ODDS_API_KEY:
        print("⚠️ No hay ODDS_API_KEY configurada.")
        return []
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/scores/?apiKey={ODDS_API_KEY}&daysFrom=1"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            completados = [g for g in data if g.get('completed')]
            print(f"   ✅ {sport_key}: {len(completados)} juegos completados encontrados.")
            return completados
    except Exception as e:
        print(f"   ❌ Error consultando resultados de {sport_key}: {e}")
        return []

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
    
    # Obtener resultados de múltiples deportes
    todos_resultados = []
    for sport in ['soccer_mexico_ligamx', 'soccer_spain_la_liga', 'soccer_italy_serie_a',
                   'soccer_uefa_champs_league', 'soccer_usa_mls', 'soccer_brazil_serie_a',
                   'americanfootball_nfl', 'baseball_mlb']:
        resultados = obtener_resultados_api(sport)
        todos_resultados.extend(resultados)
    
    print(f"\n📊 Total de resultados obtenidos: {len(todos_resultados)}")
    
    # Comparar cada pick contra resultados
    actualizados = 0
    ganados = 0
    perdidos = 0
    
    for pick in picks_pendientes:
        if pick.get('es_parlay'):
            continue  # Parlays se verifican diferente
        
        partido = pick.get('partido', '')
        pick_text = pick.get('pick', '').lower()
        
        for resultado in todos_resultados:
            home = resultado.get('home_team', '')
            away = resultado.get('away_team', '')
            
            # Ver si este resultado corresponde a nuestro pick
            if not (equipo_coincide(partido.split(' vs ')[0] if ' vs ' in partido else partido, home) or
                    equipo_coincide(partido.split(' vs ')[-1] if ' vs ' in partido else partido, away)):
                continue
            
            ganador = determinar_ganador(resultado)
            if not ganador:
                continue
            
            # Determinar si ganamos o perdimos
            gano = False
            if 'gana' in pick_text or 'ml' in pick_text or 'moneyline' in pick_text:
                # Pick de moneyline
                for equipo_pick in [pick.get('pick', '')]:
                    if equipo_coincide(equipo_pick, ganador):
                        gano = True
                    elif ganador == 'EMPATE' and 'empate' in pick_text:
                        gano = True
            
            estado = 'ganado' if gano else 'perdido'
            cuota = float(pick.get('cuota', '1.0').replace(',', '.')) if pick.get('cuota') else 1.0
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
    """Envía resumen de resultados por Telegram."""
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        
        if not token:
            return
        
        total = ganados + perdidos
        win_rate = round(ganados / total * 100, 1) if total > 0 else 0
        
        mensaje = f"📊 RESULTADOS DEL DÍA\n\n"
        mensaje += f"✅ Ganados: {ganados}\n"
        mensaje += f"❌ Perdidos: {perdidos}\n"
        mensaje += f"📈 Win Rate: {win_rate}%\n\n"
        mensaje += f"Revisa la web para el detalle completo."
        
        for dest in [chat_id, channel_id]:
            if dest:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = json.dumps({"chat_id": dest, "text": mensaje}).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req)
        
        print("   📱 Resultados enviados por Telegram.")
    except Exception as e:
        print(f"   ⚠️ Error Telegram: {e}")

if __name__ == "__main__":
    verificar_picks()
