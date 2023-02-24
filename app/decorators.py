from functools import wraps

from flask import request, redirect, url_for, flash, abort
from flask_login import current_user, LoginManager

from app.models import Club


def is_authorised(club: object, role: str) -> bool:
    """
    Checks if the current_user has the access corresponding to the role. The current user must be a part of
    the supplied club (excluding the dev role).

    :param club: Club to check authorisation for
    :param role: One of ["STUDENT", "COACH", "ADMIN", "DEV"]
    :return: Boolean
    """
    dev_access = 4

    authorised = is_role_authorised(role) and club.id == current_user.clubID

    if current_user.access == dev_access:
        authorised = True
    return authorised


def is_role_authorised(role: str) -> bool:
    """
    Checks if the current_user has the access corresponding to the role.

    :param role: One of ["STUDENT", "COACH", "ADMIN", "DEV"]
    :return: Boolean
    """
    levels = ["STUDENT", "COACH", "ADMIN", "DEV"]

    access_required = levels.index(role)
    authorised = False
    if access_required <= current_user.access:
        authorised = True
    return authorised


def club_authorised_urlpath(role):
    def original_function(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access = False
            error_msg = ""
            if 'club_name' in kwargs:
                club = Club.query.filter_by(name=kwargs['club_name']).first()
                if club:
                    if is_authorised(club, role) is True:
                        access = True
                    else:
                        error_msg = "Invalid Permissions"
                else:
                    error_msg = "No clubs with that name were found"
            else:
                error_msg = "No club name was given"
            if access is False:
                flash(error_msg, "error")
                abort(403)
                return
            return f(club, *args, **kwargs)

        return decorated_function

    return original_function


def club_exists(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        club = Club.query.filter_by(name=kwargs['club']).first()
        if club is None:
            flash("No club with that name exists", "error")
            abort(403)
            return
        return f(*args, **kwargs)

    return decorated_function

    return club_exists


def authorise_role(role):
    """
    Decorator authorising the current user by only the role
    """
    def original_function(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if is_role_authorised(role):
                return f(*args, **kwargs)
            else:
                abort(403)
                return
        return decorated_function
    return original_function




