from flask import Blueprint, redirect, url_for, flash, request, render_template, abort
from flask_login import current_user, login_user, logout_user
from flask import session as flask_session
from flask_wtf.csrf import generate_csrf
from werkzeug.urls import url_parse

from app import db
from app.models import User, Club

from .forms import signInForm, signUpForm, CoachSignUpForm, ResetPasswordRequestForm, ResetPasswordForm
from .email import send_activation_email, send_password_reset_email


auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Allows the user to log on to the system

    :return: Login page
    """
    if current_user.is_authenticated:
        return redirect(url_for('welcome_bp.index'))
    form = signInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth_bp.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != ':':
            next_page = url_for('welcome_bp.index')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)

# Dylan Huynh
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET route displays registration form, POST route generates a new user object and uploads it to the database

    :return:
    """
    form = signUpForm()
    if form.validate_on_submit():
        # TODO: Graduation year can't be none (integerField passively has InputRequired validator)
        email = form.email.data
        user = User(fName=form.fName.data.strip().lower().title(), sName=form.sName.data.strip().lower().title(),
                    schoolID=form.schoolID.data, email=email, gradYr=str(form.gradYr.data))
        user.generate_username()
        user.set_password(form.password.data)
        user.clubID = int(request.form['club'])
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        flash('Congratulations, you are now a registered user!', 'success')
        return render_template('auth/register_success.html', user=user)
    clubList = [{'name': club.name, 'id': club.id} for club in Club.query.all()]
    error = form.errors
    return render_template('auth/register.html', title='Register', form=form, clubList=clubList)


@auth_bp.route('/coachRegister', methods=['GET', 'POST'])
def coach_register():
    form = CoachSignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User(fName=form.fName.data.strip().lower().title(), sName=form.sName.data.strip().lower().title(),
                    email=email, gradYr='-1', schoolID=0)
        user.generate_username()
        user.set_password(form.password.data)
        user.clubID = int(request.form['club'])
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        flash('Congratulations, you are now a registered user!', 'success')
        return render_template('auth/coach_register_success.html', user=user)
    clubList = [{'name': club.name, 'id': club.id} for club in Club.query.all()]
    return render_template('auth/coach_register.html', title='Register', form=form, clubList=clubList)


@auth_bp.route('/logout')
def logout():
    """
    Allows users to exit from the system
    """
    logout_user()
    return redirect(url_for('welcome_bp.index'))


# By Dylan Huynh
@auth_bp.route('/request_reset_password', methods=['GET', 'POST'])
def request_reset_password():
    """
    Requesting a password reset if account details forgotten

    :return: Reset password html page
    """
    if current_user.is_authenticated:
        return redirect(url_for('welcome_bp.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Password reset email sent successfully', "success")
        return redirect(url_for('auth_bp.login'))
    return render_template('auth/request_reset_password.html', form=form)


# By Dylan Huynh
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Requesting a password reset if account details forgotten

    :return: Reset password html page
    """
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid password reset token. Please try again.', 'error')
        return redirect(url_for('auth_bp.request_reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password was successfully reset', 'success')
        return redirect(url_for('auth_bp.login'))
    return render_template('auth/reset_password.html', form=form)
