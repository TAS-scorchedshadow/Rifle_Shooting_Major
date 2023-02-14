import datetime

import pytest
from flask import url_for

from app.models import Stage
from tests.helper_functions.generate_data import generate_rand_stage


@pytest.mark.usefixtures("register_users")
class TestPlotsheet:
    def test_student_access(self, test_client, captured_templates):

        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        stage = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.datetime.now())
        response = test_client.get(f'/target?stageID={stage.id}', follow_redirects=True)

        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == 'plotsheet/student_plot_sheet.html'

    def test_higher_access(self, test_client, captured_templates):

        users = [[self.coach.username, "coachPass"], [self.admin.username, "adminPass"], [self.dev.username, "devPass"]]
        stage = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.datetime.now())
        for user in users:
            test_client.post('/login', data={
                "username": user[0],
                "password": user[1]
            })

            response = test_client.get(f'/target?stageID={stage.id}', follow_redirects=True)

            assert response.status_code == 200
            template, context = captured_templates[0]
            assert template.name == 'plotsheet/plotsheet.html'

    def test_invalid_stage_id(self, test_client, captured_templates):
        test_client.post('/login', data={
            "username": self.admin.username,
            "password": "adminPass"
        })

        response = test_client.get(f'/target?stageID=-1', follow_redirects=True)
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == 'welcome/index.html'

