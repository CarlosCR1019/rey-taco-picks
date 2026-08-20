import urllib.request
import json
from datetime import datetime

url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs?per_page=20"
req = urllib.request.Request(url, headers={"User-Agent": "AntigravityBot"})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Total workflow runs: {data.get('total_count')}")
        print("-" * 80)
        for r in data.get('workflow_runs', []):
            run_id = r.get('id')
            event = r.get('event')
            status = r.get('status')
            conclusion = r.get('conclusion')
            created_at = r.get('created_at')
            name = r.get('name')
            print(f"Run {run_id}: Event={event} | Status={status} | Conclusion={conclusion} | CreatedAt={created_at} | Name={name}")
except Exception as e:
    print(f"Error: {e}")
