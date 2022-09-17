import pytest

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

        assert response.status_code == 200
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

        assert response.status_code == 200
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