from flask import render_template

from app.email import send_email


def send_upload_email(user, stages):
    """
        Sends user an email notifying that the given stages has been uploaded

        :param user: user object
        :param stages: list of stage objects
    """
    send_email('[Riflelytics] New Stages have been uploaded',
               recipients=[user.email],
               text_body=render_template('email/new_stages.txt', user=user, stages=stages),
               html_body=render_template('email/new_stages.html', user=user, stages=stages))
