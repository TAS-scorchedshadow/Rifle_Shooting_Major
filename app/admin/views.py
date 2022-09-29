import datetime
import json

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, abort
from flask_login import login_required, current_user

from app import db
from app.decorators import club_authorised_urlpath, is_authorised
from app.models import User

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
     AJAX route for toggling a user between a student and a coach (access levels 0-1 respectively)
     Route is accessible by admins through the buttons on the user_list page

    """
    data = json.loads(request.get_data())
    userID = int(data["userID"])
    club = current_user.club
    user = User.query.filter_by(id=userID).first()
    if not club or not user:
        abort(400)

    if user.clubID != current_user.clubID:
        abort(403)

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
    AJAX route used to update the email_setting in the database. Expects email_setting to be "int"

    """
    data = json.loads(request.get_data())
    email_setting = int(data["email_setting"])
    club = current_user.club
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
    AJAX route used to update the start & end times of a season in the database. Takes in data in the
    format "{%B %d, %Y} - {%B %d, %Y}"

    Will ensure that start date < end date

    """
    data = json.loads(request.get_data())

    date_range = data["date_range"]
    dates = date_range.split(' - ')

    club = current_user.club

    if not club:
        abort(400)

    if not is_authorised(club, "ADMIN"):
        abort(403)

    start = datetime.datetime.strptime(dates[0], '%B %d, %Y')
    end = datetime.datetime.strptime(dates[1], '%B %d, %Y')

    if start > end:
        abort(400, "Start date must be less than end date")

    club.season_start = start
    club.season_end = end

    db.session.commit()

    return jsonify("complete")



@admin_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """
    AJAX route for deleting user accounts. Route is accessible by admins through the buttons on the user_list page

    """
    data = request.get_data()
    userID = json.loads(data)['userID']

    club = current_user.club

    user = User.query.filter_by(id=userID).first()
    if not club or not user:
        abort(400)

    if current_user.clubID != user.clubID:
        abort(403)

    if not is_authorised(club, "ADMIN"):
        abort(403)

    user = User.query.filter_by(id=userID).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify('success')
