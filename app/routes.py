import os
from os.path import join, dirname

import dotenv
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask import session as flask_session
from sqlalchemy import desc
import datetime

from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import *
from app.generate_data import generate_rand_stages
from app.models import Settings, User, Stage, Shot
from app.email import send_password_reset_email, send_activation_email, send_upload_email, \
    send_feedback_email
from app.upload_processing import validate_shots
from app.time_convert import utc_to_nsw, nsw_to_utc, get_grad_year, format_duration
from app.decompress import read_archive
from app.stages_calc import plotsheet_calc, stats_of_period, highest_stage, lowest_stage
import json


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error/500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Homepage for the website. Identifies whether person is signed in.

    :return: Index html page
    """
    if not current_user.is_authenticated:
        return redirect(url_for('landing'))
    if current_user.access == 0:
        return redirect(url_for('profile'))
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
    return render_template('index.html', error=search_error)


@app.route('/landing')
def landing():
    """
    First page opened when address entered

    :return: Landing html page
    """
    return render_template('landing_page.html')


# By Dylan Huynh
@login_required
@app.route('/target')
def target():
    """
    Displays target & mapping of shots from the shoot

    :return:
    """
    # This route takes an argument from url and uses it to query the database for
    # the relevant shots and range information
    stageID = request.args.get('stageID')
    stage = Stage.query.filter_by(id=stageID).first()
    if stage:
        user = User.query.filter_by(id=stage.userID).first()
        data = plotsheet_calc(stage, user)
        if current_user.access >= 1:
            return render_template('plotsheet.html', data=data, user=user, stage=stage)
        else:
            return render_template('students/student_plot_sheet.html', data=data, user=user, stage=stage)
    return render_template('index.html')


@app.route('/random_target')
def rand_target():
    """
    Displays target & mapping of shots from the shoot

    :return:
    """
    stage = generate_rand_stages(20,"300m")
    user = User.query.filter_by(username="cameron.y1").first()
    data = plotsheet_calc(stage, user)

    return render_template('plotsheet.html', data=data, user=user, stage=stage)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        feedback = request.form['feedback']
        name = request.form['name']
        if name == '':
            name = "anonymous"
        send_feedback_email(feedback, name)
        flash("Message Sent", "success")

        return redirect(url_for('index'))
    return render_template('contact.html')


# By Dylan Huynh
@app.route('/submit_notes', methods=['POST'])
def submit_notes():
    """
    AJAX route for updating the notes of a stage from the plotsheet.

    :return: indication of submission success
    """
    # Function submits changes in notes
    data = request.get_data()
    loaded_data = json.loads(data)
    stage = Stage.query.filter_by(id=loaded_data[0]).first()
    stage.notes = loaded_data[1]
    db.session.commit()
    return jsonify({'success': 'success'})


# By Dylan Huynh
@app.route('/profile', methods=['GET', 'POST'])
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
    return render_template('students/profile.html', user=user, tableInfo=tableInfo, error=search_error,
                           season_time=times)


# by Henry Guo
@app.route('/get_avg_shot_graph_data', methods=['POST'])
def get_avg_shot_data():
    """
    Collect shots for use in the averages line graph
    """
    end_date = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

    start_date = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d')
    start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())

    user_id = request.get_data().decode("utf-8")
    stats = stats_of_period(user_id, 'week', start_date, end_date)
    avg_scores = []
    st_dev = []
    timestamps = []
    for stage in stats:
        avg_scores.append(stage['avg'])
        st_dev.append(stage['stDev'])
        timestamps.append(stage['date'])
    formatted_time = []
    for date in timestamps:
        print(date)
        formatted_time.append(utc_to_nsw(date).strftime("%d/%m/%y"))
    graph_data = jsonify({'scores': avg_scores,
                          'times': formatted_time,
                          'sd': st_dev,
                          })
    return graph_data


@app.route('/testdelshoot', methods=['GET', 'POST'])
@login_required
def testdelshoot():
    """
    Code that deletes all shoots put under the sbhs.admin user.
    """
    user = User.query.filter_by(username="sbhs.admin").first()
    stage_list = [stage for stage in Stage.query.filter_by(userID=user.id).all()]
    for stage in stage_list:
        print(stage)
        db.session.delete(stage)
    db.session.commit()
    return "OK"


# By Ryan Tan
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Page to receive file entries for upload of shoot info

    :return: Upload html page
    """
    # Initialise Variables
    if not current_user.access >= 1 or current_user.username == "preview":
        return redirect(url_for('index'))
    form = uploadForm()
    stage_list = []
    invalid_list = []
    alert = [None, 0, 0]  # Alert type, Failures, Successes
    count = {"total": 0, "failure": 0, "success": 0}
    template = 'upload/upload.html'
    if form.identifier.data == "upload":
        # Uploading
        if request.method == "POST":
            template = 'upload/upload_verify.html'
            files = form.file.data
            upload_time = int(form.weeks.data)
            for file in files:
                stages = read_archive(file, upload_time)
                for stage_dict, issue_code in stages:
                    if 2 not in issue_code:  # i.e. at least more than 1 counting shot
                        stage = validate_shots(stage_dict)  # Reformat shoot stage to obtain usable data
                        stage['listID'] = count["total"]
                        stage_list.append(stage)
                        if 1 in issue_code:  # i.e. missing username
                            invalid_list.append(stage)
                        else:
                            count["success"] += 1
                        count["total"] += 1

            # Alert message handling
            if count["success"] > 0:
                alert[0] = "Success"
                alert[2] = count["success"]
            if count["failure"] > 0 or count["total"] == 0:
                alert[0] = "Warning"
                alert[1] = count["failure"]
                if count["failure"] == count["total"]:
                    # If ALL files failed, return to upload page
                    template = 'upload/upload.html'
                    alert[0] = "Failure"
    else:
        # Verifying Upload
        stage_list = json.loads(request.form["stageDump"])
        stage_define = {'location': form.location.data, 'weather': form.weather.data, 'ammoType': form.ammoType.data}
        invalid_list_id = []
        user_list = [user for user in User.query.all()]
        user_dict = {}
        for user in user_list:
            user_dict[user.username] = user.id
        for key in request.form:
            if "username." in key:
                username = request.form[key]
                stage_list[int(key[9:])]['username'] = username
                if username not in user_dict:
                    invalid_list.append(stage_list[int(key[9:])])
                    invalid_list_id.append(int(key[9:]))
                    count["failure"] += 1
        print('started')
        print(invalid_list_id)
        for item in stage_list:
            if item['listID'] not in invalid_list_id:
                # Uploads a stage
                # todo: Need to add an ammoType column to the stage database
                print(item['username'])
                stage = Stage(id=item['id'], userID=user_dict[item['username']],
                              timestamp=item['time'],
                              groupSize=item['groupSize'], groupX=item['groupX'], groupY=item['groupY'],
                              distance=item['distance'], location=stage_define['location'],
                              notes="")
                db.session.add(stage)
                # Uploads all shots in the stage
                for point in item['validShots']:
                    shot = Shot(stageID=item['id'], timestamp=point['ts'],
                                xPos=point['x'], yPos=point['y'],
                                score=point['score'], vScore=point['Vscore'],
                                sighter=point['sighter'])
                    db.session.add(shot)
                print('ready for upload')
                count["success"] += 1
            count["total"] += 1
        db.session.commit()
        print("DEBUG: Completed Upload")
        if count["success"] == count["total"]:  # successfully uploaded
            stageClassList = []
            for item in stage_list:
                stage = Stage(id=item['id'], userID=user_dict[item['username']],
                              timestamp=item['time'],
                              groupSize=item['groupSize'], groupX=item['groupX'], groupY=item['groupY'],
                              distance=item['distance'], location=stage_define['location'],
                              notes="")
                stageClassList.append(stage)
            for user in user_list:
                print(user)
                print(stageClassList)
                s = Settings.query.filter_by(id=0).first()
                if s.email_setting == 2:
                    send_upload_email(user, stageClassList)
            stage_list = []
            alert[0] = "Success"
            alert[2] = count["success"]
        else:  # Failed to upload
            stage_list = invalid_list
            count["total"] = 0
            for item in stage_list:
                item["listID"] = count["total"]
                count["total"] += 1
            template = 'upload/upload_verify.html'
            alert[0] = "Incomplete"
            alert[1] = count["failure"]
            alert[2] = count["success"]
            print("DEBUG: Not all usernames correct")
    stageDump = json.dumps(stage_list)
    return render_template(template, form=form, stageDump=stageDump, invalidList=invalid_list, alert=alert)


