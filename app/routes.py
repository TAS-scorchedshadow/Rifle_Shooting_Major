import tarfile
from distutils.util import strtobool

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask import session as flask_session
from sqlalchemy import desc
import time
from datetime import datetime, timedelta

from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db, mail
from app.forms import *
from app.models import User, Stage, Shot
from app.email import send_password_reset_email, send_activation_email, send_report_email
from app.uploadProcessing import validateShots
from app.timeConvert import utc_to_nsw, nsw_to_utc
from app.decompress import read_archive
from app.stagesCalc import stage_by_n, stage_by_date
import numpy
import json
from app.stagesCalc import conversion

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
    return render_template('index.html')


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


@app.route('/landing')
def landing():
    """
    First page opened when address entered

    :return: Landing html page
    """
    return render_template('landingPage.html')


def plotsheet_calc(stage, user):
    shots = Shot.query.filter_by(stageID=stage.id).all()
    data = {}

    formattedList = []
    scoreList = []
    num = 1
    letter = ord("A")
    shotTotal = 0
    shotsList = [stat for stat in enumerate(shots)]
    shotDuration = 'N/A'
    for i, shot in shotsList:
        scoreList.append(shot.score)
        if i == 0:
            shotDuration = 'N/A'
        else:
            start = shotsList[i - 1][1].timestamp
            diff = (shot.timestamp - start).total_seconds()
            if int(diff / 60) == 0:
                shotDuration = "{}s".format(int(diff % 60))
            else:
                shotDuration = "{}m {}s".format(int(diff / 60), int(diff % 60))
        if shot.sighter:
            formattedList.append([chr(letter), shot.xPos, shot.yPos, str(shot.score), shotDuration])
            letter += 1
        else:
            formattedList.append([str(num), shot.xPos, shot.yPos, str(shot.score), shotDuration])
            num += 1
            shotTotal += shot.score
    jsonList = json.dumps(formattedList)
    data["jsonList"] = jsonList

    # Stage Stats
    stageResponse = stage.stageStats()
    stageStats = [round(stat, 2) for stat in stageResponse]
    stageDuration = "{}m {}s".format(int(stageResponse[4] / 60), stageResponse[4] % 60)
    stageStats[4] = stageDuration
    data['stageStats'] = stageStats

    formattedList.append(
        ["Total", 0, 0, str(shotTotal), stageDuration])  # Total appended to list to make display of shots easier
    data['formattedList'] = formattedList

    # Day Stats
    dayStages = stage.same_day()
    # dayX and dayY refers to the grouping coordinates
    dayX = 0
    dayY = 0
    count = 0
    # stages of other people's shoots on the same day and stores their grouping info
    otherStages = []
    # stages of the selected user's shoots on the same day and stores their grouping info
    myStages = []

    dayStats = [0, 0, 0, 0, 0]
    for shoot in dayStages:
        if shoot.userID == stage.userID:
            count += 1
            dayResponse = shoot.stageStats()
            for i, stat in enumerate(dayResponse):
                dayStats[i] = dayStats[i] + stat
            dayX += shoot.groupX
            dayY += shoot.groupY
            myStages.append({'groupX': shoot.groupX, 'groupY': shoot.groupY})
        elif shoot.distance == stage.distance:
            otherStages.append({'groupX': shoot.groupX, 'groupY': shoot.groupY})
    dayAvg = [dayX / count, dayY / count]
    myStages = json.dumps(myStages)
    otherStages = json.dumps(otherStages)
    for i, stat in enumerate(dayStats):
        dayStats[i] = round(stat / count, 2)
    dayDuration = "{}m {}s".format(int(dayStats[4] / 60), int(dayStats[4] % 60))
    dayStats[4] = dayDuration
    data['dayStats'] = dayStats
    data['dayAvg'] = dayAvg
    data['myStages'] = myStages
    data['otherStages'] = otherStages
    # Note: due to averaging method, dayStats[4] is duration in seconds while the other vars like
    # stageStats[4] or seasonStats[4] is duration as a string
    # Instead, dayStats[5] is duration as a string

    # Get Season Stats
    seasonResponse = user.seasonStats()
    seasonStats = [round(stat, 2) for stat in seasonResponse]
    seasonDuration = "{}m {}s".format(int(seasonResponse[4] / 60), seasonResponse[4] % 60)
    seasonStats[4] = seasonDuration
    data['seasonStats'] = seasonStats

    data['range'] = json.dumps(stage.distance)

    return data


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
        if current_user.access > 1:
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
    if request.method == "POST":
        username = request.form['user']
        if username:
            user = User.query.filter_by(username=username).first()
            flask_session['profileID'] = user.id
            return redirect('/profile')
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
    tableInfo["Grade"] = user.schoolYr
    tableInfo["Email"] = user.email
    tableInfo["Permit"] = user.permitNumber
    tableInfo["Expiry"] = user.permitExpiry
    tableInfo["Sharing"] = user.sharing
    tableInfo["Mobile"] = user.mobile

    # By Rishi Wig
    # form = profileSelect()
    # if form.is_submitted():
    #     change = str(form.cell.data)
    #     newValue = form.data.data
    #     # user.(change) = newValue
    #     setattr(user, change, newValue)
    #     db.session.commit()
    #

    # z = numpy.polyfit(yearStubAvgLine, scoreStubAvgLine, 1)
    # p = numpy.poly1d(z)
    # pylab.plot(yearStubAvgLine, p(yearStubAvgLine), "r--")
    # trend = []
    # for j in range(len(yearStubAvgLine)):
    #    result = ((yearStubAvgLine[j]) * z[0]) + z[1]
    #    trend.append(result)
    # stub for shooter ID passed to the overview
    # collect data fro graphs

    # amount = 5
    # start = datetime(2016, 6, 28)
    # end = datetime(2021, 6, 29)
    # stage_by_date(userID, start, end)
    # value = stage_by_n(userID, amount)

    # stages_query = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).all()
    # info = {}
    # times = []
    # scores = []
    # for i in range(len(stages_query)):
    #     info[stages_query[i].id] = 0
    # for j in info:
    #     shots_query = Shot.query.filter_by(stageID=j).all()
    #     total = 0
    #     score = 0
    #     for k in range(len(shots_query)):
    #         total += 1
    #         score += (shots_query[k].score)
    #     info[j] = (score/total)
    #     timestamp_query = Stage.query.filter_by(id=j).order_by(Stage.timestamp).all()
    #     for m in range(len(timestamp_query)):
    #         times.append(utc_to_nsw(timestamp_query[m].timestamp))
    #     scores.append(info[j])
    # strftime turn datetime object into string format, and json.dumps helps format for passing the list to ChartJS
    return render_template('students/profile.html', user=user, tableInfo=tableInfo)
