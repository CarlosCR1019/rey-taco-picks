import os, re
filename = 'playdoit_source.html' if os.path.exists('playdoit_source.html') else 'backend/playdoit_source.html'

with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Buscar scripts inline con altenar
inline = re.findall(r'<script[^>]*>(.*?altenar.*?)</script>', content, re.DOTALL | re.IGNORECASE)
print('Scripts inline con altenar:', len(inline))
for s in inline[:3]:
    print('--> INLINE:\n', s[:600])
