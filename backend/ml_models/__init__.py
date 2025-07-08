"""
ML Models Package Initialization
"""

from .sentiment_analysis.sentiment_model import SentimentAnalyzer

try:
    from .inventory_forecasting.forecast_model import InventoryForecastingModel
except ImportError:
    InventoryForecastingModel = None

try:
    from .pricing_engine.pricing_model import DynamicPricingEngine
except ImportError:
    DynamicPricingEngine = None

__version__ = "1.0.0"
__author__ = "RetailGenie AI Team"

# Export main classes and utility functions
__all__ = ["SentimentAnalyzer", "InventoryForecastingModel", "DynamicPricingEngine"]
