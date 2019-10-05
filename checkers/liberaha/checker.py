#!/usr/bin/env python3

from pas_lib import *
import sys

def put(host, flag_id, flag, vuln):
    mch = CheckMachine(host, PORT)
    conn = mch.get_conn()

    if vuln == "1":
        key = mch.put_simple_string(conn, flag)
        cquit(Status.OK, key)
    else:
        st, key = mch.put_hset_string(conn, flag)
        cquit(Status.OK, f'{st}:{key}')


def get(host, flag_id, flag, vuln):
    mch = CheckMachine(host, PORT)
    conn = mch.get_conn()

    if vuln == "1":
        key = flag_id
        ok = mch.check_simple_string(conn, key, flag)
        if not ok:
            cquit(Status.CORRUPT, "Can't get flag in get")
    else:
        st, key = flag_id.split(':')
        ok1, ok2 = mch.check_hset_string(conn, st, key, flag)
        if not ok1:
            cquit(Status.CORRUPT, "Can't get flag in hget")

        if not ok2:
            cquit(Status.CORRUPT, "Can't get flag in hgetall")

    cquit(Status.OK)

def check(host):
    mch = CheckMachine(host, PORT)

    conn = mch.get_conn()
    s1 = rnd_string(10)
    k1 = mch.put_simple_string(conn, s1)
    ok1 = mch.check_simple_string(conn, k1, s1)
    if not ok1:
        cquit(Status.MUMBLE, "Can't get value in get")

    s2 = rnd_string(10)
    st, k2 = mch.put_hset_string(conn, s2)
    ok2, ok3 = mch.check_hset_string(conn, st, k2, s2)
    if not ok2:
        cquit(Status.MUMBLE, "Can't get value in hget")

    if not ok3:
        cquit(Status.MUMBLE, "Can't get value in hgetall")

    cquit(Status.OK)

if __name__ == '__main__':
    action, *args = sys.argv[1:]

    try:
        if action == "check":
            host, = args
            check(host)
        elif action == "put":
            host, flag_id, flag, vuln = args
            put(host, flag_id, flag, vuln)
        elif action == "get":
            host, flag_id, flag, vuln = args
            get(host, flag_id, flag, vuln)
        else:
            quit(Status.ERROR, 'System error', 'Unknown action: ' + action)
        
        cquit(Status.ERROR)
    except ConnectionRefusedError:
        cquit(Status.DOWN, 'Connection error')
    except socket.timeout:
        cquit(Status.DOWN, 'Connection error')
    except SystemError as e:
        raise
    except Exception as e:
        cquit(Status.ERROR, 'System error', str(e))