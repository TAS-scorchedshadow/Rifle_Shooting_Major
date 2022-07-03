
def test_get_target_stats_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/get_target_stats' page is requested (GET)
    THEN check that the response is valid
    """
    data = '0'
    response = test_client.get('/get_target_stats')
    assert 405 == response.status_code
