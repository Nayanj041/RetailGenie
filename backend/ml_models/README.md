# RetailGenie ML Models

This directory contains all machine learning models for the RetailGenie system.

## Structure

### 1. Sentiment Analysis (`sentiment_analysis/`)
- **Purpose**: Analyze customer feedback sentiment
- **Model**: NLTK + Scikit-learn Naive Bayes
- **Input**: Customer reviews and feedback text
- **Output**: Sentiment score (positive/negative/neutral) + confidence

### 2. Inventory Forecasting (`inventory_forecasting/`)
- **Purpose**: Predict demand and optimize inventory levels
- **Model**: LSTM + ARIMA time series models
- **Input**: Historical sales data, seasonal patterns
- **Output**: Demand predictions, reorder recommendations

### 3. Pricing Engine (`pricing_engine/`)
- **Purpose**: Dynamic pricing optimization
- **Model**: Custom algorithm with competitor analysis
- **Input**: Product demand, competitor prices, market trends
- **Output**: Optimal pricing recommendations

## Integration

All models are integrated into the Flask backend through controller classes:
- `app/controllers/ai_assistant_controller.py`
- `app/controllers/analytics_controller.py`
- `app/controllers/pricing_controller.py`

## Dependencies

```bash
pip install -r ml_requirements.txt
```

## Usage

Models are automatically loaded when the backend starts and can be accessed through REST API endpoints.
