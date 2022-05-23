import os
import tarfile
from distutils.util import strtobool

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask import session as flask_session
from sqlalchemy import desc
import time
import datetime

from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db, mail
from app.forms import *
from app.models import User, Stage, Shot
from app.email import send_password_reset_email, send_activation_email, send_report_email, send_upload_email
from app.uploadProcessing import validateShots
from app.timeConvert import utc_to_nsw, nsw_to_utc, get_grad_year, get_school_year, formatDuration
from app.decompress import read_archive
from app.stagesCalc import plotsheet_calc, stats_of_period, getFiftyScore, HighestStage, LowestStage
import numpy
import json
from sklearn.cluster import DBSCAN


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
    searchError = False
    if request.method == "POST":
        username = request.form['user']
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                flask_session['profileID'] = user.id
                return redirect('/profile')
            else:
                searchError = True
    return render_template('index.html', error=searchError)


@app.route('/landing')
def landing():
    """
    First page opened when address entered

    :return: Landing html page
    """
    return render_template('landingPage.html')


# By Dylan Huynh
@login_required
@app.route('/target')
def target():
    """
    Displays target & mapping of shits from the shoot

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
            return render_template('plotSheet.html', data=data, user=user, stage=stage)
        else:
            return render_template('students/studentPlotSheet.html', data=data, user=user, stage=stage)
    return render_template('index.html')

    # Following calculates the group center position for each stage. Also updates the database accordingly (not in use)
    # @app.route('/groupTest')
    # def getGroupStats():
    #     stages = Stage.query.all()
    #     for stage in stages:
    #         stageID = stage.id
    #         shots = Shot.query.filter_by(stageID=stageID).all()
    #         totalX = 0
    #         totalY = 0
    #         sighterNum = 0
    #         for shot in shots:
    #             if not shot.sighter:
    #                 totalX += shot.xPos
    #                 totalY += shot.yPos
    #             else:
    #                 sighterNum += 1
    #         stage.groupX = totalX / (len(shots) - sighterNum)
    #         stage.groupY = totalY / (len(shots) - sighterNum)
    #     db.session.commit()

    print('database commit successful')
    return render_template('index.html')


# By Dylan Huynh
@app.route('/submitNotes', methods=['POST'])
def submitNotes():
    """
    AJAX route for updating the notes of a stage from the plotsheet.

    :return: indication of submission success
    """
    # Function submits changes in notes
    data = request.get_data()
    loadedData = json.loads(data)
    stage = Stage.query.filter_by(id=loadedData[0]).first()
    stage.notes = loadedData[1]
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
    # userID = request.args.get('userID')
    # user = User.query.filter_by(id=userID).first()
    searchError = False
    if request.method == "POST":
        username = request.form['user']
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                flask_session['profileID'] = user.id
                return redirect('/profile')
            else:
                searchError = True
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
    return render_template('students/profile.html', user=user, tableInfo=tableInfo, error=searchError)


# by Henry Guo
@app.route('/getAvgShotGraphData', methods=['POST'])
def getAvgShotData():
    """
    Collect shots for use in the averages line graph
    """
    endDate = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

    startDate = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d')
    startDate = datetime.datetime.combine(startDate, datetime.datetime.min.time())

    userID = request.get_data().decode("utf-8")
    stats = stats_of_period(userID, 'week', startDate, endDate)
    avgScores = []
    stDev = []
    timestamps = []
    for stage in stats:
        avgScores.append(stage['avg'])
        stDev.append(stage['stDev'])
        timestamps.append(stage['date'])
    formattedTime = []
    for date in timestamps:
        print(date)
        formattedTime.append(utc_to_nsw(date).strftime("%d/%m/%y"))
    graphData = jsonify({'scores': avgScores,
                         'times': formattedTime,
                         'sd': stDev,
                         })
    return graphData



@app.route('/testdelshoot', methods=['GET', 'POST'])
@login_required
def testdelshoot():
    """
    Code that deletes all shoots put under the sbhs.admin user.
    """
    user = User.query.filter_by(username="sbhs.admin").first()
    stageList = [stage for stage in Stage.query.filter_by(userID=user.id).all()]
    for stage in stageList:
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
    form = uploadForm()
    stageList = []
    invalidList = []
    alert = [None, 0, 0]  # Alert type, Failures, Successes
    count = {"total": 0, "failure": 0, "success": 0}
    template = 'upload/upload.html'
    if form.identifier.data == "upload":
        # Uploading
        if request.method == "POST":
            template = 'upload/uploadVerify.html'
            files = form.file.data
            upload_time = int(form.weeks.data)
            for file in files:
                stages = read_archive(file, upload_time)
                for stage_dict, issue_code in stages:
                    if 2 not in issue_code:  # i.e. at least more than 1 counting shot
                        stage = validateShots(stage_dict)  # Reformat shoot stage to obtain usable data
                        stage['listID'] = count["total"]
                        stageList.append(stage)
                        if 1 in issue_code:  # i.e. missing username
                            invalidList.append(stage)
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
        stageList = json.loads(request.form["stageDump"])
        stageDefine = {'location': form.location.data, 'weather': form.weather.data, 'ammoType': form.ammoType.data}
        invalidListID = []
        userList = [user for user in User.query.all()]
        userDict = {}
        for user in userList:
            userDict[user.username] = user.id
        for key in request.form:
            if "username." in key:
                username = request.form[key]
                stageList[int(key[9:])]['username'] = username
                if username not in userDict:
                    invalidList.append(stageList[int(key[9:])])
                    invalidListID.append(int(key[9:]))
                    count["failure"] += 1
        print('started')
        print(invalidListID)
        for item in stageList:
            if item['listID'] not in invalidListID:
                # Uploads a stage
                # todo: Need to add an ammoType column to the stage database
                print(item['username'])
                stage = Stage(id=item['id'], userID=userDict[item['username']],
                              timestamp=item['time'],
                              groupSize=item['groupSize'], groupX=item['groupX'], groupY=item['groupY'],
                              distance=item['distance'], location=stageDefine['location'],
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
            for item in stageList:
                stage = Stage(id=item['id'], userID=userDict[item['username']],
                              timestamp=item['time'],
                              groupSize=item['groupSize'], groupX=item['groupX'], groupY=item['groupY'],
                              distance=item['distance'], location=stageDefine['location'],
                              notes="")
                stageClassList.append(stage)
            for user in userList:
                print(user)
                print(stageClassList)
                if os.environ["MAIL_SETTING"] == 2:
                    send_upload_email(user, stageClassList)
            stageList = []
            alert[0] = "Success"
            alert[2] = count["success"]
        else:  # Failed to upload
            stageList = invalidList
            count["total"] = 0
            for item in stageList:
                item["listID"] = count["total"]
                count["total"] += 1
            template = 'upload/uploadVerify.html'
            alert[0] = "Incomplete"
            alert[1] = count["failure"]
            alert[2] = count["success"]
            print("DEBUG: Not all usernames correct")
    stageDump = json.dumps(stageList)
    return render_template(template, form=form, stageDump=stageDump, invalidList=invalidList, alert=alert)


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
    return render_template('userAuth/login.html', form=form)


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
        return render_template('userAuth/registerSuccess.html', user=user)
    return render_template('userAuth/register.html', title='Register', form=form)


@app.route('/coachRegister', methods=['GET', 'POST'])
def coachRegister():
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
        return render_template('userAuth/registerSuccess.html', user=user)
    return render_template('userAuth/coachRegister.html', title='Register', form=form)


@app.route('/logout')
def logout():
    """
    Allows users to exit from the system
    """
    logout_user()
    return redirect(url_for('index'))


# By Dylan Huynh
@app.route('/emailActivation/<token>', methods=['GET', 'POST'])
def emailActivation(token):
    """
    Deprecated

    :param token: Time sensitive token sent by email.
    :return: TO BE FILLED
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_activation_token(token)
    if not user:
        return redirect(url_for('index'))
    user.isActive = True
    db.session.commit()
    return render_template('userAuth/resetPassword.html')


