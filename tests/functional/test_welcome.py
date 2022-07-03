import datetime as datetime

import pytest
from flask import template_rendered, url_for
from flask_login import login_user

from app import db
from app.models import User, Stage, Settings

@pytest.mark.usefixtures("create_users")
class TestIndex:
    def test_index_unauthorised(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """

        response = test_client.get('/', follow_redirects=True)


        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == 'welcome/landing_page.html'

    def test_index_student(self, test_client, captured_templates):
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

    def test_index_regular(self, test_client, captured_templates):
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


def test_landing(test_client, captured_templates):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/landing' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/landing')
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "welcome/landing_page.html"

