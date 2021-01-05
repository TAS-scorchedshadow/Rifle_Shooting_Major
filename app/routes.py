from distutils.util import strtobool

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import uploadForm, signInForm, signUpForm, reportForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Stage, Shot
from app.email import send_password_reset_email, send_activation_email
from app.uploadProcessing import validateShots

import numpy
from matplotlib import pylab

import json


@app.route('/')
def index():
    # if not current_user.is_authenticated:
    #     return redirect(url_for('landing'))
    return render_template('index.html')


@app.route('/landing')
def landing():
    return render_template('landingPage.html')


@app.route('/target')
def target_test():
    return render_template('targetTest.html')


@login_required
@app.route('/profile')
def profile():
    form = reportForm()

    yearStubAvgLine = [2018, 2019, 2020]
    scoreStubAvgLine = [5, 8, 17]

    z = numpy.polyfit(yearStubAvgLine, scoreStubAvgLine, 1)
    p = numpy.poly1d(z)
    pylab.plot(yearStubAvgLine, p(yearStubAvgLine), "r--")
    trend = []
    for j in range(len(yearStubAvgLine)):
        result = ((yearStubAvgLine[j])*z[0]) + z[1]
        trend.append(result)

    return render_template('students/profile.html', form=form, label=yearStubAvgLine, data=scoreStubAvgLine, trend=trend)


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
                # Decodes a file from FileStorage format into json format, and then extracts relevant info
                try:
                    bytes = file.read()
                    string = bytes.decode('utf-8')
                    data = json.loads(string)
                    stage = validateShots(data)  # Fixes up file to obtain relevant data and valid shots
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
        for key in request.form:
            if "username." in key:
                id = int(key[9:])
                username = request.form[key]
                stageList[id]['username'] = username
                idFound = User.query.filter_by(username=username).first()
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
                stage = Stage(jsonFilename=item['id'], userID=item['username'], timestamp=item['time'],
                              duration=item['duration'], groupSize=item['groupSize'],
                              rangeDistance=stageDefine['rangeDistance'], location=stageDefine['location'], notes="")
                # here I think stage needs to be uploaded then relocated for shots to be uploaded
                id = None
                for point in item['validShots']:
                    shot = Shot(stageID=id, timestamp=point['ts'], xPos=point['x'], yPos=point['y'],
                                score=point['score'], numV=point['Vscore'],
                                sighter=point['sighter'])
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
        #TODO account for other formats
        email = form.schoolID.data + "@student.sbhs.nsw.edu.au"
        user = User(fName=form.fName.data.strip(), sName=form.sName.data.strip(),school=form.school.data,schoolID=form.schoolID.data,email=email)
        user.generate_username()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        flash('Congratulations, you are now a registered user!','success')
        return render_template('userAuth/registerSuccess.html', user=user)
    return render_template('userAuth/register.html', title='Register', form=form)


@app.route('/emailActivation/<token>', methods=['GET','POST'])
def emailActivation(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_activation_token(token)
    if not user:
        return redirect(url_for('index'))
    user.isActive = True
    db.session.commit()
    return render_template('userAuth/resetPassword.html')


@app.route('/requestResetPassword',methods=['GET','POST'])
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
    return render_template('userAuth/requestResetPassword.html',form=form)


@app.route('/reset_password/<token>', methods=['GET','POST'])
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
    return render_template('userAuth/resetPassword.html',form=form)


@app.route('/userList')
def userList():
    users = User.query.order_by(User.schoolID).all()
    return render_template('userAuth/userList.html',users=users)


@app.route('/activate',methods=['POST'])
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

#TODO merge both functions
@app.route('/admin',methods=['POST'])
def admin():
    data = request.get_data()
    loadedData =json.loads(data)
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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

