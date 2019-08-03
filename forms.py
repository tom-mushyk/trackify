from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.validators import DataRequired, Email, URL, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password ', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password ', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Sign Up')

class AddProductForm(FlaskForm):
    name = StringField('Product name', validators=[DataRequired()])
    url = URLField('URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Add')

class AddTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Add')

class AddLinkForm(FlaskForm):
    title = StringField('Site name', validators=[DataRequired()])
    url = URLField('URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Add')

class AddWeatherForm(FlaskForm):
    name = StringField('Site name', validators=[DataRequired()])
    submit = SubmitField('Add city!')
