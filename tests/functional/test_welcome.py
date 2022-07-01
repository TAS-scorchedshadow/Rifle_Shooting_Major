import pytest
from flask_login import login_user

from app import db
from app.models import User
from flask_testing import TestCase


@pytest.fixture(scope="class")
def create_users(request, test_client):
    db.drop_all()
    db.create_all()
    student = User(username="student")
    student.set_password("coachPass")
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

    db.session.commit()


@pytest.mark.usefixtures("create_users")
class TestRoutes:
    def test_index(self, test_client):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.get('/', follow_redirects=True)
        assert response.status_code == 200
        login_user(self.student)
        response = test_client.get('/', follow_redirects=True)

    def test_landing(self, test_client):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/landing' page is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.get('/landing')
        assert response.status_code == 200
        self.assert_template_used('landing.html')
