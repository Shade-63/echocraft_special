from flask_wtf import FlaskForm
from wtforms import TextAreaField, PasswordField, StringField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
from wtforms.widgets import TextArea
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    
    def validate_username(self, field):
        """Custom validation for username format"""
        if not re.match(r'^[a-zA-Z0-9_]+$', field.data):
            raise ValidationError('Username can only contain letters, numbers, and underscores')
        
        # Check for common reserved words
        reserved_words = ['admin', 'root', 'system', 'test', 'guest', 'user']
        if field.data.lower() in reserved_words:
            raise ValidationError('This username is not available')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters')
    ])
    content = TextAreaField('Content', validators=[
        Optional(),
        Length(max=5000, message='Content cannot exceed 5000 characters')
    ], widget=TextArea())
    category = SelectField('Category', validators=[
        DataRequired(message='Please select a category')
    ], choices=[
        ('Writing', '✍️ Writing'), 
        ('Photography', '📸 Photography'),
        ('Paintings', '🎨 Paintings'),
        ('Music', '🎵 Music'),
        ('Design', '🎨 Design'),
        ('Other', '✨ Other')
    ])
    image = FileField('Upload Image (Optional)')
    
    def validate_title(self, field):
        """Custom validation for title"""
        # Remove extra whitespace
        field.data = field.data.strip()
        
        # Check for inappropriate content
        inappropriate_words = ['spam', 'advertisement', 'click here']
        if any(word in field.data.lower() for word in inappropriate_words):
            raise ValidationError('Title contains inappropriate content')
    
    def validate_content(self, field):
        """Custom validation for content"""
        if field.data:
            # Remove extra whitespace
            field.data = field.data.strip()
            
            # Check content length (excluding whitespace)
            if len(field.data.strip()) < 10:
                raise ValidationError('Content must be at least 10 characters long')