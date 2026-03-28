# Flask → Netlify + Render Migration Plan

## Overview
Convert monolithic Flask app to separated frontend (Netlify) + backend (Render) deployment.

---

## PHASE 1: BACKEND MODIFICATIONS (Flask on Render)

### 1.1 Update requirements.txt
Add CORS support (already partially implemented, but make explicit):

```
Flask==3.0.0
Flask-Cors==4.0.0
flask-mysqldb==2.0.0
mysql-connector-python==8.3.0
python-dotenv==1.0.1
requests==2.31.0
Werkzeug==3.0.1
Flask-WTF==1.2.1
gunicorn==21.2.0
```

### 1.2 Backend Routes to Convert to JSON
Priority routes that frontend needs:

| Route | Method | Current | Convert To |
|-------|--------|---------|------------|
| `/login` | POST | form → redirect | JSON response |
| `/logout` | GET | redirect | JSON response |
| `/dashboard` | GET | render template | JSON (user data) |
| `/checkin` | POST | ✅ Already JSON | ✅ No change |
| `/checkout` | POST | ✅ Already JSON | ✅ No change |
| `/mark` | GET | render template | JSON (page data) |
| `/myleave` | GET/POST | render template | JSON (leave data) |
| `/request_leave` | POST | form redirect | JSON response |
| `/view_attendance` | GET | render table | JSON array |
| `/admin` | GET | render template | JSON (admin data) |
| `/admin/employees` | GET | render table | JSON array |
| `/admin/attendance` | GET | render table | JSON array |

### 1.3 Flask App Modifications

Add to top of app.py after imports:
```python
from flask_cors import CORS

# After app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:3000", "https://your-netlify-domain.netlify.app"],
     supports_credentials=True)
```

Keep existing CORS after_request but make backend deployment URL configurable.

### 1.4 Session Management for Frontend
Frontend must send session cookies with each request:
```python
# In backend routes, session still works via cookies
# Frontend must set: credentials: 'include' in fetch()
```

### 1.5 File Upload Handler
Already exists - no changes needed. Frontend will POST multipart/form-data to existing `/checkin` endpoint.

---

## PHASE 2: FRONTEND RESTRUCTURING

### 2.1 New Folder Structure
```
frontend/
├── index.html                 # Login page
├── dashboard.html             # Employee dashboard
├── mark_attendance.html       # Check-in/Check-out
├── leave_management.html      # Leave requests
├── admin/
│   ├── dashboard.html
│   ├── employees.html
│   ├── attendance.html
│   └── leave-management.html
├── css/
│   ├── styles.css            # Main styles
│   ├── bootstrap.min.css
│   └── all.min.css  
├── js/
│   ├── api.js                # API client (centralized fetch calls)
│   ├── auth.js               # Login/logout handlers
│   ├── utils.js              # Shared utilities
│   ├── bootstrap.bundle.min.js
│   └── script.js
├── assets/
│   ├── images/
│   └── fonts/
└── .env.example              # Document API URL
```

### 2.2 Template Conversion Strategy

#### Before (Jinja2):
```html
<link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
```

#### After (Direct URL):
```html
<link rel="stylesheet" href="./css/styles.css">
<!-- OR with API_URL from config -->
<link rel="stylesheet" href="css/styles.css">
```

#### Before (Flask routing):
```html
<form method="POST" action="/login">
  <input name="username" required>
  <input type="password" name="password" required>
  <button type="submit">Login</button>
</form>
```

#### After (Fetch API):
```html
<form id="loginForm" method="POST">
  <input id="username" name="username" required>
  <input id="password" type="password" required>
  <button type="submit">Login</button>
</form>

<script src="js/api.js"></script>
<script>
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const result = await apiCall('/login', 'POST', {
    username: document.getElementById('username').value,
    password: document.getElementById('password').value,
    role: 'employee'
  });
  if (result.status === 'success' || result.authenticated) {
    window.location.href = './dashboard.html';
  }
});
</script>
```

---

## PHASE 3: CRITICAL CODE CHANGES

### 3.1 Backend: Convert /login to JSON

