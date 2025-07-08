#!/usr/bin/env python3
"""
Super Simple Flask App for Testing
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# CORS configuration
CORS(
    app,
    origins=["http://localhost:3000"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)


@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Simple Test API", "status": "running"})


@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "message": "Simple API is running"})


@app.route("/api/v1/test", methods=["POST"])
def test_post():
    try:
        data = request.get_json()
        return jsonify(
            {"success": True, "received": data, "message": "POST request successful"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Starting Simple Test API...")
    print("🌐 Running on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
