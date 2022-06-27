import unittest
from app import app, db


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_greeting(self):
        app.get('/')
        self.assert_template_used('index.html')
        self.assert_context("greeting", "hello")


if __name__ == '__main__':
    unittest.main(verbosity=2)
