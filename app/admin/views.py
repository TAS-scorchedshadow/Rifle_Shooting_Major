import datetime
import json

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, abort
from flask_login import login_required, current_user

from app import db
from app.decorators import club_authorised_urlpath, club_exists, is_authorised
from app.models import User, Club

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/user_list', methods=['GET'])
@login_required
def user_list_catch():
    return redirect(url_for(".user_list", club_name=current_user.club.name))


@admin_bp.route('/user_list/<club_name>', methods=['GET', 'POST'])
@login_required
@club_authorised_urlpath("ADMIN")
def user_list(club, club_name):
    """
    List of all current users on the system.

    :return: user_list.html
    """
    users = User.query.filter_by(clubID=club.id).order_by(User.access, User.sName).all()
    for user in users:
        user.schoolYr = user.get_school_year()
    times = {"start": club.season_start.strftime("%d:%m:%Y"), "end": club.season_end.strftime("%d:%m:%Y")}
    return render_template('admin/user_list.html', users=users, mail_setting=club.email_setting, season_time=times,
                           club=club)


@admin_bp.route('/make_admin', methods=['POST'])
@login_required
def make_admin():
    """
     AJAX route for changing the account level of specific users.
     Route is accessible by admins through the buttons on the user_list page

    """
    data = json.loads(request.get_data())
    userID = int(data["userID"])
    clubID = int(data["clubID"])
    club = Club.query.filter_by(id=clubID).first()
    user = User.query.filter_by(id=userID).first()
    if not club or not user:
        abort(400)

    if not is_authorised(club, "ADMIN"):
        abort(403)

    state = 0
    if user.access == 0:
        user.access = 1
        state = 1
    else:
        user.access = 0
    db.session.commit()
    return jsonify({'access_lvl': state})


@admin_bp.route('/email_settings', methods=['POST'])
@login_required
def email_settings():
    """
    AJAX route used to update the email_setting in the database

    """
    data = json.loads(request.get_data())
    clubID = int(data["clubID"])
    email_setting = int(data["email_setting"])
    club = Club.query.filter_by(id=clubID).first()
    if not club:
        abort(400)

    if not is_authorised(club, "ADMIN"):
        abort(403)

    club.email_setting = email_setting

    db.session.commit()

    return jsonify("complete")


@admin_bp.route('/update_season_date', methods=['POST'])
@login_required
def update_season_date():
    """
    AJAX route used to update the start & end times of a season in the database

    """
    data = json.loads(request.get_data())

    date_range = data["date_range"]
    dates = date_range.split(' - ')

    clubID = int(data["clubID"])
    club = Club.query.filter_by(id=clubID).first()

    if not club:
        abort(400)

    if not is_authorised(club, "ADMIN"):
        abort(403)

    club.season_start = datetime.datetime.strptime(dates[0], '%B %d, %Y')
    club.season_end = datetime.datetime.strptime(dates[1], '%B %d, %Y')
    db.session.commit()

    return jsonify("complete")



@admin_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """
    AJAX route for deleting user accounts. Route is accessible by admins through the buttons on the user_list page

    """
    data = request.get_data()
    userID = json.loads(data['userID'])

    clubID = int(data["clubID"])
    club = Club.query.filter_by(id=clubID).first()

    user = User.query.filter_by(id=userID).first()
    if not club or not user:
        abort(400)

    if not is_authorised(club, "ADMIN"):
        abort(403)

    user = User.query.filter_by(id=userID).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify('success')
