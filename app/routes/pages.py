import os
from flask import Blueprint, send_from_directory

pages_bp = Blueprint('pages', __name__)

# Resolve the static/pages directory
PAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'pages')


def serve_page(filename):
    return send_from_directory(PAGES_DIR, filename)


@pages_bp.route('/')
def home():
    return serve_page('home.html')

@pages_bp.route('/login')
def login():
    return serve_page('login.html')

@pages_bp.route('/register')
def register():
    return serve_page('register.html')

@pages_bp.route('/dashboard')
def dashboard():
    return serve_page('dashboard.html')

@pages_bp.route('/apply')
def apply():
    return serve_page('apply.html')

@pages_bp.route('/result')
def result():
    return serve_page('result.html')

@pages_bp.route('/history')
def history():
    return serve_page('history.html')

@pages_bp.route('/admin')
def admin():
    return serve_page('admin.html')
