from flask import Blueprint, request, jsonify, session
from app.models.db import get_db
from app.services.global_tracker import tracker_instance
import math
import pickle
import os
import pandas as pd

tracking_bp = Blueprint('tracking', __name__)
db = get_db()

# Load ML model
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model.pkl')
try:
    with open(model_path, 'rb') as f:
        fatigue_model = pickle.load(f)
except FileNotFoundError:
    fatigue_model = None

def analyze_fatigue(typing_speed, error_rate, keypress_interval, session_time, inactivity_duration, key_presses):
    """
    Analyze fatigue level using the trained ML model.
    """
    metrics = {
        'typing_speed': typing_speed,
        'inactivity_duration': inactivity_duration,
        'key_presses': key_presses,
        'error_rate': error_rate,
        'keypress_interval': keypress_interval,
        'session_time': session_time
    }
    
    if fatigue_model is not None:
        try:
            # Predict
            df = pd.DataFrame([{
                'typing_speed': typing_speed,
                'error_rate': error_rate,
                'keypress_interval': keypress_interval,
                'session_time': session_time
            }])
            fatigue_pred = fatigue_model.predict(df)[0]
            
            if fatigue_pred == 1:
                fatigue_level = 'High'
                fatigue_score = 85
                recommendation = "Take a 5-10 minute break. Relax your eyes and stretch your hands. Avoid continuous typing."
            else:
                fatigue_level = 'Low'
                fatigue_score = 20
                recommendation = "You are in normal condition. Keep up the good work and maintain your current pace."
                
            confidence = 85 # Simulated confidence from ML model
        except Exception as e:
            print(f"Prediction error: {e}")
            fatigue_level, confidence, metrics = analyze_fatigue_heuristic(typing_speed, inactivity_duration, key_presses)
            fatigue_score = metrics.get('raw_score', 50)
            recommendation = metrics.get('recommendation', '')
    else:
        fatigue_level, confidence, metrics = analyze_fatigue_heuristic(typing_speed, inactivity_duration, key_presses)
        fatigue_score = metrics.get('raw_score', 50)
        recommendation = metrics.get('recommendation', '')

    metrics['raw_score'] = fatigue_score
    metrics['recommendation'] = recommendation
    
    return fatigue_level, confidence, metrics

def analyze_fatigue_heuristic(typing_speed, inactivity_duration, key_presses):
    """
    Original heuristic logic as fallback
    """
    fatigue_score = 0
    metrics = {
        'typing_speed': typing_speed,
        'inactivity_duration': inactivity_duration,
        'key_presses': key_presses
    }
    
    if typing_speed < 25:
        fatigue_score += 30
    elif typing_speed < 40:
        fatigue_score += 15
    elif typing_speed > 70:
        fatigue_score -= 10
    
    if key_presses < 20:
        fatigue_score += 25
    elif key_presses < 80:
        fatigue_score += 10
    
    if inactivity_duration > 300:
        fatigue_score += 25
    elif inactivity_duration > 60:
        fatigue_score += 15
    
    fatigue_score = max(0, min(100, fatigue_score))
    
    if fatigue_score < 30:
        fatigue_level = 'Low'
    elif fatigue_score < 65:
        fatigue_level = 'Medium'
    else:
        fatigue_level = 'High'
    
    confidence = 75 + min(25, max(0, (key_presses - 20) // 6))
    
    if fatigue_level == 'Low':
        recommendation = "Stress State: Low. You are in optimal flow! Maintain your current pace and posture."
    elif fatigue_level == 'Medium':
        recommendation = "Stress State: Medium. Your focus is dropping. Try the 20-20-20 rule and drink some water."
    else:
        recommendation = "Stress State: High. You are exhausted! Step away from the screen and take a 10-15 minute physical break to recover."

    metrics['raw_score'] = fatigue_score
    metrics['recommendation'] = recommendation
    
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
        error_rate = data.get('error_rate', 0)
        keypress_interval = data.get('keypress_interval', 0.5)
        session_time = data.get('session_time', 0)
        
        # Save activity log
        log_id = db.save_activity_log(
            user_id,
            typing_speed,
            inactivity_duration,
            key_presses,
            error_rate=error_rate,
            keypress_interval=keypress_interval,
            session_time=session_time
        )
        
        # Analyze fatigue using ML Model
        fatigue_level, confidence, metrics = analyze_fatigue(
            typing_speed,
            error_rate,
            keypress_interval,
            session_time,
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

@tracking_bp.route('/api/global-action', methods=['POST'])
def global_action():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    action = request.json.get('action')
    if action == 'start':
        tracker_instance.start()
    elif action == 'pause':
        tracker_instance.pause()
    return jsonify({'success': True, 'state': tracker_instance.is_tracking})

@tracking_bp.route('/api/global-metrics', methods=['GET'])
def global_metrics():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    metrics = tracker_instance.get_metrics_and_reset_interval()
    if not metrics:
        return jsonify({'success': False, 'metrics': None})
        
    return jsonify({'success': True, 'metrics': metrics})

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
        'raw_score': result.get('metrics', {}).get('raw_score', '--'),
        'recommendation': result.get('metrics', {}).get('recommendation', 'Keep working efficiently!'),
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
