from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.db import get_db
import hashlib
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)
db = get_db()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('register.html')
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not all([email, password, full_name, confirm_password]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        existing_user = db.find_user_by_email(email)
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        try:
            user_id = db.register_user(email, password, full_name)
            session['user_id'] = user_id
            session['email'] = email
            session['full_name'] = full_name
            return jsonify({'success': True, 'message': 'Registration successful', 'redirect': '/dashboard'}), 201
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login user"""
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('login.html')
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
        user = db.find_user_by_email(email)
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] != hashed_password:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Login successful
        session['user_id'] = str(user['_id'])
        session['email'] = user['email']
        session['full_name'] = user['full_name']
        
        return jsonify({'success': True, 'message': 'Login successful', 'redirect': '/dashboard'}), 200

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('main.landing'))

@auth_bp.route('/api/user-info')
def user_info():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    return jsonify({
        'success': True,
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'full_name': session.get('full_name')
    }), 200
