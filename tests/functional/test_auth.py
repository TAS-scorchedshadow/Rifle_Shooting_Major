import pytest
from flask_login import current_user

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
        assert current_user.is_authenticated is True

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
        assert current_user.is_authenticated is True


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

            # Check that the email was sent with both email templates
            template0, context0 = captured_templates[0]
            template1, context1 = captured_templates[1]
            assert template0.name == "email/welcome.txt"
            assert template1.name == "email/welcome.html"

            # Check flask rendered template
            template2, context2 = captured_templates[2]
            assert template2.name == "auth/register_success.html"

        u = User.query.filter(User.fName == student_data["fName"], User.sName == student_data["sName"],
                              User.gradYr == student_data["gradYr"], User.email == student_data["email"],
                              User.schoolID == student_data["schoolID"], User.shooterID == student_data["shooterID"],
                              User.clubID == student_data["club"]).all()
        assert len(u) == 1
        assert u[0].check_password(student_data["password"]) is True

    def test_register_coach(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/coach_register' page is requested (POST)
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
            response = test_client.post('/coach_register', content_type='multipart/form-data', data=coach_data)

            assert response.status_code == 200
            assert len(outbox) == 1
            assert outbox[0].subject == "Welcome to Riflelytics!"

            # Check that the email was sent with both email templates
            template0, context0 = captured_templates[0]
            template1, context1 = captured_templates[1]
            assert template0.name == "email/welcome.txt"
            assert template1.name == "email/welcome.html"

            # Check flask rendered template
            template2, context2 = captured_templates[2]
            assert template2.name == "auth/coach_register_success.html"

        u = User.query.filter(User.fName == coach_data["fName"], User.sName == coach_data["sName"],
                              User.email == coach_data["email"], User.clubID == coach_data["club"]).all()

        assert len(u) == 1
        assert u[0].check_password(coach_data["password"]) is True
