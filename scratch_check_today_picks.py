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

print(f"Total picks pendientes vigentes para HOY: {len(resp.data)}")
for p in resp.data:
    print(f" - [{p.get('categoria')}] {p.get('partido')} | {p.get('pick')} @ {p.get('cuota')}")
