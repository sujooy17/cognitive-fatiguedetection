// Behavior Tracking Module
class BehaviorTracker {
    constructor() {
        this.isTracking = false;
        this.trackingInterval = null;
        this.trackingDuration = 30000; // 30 seconds for demo
        
        // Tracking metrics
        this.typingSpeed = 0;
        this.keyPresses = 0;
        this.errorCount = 0;
        this.startTime = null;
        this.lastKeyPressTime = null;
        this.totalIntervals = 0;
        this.inactivityDuration = 0;
        this.inactivityTimer = null;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Core tracking shifted to backend Python Global Tracker (pynput)
    }
    
    resetInactivityTimer() {
        // Managed by global tracker
    }
    
    async startTracking() {
        this.isTracking = true;
        
        try {
            await fetch('/api/global-action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'start' })
            });
        } catch(e) {
            console.error(e);
        }
        
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
        }
        
        this.trackingInterval = setInterval(() => {
            this.sendDataToServer();
        }, this.trackingDuration);
        
        console.log('Global Tracking started...');
    }
    
    async pauseTracking() {
        this.isTracking = false;
        clearInterval(this.trackingInterval);
        
        try {
            await fetch('/api/global-action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'pause' })
            });
        } catch(e) {
            console.error(e);
        }
        
        // Trigger dashboard refresh using localStorage
        try {
            localStorage.setItem('dashboardRefreshTrigger', Date.now().toString());
        } catch (e) {
            console.warn('Could not use localStorage:', e);
        }
        
        console.log('Global Tracking paused');
    }
    
    async sendDataToServer() {
        if (!this.isTracking) return;

        try {
            // Poll for OS-wide global interactions from background Python threads
            const metricsReq = await fetch('/api/global-metrics');
            const metricsRes = await metricsReq.json();
            
            if (!metricsRes.success || !metricsRes.metrics) return;
            const globalData = metricsRes.metrics;

            // Transmit Global OS Stats directly to ML predictor
            const response = await fetch('/api/track-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(globalData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Global Data tracked successfully!');
                console.log('Fatigue Level:', data.fatigue_level);
                
                // Update UI with fatigue result
                updateFatigueUI(data.fatigue_level, data.confidence);
            }
            
            return true;
        } catch (error) {
            console.error('Error tracking data:', error);
            return false;
        }
    }
    
    getMetrics() {
        return {};
    }
}

// Initialize tracker
const tracker = new BehaviorTracker();

// Auto start tracking automatically
document.addEventListener('DOMContentLoaded', () => {
    startTracking();
});

// Global tracking functions
function startTracking() {
    tracker.startTracking();
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const trackingStatus = document.getElementById('trackingStatus');
    
    if (startBtn) startBtn.style.display = 'none';
    if (stopBtn) stopBtn.style.display = 'inline-block';
    if (trackingStatus) {
        trackingStatus.innerHTML = '<i class="fas fa-dot-circle" style="color: #10b981; margin-right: 6px; animation: pulse 2s infinite;"></i><span>Monitoring Active</span>';
        trackingStatus.style.background = 'rgba(16, 185, 129, 0.15)';
        trackingStatus.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        trackingStatus.style.color = '#10b981';
        trackingStatus.classList.add('active');
    }
    
    showNotification('Global OS Monitoring started! Your typing across all apps is being tracked.', 'success');
}

function pauseTracking() {
    tracker.pauseTracking();
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const trackingStatus = document.getElementById('trackingStatus');
    
    if (stopBtn) stopBtn.style.display = 'none';
    if (trackingStatus) {
        trackingStatus.innerHTML = '<i class="fas fa-pause-circle" style="color: #f59e0b; margin-right: 6px;"></i><span>Monitoring Paused</span>';
        trackingStatus.style.background = 'rgba(245, 158, 11, 0.15)';
        trackingStatus.style.borderColor = 'rgba(245, 158, 11, 0.3)';
        trackingStatus.style.color = '#f59e0b';
        trackingStatus.classList.remove('active');
    }
    if (startBtn) {
        setTimeout(() => {
            startBtn.style.display = 'inline-block';
        }, 500);
    }
    
    showNotification('Global OS Monitoring paused.', 'info');
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
