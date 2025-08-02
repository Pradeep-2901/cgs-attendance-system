# app.py

from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import os

# Initialize the Flask app
app = Flask(__name__, static_folder='public')

# --- IMPORTANT: DATABASE CONNECTION ---
# Replace the placeholder values with your actual MySQL credentials.
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root', # <-- PUT YOUR MYSQL PASSWORD HERE
    'database': 'cgs_attendance'           # <-- The database name you created
}

# Function to get a database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# --- API ENDPOINTS ---

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    # Get the JSON data sent from the frontend
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('userType')

    if not all([username, password, user_type]):
        return jsonify({'success': False, 'message': 'Missing credentials.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'Database connection error.'}), 500
    
    cursor = conn.cursor(dictionary=True) # dictionary=True makes results easy to use
    
    sql = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s"
    
    try:
        cursor.execute(sql, (username, password, user_type))
        user = cursor.fetchone() # fetchone() gets the first result

        if user:
            # User found, login successful
            dashboard_url = 'admin-dashboard.html' if user['role'] == 'admin' else 'employee-dashboard.html'
            response_data = {
                'success': True,
                'message': 'Login successful!',
                'user': {'name': user['name'], 'id': user['id']},
                'dashboardUrl': dashboard_url
            }
            return jsonify(response_data)
        else:
            # User not found or credentials incorrect
            return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    except mysql.connector.Error as err:
        print(f"Database query error: {err}")
        return jsonify({'success': False, 'message': 'Server error.'}), 500
    finally:
        cursor.close()
        conn.close()


# --- STATIC FILE SERVING ---
# This serves your index.html and other public files

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)


# --- START SERVER ---
if __name__ == '__main__':
    # The debug=True flag automatically reloads the server when you save changes
    app.run(port=3000, debug=True)

