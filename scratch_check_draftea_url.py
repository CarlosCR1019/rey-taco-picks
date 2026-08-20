import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

for u in ["https://www.draftea.com", "https://draftea.com/mx", "https://draftea.mx"]:
    try:
        r = requests.get(u, headers=headers, timeout=10)
        print(f"URL: {u} -> Status: {r.status_code}, Final URL: {r.url}, Length: {len(r.text)}")
    except Exception as e:
        print(f"Error {u}: {e}")
