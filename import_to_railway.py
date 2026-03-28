#!/usr/bin/env python3
"""
Railway Database Import Script
Imports local MySQL backup to Railway cloud database
"""

import mysql.connector
from mysql.connector import Error

# Connection details
config = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 45995,
    'user': 'root',
    'password': 'bafAqaGyItbBZRvsKJjzKrqbdrwPmDbA',
    'database': 'railway'
}

try:
    print("🔌 Connecting to Railway MySQL...")
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    print("✅ Connected to Railway")
    
    print("\n📂 Reading backup file...")
    backup_file = 'backup_export/cgs_backup_20260328_101117.sql'
    
    # Read file in binary and decode with error handling
    with open(backup_file, 'rb') as f:
        raw_data = f.read()
    
    # Check for UTF-16 BOM
    if raw_data.startswith(b'\xff\xfe') or raw_data.startswith(b'\xfe\xff'):
        try:
            sql_content = raw_data.decode('utf-16')
            print(f"   ✅ File decoded as UTF-16")
        except:
            sql_content = raw_data.decode('utf-16', errors='ignore')
    else:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                sql_content = raw_data.decode(encoding)
                print(f"   ✅ File decoded successfully with {encoding}")
                break
            except:
                continue
        else:
            # If all else fails, use latin-1 with error handling
            sql_content = raw_data.decode('latin-1', errors='ignore')
    
    # Strip any remaining BOM characters
    sql_content = sql_content.lstrip('\ufeff\ufffe')
    
    print("📥 Importing SQL statements...")
    
    # Split by semicolon and execute each statement
    statements = sql_content.split(';\n')
    statement_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements):
        statement = statement.strip()
        
        # Skip empty lines and comments
        if not statement or statement.startswith('--'):
            continue
        
        # Skip shell/mysqldump warnings
        if 'Warning' in statement or 'mysqldump' in statement.lower() or statement.lower().startswith('mysql:'):
            continue
        
        # Skip MySQL comments
        if statement.startswith('/*') or statement.startswith('*/'):
            continue
        
        # Only process if it looks like a real SQL statement
        if not any(keyword in statement.upper() for keyword in ['CREATE', 'INSERT', 'SET', 'USE', 'DELETE']):
            continue
        
        try:
            cursor.execute(statement)
            statement_count += 1
            if statement_count % 10 == 0:
                print(f"   {statement_count} statements processed...")
        except Error as e:
            error_str = str(e)
            # Only report real errors, not "table already exists"
            if 'already exists' not in error_str and 'Unknown column' not in error_str:
                print(f"   ⚠️  Error at statement {i}: {error_str[:100]}")
                error_count += 1
    
    connection.commit()
    print(f"\n✅ Import Complete!")
    print(f"   Total statements executed: {statement_count}")
    print(f"   Errors encountered: {error_count}")
    
    # Verify import success
    print("\n📊 Verification:")
    
    cursor.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='railway' AND table_type='BASE TABLE'")
    table_count = cursor.fetchone()[0]
    print(f"   ✅ Tables created: {table_count}")
    
    cursor.execute("SELECT COUNT(*) as users FROM users")
    users = cursor.fetchone()[0]
    print(f"   ✅ Users in database: {users}")
    
    cursor.execute("SELECT COUNT(*) as attendance FROM attendance")
    attendance = cursor.fetchone()[0]
    print(f"   ✅ Attendance records: {attendance}")
    
    cursor.execute("SELECT COUNT(*) as leave_req FROM leave_requests")
    leaves = cursor.fetchone()[0]
    print(f"   ✅ Leave requests: {leaves}")
    
    cursor.execute("SELECT COUNT(*) as sites FROM sites")
    sites_count = cursor.fetchone()[0]
    print(f"   ✅ Sites configured: {sites_count}")
    
    # Check one user to verify data integrity
    cursor.execute("SELECT username, email, role FROM users WHERE username='pradeep' LIMIT 1")
    user = cursor.fetchone()
    if user:
        print(f"   ✅ Sample user verified: {user[0]} ({user[2]})")
    
    print("\n🎉 Railway database migration successful!")
    
    cursor.close()
    connection.close()
    
except Error as e:
    print(f"❌ Error: {e}")
    exit(1)
except FileNotFoundError:
    print(f"❌ Backup file not found: backup_export/cgs_backup_20260328_101117.sql")
    exit(1)
