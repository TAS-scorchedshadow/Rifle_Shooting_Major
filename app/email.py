from flask import render_template
from flask_mail import Message
from app import app, mail


def send_email(subject ,recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[PARS] Reset Your Password',
               recipients=[user.email],
               text_body=render_template('email/resetPassword.txt', user=user, token=token),
               html_body=render_template('email/resetPassword.html', user=user, token=token))

def send_activation_email(user):
    token = user.get_activation_token()
    send_email('Welcome to PARS! Confirm Your Email',
               recipients=[user.email],
               text_body=render_template('email/activate.txt', user=user, token=token),
               html_body=render_template('email/activate.html', user=user, token=token))
