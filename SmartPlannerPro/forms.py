from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from datetime import datetime
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('donor', 'Food Donor'), ('agent', 'Collection Agent'), ('admin', 'Administrator')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one or login.')

class DonationForm(FlaskForm):
    food_type = StringField('Food Type', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    expiry_time = DateTimeField('Expiry Time (YYYY-MM-DD HH:MM)', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    pickup_address = TextAreaField('Pickup Address', validators=[DataRequired(), Length(min=10, max=200)])
    submit = SubmitField('Submit Donation')
    
    def validate_expiry_time(self, expiry_time):
        if expiry_time.data < datetime.now():
            raise ValidationError('Expiry time cannot be in the past.')

class AssignAgentForm(FlaskForm):
    agent = SelectField('Select Agent', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Agent')

class UpdateStatusForm(FlaskForm):
    status = SelectField('Update Status', choices=[
        ('Assigned', 'Assigned'),
        ('Collected', 'Collected'),
        ('Delivered', 'Delivered')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')
