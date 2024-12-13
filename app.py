from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from health_screening import schedule_health_screening, get_available_slots
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Simple configuration for Replit
port = int(os.environ.get('PORT', 5000))

# Configure SQLAlchemy for Replit deployment
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 3,
    'max_overflow': 2,
    'pool_timeout': 30,
    'pool_pre_ping': True,
    'pool_recycle': 1800
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    try:
        return db.session.get(User, int(id))
    except Exception as e:
        app.logger.error(f"Error loading user: {str(e)}")
        return None

from models import User, MedicalRecord, HealthProfile, Waitlist
from forms import LoginForm, RegistrationForm, HealthProfileForm, ScreeningAppointmentForm, WaitlistForm

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    waitlist_form = WaitlistForm()
    return render_template('index.html', waitlist_form=waitlist_form)

@app.route('/join-waitlist', methods=['POST'])
def join_waitlist():
    form = WaitlistForm()
    if form.validate_on_submit():
        try:
            waitlist_entry = Waitlist(email=form.email.data)
            db.session.add(waitlist_entry)
            db.session.commit()
            flash('Thank you for joining our waitlist! We\'ll notify you when we launch.', 'success')
        except Exception as e:
            if 'unique constraint' in str(e).lower():
                flash('This email is already on our waitlist.', 'info')
            else:
                flash('An error occurred. Please try again.', 'error')
                app.logger.error(f'Error adding to waitlist: {str(e)}')
            db.session.rollback()
    return redirect(url_for('index'))

@app.route('/admin/waitlist')
@login_required
def admin_waitlist():
    """Admin view to see all waitlist entries"""
    # Only allow admin users
    if not current_user.is_authenticated or current_user.email != 'admin@pivothealth.ai':
        return redirect(url_for('index'))
    
    waitlist_entries = Waitlist.query.order_by(Waitlist.joined_at.desc()).all()
    return render_template('admin/waitlist.html', entries=waitlist_entries)

@app.route('/dashboard')
@login_required
def dashboard():
    if request.user_agent.platform and request.user_agent.platform.lower() in ['iphone', 'android']:
        return render_template('mobile/dashboard.html')
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
    """Route to schedule professional health consultations"""
    from health_screening.screening_utils import get_screening_questions
    
    form = ScreeningAppointmentForm()
    if form.validate_on_submit():
        try:
            consultation = HealthScreening(
                user_id=current_user.id,
                screening_type=form.screening_type.data,
                preferred_date=form.preferred_date.data,
                preferred_time=form.preferred_time.data,
                notes=form.notes.data,
                status='pending'
            )
            db.session.add(consultation)
            db.session.commit()
            
            # Get pre-consultation questions
            consultation_questions = get_screening_questions(form.screening_type.data)
            
            flash(f'Your {form.screening_type.data} consultation has been requested for {form.preferred_date.data} at {form.preferred_time.data}. Our team will contact you to confirm the appointment.')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while scheduling your consultation. Please try again.', 'error')
            app.logger.error(f'Error scheduling consultation: {str(e)}')
    
    screening_type = request.args.get('type', 'general')
    available_slots = get_available_slots(screening_type, form.preferred_date.data if form.preferred_date.data else None)
    screening_questions = get_screening_questions(screening_type)
    
    return render_template(
        'health_screening.html',
        form=form,
        active_screening=screening_type,
        available_slots=available_slots,
        screening_questions=screening_questions
    )

@app.route('/health/schedule/<screening_type>', methods=['GET', 'POST'])
@login_required
def schedule_screening(screening_type):
    """Route to schedule specific screening appointments"""
    form = ScreeningAppointmentForm(screening_type=screening_type)
    if form.validate_on_submit():
        try:
            screening = HealthScreening(
                user_id=current_user.id,
                screening_type=screening_type,
                preferred_date=form.preferred_date.data,
                preferred_time=form.preferred_time.data,
                notes=form.notes.data,
                status='scheduled'
            )
            db.session.add(screening)
            db.session.commit()
            flash(f'Your {screening_type} screening has been scheduled successfully.')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while scheduling your appointment. Please try again.', 'error')
            app.logger.error(f'Error scheduling screening: {str(e)}')
    return render_template('schedule_screening.html', form=form, screening_type=screening_type)

def init_db():
    try:
        with app.app_context():
            db.create_all()
            app.logger.info("Database tables created successfully")
            # Verify database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            app.logger.info("Database connection verified")
    except Exception as e:
        app.logger.error(f"Error initializing database: {str(e)}")
        raise

def configure_prod_settings(app):
    """Basic production settings"""
    pass

if __name__ != '__main__':
    # Initialize database when imported as a module
    init_db()
    
    # Configure production settings if in production
    if os.environ.get('PRODUCTION') == 'true':
        configure_prod_settings(app)
