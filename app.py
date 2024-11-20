from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

from models import User, MedicalRecord, HealthProfile
from forms import LoginForm, RegistrationForm, HealthProfileForm, ScreeningAppointmentForm

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/health/screening', methods=['GET', 'POST'])
@login_required
def health_screening():
    """Route to show available health screening options and handle appointments"""
    form = ScreeningAppointmentForm()
    if form.validate_on_submit():
        # Create appointment record
        flash(f'Your {form.screening_type.data} screening has been scheduled for {form.preferred_date.data} during {form.preferred_time.data}.')
        return redirect(url_for('dashboard'))
    
    # Get screening type from query params
    screening_type = request.args.get('type', 'general')
    return render_template('health_screening.html', form=form, active_screening=screening_type)

@app.route('/health/schedule/<screening_type>', methods=['GET', 'POST'])
@login_required
def schedule_screening(screening_type):
    """Route to schedule specific screening appointments"""
    form = ScreeningAppointmentForm()
    if form.validate_on_submit():
        flash(f'Your {screening_type} screening has been scheduled successfully.')
        return redirect(url_for('dashboard'))
    return render_template('schedule_screening.html', form=form, screening_type=screening_type)

with app.app_context():
    db.create_all()
