import random
from selenium.common.exceptions import NoSuchElementException
from auxiliary import *


def check_pages(ip, driver):
    pages_to_check = [
        '/login',
        '/register',
        '/random',
        '/last',
        '/',
    ]

    random.shuffle(pages_to_check)

    for page in pages_to_check:
        url = URL.format(ip, page)
        driver.get(url)
        check_page(driver)

        if driver.current_url != url:
            quit(driver, Status.MUMBLE, f"Strange redirect on {get_path(url)}")


def check_drafted(ip, driver, post_id, post_title):
    url = URL.format(ip, '/my')
    driver.get(url)
    check_page(driver)

    if post_title not in driver.page_source:
        quit(driver, Status.MUMBLE, "Post my check failed")

    if f'href="/post/{post_id}"' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Post my check failed")


def check_random(ip, driver, post_id, post_title):
    url = URL.format(ip, f'/random?p.id={post_id}&title="{post_title}"')
    driver.get(url)
    check_page(driver)

    if post_title not in driver.page_source:
        quit(driver, Status.MUMBLE, "Post random check failed")

    if f'href="/post/{post_id}"' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Post random check failed")


def check_published(ip, driver, post_id, post_title):
    url = URL.format(ip, f'/random?p.id={post_id}')
    driver.get(url)
    check_page(driver)

    if post_title not in driver.page_source:
        quit(driver, Status.MUMBLE, "Post published check failed")

    if f'href="/post/{post_id}"' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Post published check failed")    


def check_profile(ip, driver, username, post_id, post_title):
    url = URL.format(ip, "/")
    driver.get(url)
    check_page(driver)

    driver.find_element_by_link_text(username).click()
    check_page(driver)

    if post_title not in driver.page_source:
        quit(driver, Status.MUMBLE, "Profile check failed")

    if f'href="/post/{post_id}"' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Profile check failed")    

    if f"User {username}" not in driver.page_source:
        quit(driver, Status.MUMBLE, "Profile check failed")


def check_edit(ip, driver, post_id, title, change_publish):
    url = URL.format(ip, f'/post/{post_id}/edit')
    driver.get(url)
    check_page(driver)

    if title not in driver.page_source:
        quit(driver, Status.MUMBLE, "Edit check failed")    

    driver.find_element_by_name("title").send_keys(' edited title')
    driver.find_element_by_name("body").send_keys(' edited body')
    if change_publish:
        driver.find_element_by_name("publish").click()

    driver.find_element_by_xpath('//button[@type="submit"]').click()
    check_page(driver)

    if title not in driver.page_source:
        quit(driver, Status.MUMBLE, "Edit check failed")

    if 'edited title' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Edit check failed")

    if 'edited body' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Edit check failed")


def run(driver, ip):
    check_pages(ip, driver)
    username, _ = check_login_register(ip, driver)
    try:
        pub_id, pub_title = create_post(ip, driver, True)
    except NoSuchElementException as e:
        quit(driver, Status.MUMBLE, f"Could not create post")

    check_random(ip, driver, pub_id, pub_title)
    check_published(ip, driver, pub_id, pub_title)

    try:
        draft_id, draft_title = create_post(ip, driver, False)
    except NoSuchElementException as e:
        quit(driver, Status.MUMBLE, f"Could not create post")

    check_drafted(ip, driver, draft_id, draft_title)
    check_profile(ip, driver, username, draft_id, draft_title)

    try:
        check_edit(ip, driver, draft_id, draft_title, True)
    except NoSuchElementException as e:
        quit(driver, Status.MUMBLE, f"Could not edit post")

    check_published(ip, driver, draft_id, draft_title)

    quit(driver, Status.OK)
