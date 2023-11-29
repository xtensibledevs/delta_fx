
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

class LoginForm(FlaskForm):
    email = StringField('Email', id='email_login', validators=[DataRequired(), Email()])
    password = PasswordField('Password', id='pwd_login', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    email = StringField('Email', id='email_create', validators=[DataRequired(), Email()])
    password = PasswordField('Password', id='pwd_create', validators=[DataRequired()])