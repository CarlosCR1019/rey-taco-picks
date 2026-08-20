import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

r = requests.get("https://auth.draftea.com", headers={"User-Agent": "Mozilla/5.0"})
print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Body preview:\n{r.text[:500]}")
