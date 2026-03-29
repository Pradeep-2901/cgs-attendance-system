import os
from dotenv import load_dotenv

load_dotenv()
print('=== MySQL Configuration ===')
print(f'MYSQL_HOST: {os.getenv("MYSQL_HOST", "localhost")}')
print(f'MYSQL_PORT: {os.getenv("MYSQL_PORT", "3306")}')
print(f'MYSQL_USER: {os.getenv("MYSQL_USER", "root")}')
print(f'MYSQL_DB: {os.getenv("MYSQL_DB", "cgs")}')
print(f'FLASK_SECRET_KEY: {os.getenv("FLASK_SECRET_KEY", "not set")}')
