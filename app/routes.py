from distutils.util import strtobool

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import uploadForm, signInForm, signUpForm, reportForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.email import send_password_reset_email, send_activation_email
from app.uploadProcessing import validateShots

import numpy
from matplotlib import pylab

import json


@login_required
@app.route('/')
def landingPage():
    return render_template('landingPage.html')


@app.route('/target')
def target_test():
    return render_template('targetTest.html')


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
            for file in files:
                # Decodes a file from FileStorage format into json format, and then extracts relevant info
                try:
                    bytes = file.read()
                    string = bytes.decode('utf-8')
                    data = json.loads(string)
                    shoot = validateShots(data)  # Fixes up file to obtain relevant data and valid shots
                    print(shoot)
                    stageList.append(shoot)
                    # todo: following requires a usernameExists function, or similar
                    # idFound = usernameExists(shoot['username'])
                    # if not idFound:
                    #     invalidList.append(shoot)
                except:
                    print("File had an error in uploading")

    else:
        template = 'landingPage.html'
        stageList = json.loads(request.form["stageDump"])
        shootDefine = {'rifleRange': '', 'distance': '', 'weather': ''}
        shootDefine['rifleRange'] = request.form["rifleRange"]
        shootDefine['distance'] = request.form["distance"]
        shootDefine['weather'] = request.form["weather"]
        print(stageList)
        # todo: if all usernames are correct, handle all the uploading.
        # todo: if not, repeat this page with all settings still intact.
    stageDump = json.dumps(stageList)
    return render_template(template, form=form, stageDump=stageDump, invalidList=invalidList)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landingPage'))
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
            next_page = url_for('landingPage')
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
        return redirect(url_for('landingPage'))
    user = User.verify_activation_token(token)
    if not user:
        return redirect(url_for('landingPage'))
    user.isActive = True
    db.session.commit()
    return render_template('userAuth/resetPassword.html')


@app.route('/requestResetPassword',methods=['GET','POST'])
def requestResetPassword():
    if current_user.is_authenticated:
        return redirect(url_for('landingPage'))
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
        return redirect(url_for('landingPage'))
    user = User.verify_reset_token(token)
    if not user:
        return redirect(url_for('landingPage'))
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
    return redirect(url_for('landingPage'))

