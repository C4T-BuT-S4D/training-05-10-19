import socket
import sys
import time

ip = sys.argv[1]

s = socket.socket()
s.connect((ip, 5001))

s.send(b"DEBUG_GETSTORAGE\n")

time.sleep(1)
print(s.recv(100000))