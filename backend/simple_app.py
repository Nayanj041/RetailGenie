#!/usr/bin/env python3
"""
Super Simple Flask App for Testing
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# CORS configuration
CORS(app, origins=['http://localhost:3000'], 
     supports_credentials=True, 
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

@app.route("/", methods=["GET"])
def root():
    """
    Handle GET requests to the root endpoint and return a JSON response indicating the API is running.
    
    Returns:
        Response: A Flask JSON response with a message and status.
    """
    return jsonify({
        "message": "Simple Test API",
        "status": "running"
    })

@app.route("/api/v1/health", methods=["GET"])
def health():
    """
    Handle GET requests to the health check endpoint and return a JSON response indicating the API is healthy.
    
    Returns:
        Response: A Flask JSON response with health status and a message.
    """
    return jsonify({
        "status": "healthy",
        "message": "Simple API is running"
    })

@app.route("/api/v1/test", methods=["POST"])
def test_post():
    """
    Handle POST requests to the test endpoint by parsing JSON data from the request body and returning a confirmation response.
    
    Returns:
        Response: A JSON object indicating success and echoing the received data, or an error message with HTTP status 500 if parsing fails.
    """
    try:
        data = request.get_json()
        return jsonify({
            "success": True,
            "received": data,
            "message": "POST request successful"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 Starting Simple Test API...")
    print("🌐 Running on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
