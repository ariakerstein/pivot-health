from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class HealthProfileForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    height = FloatField('Height (cm)', validators=[DataRequired()])
    weight = FloatField('Weight (kg)', validators=[DataRequired()])
    medical_conditions = StringField('Medical Conditions')
    submit = SubmitField('Update Profile')
