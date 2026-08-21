import requests
import json

API_KEY = "AIzaSyDHqhOn-Bt9_QrFJLg_yuPAzVa0Nx4T7vQ"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

r = requests.get(url)
data = r.json()
print("Available Models:")
for m in data.get("models", []):
    name = m.get("name")
    methods = m.get("supportedGenerationMethods", [])
    if "image" in name.lower() or "imagen" in name.lower() or "generate" in str(methods).lower():
        print(f" - {name} -> {methods}")
