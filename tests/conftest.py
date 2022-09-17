import datetime as datetime

import pytest as pytest
from dateutil.relativedelta import relativedelta
from flask import template_rendered
from flask_login import login_user

from app import create_app, db
from tests.helper_functions.auth_helper import register_user, set_access
from tests.helper_functions.generate_data import generate_rand_stage
from app.models import User, Club
from config import Config

# Is subclass of Config by Flask
class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    FORCE_HTTPS = False
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
def create_club(request, test_client):
    start = datetime.datetime.now()
    end = datetime.datetime.now()
    club = Club(name="SBHS", season_start=start, season_end=end)
    db.session.add(club)
    if request.cls:
        request.cls.club = club

@pytest.fixture
def register_users(request, test_client):

    start = datetime.datetime.now()
    end = datetime.datetime.now()

    club = Club(name="SBHS", season_start=start, season_end=end)
    db.session.add(club)
    request.cls.club = club

    club2 = Club(name="SCOTS", season_start=start, season_end=end)
    db.session.add(club2)
    request.cls.club2 = club2

    db.session.commit()


    student_data = {
        "fName": "Henry",
        "sName": "Guo",
        "school": club.name,
        "gradYr": 2024,
        "schoolID": "435921000",
        "shooterID": "Xaw-423",
        "password": "studentPass",
        "confirmPassword": "studentPass"
    }
    register_user(student_data, test_client)
    u = User.query.filter_by(fName=student_data["fName"]).first()
    request.cls.student = u

    coach_data = {
        "fName": "Jeffery",
        "sName": "Lee",
        "school": club.name,
        "gradYr": 2022,
        "schoolID": "asdE2sa",
        "shooterID": "Xasx-423",
        "password": "coachPass",
        "confirmPassword": "coachPass"
    }
    #TODO: If we have a seperate coach registeration, switch the register route
    register_user(coach_data, test_client)
    u = User.query.filter_by(fName=coach_data["fName"]).first()
    set_access(u, 1)
    request.cls.coach = u

    #TODO: If we have a seperate admin registration, switch this out
    admin = User(username="admin")
    admin.set_password("adminPass")
    admin.access = 2
    admin.fName = "Richard"
    admin.sName = "Smith"
    admin.clubID = club.id
    db.session.add(admin)
    request.cls.admin = admin
    request.cls.admin.password = "adminPass"

    dev = User(username="dev")
    dev.set_password("devPass")
    dev.access = 3
    dev.fName = "Dev"
    dev.sName = "Account"
    db.session.add(dev)
    request.cls.dev = dev
    request.cls.admin.password = "adminPass"

@pytest.fixture
def create_users(request, test_client):
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

    dev = User(username="dev")
    dev.set_password("devPass")
    dev.access = 3
    dev.fName = "Dev"
    dev.sName = "Account"
    db.session.add(dev)
    request.cls.dev = dev

    start = datetime.datetime.now()
    end = datetime.datetime.now()
    settings = Club(id=0, email_setting=0, season_start=start, season_end=end)
    db.session.add(settings)
    request.cls.settings = settings

    db.session.commit()

@pytest.fixture
def api_setup(request, test_client):
    db.drop_all()
    db.create_all()
    student = User(username="student")
    student.set_password("studentPass")
    student.access = 0
    db.session.add(student)
    request.cls.student = student

    coach = User(username="coach")
    coach.set_password("coachPass")
    coach.access = 1
    db.session.add(coach)
    request.cls.coach = coach

    admin = User(username="admin")
    admin.set_password("adminPass")
    admin.access = 2
    db.session.add(admin)
    request.cls.admin = admin

    start = datetime.datetime.now()
    end = datetime.datetime.now()
    settings = Club(id=0, email_setting=0, season_start=start, season_end=end)
    db.session.add(settings)
    request.cls.settings = settings
    db.session.commit()

    request.cls.stage_ids = []
    for i in list(range(5)):
        new_stage = generate_rand_stage(10, 0, 0, 0.1, 0.1, '300m')
        new_stage.userID = student.id
        request.cls.stage_ids.append(new_stage.id)
    db.session.commit()

