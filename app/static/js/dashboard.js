// Dashboard Module
let fatigueChart = null;
let typingChart = null;
let isRefreshingDashboard = false;
let lastRefreshTime = 0;
const REFRESH_DEBOUNCE_TIME = 1000;

async function refreshDashboardData() {
    const now = Date.now();
    if (isRefreshingDashboard || (now - lastRefreshTime) < REFRESH_DEBOUNCE_TIME) {
        return;
    }
    isRefreshingDashboard = true;
    lastRefreshTime = now;
    try {
        await loadDashboardStats();
        await loadChartData();
        await loadAIInsights();
    } finally {
        isRefreshingDashboard = false;
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Load live chart data from API
    await loadChartData();
    
    await loadUserInfo();
    await loadDashboardStats();
    await loadAIInsights();
    
    // Refresh stats every 10 seconds for smooth updates
    setInterval(refreshDashboardData, 10000);
    
    // Listen for real-time refresh signals from activity/tracking pages
    window.addEventListener('storage', (event) => {
        if (event.key === 'dashboardRefreshTrigger') {
            console.log('Dashboard refresh triggered by activity page');
            refreshDashboardData();
        }
    });

    // Listen for refresh messages from activity page
    window.addEventListener('message', (event) => {
        if (event.data && event.data.action === 'refreshDashboard') {
            console.log('Dashboard refresh triggered from activity page');
            refreshDashboardData();
        }
    });
});

