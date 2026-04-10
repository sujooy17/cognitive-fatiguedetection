from datetime import datetime, timedelta
import math

class ReminderEngine:
    """
    Local AI/Heuristic model to analyze user cognitive activity data
    and provide intelligent personalized insights and reminders.
    """
    
    def __init__(self, activity_logs, fatigue_results):
        self.logs = activity_logs
        self.fatigue_results = fatigue_results
        self.now = datetime.now()
    
    def generate_insights(self):
        insights = []
        
        # Helper to get the icon based on category
        def add_insight(title, message, icon_class, border_type="secondary"):
            insights.append({
                "title": title,
                "message": message,
                "icon": icon_class,
                "type": border_type
            })
            
        if not self.logs and not self.fatigue_results:
            add_insight("Welcome", "Start tracking your activity to generate personalized insights.", "fas fa-rocket", "secondary")
            return insights

        # Analyze activity logs
        if self.logs:
            recent_logs = [l for l in self.logs if (self.now - l.get('timestamp', self.now)).total_seconds() < 24*3600]
            if recent_logs:
                avg_typing = sum(l.get('typing_speed', 0) for l in recent_logs) / len(recent_logs)
                max_inactive = max(l.get('inactivity_duration', 0) for l in recent_logs)
                
                if avg_typing > 60:
                    add_insight("High Performance", "Your typing speed is consistently high today! Keep up the good work but don't overexert yourself.", "fas fa-bolt", "success")
                elif avg_typing < 30 and len(recent_logs) > 5:
                    add_insight("Take a Breather", "Your typing speed trends lower recently. A quick 5-minute break could significantly boost your focus.", "fas fa-coffee", "warning")
                
                if max_inactive > 1800: # 30 minutes
                    add_insight("Good Rest", "We noticed you took a substantial break recently. Proper pacing prevents complete cognitive fatigue.", "fas fa-bed", "success")
                elif len(recent_logs) > 10 and max_inactive < 300: # 5 minutes
                    add_insight("Continuous Strain", "You've been working continuously without significant breaks. Follow the 20-20-20 rule to rest your eyes.", "fas fa-eye", "warning")

        # Analyze fatigue trends
        if self.fatigue_results:
            recent_fatigue = sorted([f for f in self.fatigue_results if (self.now - f.get('timestamp', self.now)).total_seconds() < 24*3600], key=lambda x: x.get('timestamp', self.now))
            if recent_fatigue:
                high_fatigue_count = sum(1 for f in recent_fatigue if f.get('fatigue_level') == 'High')
                if high_fatigue_count > 0:
                    add_insight("Elevated Fatigue Detected", f"We've detected high fatigue {high_fatigue_count} times recently. Please consider ending heavy cognitive tasks for the day.", "fas fa-exclamation-triangle", "danger")
                
                # Check timeframe of highest fatigue
                if len(recent_fatigue) > 3:
                    fatigue_peaks = [f for f in recent_fatigue if f.get('fatigue_level') in ['High', 'Medium']]
                    if fatigue_peaks:
                        peak_hour = list(fatigue_peaks)[-1].get('timestamp').hour
                        time_str = "Morning" if peak_hour < 12 else "Afternoon" if peak_hour < 17 else "Evening"
                        add_insight("Fatigue Pattern", f"Your fatigue tends to peak in the {time_str}. Try scheduling demanding work outside this window.", "fas fa-chart-line", "secondary")

        # Fallback general insights if we don't have exactly 3 insights yet
        if len(insights) == 0:
            add_insight("Consistency", "Your working patterns are currently stable. Keep maintaining regular intervals.", "fas fa-check-circle", "secondary")
            
        # Limit to top 4 insights
        return insights[:4]
