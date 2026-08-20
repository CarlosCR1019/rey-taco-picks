import urllib.request
import json

# Let's inspect the jobs of Run 32391281817 (today 10:18 AM)
url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/32391281817/jobs"
req = urllib.request.Request(url, headers={"User-Agent": "AntigravityBot"})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        for j in data.get('jobs', []):
            print(f"Job: {j.get('name')}")
            for step in j.get('steps', []):
                print(f"  - Step: {step.get('name')} | Status: {step.get('status')} | Conclusion: {step.get('conclusion')}")
except Exception as e:
    print(f"Error: {e}")
