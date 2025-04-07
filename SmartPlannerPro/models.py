from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'donor', 'admin', 'agent'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    # One donor can have many donations
    donations = db.relationship('Donation', backref='donor', lazy='dynamic', 
                               foreign_keys='Donation.donor_id')
    
    # One agent can have many assigned donations
    assigned_donations = db.relationship('Donation', backref='agent', lazy='dynamic',
                                       foreign_keys='Donation.agent_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}, Role: {self.role}>'


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    food_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False)
    pickup_address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Assigned, Collected, Delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notifications = db.relationship('Notification', backref='donation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Donation {self.id}, Status: {self.status}>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id}, Read: {self.read}>'
