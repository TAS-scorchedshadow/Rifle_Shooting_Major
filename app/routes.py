from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import uploadForm, signInForm, signUpForm, reportForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.email import send_password_reset_email

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
    return render_template('students/profile.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = uploadForm()
    if request.method == "POST":
        files = request.files.getlist('file')
        for file in files:
            # Decodes a file from FileStorage format into json format.
            bytes = file.read()
            string = bytes.decode('utf-8')
            info = json.loads(string)
            print(info)
            print(info["_id"])
            # todo: files are not passed through the redirect, pass it through *then* do processing
        return redirect(url_for('uploadV'))
    return render_template('upload/upload.html', form=form)


@app.route('/upload2', methods=['GET', 'POST'])
def uploadV():
    form = uploadForm()
    stageList = ['1', '2', '4', '2', '3', '1', '2', 2, 1, 1, 2, 3, 12, 31, 123]
    if request.method == "POST":
        return render_template('landingPage.html')
    return render_template('upload/uploadVerify.html', form=form, stageList=stageList)


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
    return render_template('UserAuth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = signUpForm()
    if form.validate_on_submit():
        user = User(fName=form.fName.data, sName=form.sName.data,school=form.school.data,schoolID=form.schoolID.data)
        user.generate_username()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!','success')
        return redirect(url_for('login'))
    return render_template('UserAuth/register.html', title='Register', form=form)


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
    return render_template('UserAuth/requestResetPassword.html',form=form)


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
    return render_template('UserAuth/resetPassword.html',form=form)

@app.route('/userList')
def userList():
    users = User.query.all()
    return render_template('UserAuth/userList.html',users=users)




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landingPage'))

