from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import pymysql
import os
import sys

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

    # Load configuration
    from config import Config
    app.config.from_object(Config)

    # JWT via Authorization header (no cookies)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    # Use MySQL
    db_uri = _get_database_uri(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pages_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        _seed_admin()

    # Auto-train ML model if not found
    _ensure_model_ready()

    return app


def _get_database_uri(Config):
    """Connect to MySQL."""
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=int(Config.MYSQL_PORT),
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            connect_timeout=3
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}`")
        conn.commit()
        conn.close()
        print(f"[DB] Connected to MySQL. Using database: {Config.MYSQL_DB}")
        return Config.MYSQL_URI
    except Exception as e:
        print(f"[DB] MySQL unavailable ({e}). Please check your MySQL configuration and ensure the server is running.")
        raise


def _seed_admin():
    """Create default admin user if not exists."""
    from app.models.models import User
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(email='admin@finaccess.com').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@finaccess.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("[DB] Default admin created: admin@finaccess.com / admin123")


def _ensure_model_ready():
    """Auto-train ML model if model.pkl is missing."""
    ml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml')
    model_path = os.path.join(ml_dir, 'model.pkl')
    if not os.path.exists(model_path):
        print("[ML] model.pkl not found. Auto-training...")
        try:
            from ml.train_model import train_model
            train_model()
        except Exception as e:
            print(f"[ML] Training failed: {e}")
