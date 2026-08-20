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

resp = supabase.table("picks").select("*").eq("estado", "pendiente").order("id", desc=True).limit(100).execute()
picks = resp.data or []

playdoit = [p for p in picks if not 'draftea' in (p.get('categoria') or '').lower() and not 'banca+' in (p.get('pick') or '').lower()]
draftea = [p for p in picks if 'draftea' in (p.get('categoria') or '').lower() or 'banca+' in (p.get('pick') or '').lower()]

print(f"Total picks pendientes: {len(picks)}")
print(f"Playdoit picks: {len(playdoit)}")
print(f"Draftea picks: {len(draftea)}")

# Save to picks.json
with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(picks, f, ensure_ascii=False, indent=2)

print("✅ picks.json sincronizado correctamente.")
