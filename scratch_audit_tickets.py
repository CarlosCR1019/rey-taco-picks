import os
import hashlib
import json

tickets_dir = "frontend/public/tickets"
manifest_file = os.path.join(tickets_dir, "manifest.json")

print("=== INSPECCIÓN DE TODOS LOS TICKETS EN EL DIRECTORIO ===")
files = [f for f in os.listdir(tickets_dir) if f.endswith('.jpg') or f.endswith('.png')]

hashes = {}
for f in sorted(files):
    path = os.path.join(tickets_dir, f)
    size = os.path.getsize(path)
    with open(path, "rb") as fp:
        md5 = hashlib.md5(fp.read()).hexdigest()
    if md5 not in hashes:
        hashes[md5] = []
    hashes[md5].append((f, size))

print(f"Total archivos: {len(files)} | Hashes únicos: {len(hashes)}")
for h, items in hashes.items():
    print(f"\nHash MD5 {h[:8]}: {len(items)} archivo(s)")
    for name, sz in items:
        print(f"  - {name} ({sz} bytes)")

if os.path.exists(manifest_file):
    with open(manifest_file, "r", encoding="utf-8") as mf:
        print("\nManifest actual:", json.load(mf))
