from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Donation, Notification
from forms import LoginForm, RegistrationForm, DonationForm, AssignAgentForm, UpdateStatusForm
from datetime import datetime
import functools

# Function to check if user has admin role
def admin_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

# Function to check if user has agent role
def agent_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'agent':
            flash('You need to be an agent to access this page.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

# Function to check if user has donor role
def donor_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'donor':
            flash('You need to be a donor to access this page.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

# Create notification
def create_notification(user_id, donation_id, message):
    notification = Notification(user_id=user_id, donation_id=donation_id, message=message)
    db.session.add(notification)
    db.session.commit()
    return notification

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard - redirects to role-specific dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'donor':
        return redirect(url_for('donor_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'agent':
        return redirect(url_for('agent_dashboard'))
    else:
        flash('Invalid user role', 'danger')
        return redirect(url_for('index'))

# Donor dashboard
@app.route('/donor/dashboard')
@login_required
@donor_required
def donor_dashboard():
    donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
    return render_template('donor/dashboard.html', donations=donations)

# Donate food route
@app.route('/donor/donate', methods=['GET', 'POST'])
@login_required
@donor_required
def donate():
    form = DonationForm()
    if form.validate_on_submit():
        donation = Donation(
            donor_id=current_user.id,
            food_type=form.food_type.data,
            quantity=form.quantity.data,
            expiry_time=form.expiry_time.data,
            pickup_address=form.pickup_address.data,
            status='Pending'
        )
        db.session.add(donation)
        db.session.commit()
        
        # Notify admins (in a real system, this could be done with email/push notifications)
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            create_notification(admin.id, donation.id, f"New donation request from {current_user.username}")
        
        flash('Donation request submitted successfully!', 'success')
        return redirect(url_for('donor_dashboard'))
    
    return render_template('donor/donate.html', form=form)

# Admin dashboard
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    pending = Donation.query.filter_by(status='Pending').count()
    assigned = Donation.query.filter_by(status='Assigned').count()
    collected = Donation.query.filter_by(status='Collected').count()
    delivered = Donation.query.filter_by(status='Delivered').count()
    
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(5).all()
    
    stats = {
        'pending': pending,
        'assigned': assigned,
        'collected': collected,
        'delivered': delivered,
        'total': pending + assigned + collected + delivered
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_donations=recent_donations)

# View all donation requests (admin)
@app.route('/admin/view_requests')
@login_required
@admin_required
def view_requests():
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        donations = Donation.query.order_by(Donation.created_at.desc()).all()
    else:
        donations = Donation.query.filter_by(status=status_filter).order_by(Donation.created_at.desc()).all()
    
    return render_template('admin/view_requests.html', donations=donations, status_filter=status_filter)

# Assign agent to donation
@app.route('/admin/assign_agent/<int:donation_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_agent(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.status != 'Pending':
        flash('This donation is already assigned or processed.', 'warning')
        return redirect(url_for('view_requests'))
    
    form = AssignAgentForm()
    # Get all agents to populate the select field
    form.agent.choices = [(a.id, a.username) for a in User.query.filter_by(role='agent').all()]
    
    if form.validate_on_submit():
        donation.agent_id = form.agent.data
        donation.status = 'Assigned'
        donation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Notify donor and agent
        agent = User.query.get(form.agent.data)
        create_notification(donation.donor_id, donation.id, f"Your donation has been assigned to agent {agent.username}")
        create_notification(agent.id, donation.id, f"You have been assigned to collect a donation")
        
        flash(f'Agent {agent.username} has been assigned to this donation.', 'success')
        return redirect(url_for('view_requests'))
    
    return render_template('admin/assign_agent.html', form=form, donation=donation)

# Agent dashboard
@app.route('/agent/dashboard')
@login_required
@agent_required
def agent_dashboard():
    assigned_donations = Donation.query.filter_by(
        agent_id=current_user.id
    ).order_by(Donation.updated_at.desc()).all()
    
    return render_template('agent/dashboard.html', donations=assigned_donations)

# Update donation status (agent)
@app.route('/agent/update_status/<int:donation_id>', methods=['GET', 'POST'])
@login_required
@agent_required
def update_status(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    
    # Check if this agent is assigned to this donation
    if donation.agent_id != current_user.id:
        flash('You are not assigned to this donation.', 'danger')
        return redirect(url_for('agent_dashboard'))
    
    form = UpdateStatusForm()
    
    # Set available status options based on current status
    if donation.status == 'Assigned':
        form.status.choices = [('Collected', 'Collected')]
    elif donation.status == 'Collected':
        form.status.choices = [('Delivered', 'Delivered')]
    else:
        flash('This donation cannot be updated further.', 'warning')
        return redirect(url_for('agent_dashboard'))
    
    if form.validate_on_submit():
        old_status = donation.status
        donation.status = form.status.data
        donation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Notify donor about status update
        create_notification(
            donation.donor_id, 
            donation.id, 
            f"Your donation status has been updated from {old_status} to {donation.status}"
        )
        
        flash(f'Donation status updated to {donation.status}', 'success')
        return redirect(url_for('agent_dashboard'))
    
    return render_template('agent/update_status.html', form=form, donation=donation)

# Get user notifications
@app.route('/notifications')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        read=False
    ).order_by(Notification.created_at.desc()).all()
    
    notification_data = [{
        'id': notification.id,
        'message': notification.message,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for notification in notifications]
    
    return jsonify(notification_data)

# Mark notification as read
@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Check if the notification belongs to the current user
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message="Access forbidden"), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

# Admin route to assign an agent (separate template)
@app.route('/admin/assign_agent_template/<int:donation_id>')
@login_required
@admin_required
def assign_agent_template(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    
    form = AssignAgentForm()
    # Get all agents to populate the select field
    form.agent.choices = [(a.id, a.username) for a in User.query.filter_by(role='agent').all()]
    
    return render_template('admin/assign_agent.html', form=form, donation=donation)
