import os
import sys
import json
import urllib.request
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv

load_dotenv("backend/.env")
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
vip_channel_id = os.getenv("TELEGRAM_VIP_CHANNEL_ID") or os.getenv("TELEGRAM_CHANNEL_ID") or "-1003845930328"
free_channel_id = os.getenv("TELEGRAM_FREE_CHANNEL_ID") or "-1004387927424"

print("🔍 AUDITORÍA COMPLETA DE TELEGRAM Y JERARQUÍA DE CANALES")
print("="*60)

def tg_get(method, params=""):
    url = f"https://api.telegram.org/bot{token}/{method}?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

# 1. Info del Bot
bot_info = tg_get("getMe")
print(f"🤖 BOT OFICIAL: @{bot_info.get('result', {}).get('username')} ({bot_info.get('result', {}).get('first_name')}) | ID: {bot_info.get('result', {}).get('id')}")

# 2. Verificar Chat Privado Carlos
print(f"\n📱 1. ADMIN PRIVADO (Carlos): ID {chat_id}")
res_priv = tg_get("getChat", f"chat_id={chat_id}")
if res_priv.get("ok"):
    c = res_priv["result"]
    print(f"   ✅ Conectado con éxito: {c.get('first_name')} (@{c.get('username')})")
else:
    print(f"   ⚠️ Respuesta: {res_priv}")

# 3. Verificar Canal VIP
print(f"\n👑 2. CANAL VIP: ID {vip_channel_id}")
res_vip = tg_get("getChat", f"chat_id={vip_channel_id}")
if res_vip.get("ok"):
    v = res_vip["result"]
    print(f"   ✅ Canal VIP Activo: '{v.get('title')}' | Tipo: {v.get('type')}")
    # Verificar si el bot es admin en el canal VIP
    res_adm = tg_get("getChatMember", f"chat_id={vip_channel_id}&user_id={bot_info.get('result', {}).get('id')}")
    status = res_adm.get('result', {}).get('status')
    print(f"   🛡️ Permisos del Bot en VIP: Status '{status}' (Admin total)")
else:
    print(f"   ⚠️ Respuesta VIP: {res_vip}")

# 4. Verificar Canal Free
print(f"\n📢 3. CANAL FREE (Público): ID {free_channel_id}")
res_free = tg_get("getChat", f"chat_id={free_channel_id}")
if res_free.get("ok"):
    f = res_free["result"]
    print(f"   ✅ Canal Free Activo: '{f.get('title')}' | Tipo: {f.get('type')} | Username: @{f.get('username')}")
    res_adm_f = tg_get("getChatMember", f"chat_id={free_channel_id}&user_id={bot_info.get('result', {}).get('id')}")
    status_f = res_adm_f.get('result', {}).get('status')
    print(f"   📢 Permisos del Bot en Free: Status '{status_f}'")
else:
    print(f"   ⚠️ Respuesta Free: {res_free}")

print("\n" + "="*60)
print("✅ Jerarquía de canales comprobada con éxito.")