# Adapted from Flask Megatutorial by Dylan Huynh
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Allows the user to log on to the system

    :return: Login page
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = signInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != ':':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('user_auth/login.html', form=form)


# Dylan Huynh
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET route displays registration form, POST route generates a new user object and uploads it to the database

    :return:
    """
    form = signUpForm()
    if form.validate_on_submit():
        email = form.schoolID.data + "@student.sbhs.nsw.edu.au"
        user = User(fName=form.fName.data.strip().lower().title(), sName=form.sName.data.strip().lower().title(),
                    school=form.school.data,
                    schoolID=form.schoolID.data, email=email, gradYr=str(form.gradYr.data))
        user.generate_username()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        flash('Congratulations, you are now a registered user!', 'success')
        return render_template('user_auth/register_success.html', user=user)
    return render_template('user_auth/register.html', title='Register', form=form)


@app.route('/coachRegister', methods=['GET', 'POST'])
def coach_register():
    form = independentSignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User(fName=form.fName.data.strip().lower().title(), sName=form.sName.data.strip().lower().title(),
                    email=email, school="OTHER")
        user.generate_username()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        flash('Congratulations, you are now a registered user!', 'success')
        return render_template('user_auth/register_success.html', user=user)
    return render_template('user_auth/coach_register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    """
    Allows users to exit from the system
    """
    logout_user()
    return redirect(url_for('index'))


# By Dylan Huynh
@app.route('/request_reset_password', methods=['GET', 'POST'])
def request_reset_password():
    """
    Requesting a password reset if account details forgotten

    :return: Reset password html page
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Password reset email sent successfully', "success")
        return redirect(url_for('login'))
    return render_template('user_auth/request_reset_password.html', form=form)


