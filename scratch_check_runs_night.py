import urllib.request
import json

url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs?per_page=10"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total runs: {data.get('total_count')}")
        for r in data.get('workflow_runs', []):
            print(f"ID: {r['id']} | Event: {r['event']} | Status: {r['status']} | Conclusion: {r['conclusion']} | Created: {r['created_at']} | Head SHA: {r['head_sha'][:7]}")
except Exception as e:
    print(f"Error: {e}")
