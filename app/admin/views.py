import datetime
import json

from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_required, current_user

from app import db
from app.decorators import roles_required, club_exists
from app.models import User, Club

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/<club>/user_list', methods=['GET', 'POST'])
@login_required
@club_exists()
@roles_required(["ADMIN"])
def user_list(club):
    """
    List of all current users on the system.

    :return: user_list.html
    """
    club = Club.query.filter_by(name=club).first()
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
        return {"Error": "Error"}

    if current_user.clubID != clubID or current_user.access < 2:
        return {"Error": "Error"}

    state = 0
    if user.access == 0:
        user.access = 1
        state = 1
    else:
        user.access = 0
    db.session.commit()
    return jsonify({'access_lvl': state})


@admin_bp.route('/email_settings', methods=['POST'])
def email_settings():
    """
    AJAX route used to update the email_setting in the database

    """
    data = json.loads(request.get_data())
    clubID = int(data["clubID"])
    email_setting = int(data["email_setting"])
    club = Club.query.filter_by(id=clubID).first()
    if not club:
        return {"Error": "Error"}

    if current_user.clubID != clubID or current_user.access < 2:
        return {"Error": "Error"}

    club.email_setting = email_setting

    db.session.commit()

    return jsonify("complete")


@admin_bp.route('/update_season_date', methods=['POST'])
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
        return {"Error": "Error"}

    if current_user.clubID != clubID or current_user.access < 2:
        return {"Error": "Error"}

    club.season_start = datetime.datetime.strptime(dates[0], '%B %d, %Y')
    club.season_end = datetime.datetime.strptime(dates[1], '%B %d, %Y')
    db.session.commit()

    return jsonify("complete")



@admin_bp.route('/delete_account', methods=['POST'])
def delete_account():
    """
    AJAX route for deleting user accounts. Route is accessible by admins through the buttons on the user_list page

    """
    data = request.get_data()
    userID = json.loads(data)
    if userID:
        try:
            user = User.query.filter_by(id=userID).first()
            db.session.delete(user)
            db.session.commit()
            return jsonify('success')
        except:
            return jsonify({'error': 'Invalid State'})
    return jsonify({'error': 'userID'})