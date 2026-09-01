import json
import urllib.request

url = 'http://127.0.0.1:5000/api/auth/register'
data = json.dumps({'email': 'testregistro@example.com', 'password': '123456'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode())
except Exception as e:
    print(type(e).__name__, e)
    if hasattr(e, 'read'):
        print(e.read().decode())
