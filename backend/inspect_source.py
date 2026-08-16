import os, re

filename = 'playdoit_source.html'
if not os.path.exists(filename):
    filename = 'backend/playdoit_source.html'

with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

scripts = re.findall(r'<script[^>]*src=[\'"](.*?)[\'"]', content)
print('Total scripts:', len(scripts))
for s in scripts:
    if any(k in s.lower() for k in ['altenar', 'sport', 'sb', 'widget', 'api', 'playdoit']):
        print('  JS:', s)

iframes = re.findall(r'<iframe[^>]*src=[\'"](.*?)[\'"]', content)
print('Total iframes:', len(iframes))
for i in iframes:
    print('  IFRAME:', i)

# Buscar URLs o endpoints en el HTML
endpoints = set(re.findall(r'https?://[a-zA-Z0-9\.\-_/]+', content))
print('\nEndpoints y dominios clave encontrados:')
for ep in endpoints:
    if any(k in ep.lower() for k in ['altenar', 'sportsbook', 'odds', 'feed', 'api']):
        print('  ENDPOINT:', ep)
