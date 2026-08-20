import requests
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Search for Draftea's public Android client configs, Firebase settings, or auth endpoints
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 1. Check if there are public Auth endpoints on api.draftea.com
auth_endpoints = [
    "/v1/auth/guest",
    "/v1/auth/anonymous",
    "/v1/auth/token",
    "/auth/token",
    "/api/v1/auth/guest",
    "/v1/public/props",
    "/v1/public/tournaments",
    "/public/props",
    "/v1/feed",
    "/v1/config"
]

print("📡 Probando endpoints de autenticación y públicos en api.draftea.com:")
for ep in auth_endpoints:
    url = f"https://api.draftea.com{ep}"
    try:
        r = requests.post(url, json={}, headers={"User-Agent": "DrafteaApp/5.16 (Android)", "Content-Type": "application/json"}, timeout=5)
        print(f" POST {ep:25} -> Status: {r.status_code} | Body: {r.text[:120]}")
    except Exception as e:
        print(f" POST {ep:25} -> Error: {e}")
        
    try:
        r = requests.get(url, headers={"User-Agent": "DrafteaApp/5.16 (Android)", "Content-Type": "application/json"}, timeout=5)
        print(f" GET  {ep:25} -> Status: {r.status_code} | Body: {r.text[:120]}")
    except Exception as e:
        print(f" GET  {ep:25} -> Error: {e}")
