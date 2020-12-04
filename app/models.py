from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    stages = db.relationship('Stage', backref='shooter', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username


class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Stage %r>' % self.notes