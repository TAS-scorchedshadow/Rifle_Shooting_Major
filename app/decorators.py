from functools import wraps
from flask import g, request, redirect, url_for, flash
from flask_login import current_user, LoginManager

from app.models import Club


def role_required(role):
    """
    Redirects unauthorised traffic to a route. Should be applied after the club_exists decorator.
    The club is taken from the wrapped function

    :param roles: List of roles that includes any combination of ["STUDENT", "COACH", "ADMIN"]
    :return: None
    """
    def original_function(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Redundency for login_required
            if not current_user.is_authenticated:
                LoginManager.unauthorized()
            levels = ["STUDENT", "COACH", "ADMIN", "DEV"]

            access_required = levels.index(role)

            club = Club.query.filter_by(name=kwargs['club']).first()
            access_given = False
            if access_required <= current_user.access and club.id == current_user.clubID:
                access_given = True

            if current_user.access is levels.index("DEV"):
                access_given = True

            if not access_given:
                flash("You don't have permission to access that page", "error")
                if request.referrer is not None:
                    return redirect(request.referrer)
                else:
                    return redirect(url_for("welcome_bp.index"))
            return f(*args, **kwargs)

        return decorated_function

    return original_function

def club_exists(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        club = Club.query.filter_by(name=kwargs['club']).first()
        if club is None:
            flash("No club with that name exists", "error")
            if request.referrer is not None:
                return redirect(request.referrer)
            else:
                return redirect(url_for("welcome_bp.index"))
        return f(*args, **kwargs)

    return decorated_function

    return club_exists
