import pytest
import json

@pytest.mark.usefixtures("create_users")
class TestIndex:
    def test_submit_notes(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/submit_notes' page is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.post('/submit_notes', json=[1, 'You suck at shooting. Just give up already'])
        assert json.loads(response.data.decode("utf-8")) == {'success': 'success'}

    def test_get_avg_shot_graph_data(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_avg_shot_graph_data' page is requested (GET)
        THEN check that the response is valid
        """
        expected = {'scores': [], 'times': [], 'sd': []}
        response = test_client.post('/get_avg_shot_graph_data', json=3)

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_users(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_users' page is requested (GET)
        THEN check that the response is valid
        """
        expected = [{'label': 'student (None None)', 'value': 'student'},
                    {'label': 'coach (None None)', 'value': 'coach'}, {'label': 'admin (None None)', 'value': 'admin'}]
        response = test_client.post('/get_users')

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_shots(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_shots' page is requested (GET)
        THEN check that the response is valid
        """
        expected = {'scores': [], 'totalScore': '0', 'groupSize': 330, 'distance': '300m', 'timestamp': '', 'std': 0,
                    'duration': 399, 'stageId': 0, 'sighters': []}
        response = test_client.post('/get_shots', json=[0, 0, "30th January 2003 - 21st March 2020"])

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_target_stats(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_target_stats' page is requested (GET)
        THEN check that the response is valid
        """
        expected = {'error': 'userID'}

        response = test_client.post('/get_target_stats', json=3)

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_all_shots_season(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_all_shots_season' page is requested (GET)
        THEN check that the response is valid
        """
        expected = {'target': [], 'boxPlot': [], 'bestStage': {'id': 0, 'score': 50, 'time': '30th January 2003'},
                    'worstStage': {'id': 0, 'score': 0, 'time': '30th January 2003'}
                    }

        response = test_client.post('/get_all_shots_season', data={'distance': '300m', 'userID': 0,
                                                                   'dateRange': '30th January 2003'})
        assert json.loads(response.data.decode("utf-8")) == expected

    def test_submit_table(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/submit_table' page is requested (GET)
        THEN check that the response is valid
        """
        expected = {'success': 'success'}

        response = test_client.post('/submit_table', json=[3, {'email': 'test@example.com'}])
        assert json.loads(response.data.decode("utf-8")) == expected