# By Dylan Huynh
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Requesting a password reset if account details forgotten

    :return: Reset password html page
    """
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid password reset token. Please try again.', 'error')
        return redirect(url_for('request_reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password was successfully reset', 'success')
        return redirect(url_for('login'))
    return render_template('user_auth/reset_password.html', form=form)


# By Dylan Huynh
@app.route('/user_list', methods=['GET', 'POST'])
@login_required
def user_list():
    """
    List of all current users on the system.

    :return: user_list.html
    """
    if not current_user.access >= 2:
        return redirect(url_for('index'))
    users = User.query.order_by(User.access, User.sName).all()
    for user in users:
        user.schoolYr = user.get_school_year()
    s = Settings.query.filter_by(id=0).first()
    times = {"start": s.season_start.strftime("%d:%m:%Y"), "end": s.season_end.strftime("%d:%m:%Y")}
    return render_template('user_auth/user_list.html', users=users, mail_setting=s.email_setting, season_time=times)


@app.route('/email_settings', methods=['POST'])
def email_settings():
    """
    AJAX route used to update the email_setting in the database

    """
    setting = json.loads(request.get_data())
    s = Settings.query.filter_by(id=0).first()
    s.email_setting = setting
    db.session.commit()

    return jsonify("complete")


@app.route('/update_season_date', methods=['POST'])
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


# By Dylan Huynh
@app.route('/delete_account', methods=['POST'])
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


# By Dylan Huynh
@app.route('/admin', methods=['POST'])
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


@app.route('/profile_list', methods=['GET', 'POST'])
@login_required
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
    return render_template('students/profile_list.html', users=users, yearGroups=yearGroups, error=searchError)


# By Dylan Huynh
@app.route('/get_users', methods=['POST'])
def get_users():
    """
    Generates a list of names used to complete the autofill fields. Used in autofill.js

    :return: List of Dictionaries, Key: Username, Value: Username, first name, last name
    """
    users = User.query.all()
    list = [{'label': "{} ({} {})".format(user.username, user.fName, user.sName), 'value': user.username} for user in
            users]
    return jsonify(list)


# By Henry Guo
@app.route('/get_shots', methods=['POST'])
def get_shots():
    """
    Collect shots for use in the recent shots card
    """

    data = request.get_data()
    loadedData = json.loads(data)
    userID = loadedData[0]
    # numLoaded are the number of tables already loaded
    numLoaded = loadedData[1]

    # Add up to 10 more tables
    totaltoLoad = numLoaded + 10

    # convert dateRange string into datetime objects
    dateRange = loadedData[2]
    if dateRange:
        dates = dateRange.split(' - ')
        # print(dates)
        startDate = datetime.datetime.strptime(dates[0], '%B %d, %Y')
        endDate = datetime.datetime.strptime(dates[1], '%B %d, %Y')
        # print(startDate, endDate)
        stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.userID == userID).order_by(
            desc(Stage.timestamp)).all()[numLoaded: totaltoLoad]
    else:
        stages = Stage.query.filter_by(userID=userID).order_by(desc(Stage.timestamp)).all()[numLoaded: totaltoLoad]
    stagesList = []
    for stage in stages:
        data = stage.format_shots()
        stage.init_stage_stats()
        displayScore = f"{data['total']}/{data['totalPossible']}"
        stagesList.append({'scores': data["scores"],
                           'totalScore': displayScore,
                           'groupSize': round(stage.groupSize, 1),
                           'distance': stage.distance,
                           'timestamp': utc_to_nsw(stage.timestamp).strftime("%d %b %Y %I:%M %p"),
                           'std': round(stage.std, 2),
                           'duration': format_duration(stage.duration),
                           'stageID': stage.id,
                           'sighters': data['sighters']
                           })
    return jsonify(stagesList)


# By Henry Guo
@app.route('/get_target_stats', methods=['POST'])
def get_target_stats():
    """
    Function provides databse information for ajax request in ajax_target.js
    """
    stageID = request.get_data().decode("utf-8")
    stage = Stage.query.filter_by(id=stageID).first()
    if stage:  # Handles if stageID parameter is given but is not found in database
        return jsonify({'success': 'success'})
    return jsonify({'error': 'userID'})


# By Henry Guo
@app.route('/get_all_shots_season', methods=['POST'])
def get_all_shots_season():
    """
    Function collects every shot in the time-frame selected by the user
    """
    input_ = request.get_data().decode('utf-8')
    loadedInput = json.loads(input_)

    dist = loadedInput['distance']
    userID = loadedInput['userID']
    dateRange = loadedInput['dateRange']
    dates = dateRange.split(' - ')

    startDate = nsw_to_utc(datetime.datetime.strptime(dates[0], '%B %d, %Y'))
    endDate = nsw_to_utc(datetime.datetime.strptime(dates[1], '%B %d, %Y'))

    data = {'target': [], 'boxPlot': [], 'bestStage': [], 'worstStage': []}
    stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.distance == dist,
                                Stage.userID == userID).all()
    print(stages)
    for stage in stages:
        stage.init_stage_stats()
        totalScore = stage.total
        fiftyScore = stage.score_as_percent()
        data['boxPlot'].append(fiftyScore)
        data['target'] = data['target'] + stage.format_shots()["scores"] + stage.format_shots()["sighters"]

    # Sort the scores for boxPlot so the lowest value can be taken.
    # The lowest value is used to determine the lower bound of the box plot
    data['boxPlot'].sort()
    print('boxplot', data['boxPlot'])
    print('boxplot', stages)
    if len(stages) > 0:
        # Get highest and lowest scoring stages
        highestStage = highest_stage(userID, startDate, endDate, dist)
        data['bestStage'] = {
            'id': highestStage.id,
            'score': round(highestStage.score_as_percent()),
            'time': str(utc_to_nsw(highestStage.timestamp))
        }
        lowestStage = lowest_stage(userID, startDate, endDate, dist)
        data['worstStage'] = {
            'id': lowestStage.id,
            'score': round(lowestStage.score_as_percent()),
            'time': str(utc_to_nsw(lowestStage.timestamp))
        }
    data = jsonify(data)
    return data


# Rishi Wig & Dylan Huynh
@app.route('/submit_table', methods=['POST'])
def submit_table():
    """
       AJAX request updates a user object(given by ID) with the new information provided in the table. Used in
    """
    data = request.get_data().decode("utf-8")
    data = json.loads(data)
    userID = data[0]
    tableDict = data[1]
    user = User.query.filter_by(id=userID).first()
    # In this case setattr changes the value of a certain field in the database to the given value.
    # e.g. user.sightHole = "5"
    if user:
        for field in tableDict:
            # Convert school year into graduation year
            if field == 'gradYr' and tableDict[field] is not None:
                try:
                    value = str(get_grad_year(tableDict[field]))
                except:
                    value = "None"
            else:
                value = tableDict[field]
            # email cannot be changed in order to prevent coaches from changing the emails on other accounts
            if value != "None" and field != 'email':
                setattr(user, field, value)
        db.session.commit()

    return jsonify({'success': 'success'})
