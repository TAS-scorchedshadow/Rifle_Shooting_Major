from datetime import datetime, timedelta
import unittest
from app import app, db
from app.time_convert import *


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_grad_year(self):
        # Test written in 2022, expected values may need to be updated
        assert (get_grad_year("2023") == 11)
        assert(get_grad_year("Happy Little Accident") == "None")

    def test_format_duration(self):
        assert (format_duration(0) == "0s")
        assert (format_duration(14) == "14s")
        assert (format_duration(60) == "1m 0s")
        assert (format_duration(75) == "1m 15s")
        assert (format_duration(605) == "10m 5s")



if __name__ == '__main__':
    unittest.main(verbosity=2)
