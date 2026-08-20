import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

matches = []
for root, dirs, files in os.walk("."):
    if ".git" in root or "node_modules" in root or "dist" in root:
        continue
    for file in files:
        if file.endswith(".py") or file.endswith(".ts") or file.endswith(".json") or file.endswith(".html") or file.endswith(".yml"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f):
                        if "onrender.com" in line or "rey-taco-picks-web" in line:
                            matches.append((filepath, i+1, line.strip()))
            except Exception:
                pass

print(f"Total coincidencias de 'onrender.com': {len(matches)}")
for m in matches:
    print(f"{m[0]}:{m[1]} -> {m[2]}")