# by Henry Guo
@app.route('/getAvgShotGraphData', methods=['POST'])
def getAvgShotData():
    userID = request.get_data().decode("utf-8")
    stages_query = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).all()
    timestamps, avgScores, total, stDev, scores = conversion(stages_query)
    formattedTime = []
    for date in timestamps:
        formattedTime.append(utc_to_nsw(date).strftime("%d/%m/%y"))
    graphData = jsonify({'scores': avgScores,
                         'times': formattedTime,
                         'sd': stDev,
                         })
    return graphData

#Rishi
@app.route('/overview')
def profile_overview():
    # stub for shooter ID passed to the overview
    shooterID = 56

    stages_query = Stage.query.filter_by(userID=shooterID).all()
    print(stages_query)
    info = {}
    times = []
    scores = []
    for i in range(len(stages_query)):
        info[stages_query[i].id] = 0
    for j in info:
        shots_query = Shot.query.filter_by(stageID=j).all()
        total = 0
        score = 0
        for k in range(len(shots_query)):
            total += 1
            score += (shots_query[k].score)
        info[j] = (score / total)
        timestamp_query = Stage.query.filter_by(id=j).all()
        for m in range(len(timestamp_query)):
            times.append(timestamp_query[m].timestamp)
        scores.append(info[j])

    # strftime turn datetime object into string format, and json.dumps helps format for passing the list to ChartJS
    for n in range(len(times)):
        times[n] = (times[n].strftime("%d-%b-%Y (%H:%M:%S.%f)"))[0:11]
    times = json.dumps(times)
    return render_template('students/profile_overview.html', dates=times, scores=scores)

