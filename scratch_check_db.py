import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('backend/.env')
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

resp = supabase.table("picks").select("*").order("id", desc=True).limit(8).execute()
print(f"Total picks frescos en Supabase: {len(resp.data)}")
for p in resp.data:
    print(f" - [{p.get('categoria')}] {p.get('partido')} | {p.get('pick')} @ {p.get('cuota')} | Estado: {p.get('estado')}")
