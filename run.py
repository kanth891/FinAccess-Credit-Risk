import os
from dotenv import load_dotenv
load_dotenv()

import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  FinAccess - Credit Risk Assessment Platform")
    print("=" * 50)
    print("  Starting server at: http://127.0.0.1:5000")
    print("  Admin login: admin@finaccess.com / admin123")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
