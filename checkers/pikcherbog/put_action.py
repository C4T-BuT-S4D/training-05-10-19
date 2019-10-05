import random
from selenium.common.exceptions import NoSuchElementException
from auxiliary import *


def run(driver, ip, flag_id, flag):
    username, password = check_login_register(ip, driver)
    try:
        post_id, post_title = create_post(
            ip, 
            driver, 
            publish=False, 
            title=None, 
            body=flag, 
            check=False,
        )
    except NoSuchElementException:
        quit(driver, Status.MUMBLE, f"Could not create post")

    quit(driver, Status.OK, f"{username}:{password}:{post_id}")
