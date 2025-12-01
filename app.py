import os
import uuid
import secrets
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from PIL import Image
from whitenoise import WhiteNoise

from forms import RegisterForm, LoginForm, BookingForm, PaymentForm, ProfileForm
from models import db, User, Train, Booking

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

# Configure database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 2 * 1024 * 1024))
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600))

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize Whitenoise for static files
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app.wsgi_app.add_files('static/img/', prefix='img/')
app.wsgi_app.add_files('static/css/', prefix='css/')
login_manager.session_protection = "strong"

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    """Validate and optimize uploaded image"""
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)
        return True
    except Exception:
        return False

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline';"
    return response

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

@app.before_request
def create_tables_and_seed():
    db.create_all()
    if Train.query.count() == 0:
        sample = [
            Train(name='Blue Express', number='BE123', from_station='City A', to_station='City B', depart='08:00', arrive='12:30', duration='4h 30m', fare=450.0),
            Train(name='Coastal Mail', number='CM456', from_station='City A', to_station='City C', depart='09:45', arrive='15:00', duration='5h 15m', fare=650.0),
            Train(name='Sunrise Special', number='SS789', from_station='City B', to_station='City C', depart='16:00', arrive='19:30', duration='3h 30m', fare=520.0),
        ]
        db.session.add_all(sample)
        db.session.commit()

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash('File size exceeds maximum allowed size (2MB)', 'danger')
    return redirect(request.url), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        # Check for existing email (case-insensitive)
        existing_user = User.query.filter(User.email.ilike(form.email.data.strip())).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', form=form)
        
        try:
            user = User(
                name=form.name.data.strip(),
                email=form.email.data.strip().lower(),
                password_hash=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Welcome! Account created successfully.', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET','POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email.ilike(form.email.data.strip())).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            flash('Logged in successfully', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/booking', methods=['GET','POST'])
@login_required
@limiter.limit("10 per minute")
def booking():
    trains = Train.query.order_by(Train.depart).all()
    if not trains:
        flash('No trains available at the moment.', 'warning')
    
    form = BookingForm()
    form.train_id.choices = [(t.id, f"{t.name} • {t.number} • {t.from_station} → {t.to_station} • {t.depart}") for t in trains] if trains else []
    
    if form.validate_on_submit():
        # Validate train exists
        train = Train.query.get(form.train_id.data)
        if not train:
            flash('Selected train not found', 'danger')
            return render_template('booking.html', trains=trains, form=form)
        
        # Validate travel date is not in the past
        if form.travel_date.data < date.today():
            flash('Travel date cannot be in the past', 'danger')
            return render_template('booking.html', trains=trains, form=form)
        
        # Check for duplicate booking (same train, date, and passenger)
        existing_booking = Booking.query.filter_by(
            user_id=current_user.id,
            train_id=train.id,
            travel_date=form.travel_date.data,
            passenger_name=form.passenger_name.data.strip()
        ).first()
        
        if existing_booking and existing_booking.paid:
            flash('You already have a paid booking for this train on this date', 'warning')
            return render_template('booking.html', trains=trains, form=form)
        
        try:
            booking = Booking(
                user_id=current_user.id,
                train_id=train.id,
                passenger_name=form.passenger_name.data.strip(),
                passenger_age=form.passenger_age.data,
                passenger_gender=form.passenger_gender.data,
                travel_date=form.travel_date.data,
                seat_class=form.seat_class.data,
                fare=train.fare,
                booked_at=datetime.utcnow()
            )
            db.session.add(booking)
            db.session.commit()
            flash('Booking created successfully', 'success')
            return redirect(url_for('payment', booking_id=booking.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating booking. Please try again.', 'danger')
    
    return render_template('booking.html', trains=trains, form=form)

@app.route('/payment/<int:booking_id>', methods=['GET','POST'])
@login_required
@limiter.limit("5 per minute")
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Authorization check
    if booking.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    # Check if already paid
    if booking.paid:
        flash('This booking has already been paid', 'info')
        return redirect(url_for('ticket', booking_id=booking.id))
    
    form = PaymentForm()
    if form.validate_on_submit():
        try:
            # In production, integrate with actual payment gateway here
            booking.paid = True
            booking.transaction_id = str(uuid.uuid4())
            booking.paid_at = datetime.utcnow()
            db.session.commit()
            flash('Payment successful! Your ticket has been confirmed.', 'success')
            return redirect(url_for('ticket', booking_id=booking.id))
        except Exception as e:
            db.session.rollback()
            flash('Payment processing failed. Please try again.', 'danger')
    
    return render_template('payment.html', booking=booking, form=form)

@app.route('/profile', methods=['GET','POST'])
@login_required
@limiter.limit("10 per minute")
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        try:
            current_user.name = form.name.data.strip()
            file = form.profile_pic.data
            
            if file and file.filename:
                # Validate file
                if not allowed_file(file.filename):
                    flash('Invalid file type. Only images (PNG, JPG, JPEG, GIF) are allowed.', 'danger')
                    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booked_at.desc()).all()
                    return render_template('profile.html', form=form, bookings=bookings)
                
                # Validate image
                if not validate_image(file):
                    flash('Invalid image file. Please upload a valid image.', 'danger')
                    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booked_at.desc()).all()
                    return render_template('profile.html', form=form, bookings=bookings)
                
                # Secure filename
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1].lower()
                filename = f"user_{current_user.id}_{uuid.uuid4().hex}{ext}"
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save and optimize image
                file.seek(0)
                img = Image.open(file)
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                
                # Resize if too large (max 800x800)
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img.save(path, 'JPEG', quality=85, optimize=True)
                
                # Delete old profile picture if exists
                if current_user.profile_pic:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_pic)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except Exception:
                            pass
                
                current_user.profile_pic = filename
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating profile. Please try again.', 'danger')
    
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booked_at.desc()).all()
    return render_template('profile.html', form=form, bookings=bookings)

@app.route('/ticket/<int:booking_id>')
@login_required
def ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    return render_template('ticket.html', booking=booking)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000) 