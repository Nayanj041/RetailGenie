"""
Inventory Forecasting Model
AI-powered demand prediction and inventory optimization
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class InventoryForecastingModel:
    """
    Advanced inventory forecasting model using machine learning
    to predict demand and optimize stock levels
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_path = os.path.join(os.path.dirname(__file__), 'inventory_model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'inventory_scaler.pkl')
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for inventory forecasting
        
        Args:
            data: DataFrame with sales/inventory data
            
        Returns:
            DataFrame with engineered features
        """
        features = data.copy()
        
        # Time-based features
        if 'date' in features.columns:
            features['date'] = pd.to_datetime(features['date'])
            features['day_of_week'] = features['date'].dt.dayofweek
            features['month'] = features['date'].dt.month
            features['quarter'] = features['date'].dt.quarter
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Sales history features
        if 'sales_quantity' in features.columns:
            # Rolling averages
            features['sales_7day_avg'] = features['sales_quantity'].rolling(window=7, min_periods=1).mean()
            features['sales_30day_avg'] = features['sales_quantity'].rolling(window=30, min_periods=1).mean()
            
            # Trend indicators
            features['sales_trend'] = features['sales_quantity'].pct_change(periods=7)
            features['sales_volatility'] = features['sales_quantity'].rolling(window=7).std()
        
        # Price-related features
        if 'price' in features.columns:
            features['price_change'] = features['price'].pct_change()
            features['price_elasticity'] = features.get('sales_quantity', 0) / features['price']
        
        # Inventory features
        if 'current_stock' in features.columns:
            features['stock_level'] = features['current_stock']
            features['days_of_inventory'] = features['current_stock'] / (features.get('sales_7day_avg', 1) + 1)
        
        # Category and seasonal features
        if 'category' in features.columns:
            category_dummies = pd.get_dummies(features['category'], prefix='category')
            features = pd.concat([features, category_dummies], axis=1)
        
        # External factors (mock data for demo)
        features['economic_index'] = np.random.normal(100, 10, len(features))
        features['competitor_activity'] = np.random.uniform(0, 1, len(features))
        
        # Fill missing values
        features = features.fillna(0)
        
        return features
    
    def train(self, training_data: pd.DataFrame, target_column: str = 'future_demand') -> Dict:
        """
        Train the inventory forecasting model
        
        Args:
            training_data: DataFrame with historical data
            target_column: Name of the target variable
            
        Returns:
            Training metrics
        """
        try:
            # Prepare features
            features_df = self.prepare_features(training_data)
            
            # Remove non-numeric columns and target
            numeric_columns = features_df.select_dtypes(include=[np.number]).columns
            feature_columns = [col for col in numeric_columns if col != target_column]
            
            X = features_df[feature_columns]
            y = features_df[target_column]
            
            # Store feature names
            self.feature_names = feature_columns
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Calculate training metrics
            y_pred = self.model.predict(X_scaled)
            mae = mean_absolute_error(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            
            # Save model
            self.save_model()
            
            logger.info(f"Inventory forecasting model trained successfully")
            
            return {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2_score': self.model.score(X_scaled, y),
                'feature_importance': dict(zip(feature_columns, self.model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Error training inventory model: {str(e)}")
            raise
    
    def predict_demand(self, product_data: Dict, forecast_days: int = 30) -> Dict:
        """
        Predict future demand for a product
        
        Args:
            product_data: Product information and historical data
            forecast_days: Number of days to forecast
            
        Returns:
            Demand prediction results
        """
        try:
            if not self.is_trained:
                self.load_model()
            
            # Create forecast DataFrame
            forecast_dates = pd.date_range(
                start=datetime.now(),
                periods=forecast_days,
                freq='D'
            )
            
            predictions = []
            confidence_intervals = []
            
            for date in forecast_dates:
                # Prepare input features
                input_data = pd.DataFrame([{
                    'date': date,
                    'sales_quantity': product_data.get('avg_daily_sales', 10),
                    'price': product_data.get('price', 100),
                    'current_stock': product_data.get('current_stock', 50),
                    'category': product_data.get('category', 'general')
                }])
                
                # Prepare features
                features_df = self.prepare_features(input_data)
                
                # Select feature columns
                X = features_df[self.feature_names]
                X_scaled = self.scaler.transform(X)
                
                # Make prediction
                prediction = self.model.predict(X_scaled)[0]
                predictions.append(max(0, prediction))  # Ensure non-negative
                
                # Calculate confidence interval (simplified)
                std_error = np.std([tree.predict(X_scaled)[0] for tree in self.model.estimators_])
                confidence_intervals.append({
                    'lower': max(0, prediction - 1.96 * std_error),
                    'upper': prediction + 1.96 * std_error
                })
            
            # Calculate additional metrics
            total_predicted_demand = sum(predictions)
            avg_daily_demand = np.mean(predictions)
            peak_demand = max(predictions)
            
            return {
                'product_id': product_data.get('product_id'),
                'forecast_period': forecast_days,
                'predictions': predictions,
                'confidence_intervals': confidence_intervals,
                'total_predicted_demand': total_predicted_demand,
                'avg_daily_demand': avg_daily_demand,
                'peak_demand': peak_demand,
                'recommended_stock_level': total_predicted_demand * 1.2,  # 20% buffer
                'reorder_point': avg_daily_demand * 7,  # 7-day buffer
                'trend': self._analyze_trend(predictions)
            }
            
        except Exception as e:
            logger.error(f"Error predicting demand: {str(e)}")
            raise
    
    def optimize_inventory(self, products: List[Dict]) -> Dict:
        """
        Optimize inventory levels for multiple products
        
        Args:
            products: List of product data dictionaries
            
        Returns:
            Optimization recommendations
        """
        recommendations = []
        
        for product in products:
            demand_forecast = self.predict_demand(product)
            
            current_stock = product.get('current_stock', 0)
            recommended_stock = demand_forecast['recommended_stock_level']
            
            recommendation = {
                'product_id': product.get('product_id'),
                'product_name': product.get('name', 'Unknown'),
                'current_stock': current_stock,
                'recommended_stock': recommended_stock,
                'predicted_demand': demand_forecast['total_predicted_demand'],
                'action': self._get_action_recommendation(current_stock, recommended_stock),
                'priority': self._calculate_priority(product, demand_forecast),
                'estimated_cost': self._estimate_cost(product, recommended_stock - current_stock)
            }
            
            recommendations.append(recommendation)
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return {
            'recommendations': recommendations,
            'total_investment_needed': sum(r['estimated_cost'] for r in recommendations if r['estimated_cost'] > 0),
            'high_priority_items': [r for r in recommendations if r['priority'] > 0.8],
            'summary': self._generate_summary(recommendations)
        }
    
    def _analyze_trend(self, predictions: List[float]) -> str:
        """Analyze demand trend from predictions"""
        if len(predictions) < 2:
            return 'stable'
        
        first_half = np.mean(predictions[:len(predictions)//2])
        second_half = np.mean(predictions[len(predictions)//2:])
        
        change = (second_half - first_half) / first_half
        
        if change > 0.1:
            return 'increasing'
        elif change < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_action_recommendation(self, current_stock: float, recommended_stock: float) -> str:
        """Get action recommendation based on stock levels"""
        ratio = current_stock / (recommended_stock + 1)
        
        if ratio < 0.5:
            return 'urgent_restock'
        elif ratio < 0.8:
            return 'restock_soon'
        elif ratio > 1.5:
            return 'reduce_stock'
        else:
            return 'maintain'
    
    def _calculate_priority(self, product: Dict, demand_forecast: Dict) -> float:
        """Calculate priority score for inventory action"""
        # Base priority on stock ratio and demand trend
        current_stock = product.get('current_stock', 0)
        predicted_demand = demand_forecast['total_predicted_demand']
        
        if predicted_demand == 0:
            return 0.1
        
        stock_ratio = current_stock / predicted_demand
        
        # Lower stock ratio = higher priority
        priority = 1 / (stock_ratio + 0.1)
        
        # Adjust for trend
        trend = demand_forecast['trend']
        if trend == 'increasing':
            priority *= 1.2
        elif trend == 'decreasing':
            priority *= 0.8
        
        return min(priority, 1.0)
    
    def _estimate_cost(self, product: Dict, quantity_needed: float) -> float:
        """Estimate cost for restocking"""
        if quantity_needed <= 0:
            return 0
        
        unit_cost = product.get('cost', product.get('price', 0) * 0.6)
        return quantity_needed * unit_cost
    
    def _generate_summary(self, recommendations: List[Dict]) -> Dict:
        """Generate summary of recommendations"""
        total_products = len(recommendations)
        urgent_items = len([r for r in recommendations if r['action'] == 'urgent_restock'])
        restock_items = len([r for r in recommendations if r['action'] in ['urgent_restock', 'restock_soon']])
        
        return {
            'total_products_analyzed': total_products,
            'urgent_restock_needed': urgent_items,
            'total_restock_needed': restock_items,
            'percentage_needing_action': (restock_items / total_products * 100) if total_products > 0 else 0
        }
    
    def save_model(self):
        """Save the trained model and scaler"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Inventory forecasting model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def load_model(self):
        """Load a previously trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                logger.info("Inventory forecasting model loaded successfully")
            else:
                logger.warning("No saved model found, using default model")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")

# Utility functions for integration
def get_inventory_predictions(products_data: List[Dict]) -> Dict:
    """
    Convenience function to get inventory predictions
    """
    model = InventoryForecastingModel()
    return model.optimize_inventory(products_data)

def predict_single_product_demand(product_data: Dict, forecast_days: int = 30) -> Dict:
    """
    Convenience function to predict demand for a single product
    """
    model = InventoryForecastingModel()
    return model.predict_demand(product_data, forecast_days)
