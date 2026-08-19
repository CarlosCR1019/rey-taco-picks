import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

run_id = 32192492639
url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        for job in data.get('jobs', []):
            print(f"Job: {job.get('name')} | Status: {job.get('status')} | Conclusion: {job.get('conclusion')} | Started: {job.get('started_at')} | Completed: {job.get('completed_at')}")
            for step in job.get('steps', []):
                print(f"  - Step: {step.get('name')} | Conclusion: {step.get('conclusion')}")
except Exception as e:
    print(f"Error: {e}")
