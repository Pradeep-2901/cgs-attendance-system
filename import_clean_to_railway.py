#!/usr/bin/env python3
"""
Clean Railway Database Import
Drops existing railway db and re-imports completely fresh
"""

import mysql.connector
from mysql.connector import Error

# Connection details
config = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 45995,
    'user': 'root',
    'password': 'bafAqaGyItbBZRvsKJjzKrqbdrwPmDbA'
}

try:
    print("🔌 Connecting to Railway MySQL (root level)...")
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    print("✅ Connected\n")
    
    # Drop and recreate database
    print("🗑️  Dropping old database...")
    cursor.execute("DROP DATABASE IF EXISTS railway")
    connection.commit()
    print("✅ Done\n")
    
    print("🏗️  Creating fresh database...")
    cursor.execute("CREATE DATABASE railway CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    connection.commit()
    print("✅ Done\n")
    
    # Switch to new database
    cursor.execute("USE railway")
    
    # Disable foreign key checks during import
    print("⚙️  Disabling foreign key checks...")
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    connection.commit()
    print("✅ Done\n")
    
    # Read backup file
    print("📂 Reading backup file...")
    with open('backup_export/cgs_clean_backup.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    print(f"   Size: {len(sql_content):,} characters\n")
    
    # Execute the SQL file line by line, building statements
    print("📥 Importing database...")
    statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('--') or line.startswith('/*!'):
            continue
        
        # Add to current statement
        current_statement += " " + line
        
        # If line ends with semicolon, execute the statement
        if line.endswith(';'):
            stmt = current_statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    statements.append(stmt[:50] + "..." if len(stmt) > 50 else stmt)
                except Error as e:
                    if 'already exists' not in str(e):
                        print(f"Warning: {e}")
            current_statement = ""
    
    connection.commit()
    print(f"✅ Import completed ({len(statements)} statements executed)\n")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    connection.commit()
    
    # Verification
    print("📊 Verification:")
    cursor.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='railway' AND table_type='BASE TABLE'")
    table_count = cursor.fetchone()[0]
    print(f"   ✅ Tables created: {table_count}")
    
    cursor.execute("SELECT COUNT(*) as users FROM users")
    users = cursor.fetchone()[0]
    print(f"   ✅ Users: {users}")
    
    cursor.execute("SELECT COUNT(*) as attendance FROM attendance")
    attendance = cursor.fetchone()[0]
    print(f"   ✅ Attendance records: {attendance}")
    
    cursor.execute("SELECT COUNT(*) as holidays FROM holidays")
    holidays = cursor.fetchone()[0]
    print(f"   ✅ Holidays: {holidays}")
    
    cursor.execute("SELECT COUNT(*) as company_settings FROM company_settings")
    company = cursor.fetchone()[0]
    print(f"   ✅ Company settings: {company}")
    
    cursor.execute("SELECT username, role FROM users WHERE username='pradeep'")
    user = cursor.fetchone()
    if user:
        print(f"   ✅ Sample user: {user[0]} ({user[1]})")
    
    print(f"\n🎉 Railway database migration successful!")
    
    cursor.close()
    connection.close()
    
except Error as e:
    print(f"❌ Error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)
