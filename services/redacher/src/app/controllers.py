from app import app
import json
import os


def add_thread_to_user(user_login, thread_id):
    path = os.path.join(os.path.dirname(__file__), app.config['PERM_FILE'])
    try:
        with open(path, 'r') as f:
            data = f.read()
            if data:
                data = json.loads(data)
            else:
                data = {}
    except FileNotFoundError:
        with open(path, 'w') as f:
            f.write('')
        data = {}
    app.logger.info('user %s was added to thread %s' % (user_login, thread_id))
    user_perms = data.get(user_login, [])
    user_perms = set(user_perms)
    user_perms.add(thread_id)
    user_perms = list(user_perms)
    data.update({user_login: user_perms})
    with open(path, 'w') as f:
        f.write(json.dumps(data))
    return True


def get_user_threads(user_login):
    path = os.path.join(os.path.dirname(__file__), app.config['PERM_FILE'])
    try:
        with open(path, 'r') as f:
            data = f.read()
            return eval(data)[user_login]
    except Exception:
        return None
