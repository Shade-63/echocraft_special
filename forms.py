from flask_wtf import FlaskForm
from wtforms import TextAreaField, PasswordField, StringField, FileField, SelectField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators= [DataRequired(), Length(min= 4, max= 20)])
    password = PasswordField('Passsword', validators= [DataRequired()])

class PostForm(FlaskForm):
    title = StringField('Title', validators= [DataRequired(), Length(max= 100)])
    content = TextAreaField('Content')
    category = SelectField('Category', choices= [
        ('Writing', 'Writing'), 
        ('Photography', 'Photography'),
        ('Paintings', 'Paintings')
        ])
    image = FileField('Upload Image (Optional)')