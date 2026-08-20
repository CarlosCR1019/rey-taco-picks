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

resp = supabase.table("picks").select("*").execute()
data = resp.data or []
print(f"Total picks in Supabase: {len(data)}")

playdoit_picks = [p for p in data if not 'draftea' in (p.get('categoria') or '').lower() and not 'banca+' in (p.get('pick') or '').lower()]
draftea_picks = [p for p in data if 'draftea' in (p.get('categoria') or '').lower() or 'banca+' in (p.get('pick') or '').lower()]

print(f"Playdoit picks count: {len(playdoit_picks)}")
print(f"Draftea picks count: {len(draftea_picks)}")

print("\n--- Playdoit Sample ---")
for p in playdoit_picks[:5]:
    print(f"[{p.get('categoria')}] {p.get('partido')} -> {p.get('pick')} | Estado: {p.get('estado')}")

print("\n--- Draftea Sample ---")
for p in draftea_picks[:5]:
    print(f"[{p.get('categoria')}] {p.get('partido')} -> {p.get('pick')} | Cuota: {p.get('cuota')}")
