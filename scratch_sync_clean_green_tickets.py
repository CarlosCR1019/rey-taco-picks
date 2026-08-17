import json
import os
import sys
from supabase import create_client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Las 5 capturas ÚNICAS, 100% VERDES Y COBRADAS (sin duplicados, sin 'abierto', sin 'en vivo')
tickets_verdes_unicos = [
    {
        "archivo": "ticket_1786857083.jpg",
        "caption": "🏆 Monterrey vs Juárez (Boosted +1.5 Goles & +3.5 Córners) @ 3.60",
        "momio": "3.60",
        "id_apuesta": "5299160185"
    },
    {
        "archivo": "ticket_1786856862.jpg",
        "caption": "🏆 Monterrey vs Juárez (SGP 4-1: ML + Ocampos + Rossi) @ 2.71",
        "momio": "2.71",
        "id_apuesta": "5299148507"
    },
    {
        "archivo": "ticket_1786980498.jpg",
        "caption": "🏆 Parlay Liga MX: América (3:0) & Chivas (1:0) @ 2.32",
        "momio": "2.32",
        "id_apuesta": "5302792144"
    },
    {
        "archivo": "ticket_1786980544.jpg",
        "caption": "🏆 Xolos vs Cruz Azul (Remates Gilberto Mora) @ 2.00",
        "momio": "2.00",
        "id_apuesta": "5302789835"
    },
    {
        "archivo": "ticket_1786856993.jpg",
        "caption": "🏆 Atlas vs Tigres UANL (Más de 8.5 Córners) @ 1.62",
        "momio": "1.62",
        "id_apuesta": "5299503425"
    }
]

# Guardar manifest.json limpio
with open("frontend/public/tickets/manifest.json", "w", encoding="utf-8") as f:
    json.dump([t["archivo"] for t in tickets_verdes_unicos], f, indent=2)

print("✅ manifest.json actualizado con 5 tickets verdes únicos.")

# Actualizar Supabase
try:
    load_dotenv('backend/.env')
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    # Limpiar tabla
    supabase.table("tickets_ganadores").delete().neq("id", 0).execute()
    
    to_insert = []
    for idx, t in enumerate(tickets_verdes_unicos):
        to_insert.append({
            "id": idx + 1,
            "archivo": t["archivo"],
            "caption": t["caption"],
            "imagen_url": f"/tickets/{t['archivo']}"
        })
    supabase.table("tickets_ganadores").insert(to_insert).execute()
    print("✅ Supabase tickets_ganadores actualizado.")
except Exception as e:
    print(f"Supabase update: {e}")
