import random
import secrets
import string
import lorem
import enum
import sys
import re
import time
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException


ALPH = string.ascii_letters + string.digits
URL = "http://{}:5003{}"


class Status(enum.Enum):
    OK      = 101
    CORRUPT = 102
    MUMBLE  = 103
    DOWN    = 104
    ERROR   = 110
    
    def __bool__(self):
        return self.value is Status.OK


def quit_driver(driver):   
    if driver:
        driver.quit()


def quit_driver_wrapper(driver):
    def _quit_driver_internal(sig, frame):
        if driver:
            driver.quit()

    return _quit_driver_internal


def quit(driver, code, *args, **kwargs):
    quit_driver(driver)
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)
    kwargs['file'] = sys.stdout
    print(*args, **kwargs)
    assert(type(code) == Status)
    sys.exit(code.value)


def check_page(driver):
    pass
    # if driver.title != 'Awesome Blog':
    #     quit(driver, Status.DOWN, f"Invalid page {get_path(driver.current_url)}")


def random_string(length=8, alph=ALPH):
    return ''.join(random.choices(alph, k=length))


def generate_username():
    return random_string()


def generate_title():
    return lorem.sentence()


def generate_body(ip):
    text = lorem.paragraph()
    words = text.split(' ')

    bold_ind = random.randint(0, len(words) - 1)
    bold_word = words[bold_ind]
    words[bold_ind] = f"**{words[bold_ind]}**"

    link = random.randint(0, len(words) - 1)
    while link == bold_ind:
        link = random.randint(0, len(words))
    link_path = f"http://{ip}:8000/{random_string(random.randint(1, 5))}_{random_string(random.randint(1, 5))}"
    link_word = words[link]
    words[link] = f"[{link_word}]({link_path})"

    code_ind = random.randint(0, len(words) - 1)
    while code_ind == link or code_ind == bold_ind:
        code_ind = random.randint(0, len(words))

    code_word = words[code_ind]
    words[code_ind] = f"`{words[code_ind]}`"

    text = ' '.join(words)

    return text, (bold_word, (link_word, link_path), code_word)


def generate_password():
    return secrets.token_hex(10)


def get_path(url):
    return urlparse(url).path


def create_account(ip, driver):
    username = generate_username()
    password = generate_password()

    url = URL.format(ip, '/register')
    driver.get(url)
    check_page(driver)
    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_xpath('//button[@type="submit"]').click()
    check_page(driver)

    if 'Welcome to Awesome Blog' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Bad redirect on register")
    
    return username, password


def login_account(ip, driver, username, password):
    url = URL.format(ip, '/login')
    
    driver.get(url)
    check_page(driver)
    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_xpath('//button[@type="submit"]').click()    
    check_page(driver)

    if 'Invalid credentials' in driver.page_source:
        quit(driver, Status.MUMBLE, "Could not login")

    if f'/user/{username}' not in driver.page_source:
        quit(driver, Status.MUMBLE, "Could not login")


def check_login_register(ip, driver):
    try:
        username, password = create_account(ip, driver)
        login_account(ip, driver, username, password)
    except NoSuchElementException as e:
        quit(driver, Status.MUMBLE, f"Register/Login check failed") 

    return username, password


def create_post(ip, driver, publish, title=None, body=None, check=True):
    if not title:
        title = generate_title()
    if not body:
        body, words = generate_body(ip)

    url = URL.format(ip, '/create_post')
    
    driver.get(url)
    check_page(driver)

    driver.find_element_by_name("title").send_keys(title)
    driver.find_element_by_name("body").send_keys(body)
    if publish:
        driver.find_element_by_name("publish").click()

    driver.find_element_by_xpath('//button[@type="submit"]').click()
    check_page(driver)

    res = re.findall("/post/(\d+)", driver.current_url)
    if not res:
        quit(driver, Status.MUMBLE, f"Could not create post")

    if check:
        if title not in driver.page_source:
            quit(driver, Status.MUMBLE, f"Post check failed")

        if f"<strong>{words[0]}</strong>"  not in driver.page_source:
            quit(driver, Status.MUMBLE, f"Markdown check failed")

        if f"<code>{words[2]}</code>" not in driver.page_source:
            quit(driver, Status.MUMBLE, f"Markdown check failed")

        if f'<a href="{words[1][1]}">{words[1][0]}</a>' not in driver.page_source:
            quit(driver, Status.MUMBLE, f"Markdown check failed")

    post_id = res[0]
    return post_id, title
