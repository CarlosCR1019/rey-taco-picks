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
resp = supabase.table("picks").select("*").order("id", desc=True).limit(15).execute()

print(f"Últimos {len(resp.data)} registros en Supabase table 'picks':")
for p in resp.data:
    print(f"ID {p.get('id')}: [{p.get('categoria')}] {p.get('partido')} | {p.get('pick')} | Estado: {p.get('estado')}")
