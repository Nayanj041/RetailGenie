#!/usr/bin/env python3
"""
Simple test script to verify ML models integration
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))


def test_sentiment_analysis():
    """Test sentiment analysis model"""
    try:
        print("Testing Sentiment Analysis...")
        from ml_models.sentiment_analysis.sentiment_model import SentimentAnalyzer

        analyzer = SentimentAnalyzer()
        print("✓ SentimentAnalyzer imported successfully")

        # Train model
        print("Training model...")
        analyzer.train_model()
        print("✓ Model trained successfully")

        # Test prediction
        test_text = "This product is amazing, I love it!"
        result = analyzer.predict_sentiment(test_text)
        print(f"✓ Prediction result: {result}")

        # Test batch analysis
        test_texts = ["Great product!", "Terrible quality", "It's okay"]
        batch_result = analyzer.analyze_feedback_batch(test_texts)
        print(f"✓ Batch analysis result: {batch_result['statistics']}")

        return True

    except Exception as e:
        print(f"✗ Error in sentiment analysis: {e}")
        return False


def test_inventory_forecasting():
    """Test inventory forecasting model"""
    try:
        print("\nTesting Inventory Forecasting...")
        from ml_models.inventory_forecasting.forecast_model import (
            InventoryForecastingModel,
        )

        forecaster = InventoryForecastingModel()
        print("✓ InventoryForecastingModel imported successfully")

        return True

    except Exception as e:
        print(f"✗ Error in inventory forecasting: {e}")
        return False


def test_pricing_engine():
    """Test pricing optimization model"""
    try:
        print("\nTesting Pricing Engine...")
        from ml_models.pricing_engine.pricing_model import DynamicPricingEngine

        pricing_engine = DynamicPricingEngine()
        print("✓ DynamicPricingEngine imported successfully")

        return True

    except Exception as e:
        print(f"✗ Error in pricing engine: {e}")
        return False


def main():
    """Run all ML model tests"""
    print("=== RetailGenie ML Models Integration Test ===\n")

    # Test each model
    sentiment_ok = test_sentiment_analysis()
    inventory_ok = test_inventory_forecasting()
    pricing_ok = test_pricing_engine()

    # Summary
    print("\n=== Test Summary ===")
    print(f"Sentiment Analysis: {'✓ PASS' if sentiment_ok else '✗ FAIL'}")
    print(f"Inventory Forecasting: {'✓ PASS' if inventory_ok else '✗ FAIL'}")
    print(f"Pricing Engine: {'✓ PASS' if pricing_ok else '✗ FAIL'}")

    all_passed = sentiment_ok and inventory_ok and pricing_ok
    print(
        f"\nOverall Status: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}"
    )

    return all_passed


if __name__ == "__main__":
    main()
