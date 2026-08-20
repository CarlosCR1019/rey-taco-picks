with open("frontend/src/style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "filter" in line:
        print(f"Line {i+1}: {line.strip()}")
