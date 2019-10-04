from checklib import *
import json
import socket
import time

PORT = 5001

class CheckMachine:

    def __init__(self, host, port):
        self.host = host
        self.port = port


    def get_conn(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(5)
        try:
            conn.connect((self.host, self.port))
        except socket.timeout as e:
            raise ConnectionRefusedError("Connection timed out to " + self.host)
        return conn


    def put_simple_string(self, conn, s):
        key = rnd_string(10)
        conn.send(('SET %s %s \n' % (key, s)).encode('ascii'))
        time.sleep(0.2)
        data = conn.recv(1024)
        return key


    def check_simple_string(self, conn, key, s):
        conn.send(('GET %s \n' % key).encode('ascii'))
        time.sleep(0.2)
        data = conn.recv(1024)
        return s in data.decode('utf-8')


    def put_hset_string(self, conn, s):
        set_name = rnd_string(10)
        key = rnd_string(10)
        conn.send(('HCREATESET %s \n' % set_name).encode('ascii'))
        time.sleep(0.2)
        data = conn.recv(1024)
        conn.send(('HSET %s %s %s \n' % (set_name, key, s)).encode('ascii'))
        data = conn.recv(1024)
        assert_in('OK', data.decode('utf-8'), "Can't do HSET in new hashset")

        return set_name, key


    def check_hset_string(self, conn, set_name, key, s):
        conn.send(('HGET %s %s \n' % (set_name, key)).encode('ascii'))
        time.sleep(0.2)
        data = conn.recv(1024)
        b1 = s in data.decode('utf-8')
        conn.send(('HGETALL %s \n' % (set_name)).encode('ascii'))
        data = conn.recv(1024)
        b2 = s in data.decode('utf-8')
        return b1, b2
