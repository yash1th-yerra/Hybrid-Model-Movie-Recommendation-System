from .extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genres = db.Column(db.String(255))
    ratings = db.relationship('Rating', backref='movie', lazy='dynamic')

    def __repr__(self):
        return f'<Movie {self.title}>'

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Rating User:{self.user_id} Movie:{self.movie_id} Score:{self.rating}>'
