import logging
from datetime import datetime

from app.controllers.ai_engine import AIEngine
from app.utils.email_utils import EmailUtils
from app.utils.firebase_utils import FirebaseUtils
from app.utils.pdf_utils import PDFUtils

logger = logging.getLogger(__name__)


class FeedbackController:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.firebase = FirebaseUtils()
        self.pdf_utils = PDFUtils()
        self.email_utils = EmailUtils()
        self.collection_name = "feedback"

    def submit_feedback(self, feedback_data):
        """
        Submit user feedback

        Args:
            feedback_data (dict): Feedback information

        Returns:
            str: Feedback ID
        """
        try:
            # Validate required fields
            required_fields = ["user_id", "product_id", "rating", "comment"]
            for field in required_fields:
                if field not in feedback_data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate rating range
            rating = feedback_data.get("rating")
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")

            # Add timestamp and AI sentiment analysis
            feedback_data["timestamp"] = datetime.now().isoformat()
            feedback_data["sentiment"] = self.ai_engine.analyze_sentiment(
                feedback_data["comment"]
            )

            # Save to Firebase
            feedback_id = self.firebase.create_document(
                self.collection_name, feedback_data
            )

            # Send notification email if rating is low
            if rating <= 2:
                self._send_low_rating_notification(feedback_data)

            return feedback_id
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            raise

    def get_product_feedback(self, product_id):
        """
        Get all feedback for a specific product

        Args:
            product_id (str): Product ID

        Returns:
            list: List of feedback entries
        """
        try:
            filters = {"product_id": product_id}
            feedback = self.firebase.get_documents(self.collection_name, filters)

            # Sort by timestamp (newest first)
            feedback.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return feedback
        except Exception as e:
            logger.error(f"Error retrieving product feedback: {str(e)}")
            raise

    def get_user_feedback(self, user_id):
        """
        Get all feedback submitted by a specific user

        Args:
            user_id (str): User ID

        Returns:
            list: List of feedback entries
        """
        try:
            filters = {"user_id": user_id}
            feedback = self.firebase.get_documents(self.collection_name, filters)

            # Sort by timestamp (newest first)
            feedback.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return feedback
        except Exception as e:
            logger.error(f"Error retrieving user feedback: {str(e)}")
            raise

    def analyze_feedback(self, product_id):
        """
        Analyze feedback for a product using AI

        Args:
            product_id (str): Product ID

        Returns:
            dict: Analysis results
        """
        try:
            # Get all feedback for the product
            feedback = self.get_product_feedback(product_id)

            if not feedback:
                return {
                    "total_reviews": 0,
                    "average_rating": 0,
                    "sentiment_analysis": {},
                    "key_themes": [],
                    "recommendations": [],
                }

            # Perform AI analysis
            analysis = self.ai_engine.analyze_feedback(feedback)

            # Calculate basic statistics
            total_reviews = len(feedback)
            average_rating = sum(f.get("rating", 0) for f in feedback) / total_reviews

            # Combine results
            analysis.update(
                {
                    "total_reviews": total_reviews,
                    "average_rating": round(average_rating, 2),
                    "analysis_timestamp": datetime.now().isoformat(),
                }
            )

            return analysis
        except Exception as e:
            logger.error(f"Error analyzing feedback: {str(e)}")
            raise

    def export_feedback_report(self, product_id):
        """
        Export feedback as PDF report

        Args:
            product_id (str): Product ID

        Returns:
            str: PDF file path
        """
        try:
            # Get feedback and analysis
            feedback = self.get_product_feedback(product_id)
            analysis = self.analyze_feedback(product_id)

            # Generate PDF report
            pdf_path = self.pdf_utils.generate_feedback_report(
                product_id, feedback, analysis
            )

            return pdf_path
        except Exception as e:
            logger.error(f"Error exporting feedback report: {str(e)}")
            raise

    def get_feedback_summary(self, product_id=None, user_id=None):
        """
        Get feedback summary with statistics

        Args:
            product_id (str, optional): Product ID
            user_id (str, optional): User ID

        Returns:
            dict: Summary statistics
        """
        try:
            filters = {}
            if product_id:
                filters["product_id"] = product_id
            if user_id:
                filters["user_id"] = user_id

            feedback = self.firebase.get_documents(self.collection_name, filters)

            if not feedback:
                return {
                    "total_feedback": 0,
                    "average_rating": 0,
                    "rating_distribution": {},
                    "sentiment_distribution": {},
                }

            # Calculate statistics
            total_feedback = len(feedback)
            average_rating = sum(f.get("rating", 0) for f in feedback) / total_feedback

            # Rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[str(i)] = len(
                    [f for f in feedback if f.get("rating") == i]
                )

            # Sentiment distribution
            sentiment_distribution = {}
            for f in feedback:
                sentiment = f.get("sentiment", "neutral")
                sentiment_distribution[sentiment] = (
                    sentiment_distribution.get(sentiment, 0) + 1
                )

            return {
                "total_feedback": total_feedback,
                "average_rating": round(average_rating, 2),
                "rating_distribution": rating_distribution,
                "sentiment_distribution": sentiment_distribution,
            }
        except Exception as e:
            logger.error(f"Error getting feedback summary: {str(e)}")
            raise

    def _send_low_rating_notification(self, feedback_data):
        """
        Send notification email for low ratings

        Args:
            feedback_data (dict): Feedback data
        """
        try:
            subject = f"Low Rating Alert - Product {feedback_data['product_id']}"
            body = f"""
            A low rating ({feedback_data['rating']}/5) has been received for product {feedback_data['product_id']}.

            User: {feedback_data['user_id']}
            Comment: {feedback_data['comment']}
            Timestamp: {feedback_data['timestamp']}

            Please review and take appropriate action.
            """

            # Send to admin email (configured in settings)
            self.email_utils.send_notification(subject, body)
        except Exception as e:
            logger.warning(f"Failed to send low rating notification: {str(e)}")
