from threading import Thread

from flask import current_app
from flask_mail import Message
from app import mail


# Email functions adapted from examples from Flask-Mail's documentation by Dylan Huynh

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body):
    """
    Sends an email to the relevant recipients

    :param subject: Fills subject of the email
    :param sender: Specifies the creator of the email
    :param recipients: Specifies the address of the emails
    :param text_body: Fills the body of the email
    :param html_body: HTML representation of the email
    :return:
    """
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
# # Dylan Huynh
# def send_report_email(banned_userIDs):
#     """
#     Sends all users an email with the data from the last week. Does not send email to banned users
#
#     :param banned_userIDs: list of user ID to NOT send an email to
#     """
#     users = User.query.all()
#     tsNow = datetime.now()
#     tsBegin = datetime.now() - timedelta(weeks=1)
#     stages = Stage.query.filter(Stage.timestamp.between(tsBegin, tsNow)).all()
#     for user in users:
#         if user.id not in banned_userIDs:
#             userStages = [stage for stage in stages if stage.userID == user.id]
#             if userStages and user.email:
#                 send_email("Weekly Report", [user.email],
#                            render_template('email/weeklyReport.txt', tsBegin=tsBegin, tsNow=tsNow, user=user)
#                            , render_template('email/weeklyReport.html', stages=stages))

