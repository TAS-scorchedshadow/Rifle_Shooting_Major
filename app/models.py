from app import db, login, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
import statistics

class User(UserMixin, db.Model):
    """
    User database table

    :parameter [UserMixin]: Defines isActive, isAuthenticated, getID, isAnonymous
    :parameter [db.Model]: TO BE FILLED
    """
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
    permitType = db.Column(db.String(20))
    sharing = db.Column(db.String(20))
    dob = db.Column(db.Date)
    mobile = db.Column(db.String(20))
    permitExpiry = db.Column(db.Date)
    isAdmin = db.Column(db.Boolean, default=False)
    isActive = db.Column(db.Boolean, default=False)
    lastActive = db.Column(db.Date)
    stages = db.relationship('Stage', backref='shooter', lazy='dynamic')

    #Gear Settings
    rifleSerial = db.Column(db.String(20))
    jacket = db.Column(db.String(10))
    glove = db.Column(db.String(10))
    hat = db.Column(db.String(10))
    slingHole = db.Column(db.String(10))
    slingPoint = db.Column(db.String(10))
    butOut = db.Column(db.String(10))
    butUp = db.Column(db.String(10))
    ringSize = db.Column(db.String(10))
    sightHole = db.Column(db.String(10))
    #Elevation Settings
    PPU300m = db.Column(db.String(8))
    ADI300m = db.Column(db.String(8))
    Fore300m = db.Column(db.String(8))
    PPU400m = db.Column(db.String(8))
    ADI400m = db.Column(db.String(8))
    Fore400m = db.Column(db.String(8))
    PPU500m = db.Column(db.String(8))
    ADI500m = db.Column(db.String(8))
    Fore500m = db.Column(db.String(8))
    PPU600m = db.Column(db.String(8))
    ADI600m = db.Column(db.String(8))
    Fore600m = db.Column(db.String(8))
    PPU700m = db.Column(db.String(8))
    ADI700m = db.Column(db.String(8))
    Fore700m = db.Column(db.String(8))
    PPU800m = db.Column(db.String(8))
    ADI800m = db.Column(db.String(8))
    Fore800m = db.Column(db.String(8))
    PPU500y = db.Column(db.String(8))
    ADI500y = db.Column(db.String(8))
    Fore500y = db.Column(db.String(8))
    PPU600y = db.Column(db.String(8))
    ADI600y = db.Column(db.String(8))
    Fore600y = db.Column(db.String(8))


    def __repr__(self):
            return '<User {}>'.format(self.username)

    def generate_username(self):
        """
        :return: TO BE FILLED
        """
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
        """
        :param password: The password set
        :return: TO BE FILLED
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        :param password: Entered password
        :return: Checks is password is correct
        """
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        """
        :param expires_in: TO BE FILLED
        :return: TO BE FILLED
        """
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    def get_activation_token(self, expires_in=600):
        """
        :param expires_in: TO BE FILLED
        :return: TO BE FILLED
        """
        return jwt.encode(
            {'activate': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_token(token):
        """
        :param token: TO BE FILLED
        :return: ID of the user
        """
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_activation_token(token):
        """
        :param token: TO BE FILLED
        :return: ID of the user
        """
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except:
            return
        return User.query.get(id)

    def seasonStats(self):
        """
        Statistics on the season

        :return: Mean, median, std, group size & duration
        """
        totalMean = 0
        totalMedian = 0
        totalStd = 0
        totalDuration = 0
        totalGroup = 0
        stages = Stage.query.filter_by(userID=self.id).all()
        for stage in stages:
            stats = stage.stageStats()
            totalMean += stats[0]
            totalMedian += stats[1]
            totalStd += stats[2]
            totalGroup +=stats[3]
            totalDuration += stats[4]
        mean = totalMean / len(stages)
        median = totalMedian /len(stages)
        std = totalStd / len(stages)
        group = totalGroup / len(stages)
        duration = int(totalDuration /len(stages))
        return mean,median,std,group,duration




class Stage(db.Model):
    """
    Stages database table

    :type: Class
    :parameter: TO BE FILLED
    """
    id = db.Column(db.BigInteger, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    groupSize = db.Column(db.Float)
    groupX = db.Column(db.Float)
    groupY = db.Column(db.Float)
    rangeDistance = db.Column(db.String(10))
    location = db.Column(db.String(50))
    notes = db.Column(db.String(255))
    shots = db.relationship('Shot', backref='stage', lazy='dynamic')

    def __repr__(self):
        return '<Stage {}>'.format(self.id)

    def stageStats(self):
        """
        :returns: Mean, median, std, group size and duration if successful
        """
        shots = Shot.query.filter_by(stageID=self.id).all()
        scores = [shot.score for shot in shots if not shot.sighter]
        try:
            mean = statistics.mean(scores)
            median = statistics.median(scores)
            std = statistics.stdev(scores)
            duration = int((shots[-1].timestamp - shots[1].timestamp).total_seconds())
            return mean, median, std, self.groupSize, duration
        except ValueError:
            raise ValueError("Error with list, likely null")

class Shot(db.Model):
    """
    Shot database table

    :type: Class
    :parameter: TO BE FILLED
    """
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
