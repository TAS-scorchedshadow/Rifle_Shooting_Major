import pytest

from app import mail
from app.models import User

@pytest.mark.usefixtures("register_users")
class TestLogin:
    def test_login_student(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        response = test_client.get('/', follow_redirects=True)

        assert response.status_code == 200

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == 'profile/profile.html'

    def test_login_regular(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.get('/', follow_redirects=True)

        assert response.status_code == 200

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == 'welcome/index.html'


@pytest.mark.usefixtures("create_club")
class TestRegister:
    def test_register_student(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/register' page is requested (POST)
        THEN check that the response is valid
        """

        student_data = {
            "fName": "Henry",
            "sName": "Guo",
            "school": self.club.name,
            "gradYr": 2024,
            "schoolID": "435921000",
            "shooterID": "Xaw-423",
            "email": "test@test.com",
            "password": "studentPass",
            "confirmPassword": "studentPass",
            "club": self.club.id,
        }

        with mail.record_messages() as outbox:
            response = test_client.post('/register', content_type='multipart/form-data', data=student_data)

            assert response.status_code == 200
            assert len(outbox) == 1
            assert outbox[0].subject == "Welcome to Riflelytics!"

        u = User.query.filter_by(fName=student_data["fName"]).first()
        assert u is not None

    def test_register_coach(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/coachRegister' page is requested (POST)
        THEN check that the response is valid
        """
        coach_data = {
            "fName": "Dylan",
            "sName": "Huynh",
            "email": "test@test.com",
            "password": "studentPass",
            "confirmPassword": "studentPass",
            "club": self.club.id,
        }

        with mail.record_messages() as outbox:
            response = test_client.post('/register', content_type='multipart/form-data', data=coach_data)

            assert response.status_code == 200
            assert len(outbox) == 1
            assert outbox[0].subject == "Welcome to Riflelytics!"
            u = User.query.filter_by(fName=coach_data["fName"]).first()

            assert u is not None