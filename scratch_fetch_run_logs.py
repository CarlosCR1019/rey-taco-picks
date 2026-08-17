import urllib.request
import json

# Get job ID for run 31976079739
url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs/31976079739/jobs"
req = urllib.request.Request(url, headers={'User-Agent': 'Python-Script'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        job_id = data['jobs'][0]['id']
        print(f"Job ID: {job_id}")
        
        log_url = f"https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/jobs/{job_id}/logs"
        log_req = urllib.request.Request(log_url, headers={'User-Agent': 'Python-Script'})
        with urllib.request.urlopen(log_req) as log_resp:
            log_text = log_resp.read().decode('utf-8', errors='ignore')
            with open("run_31976079739.log", "w", encoding="utf-8") as f:
                f.write(log_text)
            print(f"Log saved! Lines: {len(log_text.splitlines())}")
            print("\n--- LAST 50 LINES OF LOG ---")
            for line in log_text.splitlines()[-50:]:
                print(line)
except Exception as e:
    print(f"Error: {e}")
