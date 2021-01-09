from app import db, login, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
import statistics

class User(UserMixin, db.Model):
    # UserMixin defines isActive, isAuthenticated, getID, isAnonymous
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    fName = db.Column(db.String(70))
    sName = db.Column(db.String(70))
    email = db.Column(db.String(120))
    school = db.Column(db.String(5))
    schoolID = db.Column(db.String(20))
    schoolYr = db.Column(db.String(2))
    shooterID = db.Column(db.String(20))
    permitNumber = db.Column(db.String(20))
    permitExpiry = db.Column(db.Date)
    isAdmin = db.Column(db.Boolean, default=False)
    isActive = db.Column(db.Boolean, default=False)
    lastActive = db.Column(db.DateTime)
    stages = db.relationship('Stage', backref='shooter', lazy='dynamic')
    #Gear Settings
    jacket = db.Column(db.String(10))
    glove = db.Column(db.String(10))
    hat = db.Column(db.String(10))
    slingHole = db.Column(db.String(10))
    slingPoint = db.Column(db.String(10))
    butOut = db.Column(db.String(10))
    butUp = db.Column(db.String(10))
    ringSize = db.Column(db.String(10))
    sightHole = db.Column(db.String(10))


    def __repr__(self):
            return '<User {}>'.format(self.username)

    def generate_username(self):
        # Must have fName and sName initialised
        num = 1
        temp = self.fName.lower() + "." + self.sName[0].lower() + str(num)
        list = []
        for instance in User.query.all():
            list.append(instance.username)
        while temp in list:
            num += 1
            temp = self.fName.lower() + "." + self.sName[0].lower() + str(num)
        self.username = temp

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    def get_activation_token(self, expires_in=600):
        return jwt.encode(
            {'activate': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_activation_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except:
            return
        return User.query.get(id)


class Stage(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    groupSize = db.Column(db.Float)
    rangeDistance = db.Column(db.String(10))
    location = db.Column(db.String(50))
    notes = db.Column(db.String(255))
    shots = db.relationship('Shot', backref='stage', lazy='dynamic')

    def __init__(self):
        self.mean = 0
        self.median = 0
        self.std = 0

    def __repr__(self):
        return '<Stage {}>'.format(self.id)

    def stageStats(self):
        shots = Shot.query.filter_by(stageID=self.id).all()
        print(shots)
        scores = []
        for shot in shots:
            if not shot.sighter:
                scores.append(shot.score)
        try:
            mean = round(statistics.mean(scores), 2)
            median = round(statistics.median(scores),2)
            std = round(statistics.stdev(scores), 2)
            return mean, median, std
        except ValueError:
            raise ValueError("Error with list")

class Shot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stageID = db.Column(db.BigInteger, db.ForeignKey('stage.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    xPos = db.Column(db.Float)
    yPos = db.Column(db.Float)
    score = db.Column(db.Integer)
    numV = db.Column(db.Integer)
    sighter = db.Column(db.Boolean)

    def __repr__(self):
        return '<Shot {}>'.format(self.id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
