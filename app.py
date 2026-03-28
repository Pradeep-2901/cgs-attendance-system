from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb
import mysql.connector as mysql_connector
import os
from datetime import datetime, date, timedelta
import base64
import requests
import json
import math
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key_if_not_set')

# ✅ Enable CORS for frontend separation (Netlify + Render)
CORS(app, 
     resources={r"/*": {"origins": "*"}},  # Allow all endpoints
     supports_credentials=True,  # CRITICAL: Allow cookies
     allow_headers=['Content-Type', 'X-CSRFToken', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)

# ✅ Security Configuration
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True  # ✅ Enable for production HTTPS

# ✅ Add CORS headers for AJAX requests
@app.after_request
def after_request(response):
    # Cache control for all responses
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # CORS headers - Permissive for debugging
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, X-Requested-With'
    
    return response

# ✅ Enable CSRF Protection
csrf = CSRFProtect(app)

# ✅ Flask-MySQLdb Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', '3306'))  # ✅ ADD PORT CONFIG
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'cgs')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ✅ Custom Jinja2 filter to handle timedelta objects
@app.template_filter('time_format')
def time_format(time_obj, format='%H:%M:%S'):
    """Format time objects (handles both datetime and timedelta)"""
    if time_obj is None:
        return 'N/A'
    
    if isinstance(time_obj, timedelta):
        # Convert timedelta to total seconds then to hours:minutes:seconds
        total_seconds = int(time_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if format == '%H:%M':
            return f"{hours:02d}:{minutes:02d}"
        else:  # Default %H:%M:%S
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    elif hasattr(time_obj, 'strftime'):
        # Regular datetime object
        return time_obj.strftime(format)
    
    else:
        # Convert to string as fallback
        return str(time_obj)

@app.template_filter('date_format')
def date_format(date_obj, format='%Y-%m-%d'):
    """Format date objects"""
    if date_obj is None:
        return 'N/A'
    
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime(format)
    else:
        return str(date_obj)

# ✅ Correct folder to save photos
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'attendance_photos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Database connection
def get_db_connection():
    return mysql_connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', '3306')),  # Convert to int!
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'cgs')
    )

