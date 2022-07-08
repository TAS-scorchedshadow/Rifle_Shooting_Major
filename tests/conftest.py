import datetime as datetime

import pytest as pytest
from dateutil.relativedelta import relativedelta
from flask import template_rendered
from flask_login import login_user

from app import create_app, db
from app.models import User, Settings
from config import Config


# Is subclass of Config by Flask
class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///"


@pytest.fixture(scope='session')
def flask_app():
    flask_app = create_app(TestingConfig)
    yield flask_app

@pytest.fixture
def test_client(flask_app):
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            from app import db
            db.create_all()
            yield testing_client  # this is where the testing happens!
            db.drop_all()

@pytest.fixture
def captured_templates(flask_app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, flask_app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, flask_app)


@pytest.fixture
def create_users(request, test_client):
    db.drop_all()
    db.create_all()
    student = User(username="student")
    student.set_password("studentPass")
    student.access = 0

    # Set example data for the user
    student.fName = "Henry"
    student.sName = "Guo"

    student.shooterID = 1012
    student.dob = datetime.datetime.now() - relativedelta(years=18)
    student.rifle_serial = "ASC2x1"
    student.schoolID = "435921302"
    student.gradYr = "2027"
    student.email = "henry.guo@gmail.com"
    student.permitNumber = "323131"
    student.permitExpiry = datetime.datetime.now() + relativedelta(years=1)
    student.mobile = "1111 111 111"

    db.session.add(student)
    request.cls.student = student

    coach = User(username="coach")
    coach.set_password("coachPass")
    coach.access = 1
    coach.fName = "John"
    coach.sName = "Jeff"
    db.session.add(coach)
    request.cls.coach = coach

    admin = User(username="admin")
    admin.set_password("adminPass")
    admin.access = 2
    admin.fName = "Richard"
    admin.sName = "Smith"
    db.session.add(admin)
    request.cls.admin = admin

    start = datetime.datetime.now()
    end = datetime.datetime.now()
    settings = Settings(id=0,email_setting=0,season_start=start,season_end=end)
    db.session.add(settings)
    request.cls.settings = settings


    db.session.commit()

