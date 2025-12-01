from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(200))
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    from_station = db.Column(db.String(120))
    to_station = db.Column(db.String(120))
    depart = db.Column(db.String(20))
    arrive = db.Column(db.String(20))
    duration = db.Column(db.String(30))
    fare = db.Column(db.Float)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    train = db.relationship('Train')
    passenger_name = db.Column(db.String(120))
    passenger_age = db.Column(db.Integer)
    passenger_gender = db.Column(db.String(10))
    travel_date = db.Column(db.Date)
    seat_class = db.Column(db.String(30))
    fare = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)
    transaction_id = db.Column(db.String(200))
    booked_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)