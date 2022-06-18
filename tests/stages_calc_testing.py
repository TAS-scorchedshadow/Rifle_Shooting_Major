from datetime import datetime, timedelta
import unittest
import random

from app import app, db
from app.models import Shot, Stage
from app.time_convert import *
from app.generate_data import generate_rand_shot, generate_rand_stages


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_generate_shots(self):
        stage = generate_rand_stages(5, "300m")
        stage.init_shots()
        print(stage.shotList)
        assert(True == True)



if __name__ == '__main__':
    unittest.main(verbosity=2)

