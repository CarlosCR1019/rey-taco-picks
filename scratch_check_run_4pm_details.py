import urllib.request
import json
import zipfile
import io

# Let's inspect the job logs from GitHub Actions
run_id = "32075864900"
url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        jobs = data.get('jobs', [])
        for j in jobs:
            print(f"Job: {j.get('name')} - ID: {j.get('id')}")
            for s in j.get('steps', []):
                print(f"  Step: {s.get('name')} | Status: {s.get('status')} | Conclusion: {s.get('conclusion')}")
except Exception as e:
    print(f"Error: {e}")
