#!/usr/bin/env python3

from red_lib import *
import sys
import requests

def put(host, flag_id, flag, vuln):
    mch = CheckMachine(host, PORT)

    login_data = mch.register_in_service()
    login, password = login_data['login'], login_data['password']
    session = mch.login_in_service(login, password)
    invite = "invite"
    if vuln == "1":
        links = mch.create_threads_and_get_links(session)
        invite = mch.put_flags_and_get_inv_links(session, links, flag)
    else:
        invite = mch.file_upload(session, flag)

    cquit(Status.OK, f'{login}:{password}:{invite}')


def get(host, flag_id, flag, vuln):
    mch = CheckMachine(host, PORT)
    login, password, invite = flag_id.split(':')

    session = mch.login_in_service(login, password)
    if vuln == "1":
        link = mch.find_threads_by_invite(session, invite)
        flags = mch.find_by_thread_link(session, link)
        assert_in(flag, flags, "Can't find flag by invite link", Status.CORRUPT)
        session = mch.login_in_service(login, password)
        flags = mch.find_flags_by_login_and_pass(session)
        assert_in(flag, flags, "Can't find flag by invite link", Status.CORRUPT)
    else:
        file_content = mch.file_download(session, invite)
        assert_in(flag, file_content, "Can't download file with flag", Status.CORRUPT)

    cquit(Status.OK)

def check(host):
    mch = CheckMachine(host, PORT)

    login_data = mch.register_in_service()
    login, password = login_data['login'], login_data['password']
    session = mch.login_in_service(login, password)
    links = mch.create_threads_and_get_links(session)
    text1 = rnd_string(15)
    invite = mch.put_flags_and_get_inv_links(session, links, text1)
    text2 = rnd_string(15)
    file_name = mch.file_upload(session, text2)
    file_content = mch.file_download(session, file_name)
    assert_in(text2, file_content, "Can't download file")

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