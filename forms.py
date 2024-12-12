from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class HealthProfileForm(FlaskForm):
    age = IntegerField('Age', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional()])
    weight = FloatField('Weight (kg)', validators=[Optional()])
    medical_conditions = TextAreaField('Medical Conditions')
    submit = SubmitField('Update Profile')

class ScreeningAppointmentForm(FlaskForm):
    screening_type = SelectField('Screening Type', 
        choices=[
            ('general', 'General Health Screening'),
            ('mental', 'Mental Health Assessment'),
            ('dermatology', 'Dermatology Consultation'),
            ('cardio', 'Cardiovascular Health Check')
        ],
        validators=[DataRequired()]
    )
    preferred_date = StringField('Preferred Date', validators=[DataRequired()])
    preferred_time = SelectField('Preferred Time',
        choices=[
            ('morning', 'Morning (9AM-12PM)'),
            ('afternoon', 'Afternoon (1PM-5PM)'),
            ('evening', 'Evening (6PM-8PM)')
        ],
        validators=[DataRequired()]
    )
    notes = TextAreaField('Additional Notes', validators=[Optional()])
    submit = SubmitField('Schedule Screening')

class WaitlistForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Join Waitlist')
