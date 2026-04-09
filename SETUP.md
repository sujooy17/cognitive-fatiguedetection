# Setup Instructions for Running the Project

## Quick Start Guide

### 1. Initial Setup

```bash
# Navigate to project directory
cd c:\PFSD PROJECT\cognitive-fatigue-detection

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Download from: https://www.mongodb.com/try/download/community
# Install and start MongoDB service
# MongoDB will run at mongodb://localhost:27017/
```

**Option B: MongoDB Atlas (Cloud)**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free account
3. Create a cluster
4. Get connection string: `mongodb+srv://user:pass@cluster.mongo.net/?retryWrites=true&w=majority`

### 3. Configure Connection

Edit `config.py` and update the MONGODB_URI:

```python
MONGODB_URI = 'mongodb://localhost:27017/'  # For local
# OR
MONGODB_URI = 'mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority'  # For Atlas
```

### 4. Run the Application

```bash
# Make sure virtual environment is activated
# Windows
venv\Scripts\activate

# Run the app
python run.py
```

The app will be available at: **http://127.0.0.1:5000**

### 5. First Time Usage

1. **Landing Page** - Visit http://127.0.0.1:5000
2. **Register** - Create a new account at /register
3. **Login** - Log in with your credentials at /login
4. **Dashboard** - Access the main dashboard
5. **Start Tracking** - Click "Start Tracking" button
6. **Type & Move Mouse** - The system will track your behavior
7. **View Results** - See fatigue analysis after 30 seconds
8. **Check Activity** - View logs at /activity

## Features Overview

### Landing Page ✨
- Animated hero section
- Feature showcase
- Call-to-action buttons
- Beautiful gradient backgrounds

### Authentication 🔐
- User registration with validation
- Secure login
- Session management
- Password hashing

### Dashboard 📊
- Real-time statistics
- Fatigue level indicator (Low/Medium/High)
- Typing speed metrics
- Activity level monitoring
- Interactive charts using Chart.js
- Confidence score visualization

### Behavior Tracking 🎯
- Keyboard activity monitoring
- Mouse movement tracking
- Inactivity detection
- Real-time data submission
- AI-based fatigue analysis

### Activity Logs 📝
- Complete tracking history
- Detailed metrics per session
- Searchable database
- Pagination support

## API Endpoints Reference

### Public Routes
- `GET /` - Landing page
- `GET /register` - Registration page
- `POST /register` - Register new user
- `GET /login` - Login page
- `POST /login` - Authenticate user

### Protected Routes (Requires Login)
- `GET /dashboard` - Main dashboard
- `GET /activity` - Activity logs page
- `GET /logout` - Logout user

### API Endpoints
- `GET /api/user-info` - Get current user details
- `GET /api/dashboard-stats` - Get dashboard statistics
- `GET /api/chart-data` - Get chart data
- `POST /api/track-data` - Submit tracking data
- `GET /api/fatigue-result` - Get latest fatigue analysis
- `GET /api/activity-logs` - Get activity history

## Fatigue Detection Algorithm

The system analyzes four key metrics:

1. **Typing Speed** (Weight: 30%)
   - Measured in Words Per Minute (WPM)
   - Low typing = Higher fatigue

2. **Key Presses** (Weight: 25%)
   - Count of keyboard inputs
   - Low activity = Higher fatigue

3. **Mouse Movements** (Weight: 20%)
   - Frequency of mouse position changes
   - Low movement = Higher fatigue

4. **Inactivity Duration** (Weight: 25%)
   - Seconds without any activity
   - Long inactivity = Higher fatigue

**Result:** Fatigue Level (Low/Medium/High) with Confidence % (75-100%)

## Customization

### Change Tracking Duration
In `app/static/js/tracking.js`, modify:
```javascript
this.trackingDuration = 30000; // milliseconds (currently 30 seconds)
```

### Adjust Fatigue Thresholds
In `app/routes/tracking.py`, modify the `analyze_fatigue()` function:
```python
if typing_speed < 30:  # Current threshold
    fatigue_score += 30
```

### Update Designer/Colors
Global colors are in `app/static/css/style.css`:
```css
:root {
    --primary-color: #f5576c;  /* Pink/Red */
    --secondary-color: #667eea;  /* Blue */
    /* ... more colors ... */
}
```

## Troubleshooting

### Issue: MongoDB Connection Fails
**Solution:**
- Ensure MongoDB is running (mongod.exe on Windows)
- Check connection string in config.py
- For MongoDB Atlas, check firewall/whitelist settings

### Issue: Port 5000 Already in Use
**Solution (Windows PowerShell):**
```powershell
# Find process using port 5000
Get-NetTCPConnection -LocalPort 5000

# Kill the process
taskkill /PID <PID> /F

# Or change port in run.py
```

### Issue: Virtual Environment Not Activating
**Solution:**
```bash
# Try this command
python -m venv venv --clear
venv\Scripts\activate
```

### Issue: Modules Not Found After Installing
**Solution:**
```bash
# Reinstall in correct environment
pip install --upgrade pip
pip install -r requirements.txt
```

## Project Dependencies

- **Flask** - Web framework
- **Flask-CORS** - Cross-origin requests
- **pymongo** - MongoDB driver
- **python-dotenv** - Environment variables
- **Werkzeug** - WSGI utilities

## Database Collections

The app automatically creates these collections on first run:

1. **users** - Stores user accounts
2. **activity_logs** - Stores behavior tracking data
3. **fatigue_results** - Stores fatigue analysis results

## File Structure Explanation

```
app/
├── __init__.py          # App factory function
├── routes/
│   ├── main.py          # /landing, /health
│   ├── auth.py          # /register, /login, /logout
│   ├── dashboard.py     # /dashboard, /activity
│   └── tracking.py      # /api/track-data, /api/fatigue-result
├── models/
│   └── db.py            # MongoDB connection & operations
├── templates/           # HTML pages (Jinja2 templates)
└── static/
    ├── css/             # Stylesheets
    └── js/              # Client-side JavaScript
```

## Development Tips

### Enable Debug Mode
In `config.py`:
```python
DEBUG = True
```

### Access MongoDB Directly
```python
from app.models.db import get_db
db = get_db()
users = list(db.db.users.find())
```

### View Database Contents
Install MongoDB Compass (GUI):
https://www.mongodb.com/products/compass

### Check Logs
Monitor Flask server output in terminal for debugging

## Performance Notes

- Charts update every 10 seconds
- Tracking data sent every 30 seconds
- Database queries indexed for speed
- CSS uses variables for fast theming
- Responsive images and lazy loading recommended

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure MongoDB
3. ✅ Run the application
4. ✅ Create account and explore
5. Consider deploying to:
   - Heroku (free tier with MongoDB Atlas)
   - PythonAnywhere
   - AWS/Google Cloud
   - DigitalOcean

## Support & Documentation

For more information:
- **Read README.md** for detailed feature documentation
- **Check app routes** for API specifications
- **Review database schema** in the README
- **Inspect browser console** for client-side errors
- **Check Flask server output** for backend errors

---

**Enjoy monitoring cognitive fatigue! 🧠**
