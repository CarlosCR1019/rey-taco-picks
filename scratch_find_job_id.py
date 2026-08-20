import urllib.request
import json

# Check job logs
job_id = 95345781234 # let's find the job ID
url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/32308640275/jobs"
req = urllib.request.Request(url, headers={"User-Agent": "AntigravityBot"})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        for j in data.get('jobs', []):
            print(f"Job ID: {j.get('id')} - {j.get('name')}")
except Exception as e:
    print(f"Error: {e}")
