#!/usr/bin/env python3

import os
import sys
from auxiliary import *
import check_action
import put_action
import get_action
from selenium import webdriver
import atexit
import signal
import random

VULNS = "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ua_path = os.path.join(BASE_DIR, 'user_agents.txt')

with open(ua_path, 'r') as f:
    user_agent = random.choice(f.readlines())

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

while True:
    # noinspection PyBroadException
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)
    except:
        continue
    else:
        break

signal.signal(signal.SIGINT, quit_driver_wrapper(driver))
signal.signal(signal.SIGTERM, quit_driver_wrapper(driver))

if __name__ == '__main__':
    try:
        action = sys.argv[1]
        if action == 'info':
            quit(driver, Status.OK, f"vulns: {VULNS}")
        elif action == 'check':
            check_action.run(driver, sys.argv[2])
        elif action == 'put':
            put_action.run(driver, *sys.argv[2:5])
        elif action == 'get':
            get_action.run(driver, *sys.argv[2:5])
        else:
            quit(driver, Status.ERROR)
    except SystemExit:
        raise
    except BaseException as e:
        print('WTF?', e, type(e), repr(e))
        quit(driver, Status.ERROR)
