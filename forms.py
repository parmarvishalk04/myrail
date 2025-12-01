from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Regexp, ValidationError, Optional
from flask_wtf.file import FileAllowed, FileSize
from datetime import date
import re

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=120, message='Name must be between 2 and 120 characters'),
        Regexp(r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces')
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', 
               message='Password must contain at least one uppercase letter, one lowercase letter, and one number')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        if field.data:
            email = field.data.strip().lower()
            if len(email) > 120:
                raise ValidationError('Email address is too long')
            # Additional email format validation
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                raise ValidationError('Please enter a valid email address')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Sign In')

class BookingForm(FlaskForm):
    train_id = SelectField('Select Train', coerce=int, validators=[
        DataRequired(message='Please select a train')
    ])
    passenger_name = StringField('Passenger Name', validators=[
        DataRequired(message='Passenger name is required'),
        Length(min=2, max=120, message='Name must be between 2 and 120 characters'),
        Regexp(r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces')
    ])
    passenger_age = IntegerField('Age', validators=[
        DataRequired(message='Age is required'),
        NumberRange(min=1, max=120, message='Age must be between 1 and 120')
    ])
    passenger_gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired(message='Please select gender')])
    travel_date = DateField('Travel Date', validators=[
        DataRequired(message='Travel date is required')
    ], format='%Y-%m-%d')
    seat_class = SelectField('Seat Class', choices=[
        ('Economy', 'Economy'),
        ('Sleeper', 'Sleeper'),
        ('AC', 'AC')
    ], validators=[DataRequired(message='Please select seat class')])
    submit = SubmitField('Proceed to Payment')

    def validate_travel_date(self, field):
        if field.data:
            if field.data < date.today():
                raise ValidationError('Travel date cannot be in the past')

class PaymentForm(FlaskForm):
    card_name = StringField('Name on Card', validators=[
        DataRequired(message='Cardholder name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters'),
        Regexp(r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces')
    ])
    card_number = StringField('Card Number', validators=[
        DataRequired(message='Card number is required'),
        Length(min=13, max=19, message='Card number must be between 13 and 19 digits'),
        Regexp(r'^\d+$', message='Card number must contain only digits')
    ])
    expiry = StringField('Expiry (MM/YY)', validators=[
        DataRequired(message='Expiry date is required'),
        Regexp(r'^(0[1-9]|1[0-2])\/\d{2}$', message='Please enter expiry in MM/YY format')
    ])
    cvv = StringField('CVV', validators=[
        DataRequired(message='CVV is required'),
        Length(min=3, max=4, message='CVV must be 3 or 4 digits'),
        Regexp(r'^\d+$', message='CVV must contain only digits')
    ])
    submit = SubmitField('Pay Now')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=120, message='Name must be between 2 and 120 characters'),
        Regexp(r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces')
    ])
    profile_pic = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message='Only image files (JPG, PNG, GIF) are allowed'),
        FileSize(max_size=2097152, message='File size must be less than 2MB')
    ])
    submit = SubmitField('Update Profile')