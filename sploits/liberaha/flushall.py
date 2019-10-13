import socket
import sys
import time

ip = sys.argv[1]

s = socket.socket()
s.connect((ip, 5001))

s.send(b"FLUSHALL REMEMBER_TO_CHANGE_THIS_LATER\n")