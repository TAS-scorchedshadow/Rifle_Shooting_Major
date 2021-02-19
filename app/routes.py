import tarfile
from distutils.util import strtobool

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask import session as flask_session

from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db, mail
from app.forms import uploadForm, signInForm, signUpForm, reportForm, ResetPasswordRequestForm, ResetPasswordForm, \
    profileSelect
from app.models import User, Stage, Shot
from app.email import send_password_reset_email, send_activation_email
from app.uploadProcessing import validateShots
from app.timeConvert import utc_to_nsw, nsw_to_utc
from app.decompress import read_archive

import numpy
import json


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Homepage for the website. Identifies whether person is signed in.

    :return: Index html page
    """
    if request.method == "POST":
        username = request.form['user']
        if username:
            user = User.query.filter_by(username=username).first()
            flask_session['profileID'] = user.id
            return redirect('/profile')
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
        range = json.dumps(stage.rangeDistance)
        shots = Shot.query.filter_by(stageID=stageID).all()
        formattedList = []
        scoreList = []
        num = 1
        letter = ord("A")
        shotTotal = 0
        shotsList = [stat for stat in enumerate(shots)]
        shotDuration = 'N/A'
        for i, shot in shotsList:
            shotTotal += shot.score
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
        jsonList = json.dumps(formattedList)

        # Stage Stats
        stageResponse = stage.stageStats()
        stageStats = [round(stat, 2) for stat in stageResponse if isinstance(stat, float)]
        stageDuration = "{}m {}s".format(int(stageResponse[4] / 60), stageResponse[4] % 60)
        stageStats.append(stageDuration)

        formattedList.append(
            ["Total", 0, 0, str(shotTotal), stageDuration])  # Total appended to list to make display of shots easier

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
            elif shoot.rangeDistance == stage.rangeDistance:
                otherStages.append({'groupX': shoot.groupX, 'groupY': shoot.groupY})
        dayAvg = [dayX / count, dayY / count]
        myStages = json.dumps(myStages)
        otherStages = json.dumps(otherStages)
        for i, stat in enumerate(dayStats):
            dayStats[i] = round(stat / count, 2)
        dayDuration = "{}m {}s".format(int(dayStats[4] / 60), int(dayStats[4] % 60))
        dayStats.append(dayDuration)
        # Note: due to averaging method, dayStats[4] is duration in seconds while the other vars like
        # stageStats[4] or seasonStats[4] is duration as a string
        # Instead, dayStats[5] is duration as a string

        # Get Season Stats
        user = User.query.filter_by(id=stage.userID).first()
        seasonResponse = user.seasonStats()
        seasonStats = [round(stat, 2) for stat in seasonResponse if isinstance(stat, float)]
        seasonDuration = "{}m {}s".format(int(seasonResponse[4] / 60), seasonResponse[4] % 60)
        seasonStats.append(seasonDuration)

        return render_template('plotSheet.html', range=range, formattedList=formattedList,
                               jsonList=jsonList, stage=stage, stageStats=stageStats, seasonStats=seasonStats,
                               dayStats=dayStats, dayAvg=dayAvg, myStages=myStages, otherStages=otherStages)
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
    if not current_user.access >= 1:
        user = current_user
    else:
        try:
            userID = flask_session['profileID']
        except KeyError:
            userID = current_user.id
        user = User.query.filter_by(id=userID).first()
    print(user)
    form = profileSelect()
    if form.is_submitted():
        change = str(form.cell.data)
        newValue = form.data.data
        # user.(change) = newValue
        setattr(user, change, newValue)
        db.session.commit()

    info = {}
    info["SID"] = "NULL"
    info["DOB"] = user.dob
    info["Rifle Serial"] = user.rifleSerial
    info["StudentID"] = user.schoolID
    info["Grade"] = user.schoolYr
    info["Email"] = user.email
    info["Permit"] = user.permitNumber
    info["Expiry"] = user.permitExpiry
    info["Sharing"] = user.sharing
    info["Mobile"] = "NULL"
    info["Roll Class"] = "NULL"
    info["Mobile"] = "NULL"

    # z = numpy.polyfit(yearStubAvgLine, scoreStubAvgLine, 1)
    # p = numpy.poly1d(z)
    # pylab.plot(yearStubAvgLine, p(yearStubAvgLine), "r--")
    # trend = []
    # for j in range(len(yearStubAvgLine)):
    #    result = ((yearStubAvgLine[j]) * z[0]) + z[1]
    #    trend.append(result)

    return render_template('students/profile.html', form=form, user=user, info=info)


@app.route('/overview')
def profile_overview():
    # stub for shooter ID passed to the overview
    shooterID = 31

    stages_query = Stage.query.filter_by(userID=shooterID).all()
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


@app.route('/graphs')
def graphs():
    return render_template('graphs.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Page to receive file entries for upload of shoot info

    :return: Upload html page
    """
    form = uploadForm()
    stageList = []
    invalidList = []
    alert = [None, 0, 0]  # Alert type, Failures, Successes
    count = {"total": 0, "failure": 0, "success": 0}
    template = 'upload/upload.html'
    if form.identifier.data == "upload":
        if request.method == "POST":
            template = 'upload/uploadVerify.html'
            files = form.file.data
            for file in files:
                if tarfile.is_tarfile(file):
                    stages = read_archive(file, 3)
                    for stage_dict, issue_code in stages:
                        if 2 not in issue_code:
                            stage = validateShots(stage_dict)
                            stage['listID'] = count["total"]
                            stageList.append(stage)
                            if 1 in issue_code:
                                # Missing username
                                invalidList.append(stage)
                            else:
                                count["success"] += 1
                            count["total"] += 1

                    if count["success"] > 0:
                        alert[0] = "Success"
                        alert[2] = count["success"]
                    if count["failure"] > 0:
                        alert[0] = "Warning"
                        alert[1] = count["failure"]
                        if count["failure"] == count["total"]:
                            template = 'upload/upload.html'
                            alert[0] = "Failure"

    else:
        stageList = json.loads(request.form["stageDump"])
        userList = [User.query.all()]
        userDict = {}
        for user in userList:
            userDict[user.username] = user.id
        print(stageList)
        for key in request.form:
            if "username." in key:
                id = int(key[9:])
                username = request.form[key]
                stageList[id]['username'] = username
                print('yes' + str(key))
                if username in userDict:
                    count["success"] += 1
                    print(userDict[username])
                else:
                    invalidList.append(stageList[id])
                    count["failure"] += 1
        if not invalidList:  # todo: Ideally we can remove this so that the files that are done are just uploaded
            stageDefine = {}
            stageDefine['location'] = form.location.data
            stageDefine['rangeDistance'] = form.rangeDistance.data
            stageDefine['weather'] = form.weather.data
            print('started')
            print(invalidList)
            # todo THIS NEEDS TO BE FIXED PROBABLY IT'S KIIINDA JANK
            for item in stageList:
                # if item not in invalidList:  # todo: this is jank
                if 1 == 1:
                    idFound = User.query.filter_by(username=item['username']).first()
                    stage = Stage(id=item['id'], userID=idFound.id,
                                  timestamp=item['time'],
                                  groupSize=item['groupSize'],
                                  rangeDistance=stageDefine['rangeDistance'], location=stageDefine['location'],
                                  notes="")
                    db.session.add(stage)
                    # here I think stage needs to be uploaded then relocated for shots to be uploaded
                    id = item['id']
                    for point in item['validShots']:
                        shot = Shot(stageID=id, timestamp=point['ts'],
                                    xPos=point['x'], yPos=point['y'],
                                    score=point['score'], numV=point['Vscore'],
                                    sighter=point['sighter'])
                        db.session.add(shot)
                    db.session.commit()
                print('uploaded')
                count["total"] += 1
            print("DEBUG: Completed Upload")
            alert[0] = "Success"
            alert[2] = count["total"]
            if count["failure"] > 0:
                alert[0] = "Warning"
                alert[1] = count["failure"]
            stageList = []
        else:
            template = 'upload/uploadVerify.html'
            # todo: need to add an alert popup here
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
        user = User(fName=form.fName.data.strip(), sName=form.sName.data.strip(), school=form.school.data,
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


@app.route('/userList')
@login_required
def userList():
    """
    List of all current users on the system

    :return: userList html
    """
    if not current_user.access > 1:
        return redirect(url_for('index'))
    users = User.query.order_by(User.schoolID).all()
    return render_template('userAuth/userList.html', users=users)


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
    state = loadedData['state']
    userID = loadedData['id']
    if userID:
        try:
            user = User.query.filter_by(id=userID).first()
            user.isAdmin = strtobool(state)
            db.session.commit()
            return jsonify({'id': userID, 'newState': not strtobool(state)})
        except:
            print('error')
            return jsonify({'error': 'Invalid State'})


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
    print('reached')
    users = User.query.all()
    list = [{'label': "{} ({} {})".format(user.username, user.fName, user.sName), 'value': user.username,
             'group': user.group} for user in
            users]
    return jsonify(list)


@app.route('/getShots', methods=['POST'])
def getShots():
    data = request.get_data()
    loadedData = json.loads(data)
    print(loadedData)
    userID = loadedData[0]
    # numLoaded are the number of tables already loaded
    numLoaded = loadedData[1]
    print(numLoaded)
    stages = Stage.query.filter_by(userID=userID).all()[numLoaded: numLoaded + 3]
    stagesList = []
    for stage in stages:
        shots = Shot.query.filter_by(stageID=stage.id).all()
        scores = {}
        totalScore = 0
        num = 1
        letter = ord("A")
        shot_list = []
        for shot in shots:
            if shot.sighter:
                scores[chr(letter)] = shot.score
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
                           'rangeDistance': '300m',
                           'timestamp': utc_to_nsw(stage.timestamp).strftime("%d %b %Y %I:%M %p"),
                           'std': std,
                           'duration': duration,
                           'stageID': stage.id,
                           })
    print(stagesList)
    return jsonify(stagesList)
    # stage = Stage.query.filter_by(userID=userID).all()


@app.route('/getTargetStats', methods=['POST'])
def getTargetStats():
    # Function provides databse information for ajax request in gearSettings.js
    stageID = request.get_data().decode("utf-8")
    stage = Stage.query.filter_by(id=stageID).first()
    if stage:  # Handles if stageID parameter is given but is not found in database

        return jsonify({'success': 'success'})
    return jsonify({'error': 'userID'})
