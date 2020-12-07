from urllib import request

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app
from app.forms import uploadForm, signInForm, reportForm
from app.models import User


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
        return redirect(url_for('uploadV'))
    return render_template('upload/upload.html', form=form)


@app.route('/upload2')
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
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != ':':
            next_page = url_for('landingPage')
        return redirect(next_page)
    return render_template('UserAuth/login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landingPage'))

