#!/usr/bin/env python3
"""
Complete Production WSGI Entry Point
For RetailGenie with full analytics and AI features
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the complete production-ready app
from app_complete import create_complete_app

# Create app instance for WSGI servers (like Gunicorn)
app = create_complete_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
