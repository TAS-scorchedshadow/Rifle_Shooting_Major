import datetime
import json

from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_required, current_user

from app import db
from app.models import User, Settings

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/user_list', methods=['GET', 'POST'])
@login_required
def user_list():
    """
    List of all current users on the system.

    :return: user_list.html
    """
    if not current_user.access >= 2:
        return redirect(url_for('welcome_bp.index'))
    users = User.query.order_by(User.access, User.sName).all()
    for user in users:
        user.schoolYr = user.get_school_year()
    s = Settings.query.filter_by(id=0).first()
    times = {"start": s.season_start.strftime("%d:%m:%Y"), "end": s.season_end.strftime("%d:%m:%Y")}
    return render_template('admin/user_list.html', users=users, mail_setting=s.email_setting, season_time=times)


@admin_bp.route('/admin', methods=['POST'])
def admin():
    """
     AJAX route for changing the account level of specific users.
     Route is accessible by admins through the buttons on the user_list page

    """
    data = request.get_data()
    loadedData = json.loads(data)
    userID = loadedData['id']
    if userID:
        user = User.query.filter_by(id=userID).first()
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
    setting = json.loads(request.get_data())
    s = Settings.query.filter_by(id=0).first()
    s.email_setting = setting
    db.session.commit()

    return jsonify("complete")


@admin_bp.route('/update_season_date', methods=['POST'])
def update_season_date():
    """
    AJAX route used to update the start & end times of a season in the database

    """
    rtn = json.loads(request.get_data())

    date_range = rtn["date_range"]
    dates = date_range.split(' - ')

    s = Settings.query.filter_by(id=0).first()
    s.season_start = datetime.datetime.strptime(dates[0], '%B %d, %Y')
    s.season_end = datetime.datetime.strptime(dates[1], '%B %d, %Y')
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
            print('error')
            return jsonify({'error': 'Invalid State'})
    return jsonify({'error': 'userID'})