#Rishi
@app.route('/settings')
def profile_settings():
    stubID = 31

    eqiupmentInfo = {}
    equipment_query = User.query.filter_by(id=stubID).all()
    for i in range(len(equipment_query)):
        eqiupmentInfo["Glove"] = equipment_query[i].glove
        eqiupmentInfo["Hat"] = equipment_query[i].hat
        eqiupmentInfo["Jacket"] = equipment_query[i].jacket
        eqiupmentInfo["Sight Hole"] = equipment_query[i].sightHole
        eqiupmentInfo["Sling Hole"] = equipment_query[i].slingHole
        eqiupmentInfo["Sling Point"] = equipment_query[i].slingPoint

    elevationInfo = {}
    elevation_query = User.query.filter_by(id=stubID).all()
    for i in range(len(equipment_query)):
        elevationInfo["ADI300m"] = elevation_query[i].ADI300m
        elevationInfo["Fore300m"] = elevation_query[i].Fore300m
        elevationInfo["PPU300m"] = elevation_query[i].PPU300m
        elevationInfo["ADI400m"] = elevation_query[i].ADI400m
        elevationInfo["Fore400m"] = elevation_query[i].Fore400m
        elevationInfo["PPU400m"] = elevation_query[i].PPU400m
        elevationInfo["ADI500m"] = elevation_query[i].ADI500m
        elevationInfo["Fore500m"] = elevation_query[i].Fore500m
        elevationInfo["PPU500m"] = elevation_query[i].PPU500m
        elevationInfo["ADI600m"] = elevation_query[i].ADI600m
        elevationInfo["Fore600m"] = elevation_query[i].Fore600m
        elevationInfo["PPU600m"] = elevation_query[i].PPU600m
        elevationInfo["ADI700m"] = elevation_query[i].ADI700m
        elevationInfo["Fore700m"] = elevation_query[i].Fore700m
        elevationInfo["PPU700m"] = elevation_query[i].PPU700m
        elevationInfo["ADI800m"] = elevation_query[i].ADI800m
        elevationInfo["Fore800m"] = elevation_query[i].Fore800m
        elevationInfo["PPU800m"] = elevation_query[i].PPU800m
        elevationInfo["ADI500y"] = elevation_query[i].ADI500y
        elevationInfo["Fore500y"] = elevation_query[i].Fore500y
        elevationInfo["PPU500y"] = elevation_query[i].PPU500y
        elevationInfo["ADI600y"] = elevation_query[i].ADI600y
        elevationInfo["Fore600y"] = elevation_query[i].Fore600y
        elevationInfo["PPU600y"] = elevation_query[i].PPU600y

    return render_template('students/profile_settings.html', equipmentInfo=eqiupmentInfo, elevationInfo=elevationInfo)


