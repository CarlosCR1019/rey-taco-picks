import urllib.request
import json

for run_id, desc in [(32335549010, "Ayer 11:00 PM CDMX (05:25 UTC)"), (32391281817, "Hoy 10:00 AM CDMX (16:18 UTC)")]:
    url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
    req = urllib.request.Request(url, headers={"User-Agent": "AntigravityBot"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"\n==================================================")
            print(f"RUN {run_id} ({desc}):")
            print(f"==================================================")
            for j in data.get('jobs', []):
                print(f"Job: {j.get('name')} | Status: {j.get('status')} | Conclusion: {j.get('conclusion')} | Started: {j.get('started_at')} | Completed: {j.get('completed_at')}")
                for s in j.get('steps', []):
                    print(f"   Step: {s.get('name')} | Status: {s.get('status')} | Conclusion: {s.get('conclusion')}")
    except Exception as e:
        print(f"Error: {e}")
