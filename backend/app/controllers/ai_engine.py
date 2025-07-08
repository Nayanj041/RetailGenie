import json
import logging
import os
import re
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
import google.generativeai as genai
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


class AIEngine:
    def __init__(self):
        """Initialize the AI Engine with enhanced capabilities"""
        # Initialize Google Gemini with error handling
        self.gemini_model = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initialize Gemini with proper error handling"""
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel(
                    os.getenv("GEMINI_MODEL", "gemini-pro")
                )
                logger.info("AI Engine: Gemini initialized successfully")
            else:
                logger.warning("AI Engine: Gemini API key not found")
        except Exception as e:
            logger.warning(f"AI Engine: Failed to initialize Gemini: {str(e)}")
            self.gemini_model = None

        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")

    def forecast_demand(
        self, historical_data: List[float], days_ahead: int = 30
    ) -> List[float]:
        """
        Forecast demand using LSTM/ARIMA models

        Args:
            historical_data (List[float]): Historical sales data
            days_ahead (int): Number of days to forecast

        Returns:
            List[float]: Forecasted demand values
        """
        try:
            if len(historical_data) < 10:
                # Not enough data for complex forecasting, use simple moving average
                return self._simple_moving_average_forecast(historical_data, days_ahead)

            # Convert to pandas series
            data = pd.Series(historical_data)

            # Use exponential smoothing for forecasting
            forecast = self._exponential_smoothing_forecast(data, days_ahead)

            return forecast.tolist()

        except Exception as e:
            logger.error(f"Error in demand forecasting: {str(e)}")
            # Fallback to simple average
            avg = np.mean(historical_data) if historical_data else 0
            return [avg] * days_ahead

    def find_product_substitutes(
        self, original_product: Dict, all_products: List[Dict], preferences: Dict = None
    ) -> List[Dict]:
        """
        Find product substitutes using AI similarity matching

        Args:
            original_product (Dict): Original product details
            all_products (List[Dict]): All available products
            preferences (Dict): User preferences

        Returns:
            List[Dict]: Ranked substitute products
        """
        try:
            if not all_products:
                return []

            # Filter products in the same category
            category_products = [
                p
                for p in all_products
                if p.get("category") == original_product.get("category")
                and p.get("id") != original_product.get("id")
            ]

            if not category_products:
                return []

            # Calculate similarity scores
            scored_substitutes = []

            for product in category_products:
                similarity_score = self._calculate_product_similarity(
                    original_product, product
                )

                # Apply user preferences
                preference_score = self._apply_preference_scoring(
                    product, preferences or {}
                )

                # Combined score
                final_score = (similarity_score * 0.7) + (preference_score * 0.3)

                product_copy = product.copy()
                product_copy["similarity_score"] = similarity_score
                product_copy["preference_score"] = preference_score
                product_copy["final_score"] = final_score

                scored_substitutes.append(product_copy)

            # Sort by final score
            scored_substitutes.sort(key=lambda x: x["final_score"], reverse=True)

            return scored_substitutes[:10]  # Return top 10 substitutes

        except Exception as e:
            logger.error(f"Error finding substitutes: {str(e)}")
            return []

    def optimize_coupons(
        self,
        cart_items: List[Dict],
        available_coupons: List[Dict],
        purchase_history: List[Dict],
        cart_total: float,
    ) -> List[Dict]:
        """
        Optimize coupon selection using AI

        Args:
            cart_items (List[Dict]): Items in cart
            available_coupons (List[Dict]): Available coupons
            purchase_history (List[Dict]): User's purchase history
            cart_total (float): Total cart value

        Returns:
            List[Dict]: Optimized coupon recommendations
        """
        try:
            applicable_coupons = []

            for coupon in available_coupons:
                if self._is_coupon_applicable(
                    coupon, cart_items, cart_total, purchase_history
                ):
                    savings = self._calculate_coupon_savings(
                        coupon, cart_items, cart_total
                    )

                    coupon_copy = coupon.copy()
                    coupon_copy["savings"] = savings
                    coupon_copy["effectiveness_score"] = (
                        self._calculate_coupon_effectiveness(
                            coupon, cart_items, purchase_history
                        )
                    )

                    applicable_coupons.append(coupon_copy)

            # Sort by effectiveness and savings
            applicable_coupons.sort(
                key=lambda x: (x["effectiveness_score"], x["savings"]), reverse=True
            )

            # Select non-conflicting coupons that maximize savings
            optimized_coupons = self._select_optimal_coupon_combination(
                applicable_coupons
            )

            return optimized_coupons

        except Exception as e:
            logger.error(f"Error optimizing coupons: {str(e)}")
            return []

    def analyze_customer_sentiment(self, feedback_text: str) -> Dict[str, Any]:
        """
        Advanced sentiment analysis with emotion detection

        Args:
            feedback_text (str): Customer feedback text

        Returns:
            Dict[str, Any]: Detailed sentiment analysis
        """
        try:
            # Basic sentiment analysis (enhanced version)
            sentiment_score = self._calculate_sentiment_score(feedback_text)

            # Extract emotions
            emotions = self._extract_emotions(feedback_text)

            # Extract key topics/aspects
            aspects = self._extract_aspects(feedback_text)

            # Determine urgency level
            urgency = self._determine_urgency(feedback_text, sentiment_score)

            return {
                "sentiment": self._score_to_sentiment(sentiment_score),
                "sentiment_score": sentiment_score,
                "confidence": self._calculate_confidence(feedback_text),
                "emotions": emotions,
                "aspects": aspects,
                "urgency": urgency,
                "key_phrases": self._extract_key_phrases(feedback_text),
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.5,
                "emotions": [],
                "aspects": [],
                "urgency": "low",
            }

    def generate_pricing_recommendations(
        self, product_data: Dict, market_conditions: Dict
    ) -> Dict[str, Any]:
        """
        Generate dynamic pricing recommendations

        Args:
            product_data (Dict): Product information
            market_conditions (Dict): Current market conditions

        Returns:
            Dict[str, Any]: Pricing recommendations
        """
        try:
            current_price = product_data.get("price", 0)

            # Analyze demand elasticity
            demand_factor = self._calculate_demand_factor(
                product_data, market_conditions
            )

            # Analyze competitive positioning
            competition_factor = self._calculate_competition_factor(
                product_data, market_conditions
            )

            # Consider inventory levels
            inventory_factor = self._calculate_inventory_factor(product_data)

            # Calculate recommended price adjustment
            price_adjustment = self._calculate_price_adjustment(
                demand_factor, competition_factor, inventory_factor
            )

            recommended_price = current_price * (1 + price_adjustment)

            return {
                "current_price": current_price,
                "recommended_price": round(recommended_price, 2),
                "price_change": price_adjustment,
                "factors": {
                    "demand": demand_factor,
                    "competition": competition_factor,
                    "inventory": inventory_factor,
                },
                "confidence": self._calculate_pricing_confidence(
                    product_data, market_conditions
                ),
                "expected_impact": self._estimate_pricing_impact(
                    price_adjustment, product_data
                ),
            }

        except Exception as e:
            logger.error(f"Error generating pricing recommendations: {str(e)}")
            return {
                "current_price": product_data.get("price", 0),
                "recommended_price": product_data.get("price", 0),
                "price_change": 0,
                "confidence": 0.5,
            }

    def generate_general_response(self, message: str) -> str:
        """
        Generate general conversational response using AI

        Args:
            message (str): User message

        Returns:
            str: AI response
        """
        try:
            # This would use Google Gemini API in production
            # For now, using rule-based responses

            message_lower = message.lower()

            if any(word in message_lower for word in ["help", "assist", "support"]):
                return "I'm here to help you with your shopping needs. I can help you find products, check prices, get recommendations, and more!"

            elif any(word in message_lower for word in ["thank", "thanks"]):
                return (
                    "You're welcome! Is there anything else I can help you with today?"
                )

            elif any(word in message_lower for word in ["bye", "goodbye", "see you"]):
                return "Goodbye! Have a great shopping experience. Feel free to ask if you need any help!"

            else:
                return "I understand you're looking for assistance. I can help you find products, check availability, compare prices, and provide recommendations. What would you like to explore?"

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return (
                "I'm here to help with your shopping needs. How can I assist you today?"
            )

    def search_products(self, query: str, products: List[Dict]) -> List[Dict]:
        """
        Perform AI-powered product search

        Args:
            query (str): Search query
            products (List[Dict]): List of all products

        Returns:
            List[Dict]: Ranked search results
        """
        try:
            if not products:
                return []

            # Simple keyword-based search (can be enhanced with AI/ML models)
            query_lower = query.lower()
            scored_products = []

            for product in products:
                score = 0
                name = product.get("name", "").lower()
                description = product.get("description", "").lower()
                category = product.get("category", "").lower()
                tags = product.get("tags", [])

                # Calculate relevance score
                if query_lower in name:
                    score += 10
                if query_lower in description:
                    score += 5
                if query_lower in category:
                    score += 3

                # Check tags
                for tag in tags:
                    if query_lower in tag.lower():
                        score += 2

                # Fuzzy matching for partial words
                words = query_lower.split()
                for word in words:
                    if word in name or word in description:
                        score += 1

                if score > 0:
                    product_copy = product.copy()
                    product_copy["relevance_score"] = score
                    scored_products.append(product_copy)

            # Sort by relevance score
            scored_products.sort(key=lambda x: x["relevance_score"], reverse=True)

            return scored_products[:20]  # Return top 20 results
        except Exception as e:
            logger.error(f"Error in product search: {str(e)}")
            return products[:10]  # Fallback to first 10 products

    def generate_recommendations(
        self, user_preferences: Dict, products: List[Dict]
    ) -> List[Dict]:
        """
        Generate AI-powered product recommendations

        Args:
            user_preferences (Dict): User preferences and history
            products (List[Dict]): List of all products

        Returns:
            List[Dict]: Recommended products
        """
        try:
            if not products:
                return []

            # Extract user preferences
            preferred_categories = user_preferences.get("categories", [])
            price_range = user_preferences.get("price_range", {})
            previous_purchases = user_preferences.get("purchase_history", [])
            favorite_brands = user_preferences.get("brands", [])

            scored_products = []

            for product in products:
                score = 0

                # Category preference
                if product.get("category") in preferred_categories:
                    score += 15

                # Price range preference
                price = product.get("price", 0)
                min_price = price_range.get("min", 0)
                max_price = price_range.get("max", float("inf"))
                if min_price <= price <= max_price:
                    score += 10

                # Brand preference
                if product.get("brand") in favorite_brands:
                    score += 12

                # Avoid recommending previously purchased items
                if product.get("id") not in previous_purchases:
                    score += 5

                # High-rated products
                rating = product.get("rating", 0)
                if rating >= 4.0:
                    score += 8
                elif rating >= 3.5:
                    score += 5

                # Popular products (based on review count)
                review_count = product.get("review_count", 0)
                if review_count > 100:
                    score += 6
                elif review_count > 50:
                    score += 3

                if score > 0:
                    product_copy = product.copy()
                    product_copy["recommendation_score"] = score
                    scored_products.append(product_copy)

            # Sort by recommendation score
            scored_products.sort(key=lambda x: x["recommendation_score"], reverse=True)

            return scored_products[:15]  # Return top 15 recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return products[:10]  # Fallback to first 10 products

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text

        Args:
            text (str): Text to analyze

        Returns:
            str: Sentiment (positive, negative, neutral)
        """
        try:
            # Simple rule-based sentiment analysis
            # In production, use more sophisticated models

            positive_words = [
                "good",
                "great",
                "excellent",
                "amazing",
                "wonderful",
                "fantastic",
                "love",
                "perfect",
                "best",
                "awesome",
                "brilliant",
                "outstanding",
                "satisfied",
                "happy",
                "pleased",
                "delighted",
                "impressed",
            ]

            negative_words = [
                "bad",
                "terrible",
                "awful",
                "horrible",
                "worst",
                "hate",
                "disappointed",
                "poor",
                "useless",
                "broken",
                "defective",
                "unsatisfied",
                "angry",
                "frustrated",
                "annoyed",
                "regret",
            ]

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return "neutral"

    def analyze_feedback(self, feedback_list: List[Dict]) -> Dict:
        """
        Analyze feedback using AI

        Args:
            feedback_list (List[Dict]): List of feedback entries

        Returns:
            Dict: Analysis results
        """
        try:
            if not feedback_list:
                return {
                    "sentiment_analysis": {"positive": 0, "negative": 0, "neutral": 0},
                    "key_themes": [],
                    "recommendations": [],
                }

            # Sentiment analysis
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            all_comments = []

            for feedback in feedback_list:
                sentiment = feedback.get("sentiment", "neutral")
                sentiment_counts[sentiment] += 1

                comment = feedback.get("comment", "")
                if comment:
                    all_comments.append(comment.lower())

            # Extract key themes (common words/phrases)
            key_themes = self._extract_key_themes(all_comments)

            # Generate recommendations based on negative feedback
            recommendations = self._generate_improvement_recommendations(
                feedback_list, key_themes
            )

            return {
                "sentiment_analysis": sentiment_counts,
                "key_themes": key_themes,
                "recommendations": recommendations,
            }
        except Exception as e:
            logger.error(f"Error analyzing feedback: {str(e)}")
            return {
                "sentiment_analysis": {"positive": 0, "negative": 0, "neutral": 0},
                "key_themes": [],
                "recommendations": [],
            }

    def enhance_product_data(self, product_data: Dict) -> Dict:
        """
        Enhance product data with AI-generated features

        Args:
            product_data (Dict): Original product data

        Returns:
            Dict: Enhanced product data
        """
        try:
            enhanced_data = product_data.copy()

            # Generate tags based on name and description
            name = product_data.get("name", "")
            description = product_data.get("description", "")

            # Simple tag extraction (can be enhanced with NLP)
            tags = self._extract_tags(name + " " + description)
            enhanced_data["tags"] = tags

            # Add metadata
            enhanced_data["created_at"] = datetime.now().isoformat()
            enhanced_data["ai_enhanced"] = True

            return enhanced_data
        except Exception as e:
            logger.error(f"Error enhancing product data: {str(e)}")
            return product_data

    # Helper methods for advanced AI functionality

    def _simple_moving_average_forecast(
        self, data: List[float], days_ahead: int
    ) -> List[float]:
        """Simple moving average forecast for insufficient data"""
        if not data:
            return [0] * days_ahead

        # Use last 7 days or all available data
        window = min(7, len(data))
        avg = np.mean(data[-window:])

        # Add some randomness for realistic forecasting
        forecast = []
        for i in range(days_ahead):
            # Add slight trend and noise
            trend_factor = 1 + (np.random.random() - 0.5) * 0.1
            noise = np.random.normal(0, avg * 0.05)
            forecast.append(max(0, avg * trend_factor + noise))

        return forecast

    def _exponential_smoothing_forecast(
        self, data: pd.Series, days_ahead: int
    ) -> pd.Series:
        """Exponential smoothing forecast"""
        try:
            # Simple exponential smoothing
            alpha = 0.3  # Smoothing parameter

            # Initialize
            forecast = [data.iloc[0]]

            # Calculate smoothed values
            for i in range(1, len(data)):
                forecast.append(alpha * data.iloc[i] + (1 - alpha) * forecast[-1])

            # Generate future forecasts
            last_forecast = forecast[-1]
            future_forecasts = []

            for i in range(days_ahead):
                # Add slight trend based on recent data
                trend = self._calculate_trend_factor(data.tail(10))
                future_forecast = last_forecast * (1 + trend)
                future_forecasts.append(max(0, future_forecast))
                last_forecast = future_forecast

            return pd.Series(future_forecasts)

        except Exception as e:
            logger.error(f"Error in exponential smoothing: {str(e)}")
            return pd.Series([np.mean(data)] * days_ahead)

    def _calculate_trend_factor(self, data: pd.Series) -> float:
        """Calculate trend factor from recent data"""
        if len(data) < 2:
            return 0

        # Simple linear trend
        x = np.arange(len(data))
        y = data.values

        try:
            slope = np.polyfit(x, y, 1)[0]
            return slope / max(np.mean(y), 1) * 0.01  # Small trend factor
        except:
            return 0

    def _calculate_product_similarity(self, product1: Dict, product2: Dict) -> float:
        """Calculate similarity between two products"""
        try:
            similarity_score = 0

            # Price similarity (closer prices = higher similarity)
            price1 = product1.get("price", 0)
            price2 = product2.get("price", 0)
            if price1 > 0 and price2 > 0:
                price_diff = abs(price1 - price2) / max(price1, price2)
                price_similarity = 1 - min(price_diff, 1)
                similarity_score += price_similarity * 0.3

            # Brand similarity
            if product1.get("brand") == product2.get("brand"):
                similarity_score += 0.2

            # Rating similarity
            rating1 = product1.get("rating", 0)
            rating2 = product2.get("rating", 0)
            if rating1 > 0 and rating2 > 0:
                rating_diff = abs(rating1 - rating2) / 5.0
                rating_similarity = 1 - rating_diff
                similarity_score += rating_similarity * 0.2

            # Text similarity (name and description)
            text_similarity = self._calculate_text_similarity(
                product1.get("name", "") + " " + product1.get("description", ""),
                product2.get("name", "") + " " + product2.get("description", ""),
            )
            similarity_score += text_similarity * 0.3

            return min(similarity_score, 1.0)

        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF"""
        try:
            if not text1 or not text2:
                return 0

            # Simple word overlap calculation
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            intersection = words1.intersection(words2)
            union = words1.union(words2)

            return len(intersection) / len(union) if union else 0

        except Exception as e:
            logger.error(f"Error calculating text similarity: {str(e)}")
            return 0

    def _apply_preference_scoring(self, product: Dict, preferences: Dict) -> float:
        """Apply user preference scoring to product"""
        try:
            score = 0.5  # Base score

            # Price preference
            if "max_price" in preferences:
                max_price = preferences["max_price"]
                product_price = product.get("price", 0)
                if product_price <= max_price:
                    score += 0.2
                else:
                    score -= 0.1

            # Brand preference
            preferred_brands = preferences.get("preferred_brands", [])
            if product.get("brand") in preferred_brands:
                score += 0.2

            # Rating preference
            min_rating = preferences.get("min_rating", 0)
            product_rating = product.get("rating", 0)
            if product_rating >= min_rating:
                score += 0.1

            return min(max(score, 0), 1)

        except Exception as e:
            logger.error(f"Error applying preferences: {str(e)}")
            return 0.5

    def _is_coupon_applicable(
        self,
        coupon: Dict,
        cart_items: List[Dict],
        cart_total: float,
        purchase_history: List[Dict],
    ) -> bool:
        """Check if coupon is applicable to current cart"""
        try:
            # Check minimum purchase amount
            min_amount = coupon.get("min_purchase_amount", 0)
            if cart_total < min_amount:
                return False

            # Check category restrictions
            allowed_categories = coupon.get("allowed_categories", [])
            if allowed_categories:
                cart_categories = [item.get("category") for item in cart_items]
                if not any(cat in allowed_categories for cat in cart_categories):
                    return False

            # Check usage limits
            max_usage = coupon.get("max_usage_per_user", float("inf"))
            user_usage = sum(
                1
                for purchase in purchase_history
                if coupon.get("id") in purchase.get("coupons_used", [])
            )
            if user_usage >= max_usage:
                return False

            # Check expiry date
            expiry_date = coupon.get("expiry_date")
            if expiry_date:
                try:
                    expiry = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))
                    if datetime.now() > expiry:
                        return False
                except:
                    pass

            return True

        except Exception as e:
            logger.error(f"Error checking coupon applicability: {str(e)}")
            return False

    def _calculate_coupon_savings(
        self, coupon: Dict, cart_items: List[Dict], cart_total: float
    ) -> float:
        """Calculate savings from applying coupon"""
        try:
            coupon_type = coupon.get("type", "percentage")

            if coupon_type == "percentage":
                discount_percent = coupon.get("discount_percent", 0)
                max_discount = coupon.get("max_discount_amount", float("inf"))
                savings = min(cart_total * (discount_percent / 100), max_discount)

            elif coupon_type == "fixed_amount":
                savings = min(coupon.get("discount_amount", 0), cart_total)

            elif coupon_type == "buy_x_get_y":
                # Simplified calculation for buy X get Y free
                savings = self._calculate_bogo_savings(coupon, cart_items)

            else:
                savings = 0

            return savings

        except Exception as e:
            logger.error(f"Error calculating coupon savings: {str(e)}")
            return 0

    def _calculate_bogo_savings(self, coupon: Dict, cart_items: List[Dict]) -> float:
        """Calculate Buy X Get Y savings"""
        # Simplified BOGO calculation
        try:
            buy_quantity = coupon.get("buy_quantity", 1)
            get_quantity = coupon.get("get_quantity", 1)

            # Find applicable items
            applicable_items = []
            for item in cart_items:
                if item.get("category") in coupon.get("allowed_categories", []):
                    applicable_items.extend([item] * item.get("quantity", 1))

            if len(applicable_items) < buy_quantity:
                return 0

            # Sort by price (give away cheapest items)
            applicable_items.sort(key=lambda x: x.get("price", 0))

            # Calculate savings
            sets = len(applicable_items) // buy_quantity
            free_items = min(
                sets * get_quantity, len(applicable_items) - sets * buy_quantity
            )

            savings = sum(
                item.get("price", 0) for item in applicable_items[:free_items]
            )
            return savings

        except Exception as e:
            logger.error(f"Error calculating BOGO savings: {str(e)}")
            return 0

    def _calculate_coupon_effectiveness(
        self, coupon: Dict, cart_items: List[Dict], purchase_history: List[Dict]
    ) -> float:
        """Calculate coupon effectiveness score"""
        try:
            score = 0.5  # Base score

            # Historical usage success
            total_usage = coupon.get("total_usage", 0)
            successful_conversions = coupon.get("successful_conversions", 0)
            if total_usage > 0:
                conversion_rate = successful_conversions / total_usage
                score += conversion_rate * 0.3

            # Relevance to cart
            applicable_items = sum(
                1
                for item in cart_items
                if item.get("category") in coupon.get("allowed_categories", [])
            )
            if applicable_items > 0:
                score += (applicable_items / len(cart_items)) * 0.2

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Error calculating effectiveness: {str(e)}")
            return 0.5

    def _select_optimal_coupon_combination(self, coupons: List[Dict]) -> List[Dict]:
        """Select optimal combination of non-conflicting coupons"""
        try:
            # Simple greedy selection - can be enhanced with optimization algorithms
            selected = []
            used_categories = set()

            for coupon in coupons:
                coupon_categories = set(coupon.get("allowed_categories", []))

                # Check for conflicts
                if not coupon_categories.intersection(used_categories):
                    selected.append(coupon)
                    used_categories.update(coupon_categories)

                    # Limit to 3 coupons maximum
                    if len(selected) >= 3:
                        break

            return selected

        except Exception as e:
            logger.error(f"Error selecting coupon combination: {str(e)}")
            return coupons[:1] if coupons else []

    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score (-1 to 1)"""
        try:
            # Enhanced sentiment calculation
            positive_words = [
                "good",
                "great",
                "excellent",
                "amazing",
                "wonderful",
                "fantastic",
                "love",
                "perfect",
                "best",
                "awesome",
                "brilliant",
                "outstanding",
                "satisfied",
                "happy",
                "pleased",
                "delighted",
                "impressed",
                "recommend",
                "quality",
                "fast",
                "reliable",
                "helpful",
                "friendly",
                "professional",
            ]

            negative_words = [
                "bad",
                "terrible",
                "awful",
                "horrible",
                "worst",
                "hate",
                "disappointed",
                "poor",
                "useless",
                "broken",
                "defective",
                "unsatisfied",
                "angry",
                "frustrated",
                "annoyed",
                "regret",
                "slow",
                "expensive",
                "unreliable",
                "rude",
                "unprofessional",
            ]

            text_lower = text.lower()
            words = text_lower.split()

            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)

            # Normalize by text length
            text_length = len(words)
            if text_length == 0:
                return 0

            positive_ratio = positive_count / text_length
            negative_ratio = negative_count / text_length

            return positive_ratio - negative_ratio

        except Exception as e:
            logger.error(f"Error calculating sentiment: {str(e)}")
            return 0

    def _extract_emotions(self, text: str) -> List[str]:
        """Extract emotions from text"""
        try:
            emotion_keywords = {
                "joy": ["happy", "joy", "excited", "pleased", "delighted"],
                "anger": ["angry", "mad", "furious", "annoyed", "frustrated"],
                "sadness": ["sad", "disappointed", "unhappy", "regret"],
                "fear": ["worried", "concerned", "anxious", "scared"],
                "surprise": ["surprised", "shocked", "amazed", "unexpected"],
            }

            detected_emotions = []
            text_lower = text.lower()

            for emotion, keywords in emotion_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_emotions.append(emotion)

            return detected_emotions

        except Exception as e:
            logger.error(f"Error extracting emotions: {str(e)}")
            return []

    def _extract_aspects(self, text: str) -> List[str]:
        """Extract product aspects mentioned in text"""
        try:
            aspect_keywords = {
                "quality": ["quality", "build", "material", "durability"],
                "price": ["price", "cost", "expensive", "cheap", "value"],
                "service": ["service", "support", "staff", "help"],
                "delivery": ["delivery", "shipping", "fast", "slow", "arrived"],
                "packaging": ["packaging", "box", "wrapped", "damaged"],
                "design": ["design", "look", "appearance", "color", "style"],
            }

            detected_aspects = []
            text_lower = text.lower()

            for aspect, keywords in aspect_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_aspects.append(aspect)

            return detected_aspects

        except Exception as e:
            logger.error(f"Error extracting aspects: {str(e)}")
            return []

    def _determine_urgency(self, text: str, sentiment_score: float) -> str:
        """Determine urgency level of feedback"""
        try:
            urgent_keywords = ["urgent", "immediate", "asap", "emergency", "critical"]
            high_keywords = ["problem", "issue", "broken", "defective", "wrong"]

            text_lower = text.lower()

            if any(keyword in text_lower for keyword in urgent_keywords):
                return "urgent"
            elif sentiment_score < -0.5 or any(
                keyword in text_lower for keyword in high_keywords
            ):
                return "high"
            elif sentiment_score < -0.2:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"Error determining urgency: {str(e)}")
            return "low"

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        try:
            # Simple phrase extraction - can be enhanced with NLP
            sentences = text.split(".")
            key_phrases = []

            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence.split()) >= 3:
                    key_phrases.append(sentence)

            return key_phrases[:3]  # Return top 3 phrases

        except Exception as e:
            logger.error(f"Error extracting key phrases: {str(e)}")
            return []

    def _score_to_sentiment(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence in sentiment analysis"""
        try:
            # Confidence based on text length and keyword density
            words = text.split()
            if len(words) < 3:
                return 0.3
            elif len(words) < 10:
                return 0.6
            else:
                return 0.8
        except:
            return 0.5
