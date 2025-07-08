"""
Add user preferences and settings schema
Version: v2
Created: 2025-06-29T16:30:00Z
"""

import logging
from datetime import datetime, timezone

from utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


def migrate():
    """Execute the migration - Add user preferences schema"""
    firebase = FirebaseUtils()

    if not firebase.db:
        logger.error("Firebase not initialized. Cannot run migration.")
        return False

    logger.info("Starting migration: Add user preferences")

    try:
        # Create user_preferences collection schema
        preferences_schema = {
            "initialized": True,
            "version": "2.0",
            "schema_version": 2,
            "description": "User preferences and personalization settings",
            "fields": {
                "user_id": "string (required, unique)",
                "theme": "string (light/dark/auto)",
                "language": "string (en/es/fr/de)",
                "currency": "string (USD/EUR/GBP)",
                "notification_preferences": "object",
                "privacy_settings": "object",
                "ai_recommendations_enabled": "boolean",
                "marketing_emails": "boolean",
                "created_at": "timestamp",
                "updated_at": "timestamp",
            },
            "indexes": ["user_id", "theme", "language"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Create the preferences collection
        doc_id = firebase.create_document("user_preferences", preferences_schema)

        if doc_id:
            logger.info("✅ Created user_preferences collection schema")
        else:
            raise Exception("Failed to create user_preferences collection")

        # Update users collection to include preferences reference
        users_docs = firebase.get_documents("users")
        updated_count = 0

        for user_doc in users_docs:
            if "preferences_id" not in user_doc:
                # Add preferences reference to existing users
                update_data = {
                    "preferences_id": None,  # Will be set when user creates preferences
                    "preferences_created": False,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }

                success = firebase.update_document("users", user_doc["id"], update_data)
                if success:
                    updated_count += 1

        logger.info(f"✅ Updated {updated_count} existing user documents")

        # Create default notification types collection
        notification_types_schema = {
            "initialized": True,
            "version": "2.0",
            "schema_version": 2,
            "description": "Available notification types and settings",
            "notification_types": [
                {
                    "type": "order_updates",
                    "name": "Order Updates",
                    "description": "Notifications about order status changes",
                    "default_enabled": True,
                    "channels": ["email", "push"],
                },
                {
                    "type": "product_recommendations",
                    "name": "Product Recommendations",
                    "description": "AI-powered product suggestions",
                    "default_enabled": True,
                    "channels": ["email", "in_app"],
                },
                {
                    "type": "price_alerts",
                    "name": "Price Alerts",
                    "description": "Notifications when watched products go on sale",
                    "default_enabled": False,
                    "channels": ["email", "push"],
                },
                {
                    "type": "newsletter",
                    "name": "Newsletter",
                    "description": "Weekly newsletter with trends and offers",
                    "default_enabled": False,
                    "channels": ["email"],
                },
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        doc_id = firebase.create_document(
            "notification_types", notification_types_schema
        )

        if doc_id:
            logger.info("✅ Created notification_types collection")
        else:
            logger.warning("Failed to create notification_types collection")

        logger.info("✅ Migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False


def rollback():
    """Rollback the migration"""
    firebase = FirebaseUtils()

    if not firebase.db:
        logger.error("Firebase not initialized. Cannot rollback migration.")
        return False

    logger.info("Starting rollback: Remove user preferences")

    try:
        # Remove preferences-related fields from users
        users_docs = firebase.get_documents("users")
        rollback_count = 0

        for user_doc in users_docs:
            if "preferences_id" in user_doc or "preferences_created" in user_doc:
                # Remove the added fields
                # Note: Firestore doesn't support field deletion via update
                # This is a simplified rollback - in production, you might need
                # to recreate documents without the unwanted fields
                logger.info(
                    f"Would rollback user document: {user_doc.get('id', 'unknown')}"
                )
                rollback_count += 1

        logger.info(f"✅ Would rollback {rollback_count} user documents")

        # In a real rollback, you might want to:
        # 1. Delete the user_preferences collection
        # 2. Delete the notification_types collection
        # 3. Remove added fields from users (requires document recreation)

        logger.warning("⚠️ Full rollback requires manual cleanup of collections")
        logger.info(
            "Collections to manually delete: user_preferences, notification_types"
        )

        return True

    except Exception as e:
        logger.error(f"❌ Rollback failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    success = migrate()
    if success:
        print("🎉 Migration completed successfully!")
        exit(0)
    else:
        print("⚠️ Migration failed. Check logs for details.")
        exit(1)
