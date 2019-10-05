from bottle import request, redirect
from functools import wraps
import session


def get_data_from_session():
    sess = session.session.get_session(request.cookies.get('SESSION', ''))
    data = sess.get()
    return data


def logged_in(func):
    @wraps(func)
    def inner(db, *args, **kwargs):
        data = get_data_from_session()
        if 'id' in data.keys():
            return func(db, *args, **kwargs)
        else:
            return redirect('/login')

    return inner