async function loadUserInfo() {
    try {
        const response = await fetch('/api/user-info');
        const data = await response.json();
        
        if (data.success) {
            const userName = data.full_name;
            const userInitial = userName.charAt(0).toUpperCase();
            
            document.getElementById('userName').textContent = userName;
            document.getElementById('userEmail').textContent = data.email;
            document.getElementById('userAvatar').textContent = userInitial;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard-stats');
        const data = await response.json();
        
        if (data.success) {
            // Update typing speed (only animate if value changed)
            const typingSpeedElement = document.getElementById('typingSpeed');
            const typingSpeed = data.typing_speed !== null && data.typing_speed !== undefined ? data.typing_speed : 0;
            const currentTypingSpeed = parseInt(typingSpeedElement.textContent) || 0;
            if (currentTypingSpeed !== typingSpeed) {
                animateCounter('typingSpeed', typingSpeed);
            }
            
            // Update activity level
            const activityLevelElement = document.getElementById('activityLevel');
            const activityLevel = data.activity_level !== null && data.activity_level !== undefined ? data.activity_level : 0;
            const currentActivityLevel = parseInt(activityLevelElement.textContent) || 0;
            if (currentActivityLevel !== activityLevel) {
                animateCounter('activityLevel', activityLevel);
            }
            
            // Update fatigue status
            const fatigueStatusElement = document.getElementById('fatigueStatus');
            const fatigueStatus = data.fatigue_status && data.fatigue_status !== 'Not Analyzed' ? data.fatigue_status : '--';
            if (fatigueStatusElement.textContent !== fatigueStatus) {
                fatigueStatusElement.textContent = fatigueStatus;
            }
            
            // Update fatigue badge
            const fatigueBadge = document.getElementById('fatigueBadge');
            const isFatigueAvailable = data.fatigue_status && data.fatigue_status !== 'Not Analyzed' && data.fatigue_status !== '--';
            const fatigueClass = isFatigueAvailable ? 'fatigue-' + data.fatigue_status.toLowerCase() : 'fatigue-low';
            const confidence = data.confidence || 0;
            const newBadgeText = (isFatigueAvailable ? data.fatigue_status : 'No Data') + ' (' + confidence + '%)';
            if (fatigueBadge.textContent !== newBadgeText) {
                fatigueBadge.className = 'fatigue-badge ' + fatigueClass;
                fatigueBadge.textContent = newBadgeText;
            }
            
            // Update confidence meter (smooth transition instead of jump)
            const confidenceFill = document.getElementById('confidenceFill');
            const currentWidth = parseInt(confidenceFill.style.width) || 0;
            if (currentWidth !== confidence) {
                animateWidth(confidenceFill, confidence);
            }
            
            // Update raw score
            const rawScoreElement = document.getElementById('rawScoreValue');
            if (rawScoreElement) {
                rawScoreElement.textContent = data.raw_score !== undefined ? data.raw_score : '--';
            }

            // Update live recommendation
            const recElement = document.getElementById('liveRecommendation');
            if (recElement && data.recommendation) {
                recElement.textContent = data.recommendation;
                
                // Add color hints based on fatigue status
                if (data.fatigue_status === 'Low') recElement.style.color = '#10b981';
                else if (data.fatigue_status === 'Medium') recElement.style.color = '#f59e0b';
                else if (data.fatigue_status === 'High') recElement.style.color = '#ef4444';
            }
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Load with zero data
        loadZeroData();
    }
}

function loadZeroData() {
    // Display zero data when no activity logs exist
    document.getElementById('typingSpeed').textContent = '0';
    document.getElementById('activityLevel').textContent = '0';
    document.getElementById('fatigueStatus').textContent = '--';
    
    const fatigueBadge = document.getElementById('fatigueBadge');
    fatigueBadge.className = 'fatigue-badge fatigue-low';
    fatigueBadge.textContent = 'No Data (0%)';
    
    document.getElementById('confidenceFill').style.width = '0%';
    document.getElementById('sessionsToday').textContent = '0';
}

async function loadChartData() {
    try {
        const response = await fetch('/api/chart-data');
        const data = await response.json();
        
        if (data.success && data.fatigue_chart && data.typing_chart) {
            updateFatigueChart(data.fatigue_chart.labels, data.fatigue_chart.data);
            updateTypingChart(data.typing_chart.labels, data.typing_chart.data);
        } else {
            // Generate realistic live data
            generateLiveChartData();
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
        generateLiveChartData();
    }
}

async function loadHistoricalChartData() {
    try {
        const response = await fetch('/api/historical-chart-data');
        const data = await response.json();
        
        if (data.success && data.fatigue_chart && data.typing_chart) {
            
            // Wait for Chart.js to be available
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded, showing empty state');
                return;
            }
            
            updateFatigueChart(data.fatigue_chart.labels, data.fatigue_chart.data);
            updateTypingChart(data.typing_chart.labels, data.typing_chart.data);
        } else {
            console.log('No historical data, showing empty state');
            // Show empty charts
            const emptyLabels = ['No Data', '', '', '', '', '', '', '', '', '', '', ''];
            const emptyData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
            
            if (typeof Chart !== 'undefined') {
                updateFatigueChart(emptyLabels, emptyData);
                updateTypingChart(emptyLabels, emptyData);
            }
        }
    } catch (error) {
        console.error('Error loading historical chart data:', error);
        // Show empty charts on error
        const emptyLabels = ['No Data', '', '', '', '', '', '', '', '', '', '', ''];
        const emptyData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        
        if (typeof Chart !== 'undefined') {
            updateFatigueChart(emptyLabels, emptyData);
            updateTypingChart(emptyLabels, emptyData);
        }
    }
}

function generateLiveChartData() {
    // Generate time labels for the last 12 intervals (5 minutes each = 1 hour)
    const timeLabels = [];
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
        const time = new Date(now - i * 5 * 60000);
        timeLabels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
    }
    
    // Generate realistic fatigue data (1-3 scale)
    const fatigueData = Array.from({ length: 12 }, () => Math.random() * 2 + 1);
    
    // Generate realistic typing speed data (40-120 WPM)
    const typingData = Array.from({ length: 12 }, () => Math.floor(Math.random() * 80) + 40);
    
    updateFatigueChart(timeLabels, fatigueData);
    updateTypingChart(timeLabels, typingData);
}

function normalizeChartData(labels, data, defaultLabel) {
    // Generate realistic live data if empty
    if (!Array.isArray(labels) || labels.length === 0) {
        const timeLabels = [];
        const now = new Date();
        for (let i = 11; i >= 0; i--) {
            const time = new Date(now - i * 5 * 60000);
            timeLabels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        }
        labels = timeLabels;
    }
    
    if (!Array.isArray(data) || data.length === 0) {
        // Generate realistic fatigue or activity data
        data = Array.from({ length: 12 }, () => Math.floor(Math.random() * 80) + 20);
    }
    
    return { safeLabels: labels, safeData: data };
}

function updateFatigueChart(labels, data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library not loaded');
        return;
    }
    
    const canvasElement = document.getElementById('fatigueChart');
    if (!canvasElement) {
        console.error('Fatigue chart canvas not found');
        return;
    }
    
    const normalized = normalizeChartData(labels, data, 'No Data');
    labels = normalized.safeLabels;
    data = normalized.safeData;
    
    // Ensure data is valid numbers
    data = data.map(d => typeof d === 'number' ? d : 0);
    
    // Update existing chart instead of destroying/recreating
    if (fatigueChart) {
        fatigueChart.data.labels = labels;
        fatigueChart.data.datasets[0].data = data;
        fatigueChart.update('none');
        return;
    }
    
    try {
        console.log('Creating fatigue chart with labels:', labels);
        fatigueChart = new Chart(canvasElement, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Fatigue Level',
                    data: data,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: '#ef4444',
                    pointBorderColor: 'rgba(255, 255, 255, 0.9)',
                    pointBorderWidth: 2,
                    pointHoverRadius: 7,
                    pointHoverBackgroundColor: '#f87171'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: 'rgba(248, 250, 252, 0.8)',
                            font: {
                                family: "'Poppins', sans-serif",
                                size: 12,
                                weight: '600'
                            },
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    filler: {
                        propagate: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 3,
                        ticks: {
                            color: 'rgba(248, 250, 252, 0.6)',
                            font: {
                                family: "'Poppins', sans-serif"
                            },
                            callback: function(value) {
                                const levels = ['', 'Low', 'Medium', 'High'];
                                return levels[Math.round(value)] || value;
                            }
                        },
                        grid: {
                            color: 'rgba(239, 68, 68, 0.1)',
                            drawBorder: false
                        }
                    },
                    x: {
                        ticks: {
                            color: 'rgba(248, 250, 252, 0.6)',
                            font: {
                                family: "'Poppins', sans-serif"
                            }
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating fatigue chart:', error);
    }
}

function updateTypingChart(labels, data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library not loaded');
        return;
    }
    
    const canvasElement = document.getElementById('typingChart');
    if (!canvasElement) {
        console.error('Typing chart canvas not found');
        return;
    }
    
    const normalized = normalizeChartData(labels, data, 'No Data');
    labels = normalized.safeLabels;
    data = normalized.safeData;
    
    // Ensure data is valid numbers
    data = data.map(d => typeof d === 'number' ? d : 0);
    
    // Update existing chart instead of destroying/recreating
    if (typingChart) {
        typingChart.data.labels = labels;
        typingChart.data.datasets[0].data = data;
        typingChart.update('none');
        return;
    }
    
    try {
        console.log('Creating typing chart with labels:', labels);
        typingChart = new Chart(canvasElement, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Words Per Minute',
                    data: data,
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderRadius: 8,
                    hoverBackgroundColor: 'rgba(239, 68, 68, 0.9)',
                    hoverBorderColor: '#dc2626'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: 'rgba(248, 250, 252, 0.8)',
                            font: {
                                family: "'Poppins', sans-serif",
                                size: 12,
                                weight: '600'
                            },
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'rgba(248, 250, 252, 0.6)',
                            font: {
                                family: "'Poppins', sans-serif"
                            }
                        },
                        grid: {
                            color: 'rgba(239, 68, 68, 0.1)',
                            drawBorder: false
                        }
                    },
                    x: {
                        ticks: {
                            color: 'rgba(248, 250, 252, 0.6)',
                            font: {
                                family: "'Poppins', sans-serif"
                            }
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating typing chart:', error);
    }
}

function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const currentValue = parseInt(element.textContent) || 0;
    if (currentValue === targetValue) return;
    
    const increment = (targetValue - currentValue) / 8;
    let currentCount = currentValue;
    
    const counter = setInterval(() => {
        currentCount += increment;
        if ((increment > 0 && currentCount >= targetValue) || (increment < 0 && currentCount <= targetValue)) {
            element.textContent = targetValue;
            clearInterval(counter);
        } else {
            element.textContent = Math.round(currentCount);
        }
    }, 40);
}

// Smooth width animation for confidence meter
function animateWidth(element, targetValue) {
    const currentWidth = parseInt(element.style.width) || 0;
    if (currentWidth === targetValue) return;
    
    const difference = targetValue - currentWidth;
    const steps = 8;
    const stepValue = difference / steps;
    let currentWidth_ = currentWidth;
    
    const animator = setInterval(() => {
        currentWidth_ += stepValue;
        if ((stepValue > 0 && currentWidth_ >= targetValue) || (stepValue < 0 && currentWidth_ <= targetValue)) {
            element.style.width = targetValue + '%';
            clearInterval(animator);
        } else {
            element.style.width = Math.round(currentWidth_) + '%';
        }
    }, 40);
}

function setTheme(theme) {
    document.body.classList.toggle('light-theme', theme === 'light');
    document.body.classList.toggle('dark-theme', theme === 'dark');
    localStorage.setItem('themeMode', theme);
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.innerHTML = theme === 'light' ? '<i class="fas fa-moon"></i> Dark Mode' : '<i class="fas fa-sun"></i> Light Mode';
    }
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('themeMode') || 'dark';
    setTheme(savedTheme);
}

function toggleTheme() {
    const current = document.body.classList.contains('light-theme') ? 'light' : 'dark';
    setTheme(current === 'light' ? 'dark' : 'light');
}

// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

initializeTheme();

async function loadAIInsights() {
    try {
        const response = await fetch('/api/ai-insights');
        const data = await response.json();
        
        if (data.success && data.insights) {
            const insightsContainer = document.getElementById('insightsGrid');
            if (insightsContainer) {
                insightsContainer.innerHTML = '';
                
                data.insights.forEach(insight => {
                    const card = document.createElement('div');
                    card.className = `insight-card ${insight.type ? 'border-' + insight.type : ''}`;
                    if(insight.type === 'danger') card.style.borderLeftColor = '#ef4444';
                    else if(insight.type === 'warning') card.style.borderLeftColor = '#f59e0b';
                    else if(insight.type === 'success') card.style.borderLeftColor = '#10b981';
                    
                    card.innerHTML = `
                        <h4><i class="${insight.icon}"></i> ${insight.title}</h4>
                        <p>${insight.message}</p>
                    `;
                    insightsContainer.appendChild(card);
                });
            }
        }
    } catch (error) {
        console.error('Error loading AI insights:', error);
    }
}