# ✅ Admin login required decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ✅ Employee login required decorator
def employee_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow OPTIONS requests to pass through for CORS preflight
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        user_id = session.get('user_id')
        role = session.get('role')
        print(f"[DECORATOR] Checking employee_required for {request.path}")
        print(f"[DECORATOR] Session user_id: {user_id}, role: {role}")
        print(f"[DECORATOR] Request method: {request.method}")
        print(f"[DECORATOR] Is AJAX: {request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
        
        if role != 'employee':
            print(f"[DECORATOR] ❌ BLOCKING: Role is '{role}', not 'employee'")
            # Check if this is an AJAX/JSON request
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith(('/checkin', '/checkout')):
                return jsonify({'status': 'error', 'message': 'Access denied. Employee login required.', 'session_role': role, 'session_user_id': user_id}), 403
            flash('Access denied. Employee login required.', 'error')
            return redirect(url_for('home'))
        
        print(f"[DECORATOR] ✅ ALLOWED: Proceeding to {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function

# ✅ General login required decorator (for any logged-in user)
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ✅ High-Accuracy Reverse Geocoding Function (Google Maps + OSM Fallback)
def get_address_from_coords(lat, lon):
    """
    Reverse geocode coordinates to a precise street address.
    
    Primary: Google Maps Geocoding API (high accuracy)
    Fallback: OpenStreetMap Nominatim (if Google key not set or fails)
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
    
    Returns:
        str: Formatted street address or coordinates if geocoding fails
    
    Configuration:
        Replace 'YOUR_GOOGLE_MAPS_API_KEY_HERE' with your actual Google Maps API key,
        or set environment variable: GOOGLE_MAPS_API_KEY
    """
    # IMPORTANT: Replace this with your actual Google Maps API key
    # You can also use: os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY_HERE')
    API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Fallback function using OpenStreetMap Nominatim
    def fallback_to_osm():
        """Fallback to OpenStreetMap if Google Maps fails or is not configured"""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            response = requests.get(url, timeout=5, headers={'User-Agent': 'AttendanceApp/1.0'})
            if response.status_code == 200:
                data = response.json()
                return data.get('display_name', f"Lat: {lat}, Lon: {lon}")
            else:
                print(f"[Geocoding][OSM] HTTP Error {response.status_code}")
        except requests.exceptions.Timeout:
            print("[Geocoding][OSM] Request timeout")
        except requests.exceptions.RequestException as e:
            print(f"[Geocoding][OSM] Network error: {e}")
        except Exception as e:
            print(f"[Geocoding][OSM] Unexpected error: {e}")
        return f"Lat: {lat}, Lon: {lon}"
    
    # Check if Google API key is configured
    if not API_KEY or API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        print("[Geocoding] WARNING: Google Maps API key not configured. Falling back to OpenStreetMap.")
        print("[Geocoding] For better accuracy, set your Google Maps API key in the get_address_from_coords function.")
        return fallback_to_osm()
    
    # Try Google Maps Geocoding API first (for high accuracy)
    try:
        google_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'latlng': f"{lat},{lon}",
            'key': API_KEY,
            'result_type': 'street_address|premise|subpremise|route|neighborhood',
            'language': 'en'
        }
        
        print(f"[Geocoding] Using Google Maps API for coordinates: {lat}, {lon}")
        
        response = requests.get(google_url, params=params, timeout=8)
        
        # Check HTTP status code
        if response.status_code != 200:
            print(f"[Geocoding][Google] HTTP Error {response.status_code}. Falling back to OSM.")
            return fallback_to_osm()
        
        data = response.json()
        api_status = data.get('status', 'UNKNOWN')
        
        # Handle different Google API response statuses
        if api_status == 'OK':
            results = data.get('results', [])
            if results and len(results) > 0:
                formatted_address = results[0].get('formatted_address', '')
                if formatted_address:
                    print(f"[Geocoding][Google] Success: {formatted_address}")
                    return formatted_address
                else:
                    print("[Geocoding][Google] No formatted_address in response")
            else:
                print("[Geocoding][Google] Empty results array")
        
        elif api_status == 'ZERO_RESULTS':
            print(f"[Geocoding][Google] No results found for coordinates. Falling back to OSM.")
        
        elif api_status == 'REQUEST_DENIED':
            error_msg = data.get('error_message', 'N/A')
            print(f"[Geocoding][Google] API request denied. Check your API key and billing.")
            print(f"[Geocoding][Google] Error message: {error_msg}")
        
        elif api_status == 'INVALID_REQUEST':
            print(f"[Geocoding][Google] Invalid request parameters")
        
        elif api_status == 'OVER_QUERY_LIMIT':
            print(f"[Geocoding][Google] API quota exceeded. Consider upgrading your plan.")
        
        else:
            print(f"[Geocoding][Google] Unexpected status: {api_status}")
        
        # If we reach here, Google API didn't provide a result - use fallback
        print("[Geocoding] Falling back to OpenStreetMap")
        return fallback_to_osm()
    
    except requests.exceptions.Timeout:
        print("[Geocoding][Google] Request timeout. Falling back to OSM.")
        return fallback_to_osm()
    
    except requests.exceptions.RequestException as e:
        print(f"[Geocoding][Google] Network error: {e}. Falling back to OSM.")
        return fallback_to_osm()
    
    except Exception as e:
        print(f"[Geocoding][Google] Unexpected error: {e}. Falling back to OSM.")
        return fallback_to_osm()

# ====================== UNIFIED GEOFENCING SYSTEM ======================
# Complete location validation system with hierarchical priority

def haversine(lat1, lon1, lat2, lon2):
    """Return distance in meters between two lat/lon pairs."""
    if None in (lat1, lon1, lat2, lon2):
        return None
    try:
        R = 6371000  # Earth radius meters
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        dphi = math.radians(float(lat2) - float(lat1))
        dlambda = math.radians(float(lon2) - float(lon1))
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    except Exception:
        return None

# ====================== GOOGLE GEOCODING API ======================

def geocode_address(address):
    """
    Convert address to coordinates using Google Maps Geocoding API
    
    Returns: dict with 'lat', 'lon', 'formatted_address' or None if failed
    """
    # IMPORTANT: Replace with your actual Google Maps API key
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        print("⚠️ WARNING: Google Maps API key not configured!")
        return None
    
    try:
        import requests
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']
                return {
                    'lat': float(location['lat']),
                    'lon': float(location['lng']),
                    'formatted_address': result['formatted_address']
                }
        
        print(f"Geocoding failed: {data.get('status', 'Unknown error')}")
        return None
        
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

# ====================== UNIFIED VALIDATION SYSTEM ======================

def get_company_setting(cursor, setting_name):
    """Get a company setting value"""
    try:
        cursor.execute("SELECT setting_value FROM company_settings WHERE setting_name = %s", (setting_name,))
        result = cursor.fetchone()
        return result['setting_value'] if result else None
    except Exception:
        return None

def validate_location_unified(cursor, user_id, current_lat, current_lon, check_date=None):
    """
    The Grand Unifying Location Validation Logic
    
    Priority 1: Check for approved On-Site Visit for today
    Priority 2: Check employee's Default work_mode (Office/Remote)
    
    Returns: dict with 'valid', 'message', 'location_type', 'details'
    """
    if check_date is None:
        check_date = date.today()
    
    # ====================== PRIORITY 1: ON-SITE VISITS ======================
    cursor.execute("""
        SELECT sv.*, s.site_name, s.site_address, s.site_lat, s.site_lon, s.site_radius
        FROM site_visits sv
        JOIN sites s ON sv.site_id = s.id
        WHERE sv.user_id = %s 
        AND sv.visit_date = %s 
        AND sv.status = 'Approved'
        AND s.is_active = TRUE
        LIMIT 1
    """, (user_id, check_date))
    
    site_visit = cursor.fetchone()
    if site_visit:
        # Validate against approved site coordinates
        distance = haversine(current_lat, current_lon, site_visit['site_lat'], site_visit['site_lon'])
        radius = site_visit['site_radius'] or 200
        
        if distance is None:
            return {
                'valid': False,
                'message': 'Unable to verify location coordinates',
                'location_type': 'site_visit',
                'details': f"Site: {site_visit['site_name']}"
            }
        
        if distance <= radius:
            return {
                'valid': True,
                'message': f'✅ Location verified at {site_visit["site_name"]} ({int(distance)}m away)',
                'location_type': 'site_visit',
                'details': {
                    'site_name': site_visit['site_name'],
                    'site_address': site_visit['site_address'],
                    'distance': int(distance),
                    'radius': radius
                }
            }
        else:
            return {
                'valid': False,
                'message': f'❌ You must be within {radius}m of {site_visit["site_name"]}. Current distance: {int(distance)}m',
                'location_type': 'site_visit',
                'details': {
                    'site_name': site_visit['site_name'],
                    'required_distance': radius,
                    'actual_distance': int(distance)
                }
            }
    
    # ====================== PRIORITY 1.5: APPROVED REMOTE REQUESTS ======================
    cursor.execute("""
        SELECT * FROM remote_work_requests
        WHERE user_id = %s 
        AND start_date <= %s 
        AND end_date >= %s
        AND status = 'Approved'
        LIMIT 1
    """, (user_id, check_date, check_date))
    
    remote_request = cursor.fetchone()
    if remote_request:
        # Requirement: "If role = 'remote' or 'on-site': check whether they have got approval from admin or not then allow attendance."
        # Since we found an approved request for today, we allow attendance.
        # We also validate the location if coordinates are available, to ensure they are at the requested place.
        
        distance = haversine(current_lat, current_lon, remote_request['lat'], remote_request['lon'])
        radius = 200  # 200m radius
        
        if distance is None:
             # Fallback if calculation fails, but approval exists
            return {
                'valid': True,
                'message': '✅ Remote work approved for today.',
                'location_type': 'remote_request',
                'details': remote_request['address']
            }
        
        if distance <= radius:
            return {
                'valid': True,
                'message': f'✅ Location verified at approved remote location ({int(distance)}m away)',
                'location_type': 'remote_request',
                'details': {
                    'address': remote_request['address'],
                    'distance': int(distance),
                    'radius': radius
                }
            }
        else:
            # Even if distance is far, the prompt says "check whether they have got approval... then allow".
            # However, usually remote requests are for a specific place. 
            # But to strictly follow "excluded from geo-fencing checks" interpretation for approved remote:
            # We will allow it but warn, OR strictly enforce the location of the request.
            # Given the previous feature I built enforces location, I will keep it strict but maybe increase radius or just allow.
            # Let's stick to the strict location check as it's safer for an attendance system, 
            # unless "excluded from geo-fencing" means ANYWHERE.
            # The prompt says: "Remote employees and on-site field workers are excluded from geo-fencing checks."
            # This implies NO location check against Office, but maybe check against their approved location?
            # Or maybe no check at all?
            # "If role = 'remote' ... check whether they have got approval ... then allow attendance."
            # This implies approval is the ONLY condition.
            
            # Let's relax the check to just approval, but log the distance.
            return {
                'valid': True,
                'message': f'✅ Remote work approved. (Distance from requested loc: {int(distance)}m)',
                'location_type': 'remote_request',
                'details': {
                    'address': remote_request['address'],
                    'distance': int(distance)
                }
            }

    # ====================== PRIORITY 2: DEFAULT WORK MODE ======================
    cursor.execute("SELECT work_mode, remote_address, remote_lat, remote_lon FROM users WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        return {
            'valid': False,
            'message': 'Employee not found',
            'location_type': 'error',
            'details': None
        }
    
    work_mode = user_data['work_mode']
    
    if work_mode == 'Remote':
        # Requirement: "If role = 'remote' ... check whether they have got approval ... then allow attendance."
        # This block handles users with DEFAULT work_mode = 'Remote'.
        # If they have a default remote mode, they might not need daily requests, OR they need a one-time approval.
        # Assuming 'Remote' role means they are permanently remote.
        # "Remote employees ... are excluded from geo-fencing checks."
        
        return {
            'valid': True,
            'message': '✅ Remote employee attendance allowed.',
            'location_type': 'remote',
            'details': 'Permanent Remote Role'
        }
        
        # Old logic commented out to strictly follow "excluded from geo-fencing checks"
        # if not user_data['remote_lat'] or not user_data['remote_lon']: ...
        
    elif work_mode == 'Office':
        # Requirement: "Only normal (office-based) employees must mark attendance from the office location."
        # Validate against main office location
        office_lat = get_company_setting(cursor, 'office_lat')
        office_lon = get_company_setting(cursor, 'office_lon')
        office_address = get_company_setting(cursor, 'office_address')
        office_radius = int(get_company_setting(cursor, 'office_radius') or 200)
        
        if not office_lat or not office_lon:
            return {
                'valid': False,
                'message': '❌ Main office location not configured. Contact admin.',
                'location_type': 'office',
                'details': 'Configuration missing'
            }
        
        distance = haversine(current_lat, current_lon, float(office_lat), float(office_lon))
        
        if distance is None:
            return {
                'valid': False,
                'message': 'Unable to verify office location coordinates',
                'location_type': 'office',
                'details': office_address
            }
        
        if distance <= office_radius:
            return {
                'valid': True,
                'message': f'✅ Location verified at main office ({int(distance)}m away)',
                'location_type': 'office',
                'details': {
                    'address': office_address,
                    'distance': int(distance),
                    'radius': office_radius
                }
            }
        else:
            return {
                'valid': False,
                'message': f'❌ You must be at the main office. Current distance: {int(distance)}m (limit: {office_radius}m)',
                'location_type': 'office',
                'details': {
                    'address': office_address,
                    'required_distance': office_radius,
                    'actual_distance': int(distance)
                }
            }
    
    else:
        return {
            'valid': False,
            'message': f'❌ Unknown work mode: {work_mode}. Contact admin.',
            'location_type': 'error',
            'details': f'Invalid work mode: {work_mode}'
        }

# ====================== DEBUG ENDPOINTS ======================

@app.route('/test_session')
def test_session():
    """Debug endpoint to check session state"""
    session_data = {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'employee_name': session.get('employee_name'),
        'session_keys': list(session.keys())
    }
    return jsonify({
        'status': 'success',
        'session': session_data,
        'is_employee': session.get('role') == 'employee',
        'is_authenticated': 'user_id' in session
    })

@app.route('/health')
def health_check():
    """Health check endpoint for database and session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'ok',
        'database': db_status,
        'session_active': 'user_id' in session,
        'timestamp': datetime.now().isoformat()
    })

# ====================== BASIC ROUTES ======================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
@csrf.exempt  # Allow direct JSON submissions from frontend
def login():
    """
    Unified login handler supporting both:
    1. Traditional form submissions (existing templates)
    2. JSON requests (new frontend)
    """
    try:
        # Support both JSON and form data
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            requested_role = data.get('role', 'employee')
            is_api_request = True
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            requested_role = request.form.get('role', 'employee')
            is_api_request = False

        # Use proper database connection with port handling
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # Check credentials AND role match
        cursor.execute("SELECT * FROM users WHERE username = %s AND role = %s", 
                      (username, requested_role))
        user = cursor.fetchone()
        
        # Verify password (STRICT: Only hashed passwords allowed)
        if user and check_password_hash(user['password'], password):
            cursor.close()
            db.close()
            
            # Set session with explicit values
            session.clear()
            session['user_id'] = str(user['user_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            session['employee_name'] = user.get('name', user['username'])
            session.permanent = True
            
            print(f"\n[LOGIN] ✅ User logged in: {user['username']} (Role: {user['role']}, ID: {user['user_id']})")
            
            # Return JSON for API requests, redirect for form submissions
            if is_api_request:
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
                if user['role'] == 'admin':
                    flash(f'Welcome Admin {user["name"] or username}!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash(f'Welcome {user["name"] or username}!', 'success')
                    return redirect(url_for('dashboard'))
        else:
            cursor.close()
            db.close()
            if is_api_request:
                return jsonify({
                    'status': 'error',
                    'authenticated': False,
                    'message': f'Invalid {requested_role} credentials!'
                }), 401
            else:
                flash(f'Invalid {requested_role} credentials!', 'error')
                return render_template('index.html')
            
    except Exception as e:
        print(f"Login error: {e}")
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Login failed. Please try again.'
            }), 500
        else:
            flash('Login failed. Please try again.', 'error')
            return render_template('index.html')

@app.route('/logout', methods=['GET', 'POST'])
@csrf.exempt
def logout():
    """Unified logout handler for both forms and API"""
    username = session.get('username', 'User')
    session.clear()
    
    if request.is_json or request.method == 'POST' and request.headers.get('Accept') == 'application/json':
        return jsonify({
            'status': 'success',
            'message': f'Goodbye {username}!',
            'authenticated': False
        }), 200
    else:
        flash(f'Goodbye {username}!', 'success')
        return redirect(url_for('home'))

# ====================== ADMIN ROUTES ======================

@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'employee'")
        total_employees = cursor.fetchone()['total']
        today = date.today()
        cursor.execute("SELECT COUNT(*) as today_attendance FROM attendance WHERE date = %s", (today,))
        today_attendance = cursor.fetchone()['today_attendance']

        # Pending comp-off
        cursor.execute("SELECT COUNT(*) AS pending_compoff FROM compoff_requests WHERE status='Pending'")
        pending_compoff = cursor.fetchone()['pending_compoff']
        cursor.execute("""
            SELECT a.*, u.name as employee_name 
            FROM attendance a 
            JOIN users u ON a.user_id = u.user_id 
            WHERE u.role = 'employee'
            ORDER BY a.date DESC, a.check_in_time DESC 
            LIMIT 5
        """)
        recent_attendance = cursor.fetchall()
        conn.close()
        return render_template('admin_dashboard.html',
                             username=session['username'],
                             total_employees=total_employees,
                             today_attendance=today_attendance,
                             recent_attendance=recent_attendance,
                             pending_compoff=pending_compoff)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        flash(f'Dashboard error: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/admin/employees')
@admin_required
def manage_employees():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role = 'employee' ORDER BY name")
        employees = cursor.fetchall()
        conn.close()
        
        return render_template('manage_employees.html',
                             username=session['username'],
                             employees=employees)
    except Exception as e:
        print(f"Manage employees error: {e}")
        flash(f'Error loading employees: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_employee', methods=['GET', 'POST'])
@admin_required
def add_employee():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            username = request.form['username'].strip()
            password = request.form['password']
            
            if not name or not username or not password:
                flash('Name, username, and password are required!', 'error')
                return render_template('add_employee.html', username=session['username'])
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists! Please choose a different username.', 'error')
                conn.close()
                return render_template('add_employee.html', username=session['username'])
            
            # Generate next user_id
            cursor.execute("SELECT MAX(CAST(user_id AS UNSIGNED)) FROM users WHERE user_id REGEXP '^[0-9]+$'")
            result = cursor.fetchone()
            next_id = str((result[0] or 0) + 1)
            
            # Get geofencing fields
            work_mode = request.form.get('work_mode', 'Office')
            remote_address = request.form.get('remote_address', '').strip()
            
            # Geocode remote address if provided
            remote_lat = remote_lon = None
            if work_mode == 'Remote' and remote_address:
                geocode_result = geocode_address(remote_address)
                if geocode_result:
                    remote_lat = geocode_result['lat']
                    remote_lon = geocode_result['lon']
                else:
                    flash('⚠️ Unable to geocode remote address. Employee added, but remote location needs manual configuration.', 'warning')
            
            # Insert new employee with geofencing support
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (user_id, name, username, password, role, work_mode, 
                                 remote_address, remote_lat, remote_lon) 
                VALUES (%s, %s, %s, %s, 'employee', %s, %s, %s, %s)
            """, (next_id, name, username, hashed_password, work_mode, remote_address, remote_lat, remote_lon))
            
            conn.commit()
            conn.close()
            
            flash(f'Employee {name} added successfully with ID: {next_id}!', 'success')
            return redirect(url_for('manage_employees'))
            
        except Exception as e:
            print(f"Add employee error: {e}")
            flash(f'Error adding employee: {str(e)}', 'error')
    
    return render_template('add_employee.html', username=session['username'])

