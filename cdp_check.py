import json
import urllib.request

try:
    req = urllib.request.Request("http://127.0.0.1:9222/json/version")
    with urllib.request.urlopen(req) as resp:
        print("Version info:", resp.read().decode())
except Exception as e:
    print("Error:", e)
