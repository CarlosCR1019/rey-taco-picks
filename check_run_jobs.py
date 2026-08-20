import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

run_id = 32424960766
url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
r = requests.get(url)
jobs = r.json().get("jobs", [])

for j in jobs:
    print(f"Job: {j['name']} | Status: {j['status']} | Conclusion: {j['conclusion']}")
    for s in j.get("steps", []):
        print(f"  Step: {s['name']} -> {s['status']} ({s['conclusion']})")
