import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs?per_page=10"
headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total runs: {data.get('total_count')}")
        for r in data.get('workflow_runs', []):
            print(f"ID: {r.get('id')} | Event: {r.get('event')} | Status: {r.get('status')} | Conclusion: {r.get('conclusion')} | CreatedAt: {r.get('created_at')} | Name: {r.get('name')}")
except Exception as e:
    print(f"Error: {e}")
