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


    def test_get_season_times(self):
        os.environ["SEASON_START"] = '01/01/2022'
        os.environ["SEASON_END"] = '22/12/2023'

        begin, end = get_season_times()

        assert (begin == datetime(2022, 1, 1))
        assert (end == datetime(2023, 12, 22))

        os.environ["SEASON_START"] = "I'm a happy sentence"
        os.environ["SEASON_END"] = '32/12/2023'

        begin, end = get_season_times()

        assert (begin == datetime(2022, 1, 1))
        assert (end == datetime(2022, 12, 31))





if __name__ == '__main__':
    unittest.main(verbosity=2)
