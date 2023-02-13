import pytest
import json

template_403 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> Page Not Found  | Riflelytics</title>
    <script src="https://kit.fontawesome.com/de048b62de.js" crossorigin="anonymous"></script>
    <link rel="shortcut icon" href="/static/favicon.ico">

    <link rel="stylesheet" type="text/css" href="../static/css/template.css">
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400,700&display=swap" rel="stylesheet"/>
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Play:wght@400;700&display=swap" rel="stylesheet">

    <script src="https://code.jquery.com/jquery-3.5.1.js" integrity="sha256-QWo7LDvxbWT2tbbQ97B53yJnYU3WhH/C8ycbRAkjPDc=" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.min.js" integrity="sha384-w1Q4orYjBQndcko6MimVbzY0tgp4pWB4lZ7lr30WKz0vr/aWKhXdBNmNb5D92v7s" crossorigin="anonymous"></script>

    <script src="../static/htmx/htmx.min.js"></script>
</head>
<body>
    
        <!-- Sidebar  -->
        <nav id="sidebar">
            <ul class="list-unstyled components">
                <li class="sidebar-header" style="padding-left: 5px; padding-right: 2px">
                    <svg class="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 231.1 175.2">
                       <polygon class="logoCol" points="113.9 67.9 153.1 0 74.7 0 113.9 67.9"/>
                       <polygon class="logoCol" points="69.4 13.1 108.6 79 32.6 175 0 138.9 69.4 13.1"/>
                       <polygon class="logoCol" points="158.8 11.6 120.2 79.1 198.6 175.2 231.1 138.1 158.8 11.6"/>
                    </svg>
                    <span class=fnt-play style="display: inline; vertical-align: middle">Riflelytics</span>
                </li>
                
                    
                        <li>
                        <a href="/profile">
                            <i class="fas fa-user"></i>
                            <span>My Profile</span>
                        </a>
                    </li>
                    
                    
                    
                    <li>
                        <a href="/contact">
                            <i class="fas fa-paper-plane"></i>
                            <span>Contact Us</span>
                        </a>
                    </li>
                
                
                    <li>
                        <a href="/logout">
                            <i class="fas fa-sign-out-alt"></i>
                            <span>Sign Out</span>
                        </a>
                    </li>
                
        </ul>
        </nav>

    
        <div id="content">
            <div>
                
                    
                
            </div>

            
    <div class="container-fluid text-center">
        <h1>403 - Forbidden</h1>
        <p>You do not have access to this page</p>
        <p></p>
        <p><a href="/">Back to home</a>
        <p>If you are meant to have access/are having issues please contact <b>riflelytics@gmail.com</b></p>
    </div>

        </div>
    </div>
</body>
</html>"""

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
        response = test_client.post('/get_all_shots_season', json={'distance': '300m', 'userID': self.student.id,
                                                                   'dateRange': 'January 30, 2003 - March 21, 2023'})
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
        response = test_client.get('/api/num_shots_season_all', json={'distance': '300m', 'userID': self.student.id,
                                                                   'dateRange': 'January 30, 2003 - March 21, 2023'})
        assert response.data.decode("utf-8") == template_403

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
        assert response.data.decode("utf-8") != expected

        response = test_client.post('/submit_table', json=[self.student.id, {'email': 'test@example.com'}])
        assert json.loads(response.data.decode("utf-8")) == expected
