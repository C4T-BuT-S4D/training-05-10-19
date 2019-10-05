from bs4 import BeautifulSoup
from checklib import *
import secrets
import requests
import json
import base64

PORT = 5002
web_links = {
    'https://yandex.ru': "Яндекс",
    "https://shadowservants.ru": "Ддосишь",
}

class CheckMachine:

    @property
    def url(self):
        return f'http://{self.host}:{self.port}'


    def __init__(self, host, port):
        self.host = host
        self.port = port


    def register_in_service(self, who='MC'):
        register_url = self.url + '/register'
        login = secrets.choice(('Sunlover', 'Pomo', 'Johnny', 'alagunto', 'Kekov'))
        login = login + '_' + rnd_username()
        password = rnd_password()
        type = '2'
        if who != 'MC':
            type = '1'
        data = dict(
            type=type,
            login=login,
            password=password
        )
        r = requests.post(url=register_url, data=data, allow_redirects=False)
        assert_eq(r.status_code, 303, "Can't register in service")
        return data


    def login_in_service(self, data):
        login_url = self.url + '/login'
        s = requests.Session()
        r = s.get(url=login_url, allow_redirects=True)
        assert_eq(r.status_code, 200, "Can't login in service")
        r = s.post(url=login_url, data=data, allow_redirects=True)
        assert_eq(r.status_code, 200, "Can't login in service")
        return s


    def put_string(self, session, s):
        name = rnd_string(10)
        create_url = self.url + '/create'
        r = session.post(url=create_url, data=dict(name=name, text=s))
        assert_eq(r.status_code, 200, "Can't create text")


    def get_searchable_link(self, s, link):
        resp = s.get(self.url + link)
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        last_link = links.pop()
        return last_link.get("href", "/not_found_lol")


    def find_all_links(self, session):
        list_url = self.url + '/list'
        r = session.get(url=list_url)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        result_links = []
        for link in links:
            link = link.get("href", "/not_found_lol")
            if "text" in link:
                result_links.append(link)
        result_links = [self.get_searchable_link(session, x) for x in result_links]
        return dict(links=result_links)


    def find_all_strings_by_links(self, session, links):
        s = []
        for link in links:
            find_url = self.url + link
            r = session.get(find_url)
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            areas = soup.find_all('textarea')
            if areas:
                s += [x.string for x in areas]
        return s


    def create_text_by_url(self, session):
        create_url = self.url + '/create_url'
        name = rnd_string(10)

        text_url_pair = secrets.choice(list(web_links.items()))

        text_url = text_url_pair[0]

        r = session.post(url=create_url, data=dict(name=name, url=text_url))
        assert_eq(r.status_code, 200, "Can't create text by link")

        list_url = self.url + '/list'
        r = session.get(url=list_url)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        last = links.pop().get("href", "/bad_href")

        r = session.get(url=self.url + last)
        assert_in(text_url_pair[1], r.text, "Can't create text by link")


    def check_print_session_works(self, username, s):
        print_url = self.url + '/print'
        r = s.get(print_url)
        assert_eq(r.status_code, 200, "Can't print banned user data")
        try:
            data = json.loads(base64.b64decode(r.text))
            assert_in(username, data.values(), "Can't print banned user data")
        except Exception:
            cquit(Status.MUMBLE, "Can't print banned user data")