import os

class Config:
    # Secret key for Flask sessions and JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'finaccess-secret-key-2024-change-in-production')

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'finaccess-jwt-secret-2024-change-in-production')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False          # Set True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = False    # Simplified for student project
    JWT_ACCESS_TOKEN_EXPIRES = False   # Token does not expire (student project)

    # MySQL Configuration
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'finaccess_db')

    MYSQL_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    # Fallback to SQLite if MySQL is unavailable
    SQLITE_URI = 'sqlite:///finaccess.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
