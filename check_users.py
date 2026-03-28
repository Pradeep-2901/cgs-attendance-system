import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB')
)
cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT user_id, username, name, role FROM users')
print("\n=== Users in Database ===")
for row in cursor:
    print(f"ID: {row['user_id']} | Username: {row['username']} | Name: {row['name']} | Role: {row['role']}")
conn.close()
