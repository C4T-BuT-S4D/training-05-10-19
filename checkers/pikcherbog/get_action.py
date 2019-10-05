import random
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from auxiliary import *


def run(driver, ip, flag_id, flag):
    username, password, post_id = flag_id.split(':')

    try:
        login_account(ip, driver, username, password)
    except NoSuchElementException:
        quit(driver, Status.MUMBLE, "Login failed")

    url = URL.format(ip, '/my')
    driver.get(url)
    check_page(driver)

    if f'href="/post/{post_id}"' not in driver.page_source:
        quit(driver, Status.CORRUPT, "Post not found")

    url = URL.format(ip, f'/post/{post_id}')
    driver.get(url)
    check_page(driver)

    if flag not in driver.page_source:
        quit(driver, Status.CORRUPT, "Flag not found")

    if random.randint(0, 1):
        url = URL.format(ip, '/logout')
        driver.get(url)
        check_page(driver)
        if username in driver.page_source:
            quit(driver, Status.MUMBLE, "Logout failed")

    quit(driver, Status.OK)
