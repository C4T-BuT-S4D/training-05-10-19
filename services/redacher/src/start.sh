#!/bin/sh

cd /app/src

gunicorn --worker-class gevent --worker-connections 768 --bind 0.0.0.0:5000 app:app