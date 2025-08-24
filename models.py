from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable= False, index= True)
    password_hash = db.Column(db.String(255), nullable = False)

    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash form"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(100), nullable= False, index= True)
    created_at = db.Column(db.DateTime, default= datetime.utcnow, index= True)
    content = db.Column(db.Text)
    category = db.Column(db.String(20), index= True)
    img_url = db.Column(db.String(500))
    likes = db.Column(db.Integer, default= 0)
    funny = db.Column(db.Integer, default= 0)
    inspire = db.Column(db.Integer, default= 0)

    #need to define proper relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete= 'CASCADE'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy= True, cascade= 'all, delete-orphan'))

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_at}')"