from datetime import datetime, date

import pytest
from flask import url_for


@pytest.mark.usefixtures("create_users")
class TestProfileList:
    def test_profile_list_unauthorised(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        response = test_client.get('/profile_list', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name != 'profile/profile_list.html'

    def test_profile_list_student(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        response = test_client.get('/profile_list', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name != 'profile/profile_list.html'

    def test_profile_list_coach(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.get('/profile_list', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == 'profile/profile_list.html'

    def test_profile_list_admin(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.get('/profile_list', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == 'profile/profile_list.html'


@pytest.mark.usefixtures("create_users")
class TestProfile:
    def test_profile_unauthorised(self, test_client, captured_templates):

        response = test_client.get('/profile', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name != "profile/profile.html"
        assert template.name == "auth/login.html"

    def test_profile_student(self, test_client, captured_templates):

        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        response = test_client.get('/profile', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]

        assert context["user"] == self.student

        info = {}
        info["SID"] = self.student.shooterID
        info["DOB"] = self.student.dob
        info["Rifle Serial"] = self.student.rifle_serial
        info["StudentID"] = self.student.schoolID
        info["Grade"] = self.student.get_school_year()
        info["Email"] = self.student.email
        info["Permit"] = self.student.permitNumber
        info["Expiry"] = self.student.permitExpiry
        info["Sharing"] = self.student.sharing
        info["Mobile"] = self.student.mobile

        assert context["tableInfo"] == info

        assert type(context["error"]) is bool

        assert "start" in context["season_time"]
        datetime.strptime(context["season_time"]["start"], "%d:%m:%Y")
        assert "end" in context["season_time"]

        assert isinstance(context["season_time"]["end"], str)
        datetime.strptime(context["season_time"]["end"], "%d:%m:%Y")


        assert template.name == "profile/profile.html"

def test_get_target_stats_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/get_target_stats' page is requested (GET)
    THEN check that the response is valid
    """
    data = '0'
    response = test_client.get('/get_target_stats')
    assert 405 == response.status_code
