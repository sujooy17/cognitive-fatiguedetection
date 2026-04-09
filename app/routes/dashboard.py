from flask import Blueprint, render_template, jsonify, session, redirect, url_for
from app.models.db import get_db
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)
db = get_db()

@dashboard_bp.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

@dashboard_bp.route('/activity')
def activity():
    """Activity tracking page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('activity.html')

@dashboard_bp.route('/api/dashboard-stats')
def dashboard_stats():
    """Get dashboard statistics"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get latest activity
    latest_activity = db.db.activity_logs.find_one(
        {'user_id': user_id},
        sort=[('timestamp', -1)]
    )
    
    # Get latest fatigue result
    latest_fatigue = db.get_latest_fatigue_result(user_id)
    
    # Get activity count today
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_activities = db.db.activity_logs.count_documents({
        'user_id': user_id,
        'timestamp': {'$gte': today}
    })
    
    # Get average typing speed (last 10 activities)
    recent_activities = list(db.db.activity_logs.find(
        {'user_id': user_id}
    ).sort('timestamp', -1).limit(10))
    
    avg_typing_speed = 0
    if recent_activities:
        avg_typing_speed = sum(a.get('typing_speed', 0) for a in recent_activities) / len(recent_activities)
    
    return jsonify({
        'success': True,
        'typing_speed': latest_activity.get('typing_speed', 0) if latest_activity else 0,
        'activity_level': latest_activity.get('key_presses', 0) if latest_activity else 0,
        'fatigue_status': latest_fatigue.get('fatigue_level', 'Not Analyzed') if latest_fatigue else 'Not Analyzed',
        'confidence': latest_fatigue.get('confidence', 0) if latest_fatigue else 0,
        'activities_today': today_activities,
        'avg_typing_speed': round(avg_typing_speed, 2)
    }), 200

@dashboard_bp.route('/api/chart-data')
def chart_data():
    """Get chart data for the dashboard"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get fatigue history (last 30 records)
    fatigue_history = db.get_fatigue_history(user_id, limit=30)
    
    labels = []
    fatigue_data = []
    
    for result in reversed(fatigue_history):
        timestamp = result.get('timestamp')
        if timestamp:
            labels.append(timestamp.strftime('%H:%M'))
        fatigue_level = result.get('fatigue_level', 'Low')
        fatigue_value = 1 if fatigue_level == 'Low' else 2 if fatigue_level == 'Medium' else 3
        fatigue_data.append(fatigue_value)
    
    # Get activity history
    activity_history = db.get_user_activity(user_id, limit=30)
    activity_labels = []
    typing_speeds = []
    
    for activity in reversed(activity_history):
        timestamp = activity.get('timestamp')
        if timestamp:
            activity_labels.append(timestamp.strftime('%H:%M'))
        typing_speeds.append(activity.get('typing_speed', 0))
    
    return jsonify({
        'success': True,
        'fatigue_chart': {
            'labels': labels,
            'data': fatigue_data
        },
        'typing_chart': {
            'labels': activity_labels,
            'data': typing_speeds
        }
    }), 200
