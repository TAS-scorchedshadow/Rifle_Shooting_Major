import copy
from datetime import datetime
from time import strftime

import pytest

from app.models import User
from tests.helper_functions.auth_helper import set_club


@pytest.mark.usefixtures("register_users")
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

    def test_profile_post_text(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post(f'/profile_list/{self.club.name}',
                                    data={"user-search": self.student.username, "user": ""},
                                    follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert context["user"] == self.student
        assert template.name == 'profile/profile.html'

    def test_profile_post_text_error(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post(f'/profile_list/{self.club.name}',
                                    data={"user-search": "Not a name", "user": ""},
                                    follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert context["error"] is True
        assert template.name == 'profile/profile_list.html'

    def test_profile_post_card(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post(f'/profile_list/{self.club.name}',
                                    data={"user-search": "", "user": self.student.id},
                                    follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == 'profile/profile.html'


@pytest.mark.usefixtures("register_users")
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

    def test_profile_coach_look_self(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.get('/profile', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]

        assert context["user"] == self.coach

        info = {}
        info["SID"] = self.coach.shooterID
        info["DOB"] = self.coach.dob
        info["Rifle Serial"] = self.coach.rifle_serial
        info["StudentID"] = self.coach.schoolID
        info["Grade"] = self.coach.get_school_year()
        info["Email"] = self.coach.email
        info["Permit"] = self.coach.permitNumber
        info["Expiry"] = self.coach.permitExpiry
        info["Sharing"] = self.coach.sharing
        info["Mobile"] = self.coach.mobile

        assert context["tableInfo"] == info

        assert type(context["error"]) is bool

        assert "start" in context["season_time"]
        datetime.strptime(context["season_time"]["start"], "%d:%m:%Y")
        assert "end" in context["season_time"]

        assert isinstance(context["season_time"]["end"], str)
        datetime.strptime(context["season_time"]["end"], "%d:%m:%Y")

        assert template.name == "profile/profile.html"

    def test_profile_coach_look_other(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        with test_client.session_transaction() as sess:
            sess['profileID'] = self.student.id

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

    def test_profile_coach_post(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.post('/profile', data={"user": self.student.username}, follow_redirects=True)

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

    def test_profile_admin_look_self(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.get('/profile', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]

        assert context["user"] == self.admin

        info = {}
        info["SID"] = self.admin.shooterID
        info["DOB"] = self.admin.dob
        info["Rifle Serial"] = self.admin.rifle_serial
        info["StudentID"] = self.admin.schoolID
        info["Grade"] = self.admin.get_school_year()
        info["Email"] = self.admin.email
        info["Permit"] = self.admin.permitNumber
        info["Expiry"] = self.admin.permitExpiry
        info["Sharing"] = self.admin.sharing
        info["Mobile"] = self.admin.mobile

        assert context["tableInfo"] == info

        assert type(context["error"]) is bool

        assert "start" in context["season_time"]
        datetime.strptime(context["season_time"]["start"], "%d:%m:%Y")
        assert "end" in context["season_time"]

        assert isinstance(context["season_time"]["end"], str)
        datetime.strptime(context["season_time"]["end"], "%d:%m:%Y")

        assert template.name == "profile/profile.html"

    def test_profile_admin_look_other(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        with test_client.session_transaction() as sess:
            sess['profileID'] = self.student.id

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

    def test_profile_admin_post(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post('/profile', data={"user": self.student.username}, follow_redirects=True)

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

    def test_profile_search_error(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post('/profile', data={"user": "Not a name"}, follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]

        assert context["error"] is True

        assert template.name == "profile/profile.html"


def test_get_target_stats_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/get_target_stats' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/get_target_stats')
    assert 405 == response.status_code


def user_assert_helper(user, form):
    # Did not use a getattr() loop as there's special behaviour in the database
    assert user.id == form["userID"]
    assert user.fName == form["fName"]
    assert user.sName == form["sName"]
    assert user.email == form["email"]
    # Update gradYr in the database?
    assert user.gradYr == str(form["gradYr"])
    assert user.mobile == form["mobile"]
    assert user.rifle_serial == form["rifle_serial"]
    assert user.schoolID == form["schoolID"]
    assert user.shooterID == form["shooterID"]
    assert user.permitType == form["permitType"]
    assert user.permitNumber == form["permitNumber"]
    assert user.permitExpiry.strftime("%Y-%m-%d") == form['permitExpiry']


@pytest.mark.usefixtures("register_users")
class TestUpdateUserInfo:

    # This form does not set the target user
    # It will be set individually in each test
    form = {
        "userID": -1,
        "fName": "123x",
        "sName": "Hello",
        "email": "new@gmail.com",
        "gradYr": 2022,
        "mobile": "0403588000",
        "rifle_serial": "new Rifle serial",
        "schoolID": "435921000",
        "shooterID": "Shooter ID",
        "permitType": "P-50",
        "permitNumber": "Hello World",
        "permitExpiry":  datetime.now().strftime("%Y-%m-%d")
    }

    def test_student_self_update(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        form = self.form
        form['userID'] = self.student.id

        r = test_client.post('/update_user_info', data=form, follow_redirects=True)
        assert b"Details Updated Successfully" in r.data
        user_assert_helper(self.student, form)

    def test_student_to_coach_update(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        form = self.form
        form['userID'] = self.coach.id

        r = test_client.post('/update_user_info', data=form, follow_redirects=True)
        assert b"Invalid permissions to edit this user" in r.data

    def test_student_to_admin_update(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        form = self.form
        form['userID'] = self.admin.id

        r = test_client.post('/update_user_info', data=form, follow_redirects=True)
        assert b"Invalid permissions to edit this user" in r.data

    def test_coach_to_admin_update(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        form = self.form
        form['userID'] = self.admin.id

        r = test_client.post('/update_user_info', data=form, follow_redirects=True)
        assert b"Invalid permissions to edit this user" in r.data

    def test_coach_to_other_school_update(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        set_club(self.student, self.club2)
        form = self.form
        form['userID'] = self.student.id

        r = test_client.post('/update_user_info', data=form, follow_redirects=True)
        assert b"Invalid permissions to edit this user" in r.data


@pytest.mark.usefixtures("register_users")
class TestSeasonShotData:
    # This functionality is hard to test from the AJAX route. See unit testing functions for testing on num_shots
    def test_invalid_userID(self, test_client):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })
        start = self.club.season_start.strftime("%d:%m:%Y")
        end = self.club.season_end.strftime("%d:%m:%Y")
        r = test_client.get(f'/profile/get_season_shot_data?start={start}&end={end}&userID={self.student.id}')
        assert r.status_code == 200