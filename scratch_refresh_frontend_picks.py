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

resp = supabase.table("picks").select("*").eq("estado", "pendiente").order("id", desc=True).execute()
picks = resp.data or []

with open("frontend/public/picks.json", "w", encoding="utf-8") as f:
    json.dump(picks, f, ensure_ascii=False, indent=2)

print(f"✅ frontend/public/picks.json actualizado con {len(picks)} picks vigentes.")