@app.route('/table')
def table():
    userID = 43
    user = User.query.filter_by(id=userID).first()
    tableInfo = {}
    tableInfo["SID"] = user.shooterID
    tableInfo["DOB"] = user.dob
    tableInfo["Rifle Serial"] = user.rifle_serial
    tableInfo["StudentID"] = user.schoolID
    tableInfo["Grade"] = user.schoolYr
    tableInfo["Email"] = user.email
    tableInfo["Permit"] = user.permitNumber
    tableInfo["Expiry"] = user.permitExpiry
    tableInfo["Sharing"] = user.sharing
    tableInfo["Mobile"] = user.mobile
    return render_template('table.html', userID=userID, tableInfo=tableInfo)


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
                            count["failure"] += 1
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
                # todo: Need to add an ammoType column to the shot database
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
        if count["success"] == count["total"]:
            stageList = []
            alert[0] = "Success"
            alert[2] = count["success"]
        else:
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
        print('submitted')
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Allows user to register an account on the system

    :return:
    """
    form = signUpForm()
    if form.validate_on_submit():
        # TODO account for other formats
        email = form.schoolID.data + "@student.sbhs.nsw.edu.au"
        user = User(fName=form.fName.data.strip().lower().title(), sName=form.sName.data.strip().lower().title(),
                    school=form.school.data,
                    schoolID=form.schoolID.data, email=email)
        user.generate_username()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        flash('Congratulations, you are now a registered user!', 'success')
        return render_template('userAuth/registerSuccess.html', user=user)
    return render_template('userAuth/register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    """
    Allows users to exit from the system

    :return: TO BE FILLED
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/emailActivation/<token>', methods=['GET', 'POST'])
def emailActivation(token):
    """
    TO BE FILLED

    :param token: TO BE FILLED
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


@app.route('/userList', methods=['GET', 'POST'])
@login_required
def userList():
    """
    List of all current users on the system

    :return: userList html
    """
    if not current_user.access >= 2:
        return redirect(url_for('index'))
    users = User.query.order_by(User.access, User.sName).all()
    if request.method == 'POST':
        file = request.files['file']
        read_file = file.read().decode('utf-8')
        newUsers = []
        roll = []
        for line in read_file.splitlines():
            if not line == "<end>":
                student = line.split('\t')
                names = student[1].split()
                fNames = []
                sNames = []
                for name in names:
                    if name.isupper():
                        if name.isalpha():
                            sNames.append(name.lower())
                    else:
                        fNames.append(name.lower())
                fName = " ".join(fNames).title()
                sName = " ".join(sNames).title()
                print(f"#{fName}# #{sName}#")
                user = User.query.filter_by(fName=fName, sName=sName).first()
                if user:
                    roll.append(user)
                else:
                    # Create User object from SBHS data
                    newUser = User(fName=fName, sName=sName, schoolID=student[0], schoolYr=student[2][:-2],
                                   email=student[0] + "@student.sbhs.nsw.edu.au")
                    newUser.generate_username()
                    newUser.set_password("password")
                    newUsers.append(newUser)
        missingUsers = [user for user in users if user not in roll]
        print(f"New Users {newUsers}")
        print(f"Missing Users {missingUsers}")
        return render_template('userAuth/userList.html', users=users, newUsers=newUsers, missingUsers=missingUsers)
    return render_template('userAuth/userList.html', users=users)


@app.route('/profileList')
@login_required
# todo figure out why cards are not appearing
def profileList():
    if not current_user.access > 1:
        return redirect(url_for('index'))
    users = User.query.order_by(User.username).all()
    return render_template('students/profileList.html', users=users)


@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    """
    Allows users to remove their account from the system

    :return: TO BE FILLED
    """
    print('reached')
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


# TODO merge both functions
@app.route('/admin', methods=['POST'])
def admin():
    """
    TO BE FILLED

    :return: TO BE FILLED
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


# TODO merge both functions
@app.route('/createAccount', methods=['POST'])
def createAccount():
    """
    TO BE FILLED

    :return: TO BE FILLED
    """
    data = request.get_data()
    loadedData = json.loads(data)
    user = loadedData['test']
    print(user)
    print(user.sName)


@app.route('/getGear', methods=['POST'])
def getGear():
    # Function provides databse information for ajax request in gearSettings.js
    print('reached')
    userID = request.get_data().decode("utf-8")
    print(userID)
    user = User.query.filter_by(id=userID).first()
    if user:  # Handles if userID parameter is given but is not found in database
        return jsonify({'jacket': user.jacket, 'glove': user.glove,
                        'hat': user.hat, 'slingHole': user.slingHole, 'slingLength': user.slingPoint,
                        'butOut': user.butOut, 'butUp': user.butUp, 'ringSize': user.ringSize,
                        'sightHole': user.sightHole})
    return jsonify({'error': 'userID'})


@app.route('/setGear', methods=['POST'])
def setGear():
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

@app.route('/getUsers', methods=['POST'])
def getUsers():
    users = User.query.all()
    list = [{'label': "{} ({} {})".format(user.username, user.fName, user.sName), 'value': user.username,
             'group': user.group} for user in
            users]
    return jsonify(list)


