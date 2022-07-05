
@pytest.mark.usefixtures("create_users")
class TestIndex:
    def test_submit_notes(self, test_client, captured_templates):
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