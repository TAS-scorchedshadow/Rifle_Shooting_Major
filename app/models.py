from app import db, login, app
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
import statistics
from app.timeConvert import nsw_to_utc, utc_to_nsw


class User(UserMixin, db.Model):
    """
    User database table

    :parameter [UserMixin]: Defines isActive, isAuthenticated, getID, isAnonymous
    :parameter [db.Model]: Defines database model with SQLAlchemy
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
    gradYr = db.Column(db.String(4))
    shooterID = db.Column(db.String(20))
    permitNumber = db.Column(db.String(20))
    permitType = db.Column(db.String(20))
    sharing = db.Column(db.String(20))
    dob = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    permitExpiry = db.Column(db.Date)
    access = db.Column(db.Integer, default=0)
    labels = db.Column(db.JSON)
    stages = db.relationship('Stage', backref='shooter', lazy='dynamic')

    # Gear Settings
    rifle_serial = db.Column(db.String(20))
    rifle_slingPointLength = db.Column(db.String(20))
    rifle_buttLength = db.Column(db.String(20))
    rifle_buttHeight = db.Column(db.String(20))
    rifle_sightHole = db.Column(db.String(20))

    # New Elevation
    elevation_300m = db.Column(db.String(20))
    ringSize_300m = db.Column(db.String(20))

    elevation_400m = db.Column(db.String(20))
    ringSize_400m = db.Column(db.String(20))

    elevation_500m = db.Column(db.String(20))
    ringSize_500m = db.Column(db.String(20))

    elevation_600m = db.Column(db.String(20))
    ringSize_600m = db.Column(db.String(20))

    elevation_700m = db.Column(db.String(20))
    ringSize_700m = db.Column(db.String(20))

    elevation_800m = db.Column(db.String(20))
    ringSize_800m = db.Column(db.String(20))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # By Dylan Huynh
    def generate_username(self):
        """
        Create username eg. Bob Smith --> Bob.S2
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

    def get_school_year(self):
        """
        Determines the user's school year based on their graduation year & the current time

        :return: school_year as integer ie. 7,8,9,10,11,12
        """
        try:
            cur_year = datetime.today().year
            school_year = cur_year - int(self.gradYr) + 12
            return school_year
        except:
            print("Students graduation year is not defined")

    # The following password and token verification functions are adapted from Miguel Grinberg's Flask Megatutorial
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
        """
        :param token: Token inputted by user, currently given by email
        :return: ID of the user
        """
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except:
            return
        return User.query.get(id)

    # By Dylan Huynh
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
            if stats:
                totalMean += stats[0]
                totalMedian += stats[1]
                totalStd += stats[2]
                totalGroup += stats[3]
                totalDuration += stats[4]
        mean = totalMean / len(stages)
        median = totalMedian / len(stages)
        std = totalStd / len(stages)
        group = totalGroup / len(stages)
        duration = int(totalDuration / len(stages))
        return mean, median, std, group, duration


class Stage(db.Model):
    """
    Stages database table
    """
    id = db.Column(db.BigInteger, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    groupSize = db.Column(db.Float, default=0)
    groupX = db.Column(db.Float, default=0)
    groupY = db.Column(db.Float, default=0)
    distance = db.Column(db.String(10))
    location = db.Column(db.String(50))
    settings = db.Column(db.JSON)
    notes = db.Column(db.String(255))
    shots = db.relationship('Shot', backref='stage', lazy='dynamic')

    def __repr__(self):
        return '<Stage {}>'.format(self.id)

    def same_day(self):
        # Because datetime is stored as utc, we have to first convert it to local time to get the time for the start and end of the day
        # Then it must be converted back to utc to query the database
        # Returns a tuple with all the stages on the same day as the stage given
        dayStartAEST = utc_to_nsw(self.timestamp).replace(hour=0, minute=0, second=0, microsecond=0)
        dayEndAEST = dayStartAEST + timedelta(days=1)
        dayStart = nsw_to_utc(dayStartAEST)
        dayEnd = nsw_to_utc(dayEndAEST)
        dayStages = Stage.query.filter(Stage.timestamp.between(dayStart, dayEnd))
        return dayStages

    def stageStats(self):
        """
        :returns: Mean, median, std, group size and duration if successful
        """
        shots = Shot.query.filter_by(stageID=self.id).all()
        scores = [shot.score for shot in shots if not shot.sighter]
        if scores:
            mean = statistics.mean(scores)
            median = statistics.median(scores)
            std = statistics.stdev(scores)
            duration = int((shots[-1].timestamp - shots[1].timestamp).total_seconds())
            return mean, median, std, self.groupSize, duration
        return


class Shot(db.Model):
    """
    Shot database table

    """
    id = db.Column(db.Integer, primary_key=True)
    stageID = db.Column(db.BigInteger, db.ForeignKey('stage.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    xPos = db.Column(db.Float)
    yPos = db.Column(db.Float)
    score = db.Column(db.Integer)
    vScore = db.Column(db.Integer)
    sighter = db.Column(db.Boolean)
    outlier = False

    def __repr__(self):
        return '<Shot {}>'.format(self.id)

    # By Dylan Huynh
    def positionfromCenterMOA(self, distance):
        if distance[-1:] == "m":  # If in meters
            # Finding MOA(Square) in Millimetres
            moa = ((1.047 * 25.4) / 100) * (39.37 / 36) * int(distance[:-1])
            xChangeMoa = self.xPos / moa
            yChangeMoa = self.yPos / moa
            shortestDistance = (self.xPos ** 2 + self.yPos ** 2) ** 0.5
            # print(xChangeMoa, yChangeMoa, shortestDistance)
            return xChangeMoa, yChangeMoa, shortestDistance
        return "Invalid Distance"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
