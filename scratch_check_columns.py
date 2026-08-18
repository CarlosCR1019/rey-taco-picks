import urllib.request
import json
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Fetch 1 record to see all keys
url = f"{supabase_url}/rest/v1/picks?limit=1"
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}"
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Columnas en public.picks:", list(data[0].keys()) if data else "Vacio")
        print("Ejemplo de registro:", data[0] if data else "None")
except Exception as e:
    print(f"Error: {e}")
