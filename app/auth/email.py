from flask import render_template

from app.email import send_email


def send_password_reset_email(user):
    """
    Sends an email for users to reset their passwords

    :param user: User requesting for a change in password
    """
    token = user.get_reset_password_token()
    send_email('[Riflelytics] Reset Your Password',
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))


def send_activation_email(user):
    """
    Sends a confirmation email to the newly registered user

    :param user: Newly registered user
    """
    token = user.get_activation_token()
    send_email('Welcome to Riflelytics! Confirm Your Email',
               recipients=[user.email],
               text_body=render_template('email/welcome.txt', user=user, token=token),
               html_body=render_template('email/welcome.html', user=user, token=token))