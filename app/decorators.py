from flask import request, redirect, url_for, flash
from flask_login import current_user, LoginManager

from app.models import Club


def is_authorised(club: object, role: str) -> bool:
    levels = ["STUDENT", "COACH", "ADMIN", "DEV"]

    access_required = levels.index(role)
    authorised = False
    if access_required <= current_user.access and club.id == current_user.clubID:
        authorised = True

    if current_user.access is levels.index("DEV"):
        authorised = True
    return authorised


def club_authorised_urlpath(role):
    def original_function(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            club = Club.query.filter_by(name=kwargs['club_name']).first()
            access = False
            error_msg = ""
            if club:
                if is_authorised(club, role) is True:
                    access = True
                else:
                    error_msg = "Invalid Permissions"
            else:
                error_msg = "No clubs with that name were found"

            if access is False:
                flash(error_msg, "error")
                if request.referrer is not None:
                    return redirect(request.referrer)
                else:
                    return redirect(url_for("welcome_bp.index"))
            return f(club, *args, **kwargs)

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
