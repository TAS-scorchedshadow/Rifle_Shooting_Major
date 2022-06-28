from functools import wraps
from flask import g, request, redirect, url_for, flash
from flask_login import current_user

def authRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to view this page", 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function