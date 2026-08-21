import urllib.request
import urllib.parse
import json

page_id = "1311611272037375"
page_token = "EAGMJ4QmnNEIBSWAiGqNKTYT3vuhTX4add90vX8zZARYJZBhpGKP1z4zDraTDySa6eIZBeNIEGA3Fa0kOiUEsa2IZCtQxa5dXVSwuFGcu1DWM59DoHZAc8BzFeSUY4KDZCd8NwJZCn76JE84ztS1pYGZARcLci4hyA7myzXZCrkGx9KG5fq809uJleG8Hpil7uuqBayusu9o6cTeLf92nihYFG6jCeZB0AUuPg9rLMhfzLmvC1XEE9tf8ouD6Xc"

url = f"https://graph.facebook.com/v19.0/{page_id}?fields=id,name,instagram_business_account,connected_instagram_account&access_token={urllib.parse.quote(page_token)}"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        print("Connected Instagram Account Info:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
