// Behavior Tracking Module
class BehaviorTracker {
    constructor() {
        this.isTracking = false;
        this.trackingInterval = null;
        this.trackingDuration = 30000; // 30 seconds for demo
        
        // Tracking metrics
        this.typingSpeed = 0;
        this.keyPresses = 0;
        this.startTime = null;
        this.inactivityDuration = 0;
        this.inactivityTimer = null;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Track key presses
        document.addEventListener('keydown', (e) => {
            if (this.isTracking) {
                this.keyPresses++;
                this.resetInactivityTimer();
            }
        });
        
        // Track clicks and reset inactivity timer
        document.addEventListener('click', () => {
            if (this.isTracking) {
                this.resetInactivityTimer();
            }
        });
    }
    
    resetInactivityTimer() {
        this.inactivityDuration = 0;
        if (this.inactivityTimer) {
            clearInterval(this.inactivityTimer);
        }
    }
    
    startTracking() {
        this.isTracking = true;
        this.keyPresses = 0;
        this.inactivityDuration = 0;
        this.typingSpeed = 0;
        this.startTime = Date.now();
        
        // Track inactivity
        if (this.inactivityTimer) {
            clearInterval(this.inactivityTimer);
        }
        this.inactivityTimer = setInterval(() => {
            if (this.isTracking) {
                this.inactivityDuration++;
            }
        }, 1000);
        
        // Send data to server every 30 seconds
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
        }
        this.trackingInterval = setInterval(() => {
            this.sendDataToServer();
        }, this.trackingDuration);
        
        console.log('Tracking started...');
    }
    
    async stopTracking() {
        this.isTracking = false;
        clearInterval(this.trackingInterval);
        clearInterval(this.inactivityTimer);
        
        // Send final data
        await this.sendDataToServer();
        
        // Trigger dashboard refresh using localStorage
        try {
            localStorage.setItem('dashboardRefreshTrigger', Date.now().toString());
        } catch (e) {
            console.warn('Could not use localStorage:', e);
        }
        
        console.log('Tracking stopped');
        console.log('Final metrics:', {
            typing_speed: this.typingSpeed,
            inactivity_duration: this.inactivityDuration,
            key_presses: this.keyPresses
        });
    }
    
    async sendDataToServer() {
        if (!this.isTracking && this.keyPresses === 0) return;

        const elapsedMilliseconds = Math.max(Date.now() - this.startTime, 1000);
        const elapsedMinutes = elapsedMilliseconds / 60000;
        this.typingSpeed = Math.round((this.keyPresses / 5) / elapsedMinutes);

        try {
            const response = await fetch('/api/track-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    typing_speed: this.typingSpeed,
                    inactivity_duration: this.inactivityDuration,
                    key_presses: this.keyPresses
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Data tracked successfully!');
                console.log('Fatigue Level:', data.fatigue_level);
                console.log('Confidence:', data.confidence + '%');
                
                // Update UI with fatigue result
                updateFatigueUI(data.fatigue_level, data.confidence);
                
                // Reset counters for next interval
                if (this.isTracking) {
                    this.keyPresses = 0;
                    this.inactivityDuration = 0;
                    this.startTime = Date.now();
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error tracking data:', error);
            return false;
        }
    }
    
    getMetrics() {
        return {
            typing_speed: Math.round(this.typingSpeed),
            inactivity_duration: this.inactivityDuration,
            key_presses: this.keyPresses
        };
    }
}

// Initialize tracker
const tracker = new BehaviorTracker();

// Global tracking functions
function startTracking() {
    tracker.startTracking();
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const trackingStatus = document.getElementById('trackingStatus');
    
    if (startBtn) startBtn.style.display = 'none';
    if (stopBtn) stopBtn.style.display = 'inline-block';
    if (trackingStatus) trackingStatus.classList.add('active');
    
    showNotification('Monitoring started! Your behavior is being tracked.', 'success');
}

function stopTracking() {
    tracker.stopTracking();
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const trackingStatus = document.getElementById('trackingStatus');
    
    if (stopBtn) stopBtn.style.display = 'none';
    if (trackingStatus) trackingStatus.classList.remove('active');
    if (startBtn) {
        setTimeout(() => {
            startBtn.style.display = 'inline-block';
        }, 500);
    }
    
    showNotification('Monitoring stopped. Data has been saved.', 'info');
}

function updateFatigueUI(fatigueLevel, confidence) {
    const statusElement = document.getElementById('fatigueStatus');
    const badgeElement = document.getElementById('fatigueBadge');
    const confidenceFill = document.getElementById('confidenceFill');
    
    statusElement.textContent = fatigueLevel;
    
    // Update confidence meter
    confidenceFill.style.width = confidence + '%';
    
    // Update badge styling
    badgeElement.textContent = fatigueLevel + ' (' + confidence + '%)';
    badgeElement.className = 'fatigue-badge fatigue-' + fatigueLevel.toLowerCase();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? 'rgba(40, 167, 69, 0.2)' : 'rgba(23, 162, 184, 0.2)'};
        border: 1px solid ${type === 'success' ? 'rgba(40, 167, 69, 0.5)' : 'rgba(23, 162, 184, 0.5)'};
        color: ${type === 'success' ? '#6bff9d' : '#6bffff'};
        border-radius: 10px;
        z-index: 10000;
        animation: slideRight 0.3s ease-out;
        font-family: 'Poppins', sans-serif;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideLeft 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add animation styles to body once
if (!document.getElementById('tracking-style')) {
    const style = document.createElement('style');
    style.id = 'tracking-style';
    style.textContent = `
        @keyframes slideRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideLeft {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(30px);
            }
        }
    `;
    document.head.appendChild(style);
}
