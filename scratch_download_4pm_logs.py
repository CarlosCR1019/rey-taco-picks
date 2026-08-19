import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Get job ID
run_id = 32192492639
url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/{run_id}/jobs"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode())
    job = data.get('jobs', [])[0]
    job_id = job.get('id')
    print(f"Job ID: {job_id}")

log_url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/jobs/{job_id}/logs"
req_log = urllib.request.Request(log_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req_log, timeout=10) as resp:
        log_content = resp.read().decode('utf-8', errors='ignore')
        print("=== LOG OUTPUT DE RUN 32192492639 (4:23 PM) ===")
        # Print lines around Run Scraper
        lines = log_content.split('\n')
        for l in lines[-100:]:
            print(l)
except Exception as e:
    print(f"Error descargando log: {e}")
