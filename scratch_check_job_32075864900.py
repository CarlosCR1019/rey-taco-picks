import urllib.request
import json

url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/32075864900/jobs"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        for j in data.get('jobs', []):
            print(f"Job: {j['name']} | Status: {j['status']} | Conclusion: {j['conclusion']}")
            for s in j.get('steps', []):
                print(f"  Step: {s['name']} | Status: {s['status']} | Conclusion: {s['conclusion']}")
except Exception as e:
    print(f"Error: {e}")
