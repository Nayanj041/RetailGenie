#!/usr/bin/env python3
"""
Simple Flask test to diagnose the issue
"""

import sys
import os

print("🧪 Simple Flask Test")
print("=" * 20)

try:
    print("1. Testing basic Python...")
    print(f"   Python version: {sys.version}")
    print(f"   Working directory: {os.getcwd()}")
    
    print("2. Testing Flask import...")
    from flask import Flask
    print("   ✅ Flask imported successfully")
    
    print("3. Creating Flask app...")
    app = Flask(__name__)
    print("   ✅ Flask app created")
    
    @app.route('/test')
    def test():
        return {"message": "Simple test working", "status": "success"}
    
    print("4. Starting server...")
    print("   🌐 Server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
