import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
tickets_dir = "frontend/public/tickets"

official_tickets = [
    "ticket_1787030886.jpg",  # 17/08: Parlay Paradas Porteros @ 5.25 (Pachuca & Necaxa)
    "ticket_1787030798.jpg",  # 17/08: Boosted Remates @ 3.40 (Torres & Cambindo)
    "ticket_1787030974.jpg",  # 17/08: Necaxa Córners +8.5 @ 1.45
    "ticket_1786980498.jpg",  # 16/08: Parlay América & Chivas @ 2.32
    "ticket_1786980544.jpg",  # 16/08: Xolos Remates Gilberto Mora @ 2.00
    "ticket_1786857083.jpg",  # 15/08: Monterrey Boosted @ 3.60
    "ticket_1786856862.jpg",  # 15/08: Monterrey SGP @ 2.71
    "ticket_1786857038.jpg",  # 15/08: Atlas Córners @ 1.62 (CON SALDO OCULTO, SIN $10)
]

manifest_path = os.path.join(tickets_dir, "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(official_tickets, f, indent=2)

print("manifest.json actualizado con 8 tickets de saldos ocultos.")

all_files = [f for f in os.listdir(tickets_dir) if f.endswith('.jpg') or f.endswith('.png')]
for f in all_files:
    if f not in official_tickets and f != "manifest.json":
        full_path = os.path.join(tickets_dir, f)
        os.remove(full_path)
        print(f"Eliminado ticket no oficial / duplicado: {f}")

print("Directorio de tickets completamente limpio y depurado.")
