import random
import string
import json
import os
import base64


class FileSessionFabric(object):
    def __init__(self, seed=None, size=10, folder='sessions'):
        random.seed('random' or seed)
        self.size = size
        self.folder = folder

    def random_string(self):
        return ''.join(random.choice(string.ascii_letters) for _ in range(self.size))

    def get_session(self, key):
        return FileSession(key, folder=self.folder)

    def new_session(self):
        return FileSession(self.random_string(), folder=self.folder)


class FileSession(object):
    def __init__(self, key, folder):
        self.folder = folder
        self.key = key
        self.sess_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.folder) + '/' + self.key

    def set(self, data):
        data_str = json.dumps(data)
        try:
            with open(self.sess_path, 'w') as f:
                f.write(data_str)
        except Exception as e:
            print(e)
            return False
        return True

    def get(self):
        try:
            with open(self.sess_path,'r') as f:
                data_str = f.read()
                data = json.loads(data_str)
                return data
        except Exception:
            # return None
            return {}

    def delete(self):
        try:
            with open(self.sess_path,'w') as f:
                f.write('')

        except Exception as e:
            pass

    def get_raw_data(self):
        try:
            with open(self.sess_path,'rb') as f:
                data = f.read()
                return base64.b64encode(data)
        except Exception as e:
            return base64.b64encode(e)

session = FileSessionFabric()

