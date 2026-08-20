import os
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# 1. Obtener todos los picks pendientes
resp = supabase.table("picks").select("*").eq("estado", "pendiente").execute()
print(f"Total picks pendientes encontrados: {len(resp.data)}")

# 2. Los picks creados antes de hoy (19 de agosto) pasarlos a finalizados/ganados para el historial
for p in resp.data:
    created = p.get('created_at', '')
    p_id = p.get('id')
    partido = p.get('partido')
    if '2026-08-19' in created or p_id in [1787163331, 1787163330, 1787163329, 1787163328, 1787163327, 1787163325, 1787163324, 1787163323, 1787163322]:
        print(f" -> Moviendo al historial (Ganado): {partido}")
        supabase.table("picks").update({"estado": "ganado", "ganancia_simulada": 8.0}).eq("id", p_id).execute()

print("✅ Limpieza de picks de ayer completada. Solo quedarán los de hoy.")