@app.route('/admin/delete_employee/<user_id>')
@admin_required
def delete_employee(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get employee name before deletion - user_id is string
        cursor.execute("SELECT name FROM users WHERE user_id = %s AND role = 'employee'", (user_id,))
        employee = cursor.fetchone()
        
        if not employee:
            flash('Employee not found!', 'error')
            return redirect(url_for('manage_employees'))
        
        # Delete employee's attendance records first (foreign key constraint)
        cursor.execute("DELETE FROM attendance WHERE user_id = %s", (user_id,))
        
        # Delete employee
        cursor.execute("DELETE FROM users WHERE user_id = %s AND role = 'employee'", (user_id,))
        
        conn.commit()
        conn.close()
        
        flash(f'Employee {employee["name"]} deleted successfully!', 'success')
        
    except Exception as e:
        print(f"Delete employee error: {e}")
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('manage_employees'))

@app.route('/admin/edit_employee/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_employee(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            name = request.form['name'].strip()
            username = request.form['username'].strip()
            password = request.form['password'].strip()
            
            if not name or not username:
                flash('Name and username are required!', 'error')
                return redirect(url_for('edit_employee', user_id=user_id))
            
            # Check if username exists for other users
            cursor.execute("SELECT user_id FROM users WHERE username = %s AND user_id != %s", (username, user_id))
            if cursor.fetchone():
                flash('Username already exists! Please choose a different username.', 'error')
                return redirect(url_for('edit_employee', user_id=user_id))
            
            # Get geofencing fields
            work_mode = request.form.get('work_mode', 'Office')
            remote_address = request.form.get('remote_address', '').strip()
            
            # Geocode remote address if provided
            remote_lat = remote_lon = None
            if work_mode == 'Remote' and remote_address:
                geocode_result = geocode_address(remote_address)
                if geocode_result:
                    remote_lat = geocode_result['lat']
                    remote_lon = geocode_result['lon']
                else:
                    flash('⚠️ Unable to geocode remote address. Employee updated, but remote location needs manual configuration.', 'warning')
            
            # Update employee with geofencing support
            if password:
                hashed_password = generate_password_hash(password)
                cursor.execute("""
                    UPDATE users 
                    SET name = %s, username = %s, password = %s, work_mode = %s,
                        remote_address = %s, remote_lat = %s, remote_lon = %s
                    WHERE user_id = %s AND role = 'employee'
                """, (name, username, hashed_password, work_mode, remote_address, remote_lat, remote_lon, user_id))
            else:
                cursor.execute("""
                    UPDATE users 
                    SET name = %s, username = %s, work_mode = %s,
                        remote_address = %s, remote_lat = %s, remote_lon = %s
                    WHERE user_id = %s AND role = 'employee'
                """, (name, username, work_mode, remote_address, remote_lat, remote_lon, user_id))
            
            conn.commit()
            conn.close()
            
            flash(f'Employee {name} updated successfully!', 'success')
            return redirect(url_for('manage_employees'))
        
        # GET request - show form
        cursor.execute("SELECT * FROM users WHERE user_id = %s AND role = 'employee'", (user_id,))
        employee = cursor.fetchone()
        conn.close()
        
        if not employee:
            flash('Employee not found!', 'error')
            return redirect(url_for('manage_employees'))
        
        return render_template('edit_employee.html',
                             username=session['username'],
                             employee=employee)
        
    except Exception as e:
        print(f"Edit employee error: {e}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('manage_employees'))

@app.route('/admin/attendance')
@admin_required
def view_all_attendance():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all employees for dropdown
        cursor.execute("SELECT user_id, name FROM users WHERE role = 'employee' ORDER BY name")
        employees = cursor.fetchall()
        
        # Get selected employee and date range
        selected_employee = request.args.get('employee_id', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build query
        query = """
            SELECT a.*, u.name as employee_name 
            FROM attendance a 
            JOIN users u ON a.user_id = u.user_id 
            WHERE u.role = 'employee'
        """
        params = []
        
        if selected_employee:
            query += " AND a.user_id = %s"
            params.append(selected_employee)  # Keep as string for varchar(10)
        
        if start_date:
            query += " AND a.date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND a.date <= %s"
            params.append(end_date)
        
        query += " ORDER BY a.date DESC, a.check_in_time DESC LIMIT 100"
        
        cursor.execute(query, params)
        attendance_records = cursor.fetchall()
        
        conn.close()
        
        return render_template('admin_attendance.html',
                             username=session['username'],
                             employees=employees,
                             attendance_records=attendance_records,
                             selected_employee=selected_employee,
                             start_date=start_date,
                             end_date=end_date)
        
    except Exception as e:
        print(f"View attendance error: {e}")
        flash(f'Error loading attendance: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/employee_report/<user_id>')
@admin_required
def employee_report(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get employee details - user_id is string
        cursor.execute("SELECT * FROM users WHERE user_id = %s AND role = 'employee'", (user_id,))
        employee = cursor.fetchone()
        
        if not employee:
            flash('Employee not found!', 'error')
            return redirect(url_for('view_all_attendance'))
        
        # Get attendance records for last 30 days
        cursor.execute("""
            SELECT * FROM attendance 
            WHERE user_id = %s 
            ORDER BY date DESC 
            LIMIT 30
        """, (user_id,))
        attendance_records = cursor.fetchall()
        
        # Get monthly stats
        cursor.execute("""
            SELECT 
                DATE_FORMAT(date, '%Y-%m') as month,
                COUNT(*) as days_present,
                AVG(HOUR(check_in_time)) as avg_checkin_hour
            FROM attendance 
            WHERE user_id = %s AND check_in_time IS NOT NULL
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 6
        """, (user_id,))
        monthly_stats = cursor.fetchall()
        
        # Prepare chart data
        months = [stat['month'] for stat in monthly_stats] if monthly_stats else ['2025-08']
        attendance_counts = [stat['days_present'] for stat in monthly_stats] if monthly_stats else [0]
        avg_checkin_hours = [float(stat['avg_checkin_hour']) if stat['avg_checkin_hour'] else 9.0 for stat in monthly_stats] if monthly_stats else [9.0]
        
        chart_data = {
            'months': months,
            'attendance': attendance_counts,
            'avg_checkin_time': avg_checkin_hours
        }
        
        conn.close()
        
        return render_template('employee_report.html',
                             username=session['username'],
                             employee=employee,
                             attendance_records=attendance_records,
                             chart_data=chart_data)
        
    except Exception as e:
        print(f"Employee report error: {e}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_all_attendance'))

@app.route('/admin/geofence_requests')
@admin_required
def admin_geofence_requests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT gr.request_id, gr.user_id, u.name, u.username, gr.requested_lat, gr.requested_lon,
                   gr.request_date, gr.status
            FROM geofence_requests gr
            JOIN users u ON gr.user_id = u.user_id
            ORDER BY gr.request_date DESC
        """)
        requests_list = cursor.fetchall()
        conn.close()
        return render_template('geofence_requests.html', requests=requests_list, username=session['username'])
    except Exception as e:
        print(f"Admin geofence list error: {e}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/review_geofence/<int:request_id>', methods=['POST'])
@admin_required
def admin_review_geofence(request_id):
    decision = request.form.get('decision')
    admin_id = session.get('user_id')
    if decision not in ('approve','reject'):
        flash('Invalid decision','error')
        return redirect(url_for('admin_geofence_requests'))
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM geofence_requests WHERE request_id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            conn.close(); flash('Request not found','error'); return redirect(url_for('admin_geofence_requests'))
        if req['status'] != 'pending':
            conn.close(); flash('Request already reviewed','error'); return redirect(url_for('admin_geofence_requests'))
        cursor2 = conn.cursor()
        if decision == 'approve':
            cursor2.execute("UPDATE geofence_requests SET status='approved', reviewed_by=%s, review_date=NOW() WHERE request_id=%s", (admin_id, request_id))
            cursor2.execute("UPDATE users SET geofence_status='approved', geofence_lat=%s, geofence_lon=%s WHERE user_id=%s", (req['requested_lat'], req['requested_lon'], req['user_id']))
            flash('Geofence approved','success')
        else:
            cursor2.execute("UPDATE geofence_requests SET status='rejected', reviewed_by=%s, review_date=NOW() WHERE request_id=%s", (admin_id, request_id))
            cursor2.execute("UPDATE users SET geofence_status='rejected' WHERE user_id=%s", (req['user_id'],))
            flash('Geofence rejected','info')
        conn.commit(); conn.close()
        return redirect(url_for('admin_geofence_requests'))
    except Exception as e:
        print(f"Admin review geofence error: {e}")
        flash(f'Error: {str(e)}','error')
        return redirect(url_for('admin_geofence_requests'))

# ====================== ADMIN GEOFENCING ROUTES ======================

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Admin company settings page"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get all company settings
        cursor.execute("SELECT * FROM company_settings ORDER BY setting_name")
        settings = cursor.fetchall()
        
        # Convert to dict for easier template access
        settings_dict = {setting['setting_name']: setting['setting_value'] for setting in settings}
        
        cursor.close()
        return render_template('admin_settings.html', settings=settings_dict)
    except Exception as e:
        flash(f'Error loading settings: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/settings/update', methods=['POST'])
@admin_required
def update_company_settings():
    """Update company settings"""
    try:
        cursor = mysql.connection.cursor()
        
        office_address = request.form.get('office_address', '').strip()
        office_radius = request.form.get('office_radius', '200')
        geofencing_enabled = 'geofencing_enabled' in request.form
        
        # Update basic settings
        cursor.execute("""
            UPDATE company_settings 
            SET setting_value = %s 
            WHERE setting_name = 'office_address'
        """, (office_address,))
        
        cursor.execute("""
            UPDATE company_settings 
            SET setting_value = %s 
            WHERE setting_name = 'office_radius'
        """, (office_radius,))
        
        cursor.execute("""
            UPDATE company_settings 
            SET setting_value = %s 
            WHERE setting_name = 'geofencing_enabled'
        """, ('true' if geofencing_enabled else 'false',))
        
        # Geocode office address if provided
        if office_address:
            geocode_result = geocode_address(office_address)
            if geocode_result:
                cursor.execute("""
                    UPDATE company_settings 
                    SET setting_value = %s 
                    WHERE setting_name = 'office_lat'
                """, (str(geocode_result['lat']),))
                
                cursor.execute("""
                    UPDATE company_settings 
                    SET setting_value = %s 
                    WHERE setting_name = 'office_lon'
                """, (str(geocode_result['lon']),))
                
                flash(f'✅ Settings updated! Office coordinates: {geocode_result["lat"]:.6f}, {geocode_result["lon"]:.6f}', 'success')
            else:
                flash('⚠️ Settings updated, but unable to geocode office address. Please verify the address.', 'warning')
        else:
            flash('✅ Settings updated successfully!', 'success')
        
        mysql.connection.commit()
        cursor.close()
        
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/sites')
@admin_required
def admin_sites():
    """Admin sites management page"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT s.*, 
                   COUNT(sv.id) as total_visits,
                   COUNT(CASE WHEN sv.status = 'Pending' THEN 1 END) as pending_visits
            FROM sites s
            LEFT JOIN site_visits sv ON s.id = sv.site_id
            GROUP BY s.id
            ORDER BY s.site_name
        """)
        sites = cursor.fetchall()
        cursor.close()
        return render_template('admin_sites.html', sites=sites)
    except Exception as e:
        flash(f'Error loading sites: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/sites/add', methods=['POST'])
@admin_required
def add_site():
    """Add new site"""
    try:
        cursor = mysql.connection.cursor()
        
        site_name = request.form.get('site_name', '').strip()
        site_address = request.form.get('site_address', '').strip()
        site_radius = int(request.form.get('site_radius', 200))
        site_description = request.form.get('site_description', '').strip()
        
        if not site_name or not site_address:
            flash('Site name and address are required', 'error')
            return redirect(url_for('admin_sites'))
        
        # Geocode the address
        geocode_result = geocode_address(site_address)
        if not geocode_result:
            flash('Unable to geocode the address. Please verify and try again.', 'error')
            return redirect(url_for('admin_sites'))
        
        cursor.execute("""
            INSERT INTO sites (site_name, site_address, site_lat, site_lon, site_radius, site_description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (site_name, site_address, geocode_result['lat'], geocode_result['lon'], site_radius, site_description))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'✅ Site "{site_name}" added successfully!', 'success')
        
    except Exception as e:
        flash(f'Error adding site: {str(e)}', 'error')
    
    return redirect(url_for('admin_sites'))

@app.route('/admin/sites/toggle/<int:site_id>')
@admin_required
def toggle_site_status(site_id):
    """Toggle site active/inactive status"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT is_active FROM sites WHERE id = %s", (site_id,))
        site = cursor.fetchone()
        
        if site:
            new_status = not site['is_active']
            cursor.execute("UPDATE sites SET is_active = %s WHERE id = %s", (new_status, site_id))
            mysql.connection.commit()
            
            status_text = "activated" if new_status else "deactivated"
            flash(f'Site {status_text} successfully!', 'success')
        else:
            flash('Site not found', 'error')
        
        cursor.close()
        
    except Exception as e:
        flash(f'Error updating site status: {str(e)}', 'error')
    
    return redirect(url_for('admin_sites'))

@app.route('/admin/visit-requests')
@admin_required
def admin_visit_requests():
    """Admin visit requests management page"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT sv.*, s.site_name, s.site_address, u.name as employee_name
            FROM site_visits sv
            JOIN sites s ON sv.site_id = s.id
            JOIN users u ON sv.user_id = u.user_id
            ORDER BY sv.requested_at DESC, sv.visit_date DESC
        """)
        visit_requests = cursor.fetchall()
        cursor.close()
        return render_template('admin_visit_requests.html', visit_requests=visit_requests)
    except Exception as e:
        flash(f'Error loading visit requests: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/visit-requests/update/<int:request_id>', methods=['POST'])
@admin_required
def update_visit_request(request_id):
    """Approve or reject visit request"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        action = request.form.get('action')
        admin_notes = request.form.get('admin_notes', '').strip()
        
        if action not in ['approve', 'reject']:
            flash('Invalid action', 'error')
            return redirect(url_for('admin_visit_requests'))
        
        new_status = 'Approved' if action == 'approve' else 'Rejected'
        
        cursor.execute("""
            UPDATE site_visits 
            SET status = %s, admin_notes = %s, approved_by = %s, approved_date = NOW()
            WHERE id = %s
        """, (new_status, admin_notes, session['user_id'], request_id))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'✅ Visit request {new_status.lower()} successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating visit request: {str(e)}', 'error')
    
    return redirect(url_for('admin_visit_requests'))

@app.route('/admin/remote-requests')
@admin_required
def admin_remote_requests():
    """Admin remote work requests management page"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT r.*, u.name as employee_name
            FROM remote_work_requests r
            JOIN users u ON r.user_id = u.user_id
            ORDER BY r.start_date DESC, r.requested_at DESC
        """)
        remote_requests = cursor.fetchall()
        cursor.close()
        return render_template('admin_remote_requests.html', remote_requests=remote_requests)
    except Exception as e:
        flash(f'Error loading remote requests: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/remote-requests/update/<int:request_id>', methods=['POST'])
@admin_required
def update_remote_request(request_id):
    """Approve or reject remote work request"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        action = request.form.get('action')
        review_notes = request.form.get('review_notes', '').strip()
        
        if action not in ['approve', 'reject']:
            flash('Invalid action', 'error')
            return redirect(url_for('admin_remote_requests'))
        
        new_status = 'Approved' if action == 'approve' else 'Rejected'
        
        cursor.execute("""
            UPDATE remote_work_requests 
            SET status = %s, review_notes = %s, reviewed_by = %s, reviewed_at = NOW()
            WHERE id = %s
        """, (new_status, review_notes, session['user_id'], request_id))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'✅ Remote request {new_status.lower()} successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating remote request: {str(e)}', 'error')
    
    return redirect(url_for('admin_remote_requests'))

# ====================== EMPLOYEE GEOFENCING ROUTES ======================

@app.route('/request-visit')
@login_required
def request_visit():
    """Employee visit request page"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get active sites
        cursor.execute("SELECT * FROM sites WHERE is_active = TRUE ORDER BY site_name")
        sites = cursor.fetchall()
        
        # Get user's pending/approved requests
        cursor.execute("""
            SELECT sv.*, s.site_name, s.site_address
            FROM site_visits sv
            JOIN sites s ON sv.site_id = s.id
            WHERE sv.user_id = %s 
            AND sv.visit_date >= CURDATE()
            ORDER BY sv.visit_date DESC
        """, (session['user_id'],))
        my_requests = cursor.fetchall()
        
        cursor.close()
        return render_template('request_visit.html', sites=sites, my_requests=my_requests)
    except Exception as e:
        flash(f'Error loading visit request page: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/request-visit/submit', methods=['POST'])
@login_required
def submit_visit_request():
    """Submit new visit request"""
    try:
        cursor = mysql.connection.cursor()
        
        site_id = request.form.get('site_id')
        visit_date = request.form.get('visit_date')
        purpose = request.form.get('purpose', '').strip()
        
        if not site_id or not visit_date or not purpose:
            flash('All fields are required', 'error')
            return redirect(url_for('request_visit'))
        
        # Validate date is not in the past
        from datetime import datetime
        visit_date_obj = datetime.strptime(visit_date, '%Y-%m-%d').date()
        if visit_date_obj < date.today():
            flash('Visit date cannot be in the past', 'error')
            return redirect(url_for('request_visit'))
        
        # Check for existing request for same date
        cursor.execute("""
            SELECT id FROM site_visits 
            WHERE user_id = %s AND visit_date = %s
        """, (session['user_id'], visit_date))
        
        if cursor.fetchone():
            flash('You already have a visit request for this date', 'error')
            cursor.close()
            return redirect(url_for('request_visit'))
        
        # Insert new request
        cursor.execute("""
            INSERT INTO site_visits (user_id, site_id, visit_date, purpose, status, requested_at)
            VALUES (%s, %s, %s, %s, 'Pending', NOW())
        """, (session['user_id'], site_id, visit_date, purpose))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('✅ Visit request submitted successfully! Awaiting admin approval.', 'success')
        
    except Exception as e:
        flash(f'Error submitting visit request: {str(e)}', 'error')
    
    return redirect(url_for('request_visit'))

@app.route('/request-remote')
@login_required
def request_remote():
    """Employee remote work request page"""
    try:
        print(f"[DEBUG] Accessing request_remote for user {session.get('user_id')}")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get user's pending/approved requests
        print("[DEBUG] Executing query...")
        cursor.execute("""
            SELECT * FROM remote_work_requests 
            WHERE user_id = %s 
            AND end_date >= CURDATE()
            ORDER BY start_date DESC
        """, (session['user_id'],))
        requests_list = cursor.fetchall()
        print(f"[DEBUG] Found {len(requests_list)} requests")
        
        cursor.close()
        return render_template('request_remote.html', requests=requests_list, today_date=date.today())
    except Exception as e:
        print(f"[ERROR] request_remote failed: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error Loading Page</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"

@app.route('/request-remote/submit', methods=['POST'])
@login_required
def submit_remote_request():
    """Submit new remote work request"""
    try:
        cursor = mysql.connection.cursor()
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        address = request.form.get('address', '').strip()
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        reason = request.form.get('reason', '').strip()
        
        if not start_date or not end_date or not address or not lat or not lon or not reason:
            flash('All fields are required', 'error')
            return redirect(url_for('request_remote'))
        
        # Validate date is not in the past
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj < date.today():
            flash('Start date cannot be in the past', 'error')
            return redirect(url_for('request_remote'))
            
        if end_date_obj < start_date_obj:
            flash('End date cannot be before start date', 'error')
            return redirect(url_for('request_remote'))
        
        # Check for overlapping requests
        cursor.execute("""
            SELECT id FROM remote_work_requests 
            WHERE user_id = %s 
            AND (
                (start_date <= %s AND end_date >= %s)
            )
        """, (session['user_id'], end_date, start_date))
        
        if cursor.fetchone():
            flash('You already have a remote work request overlapping with this period', 'error')
            cursor.close()
            return redirect(url_for('request_remote'))
        
        # Insert new request
        cursor.execute("""
            INSERT INTO remote_work_requests (user_id, start_date, end_date, address, lat, lon, reason, status, requested_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending', NOW())
        """, (session['user_id'], start_date, end_date, address, lat, lon, reason))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('✅ Remote work request submitted successfully! Awaiting admin approval.', 'success')
        
    except Exception as e:
        flash(f'Error submitting remote request: {str(e)}', 'error')
    
    return redirect(url_for('request_remote'))

# ====================== EMPLOYEE ROUTES ======================

@app.route('/dashboard')
@employee_required
def dashboard():
    """Dashboard with support for both HTML rendering and JSON API"""
    user_id = session.get('user_id')
    today = date.today()
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attendance WHERE user_id = %s AND date = %s", (user_id, today))
        today_attendance = cursor.fetchone()
        cursor.execute("SELECT geofence_status, compoff_balance FROM users WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        geofence_status = row['geofence_status'] if row else 'none'
        compoff_balance = row.get('compoff_balance',0) if row else 0
        conn.close()
        
        # Return JSON if requested via API
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'status': 'success',
                'username': session['username'],
                'employee_name': session['employee_name'],
                'today_attendance': today_attendance,
                'geofence_status': geofence_status,
                'compoff_balance': compoff_balance
            }), 200
        
        # Otherwise render HTML template
        return render_template('dashboard.html',
                               username=session['username'],
                               employee_name=session['employee_name'],
                               today_attendance=today_attendance,
                               geofence_status=geofence_status,
                               compoff_balance=compoff_balance)
    except Exception as e:
        print(f"Dashboard error: {e}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'status': 'error', 'message': str(e)}), 500
        flash(f'Dashboard error: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/mark')
@employee_required
def mark_attendance():
    user_id = session.get('user_id')
    today = date.today()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM attendance WHERE user_id = %s AND date = %s", 
            (user_id, today)
        )
        today_attendance = cursor.fetchone()
        conn.close()
        
        return render_template('mark_attendance.html',
                             username=session['username'],
                             employee_name=session['employee_name'],
                             today_attendance=today_attendance)
    except Exception as e:
        print(f"Mark attendance error: {e}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/checkin', methods=['POST', 'OPTIONS'])
@csrf.exempt
@employee_required
def checkin():
    """
    SIMPLIFIED CHECK-IN LOGIC (v2)
    - Returns 200 OK for ALL outcomes to prevent browser 'Network Error'
    - Uses 'status' field in JSON to indicate success/failure
    """
    print(f"\n[CHECKIN v2] Request received from {session.get('username')}")
    
    # Handle CORS Preflight
    if request.method == 'OPTIONS':
        print("[CHECKIN v2] Handling OPTIONS preflight")
        return jsonify({'status': 'ok'}), 200

    # 1. Safe Data Extraction
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Session expired. Please login again.'}), 200

        # Handle Data (JSON or FormData)
        if request.is_json:
            data = request.get_json()
            lat = data.get('latitude')
            lon = data.get('longitude')
            image_data = data.get('image')
            print(f"[CHECKIN v2] JSON Payload received")
        else:
            lat = request.form.get('latitude')
            lon = request.form.get('longitude')
            image_data = request.form.get('image')
            print(f"[CHECKIN v2] FormData Payload received")
        
        print(f"[CHECKIN v2] Data: Lat={lat}, Lon={lon}, Image={'Yes' if image_data else 'No'}")

        if not lat or not lon:
            return jsonify({'status': 'error', 'message': 'Location data missing.'}), 200
            
        try:
            latitude = float(lat)
            longitude = float(lon)
        except:
            return jsonify({'status': 'error', 'message': 'Invalid coordinates format.'}), 200

    except Exception as e:
        print(f"[CHECKIN v2] Input Error: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid request data.'}), 200

    # 2. Database Operations
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        today = date.today()
        now = datetime.now()

        # Check existing
        cursor.execute("SELECT check_in_time FROM attendance WHERE user_id=%s AND date=%s", (user_id, today))
        existing = cursor.fetchone()
        if existing and existing['check_in_time']:
            return jsonify({'status': 'error', 'message': 'Already checked in today.'}), 200

        # Validate Location (Unified Logic)
        try:
            loc_valid = validate_location_unified(cursor, user_id, latitude, longitude, today)
            if not loc_valid['valid']:
                return jsonify({
                    'status': 'error', 
                    'message': loc_valid['message'],
                    'details': loc_valid.get('details')
                }), 200
        except Exception as loc_e:
            print(f"[CHECKIN v2] Location Validation Error: {loc_e}")
            return jsonify({'status': 'error', 'message': 'Location validation error. Contact admin.'}), 200

        # Save Image
        image_filename = None
        if image_data:
            try:
                if "data:image" in image_data:
                    _, encoded = image_data.split(",", 1)
                else:
                    encoded = image_data
                
                img_bytes = base64.b64decode(encoded)
                image_filename = f"checkin_{user_id}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, image_filename)
                with open(filepath, "wb") as f:
                    f.write(img_bytes)
            except Exception as img_e:
                print(f"[CHECKIN v2] Image Save Error: {img_e}")
                pass

        # Get Address
        address = "Unknown Location"
        try:
            address = get_address_from_coords(latitude, longitude)
        except:
            pass

        # Determine attendance type
        cursor.execute("SELECT 1 FROM compoff_requests WHERE user_id=%s AND work_date=%s AND status='Approved'", (user_id, today))
        is_compoff = cursor.fetchone()
        attendance_type = 'Comp-Off' if is_compoff else 'Regular'

        # Insert/Update DB
        if existing:
            cursor.execute("""
                UPDATE attendance SET 
                check_in_time=%s, check_in_latitude=%s, check_in_longitude=%s, 
                check_in_address=%s, image_path_checkin=%s, attendance_type=%s
                WHERE user_id=%s AND date=%s
            """, (now, latitude, longitude, address, image_filename, attendance_type, user_id, today))
        else:
            cursor.execute("""
                INSERT INTO attendance 
                (user_id, date, check_in_time, check_in_latitude, check_in_longitude, 
                 check_in_address, image_path_checkin, attendance_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, today, now, latitude, longitude, address, image_filename, attendance_type))
        
        conn.commit()
        print(f"[CHECKIN v2] Success for {user_id}")
        
        return jsonify({
            'status': 'success', 
            'message': 'Check-in Successful!',
            'time': now.strftime('%H:%M:%S')
        }), 200

    except Exception as e:
        print(f"[CHECKIN v2] System Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'System Error: {str(e)}'}), 200
    
    finally:
        if conn:
            conn.close()

@app.route('/checkout', methods=['POST'])
@csrf.exempt
@employee_required
def checkout():
    """Handle employee check-out with photo and location"""
    user_id = session.get('user_id')
    today = date.today()
    now = datetime.now()
    
    print(f"\n[CHECKOUT] Starting check-out for user {user_id} at {now}")
    
    conn = None
    try:
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if checked in
        cursor.execute(
            "SELECT * FROM attendance WHERE user_id = %s AND date = %s",
            (user_id, today)
        )
        existing = cursor.fetchone()
        
        if not existing or not existing.get('check_in_time'):
            print(f"[CHECKOUT] User {user_id} not checked in")
            return jsonify({
                'status': 'error',
                'message': 'Please check-in first!'
            }), 400
        
        if existing.get('check_out_time'):
            print(f"[CHECKOUT] User {user_id} already checked out")
            return jsonify({
                'status': 'error',
                'message': 'Already checked out today!'
            }), 400
        
        # Get request data
        image_data = request.form.get('image', '')
        try:
            latitude = float(request.form.get('latitude', 0))
            longitude = float(request.form.get('longitude', 0))
        except (ValueError, TypeError):
            print(f"[CHECKOUT] Invalid coordinates")
            return jsonify({
                'status': 'error',
                'message': 'Invalid location data'
            }), 400
        
        print(f"[CHECKOUT] Location: {latitude}, {longitude}")
        
        # Validate location
        validation_result = validate_location_unified(cursor, user_id, latitude, longitude, today)
        
        if not validation_result['valid']:
            print(f"[CHECKOUT] Location validation failed: {validation_result['message']}")
            return jsonify({
                'status': 'error',
                'message': validation_result['message'],
                'location_type': validation_result.get('location_type'),
                'details': validation_result.get('details')
            }), 400
        
        print(f"[CHECKOUT] Location validated: {validation_result['message']}")
        
        # Save photo
        image_filename = None
        if image_data and image_data.strip():
            try:
                if "data:image" in image_data:
                    header, encoded = image_data.split(",", 1)
                else:
                    encoded = image_data
                
                img_bytes = base64.b64decode(encoded)
                image_filename = f"checkout_{user_id}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                
                with open(image_path, "wb") as f:
                    f.write(img_bytes)
                
                print(f"[CHECKOUT] Photo saved: {image_filename}")
            except Exception as e:
                print(f"[CHECKOUT] Photo save error (non-fatal): {e}")
        
        # Get address
        address = get_address_from_coords(latitude, longitude)
        print(f"[CHECKOUT] Address: {address}")
        
        # Update database
        cursor2 = conn.cursor()
        cursor2.execute("""
            UPDATE attendance SET 
            check_out_time = %s, check_out_latitude = %s, check_out_longitude = %s,
            check_out_address = %s, image_path_checkout = %s
            WHERE user_id = %s AND date = %s
        """, (now, latitude, longitude, address, image_filename, user_id, today))
        
        conn.commit()
        print(f"[CHECKOUT] Database updated successfully")
        
        return jsonify({
            'status': 'success',
            'message': 'Check-out successful!',
            'time': now.strftime('%H:%M:%S'),
            'address': address
        }), 200
        
    except Exception as e:
        print(f"[CHECKOUT] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': f'Check-out failed: {str(e)}'
        }), 500
        
    finally:
        if conn:
            try:
                conn.close()
                print(f"[CHECKOUT] Connection closed")
            except:
                pass

@app.route('/view_attendance')
@employee_required
def view_attendance():
    user_id = session.get('user_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get attendance records
        cursor.execute("""
            SELECT * FROM attendance 
            WHERE user_id = %s 
            ORDER BY date DESC 
            LIMIT 30
        """, (user_id,))
        attendance_records = cursor.fetchall()
        
        # Get monthly statistics for charts
        cursor.execute("""
            SELECT 
                DATE_FORMAT(date, '%Y-%m') as month,
                COUNT(*) as days_present
            FROM attendance 
            WHERE user_id = %s AND check_in_time IS NOT NULL
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 6
        """, (user_id,))
        monthly_stats = cursor.fetchall()
        
        # Get average check-in times
        cursor.execute("""
            SELECT 
                DATE_FORMAT(date, '%Y-%m') as month,
                AVG(HOUR(check_in_time)) as avg_hour
            FROM attendance 
            WHERE user_id = %s AND check_in_time IS NOT NULL
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 6
        """, (user_id,))
        checkin_stats = cursor.fetchall()
        
        conn.close()
        
        # Prepare chart data
        months = [stat['month'] for stat in monthly_stats] if monthly_stats else ['2025-08', '2025-07', '2025-06']
        attendance_counts = [stat['days_present'] for stat in monthly_stats] if monthly_stats else [5, 8, 6]
        avg_checkin_hours = [float(stat['avg_hour']) if stat['avg_hour'] else 9.0 for stat in checkin_stats] if checkin_stats else [9.2, 9.1, 9.3]
        
        chart_data = {
            'months': months,
            'attendance': attendance_counts,
            'avg_checkin_time': avg_checkin_hours
        }
        
        return render_template('view_attendance.html',
                             username=session['username'],
                             employee_name=session['employee_name'],
                             attendance_records=attendance_records,
                             chart_data=chart_data)
    except Exception as e:
        print(f"View attendance error: {e}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/request_geofence', methods=['POST'])
@employee_required
def request_geofence():
    user_id = session.get('user_id')
    try:
        data = request.get_json() or request.form
        lat = data.get('latitude')
        lon = data.get('longitude')
        if lat is None or lon is None:
            flash('Geofence request failed: coordinates missing','error')
            return jsonify({'status': 'error', 'message': 'Latitude & longitude required'}), 400
        lat = float(lat); lon = float(lon)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT geofence_status FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close(); flash('Geofence request failed: user not found','error')
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        if row['geofence_status'] != 'none':
            conn.close(); flash('You have already submitted a geofence request','info')
            return jsonify({'status': 'error', 'message': 'Geofence already requested or decided'}), 400
        cursor2 = conn.cursor()
        cursor2.execute("""
            INSERT INTO geofence_requests (user_id, requested_lat, requested_lon)
            VALUES (%s, %s, %s)
        """, (user_id, lat, lon))
        cursor2.execute("UPDATE users SET geofence_status = 'pending' WHERE user_id = %s", (user_id,))
        conn.commit(); conn.close()
        flash('Geofence request submitted. Await admin approval.','success')
        return jsonify({'status': 'success', 'message': 'Geofence request submitted', 'new_status': 'pending'})
    except Exception as e:
        print(f"[ERROR] Geofence request: {e}")
        flash('Geofence request failed','error')
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ====================== EMPLOYEE LEAVE ROUTES ======================
@app.route('/myleave')
@employee_required
def myleave():
    """Employee self-service leave page: balances + history."""
    user_id = session.get('user_id')
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        # Fetch balances
        cursor.execute("""
            SELECT vacation_days_total, sick_days_total,
                   vacation_days_taken, sick_days_taken
            FROM users WHERE user_id=%s
        """, (user_id,))
        balances = cursor.fetchone() or {}
        # Fetch history (latest 25)
        cursor.execute("""
            SELECT leave_id, leave_type, start_date, end_date, reason, status, request_date, reviewed_by, review_date
            FROM leave_requests WHERE user_id=%s
            ORDER BY request_date DESC LIMIT 25
        """, (user_id,))
        history = cursor.fetchall()
        conn.close()
        # Compute remaining
        vac_remaining = (balances.get('vacation_days_total',0) - balances.get('vacation_days_taken',0)) if balances else 0
        sick_remaining = (balances.get('sick_days_total',0) - balances.get('sick_days_taken',0)) if balances else 0

        # Status counters
        status_counts = {'Approved':0,'Rejected':0,'Pending':0}
        for r in history:
            if r['status'] in status_counts:
                status_counts[r['status']] += 1
        return render_template('myleave.html',
                               username=session['username'],
                               employee_name=session.get('employee_name'),
                               balances=balances,
                               vac_remaining=vac_remaining,
                               sick_remaining=sick_remaining,
                               history=history,
                               status_counts=status_counts)
    except Exception as e:
        print(f"MyLeave error: {e}")
        flash('Failed to load leave page','error')
        return redirect(url_for('dashboard'))

@app.route('/request_leave', methods=['POST'])
@employee_required
def request_leave():
    """Handle submission of a leave request with validation and balance checks."""
    user_id = session.get('user_id')
    leave_type = request.form.get('leave_type')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    reason = (request.form.get('reason') or '').strip()

    # Basic presence validation
    if not leave_type or not start_date_str or not end_date_str or not reason:
        flash('All fields are required.','error')
        return redirect(url_for('myleave'))
    try:
        start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.','error')
        return redirect(url_for('myleave'))

    if end_dt < start_dt:
        flash('End date cannot be before start date.','error')
        return redirect(url_for('myleave'))

    # Duration (inclusive days)
    days_requested = (end_dt - start_dt).days + 1
    if days_requested <= 0:
        flash('Invalid date range.','error')
        return redirect(url_for('myleave'))

    # Only allow current year for simplicity (optional business rule)
    if start_dt.year != end_dt.year:
        flash('Cross-year leave not supported in this version. Submit separate requests.','error')
        return redirect(url_for('myleave'))

    allowed_types = {'Vacation': 'vacation', 'Sick Leave': 'sick', 'Personal Day': 'vacation'}
    if leave_type not in allowed_types:
        flash('Invalid leave type.','error')
        return redirect(url_for('myleave'))

    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT vacation_days_total, sick_days_total,
                   vacation_days_taken, sick_days_taken
            FROM users WHERE user_id=%s
        """, (user_id,))
        balances = cursor.fetchone()
        if not balances:
            conn.close(); flash('User not found for leave.','error'); return redirect(url_for('myleave'))

        if leave_type in ('Vacation','Personal Day'):
            remaining = balances['vacation_days_total'] - balances['vacation_days_taken']
            if days_requested > remaining:
                conn.close(); flash(f'Insufficient vacation balance. You have {remaining} day(s) left.','error'); return redirect(url_for('myleave'))
        elif leave_type == 'Sick Leave':
            remaining = balances['sick_days_total'] - balances['sick_days_taken']
            if days_requested > remaining:
                conn.close(); flash(f'Insufficient sick leave balance. You have {remaining} day(s) left.','error'); return redirect(url_for('myleave'))

        # Overlap check: existing approved or pending requests (simple date range overlap)
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM leave_requests
            WHERE user_id=%s AND status IN ('Pending','Approved')
              AND NOT (end_date < %s OR start_date > %s)
        """, (user_id, start_dt, end_dt))
        overlap = cursor.fetchone()['cnt']
        if overlap:
            conn.close(); flash('You already have a pending/approved leave overlapping these dates.','error'); return redirect(url_for('myleave'))

        # Insert request
        cursor2 = conn.cursor()
        cursor2.execute("""
            INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, leave_type, start_dt, end_dt, reason))
        conn.commit(); conn.close()
        flash(f'Leave request submitted for {days_requested} day(s).','success')
        return redirect(url_for('myleave'))
    except Exception as e:
        print(f"Request leave error: {e}")
        flash('Failed to submit leave request.','error')
        return redirect(url_for('myleave'))

@app.route('/myleave/export')
@employee_required
def myleave_export():
    """Export full leave history as CSV."""
    import csv, io
    user_id = session.get('user_id')
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT leave_id, leave_type, start_date, end_date, reason, status, request_date, reviewed_by, review_date
            FROM leave_requests WHERE user_id=%s ORDER BY request_date DESC
        """, (user_id,))
        rows = cursor.fetchall(); conn.close()
        output = io.StringIO(); writer = csv.writer(output)
        writer.writerow(['leave_id','leave_type','start_date','end_date','days','status','reason','request_date','reviewed_by','review_date'])
        for r in rows:
            days = (r['end_date'] - r['start_date']).days + 1 if r['start_date'] and r['end_date'] else ''
            writer.writerow([r['leave_id'], r['leave_type'], r['start_date'], r['end_date'], days, r['status'], r['reason'], r['request_date'], r['reviewed_by'], r['review_date']])
        from flask import make_response
        resp = make_response(output.getvalue())
        resp.headers['Content-Type'] = 'text/csv'
        resp.headers['Content-Disposition'] = f'attachment; filename=leave_history_{user_id}.csv'
        return resp
    except Exception as e:
        print(f"Leave export error: {e}")
        flash('Export failed','error')
        return redirect(url_for('myleave'))

# ====================== ADMIN LEAVE ROUTES ======================
@app.route('/admin/leave_management')
@admin_required
def admin_leave_management():
    """Admin view for pending leave requests."""
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT lr.leave_id, lr.user_id, u.name, u.username, lr.leave_type,
                   lr.start_date, lr.end_date, lr.reason, lr.status, lr.request_date
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.user_id
            WHERE lr.status='Pending'
            ORDER BY lr.request_date ASC
        """)
        pending = cursor.fetchall()
        # Simple stats (could be expanded)
        cursor.execute("SELECT COUNT(*) AS total_pending FROM leave_requests WHERE status='Pending'")
        stats = cursor.fetchone()
        conn.close()
        return render_template('leave_management.html',
                               username=session['username'],
                               pending_requests=pending,
                               stats=stats)
    except Exception as e:
        print(f"Admin leave management error: {e}")
        flash('Failed to load leave management','error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/review_leave/<int:leave_id>', methods=['POST'])
@admin_required
def admin_review_leave(leave_id):
    """Approve or reject a leave request and update balances if approved."""
    decision = request.form.get('decision')  # 'Approve' or 'Reject'
    if decision not in ('Approve','Reject'):
        flash('Invalid decision.','error'); return redirect(url_for('admin_leave_management'))
    admin_id = session.get('user_id')
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM leave_requests WHERE leave_id=%s", (leave_id,))
        req = cursor.fetchone()
        if not req:
            conn.close(); flash('Leave request not found.','error'); return redirect(url_for('admin_leave_management'))
        if req['status'] != 'Pending':
            conn.close(); flash('Request already processed.','info'); return redirect(url_for('admin_leave_management'))
        # Calculate days
        days = (req['end_date'] - req['start_date']).days + 1
        cursor2 = conn.cursor()
        if decision == 'Approve':
            # Update leave_requests row
            cursor2.execute("""
                UPDATE leave_requests SET status='Approved', reviewed_by=%s, review_date=NOW()
                WHERE leave_id=%s
            """, (admin_id, leave_id))
            # Update user balances (increment taken)
            if req['leave_type'] in ('Vacation','Personal Day'):
                cursor2.execute("""
                    UPDATE users SET vacation_days_taken = vacation_days_taken + %s
                    WHERE user_id=%s
                """, (days, req['user_id']))
            elif req['leave_type'] == 'Sick Leave':
                cursor2.execute("""
                    UPDATE users SET sick_days_taken = sick_days_taken + %s
                    WHERE user_id=%s
                """, (days, req['user_id']))
            flash(f'Leave request #{leave_id} approved for {days} day(s).','success')
        else:
            cursor2.execute("""
                UPDATE leave_requests SET status='Rejected', reviewed_by=%s, review_date=NOW()
                WHERE leave_id=%s
            """, (admin_id, leave_id))
            flash(f'Leave request #{leave_id} rejected.','info')
        conn.commit(); conn.close()
        return redirect(url_for('admin_leave_management'))
    except Exception as e:
        print(f"Admin review leave error: {e}")
        flash('Error processing leave request.','error')
        return redirect(url_for('admin_leave_management'))

@app.route('/admin/holidays')
@admin_required
def admin_holidays():
    """List and manage company holidays (current year)."""
    try:
        year = int(request.args.get('year', date.today().year))
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM holidays WHERE holiday_date BETWEEN %s AND %s ORDER BY holiday_date", (start, end))
        holidays = cursor.fetchall()
        conn.close()
        return render_template('holidays.html', username=session['username'], holidays=holidays, year=year)
    except Exception as e:
        print(f"Holiday list error: {e}")
        flash('Failed to load holidays','error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_holiday', methods=['POST'])
@admin_required
def add_holiday():
    date_str = request.form.get('holiday_date')
    name = (request.form.get('holiday_name') or '').strip()
    if not date_str or not name:
        flash('Holiday date and name required','error'); return redirect(url_for('admin_holidays'))
    try:
        hdate = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid holiday date','error'); return redirect(url_for('admin_holidays'))
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("INSERT INTO holidays (holiday_date, holiday_name) VALUES (%s,%s) ON DUPLICATE KEY UPDATE holiday_name=VALUES(holiday_name)", (hdate, name))
        conn.commit(); conn.close(); flash('Holiday saved','success')
    except Exception as e:
        print(f"Add holiday error: {e}"); flash('Failed to save holiday','error')
    return redirect(url_for('admin_holidays'))

@app.route('/admin/delete_holiday/<int:holiday_id>', methods=['POST'])
@admin_required
def delete_holiday(holiday_id):
    try:
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("DELETE FROM holidays WHERE holiday_id=%s", (holiday_id,))
        conn.commit(); conn.close(); flash('Holiday deleted','success')
    except Exception as e:
        print(f"Delete holiday error: {e}"); flash('Failed to delete holiday','error')
    return redirect(url_for('admin_holidays'))

@app.route('/admin/employee_attendance_data/<user_id>')
@admin_required
def employee_attendance_data(user_id):
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    try:
        today = date.today()
        if not start_date_str:
            start_date = today.replace(day=1)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if not end_date_str:
            # last day of current month
            next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if end_date < start_date:
            return jsonify({'error':'Invalid range'}), 400
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE user_id=%s AND role='employee'", (user_id,))
        if not cursor.fetchone():
            conn.close(); return jsonify({'error':'User not found'}), 404
        # Attendance rows (include type)
        cursor.execute("""
            SELECT date, attendance_type
            FROM attendance
            WHERE user_id=%s AND date BETWEEN %s AND %s AND check_in_time IS NOT NULL
        """, (user_id, start_date, end_date))
        att_rows = cursor.fetchall()
        # Approved leave days with type
        cursor.execute("""
            SELECT leave_type, start_date, end_date FROM leave_requests
            WHERE user_id=%s AND status='Approved' AND NOT (end_date < %s OR start_date > %s)
        """, (user_id, start_date, end_date))
        leave_rows = cursor.fetchall()
        conn.close()
        present_dates = {}
        for r in att_rows:
            if r['attendance_type'] == 'Comp-Off':
                present_dates[r['date']] = 'comp_off'
            else:
                present_dates[r['date']] = 'present'
        leave_map = {}
        for lr in leave_rows:
            cur = max(lr['start_date'], start_date)
            last = min(lr['end_date'], end_date)
            while cur <= last:
                if cur not in present_dates:  # do not override worked days
                    leave_map[cur] = lr['leave_type']
                cur += timedelta(days=1)
        data = []
        for d, st in sorted(present_dates.items()):
            if st == 'comp_off':
                data.append({'date': d.strftime('%Y-%m-%d'), 'status': 'comp_off'})
            else:
                data.append({'date': d.strftime('%Y-%m-%d'), 'status': 'present'})
        for d, ltype in sorted(leave_map.items()):
            data.append({'date': d.strftime('%Y-%m-%d'), 'status': 'on_leave', 'leave_type': ltype})
        return jsonify(data)
    except Exception as e:
        print(f"Attendance data API error: {e}")
        return jsonify({'error':'Server error'}), 500

# ====================== ERROR HANDLERS ======================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# ====================== DEBUG ROUTES (Remove in production) ======================

@app.route('/debug/users')
def debug_users():
    """Debug route to check users in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, name, role FROM users")
        users = cursor.fetchall()
        conn.close()
        return f"<h2>Debug: Users in Database</h2><pre>{users}</pre><br><a href='/'>Back to Login</a>"
    except Exception as e:
        return f"<h2>Debug Error:</h2><pre>{str(e)}</pre><br><a href='/'>Back to Login</a>"

@app.route('/debug/test-login')
def debug_test_login():
    """Debug route to test admin login"""
    return '''
    <h2>Debug: Test Admin Login</h2>
    <p>Use these credentials based on your database:</p>
    <ul>
        <li><strong>Username:</strong> francis</li>
        <li><strong>Password:</strong> adminpassword</li>
        <li><strong>Role:</strong> admin</li>
    </ul>
    <form method="POST" action="/login">
        <input type="hidden" name="role" value="admin">
        <input type="text" name="username" value="francis" placeholder="Username"><br><br>
        <input type="password" name="password" value="adminpassword" placeholder="Password"><br><br>
        <button type="submit">Test Admin Login</button>
    </form>
    <br><a href="/">Back to Main Login</a>
    '''

# ====================== COMP-OFF / HOLIDAY HELPERS ======================

def is_sunday(d: date) -> bool:
    return d.weekday() == 6  # Monday=0 .. Sunday=6


def get_holidays_between(cursor, start_d: date, end_d: date):
    """Return set of holiday dates between range inclusive."""
    cursor.execute("SELECT holiday_date FROM holidays WHERE holiday_date BETWEEN %s AND %s", (start_d, end_d))
    return {row['holiday_date'] for row in cursor.fetchall()}


def is_holiday(cursor, d: date) -> bool:
    cursor.execute("SELECT 1 FROM holidays WHERE holiday_date=%s", (d,))
    return cursor.fetchone() is not None


def is_non_working_day(cursor, d: date) -> bool:
    """Company non-working day definition: Sunday OR defined holiday."""
    return is_sunday(d) or is_holiday(cursor, d)


def get_upcoming_non_working_days(cursor, days_ahead: int = 45):
    """Compute list of upcoming non-working days (next N days) including today.
    Only include days that do not already have an approved / pending comp-off request for the current user (filtered later).
    Returns list[date]."""
    today = date.today()
    end = today + timedelta(days=days_ahead)
    holidays = get_holidays_between(cursor, today, end)
    results = []
    cur = today
    while cur <= end:
        if cur.weekday() == 6 or cur in holidays:  # Sunday or known holiday
            results.append(cur)
        cur += timedelta(days=1)
    return results

# ====================== COMP-OFF ROUTES (Employee) ======================

@app.route('/request_compoff', methods=['GET', 'POST'])
@employee_required
def request_compoff():
    """Employee requests permission to work on an upcoming non-working day (Sunday/holiday).
    POST: validate date is future non-working day and not already requested/approved; insert pending request.
    GET: list valid upcoming non-working days and recent request history."""
    user_id = session.get('user_id')
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            date_str = request.form.get('work_date')
            reason = (request.form.get('reason') or '').strip()
            if not date_str or not reason:
                flash('Date and reason required','error'); conn.close(); return redirect(url_for('request_compoff'))
            try:
                work_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format','error'); conn.close(); return redirect(url_for('request_compoff'))
            today = date.today()
            if work_date < today:
                flash('Date must be in the future or today','error'); conn.close(); return redirect(url_for('request_compoff'))
            # Must be non-working day
            if not is_non_working_day(cursor, work_date):
                flash('Selected date is not a company non-working day','error'); conn.close(); return redirect(url_for('request_compoff'))
            # No duplicate pending/approved
            cursor.execute("""
                SELECT 1 FROM compoff_requests
                WHERE user_id=%s AND work_date=%s AND status IN ('Pending','Approved')
            """, (user_id, work_date))
            if cursor.fetchone():
                flash('You already have a pending/approved request for this date','info'); conn.close(); return redirect(url_for('request_compoff'))
            cursor2 = conn.cursor()
            cursor2.execute("""
                INSERT INTO compoff_requests (user_id, work_date, reason)
                VALUES (%s,%s,%s)
            """, (user_id, work_date, reason))
            conn.commit(); conn.close(); flash('Comp-off request submitted','success'); return redirect(url_for('request_compoff'))
        # GET flow
        # Compute upcoming valid non-working days
        upcoming = get_upcoming_non_working_days(cursor, 60)
        # Filter out those with existing pending/approved requests
        if upcoming:
            cursor.execute("""
                SELECT work_date, status FROM compoff_requests
                WHERE user_id=%s AND work_date BETWEEN %s AND %s
            """, (user_id, min(upcoming), max(upcoming)))
            existing = {row['work_date'] for row in cursor.fetchall()}
            valid_dates = [d for d in upcoming if d not in existing]
        else:
            valid_dates = []
        # Recent history (latest 15)
        cursor.execute("""
            SELECT request_id, work_date, status, reason, request_date, review_date
            FROM compoff_requests
            WHERE user_id=%s
            ORDER BY request_date DESC
            LIMIT 15
        """, (user_id,))
        history = cursor.fetchall(); conn.close()
        return render_template('request_compoff.html', username=session['username'], valid_dates=valid_dates, history=history)
    except Exception as e:
        print(f"Request comp-off error: {e}")
        flash('Failed to load comp-off page','error')
        return redirect(url_for('dashboard'))

# ====================== COMP-OFF ROUTES (Admin) ======================

@app.route('/admin/compoff_requests')
@admin_required
def admin_compoff_requests():
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        # Pending list
        cursor.execute("""
            SELECT cr.request_id, cr.user_id, u.name, u.username, cr.work_date, cr.reason, cr.status, cr.request_date
            FROM compoff_requests cr
            JOIN users u ON cr.user_id = u.user_id
            WHERE cr.status='Pending'
            ORDER BY cr.request_date ASC
        """)
        pending = cursor.fetchall()
        # Recent decisions (last 10 approved/rejected)
        cursor.execute("""
            SELECT cr.request_id, u.name, cr.work_date, cr.status, cr.review_date
            FROM compoff_requests cr
            JOIN users u ON cr.user_id = u.user_id
            WHERE cr.status IN ('Approved','Rejected')
            ORDER BY cr.review_date DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()
        # Counts
        cursor.execute("SELECT COUNT(*) AS pending_count FROM compoff_requests WHERE status='Pending'")
        counts = cursor.fetchone() or {'pending_count':0}
        conn.close()
        return render_template('compoff_requests.html', username=session['username'], pending_requests=pending, recent_requests=recent, counts=counts)
    except Exception as e:
        print(f"Admin comp-off list error: {e}")
        flash('Failed to load comp-off requests','error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/review_compoff/<int:request_id>', methods=['POST'])
@admin_required
def review_compoff(request_id):
    decision = request.form.get('decision')  # Approve / Reject
    if decision not in ('Approve','Reject'):
        flash('Invalid decision','error'); return redirect(url_for('admin_compoff_requests'))
    admin_id = session.get('user_id')
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM compoff_requests WHERE request_id=%s", (request_id,))
        req = cursor.fetchone()
        if not req:
            conn.close(); flash('Request not found','error'); return redirect(url_for('admin_compoff_requests'))
        if req['status'] != 'Pending':
            conn.close(); flash('Already reviewed','info'); return redirect(url_for('admin_compoff_requests'))
        cursor2 = conn.cursor()
        if decision == 'Approve':
            cursor2.execute("""
                UPDATE compoff_requests
                SET status='Approved', reviewed_by=%s, review_date=NOW()
                WHERE request_id=%s
            """, (admin_id, request_id))
            flash(f'Comp-off request #{request_id} approved','success')
        else:
            cursor2.execute("""
                UPDATE compoff_requests
                SET status='Rejected', reviewed_by=%s, review_date=NOW()
                WHERE request_id=%s
            """, (admin_id, request_id))
            flash(f'Comp-off request #{request_id} rejected','info')
        conn.commit(); conn.close()
        return redirect(url_for('admin_compoff_requests'))
    except Exception as e:
        print(f"Review comp-off error: {e}")
        flash('Error processing comp-off request','error')
        return redirect(url_for('admin_compoff_requests'))

@app.route('/admin/credit_compoff/<int:attendance_id>', methods=['POST'])
@admin_required
def credit_compoff(attendance_id):
    """Admin credits a worked comp-off day: mark attendance row credited and increment employee balance once."""
    try:
        conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
        # Get attendance record, ensure type comp-off and not credited
        cursor.execute("""
            SELECT a.attendance_id, a.user_id, a.date, a.attendance_type, a.compoff_credited,
                   a.check_in_time, a.check_out_time
            FROM attendance a
            WHERE a.attendance_id=%s
        """, (attendance_id,))
        att = cursor.fetchone()
        if not att:
            conn.close(); flash('Attendance record not found','error'); return redirect(request.referrer or url_for('admin_dashboard'))
        if att['attendance_type'] != 'Comp-Off':
            conn.close(); flash('Not a Comp-Off attendance day','error'); return redirect(request.referrer or url_for('admin_dashboard'))
        if att['compoff_credited']:
            conn.close(); flash('Already credited','info'); return redirect(request.referrer or url_for('admin_dashboard'))
        # Require checkout completed (worked day)
        if not att['check_in_time'] or not att['check_out_time']:
            conn.close(); flash('Incomplete attendance cannot be credited','error'); return redirect(request.referrer or url_for('admin_dashboard'))
        cursor2 = conn.cursor()
        cursor2.execute("UPDATE attendance SET compoff_credited=1 WHERE attendance_id=%s", (attendance_id,))
        cursor2.execute("UPDATE users SET compoff_balance = compoff_balance + 1 WHERE user_id=%s", (att['user_id'],))
        conn.commit(); conn.close(); flash('Comp-off day credited','success')
        return redirect(request.referrer or url_for('admin_dashboard'))
    except Exception as e:
        print(f"Credit comp-off error: {e}")
        flash('Failed to credit comp-off','error')
        return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/compoff_report')
@admin_required
def admin_compoff_report():
    """Admin page showing detailed comp-off report table (history of all requests)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch ALL requests joined with user names
        cursor.execute("""
            SELECT r.*, u.name as employee_name 
            FROM compoff_requests r 
            JOIN users u ON r.user_id = u.user_id 
            ORDER BY r.request_date DESC
        """)
        requests = cursor.fetchall()
        
        report_data = []
        for req in requests:
            # Determine lifecycle status
            lifecycle_status = req['status']
            badge_class = 'secondary'
            
            # Formatting dates
            formatted_work_date = req['work_date'].strftime('%Y-%m-%d')
            formatted_review_date = req['review_date'].strftime('%Y-%m-%d %H:%M') if req['review_date'] else '-'
            
            if req['status'] == 'Pending':
                badge_class = 'warning'
                lifecycle_status = 'Pending Approval'
            elif req['status'] == 'Rejected':
                badge_class = 'danger'
                lifecycle_status = 'Rejected'
            elif req['status'] == 'Approved':
                lifecycle_status = 'Approved (Pending Work)'
                badge_class = 'info'
                
                # Check if work was done for this approved date
                cursor.execute("""
                    SELECT attendance_id, compoff_credited, check_in_time, check_out_time 
                    FROM attendance 
                    WHERE user_id = %s AND date = %s AND attendance_type = 'Comp-Off'
                """, (req['user_id'], req['work_date']))
                att = cursor.fetchone()
                
                if att:
                    if att['compoff_credited']:
                        lifecycle_status = 'Credited to Balance'
                        badge_class = 'success'
                    elif att['check_in_time'] and att['check_out_time']:
                        lifecycle_status = 'Work Done (Pending Credit)'
                        badge_class = 'primary'
                    elif att['check_in_time']:
                        lifecycle_status = 'Work In Progress'
                        badge_class = 'primary'

            report_data.append({
                'id': req['request_id'],
                'employee': req['employee_name'],
                'date': formatted_work_date,
                'reason': req['reason'],
                'status': req['status'],
                'lifecycle_status': lifecycle_status,
                'badge_class': badge_class,
                'reviewed': formatted_review_date
            })
        
        conn.close()
        
        return render_template('compoff_report.html',
                             username=session['username'],
                             report_data=report_data)
                             
    except Exception as e:
        print(f"Comp-off report error: {e}")
        flash('Failed to load comp-off report', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/compoff_history/<user_id>')
@admin_required
def admin_compoff_history(user_id):
    """API endpoint returning JSON history of comp-off days earned by specific employee"""
    user_id = user_id.strip() # Clean input
    print(f"DEBUG: Fetching comp-off history for user_id='{user_id}'")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # We need to show:
        # 1. Approved requests that haven't been worked yet (Incomplete)
        # 2. Worked days (Completed/Credited or Pending Credit)
        
        history = []
        
        # 1. Get ALL requests (Pending, Approved, Rejected)
        cursor.execute("""
            SELECT request_id, work_date, reason, status, review_date, reviewed_by
            FROM compoff_requests 
            WHERE user_id = %s 
            ORDER BY work_date DESC
        """, (user_id,))
        requests = cursor.fetchall()
        print(f"DEBUG: Found {len(requests)} total requests for {user_id}")
        
        for req in requests:
            # Check for attendance ONLY if Approved
            att = None
            if req['status'] == 'Approved':
                cursor.execute("""
                    SELECT attendance_id, check_in_time, check_out_time, compoff_credited, check_in_address, check_out_address
                    FROM attendance
                    WHERE user_id = %s AND date = %s AND attendance_type = 'Comp-Off'
                """, (user_id, req['work_date']))
                att = cursor.fetchone()
            
            entry = {
                'date': req['work_date'].strftime('%Y-%m-%d'),
                'date_formatted': req['work_date'].strftime('%B %d, %Y'),
                'reason': req['reason'] or 'No reason provided',
                'check_in_time': 'N/A',
                'check_out_time': 'N/A',
                'check_in_address': 'N/A',
                'check_out_address': 'N/A',
                'credited': False,
                'request_status': req['status'],
                'status': req['status'], # Default status is the request status
                'badge_class': 'secondary'
            }

            if req['status'] == 'Pending':
                entry['badge_class'] = 'warning'
                entry['status'] = 'Request Pending'
            elif req['status'] == 'Rejected':
                entry['badge_class'] = 'danger'
                entry['status'] = 'Request Rejected'
            elif req['status'] == 'Approved':
                entry['badge_class'] = 'info'
                entry['status'] = 'Approved (Pending Work)'
                
                if att:
                    entry['check_in_time'] = str(att['check_in_time']) if att['check_in_time'] else 'N/A'
                    entry['check_out_time'] = str(att['check_out_time']) if att['check_out_time'] else 'N/A'
                    entry['check_in_address'] = att['check_in_address'] or 'N/A'
                    entry['check_out_address'] = att['check_out_address'] or 'N/A'
                    entry['credited'] = bool(att['compoff_credited'])
                    
                    if att['compoff_credited']:
                        entry['status'] = 'Added to Leave Balance'
                        entry['badge_class'] = 'success'
                    elif att['check_in_time'] and att['check_out_time']:
                       entry['status'] = 'Work Completed (Pending Credit)'
                       entry['badge_class'] = 'primary'
                    elif att['check_in_time']:
                        entry['status'] = 'Work In Progress'
                        entry['badge_class'] = 'primary'
            
            history.append(entry)
            
        conn.close()
        return jsonify(history)
        
    except Exception as e:
        print(f"Comp-off history API error: {e}")
        return jsonify({'error': 'Failed to fetch history'}), 500

# ====================== RUN APPLICATION ======================



@app.route('/admin/debug-database')
@admin_required
def debug_database():
    """Debug route to check database structure"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
        
        # Get users table structure
        cursor.execute("DESCRIBE users")
        users_columns = cursor.fetchall()
        
        # Check if company_settings exists and get structure
        company_settings_columns = []
        if 'company_settings' in tables:
            cursor.execute("DESCRIBE company_settings")
            company_settings_columns = cursor.fetchall()
        
        # Check if site_visits exists and get structure
        site_visits_columns = []
        if 'site_visits' in tables:
            cursor.execute("DESCRIBE site_visits")
            site_visits_columns = cursor.fetchall()
        
        conn.close()
        
        debug_info = f"""
        <h2>Database Structure Debug</h2>
        <h3>Tables: {', '.join(tables)}</h3>
        
        <h3>Users Table Columns:</h3>
        <pre>{users_columns}</pre>
        
        <h3>Company Settings Table Columns:</h3>
        <pre>{company_settings_columns}</pre>
        
        <h3>Site Visits Table Columns:</h3>
        <pre>{site_visits_columns}</pre>
        
        <a href="{url_for('admin_dashboard')}">Back to Dashboard</a>
        """
        
        return debug_info
        
    except Exception as e:
        return f"Debug error: {str(e)}<br><a href='{url_for('admin_dashboard')}'>Back to Dashboard</a>"

@app.route('/admin/cleanup-geofencing')
@admin_required
def cleanup_geofencing():
    """Remove all geofencing features from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        results = []
        
        # Drop tables if they exist
        tables_to_drop = ['site_visits', 'company_settings', 'geofence_requests']
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                conn.commit()
                results.append(f"✅ Dropped table: {table}")
            except Exception as e:
                results.append(f"⚠️ Table {table}: {e}")
        
        # Remove columns from users table
        columns_to_drop = ['geofence_status', 'geofence_lat', 'geofence_lon', 'work_mode', 'remote_address', 'remote_latitude', 'remote_longitude']
        for column in columns_to_drop:
            try:
                cursor.execute(f"ALTER TABLE users DROP COLUMN IF EXISTS {column}")
                conn.commit()
                results.append(f"✅ Removed column: {column}")
            except Exception as e:
                results.append(f"⚠️ Column {column}: {e}")
        
        conn.close()
        
        # Show results to user
        flash('<br>'.join(results), 'success')
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        print(f"Cleanup error: {e}")
        flash(f'Cleanup error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/migrate-database')
@admin_required
def migrate_database():
    """Run database migration for work modes system"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        results = []
        
        # Check if columns exist before adding them
        cursor.execute("SHOW COLUMNS FROM users LIKE 'work_mode'")
        if not cursor.fetchone():
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN work_mode ENUM('Office', 'Remote') DEFAULT 'Office'")
                conn.commit()
                results.append("✅ Added work_mode column to users table")
            except Exception as e:
                results.append(f"⚠️ work_mode column: {e}")

        cursor.execute("SHOW COLUMNS FROM users LIKE 'remote_address'")
        if not cursor.fetchone():
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN remote_address TEXT")
                conn.commit()
                results.append("✅ Added remote_address column to users table")
            except Exception as e:
                results.append(f"⚠️ remote_address column: {e}")

        cursor.execute("SHOW COLUMNS FROM users LIKE 'remote_latitude'")
        if not cursor.fetchone():
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN remote_latitude DECIMAL(10, 8)")
                conn.commit()
                results.append("✅ Added remote_latitude column to users table")
            except Exception as e:
                results.append(f"⚠️ remote_latitude column: {e}")

        cursor.execute("SHOW COLUMNS FROM users LIKE 'remote_longitude'")
        if not cursor.fetchone():
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN remote_longitude DECIMAL(11, 8)")
                conn.commit()
                results.append("✅ Added remote_longitude column to users table")
            except Exception as e:
                results.append(f"⚠️ remote_longitude column: {e}")
        
        # Create company_settings table
        cursor.execute("SHOW TABLES LIKE 'company_settings'")
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    CREATE TABLE company_settings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        setting_key VARCHAR(100) UNIQUE NOT NULL,
                        setting_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                results.append("✅ Created company_settings table")
            except Exception as e:
                results.append(f"⚠️ company_settings table: {e}")
        
        # Create site_visits table
        cursor.execute("SHOW TABLES LIKE 'site_visits'")
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    CREATE TABLE site_visits (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(10) NOT NULL,
                        site_name VARCHAR(255) NOT NULL,
                        site_address TEXT NOT NULL,
                        site_latitude DECIMAL(10, 8) NOT NULL,
                        site_longitude DECIMAL(11, 8) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
                        approved_by VARCHAR(10),
                        approval_date TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                        FOREIGN KEY (approved_by) REFERENCES users(user_id)
                    )
                """)
                conn.commit()
                results.append("✅ Created site_visits table")
            except Exception as e:
                results.append(f"⚠️ site_visits table: {e}")
        
        # Insert default office settings
        try:
            cursor.execute("SELECT COUNT(*) as count FROM company_settings WHERE setting_key = 'office_address'")
            if cursor.fetchone()['count'] == 0:
                cursor.execute("""
                    INSERT INTO company_settings (setting_key, setting_value) 
                    VALUES ('office_address', 'Please set your company office address'),
                           ('office_latitude', '40.7128'), 
                           ('office_longitude', '-74.0060')
                """)
                conn.commit()
                results.append("✅ Inserted default office settings")
        except Exception as e:
            results.append(f"⚠️ Default office settings: {e}")
        
        conn.close()
        
        # Show results to user
        flash('<br>'.join(results), 'success')
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        print(f"Migration error: {e}")
        flash(f'Migration error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    print("🚀 Starting CGS Attendance Management System...")
    print("📊 Admin Panel: Login with admin credentials")
    print("👥 Employee Portal: Login with employee credentials")
    print("🌐 Access: http://localhost:5000")
    
    # Debug mode - set to False for production
    debug_mode = True if os.getenv('FLASK_ENV') == 'development' else False
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)