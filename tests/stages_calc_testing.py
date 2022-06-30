from datetime import datetime, timedelta
import unittest
import random

from app import app, db
from app.models import Shot, Stage
from app.time_convert import *
from app.generate_data import generate_rand_stage


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_generate_stage(self):
        stage = generate_rand_stage(20,0,0,0.1,0.1,"300m")
        stage.init_shots()
        assert(len(stage.shotList) == 20)
        generate_rand_stage(20, 0, 0, 0.1, 0.1, "300m")
        generate_rand_stage(20, 0, 0, 0.1, 0.1, "300m")



if __name__ == '__main__':
    unittest.main(verbosity=2)