@app.route('/getShots', methods=['POST'])
def getShots():
    """
    Collect shots for use in the recent shots card
    :return:
    """
    data = request.get_data()
    loadedData = json.loads(data)
    userID = loadedData[0]
    # numLoaded are the number of tables already loaded
    numLoaded = loadedData[1]
    stages = Stage.query.filter_by(userID=userID).order_by(desc(Stage.timestamp)).all()[numLoaded: numLoaded + 3]
    stagesList = []
    for stage in stages:
        shots = Shot.query.filter_by(stageID=stage.id).all()
        sighters = {}
        scores = {}
        totalScore = 0
        num = 1
        letter = ord("A")
        shot_list = []
        for shot in shots:
            if shot.sighter:
                sighters[chr(letter)] = shot.score
                letter += 1
            else:
                scores[str(num)] = shot.score
                num += 1
                totalScore += shot.score
                shot_list.append(shot.score)
        std = round(numpy.std(shot_list), 1)
        duration = str(shots[-1].timestamp - shots[1].timestamp)
        duration = duration.split(':')
        # str(int()) is done to remove the zero in single digit numbers
        duration = '{}m {}s'.format(str(int(duration[1])), str(int(duration[2])))
        # TODO add weather
        stagesList.append({'scores': scores,
                           'totalScore': totalScore,
                           'groupSize': round(stage.groupSize, 1),
                           'distance': stage.distance,
                           'timestamp': utc_to_nsw(stage.timestamp).strftime("%d %b %Y %I:%M %p"),
                           'std': std,
                           'duration': duration,
                           'stageID': stage.id,
                           'sighters': sighters
                           })
    return jsonify(stagesList)
    # stage = Stage.query.filter_by(userID=userID).all()


@app.route('/getTargetStats', methods=['POST'])
def getTargetStats():
    """
    Function provides databse information for ajax request in gearSettings.js
    :return:
    """
    stageID = request.get_data().decode("utf-8")
    stage = Stage.query.filter_by(id=stageID).first()
    if stage:  # Handles if stageID parameter is given but is not found in database

        return jsonify({'success': 'success'})
    return jsonify({'error': 'userID'})


@app.route('/testHeatmap')
def testHeatmap():
    user = 61
    data = []
    shotList = []
    stages = Stage.query.filter_by(distance='300m').all()
    for stage in stages:
        shots = Shot.query.filter_by(stageID=stage.id).all()
        for shot in shots:
            data.append({'x': 2*shot.xPos + 600, 'y': 600 - 2*shot.yPos, 'value': 1})
            shotList.append(['1', shot.xPos, shot.yPos, shot.score])
    data = json.dumps(data)
    shotList = json.dumps(shotList)
    return render_template('testHeatmap.html', data=data, shotList=shotList)


@app.route('/getAllShotsSeason', methods=['POST'])
def getAllShotsSeason():
    """
    Function collects every shot from the user in the season
    :return:
    """
    input_ = request.get_data().decode('utf-8')
    loadedInput = json.loads(input_)
    dist = loadedInput['distance']
    userID = loadedInput['userID']
    data = {'heatmap': [], 'target': []}
    stages = Stage.query.filter_by(distance=dist, userID=userID).all()
    for stage in stages:
        shots = Shot.query.filter_by(stageID=stage.id).all()
        for shot in shots:
            #TODO change the value 300 depending on the shoot distance
            data['heatmap'].append({'x': round(shot.xPos + 300), 'y': round(300 - shot.yPos), 'value': 1})
            data['target'].append(['1', shot.xPos, shot.yPos, shot.score])
    dataDump = json.dumps(data)
    data = jsonify(data)
    return data


@app.route('/submitNotes', methods=['POST'])
def submitNotes():
    # Function submits changes in notes
    data = request.get_data()
    loadedData = json.loads(data)
    stage = Stage.query.filter_by(id=loadedData[0]).first()
    stage.notes = loadedData[1]
    db.session.commit()
    return jsonify({'success': 'success'})


# By Andrew Tam
def groupAvg(userID):
    XTotal = 0
    YTotal = 0
    stages = Stage.query.filter_by(userID=userID).all()
    length = len(stages)
    for i in range(length):
        XTotal = XTotal + stages[i].groupX
        YTotal = YTotal + stages[i].groupY
    groupXAvg = XTotal / length
    groupYAvg = YTotal / length

    return groupXAvg, groupYAvg


@app.route('/submitTable', methods=['POST'])
def submitTable():
    data = request.get_data().decode("utf-8")
    data = json.loads(data)
    userID = data[0]
    tableDict = data[1]
    user = User.query.filter_by(id=userID).first()
    # In this case setattr changes the value of a certain field in the database to the given value.
    # e.g. user.sightHole = "5"
    if user:
        for field in tableDict:
            value = tableDict[field]
            if value != "None":
                setattr(user, field,tableDict[field])
        db.session.commit()

    return jsonify({'success': 'success'})


@app.route('/sendWeeklyReport', methods=['POST'])
def sendWeeklyReport(banned_IDs):
    send_report_email(banned_userIDs=banned_IDs)
    return

