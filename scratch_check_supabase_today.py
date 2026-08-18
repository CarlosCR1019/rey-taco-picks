import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Check Supabase table public.picks for records created today (2026-08-18)
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

url = f"{supabase_url}/rest/v1/picks?order=created_at.desc&limit=10"
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}"
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        picks = json.loads(resp.read().decode())
        print(f"Total picks devueltos por Supabase: {len(picks)}")
        for p in picks:
            print(f"ID: {p.get('id')} | Partido: {p.get('partido') or p.get('evento')} | Pick: {p.get('pick') or p.get('seleccion')} | Cuota: {p.get('cuota')} | Creado: {p.get('created_at')} | Horario: {p.get('horario')}")
except Exception as e:
    print(f"Error consultando Supabase: {e}")
