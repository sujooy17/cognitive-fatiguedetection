from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('landing.html')

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok'}, 200
