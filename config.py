import os

class Config:
    # Secret key for Flask sessions and JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'finaccess-secret-key-2026-change-in-production')

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'finaccess-jwt-secret-2026-change-in-production')
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

    _raw_uri = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost:3306/finaccess_db')
    
    # Automatically convert Aiven's mysql:// to SQLAlchemy's expected mysql+pymysql://
    if _raw_uri.startswith('mysql://'):
        MYSQL_URI = _raw_uri.replace('mysql://', 'mysql+pymysql://', 1)
    else:
        MYSQL_URI = _raw_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
