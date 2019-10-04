from bs4 import BeautifulSoup
from checklib import *
import secrets
import requests

PORT = 5000

class CheckMachine:

    @property
    def url(self):
        return f'http://{self.host}:{self.port}'
    

    def __init__(self, host, port):
        self.host = host
        self.port = port


    def register_in_service(self):
        register_url = f'{self.url}/register'
        login = secrets.choice(('Sunlover', 'Pomo', 'Johnny', 'alagunto', 'Kekov'))
        login = login + '_' + rnd_username()
        password = rnd_password()
        data = {
            'login': login,
            'password': password
        }
        r = requests.post(url=register_url, data=data, allow_redirects=False)
        assert_eq(r.status_code, 302, "Can't register in service")
        return data


    def login_in_service(self, login, password):
        login_url = f'{self.url}/login'
        session = requests.Session()
        r = session.get(url=login_url, allow_redirects=True)
        assert_eq(r.status_code, 200, "Can't login in service")
        login_data = {
            'login': login,
            'password': password
        }
        r = session.post(url=login_url, data=login_data, allow_redirects=True)
        assert_eq(r.status_code, 200, "Can't login in service")
        return session


    def create_threads_and_get_links(self, session):
        thread_name = 'Thread_' + rnd_string(10)
        create_url = f'{self.url}/create'
        r = session.post(url=create_url, data={ 'name': thread_name })
        assert_eq(r.status_code, 200, "Can't create thread")
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        result_links = []
        for link in links:
            if 'threads' in link['href']:
                result_links.append(link['href'])
        return result_links


    def put_flags_and_get_inv_links(self, session, links, flag):
        for link in links:
            thread_url = self.url + link
            r = session.post(thread_url, data={ 'text': flag })
            assert_eq(r.status_code, 200, "Can't add message to thread")
            soup = BeautifulSoup(r.text, 'html.parser')
            invite = soup.find_all('a')[-1]['href']
            return invite
        cquit(Status.MUMBLE, "Can't get invite link")


    def find_by_thread_link(self, session, link):
        thread_url = self.url + link
        r = session.get(thread_url)
        assert_eq(r.status_code, 200, "Can't find thread page")
        soup = BeautifulSoup(r.text, 'html.parser')
        flags = soup.find_all('h4')[:-1]
        flags = [x.string for x in flags]
        flags = [x.split()[-1] for x in flags]
        return flags


    def find_flags_by_login_and_pass(self, session):
        list_url = f'{self.url}/list'
        r = session.get(list_url)
        assert_eq(r.status_code, 200, "Can't get list of threads")
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a')
        thread = links[-1]['href']
        return self.find_by_thread_link(session, thread)


    def find_threads_by_invite(self, session, invite):
        inv_url = self.url + invite
        r = session.get(inv_url)
        assert_eq(r.status_code, 200, "Can't get thread by invite link")
        r = session.get(f'{self.url}/list')
        soup = BeautifulSoup(r.text, 'html.parser')
        thread_link = soup.find_all('a')[-1]['href']
        return thread_link


    def file_upload(self, session, file_content):
        file_name = rnd_string(15)
        files = { 'file': (file_name, file_content) }
        upload_url = f'{self.url}/upload'
        r = session.post(upload_url, files=files, allow_redirects=False)
        assert_eq(r.status_code, 302, "Can't upload file")
        return file_name


    def file_download(self, session, file_name):
        r = session.get(f'{self.url}/uploads/{file_name}')
        assert_eq(r.status_code, 200, "Can't download file")
        return r.text
