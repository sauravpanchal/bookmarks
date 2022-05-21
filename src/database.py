from enum import unique
from turtle import update
from venv import create
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())
    
    bookmarks = db.relationship("Bookmark", backref = "user")


    def __repr__(self) -> str:
        return "User >>> {self.username}"

class Bookmarks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text, nullable = True)
    url = db.Column(db.Text, nullable = False)
    short_url = db.Column(db.String(8), nullable = True)
    visits = db.Column(db.Integer, default = 0)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    created_at = db.Column(db.DateTime, default = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())

    def generate_short_url(self):
        char_choices = string.digits + string.ascii_letters
        picked_chars = ''.join(random.choices(char_choices, k = 8))

        link = self.query.filter_by(short_url = picked_chars).first()

        # checks if short_url's combination exist in database or not.
        # if it exists then generate again (because we need unique short_url) else return picked_chars
        if link:
            self.generate_short_url()
        else:
            return picked_chars

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.short_url = self.generate_short_url()

    def __repr__(self) -> str:
        return "Bookmark >> {self.url}"

