import urllib.request
import json

url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs"
req = urllib.request.Request(url, headers={'User-Agent': 'Python-Script'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total runs found: {data.get('total_count')}")
        for r in data.get('workflow_runs', [])[:10]:
            print(f"Run ID: {r['id']} | Event: {r['event']} | Status: {r['status']} | Conclusion: {r['conclusion']} | CreatedAt: {r['created_at']} | Name: {r['name']}")
except Exception as e:
    print(f"Error fetching GitHub runs: {e}")
