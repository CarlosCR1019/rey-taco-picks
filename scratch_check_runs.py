import urllib.request
import json

url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs"
req = urllib.request.Request(url, headers={"User-Agent": "AntigravityBot"})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Total workflow runs: {data.get('total_count')}")
        for r in data.get('workflow_runs', [])[:8]:
            print(f" - ID: {r.get('id')} | Event: {r.get('event')} | Status: {r.get('status')} | Conclusion: {r.get('conclusion')} | Created: {r.get('created_at')} | Name: {r.get('name')}")
except Exception as e:
    print(f"Error fetching runs: {e}")
