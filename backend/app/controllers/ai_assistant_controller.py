import json
import logging
import os
from datetime import datetime

import google.generativeai as genai
import speech_recognition as sr

from app.controllers.ai_engine import AIEngine
from app.utils.email_utils import EmailUtils
from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class AIAssistantController:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.firebase = FirebaseUtils()
        self.email_utils = EmailUtils()
        self.chat_collection = "chat_history"
        self.products_collection = "products"
        self.coupons_collection = "coupons"

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
                logger.info("Gemini AI initialized successfully")
            else:
                logger.warning("Gemini API key not found - AI features will be limited")
        except Exception as e:
            logger.warning(
                f"Failed to initialize Gemini AI: {str(e)} - AI features will be limited"
            )
            self.gemini_model = None
            self.gemini_model = None
            logger.warning("Gemini API key not configured")

    def process_chat_message(self, message, user_id, context=None):
        """
        Process chat message with AI assistant

        Args:
            message (str): User message
            user_id (str): User ID
            context (dict): Chat context

        Returns:
            dict: AI response with actions
        """
        try:
            # Get user's chat history for context
            chat_history = self._get_chat_history(user_id, limit=5)

            # Analyze user intent
            intent = self._analyze_intent(message)

            # Generate AI response based on intent
            if intent == "product_search":
                response = self._handle_product_search(message, user_id, context)
            elif intent == "product_substitute":
                response = self._handle_substitute_request(message, user_id, context)
            elif intent == "price_inquiry":
                response = self._handle_price_inquiry(message, user_id, context)
            elif intent == "store_navigation":
                response = self._handle_store_navigation(message, user_id, context)
            elif intent == "coupon_inquiry":
                response = self._handle_coupon_inquiry(message, user_id, context)
            else:
                response = self._handle_general_inquiry(message, user_id, context)

            # Save chat interaction
            self._save_chat_interaction(user_id, message, response)

            return response
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return {
                "text": "I'm sorry, I'm having trouble processing your request right now. Please try again.",
                "intent": "error",
                "actions": [],
            }

    def process_voice_command(self, audio_file, user_id, language="en"):
        """
        Process voice command from user

        Args:
            audio_file: Audio file object
            user_id (str): User ID
            language (str): Language code

        Returns:
            dict: Voice processing response
        """
        try:
            # Convert speech to text
            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language=language)

            # Process the text message
            response = self.process_chat_message(text, user_id)

            # Add voice-specific features
            response["voice_input"] = text
            response["language"] = language

            # Generate text-to-speech response if needed
            if response.get("generate_speech", False):
                response["audio_response"] = self._generate_speech(
                    response["text"], language
                )

            return response
        except sr.UnknownValueError:
            return {
                "text": "I couldn't understand what you said. Please try again.",
                "error": "speech_recognition_failed",
                "voice_input": None,
            }
        except Exception as e:
            logger.error(f"Error processing voice command: {str(e)}")
            return {
                "text": "I'm having trouble processing your voice command. Please try again.",
                "error": str(e),
            }

    def find_product_substitutes(self, product_id, preferences=None):
        """
        Find product substitutes using AI

        Args:
            product_id (str): Original product ID
            preferences (dict): User preferences

        Returns:
            dict: Product substitutes
        """
        try:
            # Get original product details
            original_product = self.firebase.get_document(
                self.products_collection, product_id
            )

            if not original_product:
                return {"substitutes": [], "message": "Original product not found"}

            # Get all products in the same category
            category_products = self.firebase.get_documents(
                self.products_collection, {"category": original_product.get("category")}
            )

            # Use AI to find best substitutes
            substitutes = self.ai_engine.find_product_substitutes(
                original_product, category_products, preferences
            )

            # Add substitute reasoning
            for substitute in substitutes:
                substitute["reason"] = self._generate_substitute_reason(
                    original_product, substitute
                )

            return {
                "original_product": original_product,
                "substitutes": substitutes[:5],  # Top 5 substitutes
                "total_found": len(substitutes),
                "preferences_applied": preferences or {},
            }
        except Exception as e:
            logger.error(f"Error finding substitutes: {str(e)}")
            raise

    def optimize_coupons(self, user_id, cart_items):
        """
        Optimize coupon recommendations for user's cart

        Args:
            user_id (str): User ID
            cart_items (list): Items in user's cart

        Returns:
            dict: Optimized coupon recommendations
        """
        try:
            # Get user's purchase history
            user_data = self.firebase.get_document("users", user_id)
            purchase_history = (
                user_data.get("purchase_history", []) if user_data else []
            )

            # Get available coupons
            available_coupons = self.firebase.get_documents(
                self.coupons_collection, {"is_active": True}
            )

            # Calculate cart total and analyze items
            cart_total = sum(
                item.get("price", 0) * item.get("quantity", 1) for item in cart_items
            )
            cart_categories = [item.get("category") for item in cart_items]

            # Use AI to optimize coupon selection
            optimized_coupons = self.ai_engine.optimize_coupons(
                cart_items, available_coupons, purchase_history, cart_total
            )

            # Calculate potential savings
            total_savings = sum(
                coupon.get("savings", 0) for coupon in optimized_coupons
            )

            return {
                "recommended_coupons": optimized_coupons,
                "total_savings": total_savings,
                "cart_total": cart_total,
                "final_total": cart_total - total_savings,
                "savings_percentage": (
                    (total_savings / cart_total * 100) if cart_total > 0 else 0
                ),
            }
        except Exception as e:
            logger.error(f"Error optimizing coupons: {str(e)}")
            raise

    def calculate_sustainability_score(self, cart_items):
        """
        Calculate sustainability score for cart items

        Args:
            cart_items (list): Items in cart

        Returns:
            dict: Sustainability analysis
        """
        try:
            total_score = 0
            item_scores = []
            sustainability_factors = []

            for item in cart_items:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)

                # Get product sustainability data
                product = self.firebase.get_document(
                    self.products_collection, product_id
                )

                if product:
                    # Calculate item sustainability score
                    item_score = self._calculate_item_sustainability_score(product)
                    total_score += item_score * quantity

                    item_scores.append(
                        {
                            "product_id": product_id,
                            "name": product.get("name"),
                            "score": item_score,
                            "quantity": quantity,
                            "factors": self._get_sustainability_factors(product),
                        }
                    )

            # Calculate overall score (0-100)
            overall_score = total_score / len(cart_items) if cart_items else 0

            # Generate recommendations for improvement
            recommendations = self._generate_sustainability_recommendations(item_scores)

            return {
                "overall_score": round(overall_score, 1),
                "grade": self._get_sustainability_grade(overall_score),
                "item_scores": item_scores,
                "recommendations": recommendations,
                "environmental_impact": self._calculate_environmental_impact(
                    cart_items
                ),
                "green_alternatives": self._suggest_green_alternatives(cart_items),
            }
        except Exception as e:
            logger.error(f"Error calculating sustainability score: {str(e)}")
            raise

    def _get_chat_history(self, user_id, limit=5):
        """Get recent chat history for context"""
        try:
            history = self.firebase.query_documents(
                self.chat_collection, "user_id", "==", user_id, limit=limit
            )

            # Sort by timestamp
            history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return history
        except:
            return []

    def _analyze_intent(self, message):
        """Analyze user intent from message"""
        message_lower = message.lower()

        if any(
            word in message_lower for word in ["find", "search", "looking for", "need"]
        ):
            return "product_search"
        elif any(
            word in message_lower
            for word in ["substitute", "alternative", "replace", "similar"]
        ):
            return "product_substitute"
        elif any(
            word in message_lower for word in ["price", "cost", "how much", "expensive"]
        ):
            return "price_inquiry"
        elif any(
            word in message_lower for word in ["where", "location", "aisle", "section"]
        ):
            return "store_navigation"
        elif any(
            word in message_lower for word in ["coupon", "discount", "deal", "offer"]
        ):
            return "coupon_inquiry"
        else:
            return "general_inquiry"

    def _handle_product_search(self, message, user_id, context):
        """Handle product search requests"""
        try:
            # Extract search terms (enhanced with Gemini if available)
            search_terms = self._extract_search_terms_with_ai(message)

            # Get all products from Firebase
            all_products = self.firebase.get_documents(self.products_collection)

            # Search products using AI engine
            products = self.ai_engine.search_products(search_terms, all_products)

            # Generate AI-powered response
            if len(products) > 0:
                response_text = (
                    f"I found {len(products)} products that match your search"
                )
                if self.gemini_model:
                    # Use Gemini to generate a more natural response
                    ai_response = self._generate_search_response(message, products[:3])
                    if ai_response:
                        response_text = ai_response
            else:
                response_text = "I couldn't find any products matching your search. Let me suggest some alternatives."
                # Could add alternative suggestions here

            return {
                "text": response_text,
                "intent": "product_search",
                "products": products[:5],
                "actions": ["show_products"],
                "search_terms": search_terms,
                "total_found": len(products),
            }
        except Exception as e:
            logger.error(f"Error in product search: {str(e)}")
            return {
                "text": "I'm having trouble searching for products right now. Please try again.",
                "intent": "error",
                "actions": [],
            }

    def _extract_search_terms_with_ai(self, message):
        """Extract search terms using AI for better understanding"""
        try:
            if self.gemini_model:
                # Use Gemini to extract key product-related terms
                prompt = f"""Extract the key product search terms from this message: "{message}"
                Return only the essential product keywords, separated by spaces.
                Focus on product names, categories, brands, or features.
                
                Example:
                Message: "I'm looking for wireless headphones for gaming"
                Keywords: wireless headphones gaming
                
                Message: {message}
                Keywords:"""

                response = self.gemini_model.generate_content(prompt)

                extracted_terms = response.text.strip()
                if extracted_terms and len(extracted_terms) > 0:
                    return extracted_terms

            # Fallback to simple extraction
            return self._extract_search_terms(message)

        except Exception as e:
            logger.error(f"Error extracting search terms with AI: {str(e)}")
            return self._extract_search_terms(message)

    def _generate_search_response(self, original_message, products):
        """Generate natural response using Gemini for search results"""
        try:
            if not self.gemini_model or not products:
                return None

            product_descriptions = []
            for product in products:
                desc = f"{product.get('name', 'Unknown')} (${product.get('price', 0)}) - {product.get('category', 'General')}"
                product_descriptions.append(desc)

            prompt = f"""The user asked: "{original_message}"
            I found these products: {'; '.join(product_descriptions)}
            
            Write a helpful, conversational response (max 100 words) that:
            1. Acknowledges their request
            2. Mentions the products found
            3. Offers to help further
            
            Keep it natural and friendly.
            
            Response:"""

            response = self.gemini_model.generate_content(prompt)

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating AI search response: {str(e)}")
            return None

    def _handle_substitute_request(self, message, user_id, context):
        """Handle product substitute requests"""
        # Implementation for substitute handling
        return {
            "text": "I can help you find alternatives. What product are you looking to substitute?",
            "intent": "product_substitute",
            "actions": ["request_product_info"],
        }

    def _handle_price_inquiry(self, message, user_id, context):
        """Handle price inquiry requests"""
        return {
            "text": "I can help you check prices. What product would you like to know about?",
            "intent": "price_inquiry",
            "actions": ["request_product_info"],
        }

    def _handle_store_navigation(self, message, user_id, context):
        """Handle store navigation requests"""
        return {
            "text": "I can help you navigate the store. What are you looking for?",
            "intent": "store_navigation",
            "actions": ["show_store_map"],
        }

    def _handle_coupon_inquiry(self, message, user_id, context):
        """Handle coupon inquiry requests"""
        return {
            "text": "Let me check for available coupons and deals for you.",
            "intent": "coupon_inquiry",
            "actions": ["show_coupons"],
        }

    def _handle_general_inquiry(self, message, user_id, context):
        """Handle general inquiries using Google Gemini"""
        try:
            # If Gemini API key is configured, use Gemini
            if self.gemini_model:
                response = self._get_gemini_response(message, context)
                return {"text": response, "intent": "general_inquiry", "actions": []}
            else:
                # Fallback to rule-based response
                response = self.ai_engine.generate_general_response(message)
                return {"text": response, "intent": "general_inquiry", "actions": []}
        except Exception as e:
            logger.error(f"Error in general inquiry: {str(e)}")
            return {
                "text": "I'm here to help with your shopping needs. How can I assist you?",
                "intent": "general_inquiry",
                "actions": [],
            }

    def _get_gemini_response(self, message, context=None):
        """Get response from Google Gemini"""
        try:
            # Build conversation context
            system_prompt = """You are a helpful AI shopping assistant for RetailGenie, 
            an e-commerce platform. You help customers find products, answer questions about 
            pricing, suggest alternatives, and provide shopping advice. Keep responses 
            conversational, helpful, and focused on retail/shopping topics. Limit responses to 150 words."""

            # Combine system prompt with user message
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"

            # Add context if provided
            if context and context.get("recent_searches"):
                context_info = f"User has recently searched for: {', '.join(context['recent_searches'])}\n"
                full_prompt = (
                    f"{system_prompt}\n\n{context_info}User: {message}\n\nAssistant:"
                )

            response = self.gemini_model.generate_content(full_prompt)

            return response.text.strip()

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            # Fallback to rule-based response
            return self.ai_engine.generate_general_response(message)

    def _save_chat_interaction(self, user_id, message, response):
        """Save chat interaction to database"""
        try:
            interaction = {
                "user_id": user_id,
                "user_message": message,
                "ai_response": response.get("text"),
                "intent": response.get("intent"),
                "timestamp": datetime.now().isoformat(),
                "actions": response.get("actions", []),
            }

            self.firebase.create_document(self.chat_collection, interaction)
        except Exception as e:
            logger.warning(f"Failed to save chat interaction: {str(e)}")

    def _extract_search_terms(self, message):
        """Extract search terms from user message"""
        # Simple implementation - can be enhanced with NLP
        stop_words = {
            "i",
            "am",
            "looking",
            "for",
            "need",
            "want",
            "find",
            "search",
            "the",
            "a",
            "an",
        }
        words = message.lower().split()
        return " ".join([word for word in words if word not in stop_words])

    def _generate_substitute_reason(self, original, substitute):
        """Generate reason for product substitute"""
        reasons = []

        if substitute.get("price", 0) < original.get("price", 0):
            reasons.append("More affordable")

        if substitute.get("rating", 0) > original.get("rating", 0):
            reasons.append("Higher rated")

        if substitute.get("brand") == original.get("brand"):
            reasons.append("Same brand")

        return ", ".join(reasons) if reasons else "Similar product"

    def _calculate_item_sustainability_score(self, product):
        """Calculate sustainability score for individual product"""
        score = 50  # Base score

        # Adjust based on product attributes
        if product.get("organic"):
            score += 20

        if product.get("recycled_packaging"):
            score += 15

        if product.get("local_sourced"):
            score += 10

        if product.get("carbon_neutral"):
            score += 15

        return min(score, 100)

    def _get_sustainability_factors(self, product):
        """Get sustainability factors for a product"""
        factors = []

        if product.get("organic"):
            factors.append("Organic")

        if product.get("recycled_packaging"):
            factors.append("Recycled packaging")

        if product.get("local_sourced"):
            factors.append("Locally sourced")

        if product.get("carbon_neutral"):
            factors.append("Carbon neutral")

        return factors

    def _generate_sustainability_recommendations(self, item_scores):
        """Generate sustainability improvement recommendations"""
        recommendations = []

        low_score_items = [item for item in item_scores if item["score"] < 60]

        if low_score_items:
            recommendations.append(
                {
                    "type": "product_alternatives",
                    "message": f"Consider eco-friendly alternatives for {len(low_score_items)} items",
                    "items": [item["product_id"] for item in low_score_items],
                }
            )

        recommendations.append(
            {
                "type": "general",
                "message": "Choose products with recycled packaging when possible",
            }
        )

        return recommendations

    def _calculate_environmental_impact(self, cart_items):
        """Calculate environmental impact metrics"""
        return {
            "carbon_footprint": "2.5 kg CO2",
            "water_usage": "150 liters",
            "packaging_waste": "0.8 kg",
        }

    def _suggest_green_alternatives(self, cart_items):
        """Suggest green alternatives for cart items"""
        # This would find eco-friendly alternatives
        return []

    def _get_sustainability_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"

    def _generate_speech(self, text, language):
        """Generate speech from text (placeholder)"""
        # In a real implementation, this would use text-to-speech API
        return {"audio_url": "/api/tts/generate", "text": text, "language": language}
