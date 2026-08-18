with open("frontend/src/main.ts", "r", encoding="utf-8") as f:
    text = f.read()

keywords = ["calcula", "stake", "cuota", "parlay", "banco", "bankroll"]
for kw in keywords:
    count = text.lower().count(kw)
    print(f"Keyword '{kw}': {count} occurrences in main.ts")
