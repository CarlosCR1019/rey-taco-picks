import os
import requests
import json

port_file = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort")
if os.path.exists(port_file):
    with open(port_file, "r") as f:
        lines = f.readlines()
        port = lines[0].strip()
        print(f"DevToolsActivePort encontrado en puerto: {port}")
        try:
            r = requests.get(f"http://127.0.0.1:{port}/json/list")
            tabs = r.json()
            print(f"Total tabs abiertos: {len(tabs)}")
            for t in tabs:
                print(f" - [{t.get('title')}] URL: {t.get('url')}")
        except Exception as e:
            print(f"Error conectando a Chrome debugging: {e}")
else:
    print("DevToolsActivePort no encontrado. Chrome no tiene puerto de depuración activo.")
