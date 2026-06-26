from flask_login import UserMixin
from __init__ import db


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(200), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	profession = db.Column(db.String(100), nullable=False)
	age = db.Column(db.Integer, nullable=False)
	gender = db.Column(db.String(10), nullable=False)
	state = db.Column(db.String(100), nullable=False)
	profile_image = db.Column(db.String(200), nullable=True, default="default.jpg")

	def __repr__(self):
		return f'<User {self.name}>'

