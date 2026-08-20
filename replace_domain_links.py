import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

replaced_count = 0
files_modified = []

for root, dirs, files in os.walk("."):
    if ".git" in root or "node_modules" in root or "dist" in root:
        continue
    for file in files:
        if file.endswith(".py") or file.endswith(".ts") or file.endswith(".json") or file.endswith(".html") or file.endswith(".yml") or file.endswith(".md"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "rey-taco-picks-web.onrender.com" in content:
                    new_content = content.replace("https://reytacopicks.com/", "https://reytacopicks.com/")
                    new_content = new_content.replace("https://reytacopicks.com", "https://reytacopicks.com")
                    new_content = new_content.replace("https://reytacopicks.com", "https://reytacopicks.com")
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    files_modified.append(filepath)
                    replaced_count += content.count("rey-taco-picks-web.onrender.com")
            except Exception as e:
                print(f"Error procesando {filepath}: {e}")

print(f"✅ Se actualizaron {replaced_count} enlaces a 'https://reytacopicks.com' en {len(files_modified)} archivos:")
for fm in files_modified:
    print(" -", fm)
