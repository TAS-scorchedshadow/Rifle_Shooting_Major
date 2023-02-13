from datetime import datetime
import json

import pytest

from app.models import Club, User
from tests.helper_functions.auth_helper import set_club


@pytest.mark.usefixtures("register_users")
class TestUserList:
    def test_user_list_unauthorised(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        response = test_client.get('/user_list', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name != 'admin/user_list.html'

    def test_user_list_student(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        set_club(self.student, self.club)

        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        response = test_client.get('/user_list', follow_redirects=True)

        assert response.status_code == 403
        template, context = captured_templates[0]
        assert template.name != 'admin/user_list.html'

    def test_user_list_coach(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        set_club(self.coach, self.club)

        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.get('/user_list', follow_redirects=True)

        assert response.status_code == 403
        template, context = captured_templates[0]
        assert template.name != 'admin/user_list.html'

    def test_user_list_admin(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        set_club(self.admin, self.club)

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.get('/user_list', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == 'admin/user_list.html'

@pytest.mark.usefixtures("register_users")
class TestMakeAdmin:
    def test_invalid_uID(self, test_client):

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, self.club)

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": -1
        }))

        assert response.status_code == 400

    def test_invalid_club(self, test_client):

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, Club(id=-1))

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 400

    def test_edit_different_club(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, self.club)
        set_club(self.student, self.club2)

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 403

    def test_invalid_access_coach(self, test_client):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        set_club(self.coach, self.club)
        set_club(self.student, self.club)

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 403

    def test_invalid_access_student(self, test_client):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        set_club(self.student, self.club)
        set_club(self.student, self.club)

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 403

    def test_invalid_access_student(self, test_client):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        set_club(self.student, self.club)
        set_club(self.coach, self.club)

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": self.coach.id
        }))

        assert response.status_code == 403 or "403 FORBIDDEN"

    def test_student_to_coach(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        assert self.student.access == 0

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 200
        assert json.loads(response.data)['access_lvl'] == 1
        assert self.student.access == 1

    def test_coach_to_student(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        assert self.coach.access == 1

        response = test_client.post('/make_admin', data=json.dumps({
            "userID": self.coach.id
        }))

        assert response.status_code == 200
        assert json.loads(response.data)['access_lvl'] == 0
        assert self.coach.access == 0

@pytest.mark.usefixtures("register_users")
class TestDeleteAccount:
    def test_invalid_uID(self, test_client):

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, self.club)

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": -1
        }))

        assert response.status_code == 400

    def test_invalid_club(self, test_client):

        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, Club(id=-1))

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 400

    def test_edit_different_club(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, self.club)
        set_club(self.student, self.club2)

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 403

    def test_invalid_access_coach(self, test_client):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        set_club(self.coach, self.club)
        set_club(self.student, self.club)

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 403

    def test_invalid_access_student(self, test_client):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        set_club(self.student, self.club)
        set_club(self.student, self.club)

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 403

    def test_delete_student(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        assert self.student.access == 0

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.student.id
        }))

        assert response.status_code == 200
        assert User.query.filter_by(id=self.student.id).first() is None
        print(User.query.all())

    def test_delete_coach(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.coach.id
        }))

        assert response.status_code == 200
        assert User.query.filter_by(id=self.coach.id).first() is None

    def test_delete_admin(self, test_client):
        # Yes the admin can delete themselves, need to discuss if this is the intended behaviour
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.admin.id
        }))

        assert response.status_code == 200
        assert User.query.filter_by(id=self.admin.id).first() is None

    def test_delete_dev(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post('/delete_account', data=json.dumps({
            "userID": self.dev.id
        }))

        assert response.status_code == 403

@pytest.mark.usefixtures("register_users")
class TestUpdateSeasonDate:
    start = datetime(datetime.today().year, 1, 5)
    end = datetime(datetime.today().year, 12, 12)
    dates = "{} - {}".format(start.strftime("%B %d, %Y"),end.strftime("%B %d, %Y"))
    dates_reversed = "{} - {}".format(end.strftime("%B %d, %Y"), start.strftime("%B %d, %Y"))

    def test_invalid_club(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, Club(id=-1))

        response = test_client.post('/update_season_date', data=json.dumps({
            "date_range": self.dates,
            "clubID": self.club.id
        }))

        assert response.status_code == 400

    def test_student_invalid(self, test_client):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        response = test_client.post('/update_season_date', data=json.dumps({
            "date_range": self.dates,
            "clubID": self.club.id
        }))

        assert response.status_code == 403

    def test_coach_invalid(self, test_client):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        response = test_client.post('/update_season_date', data=json.dumps({
            "date_range": self.dates,
            "clubID": self.club.id
        }))

        assert response.status_code == 403

    def test_date_out_of_order(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post('/update_season_date', data=json.dumps({
            "date_range": self.dates_reversed,
            "clubID": self.club.id
        }))

        assert response.status_code == 400

    def test_valid_edit(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.post('/update_season_date', data=json.dumps({
            "date_range": self.dates,
            "clubID": self.club.id
        }))

        assert response.status_code == 200
        assert self.club.season_start == self.start
        assert self.club.season_end == self.end

@pytest.mark.usefixtures("register_users")
class TestEmailSettings:
    def test_invalid_club(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        set_club(self.admin, Club(id=-1))

        response = test_client.post('/email_settings', data=json.dumps({
            "email_setting": "0",
        }))

        assert response.status_code == 400

    def test_invalid_student(self, test_client):
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        response = test_client.post('/email_settings', data=json.dumps({
            "email_setting": "0",
        }))

        assert response.status_code == 403

    def test_invalid_coach(self, test_client):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.post('/email_settings', data=json.dumps({
            "email_setting": "0",
        }))

        assert response.status_code == 403

    def test_valid_edit(self, test_client):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        email_settings = ["0", "2"]
        for element in email_settings:
            response = test_client.post('/email_settings', data=json.dumps({
                "email_setting": element,
            }))

            assert response.status_code == 200
            assert self.club.email_setting == int(element)
