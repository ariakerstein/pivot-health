from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from datetime import datetime
import os
from health_screening import schedule_health_screening, get_available_slots
from database import db, init_db

app = Flask(__name__)
# Add SVG MIME type
app.config['MIME_TYPES'] = {'svg': 'image/svg+xml'}

# Enhanced proxy configuration for HTTPS and domain handling
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_proto=1,
    x_host=1,
    x_prefix=1,
    x_port=1
)

# Security settings
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Production configuration
if os.environ.get('PRODUCTION') == 'true':
    # Domain settings for pivothealth.ai with enhanced SSL configuration
    app.config.update(
        SERVER_NAME='pivothealth.ai',
        PREFERRED_URL_SCHEME='https',
        SESSION_COOKIE_DOMAIN='.pivothealth.ai',
        SESSION_COOKIE_SECURE=True,
        REMEMBER_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=86400,  # 24 hours
        SESSION_COOKIE_SAMESITE='Strict',
        CORS_HEADERS='Content-Type'
    )
    
    # SSL certificate configuration
    ssl_cert = os.environ.get('SSL_CERT_PATH')
    ssl_key = os.environ.get('SSL_KEY_PATH')
    if ssl_cert and ssl_key:
        if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
            app.config.update(
                SSL_CERTIFICATE=ssl_cert,
                SSL_PRIVATE_KEY=ssl_key
            )
            # Enable HTTPS-only cookies
            app.config['SESSION_COOKIE_SECURE'] = True
            app.config['REMEMBER_COOKIE_SECURE'] = True
        else:
            app.logger.error(f"SSL certificate files not found at {ssl_cert} or {ssl_key}")
    
    # Enhanced security headers for production
    @app.after_request
    def add_security_headers(response):
        headers = {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self' https://*.pivothealth.ai; "
                                     "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                                     "style-src 'self' 'unsafe-inline'; "
                                     "img-src 'self' data:; "
                                     "font-src 'self' data:;"
        }
        for key, value in headers.items():
            response.headers[key] = value
        return response


# Configure SQLAlchemy (maintained original configuration)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 3,
    'max_overflow': 2,
    'pool_timeout': 30,
    'pool_pre_ping': True,
    'pool_recycle': 1800
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)
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

@app.route('/.well-known/acme-challenge/<token>')
def acme_challenge(token):
    """Handle ACME challenge for SSL certificate validation"""
    app.logger.info(f"ACME challenge requested for token: {token}")
    
    # Look for the challenge file in the static directory
    challenge_dir = os.path.join(app.static_folder, '.well-known', 'acme-challenge')
    challenge_path = os.path.join(challenge_dir, token)
    
    app.logger.info(f"Looking for challenge file at: {challenge_path}")
    
    if os.path.exists(challenge_path):
        with open(challenge_path, 'r') as f:
            content = f.read().strip()
            app.logger.info(f"Serving challenge content: {content}")
            return content, 200, {'Content-Type': 'text/plain'}
    
    # For debugging purposes, list all files in the challenge directory
    if os.path.exists(challenge_dir):
        files = os.listdir(challenge_dir)
        app.logger.info(f"Files in challenge directory: {files}")
    else:
        app.logger.warning("Challenge directory does not exist")
    
    return 'Not found', 404

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

@app.route('/symptom-checker')
@login_required
def symptom_checker():
    return render_template('symptom_checker.html')

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
        # Allow both Replit domain and custom domain during SSL setup
        app.config['SERVER_NAME'] = None  # Allow all hostnames during setup
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
        

# For both production and development
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    init_db()  # Initialize database in main process
    if os.environ.get('PRODUCTION') == 'true':
        # Let gunicorn handle the server
        pass
    else:
        app.run(debug=False, host='0.0.0.0', port=port)