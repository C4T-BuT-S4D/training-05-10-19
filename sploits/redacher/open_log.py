import requests
import sys

ip = sys.argv[1]

r = requests.get(f"http://{ip}:5000/static/log.log")

print(r.text)