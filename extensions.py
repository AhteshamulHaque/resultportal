from flaskext.mysql import MySQL
from flask import session, redirect, url_for, request
from functools import wraps

mysql = MySQL()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in', None) is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function