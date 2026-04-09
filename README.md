# AI-Based Detection of Cognitive Fatigue Using User Behavior Patterns

A full-stack Flask web application that detects cognitive fatigue through real-time analysis of user behavior patterns including typing speed, mouse movement, and activity levels.

## Features

✨ **Modern UI/UX**
- Beautiful glassmorphism design
- Dark theme with gradient backgrounds
- Smooth animations and transitions
- Fully responsive (mobile, tablet, desktop)
- Professional SaaS-style dashboard

🧠 **Cognitive Fatigue Detection**
- Real-time typing speed analysis
- Mouse movement tracking
- Inactivity detection
- AI-based fatigue level classification (Low/Medium/High)
- Confidence scoring for predictions

📊 **Analytics & Dashboard**
- Real-time statistics cards
- Interactive Chart.js graphs
- Fatigue history visualization
- Activity logs and trends
- Session tracking

🔐 **User Management**
- Secure registration and login
- Session management
- User profile

## Tech Stack

- **Backend:** Flask, Python
- **Database:** MongoDB (pymongo)
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Chart.js
- **Icons:** Font Awesome 6
- **Fonts:** Google Fonts (Poppins)
- **Styling:** Glassmorphism & Modern UI patterns

## Project Structure

```
cognitive-fatigue-detection/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py                 # Landing page routes
│   │   ├── auth.py                 # Login/Register routes
│   │   ├── dashboard.py            # Dashboard routes
│   │   └── tracking.py             # Data tracking & fatigue analysis
│   ├── models/
│   │   ├── __init__.py
│   │   └── db.py                   # MongoDB connection & operations
│   ├── templates/
│   │   ├── landing.html            # Landing page
│   │   ├── login.html              # Login page
│   │   ├── register.html           # Registration page
│   │   ├── dashboard.html          # Main dashboard
│   │   └── activity.html           # Activity logs page
│   └── static/
│       ├── css/
│       │   └── style.css           # Main styles (glassmorphism)
│       └── js/
│           ├── tracking.js         # User behavior tracking
│           └── dashboard.js        # Dashboard functionality
├── config.py                       # Configuration settings
├── run.py                          # Entry point
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB (running locally or cloud instance)
- Git

### Step 1: Clone & Setup Environment

```bash
cd cognitive-fatigue-detection
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure MongoDB

Update `config.py` with your MongoDB connection string:

```python
MONGODB_URI = 'mongodb://localhost:27017/'
# OR for MongoDB Atlas:
MONGODB_URI = 'mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority'
```

### Step 4: Run the Application

```bash
python run.py
```

The application will start at `http://127.0.0.1:5000`

## Usage

### 1. **Landing Page**
   - Visit the home page
   - See project overview with animated background

### 2. **Register Account**
   - Click "Create Account"
   - Fill in full name, email, and password
   - Account will be stored in MongoDB

### 3. **Login**
   - Enter your credentials
   - Secure session management with Flask

### 4. **Dashboard**
   - View real-time typing speed
   - Monitor activity level
   - See fatigue status with confidence score
   - View interactive charts
   - Use the "Start Tracking" button to begin

### 5. **Tracking**
   - Click "Start Tracking" to monitor behavior
   - Keyboard input is tracked
   - Mouse movements are recorded
   - Inactivity periods are measured
   - Data is sent to backend every 30 seconds for analysis

### 6. **Activity Logs**
   - Navigate to Activity page
   - View detailed logs of all tracking sessions
   - See metrics like typing speed, key presses, mouse movements
   - Search and filter activity data

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /api/user-info` - Get current user info

### Dashboard
- `GET /dashboard` - Dashboard page
- `GET /api/dashboard-stats` - Get dashboard statistics
- `GET /api/chart-data` - Get chart data

### Tracking & Analysis
- `POST /api/track-data` - Submit tracking data
- `GET /api/fatigue-result` - Get latest fatigue result
- `GET /api/activity-logs` - Get user activity logs

## Fatigue Detection Algorithm

The system analyzes fatigue based on:

| Metric | Weight | Low | Medium | High |
|--------|--------|-----|--------|------|
| Typing Speed (WPM) | 30% | >50 | 30-50 | <30 |
| Key Presses | 25% | 150-300 | 50-150 | <50 |
| Mouse Movements | 20% | >50 | 20-50 | <20 |
| Inactivity (sec) | 25% | <60 | 60-300 | >300 |

**Confidence Score:** 75-100% based on data completeness

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password": "hashed_password",
  "full_name": "John Doe",
  "created_at": ISODate(),
  "is_active": boolean
}
```

### Activity Logs Collection
```json
{
  "_id": ObjectId,
  "user_id": "user_id",
  "typing_speed": 65,
  "mouse_moves": 150,
  "inactivity_duration": 45,
  "key_presses": 200,
  "timestamp": ISODate()
}
```

### Fatigue Results Collection
```json
{
  "_id": ObjectId,
  "user_id": "user_id",
  "fatigue_level": "Low|Medium|High",
  "confidence": 85,
  "metrics": {...},
  "timestamp": ISODate()
}
```

## UI Features

### Glassmorphism Design
- Semi-transparent cards with backdrop blur
- Gradient backgrounds
- Smooth hover effects
- Modern rounded corners

### Responsive Design
- Mobile-first approach
- Sidebar collapses on mobile
- Touch-friendly buttons
- Optimized for all screen sizes

### Animations
- Smooth page transitions
- Loading spinners
- Hover effects on cards and buttons
- Chart animations
- Pulsing effects for active states

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Performance

- Lazy loading of charts
- Optimized CSS with variables
- Efficient JavaScript event listeners
- Database indexing on frequently queried fields
- CORS enabled for better performance

## Security Features

- Password hashing (SHA-256)
- Session management
- CSRF protection ready
- Secure MongoDB connection
- Input validation on frontend and backend

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Advanced ML-based fatigue detection
- [ ] Email notifications for high fatigue
- [ ] Data export (CSV/PDF)
- [ ] Mobile app version
- [ ] Dark/Light theme toggle
- [ ] Multi-language support
- [ ] Two-factor authentication
- [ ] Fatigue recommendations
- [ ] Team analytics dashboard

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod`
- Check connection string in `config.py`
- For MongoDB Atlas, verify IP whitelist

### Port 5000 Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### Charts Not Displaying
- Ensure Chart.js is loaded from CDN
- Check browser console for errors
- Verify data is returned from API

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or feedback, please open an issue on GitHub or contact the developer.

---

**Made with ❤️ for cognitive wellness**
