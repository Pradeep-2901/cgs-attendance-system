#!/usr/bin/env python3
"""
Fix user passwords in Railway database
Reset all users to known test passwords for demo
"""

import mysql.connector
from werkzeug.security import generate_password_hash

# Railway connection
railway_config = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 45995,
    'user': 'root',
    'password': 'bafAqaGyItbBZRvsKJjzKrqbdrwPmDbA',
    'database': 'railway'
}

# Demo passwords for testing
user_passwords = {
    'pradeep': 'test123',
    'sounthar': 'test123',
    'aadhi': 'test123',
    'francis': 'admin123'
}

try:
    print("Connecting to Railway...")
    conn = mysql.connector.connect(**railway_config)
    cursor = conn.cursor()
    
    print("\nResetting passwords for demo users:\n")
    
    for username, password in user_passwords.items():
        # Generate Flask-compatible password hash
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Update in Railway
        cursor.execute(
            "UPDATE users SET password = %s WHERE username = %s",
            (password_hash, username)
        )
        
        rows_affected = cursor.rowcount
        status = "✓ Updated" if rows_affected > 0 else "✗ Not found"
        print(f"  {status}: {username} → {password}")
    
    conn.commit()
    
    print("\n" + "="*80)
    print("Displaying updated users:\n")
    
    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()
    
    for user in users:
        pwd_suggestion = user_passwords.get(user[0], "(password unchanged)")
        print(f"  {user[0]:<20} {user[1]:<15} {pwd_suggestion}")
    
    print("\n" + "="*80)
    print("Ready for testing!")
    print("="*80 + "\n")
    
    print("TEST THESE CREDENTIALS ON RENDER:")
    print("-"*80)
    for username, password in user_passwords.items():
        print(f"  Username: {username:<20} Password: {password}")
    print("-"*80 + "\n")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
