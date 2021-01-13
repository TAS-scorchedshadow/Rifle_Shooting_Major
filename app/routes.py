from distutils.util import strtobool

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import Date, cast, and_
from sqlalchemy.orm import session
from werkzeug.urls import url_parse

from app import app, db
from app.forms import uploadForm, signInForm, signUpForm, reportForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Stage, Shot
from app.email import send_password_reset_email, send_activation_email
from app.uploadProcessing import validateShots

from datetime import datetime
import numpy
from matplotlib import pylab
import json


@app.route('/')
def index():
    if not current_user.is_authenticated:
      return redirect(url_for('landing'))
    return render_template('index.html')


@app.route('/landing')
def landing():
    return render_template('landingPage.html')


@app.route('/target')
def target_test():
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
        for shot in shots:
            shotTotal += shot.score
            scoreList.append(shot.score)
            if shot.sighter:
                formattedList.append([chr(letter), shot.xPos, shot.yPos, str(shot.score)])
                letter += 1
            else:
                formattedList.append([str(num), shot.xPos, shot.yPos, str(shot.score)])
                num += 1
        jsonList = json.dumps(formattedList)
        formattedList.append(["Total", 0, 0, str(shotTotal)]) #Total appended to list to make display of shots easier

        #Stage Stats
        stageResponse = stage.stageStats()
        stageStats = [round(stat,2) for stat in stageResponse if isinstance(stat,float)]
        duration = "{}m {}s".format(int(stageResponse[4]/60),stageResponse[4] % 60)
        stageStats.append(duration)

        #test = Stage.query.filter(Stage.timestamp == stage.timestamp.date()).all()

        #Get Season Stats
        user = User.query.filter_by(id=stage.userID).first()
        seasonResponse = user.seasonStats()
        seasonStats = [round(stat,2) for stat in seasonResponse if isinstance(stat,float)]
        duration = "{}m {}s".format(int(seasonResponse[4]/60),seasonResponse[4] % 60)
        seasonStats.append(duration)
        return render_template('plotSheet.html', range=range, formattedList=formattedList, jsonList=jsonList,stage=stage,stageStats=stageStats,seasonStats=seasonStats)
    return render_template('index.html')


@login_required
@app.route('/profile')
def profile():
    userID = request.args.get('userID')
    user = User.query.filter_by(id=userID).first()
    form = reportForm()
    yearStubAvgLine = [2018, 2019, 2020]
    scoreStubAvgLine = [5, 8, 17]

    stubID = 36
    name = ""
    info = {}
    details_query = User.query.filter_by(id=stubID).all()
    for i in range(len(details_query)):
        name += details_query[i].fName + " " + details_query[i].sName
        #info["SID"] = details_query[i].schoolID
        info["SID"] = "NULL"
        info["DOB"] = details_query[i].dob
        info["Rifle Serial"] = details_query[i].rifleSerial
        info["StudentID"] = details_query[i].schoolID
        info["Grade"] = details_query[i].schoolYr
        info["Email"] = details_query[i].email
        info["Permit"] = details_query[i].permitNumber
        info["Expiry"] = details_query[i].permitExpiry
        info["Sharing"] = details_query[i].sharing
        info["Mobile"] = "NULL"
        info["Roll Class"] = "NULL"
        info["Mobile"] = "NULL"
        #info["Mobile"] = details_query[i].mobile
        #info["Roll Class"] = details_query[i].schoolYR
        #info["Mobile"] = details_query[i].mobile
    print(info)
    print(name)

    z = numpy.polyfit(yearStubAvgLine, scoreStubAvgLine, 1)
    p = numpy.poly1d(z)
    pylab.plot(yearStubAvgLine, p(yearStubAvgLine), "r--")
    trend = []
    for j in range(len(yearStubAvgLine)):
        result = ((yearStubAvgLine[j]) * z[0]) + z[1]
        trend.append(result)

    return render_template('students/profile.html', form=form, label=yearStubAvgLine, data=scoreStubAvgLine,
                           trend=trend, user=user, info=info, name=name)


