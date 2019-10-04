from flask import session, redirect
from functools import wraps


def loggedin():
    return 'login' in session


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if loggedin():
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return inner