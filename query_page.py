import urllib.request
import urllib.parse
import json

user_token = "EAGMJ4QmnNEIBScbdEja4jkcQFhMXOuOrgddXCrObq85ualIExqEuyiGXXlL3JqsCs2LAn2r9ZAPl2OJwBFDqMqAxtJRw7PDgfJbXyl9dPsCnpkTbZCauhGR3clAPKVV1eXR4KlVivT6ZBTLAfmxexOlJZCw8FfT6SRZCp7HLmJeimZAxjycCwS2or6f28u9VySZBvxdyzisBg7rcwhnQSDMtkxltUuZCiZBrAqh2qUGHlC4HaPghgwp3Rve5Tyw9FAfrD92RNVMDoYZCeHqiNWvOgorVqfBwSWBusOtgZDZD"
page_id = "1311611272037375"

url = f"https://graph.facebook.com/v19.0/{page_id}?fields=id,name,access_token,instagram_business_account&access_token={urllib.parse.quote(user_token)}"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        print("Page Details:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
