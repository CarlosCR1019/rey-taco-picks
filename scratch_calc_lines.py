import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("frontend/src/main.ts", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l.lower() for k in ["calcula", "calculator"]):
        print(f"Line {i+1}: {l.strip()}")
