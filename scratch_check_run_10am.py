import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

run_id = "32159395774"
url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        jobs = data.get('jobs', [])
        for j in jobs:
            print(f"Job ID: {j.get('id')} | Name: {j.get('name')} | Status: {j.get('status')} | Conclusion: {j.get('conclusion')}")
            for step in j.get('steps', []):
                print(f"  - Step: {step.get('name')} | Status: {step.get('status')} | Conclusion: {step.get('conclusion')}")
except Exception as e:
    print(f"Error: {e}")
