from flask import Blueprint, request, jsonify, session
from app.models.db import get_db
import math

tracking_bp = Blueprint('tracking', __name__)
db = get_db()

def analyze_fatigue(typing_speed, inactivity_duration, key_presses):
    """
    Analyze fatigue level based on user behavior patterns
    Returns: fatigue_level (Low/Medium/High), confidence (0-100)
    """
    
    fatigue_score = 0
    metrics = {
        'typing_speed': typing_speed,
        'inactivity_duration': inactivity_duration,
        'key_presses': key_presses
    }
    
    # Typing speed analysis (Low typing speed indicates fatigue)
    if typing_speed < 25:
        fatigue_score += 30
    elif typing_speed < 40:
        fatigue_score += 15
    elif typing_speed > 70:
        fatigue_score -= 10
    
    # Key presses activity
    if key_presses < 20:
        fatigue_score += 25
    elif key_presses < 80:
        fatigue_score += 10
    
    # Inactivity analysis (High inactivity indicates fatigue)
    if inactivity_duration > 300:  # 5 minutes
        fatigue_score += 25
    elif inactivity_duration > 60:  # 1 minute
        fatigue_score += 15
    
    # Normalize score to 0-100
    fatigue_score = max(0, min(100, fatigue_score))
    
    # Determine fatigue level
    if fatigue_score < 30:
        fatigue_level = 'Low'
    elif fatigue_score < 65:
        fatigue_level = 'Medium'
    else:
        fatigue_level = 'High'
    
    confidence = 75 + min(25, max(0, (key_presses - 20) // 6))  # 75-100% confidence
    
    return fatigue_level, confidence, metrics

@tracking_bp.route('/api/track-data', methods=['POST'])
def track_data():
    """Receive tracking data from frontend"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        typing_speed = data.get('typing_speed', 0)
        inactivity_duration = data.get('inactivity_duration', 0)
        key_presses = data.get('key_presses', 0)
        
        # Save activity log
        log_id = db.save_activity_log(
            user_id,
            typing_speed,
            inactivity_duration,
            key_presses
        )
        
        # Analyze fatigue
        fatigue_level, confidence, metrics = analyze_fatigue(
            typing_speed,
            inactivity_duration,
            key_presses
        )
        
        # Save fatigue result
        result_id = db.save_fatigue_result(user_id, fatigue_level, confidence, metrics)
        
        return jsonify({
            'success': True,
            'message': 'Data tracked successfully',
            'fatigue_level': fatigue_level,
            'confidence': confidence,
            'log_id': log_id,
            'result_id': result_id
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@tracking_bp.route('/api/fatigue-result', methods=['GET'])
def get_fatigue_result():
    """Get latest fatigue result"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    result = db.get_latest_fatigue_result(user_id)
    
    if not result:
        return jsonify({
            'success': True,
            'fatigue_level': 'Not Analyzed',
            'confidence': 0
        }), 200
    
    return jsonify({
        'success': True,
        'fatigue_level': result.get('fatigue_level'),
        'confidence': result.get('confidence'),
        'timestamp': result.get('timestamp').isoformat() if result.get('timestamp') else None
    }), 200

@tracking_bp.route('/api/activity-logs')
def get_activity_logs():
    """Get user's activity logs"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    limit = request.args.get('limit', 50, type=int)
    
    logs = db.get_user_activity(user_id, limit=limit)
    
    # Convert to JSON serializable format
    for log in logs:
        log['_id'] = str(log['_id'])
        log['timestamp'] = log['timestamp'].isoformat() if log.get('timestamp') else None
    
    return jsonify({
        'success': True,
        'logs': logs
    }), 200

@tracking_bp.route('/api/historical-chart-data')
def get_historical_chart_data():
    """Get historical chart data from past activities"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    from datetime import datetime, timedelta
    
    user_id = session['user_id']
    
    # Get activity logs from last 24 hours
    logs = db.get_user_activity(user_id, limit=200)
    
    if not logs:
        return jsonify({
            'success': False,
            'message': 'No activity data available'
        }), 200
    
    # Filter logs from last 24 hours and organize by 1-hour intervals
    now = datetime.utcnow()
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    # Initialize 12 time intervals (2-hour intervals)
    time_intervals = []
    interval_data = {}
    
    for i in range(12, -1, -1):
        interval_time = now - timedelta(hours=i*2)
        time_label = interval_time.strftime('%H:%M')
        time_intervals.append(time_label)
        interval_data[time_label] = {
            'typing_speeds': [],
            'fatigue_levels': [],
            'key_presses': [],
            'inactivity_durations': []
        }
    
    # Process logs and group by intervals
    for log in logs:
        log_time = log.get('timestamp')
        if not log_time:
            continue
            
        if log_time < twenty_four_hours_ago:
            continue
        
        # Find which interval this log belongs to
        hours_ago = (now - log_time).total_seconds() / 3600
        interval_index = min(int(hours_ago / 2), 11)
        interval_label = time_intervals[interval_index]
        
        # Collect metrics
        if log.get('typing_speed'):
            interval_data[interval_label]['typing_speeds'].append(log.get('typing_speed', 0))
        if log.get('key_presses'):
            interval_data[interval_label]['key_presses'].append(log.get('key_presses', 0))
        if log.get('inactivity_duration'):
            interval_data[interval_label]['inactivity_durations'].append(log.get('inactivity_duration', 0))
        if log.get('fatigue_level'):
            fatigue_val = {'Low': 1, 'Medium': 2, 'High': 3}.get(log.get('fatigue_level'), 1)
            interval_data[interval_label]['fatigue_levels'].append(fatigue_val)
    
    # Calculate averages for each interval
    fatigue_chart_data = []
    typing_chart_data = []
    
    for label in time_intervals:
        data = interval_data[label]
        
        # Average fatigue level
        avg_fatigue = sum(data['fatigue_levels']) / len(data['fatigue_levels']) if data['fatigue_levels'] else 1
        fatigue_chart_data.append(round(avg_fatigue, 2))
        
        # Average typing speed
        avg_typing = sum(data['typing_speeds']) / len(data['typing_speeds']) if data['typing_speeds'] else 50
        typing_chart_data.append(round(avg_typing, 2))
    
    return jsonify({
        'success': True,
        'fatigue_chart': {
            'labels': time_intervals,
            'data': fatigue_chart_data
        },
        'typing_chart': {
            'labels': time_intervals,
            'data': typing_chart_data
        }
    }), 200

@tracking_bp.route('/api/activity-logs/delete/all', methods=['DELETE'])
def delete_all_activity_logs():
    """Delete all activity logs for the user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    try:
        # Delete all logs for this user
        result = db.delete_all_user_activity_logs(user_id)
        
        return jsonify({
            'success': True,
            'message': f'Deleted {result.deleted_count} activity logs',
            'deleted_count': result.deleted_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@tracking_bp.route('/api/activity-logs/<log_id>', methods=['DELETE'])
def delete_activity_log(log_id):
    """Delete a specific activity log"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    from bson import ObjectId
    user_id = session['user_id']
    
    try:
        # Delete the specific log
        result = db.delete_activity_log(user_id, ObjectId(log_id))
        
        if result.deleted_count > 0:
            return jsonify({
                'success': True,
                'message': 'Activity log deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Activity log not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
