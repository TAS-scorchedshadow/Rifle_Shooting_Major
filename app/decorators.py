from functools import wraps
from flask import g, request, redirect, url_for, flash
from flask_login import current_user, LoginManager


def roles_required(roles):
    def original_function(f):
        def decorated_function(*args, **kwargs):
            # Redundency for login_required
            if not current_user.is_authenticated:
                LoginManager.unauthorized()
            levels = ["STUDENT", "COACH", "ADMIN"]

            if not all(i in levels for i in roles):
                raise ValueError("Unknown Role")
            if current_user.access > len(levels) - 1:
                current_user.access = len(levels) - 1
            role = levels[current_user.access]
            if not (role in roles):
                flash("You don't have permission to access that page", "error")
                if request.referrer is not None:
                    return redirect(request.referrer)
                else:
                    return redirect(url_for("welcome_bp.index"))
            return f(*args, **kwargs)

        return decorated_function

    return original_function
