import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs?per_page=10"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total workflow runs encontrados: {data.get('total_count')}")
        for r in data.get('workflow_runs', []):
            print(f"- ID: {r.get('id')} | Event: {r.get('event')} | Status: {r.get('status')} | Conclusion: {r.get('conclusion')} | Created: {r.get('created_at')} | Head Commit: {r.get('head_commit', {}).get('message')[:40]}")
except Exception as e:
    print(f"Error consultando GitHub API: {e}")
