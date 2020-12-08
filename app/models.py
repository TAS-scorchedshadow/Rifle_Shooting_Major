from app import db
from app import login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    # UserMixin defines isActive, isAuthenticated, getID, isAnonymous
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    fName = db.Column(db.String(70))
    sName = db.Column(db.String(70))
    email = db.Column(db.String(120), index=True, unique=True)
    schoolID = db.Column(db.String(20))
    schoolYr = db.Column(db.String(2))
    shooterID = db.Column(db.String(20))
    permitNumber = db.Column(db.String(20))
    permitExpiry = db.Column(db.Date)
    isAdmin = db.Column(db.Boolean, default=False)
    stages = db.relationship('Stage', backref='shooter', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # def generate_username(self):
    #     # Must have fName and sName initialised
    #     num = 1
    #     temp = self.fName.lower() + "." + self.sName.lower() + str(num)
    #     user_list = User.query.all()
    #     while temp in user_list:
    #         num += 1
    #     self.username = temp

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jsonFilename = db.Column(db.String(128))
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    duration = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    groupSize = db.Column(db.Float)
    rangeType = db.Column(db.String(10))
    location = db.Column(db.String(50))
    notes = db.Column(db.String(255))
    shots = db.relationship('Shot', backref='stage', lazy='dynamic')

    def __repr__(self):
        return '<Stage {}>'.format(self.jsonFilename)


class Shot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stageID = db.Column(db.Integer, db.ForeignKey('stage.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    xPos = db.Column(db.Float)
    yPos = db.Column(db.Float)
    score = db.Integer
    numV = db.Integer

    def __repr__(self):
        return '<Shot {}>'.format(self.id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
