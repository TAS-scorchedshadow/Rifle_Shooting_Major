import datetime
import json

from flask import Blueprint, request, redirect, render_template, flash, url_for
from flask import session as flask_session
from flask_login import login_required, current_user

from app import db
from app.api.api import get_stages, num_shots
from app.models import User, Club
from app.decorators import club_authorised_urlpath, club_exists, is_authorised
from app.profile.forms import updateInfoForm

profile_bp = Blueprint('profile_bp', __name__)


@profile_bp.route('/profile_list', methods=['GET'])
@login_required
def catch_profile_list():
    return redirect(url_for(".profile_list", club_name=current_user.club.name))


@profile_bp.route('/profile_list/<club_name>', methods=['GET', 'POST'])
@login_required
@club_authorised_urlpath("COACH")
def profile_list(club, club_name):
    searchError = False
    if request.method == "POST":
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
    users = User.query.filter_by(clubID=club.id).order_by(User.username).all()
    yearGroups = {'12': ['Year 12'], '11': ['Year 11'], '10': ['Year 10'], '9': ['Year 9'], '8': ['Year 8'],
                  '7': ['Year 7'], 'other': ['Graduated']}
    for user in users:
        schoolYr = str(user.get_school_year())
        if schoolYr in yearGroups:
            yearGroups[schoolYr].append([user.sName, user.fName, user.username])
        else:
            yearGroups['other'].append([user.sName, user.fName, user.username])

    yearGroups = json.dumps(yearGroups)
    return render_template('profile/profile_list.html', users=users, yearGroups=yearGroups, error=searchError, club=club)


def can_access_profile(user) -> bool:
    if current_user.access == 3:
        return True
    if user.club == current_user.club and current_user.access >= 1:
        return True
    return False

@profile_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """
    Page which displays shooter/stages/shot information

    :param username: User to display
    :return: profile.html with info dictionary for the table, form for forms and variables/lists for ChartJS
    """

    search_error = False
    if "username" not in request.args:
        user = current_user
    else:
        username = request.args["username"]
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = current_user
            search_error = True
        elif not can_access_profile(user):
            user = current_user


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

    club = user.club
    if not club:
        flash("No club with that name exists", "error")
        if request.referrer is not None:
            return redirect(request.referrer)
        else:
            return redirect(url_for("welcome_bp.index"))
    times = {"start": club.season_start.strftime("%d:%m:%Y"), "end": club.season_end.strftime("%d:%m:%Y")}
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    form = updateInfoForm(request.form)
    return render_template('profile/profile.html', user=user, tableInfo=tableInfo, error=search_error, today=today,
                           season_time=times, form=form, club=club)


@profile_bp.route('/update_user_info', methods=['POST'])
def update_user_info():
    form = updateInfoForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(id=int(form.userID.data)).first()
        if (current_user.access > user.access and current_user.clubID == user.clubID) or current_user.id == user.id:
            for field in form:
                if field.id != 'userID':
                    if field.data != "None":
                        setattr(user, field.id, field.data)
            db.session.commit()
            flash("Details Updated Successfully", "success")
        else:
            flash("Invalid permissions to edit this user", "error")
    return redirect('/profile')


@profile_bp.route('/get_stages', methods=["GET"])
def html_get_stages():
    userID = request.args.get('userID')
    date = datetime.datetime.strptime(request.args.get('start-date'), '%Y-%m-%d')
    page = int(request.args.get('page'))
    stages, final_page = get_stages(userID, date, page)
    html = ""
    if stages is None:
        return html
    for i, stage in enumerate(stages):
        htmlScoresBody = ""
        htmlSighters = ""
        for shot in stage['scores']:
            htmlScoresBody = htmlScoresBody + f"{shot['scoreVal']} "
        for shot in stage['sighters']:
            htmlSighters = htmlSighters + f"{shot['scoreVal']} "
        stage_html = ""
        if i < len(stages) - 1 or final_page is True:
            stage_html += """<div class="stage-overview">"""
        else:
            stage_html += f"""<div class="stage-overview" hx-get=/get_stages?userID={userID}&page={page+1} 
            hx-trigger="revealed" hx-swap="afterend" hx-include="[name='start-date']" hx-indicator="#indicator">"""
        stage_html += f"""
                <div class="row">
                    <div class="col-12 pb-4">
                        <div class="card shadow border-0 card-hover">
                            <div class="card-header recent-header">
                                <div class="row">
                                    <div class="col-4 align-self-center">
                                        <p class="text-left" style="font-size:12px; color: black">
                                        <i class="fas fa-clock"></i><span class="pl-1">{stage['duration']}</span>
                                        </p>
                                    </div>
                                    <div class="col-4 align-self-center">
                                        <p display="block" class="text-center" style="font-size:12px;">{stage['timestamp']}</p>
                                    </div>
                                    <div class="col-4 align-self-center">
                                        <p class="text-right" style="font-size:12px; color: black">
                                            <a href="/target?stageID={stage['stageID']}" class="stage-view show-sheet" target="_blank">
                                                    <u>View Plotsheet</u>
                                                    <i class="fas fa-external-link-alt" style="color:black;"></i>
                                            </a>
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="recent-body">
                                <div class="row">
                                    <div class="col-12">
                                        <div class="table-responsive">
                                            <table class="table table-sm table-bordered recentShotsTable">
                                                <thead>
                                                    <tr>
                                                        <th style='width: 55px;'>Range</th>
                                                        <th style='width: 62px;'>Sighters</th>
                                                        <th>Shots</th>
                                                        <th style='width: 69px;'>Total</th>
                                                        <th style='width: 37px;'>Std</th>
                                                        <th style='width: 55px;'>Group</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <th>{stage['distance']}</th>
                                                        <th>{htmlSighters}</th>
                                                        <th>{htmlScoresBody}</th>
                                                        <th>{stage['totalScore']}</th>
                                                        <th>{stage['std']}</th>
                                                        <th>{stage['groupSize']}</th>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        html += stage_html
    return html


@profile_bp.route('/profile/get_season_shot_data', methods=["GET"])
def season_shot_data():
    """
    GET request for seasonal shot data.
    expects {userID, start, end} where start end is in "%d:%m:%Y"

    :return: html displaying the shot data
    """
    userID = request.args.get('userID')
    season_start = datetime.datetime.strptime(request.args.get('start'), "%d:%m:%Y")
    season_end = datetime.datetime.strptime(request.args.get('end'), "%d:%m:%Y")
    data = num_shots(userID, season_start, season_end)
    html = f"""
            <table class="table table-sm table-bordered">
              <tbody>
                <tr>
                  <th scope="row">Sessions</th>
                  <td>{data["num_sessions"]}</td>
                </tr>
                <tr>
                  <th scope="row">Stages</th>
                  <td>{data["num_stages"]}</td>
                </tr>
                <tr>
                  <th scope="row">Shots</th>
                  <td>{data["num_shots"]}</td>
                </tr>
                <tr>
                  <th scope="row">Avr. Shots per Session</th>
                  <td>{data["num_shots_per_session"]}</td>
                </tr>
              </tbody>
            </table>
          """
    return html
