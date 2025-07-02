import logging

from app.controllers.ai_engine import AIEngine
from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class ProductController:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.firebase = FirebaseUtils()
        self.collection_name = "products"

    def get_products(self, filters=None):
        """
        Retrieve products with optional filters

        Args:
            filters (dict): Optional filters for products

        Returns:
            list: List of products
        """
        try:
            products = self.firebase.get_documents(self.collection_name, filters)
            return products
        except Exception as e:
            logger.error(f"Error retrieving products: {str(e)}")
            raise

    def get_product_by_id(self, product_id):
        """
        Retrieve a specific product by ID

        Args:
            product_id (str): Product ID

        Returns:
            dict: Product data or None if not found
        """
        try:
            product = self.firebase.get_document(self.collection_name, product_id)
            return product
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
            raise

    def search_products(self, query):
        """
        Search products using AI-powered search

        Args:
            query (str): Search query

        Returns:
            list: List of matching products
        """
        try:
            # Get all products first
            all_products = self.firebase.get_documents(self.collection_name)

            # Use AI engine to perform intelligent search
            search_results = self.ai_engine.search_products(query, all_products)

            return search_results
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            raise

    def get_recommendations(self, user_preferences):
        """
        Get AI-powered product recommendations

        Args:
            user_preferences (dict): User preferences and history

        Returns:
            list: List of recommended products
        """
        try:
            # Get all products
            all_products = self.firebase.get_documents(self.collection_name)

            # Use AI engine to generate recommendations
            recommendations = self.ai_engine.generate_recommendations(
                user_preferences, all_products
            )

            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise

    def create_product(self, product_data):
        """
        Create a new product

        Args:
            product_data (dict): Product information

        Returns:
            str: Product ID
        """
        try:
            # Validate required fields
            required_fields = ["name", "description", "price", "category"]
            for field in required_fields:
                if field not in product_data:
                    raise ValueError(f"Missing required field: {field}")

            # Add AI-generated tags and features
            enhanced_data = self.ai_engine.enhance_product_data(product_data)

            # Save to Firebase
            product_id = self.firebase.create_document(
                self.collection_name, enhanced_data
            )

            return product_id
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    def update_product(self, product_id, update_data):
        """
        Update an existing product

        Args:
            product_id (str): Product ID
            update_data (dict): Fields to update

        Returns:
            bool: Success status
        """
        try:
            # Check if product exists
            existing_product = self.firebase.get_document(
                self.collection_name, product_id
            )
            if not existing_product:
                raise ValueError("Product not found")

            # Update the product
            success = self.firebase.update_document(
                self.collection_name, product_id, update_data
            )

            return success
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise

    def delete_product(self, product_id):
        """
        Delete a product

        Args:
            product_id (str): Product ID

        Returns:
            bool: Success status
        """
        try:
            success = self.firebase.delete_document(self.collection_name, product_id)
            return success
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise
