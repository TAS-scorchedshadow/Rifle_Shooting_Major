import json

from flask import Blueprint, request, redirect, render_template
from flask import session as flask_session
from flask_login import login_required, current_user

from app.models import User, Settings
from app.decorators import roles_required

profile_bp = Blueprint('profile_bp', __name__)


@profile_bp.route('/profile_list', methods=['GET', 'POST'])
@login_required
@roles_required(["COACH"])
def profile_list():
    searchError = False
    if request.method == "POST":
        print(request.form)
        textInput = request.form['user-search']
        cardInput = request.form['user']
        if textInput:
            user = User.query.filter_by(username=textInput).first()
            if user:
                flask_session['profileID'] = user.id
                return redirect('/profile')
            else:
                searchError = True
        if cardInput:
            flask_session['profileID'] = int(cardInput)
            return redirect('/profile')
    users = User.query.order_by(User.username).all()
    yearGroups = {'12': ['Year 12'], '11': ['Year 11'], '10': ['Year 10'], '9': ['Year 9'], '8': ['Year 8'],
                  '7': ['Year 7'], 'other': ['Graduated']}
    for user in users:
        schoolYr = str(user.get_school_year())
        if schoolYr in yearGroups:
            yearGroups[schoolYr].append([user.sName, user.fName, user.id])
        else:
            yearGroups['other'].append([user.sName, user.fName, user.id])

    yearGroups = json.dumps(yearGroups)
    return render_template('profile/profile_list.html', users=users, yearGroups=yearGroups, error=searchError)



@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Page which displays shooter/stages/shot information

    :parameter [UserID]: Database Shooter ID. Not passed to function, but read from URL
    :return: profile.html with info dictionary for the table, form for forms and variables/lists for ChartJS
    """
    search_error = False
    if request.method == "POST":
        username = request.form['user']
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                flask_session['profileID'] = user.id
                return redirect('/profile')
            else:
                search_error = True
    if not current_user.access >= 1:
        user = current_user
    else:
        try:
            userID = flask_session['profileID']
        except KeyError:
            userID = current_user.id
        user = User.query.filter_by(id=userID).first()

    tableInfo = {}
    tableInfo["SID"] = user.shooterID
    tableInfo["DOB"] = user.dob
    tableInfo["Rifle Serial"] = user.rifle_serial
    tableInfo["StudentID"] = user.schoolID
    tableInfo["Grade"] = user.get_school_year()
    tableInfo["Email"] = user.email
    tableInfo["Permit"] = user.permitNumber
    tableInfo["Expiry"] = user.permitExpiry
    tableInfo["Sharing"] = user.sharing
    tableInfo["Mobile"] = user.mobile

    s = Settings.query.filter_by(id=0).first()
    times = {"start": s.season_start.strftime("%d:%m:%Y"), "end": s.season_end.strftime("%d:%m:%Y")}
    return render_template('profile/profile.html', user=user, tableInfo=tableInfo, error=search_error,
                           season_time=times)

