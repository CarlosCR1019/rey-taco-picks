import urllib.request
import json

runs_to_check = [31976079739, 31998200166]

for run_id in runs_to_check:
    print(f"\n==================================================")
    print(f"Inspeccionando Run ID: {run_id}")
    print(f"==================================================")
    url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
    req = urllib.request.Request(url, headers={'User-Agent': 'Python-Script'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            for job in data.get('jobs', []):
                print(f"Job Name: {job['name']} | Status: {job['status']} | Conclusion: {job['conclusion']}")
                for step in job.get('steps', []):
                    print(f"   Step: {step['name']} | Status: {step['status']} | Conclusion: {step['conclusion']}")
    except Exception as e:
        print(f"Error fetching jobs: {e}")
