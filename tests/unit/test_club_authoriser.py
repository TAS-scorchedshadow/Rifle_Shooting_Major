import pytest
from flask_login import current_user

from app.decorators import is_authorised
from tests.helper_functions.auth_helper import set_club


@pytest.mark.usefixtures("register_users")
class TestIsAuthorised:

    def test_auth_student(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        assert is_authorised(self.club, "STUDENT") is True
        assert is_authorised(self.club, "COACH") is False
        assert is_authorised(self.club, "ADMIN") is False
        assert is_authorised(self.club, "DEV") is False

        set_club(self.student, self.club2)

        assert is_authorised(self.club, "STUDENT") is False
        assert is_authorised(self.club, "COACH") is False
        assert is_authorised(self.club, "ADMIN") is False
        assert is_authorised(self.club, "DEV") is False


    def test_auth_coach(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        assert is_authorised(self.club, "STUDENT") is True
        assert is_authorised(self.club, "COACH") is True
        assert is_authorised(self.club, "ADMIN") is False
        assert is_authorised(self.club, "DEV") is False

        set_club(self.coach, self.club2)

        assert is_authorised(self.club, "STUDENT") is False
        assert is_authorised(self.club, "COACH") is False
        assert is_authorised(self.club, "ADMIN") is False
        assert is_authorised(self.club, "DEV") is False

    def test_auth_admin(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        assert is_authorised(self.club, "STUDENT") is True
        assert is_authorised(self.club, "COACH") is True
        assert is_authorised(self.club, "ADMIN") is True
        assert is_authorised(self.club, "DEV") is False

        set_club(self.admin, self.club2)

        assert is_authorised(self.club, "STUDENT") is False
        assert is_authorised(self.club, "COACH") is False
        assert is_authorised(self.club, "ADMIN") is False
        assert is_authorised(self.club, "DEV") is False

    def test_auth_dev(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.dev.username,
            "password": "devPass"
        })

        assert current_user.clubID != self.club.id
        assert is_authorised(self.club, "STUDENT") is True
        assert is_authorised(self.club, "COACH") is True
        assert is_authorised(self.club, "ADMIN") is True
        assert is_authorised(self.club, "DEV") is True

        set_club(self.dev, self.club)

        assert current_user.clubID is self.club.id
        assert is_authorised(self.club, "STUDENT") is True
        assert is_authorised(self.club, "COACH") is True
        assert is_authorised(self.club, "ADMIN") is True
        assert is_authorised(self.club, "DEV") is True