# By Dylan Huynh
@app.route('/requestResetPassword', methods=['GET', 'POST'])
def requestResetPassword():
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
        flash('Check your email')
        return redirect(url_for('login'))
    return render_template('userAuth/requestResetPassword.html', form=form)


# By Dylan Huynh
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Requesting a password reset if account details forgotten

    :return: Reset password html page
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('login'))
    return render_template('userAuth/resetPassword.html', form=form)


# By Dylan Huynh
@app.route('/userList', methods=['GET', 'POST'])
@login_required
def userList():
    """
    List of all current users on the system.

    :return: userList.html
    """
    if not current_user.access >= 2:
        return redirect(url_for('index'))
    users = User.query.order_by(User.access, User.sName).all()
    for user in users:
        user.schoolYr = user.get_school_year()
    return render_template('userAuth/userList.html', users=users, mail_setting=os.environ["MAIL_SETTING"])


# By Dylan Huynh
@app.route('/emailSettings', methods=['POST'])
def emailSettings():
    """
    AJAX route used to update the enviroment variable MAIL_SETTING

    """
    setting = json.loads(request.get_data())
    os.environ["MAIL_SETTING"] = setting
    return jsonify("complete")


# By Dylan Huynh
@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    """
    AJAX route for deleting user accounts. Route is accessible by admins through the buttons on the userList page

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
     Route is accessible by admins through the buttons on the userList page

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


# By Dylan Huynh
@app.route('/createAccount', methods=['POST'])
def createAccount():
    """
    @deprecated

    """
    data = request.get_data()
    loadedData = json.loads(data)
    user = loadedData['test']
    print(user)
    print(user.sName)


# By Andrew Tam
@app.route('/profileList', methods=['GET', 'POST'])
@login_required
def profileList():
    # with assistance from Henry and using Dylan's existing code
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
    return render_template('students/profileList.html', users=users, yearGroups=yearGroups, error=searchError)


# By Dylan Huynh
@app.route('/getGear', methods=['POST'])
def getGear():
    """
     AJAX request to obtain gear data before display. Route accessible from plotsheet.html and profile.html

    :return: JSON containing gear information
    """
    # Function provides databse information for ajax request in gearSettings.js
    userID = request.get_data().decode("utf-8")
    user = User.query.filter_by(id=userID).first()
    if user:  # Handles if userID parameter is given but is not found in database
        return jsonify({'jacket': user.jacket, 'glove': user.glove,
                        'hat': user.hat, 'slingHole': user.slingHole, 'slingLength': user.slingPoint,
                        'butOut': user.butOut, 'butUp': user.butUp, 'ringSize': user.ringSize,
                        'sightHole': user.sightHole})
    return jsonify({'error': 'userID'})


# By Dylan Huynh
@app.route('/getUsers', methods=['POST'])
def getUsers():
    """
    Generates a list of names used to complete the autofill fields. Used in autofill.js

    :return: List of Dictionaries, Key: Username, Value: Username, first name, last name
    """
    users = User.query.all()
    list = [{'label': "{} ({} {})".format(user.username, user.fName, user.sName), 'value': user.username} for user in
            users]
    return jsonify(list)


# By Dylan Huynh
@app.route('/sendWeeklyReport', methods=['POST'])
def sendWeeklyReport(banned_IDs):
    send_report_email(banned_userIDs=banned_IDs)
    return


# By Henry Guo
@app.route('/getShots', methods=['POST'])
def getShots():
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
        #print(dates)
        startDate = datetime.datetime.strptime(dates[0], '%B %d, %Y')
        endDate = datetime.datetime.strptime(dates[1], '%B %d, %Y')
        #print(startDate, endDate)
        stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.userID == userID).order_by(
            desc(Stage.timestamp)).all()[numLoaded: totaltoLoad]
    else:
        stages = Stage.query.filter_by(userID=userID).order_by(desc(Stage.timestamp)).all()[numLoaded: totaltoLoad]
    stagesList = []
    for stage in stages:
        data = stage.formatShots()
        stage.initStageStats()
        displayScore = f"{data['total']}/{data['totalPossible']}"
        stagesList.append({'scores': data["scores"],
                           'totalScore': displayScore,
                           'groupSize': round(stage.groupSize, 1),
                           'distance': stage.distance,
                           'timestamp': utc_to_nsw(stage.timestamp).strftime("%d %b %Y %I:%M %p"),
                           'std': round(stage.std, 2),
                           'duration': formatDuration(stage.duration),
                           'stageID': stage.id,
                           'sighters': data['sighters']
                           })
    return jsonify(stagesList)
    # stage = Stage.query.filter_by(userID=userID).all()


# By Henry Guo
@app.route('/getTargetStats', methods=['POST'])
def getTargetStats():
    """
    Function provides databse information for ajax request in targetAjax.js
    """
    stageID = request.get_data().decode("utf-8")
    stage = Stage.query.filter_by(id=stageID).first()
    if stage:  # Handles if stageID parameter is given but is not found in database

        return jsonify({'success': 'success'})
    return jsonify({'error': 'userID'})


# By Henry Guo
@app.route('/getAllShotsSeason', methods=['POST'])
def getAllShotsSeason():
    """
    Function collects every shot in the time-frame selected by the user
    """
    input_ = request.get_data().decode('utf-8')
    loadedInput = json.loads(input_)
    print(loadedInput)
    dist = loadedInput['distance']
    userID = loadedInput['userID']
    size = int(loadedInput['size'])
    dateRange = loadedInput['dateRange']
    dates = dateRange.split(' - ')
    print(dates)
    startDate = nsw_to_utc(datetime.datetime.strptime(dates[0], '%B %d, %Y'))
    endDate = nsw_to_utc(datetime.datetime.strptime(dates[1], '%B %d, %Y'))
    print(startDate, endDate)
    target_widths = {
        "300m": 600,
        "400m": 800,
        "500m": 1320,
        "600m": 1320,
        "700m": 1830,
        "800m": 1830,
        "274m": 390,
        "365m": 520,
        "457m": 915,
        "548m": 915,
    }
    ratio = size / target_widths[dist]
    print(size, dist)
    print(ratio)
    data = {'heatmap': [], 'target': [], 'boxPlot': [], 'bestStage': [], 'worstStage': []}
    stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.distance == dist,
                                Stage.userID == userID).all()
    print(stages)
    for stage in stages:
        stage.initStageStats()
        for shot in stage.shotList:
            data['heatmap'].append(
                {'x': round(shot.xPos * ratio + (size / 2)), 'y': round(size / 2 - shot.yPos * ratio), 'value': 1})
        totalScore = stage.total
        fiftyScore = (totalScore / len(stage.shotList)) * 10
        data['boxPlot'].append(fiftyScore)
        data['target'] = data['target'] + stage.formatShots()["scores"] + stage.formatShots()["sighters"]

    # Sort the scores for boxPlot so the lowest value can be taken.
    # The lowest value is used to determine the lower bound of the box plot
    data['boxPlot'].sort()
    print('boxplot', data['boxPlot'])
    print('boxplot', stages)
    if len(stages) > 0:
        # Get highest and lowest scoring stages
        highestStage = HighestStage(userID, startDate, endDate, dist)
        data['bestStage'] = {
            'id': highestStage.id,
            'score': round(getFiftyScore(highestStage)),
            'time': str(utc_to_nsw(highestStage.timestamp))
        }
        lowestStage = LowestStage(userID, startDate, endDate, dist)
        data['worstStage'] = {
            'id': lowestStage.id,
            'score': round(getFiftyScore(lowestStage)),
            'time': str(utc_to_nsw(lowestStage.timestamp))
        }
    data = jsonify(data)
    return data


# Dylan Huynh
@app.route('/setGear', methods=['POST'])
def setGear():
    """
        @ Deprecated
         AJAX request to update the database with changes to the gear. Route accessible from plotsheet.html and profile.html
    """
    # Function takes input information from gearSettings.js and makes appropiate changes to the database
    data = request.get_data()
    loadedData = json.loads(data)
    userID = loadedData[0]
    user = User.query.filter_by(id=userID).first()
    if user:  # Handles if userID parameter is given but is not found in database
        field = loadedData[1]
        value = loadedData[2]
        # In this case setattr changes the value of a certain field in the database to the given value.
        # e.g. user.sightHole = "5"
        setattr(user, field, value)
        db.session.commit()
        return jsonify('success')
    return jsonify({'error': 'userID'})


# Rishi Wig & Dylan Huynh
@app.route('/submitTable', methods=['POST'])
def submitTable():
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


# Dylan Huynh
@app.route('/changeGroups', methods=['GET', 'POST'])
def change():
    if request.method == "POST":
        username = request.form['user']
        group = request.form['group']
        if username:
            user = User.query.filter_by(username=username).first()
            user.group = int(group)
            db.session.commit()
            print("group changed")
    return render_template('groupEditor.html')
