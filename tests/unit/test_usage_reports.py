import json
import os
from datetime import datetime, timedelta

import pytest

from app import db
from app.models import Stage
from tests.helper_functions.generate_data import generate_rand_stage
from usage_reports.report import generate_usage_report


@pytest.mark.usefixtures("register_users")
class TestUsageReports:

    def test_bad_inputs(self, test_client):
        for i in range(1, 10):
            stage = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.strptime(f"2022-{i}-{i}", "%Y-%m-%d"))
            stage.userID = self.student.id

            stage2 = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.strptime(f"2022-{i}-{i}", "%Y-%m-%d") +
                                         timedelta(hours=3))
            stage2.userID = self.coach.id
        db.session.commit()

        with pytest.raises(ValueError):
            generate_usage_report(self.club.name, "2022-10-10", "2022-01-01", 5)

        with pytest.raises(ValueError):
            generate_usage_report(self.club.name, "2022-01-01", "2022-31-01", 5)


    def test_one_school(self, test_client):
        for i in range(1, 10):
            stage = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.strptime(f"2022-{i}-{i}", "%Y-%m-%d"))
            stage.userID = self.student.id

            stage2 = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.strptime(f"2022-{i}-{i}", "%Y-%m-%d") +
                                         timedelta(hours=3))
            stage2.userID = self.coach.id
        db.session.commit()

        generate_usage_report(self.club.name, "2022-01-01", "2022-10-10", 5)

        filename = f"{self.club.name} 2022-01-01 to 2022-10-10.txt"
        # Breaks here if filename is incorrect
        f = open(filename)

        data = json.load(f)
        assert len(data["active_users"]) == data["club_info"]["num_active_users"]
        assert data["club_info"]["num_active_users"] == 2
        assert data["active_users"][0]["username"] == self.student.username
        assert data["active_users"][1]["username"] == self.coach.username

        assert len(data["inactive_users"]) == data["club_info"]["num_inactive_users"]
        assert data["club_info"]["num_inactive_users"] == 1
        assert data["inactive_users"][0]["username"] == self.admin.username

        f.close()
        os.remove(filename)

    def test_two_schools(self, test_client):
        for i in range(1, 10):
            stage = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.strptime(f"2022-{i}-{i}", "%Y-%m-%d"))
            stage.userID = self.student.id

            stage2 = generate_rand_stage(10, 0, 0, 0.1, 0.1, "300m", datetime.strptime(f"2022-{i}-{i}", "%Y-%m-%d") +
                                         timedelta(hours=3))
            stage2.userID = self.coach.id
            self.coach.clubID = self.club2.id
        db.session.commit()

        generate_usage_report(self.club.name, "2022-01-01", "2022-10-10", 5)

        filename = f"{self.club.name} 2022-01-01 to 2022-10-10.txt"
        # Breaks here if filename is incorrect
        f = open(filename)

        data = json.load(f)
        assert len(data["active_users"]) == data["club_info"]["num_active_users"]
        assert data["club_info"]["num_active_users"] == 1
        assert data["active_users"][0]["username"] == self.student.username

        assert len(data["inactive_users"]) == data["club_info"]["num_inactive_users"]
        assert data["club_info"]["num_inactive_users"] == 1
        assert data["inactive_users"][0]["username"] == self.admin.username

        f.close()
        os.remove(filename)