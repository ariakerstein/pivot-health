import os
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

from models import User, MedicalRecord, HealthProfile
from forms import LoginForm, RegistrationForm, HealthProfileForm

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    health_profile = current_user.health_profile
    medical_records = current_user.medical_records
    return render_template('dashboard.html', 
                         health_profile=health_profile,
                         medical_records=medical_records)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Marketplace Routes
@app.route('/recently-viewed')
@login_required
def recently_viewed():
    return render_template('marketplace/recently_viewed.html')

@app.route('/diagnostic-services')
@login_required
def diagnostic_services():
    return render_template('marketplace/diagnostic_services.html')

@app.route('/patient-support')
@login_required
def patient_support():
    return render_template('marketplace/patient_support.html')

@app.route('/medical-equipment')
@login_required
def medical_equipment():
    return render_template('marketplace/medical_equipment.html')

@app.route('/caregiver-resources')
@login_required
def caregiver_resources():
    return render_template('marketplace/caregiver_resources.html')

@app.route('/health-articles')
@login_required
def health_articles():
    return render_template('marketplace/health_articles.html')

with app.app_context():
    db.create_all()
