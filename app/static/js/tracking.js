// Behavior Tracking Module
class BehaviorTracker {
    constructor() {
        this.isTracking = false;
        this.trackingInterval = null;
        this.trackingDuration = 5000; // 5 seconds for rapid feedback
        
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
    
    async stopTracking() {
        this.isTracking = false;
        clearInterval(this.trackingInterval);
        
        try {
            await fetch('/api/global-action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'stop' })
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
        
        console.log('Global Tracking stopped');
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

                // AI Recommendations Alert
                if (data.fatigue_level === 'High' && data.recommendation) {
                    const lastAlertTime = parseInt(localStorage.getItem('lastFatigueAlertTime') || '0');
                    const now = Date.now();
                    // Alert once every 5 minutes max
                    if (now - lastAlertTime > 5 * 60 * 1000) {
                        showGlobalModal('High Cognitive Fatigue Detected!', data.recommendation, 'danger');
                        localStorage.setItem('lastFatigueAlertTime', now.toString());
                    }
                }
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

// Sync global tracker state silently on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/global-metrics');
        const data = await response.json();
        if (data.success && data.metrics && data.metrics.is_tracking) {
            tracker.isTracking = true;
            if (!tracker.trackingInterval) {
                tracker.trackingInterval = setInterval(() => {
                    tracker.sendDataToServer();
                }, tracker.trackingDuration);
            }
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
        }
    } catch (e) {}
});

// Global tracking functions
function startTracking(isAutoStart = false) {
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
    
    // Only show modal if it's explicitly started via button OR hasn't been shown in this active tab session
    if (!isAutoStart || !sessionStorage.getItem('trackerModalShown')) {
        showGlobalModal('Background Tracking Started', 'Your typing patterns and interactions are now being globally monitored by the OS to protect against cognitive fatigue.', 'success');
        sessionStorage.setItem('trackerModalShown', 'true');
    }
}

function stopTracking() {
    tracker.stopTracking();
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const trackingStatus = document.getElementById('trackingStatus');
    
    if (stopBtn) stopBtn.style.display = 'none';
    if (trackingStatus) {
        trackingStatus.innerHTML = '<i class="fas fa-stop-circle" style="color: #f59e0b; margin-right: 6px;"></i><span>Monitoring Stopped</span>';
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
    
    showGlobalModal('Tracking Stopped', 'Global OS Monitoring has been securely stopped. Your activities are no longer being logged.', 'warning');
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

function showGlobalModal(title, text, type = 'info') {
    const modal = document.getElementById('globalAlertModal');
    const icon = document.getElementById('alertModalIcon');
    const titleEl = document.getElementById('alertModalTitle');
    const textEl = document.getElementById('alertModalText');
    const btn = document.getElementById('alertModalBtn');

    if (!modal) return;

    titleEl.textContent = title;
    textEl.textContent = text;

    if (type === 'success') {
        icon.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i>';
        btn.style.background = '#10b981';
    } else if (type === 'danger') {
        icon.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>';
        btn.style.background = '#ef4444';
    } else if (type === 'warning') {
        icon.innerHTML = '<i class="fas fa-exclamation-circle" style="color: #f59e0b;"></i>';
        btn.style.background = '#f59e0b';
    } else {
        icon.innerHTML = '<i class="fas fa-info-circle" style="color: #3b82f6;"></i>';
        btn.style.background = '#3b82f6';
    }

    modal.classList.add('active');
}

function closeGlobalModal() {
    const modal = document.getElementById('globalAlertModal');
    if (modal) modal.classList.remove('active');
}

// Make accessible globally
window.closeGlobalModal = closeGlobalModal;

function showNotification(message, type = 'info') {
    let title = 'Information';
    if (type === 'success') title = 'Tracking Activated';
    if (type === 'warning' || type === 'info') title = 'Status Update';

    showGlobalModal(title, message, type);
}