Replace login route with:
```python
@app.route('/login', methods=['POST'])
@csrf.exempt  # Frontend won't have CSRF token
def login():
    """JSON login endpoint for frontend"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        requested_role = data.get('role', 'employee')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND role = %s", 
                      (username, requested_role))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            cursor.close()
            
            session.clear()
            session['user_id'] = str(user['user_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            session['employee_name'] = user.get('name', user['username'])
            session.permanent = True
            
            return jsonify({
                'status': 'success',
                'authenticated': True,
                'role': user['role'],
                'user_id': user['user_id'],
                'username': user['username'],
                'name': user.get('name', user['username']),
                'message': f"Welcome {user['name'] or username}!"
            }), 200
        else:
            cursor.close()
            return jsonify({
                'status': 'error',
                'authenticated': False,
                'message': f'Invalid {requested_role} credentials!'
            }), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Login failed. Please try again.'
        }), 500
```

### 3.2 Backend: Convert /logout to JSON
```python
@app.route('/logout', methods=['POST'])
@csrf.exempt
def logout():
    """JSON logout endpoint"""
    username = session.get('username', 'User')
    session.clear()
    return jsonify({
        'status': 'success',
        'message': f'Goodbye {username}!',
        'authenticated': False
    }), 200
```

### 3.3 Backend: Convert /dashboard to JSON
```python
@app.route('/dashboard')
@employee_required
def dashboard():
    """Return dashboard data as JSON"""
    user_id = session.get('user_id')
    today = date.today()
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attendance WHERE user_id = %s AND date = %s", (user_id, today))
        today_attendance = cursor.fetchone()
        cursor.execute("SELECT geofence_status, compoff_balance FROM users WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        
        return jsonify({
            'status': 'success',
            'username': session['username'],
            'employee_name': session['employee_name'],
            'today_attendance': today_attendance,
            'geofence_status': row['geofence_status'] if row else 'none',
            'compoff_balance': row.get('compoff_balance', 0) if row else 0
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if conn:
            conn.close()
```

### 3.4 Frontend: Centralized API Client (`js/api.js`)
```javascript
// Configuration
const API_BASE_URL = localStorage.getItem('API_URL') || 'http://localhost:5000';

// Helper to make API calls with credentials
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        credentials: 'include', // CRITICAL: Send session cookies
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        return { status: 'error', message: error.message };
    }
}

// File upload with credentials
async function uploadFile(endpoint, formData) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        return await response.json();
    } catch (error) {
        console.error('Upload Error:', error);
        return { status: 'error', message: error.message };
    }
}
```

### 3.5 Frontend: Login Handler (`js/auth.js`)
```javascript
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm') || document.getElementById('employeeForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;
    const role = document.querySelector('input[name="role"]').value || 'employee';
    
    const result = await apiCall('/login', 'POST', { username, password, role });
    
    if (result.status === 'success') {
        localStorage.setItem('user_role', result.role);
        localStorage.setItem('user_id', result.user_id);
        
        // Redirect based on role
        if (result.role === 'admin') {
            window.location.href = './admin/dashboard.html';
        } else {
            window.location.href = './dashboard.html';
        }
    } else {
        showMessage(result.message || 'Login failed', 'error');
    }
}

function handleLogout() {
    apiCall('/logout', 'POST').then(() => {
        localStorage.clear();
        window.location.href = './index.html';
    });
}

function showMessage(message, type = 'info') {
    // Show toast/alert
    alert(message);
}
```

### 3.6 Frontend: Attendance Check-in (`mark_attendance.html`)
```html
<form id="checkinForm">
    <button type="submit">Check In</button>
</form>

<script src="../js/api.js"></script>
<script>
document.getElementById('checkinForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    try {
        const position = await getLocation();
        const photo = await capturePhoto();
        
        const formData = new FormData();
        formData.append('latitude', position.coords.latitude);
        formData.append('longitude', position.coords.longitude);
        if (photo) formData.append('image', photo);
        
        const result = await uploadFile('/checkin', formData);
        
        if (result.status === 'success') {
            alert('Check-in successful!');
        } else {
            alert('Check-in failed: ' + result.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

function getLocation() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
}

async function capturePhoto() {
    // Use existing photo capture logic
    return null;
}
</script>
```

---

## PHASE 4: DEPLOYMENT CONFIGURATION

### 4.1 Backend: Render Deployment

Create `render.yaml` or use Web Service settings:
```yaml
services:
  - type: web
    name: cgs-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    envVars:
      - key: MYSQL_HOST
        value: external-db.example.com
      - key: MYSQL_USER
        value: cgs_user
      - key: MYSQL_PASSWORD
        fromSecret: DB_PASSWORD
      - key: MYSQL_DB
        value: cgs
      - key: FLASK_SECRET_KEY
        fromSecret: FLASK_SECRET
```

