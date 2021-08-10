from datetime import datetime, timedelta

from flask import render_template
from flask_mail import Message
from app import app, mail
from app.models import User, Stage
# Email functions adapted from examples from Flask-Mail's documentation by Dylan Huynh

def send_email(subject ,recipients, text_body, html_body):
    """
    Sends an email to the relevant recipients

    :param subject: Fills subject of the email
    :param sender: Specifies the creator of the email
    :param recipients: Specifies the address of the emails
    :param text_body: Fills the body of the email
    :param html_body: HTML representation of the email
    :return:
    """
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    """
    Sends an email for users to reset their passwords

    :param user: User requesting for a change in password
    """
    token = user.get_reset_password_token()
    send_email('[Riflelytics] Reset Your Password',
               recipients=[user.email],
               text_body=render_template('email/resetPassword.txt', user=user, token=token),
               html_body=render_template('email/resetPassword.html', user=user, token=token))

def send_activation_email(user):
    """
    Sends a confirmation email to the newly registered user

    :param user: Newly registered user
    """
    token = user.get_activation_token()
    send_email('Welcome to Riflelytics! Confirm Your Email',
               recipients=[user.email],
               text_body=render_template('email/activate.txt', user=user, token=token),
               html_body=render_template('email/activate.html', user=user, token=token))

# Dylan Huynh
def send_report_email(banned_userIDs):
    """
    Sends all users an email with the data from the last week. Does not send email to banned users

    :param banned_userIDs: list of user ID to NOT send an email to
    """
    users = User.query.all()
    tsNow = datetime.now()
    tsBegin = datetime.now() - timedelta(weeks=1)
    stages = Stage.query.filter(Stage.timestamp.between(tsBegin, tsNow)).all()
    for user in users:
        if user.id not in banned_userIDs:
            userStages = [stage for stage in stages if stage.userID == user.id]
            if userStages and user.email:
                send_email("Weekly Report",[user.email],render_template('email/weeklyReport.txt',tsBegin=tsBegin,tsNow=tsNow, user=user)
                           ,render_template('email/weeklyReport.html', stages=stages))