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

# Eliminar todos los picks relacionados con Draftea
print("🧹 Limpiando registros de Draftea en Supabase...")
supabase.table("picks").delete().like("categoria", "%Draftea%").execute()
supabase.table("picks").delete().like("pick", "%BANCA+%").execute()
supabase.table("picks").delete().like("razonamiento", "%Draftea%").execute()

# Obtener los picks limpios y oficiales de Playdoit
resp = supabase.table("picks").select("*").eq("estado", "pendiente").order("id", desc=True).limit(100).execute()
clean_picks = resp.data or []

print(f"✅ Total picks activos de Playdoit en Supabase: {len(clean_picks)}")
for p in clean_picks:
    print(f" - [{p.get('categoria')}] {p.get('partido')} -> {p.get('pick')} | Cuota: {p.get('cuota')}")

# Guardar en frontend/public/picks.json
with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(clean_picks, f, ensure_ascii=False, indent=2)

print("✅ frontend/public/picks.json actualizado con picks exclusivos de Playdoit.")