@app.route('/overview')
def profile_overview():
    # stub for shooter ID passed to the overview
    shooterID = 31

    # database query from the shooter ID to find the stages. first loop gets the stages and creates a dictionary
    # following loops gets the scores, adds them together and places them as the respective values
    # database query to get times and corroborate with the scores from the dictionary in the previous function
    stages_query = Stage.query.filter_by(userID=shooterID).all()
    info = {}
    times = []
    scores = []
    for i in range(len(stages_query)):
        info[stages_query[i].id] = 0
    for j in info:
        shots_query = Shot.query.filter_by(stageID=j).all()
        score = 0
        for k in range(len(shots_query)):
            score += (shots_query[k].score)
        info[j] = score
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
    shooterID = 31

    info = {}
    equipment_query = User.query.filter_by(id=shooterID).all()
    for i in range(len(equipment_query)):
        info["Glove"] = equipment_query[i].glove
        info["Hat"] = equipment_query[i].hat
        info["Jacket"] = equipment_query[i].jacket
        info["Sight Hole"] = equipment_query[i].sightHole
        info["Sling Hole"] = equipment_query[i].slingHole
        info["Sling Point"] = equipment_query[i].slingPoint

    return render_template('students/profile_settings.html', info=info)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = uploadForm()
    stageList = []
    invalidList = []
    template = 'upload/upload.html'
    if form.identifier.data == "upload":
        if request.method == "POST":
            template = 'upload/uploadVerify.html'
            files = request.files.getlist('file')
            count = 0
            for file in files:
                try:
                    bytes = file.read()
                    string = bytes.decode('utf-8')
                    data = json.loads(string)
                    stage = validateShots(data)
                    # Decodes a file from FileStorage format into json format, and then extracts relevant info
                    # Fixes up file to obtain relevant data and valid shots
                    stage['listID'] = count
                    stageList.append(stage)
                    # todo: User.query.filter_by is exceptionally slow, if possible find a faster way to search username
                    idFound = User.query.filter_by(username=stage['username']).first()
                    if idFound is None:
                        invalidList.append(stage)
                except:
                    print("File had an error in uploading")
                count += 1

    else:
        stageList = json.loads(request.form["stageDump"])
        print(stageList)
        for key in request.form:
            if "username." in key:
                id = int(key[9:])
                username = request.form[key]
                stageList[id]['username'] = username
                idFound = User.query.filter_by(username=username).first()
                stageList[id]['userID'] = idFound.id
                if idFound is None:
                    invalidList.append(stageList[id])
        if not invalidList:
            stageDefine = {}
            stageDefine['location'] = form.location.data
            stageDefine['rangeDistance'] = form.rangeDistance.data
            stageDefine['weather'] = form.weather.data
            # todo: handle uploading
            for item in stageList:
                print(item)
                try:
                    stage = Stage(id=item['id'], userID=item['userID'],
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
                except:
                    print('DEBUG: Duplicate file')
            print("DEBUG: All usernames correct")
            stageList = []
        else:
            template = 'upload/uploadVerify.html'
            # todo: need to add an alert popup here
            print("DEBUG: Not all usernames correct")
    stageDump = json.dumps(stageList)
    return render_template(template, form=form, stageDump=stageDump, invalidList=invalidList)


@app.route('/login', methods=['GET', 'POST'])
def login():
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


@app.route('/emailActivation/<token>', methods=['GET', 'POST'])
def emailActivation(token):
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
def userList():
    users = User.query.order_by(User.schoolID).all()
    return render_template('userAuth/userList.html', users=users)


@app.route('/activate', methods=['POST'])
def activate():
    data = request.get_data()
    loadedData = json.loads(data)
    userID = loadedData['id']
    state = loadedData['state']
    if userID:
        try:
            user = User.query.filter_by(id=userID).first()
            user.isActive = strtobool(state)
            db.session.commit()
            return jsonify({'id': userID, 'newState': not strtobool(state)})
        except:
            print('error')
            return jsonify({'error': 'Invalid State'})

    return jsonify({'error': 'userID'})


# TODO merge both functions
@app.route('/admin', methods=['POST'])
def admin():
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
                           'timestamp': stage.timestamp,
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

        return jsonify({'success':'success'})
    return jsonify({'error': 'userID'})



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
