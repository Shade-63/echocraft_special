from datetime import datetime
from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable= False, index= True)
    password= db.Column(db.String(60), nullable= False)

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