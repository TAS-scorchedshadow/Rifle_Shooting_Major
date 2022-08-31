import datetime as datetime

import pytest
from flask import template_rendered, url_for
from flask_login import login_user

from app import db, mail
from app.models import User, Stage, Club


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

    def test_index_post(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.post('/', data={"user": self.student.username}, follow_redirects=True)

        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == 'profile/profile.html'

    def test_index_post_error(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.coach.username,
            "password": "coachPass"
        })

        response = test_client.post('/', data={"user": "Not a Username"}, follow_redirects=True)

        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert context["error"] is True
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


@pytest.mark.usefixtures("create_users")
class TestContactUs:
    def test_contact_render(self, test_client, captured_templates):
        response = test_client.get('/contact', follow_redirects=True)

        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == 'welcome/contact.html'

    def test_contact_post(self, test_client, captured_templates):
        response = test_client.post('/contact', follow_redirects=True, data={
            'name': self.student.fName,
            'feedback': "Hello"
        })

        assert response.status_code == 200

    def test_contact_email(self, test_client, captured_templates):
        with mail.record_messages() as outbox:
            response = test_client.post('/contact', data={
                'name': self.student.fName,
                'feedback': "Hello"
            })

            assert response.status_code == 302

            assert len(outbox) == 1
            assert outbox[0].subject == "[Riflelytics] Feedback has been sent"

    def test_contact_email_anonymous(self, test_client, captured_templates):
        with mail.record_messages() as outbox:
            response = test_client.post('/contact', data={
                'name': "",
                'feedback': "Hello"
            })

            assert response.status_code == 302

            assert len(outbox) == 1
            assert outbox[0].subject == "[Riflelytics] Feedback has been sent"
