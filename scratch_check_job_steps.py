import urllib.request
import json
import zipfile
import io

run_id = 32308640275
url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
req = urllib.request.Request(url, headers={"User-Agent": "AntigravityBot"})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        for j in data.get('jobs', []):
            print(f"Job: {j.get('name')} | Status: {j.get('status')} | Conclusion: {j.get('conclusion')} | Started: {j.get('started_at')} | Completed: {j.get('completed_at')}")
            for s in j.get('steps', []):
                print(f"   Step: {s.get('name')} | Status: {s.get('status')} | Conclusion: {s.get('conclusion')}")
except Exception as e:
    print(f"Error fetching jobs: {e}")
