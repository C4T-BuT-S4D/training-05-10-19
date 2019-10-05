#!/usr/bin/env python3

from bot_lib import *
import sys
import requests
import json

def put(host, flag_id, flag, vuln):
    mch = CheckMachine(host, PORT)

    data = {}
    data.update(mch.register_in_service("ghost"))
    s = mch.login_in_service(data)
    mch.put_string(s, flag)
    data.update(mch.find_all_links(s))
    mch.create_text_by_url(s)

    cquit(Status.OK, json.dumps(data))


def get(host, flag_id, flag, vuln):
    mch = CheckMachine(host, PORT)
    data = json.loads(flag_id)

    user_data = mch.register_in_service()
    s = mch.login_in_service(user_data)
    finded = mch.find_all_strings_by_links(s, data['links'])
    assert_in(flag, finded, "Can't find flag by /find")

    cquit(Status.OK)

def check(host):
    mch = CheckMachine(host, PORT)

    data = {}
    st = rnd_string(10)
    data.update(mch.register_in_service("ghost"))
    s = mch.login_in_service(data)
    mch.put_string(s, st)
    data.update(mch.find_all_links(s))
    mch.create_text_by_url(s)

    user_data = mch.register_in_service()
    s = mch.login_in_service(user_data)
    finded = mch.find_all_strings_by_links(s, data['links'])
    assert_in(st, finded, "Can't find flag by /find")

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
    except requests.exceptions.ConnectionError:
        cquit(Status.DOWN, 'Connection error')
    except SystemError as e:
        raise
    except Exception as e:
        cquit(Status.ERROR, 'System error', str(e))