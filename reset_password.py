import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import os

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB')
)
cursor = conn.cursor()
hashed = generate_password_hash('test123')
cursor.execute('UPDATE users SET password = %s WHERE username = %s', (hashed, 'pradeep'))
conn.commit()
cursor.close()
conn.close()
print("Password for pradeep updated to: test123")
