import requests
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check latest runs of CarlosCR1019/rey-taco-picks
url = "https://api.github.com/repos/CarlosCR1019/rey-taco-picks/actions/runs?per_page=5"
r = requests.get(url)
data = r.json()

for run in data.get("workflow_runs", []):
    print(f"Run ID: {run['id']} | Status: {run['status']} | Conclusion: {run['conclusion']} | Name: {run['name']} | Event: {run['event']}")
    print(f" -> URL: {run['html_url']}")
