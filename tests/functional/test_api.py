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
        response = test_client.post('/submit_notes', json=[self.stage_ids[0], 'You suck at shooting. Just give up already'])

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

    def test_get_names(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_users' page is requested (GET)
        THEN check that the response is valid
        """
        expected = [{'label': 'student (None None)', 'value': 'student'},
                    {'label': 'coach (None None)', 'value': 'coach'}, {'label': 'admin (None None)', 'value': 'admin'}]
        response = test_client.get('/get_names')

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_shots(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_shots' page is requested (GET)
        THEN check that the response is valid
        """
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
        expected = {'error': 'userID'}

        response = test_client.post('/get_target_stats', json=3)

        assert json.loads(response.data.decode("utf-8")) == expected

    def test_get_all_shots_season(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/get_all_shots_season' page is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.post('/get_all_shots_season', json={'distance': '300m', 'userID': self.student.id,
                                                                   'dateRange': 'January 30, 2003 - March 21, 2023'})
        decoded_res = json.loads(response.data.decode("utf-8"))

        assert len(decoded_res['target']) == 50

    def test_submit_table(self, test_client, captured_templates):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/submit_table' page is requested (GET)
        THEN check that the response is valid
        """
        expected = {'success': 'success'}

        response = test_client.post('/submit_table', json=[3, {'email': 'test@example.com'}])
        assert json.loads(response.data.decode("utf-8")) == expected