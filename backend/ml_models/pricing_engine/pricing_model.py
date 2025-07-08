"""
Dynamic Pricing Engine
AI-powered pricing optimization for retail products
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class DynamicPricingEngine:
    """
    Advanced pricing engine using machine learning to optimize prices
    based on demand, competition, and market conditions
    """
    
    def __init__(self):
        self.demand_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.profit_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_path = os.path.join(os.path.dirname(__file__), 'pricing_model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'pricing_scaler.pkl')
    
    def prepare_pricing_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for pricing optimization
        
        Args:
            data: DataFrame with product and market data
            
        Returns:
            DataFrame with engineered features
        """
        features = data.copy()
        
        # Price-related features
        if 'price' in features.columns:
            features['price_log'] = np.log(features['price'] + 1)
            features['price_normalized'] = features['price'] / features['price'].max()
        
        # Cost and margin features
        if 'cost' in features.columns and 'price' in features.columns:
            features['margin'] = features['price'] - features['cost']
            features['margin_percentage'] = (features['margin'] / features['price']) * 100
            features['markup'] = features['price'] / (features['cost'] + 1)
        
        # Demand features
        if 'sales_quantity' in features.columns:
            features['demand_elasticity'] = self._calculate_price_elasticity(features)
            features['sales_velocity'] = features['sales_quantity'] / features.get('inventory_level', 1)
        
        # Competition features
        if 'competitor_price' in features.columns:
            features['price_vs_competition'] = features['price'] / (features['competitor_price'] + 1)
            features['competitive_advantage'] = features['competitor_price'] - features['price']
        
        # Market features
        features['market_demand_index'] = np.random.normal(1.0, 0.2, len(features))
        features['seasonal_factor'] = self._calculate_seasonal_factor(features)
        
        # Product category features
        if 'category' in features.columns:
            category_dummies = pd.get_dummies(features['category'], prefix='category')
            features = pd.concat([features, category_dummies], axis=1)
        
        # Customer segmentation features
        features['premium_customer_ratio'] = np.random.uniform(0.1, 0.4, len(features))
        features['price_sensitive_ratio'] = 1 - features['premium_customer_ratio']
        
        # Inventory features
        if 'inventory_level' in features.columns:
            features['inventory_turnover'] = features.get('sales_quantity', 0) / (features['inventory_level'] + 1)
            features['stock_out_risk'] = np.where(features['inventory_level'] < 10, 1, 0)
        
        # Time-based features
        if 'date' in features.columns:
            features['date'] = pd.to_datetime(features['date'])
            features['day_of_week'] = features['date'].dt.dayofweek
            features['month'] = features['date'].dt.month
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
            features['is_holiday'] = np.random.binomial(1, 0.1, len(features))  # Mock holiday data
        
        # Fill missing values
        features = features.fillna(0)
        
        return features
    
    def _calculate_price_elasticity(self, data: pd.DataFrame) -> pd.Series:
        """Calculate price elasticity of demand"""
        if 'price' not in data.columns or 'sales_quantity' not in data.columns:
            return pd.Series(np.zeros(len(data)))
        
        # Simple elasticity calculation
        price_change = data['price'].pct_change()
        demand_change = data['sales_quantity'].pct_change()
        
        elasticity = demand_change / (price_change + 1e-8)
        return elasticity.fillna(0)
    
    def _calculate_seasonal_factor(self, data: pd.DataFrame) -> pd.Series:
        """Calculate seasonal demand factor"""
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            month = data['date'].dt.month
            # Simple seasonal pattern (higher in winter months)
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * (month - 1) / 12)
        else:
            seasonal_factor = pd.Series(np.ones(len(data)))
        
        return seasonal_factor
    
    def train(self, training_data: pd.DataFrame) -> Dict:
        """
        Train the pricing optimization models
        
        Args:
            training_data: DataFrame with historical pricing and sales data
            
        Returns:
            Training metrics
        """
        try:
            # Prepare features
            features_df = self.prepare_pricing_features(training_data)
            
            # Select numeric features
            numeric_columns = features_df.select_dtypes(include=[np.number]).columns
            feature_columns = [col for col in numeric_columns if col not in ['sales_quantity', 'profit']]
            
            X = features_df[feature_columns]
            y_demand = features_df.get('sales_quantity', np.random.randint(1, 100, len(features_df)))
            y_profit = features_df.get('profit', np.random.uniform(10, 1000, len(features_df)))
            
            # Store feature names
            self.feature_names = feature_columns
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train models
            self.demand_model.fit(X_scaled, y_demand)
            self.profit_model.fit(X_scaled, y_profit)
            self.is_trained = True
            
            # Calculate training metrics
            demand_pred = self.demand_model.predict(X_scaled)
            profit_pred = self.profit_model.predict(X_scaled)
            
            demand_mae = mean_absolute_error(y_demand, demand_pred)
            profit_mae = mean_absolute_error(y_profit, profit_pred)
            
            # Save models
            self.save_model()
            
            logger.info("Pricing models trained successfully")
            
            return {
                'demand_model_mae': demand_mae,
                'profit_model_mae': profit_mae,
                'demand_r2': self.demand_model.score(X_scaled, y_demand),
                'profit_r2': self.profit_model.score(X_scaled, y_profit),
                'feature_importance': dict(zip(feature_columns, self.demand_model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Error training pricing models: {str(e)}")
            raise
    
    def optimize_price(self, product_data: Dict, objective: str = 'profit') -> Dict:
        """
        Optimize price for a single product
        
        Args:
            product_data: Product information and market data
            objective: Optimization objective ('profit', 'revenue', 'market_share')
            
        Returns:
            Optimal pricing recommendation
        """
        try:
            if not self.is_trained:
                self.load_model()
            
            current_price = product_data.get('current_price', 100)
            cost = product_data.get('cost', current_price * 0.6)
            min_price = cost * 1.1  # Minimum 10% margin
            max_price = current_price * 2.0  # Maximum 100% increase
            
            # Test price range
            price_range = np.linspace(min_price, max_price, 50)
            results = []
            
            for test_price in price_range:
                # Create test data
                test_data = pd.DataFrame([{
                    'price': test_price,
                    'cost': cost,
                    'competitor_price': product_data.get('competitor_price', current_price),
                    'inventory_level': product_data.get('inventory_level', 50),
                    'category': product_data.get('category', 'general'),
                    'date': datetime.now()
                }])
                
                # Prepare features
                features_df = self.prepare_pricing_features(test_data)
                X = features_df[self.feature_names]
                X_scaled = self.scaler.transform(X)
                
                # Predict demand and profit
                predicted_demand = max(0, self.demand_model.predict(X_scaled)[0])
                predicted_profit = self.profit_model.predict(X_scaled)[0]
                
                # Calculate metrics
                revenue = test_price * predicted_demand
                total_profit = (test_price - cost) * predicted_demand
                margin_percentage = ((test_price - cost) / test_price) * 100
                
                results.append({
                    'price': test_price,
                    'predicted_demand': predicted_demand,
                    'revenue': revenue,
                    'profit': total_profit,
                    'margin_percentage': margin_percentage,
                    'profit_per_unit': test_price - cost
                })
            
            # Find optimal price based on objective
            if objective == 'profit':
                optimal_result = max(results, key=lambda x: x['profit'])
            elif objective == 'revenue':
                optimal_result = max(results, key=lambda x: x['revenue'])
            else:  # market_share
                optimal_result = max(results, key=lambda x: x['predicted_demand'])
            
            # Calculate impact metrics
            current_demand = self._predict_current_demand(product_data)
            demand_change = (optimal_result['predicted_demand'] - current_demand) / current_demand * 100
            price_change = (optimal_result['price'] - current_price) / current_price * 100
            
            return {
                'product_id': product_data.get('product_id'),
                'current_price': current_price,
                'optimal_price': optimal_result['price'],
                'price_change_percentage': price_change,
                'predicted_demand': optimal_result['predicted_demand'],
                'demand_change_percentage': demand_change,
                'expected_revenue': optimal_result['revenue'],
                'expected_profit': optimal_result['profit'],
                'margin_percentage': optimal_result['margin_percentage'],
                'confidence_score': self._calculate_confidence(results, optimal_result),
                'recommendation_strength': self._get_recommendation_strength(price_change),
                'risk_factors': self._identify_risk_factors(product_data, optimal_result)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing price: {str(e)}")
            raise
    
    def optimize_portfolio_pricing(self, products: List[Dict], objective: str = 'profit') -> Dict:
        """
        Optimize pricing for a portfolio of products
        
        Args:
            products: List of product data dictionaries
            objective: Optimization objective
            
        Returns:
            Portfolio pricing recommendations
        """
        recommendations = []
        total_current_revenue = 0
        total_optimized_revenue = 0
        total_current_profit = 0
        total_optimized_profit = 0
        
        for product in products:
            result = self.optimize_price(product, objective)
            recommendations.append(result)
            
            # Calculate totals
            current_demand = self._predict_current_demand(product)
            current_revenue = product.get('current_price', 100) * current_demand
            current_profit = (product.get('current_price', 100) - product.get('cost', 60)) * current_demand
            
            total_current_revenue += current_revenue
            total_optimized_revenue += result['expected_revenue']
            total_current_profit += current_profit
            total_optimized_profit += result['expected_profit']
        
        # Sort by potential impact
        recommendations.sort(key=lambda x: abs(x['price_change_percentage']), reverse=True)
        
        return {
            'recommendations': recommendations,
            'portfolio_summary': {
                'total_products': len(products),
                'current_revenue': total_current_revenue,
                'optimized_revenue': total_optimized_revenue,
                'revenue_improvement': ((total_optimized_revenue - total_current_revenue) / total_current_revenue * 100) if total_current_revenue > 0 else 0,
                'current_profit': total_current_profit,
                'optimized_profit': total_optimized_profit,
                'profit_improvement': ((total_optimized_profit - total_current_profit) / total_current_profit * 100) if total_current_profit > 0 else 0
            },
            'high_impact_products': [r for r in recommendations if abs(r['price_change_percentage']) > 10],
            'pricing_strategy': self._generate_pricing_strategy(recommendations)
        }
    
    def _predict_current_demand(self, product_data: Dict) -> float:
        """Predict current demand for baseline calculations"""
        # Simplified current demand prediction
        return product_data.get('avg_sales', 50)
    
    def _calculate_confidence(self, results: List[Dict], optimal_result: Dict) -> float:
        """Calculate confidence score for the optimal price"""
        # Calculate how much better the optimal result is compared to alternatives
        profits = [r['profit'] for r in results]
        max_profit = max(profits)
        second_max = sorted(profits, reverse=True)[1] if len(profits) > 1 else max_profit * 0.9
        
        confidence = (max_profit - second_max) / max_profit if max_profit > 0 else 0.5
        return min(max(confidence, 0.1), 1.0)
    
    def _get_recommendation_strength(self, price_change: float) -> str:
        """Get recommendation strength based on price change"""
        abs_change = abs(price_change)
        if abs_change < 5:
            return 'weak'
        elif abs_change < 15:
            return 'moderate'
        else:
            return 'strong'
    
    def _identify_risk_factors(self, product_data: Dict, optimal_result: Dict) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        price_change = optimal_result.get('price_change_percentage', 0)
        
        if abs(price_change) > 20:
            risks.append('Large price change may impact customer perception')
        
        if optimal_result.get('margin_percentage', 0) < 20:
            risks.append('Low profit margin')
        
        if product_data.get('inventory_level', 0) < 10:
            risks.append('Low inventory may limit demand capture')
        
        competitor_price = product_data.get('competitor_price', 0)
        if competitor_price > 0 and optimal_result['optimal_price'] > competitor_price * 1.2:
            risks.append('Price significantly higher than competition')
        
        return risks
    
    def _generate_pricing_strategy(self, recommendations: List[Dict]) -> Dict:
        """Generate overall pricing strategy recommendations"""
        price_increases = [r for r in recommendations if r['price_change_percentage'] > 5]
        price_decreases = [r for r in recommendations if r['price_change_percentage'] < -5]
        
        strategy = {
            'products_to_increase': len(price_increases),
            'products_to_decrease': len(price_decreases),
            'avg_price_change': np.mean([r['price_change_percentage'] for r in recommendations]),
            'strategy_focus': 'profit_maximization' if len(price_increases) > len(price_decreases) else 'market_penetration'
        }
        
        return strategy
    
    def save_model(self):
        """Save the trained models and scaler"""
        try:
            model_data = {
                'demand_model': self.demand_model,
                'profit_model': self.profit_model,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Pricing models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def load_model(self):
        """Load previously trained models"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                model_data = joblib.load(self.model_path)
                self.demand_model = model_data['demand_model']
                self.profit_model = model_data['profit_model']
                self.feature_names = model_data.get('feature_names', [])
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                logger.info("Pricing models loaded successfully")
            else:
                logger.warning("No saved models found, using default models")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")

# Utility functions for integration
def optimize_product_price(product_data: Dict, objective: str = 'profit') -> Dict:
    """
    Convenience function to optimize price for a single product
    """
    engine = DynamicPricingEngine()
    return engine.optimize_price(product_data, objective)

def optimize_portfolio_prices(products_data: List[Dict], objective: str = 'profit') -> Dict:
    """
    Convenience function to optimize prices for multiple products
    """
    engine = DynamicPricingEngine()
    return engine.optimize_portfolio_pricing(products_data, objective)
