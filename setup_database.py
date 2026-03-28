import mysql.connector
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
DB_NAME = os.getenv('MYSQL_DB', 'cgs')

def get_db_connection(database=None):
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database
    )

def test_mysql_connection():
    """Test if we can connect to MySQL server"""
    try:
        print("🔍 Testing MySQL connection...")
        
        # First test basic MySQL connection (without database)
        connection = get_db_connection()
        
        print("✅ MySQL server connection successful!")
        
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"✅ Database '{DB_NAME}' already exists")
        else:
            print(f"❌ Database '{DB_NAME}' does not exist")
            
        connection.close()
        return True, db_exists is not None
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection failed: {e}")
        return False, False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, False

def create_database_and_tables():
    """Create the CGS database and required tables"""
    try:
        print("\n🏗️  Creating database and tables...")
        
        # Connect to MySQL server
        connection = get_db_connection()
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ Database '{DB_NAME}' created/verified")
        
        # Use the database
        cursor.execute(f"USE {DB_NAME}")
        
        # Create users table
        users_table = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(10) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(100),
            role ENUM('admin', 'employee') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cursor.execute(users_table)
        print("✅ Users table created/verified")
        
        # Create attendance table
        attendance_table = '''
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(10),
            date DATE NOT NULL,
            check_in_time TIME,
            check_out_time TIME,
            check_in_address TEXT,
            check_out_address TEXT,
            check_in_photo VARCHAR(255),
            check_out_photo VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        '''
        cursor.execute(attendance_table)
        print("✅ Attendance table created/verified")
        
        connection.commit()
        connection.close()
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Database setup failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_admin_user():
    """Create a default admin user"""
    try:
        print("\n👤 Creating admin user...")
        
        # Connect to the CGS database
        connection = get_db_connection(database=DB_NAME)
        
        cursor = connection.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin' OR role = 'admin'")
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print("ℹ️  Admin user already exists")
            cursor.execute("SELECT username, name, role FROM users WHERE role = 'admin'")
            admins = cursor.fetchall()
            print("📋 Existing admin accounts:")
            for admin in admins:
                print(f"   Username: {admin[0]}, Name: {admin[1]}, Role: {admin[2]}")
        else:
            # Create admin user
            hashed_password = generate_password_hash('admin123')
            admin_data = (
                'ADM001',       # user_id
                'admin',        # username
                hashed_password, # password (hashed)
                'System Administrator',  # name
                'admin'         # role
            )
            
            cursor.execute("""
                INSERT INTO users (user_id, username, password, name, role) 
                VALUES (%s, %s, %s, %s, %s)
            """, admin_data)
            
            print("✅ Admin user created successfully!")
            print("📋 Admin Credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  IMPORTANT: Change this password in production!")
            
        # Create a test employee user too
        cursor.execute("SELECT * FROM users WHERE username = 'employee1'")
        existing_emp = cursor.fetchone()
        
        if not existing_emp:
            hashed_emp_password = generate_password_hash('emp123')
            emp_data = (
                'EMP001',       # user_id
                'employee1',    # username
                hashed_emp_password, # password (hashed)
                'John Doe',     # name
                'employee'      # role
            )
            
            cursor.execute("""
                INSERT INTO users (user_id, username, password, name, role) 
                VALUES (%s, %s, %s, %s, %s)
            """, emp_data)
            
            print("✅ Test employee user created!")
            print("📋 Employee Credentials:")
            print("   Username: employee1")
            print("   Password: emp123")
        
        connection.commit()
        connection.close()
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ User creation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_setup():
    """Verify the complete setup"""
    try:
        print("\n🔍 Verifying setup...")
        
        connection = get_db_connection(database=DB_NAME)
        
        cursor = connection.cursor()
        
        # Count tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables: {[table[0] for table in tables]}")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 Total users in database: {user_count}")
        
        # Show user breakdown
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        role_counts = cursor.fetchall()
        for role, count in role_counts:
            print(f"   {role.title()}s: {count}")
        
        connection.close()
        
        print("\n🎉 Setup verification complete!")
        print("\n🚀 You can now run your Flask app with: python app.py")
        print("📱 Try logging in with:")
        print("   Admin: username='admin', password='admin123'")
        print("   Employee: username='employee1', password='emp123'")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 CGS Attendance System - Database Setup")
    print("=" * 50)
    
    # Step 1: Test MySQL connection
    mysql_connected, db_exists = test_mysql_connection()
    
    if not mysql_connected:
        print("\n❌ Cannot proceed without MySQL connection.")
        print("💡 Make sure MySQL is installed and running.")
        print("💡 Check your credentials in the script (host, user, password).")
        sys.exit(1)
    
    # Step 2: Create database and tables
    if create_database_and_tables():
        print("✅ Database setup completed")
    else:
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Step 3: Create admin user
    if create_admin_user():
        print("✅ User setup completed")
    else:
        print("❌ User setup failed")
        sys.exit(1)
    
    # Step 4: Verify everything
    verify_setup()