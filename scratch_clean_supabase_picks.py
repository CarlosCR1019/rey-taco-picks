import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
res = supabase.table('picks').delete().eq('estado', 'pendiente').execute()
print(f"Picks pendientes antiguos eliminados: {len(res.data) if res.data else 0}")
