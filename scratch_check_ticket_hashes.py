import os
import hashlib
from PIL import Image

tickets_dir = "frontend/public/tickets"
files = [f for f in os.listdir(tickets_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

hashes = {}
for f in files:
    path = os.path.join(tickets_dir, f)
    with open(path, "rb") as fp:
        data = fp.read()
        h = hashlib.md5(data).hexdigest()
        size = len(data)
        if h not in hashes:
            hashes[h] = []
        hashes[h].append((f, size))

print(f"Total archivos: {len(files)}, Hashes únicos: {len(hashes)}")
for h, file_list in hashes.items():
    print(f"Hash {h[:8]} ({file_list[0][1]} bytes): {[x[0] for x in file_list]}")
