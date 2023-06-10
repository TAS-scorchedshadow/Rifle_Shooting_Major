from flask import render_template

from app.email import send_email


def send_feedback_email(text, sender):
    """
        Sends feedback to riflelytics@gmail.com

        :param text: feedback text
        :param sender: string of sender name
    """
    send_email('[Riflelytics] Feedback has been sent',
               recipients=["contact@riflelytics.com"],
               text_body=render_template('email/feedback.txt', text=text, sender=sender),
               html_body=render_template('email/feedback.html', text=text, sender=sender))
