#!/usr/bin/env python3
"""
Simple Flask server to test ML endpoints
"""

import sys
import os
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

def create_success_response(data):
    """Create success response"""
    return jsonify({"success": True, "data": data})

def create_error_response(message, status_code, path):
    """Create error response"""
    return jsonify({
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "path": path
        }
    })

@app.route("/api/v1/ml/sentiment/analysis", methods=["GET"])
def get_sentiment_analysis():
    """Get sentiment analysis of customer feedback"""
    try:
        # Import ML model
        from ml_models.sentiment_analysis.sentiment_model import SentimentAnalyzer
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        
        # Train model (in production, load pre-trained model)
        analyzer.train_model()
        
        # Mock feedback data for testing
        feedback_texts = [
            "This product is amazing, I love it!",
            "Great quality and fast delivery",
            "Not as described, very disappointed",
            "It's okay, nothing special",
            "Excellent customer service"
        ]
        
        # Analyze batch of feedback
        batch_results = analyzer.analyze_feedback_batch(feedback_texts)
        
        # Format response
        analysis_data = {
            "analysis": {
                "overall_sentiment": batch_results['statistics']['overall_sentiment'],
                "sentiment_distribution": {
                    "positive": batch_results['statistics']['positive_count'],
                    "neutral": batch_results['statistics']['neutral_count'],
                    "negative": batch_results['statistics']['negative_count']
                },
                "trending_topics": [
                    {"topic": "product quality", "sentiment": "positive", "mentions": batch_results['statistics']['positive_count']},
                    {"topic": "customer service", "sentiment": "neutral", "mentions": batch_results['statistics']['neutral_count']},
                    {"topic": "delivery", "sentiment": "negative", "mentions": batch_results['statistics']['negative_count']}
                ],
                "confidence": batch_results['statistics']['average_confidence']
            },
            "total_feedback": batch_results['statistics']['total_feedback'],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return create_success_response(analysis_data)
        
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return create_error_response("Failed to analyze sentiment", 500, request.path), 500

@app.route("/api/v1/ml/inventory/forecast", methods=["GET"])
def get_inventory_forecast():
    """Get inventory demand forecasting"""
    try:
        # Mock inventory data and predictions
        predictions = {
            "1": {"predicted_demand": 15, "trend": "up", "confidence": 0.85, "current_stock": 45, "recommended_reorder": False},
            "2": {"predicted_demand": 25, "trend": "down", "confidence": 0.72, "current_stock": 8, "recommended_reorder": True},
            "3": {"predicted_demand": 8, "trend": "stable", "confidence": 0.91, "current_stock": 120, "recommended_reorder": False}
        }
        
        return create_success_response({
            "predictions": predictions,
            "generated_at": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        print(f"Error in inventory forecasting: {str(e)}")
        return create_error_response("Failed to generate inventory forecast", 500, request.path), 500

@app.route("/api/v1/analytics", methods=["GET"])
def get_analytics():
    """Get analytics data"""
    try:
        time_range = request.args.get("time_range", "week")
        
        # Mock analytics data
        analytics_data = {
            "overview": {
                "total_revenue": 125340.50,
                "revenue_change": 12.5,
                "total_orders": 1234,
                "orders_change": 8.3,
                "total_customers": 856,
                "customers_change": 15.2,
                "conversion_rate": 3.4,
                "conversion_change": -2.1
            },
            "sales_trend": [
                {"date": "2024-07-01", "revenue": 12000, "orders": 120},
                {"date": "2024-07-02", "revenue": 15000, "orders": 145},
                {"date": "2024-07-03", "revenue": 18000, "orders": 160},
                {"date": "2024-07-04", "revenue": 14000, "orders": 135},
                {"date": "2024-07-05", "revenue": 22000, "orders": 180}
            ],
            "top_products": [
                {"name": "Smart Headphones", "sales": 450, "revenue": 89910},
                {"name": "Cotton T-Shirt", "sales": 320, "revenue": 9597},
                {"name": "Programming Book", "sales": 180, "revenue": 8998},
                {"name": "Running Shoes", "sales": 150, "revenue": 14985},
                {"name": "Coffee Mug", "sales": 280, "revenue": 4200}
            ],
            "category_distribution": [
                {"name": "Electronics", "value": 45, "revenue": 67500},
                {"name": "Clothing", "value": 30, "revenue": 22500},
                {"name": "Books", "value": 15, "revenue": 11250},
                {"name": "Home & Garden", "value": 10, "revenue": 7500}
            ],
            "customer_segments": [
                {"segment": "Premium", "customers": 150, "avg_order_value": 285},
                {"segment": "Regular", "customers": 400, "avg_order_value": 125},
                {"segment": "New", "customers": 306, "avg_order_value": 85}
            ],
            "time_range": time_range,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        return create_success_response(analytics_data)

    except Exception as e:
        print(f"Error getting analytics: {str(e)}")
        return create_error_response("Failed to get analytics", 500, request.path), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()})

if __name__ == "__main__":
    print("Starting ML Test Server...")
    print("Available endpoints:")
    print("- GET /api/v1/ml/sentiment/analysis")
    print("- GET /api/v1/ml/inventory/forecast") 
    print("- GET /api/v1/analytics")
    print("- GET /health")
    
    app.run(debug=True, host="0.0.0.0", port=5001)
