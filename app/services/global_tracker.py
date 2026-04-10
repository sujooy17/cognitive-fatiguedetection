import time
import threading
from pynput import keyboard

class GlobalTracker:
    def __init__(self):
        self.is_tracking = False
        self.key_presses = 0
        self.error_count = 0
        self.total_intervals = 0
        self.last_keypress_time = None
        self.start_time = None
        self.inactivity_duration = 0
        self.last_activity_time = time.time()
        
        self.listener = None

    def _on_press(self, key):
        if not self.is_tracking:
            return

        now = time.time()
        self.key_presses += 1
        
        # Inactivity reset
        self.last_activity_time = now

        # Error count (Backspace or Delete)
        if key == keyboard.Key.backspace or key == keyboard.Key.delete:
            self.error_count += 1

        # Intervals
        if self.last_keypress_time:
            self.total_intervals += (now - self.last_keypress_time)
        self.last_keypress_time = now

    def start(self):
        if self.is_tracking:
            return
            
        self.is_tracking = True
        self.key_presses = 0
        self.error_count = 0
        self.total_intervals = 0
        self.last_keypress_time = None
        
        if not self.start_time:
            self.start_time = time.time()
            
        self.last_activity_time = time.time()

        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()

    def pause(self):
        self.is_tracking = False

    def get_metrics_and_reset_interval(self):
        if not self.is_tracking and self.key_presses == 0:
            return None
            
        now = time.time()
        self.inactivity_duration = max(0, int(now - self.last_activity_time))
        
        session_elapsed_seconds = max(now - (self.start_time if self.start_time else now), 1)
        session_time = session_elapsed_seconds / 60.0
        
        # Instead of interval minutes, calculate typing speed based on a standard 30s block
        typing_speed = round((self.key_presses / 5.0) / 0.5)

        error_rate = (self.error_count / self.key_presses * 100.0) if self.key_presses > 0 else 0.0
        keypress_interval = (self.total_intervals / (self.key_presses - 1)) if self.key_presses > 1 else 0.0
        
        metrics = {
            'typing_speed': int(typing_speed),
            'inactivity_duration': int(self.inactivity_duration),
            'key_presses': self.key_presses,
            'error_rate': round(error_rate, 2),
            'keypress_interval': round(keypress_interval, 3),
            'session_time': round(session_time, 2),
            'is_tracking': self.is_tracking
        }
        
        # Reset interval counters
        if self.is_tracking:
            self.key_presses = 0
            self.error_count = 0
            self.total_intervals = 0
            self.last_keypress_time = None
            
        return metrics

# Singleton instance
tracker_instance = GlobalTracker()
