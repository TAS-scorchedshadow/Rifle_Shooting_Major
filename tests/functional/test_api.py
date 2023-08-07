import datetime

import pytest
import json

@pytest.mark.usefixtures("api_setup")
class TestApi:
    def test_submit_notes(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/submit_notes' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })
        response = test_client.post('/submit_notes',
                                    json=[self.stage_ids[0], 'You suck at shooting. Just give up already'])

        assert json.loads(response.data.decode("utf-8")) == {'success': 'success'}

    def test_get_avg_shot_graph_data(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_avg_shot_graph_data' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })
        expected = {'scores': [], 'times': [], 'sd': []}
        response = test_client.post('/get_avg_shot_graph_data', json=3)

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_names(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_users' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })
        expected = [{'label': 'student (None None)', 'value': 'student'},
                    {'label': 'coach (None None)', 'value': 'coach'},
                    {'label': 'dev (None None)', 'value': 'dev'},
                    {'label': 'admin (None None)', 'value': 'admin'}]
        response = test_client.get('/get_names')

        assert json.loads(response.data.decode("utf-8")) == expected

        # Test incorrect club


    def test_get_shots(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_shots' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })
        response = test_client.post('/get_shots', json=[self.student.id, 0, "January 30, 2003 - March 21, 2023"])
        response_list = json.loads(response.data.decode("utf-8"))
        for stage in response_list:
            assert len(stage['scores']) == 10

    def test_get_target_stats(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_target_stats' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })
        expected = {'error': 'userID'}

        response = test_client.post('/get_target_stats', json=3)

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_all_shots_season(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_all_shots_season' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })

        startDate = datetime.datetime.now() - datetime.timedelta(days=30)
        endDate = datetime.datetime.now() + datetime.timedelta(days=30)

        dateRange = f'{startDate.strftime("%B %d, %Y")} - {endDate.strftime("%B %d, %Y")}'
        print(dateRange)
        response = test_client.post('/get_all_shots_season', json={'distance': '300m', 'userID': self.student.id,
                                                                   'dateRange': dateRange})
        decoded_res = json.loads(response.data.decode("utf-8"))

        assert len(decoded_res['target']) == 50

    def test_get_all_shots_season_all(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_all_shots_season' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })
        response = test_client.get('/api/num_shots_season_all', json={'distance': '300m', 'userID': self.student.id})
        assert response.status_code == 403

    def test_submit_table(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/submit_table' page is requested (GET)
        THEN check that the response is valid
        """
        test_client.post('/login', data={
            "username": self.student.username,
            "password": "studentPass"
        })
        expected = {'success': 'success'}

        response = test_client.post('/submit_table', json=[3, {'email': 'test@example.com'}])
        assert response.status_code == 403

        response = test_client.post('/submit_table', json=[self.student.id, {'email': 'test@example.com'}])
        assert json.loads(response.data.decode("utf-8")) == expected
        assert response.status_code == 200
