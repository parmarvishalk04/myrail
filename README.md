# BlueRail - Production-Level Train Booking System

A secure, modern, and production-ready train booking application built with Flask.

## 🚀 Features

### Security
- **Environment-based configuration** using `.env` files
- **Rate limiting** to prevent abuse (Flask-Limiter)
- **Security headers** (XSS protection, CSRF, HSTS, etc.)
- **Strong password validation** (uppercase, lowercase, numbers)
- **Secure file uploads** with validation and image optimization
- **Session security** with HTTP-only and Secure cookies
- **SQL injection protection** via SQLAlchemy ORM
- **Input sanitization** and validation

### Styling & UX
- **Modern, responsive design** with CSS Grid and Flexbox
- **Mobile-first approach** for all devices
- **Smooth animations** and transitions
- **Accessibility features** (ARIA labels, keyboard navigation)
- **Professional color scheme** with CSS variables
- **Print-optimized tickets**

### Accuracy & Validation
- **Comprehensive form validation** on client and server side
- **Date validation** (past dates blocked)
- **Duplicate booking prevention**
- **Transaction management** with rollback on errors
- **Email format validation**
- **Card number formatting** and validation
- **Error handling** with user-friendly messages

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   cd train_project2
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and set your SECRET_KEY (use a strong random string)
   # Generate a secret key: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Initialize the database**
   ```bash
   python app.py
   ```
   The database will be created automatically on first run.

## 🏃 Running the Application

### Development Mode
```bash
# Set in .env: FLASK_DEBUG=True
python app.py
```

### Production Mode
```bash
# Set in .env: FLASK_DEBUG=False
# Use a production WSGI server like Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
train_project2/
├── app.py                 # Main Flask application
├── models.py             # Database models (User, Train, Booking)
├── forms.py              # WTForms validation forms
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
├── static/
│   ├── css/
│   │   └── style.css    # Modern CSS styling
│   ├── img/             # Images (logo, hero image)
│   └── uploads/         # User profile pictures
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── booking.html     # Booking page
│   ├── payment.html     # Payment page
│   ├── ticket.html      # Ticket view
│   ├── profile.html     # User profile
│   ├── auth/
│   │   ├── login.html   # Login page
│   │   └── register.html # Registration page
│   └── errors/
│       ├── 404.html     # 404 error page
│       └── 500.html     # 500 error page
└── app.db               # SQLite database (created automatically)
```

## 🔐 Security Features

### Implemented
- ✅ Environment-based secret keys
- ✅ Password hashing (Werkzeug)
- ✅ CSRF protection (Flask-WTF)
- ✅ Rate limiting (Flask-Limiter)
- ✅ Security headers (XSS, HSTS, etc.)
- ✅ Input validation and sanitization
- ✅ Secure file uploads
- ✅ SQL injection prevention
- ✅ Session security

### Recommended for Production
- Use PostgreSQL or MySQL instead of SQLite
- Implement HTTPS with SSL certificates
- Set up logging and monitoring
- Use a reverse proxy (Nginx)
- Implement email verification
- Add two-factor authentication
- Set up automated backups
- Use Redis for rate limiting storage
- Implement CAPTCHA for registration/login

## 🎨 Styling Features

- Modern CSS with custom properties (variables)
- Responsive grid and flexbox layouts
- Smooth animations and transitions
- Print-optimized ticket styling
- Accessibility compliant (WCAG guidelines)
- Mobile-first responsive design

## ✅ Validation Features

- **Name**: Letters and spaces only, 2-120 characters
- **Email**: Format validation, case-insensitive
- **Password**: Min 8 chars, uppercase, lowercase, number
- **Age**: 1-120 range
- **Date**: No past dates allowed
- **Card Number**: 13-19 digits, formatted display
- **CVV**: 3-4 digits
- **Expiry**: MM/YY format validation
- **File Upload**: Image validation, size limits (2MB max)

## 🚦 Rate Limits

- **Default**: 200 requests per day, 50 per hour
- **Login/Register**: 5 requests per minute
- **Payment**: 5 requests per minute
- **Booking**: 10 requests per minute
- **Profile**: 10 requests per minute

## 📝 API Endpoints

| Route | Method | Description | Auth Required |
|-------|--------|-------------|---------------|
| `/` | GET | Homepage | No |
| `/register` | GET, POST | User registration | No |
| `/login` | GET, POST | User login | No |
| `/logout` | GET | User logout | Yes |
| `/booking` | GET, POST | Book a ticket | Yes |
| `/payment/<id>` | GET, POST | Complete payment | Yes |
| `/profile` | GET, POST | User profile | Yes |
| `/ticket/<id>` | GET | View ticket | Yes |

## 🐛 Error Handling

- **404**: Page not found
- **500**: Internal server error
- **413**: File too large
- **Rate limit exceeded**: Custom error message
- **Validation errors**: Inline form error display

## 🔄 Database Models

### User
- id, name, email, password_hash, profile_pic
- Relationships: bookings

### Train
- id, name, number, from_station, to_station, depart, arrive, duration, fare

### Booking
- id, user_id, train_id, passenger_name, passenger_age, passenger_gender
- travel_date, seat_class, fare, paid, transaction_id
- booked_at, paid_at

## 🧪 Testing Recommendations

1. **Manual Testing**
   - Test all forms with invalid inputs
   - Test date validation
   - Test duplicate booking prevention
   - Test file upload validation
   - Test rate limiting

2. **Security Testing**
   - Test SQL injection attempts
   - Test XSS attempts
   - Test CSRF protection
   - Test file upload restrictions

## 📦 Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker (example Dockerfile)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production
```env
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/dbname
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational purposes.

## 👤 Author

BlueRail Development Team

## 🙏 Acknowledgments

- Flask framework
- WTForms for form validation
- SQLAlchemy for ORM
- All contributors