### 4.2 Frontend: Netlify Deployment

Create `netlify.toml`:
```toml
[build]
  command = "echo 'Static site - no build needed'"
  publish = "."

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[context.production]
  environment = { API_URL = "https://cgs-backend.onrender.com" }
```

Create `_redirects` file in root:
```
/* /index.html 200
```

Create `js/config.js` (loaded in each HTML):
```javascript
// Automatically set API URL based on environment
if (window.location.hostname === 'localhost') {
    localStorage.setItem('API_URL', 'http://localhost:5000');
} else if (window.location.hostname.includes('netlify.app')) {
    localStorage.setItem('API_URL', 'https://cgs-backend.onrender.com');
}
```

### 4.3 Backend: .env file for local development
```
FLASK_SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-db-password
MYSQL_DB=cgs
GOOGLE_MAPS_API_KEY=your-key-here
```

### 4.4 .env for Render deployment
Set via Render dashboard environment variables (not committed to git)

---

## PHASE 5: MIGRATION CHECKLIST

### Backend Changes
- [ ] Add `flask-cors` and `gunicorn` to requirements.txt
- [ ] Update `/login` to return JSON
- [ ] Update `/logout` to return JSON
- [ ] Update `/dashboard` to return JSON
- [ ] Update `/mark` to return JSON
- [ ] Add API endpoints for `/get-attendance-data`, `/get-leave-data`, etc.
- [ ] Test all routes with curl or Postman
- [ ] Update app.run() to use gunicorn for production
- [ ] Create `.env.example` 
- [ ] Verify CORS headers are sent correctly

### Frontend Changes
- [ ] Copy templates to `frontend/` folder structure
- [ ] Remove all `{{ url_for() }}` and replace with relative paths
- [ ] Remove all `{% csrf_token() %}`
- [ ] Create `js/api.js` with centralized fetch calls
- [ ] Create `js/auth.js` with login/logout handlers
- [ ] Convert all form submits to fetch() calls
- [ ] Update all form actions from `/login` to JavaScript handlers
- [ ] Add localStorage for storing API URL and user info
- [ ] Test all pages load correctly with relative paths
- [ ] Verify authentication flow works with session cookies

### Deployment Setup
- [ ] Create Render Web Service (connect GitHub repo)
- [ ] Set Render environment variables
- [ ] Add MySQL connection details to Render
- [ ] Create Netlify site and connect to frontend folder
- [ ] Set Netlify build settings (publish = .)
- [ ] Create Netlify redirects file
- [ ] Update CORS allowed origins in Flask
- [ ] Test end-to-end: login → check-in → check-out → view data

---

## PHASE 6: TESTING MATRIX

| Feature | Backend | Frontend | Live |
|---------|---------|----------|------|
| Login (Employee) | ✓ | ✓ | ✓ |
| Login (Admin) | ✓ | ✓ | ✓ |
| Check-in | ✓ | ✓ | ✓ |
| Check-out | ✓ | ✓ | ✓ |
| Dashboard Load | ✓ | ✓ | ✓ |
| Leave Request | ✓ | ✓ | ✓ |
| Photo Upload | ✓ | ✓ | ✓ |
| Location Validation | ✓ | ✓ | ✓ |
| Session Persistence | ✓ | ✓ | ✓ |
| Logout | ✓ | ✓ | ✓ |

---

## KEY CONSIDERATIONS

1. **Session Cookies**: Frontend MUST use `credentials: 'include'` in fetch()
2. **CORS Origins**: Update Flask CORS to include Netlify domain
3. **Photo Upload**: Still multipart/form-data POST to backend
4. **Environment Variables**: Use `.env` locally, Render dashboard for production
5. **Database**: No changes needed - same connection string
6. **File Storage**: Already exists in `static/attendance_photos/` - configure for Render
7. **Performance**: For 10-20 employees, no optimization needed; keep as-is
8. **Demo Focus**: Only test core flows; ignore advanced features like geofencing

---

## Post-Migration Support

- Monitor backend logs on Render for errors
- Check CORS issues in browser DevTools Console
- Verify session cookies are being sent (Look for `__session` cookies)
- Use Netlify analytics to monitor frontend loads
- Set up error tracking (optional: Sentry)

