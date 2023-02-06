import pytest

from app import db
from app.api.api import num_shots
from datetime import datetime, timedelta

from tests.helper_functions.generate_data import generate_rand_stage


@pytest.mark.usefixtures("register_users")
class TestNumShots:
    start_date = datetime(datetime.now().year, 1, 1)
    end_date = datetime(datetime.now().year, 12, 31)

    def test_invalid_userID(self, test_client):
        # Invalid userID -> return 0 on all fields
        r = num_shots(-1, self.start_date, self.end_date)
        assert r["num_sessions"] == 0
        assert r["num_shots"] == 0
        assert r["num_stages"] == 0
        assert r["num_shots_per_session"] == 0

    def test_success(self, test_client):
        n_shots = 10
        n_stages = 20
        for i in range(0, n_stages):
            stage = generate_rand_stage(n_shots, 0, 0, 0.1, 0.1, "300m", datetime.now())
            stage.userID = self.student.id
            db.session.commit()
        r = num_shots(self.student.id, self.start_date, self.end_date)
        assert r["num_sessions"] == 1
        assert r["num_shots"] == n_shots * n_stages
        assert r["num_stages"] == n_stages
        assert r["num_shots_per_session"] == n_shots * n_stages

    def test_sessions(self, test_client):
        n_shots = 10
        n_stages = 20
        time_offset = datetime.now()
        for i in range(0, n_stages):
            stage = generate_rand_stage(n_shots, 0, 0, 0.1, 0.1, "300m", datetime.now())
            time_offset += timedelta(hours=13)
            stage.timestamp = time_offset
            stage.userID = self.student.id
            db.session.commit()
        r = num_shots(self.student.id, self.start_date, self.end_date)
        assert r["num_sessions"] == n_stages
        assert r["num_shots"] == n_shots * n_stages
        assert r["num_stages"] == n_stages
        assert r["num_shots_per_session"] == 10
