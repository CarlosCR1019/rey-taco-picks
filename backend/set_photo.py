import urllib.request
import uuid
import os

TOKEN = '8684914807:AAHjNX6cz_sn1EUZVl0wt4v5iYWzJ8JU5UE'
CHAT_ID = '-1003845930328' # Canal @ReyTacoPicks
PHOTO_PATH = r'C:\Users\carlo\.gemini\antigravity\scratch\rey-taco-picks\frontend\public\favicon.png'

boundary = uuid.uuid4().hex
headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

body = []
body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{CHAT_ID}\r\n'.encode('utf-8'))
with open(PHOTO_PATH, 'rb') as f:
    photo_data = f.read()
body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="photo.png"\r\nContent-Type: image/png\r\n\r\n'.encode('utf-8'))
body.append(photo_data)
body.append(f'\r\n--{boundary}--\r\n'.encode('utf-8'))

payload = b''.join(body)
url = f'https://api.telegram.org/bot{TOKEN}/setChatPhoto'

req = urllib.request.Request(url, data=payload, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        print('RESULTADO:', resp.read().decode())
except Exception as e:
    print('ERROR:', e)
    if hasattr(e, 'read'):
        print(e.read().decode())
