"""
Initial schema migration for RetailGenie Firestore database
Creates all necessary collections with proper structure
"""

import logging
from datetime import datetime, timezone

from utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


def migrate():
    """Initialize Firestore collections with proper schema"""
    firebase = FirebaseUtils()

    if not firebase.db:
        logger.error("Firebase not initialized. Cannot run migration.")
        return False

    logger.info("Starting initial schema migration...")

    # Define collections with their initial schema
    collections = {
        "products": {
            "initialized": True,
            "version": "1.0",
            "schema_version": 1,
            "description": "Product catalog with inventory management",
            "fields": {
                "name": "string (required)",
                "price": "number (required)",
                "category": "string",
                "description": "string",
                "in_stock": "boolean",
                "created_at": "timestamp",
                "updated_at": "timestamp",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        "users": {
            "initialized": True,
            "version": "1.0",
            "schema_version": 1,
            "description": "User accounts and authentication",
            "fields": {
                "email": "string (required, unique)",
                "name": "string (required)",
                "role": "string (admin/user)",
                "created_at": "timestamp",
                "last_login": "timestamp",
                "preferences": "object",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        "feedback": {
            "initialized": True,
            "version": "1.0",
            "schema_version": 1,
            "description": "User feedback and reviews",
            "fields": {
                "user_id": "string (required)",
                "product_id": "string",
                "rating": "number (1-5)",
                "comment": "string",
                "type": "string (review/bug/feature)",
                "status": "string (open/resolved)",
                "created_at": "timestamp",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        "orders": {
            "initialized": True,
            "version": "1.0",
            "schema_version": 1,
            "description": "Order management and tracking",
            "fields": {
                "user_id": "string (required)",
                "products": "array (required)",
                "total_amount": "number (required)",
                "status": "string (pending/confirmed/shipped/delivered/cancelled)",
                "payment_status": "string (pending/paid/failed/refunded)",
                "shipping_address": "object",
                "created_at": "timestamp",
                "updated_at": "timestamp",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        "analytics": {
            "initialized": True,
            "version": "1.0",
            "schema_version": 1,
            "description": "Analytics data and metrics",
            "fields": {
                "metric_type": "string (required)",
                "value": "number",
                "metadata": "object",
                "date": "string (YYYY-MM-DD)",
                "created_at": "timestamp",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        "recommendations": {
            "initialized": True,
            "version": "1.0",
            "schema_version": 1,
            "description": "AI-generated product recommendations",
            "fields": {
                "user_id": "string (required)",
                "product_ids": "array (required)",
                "algorithm": "string",
                "confidence_score": "number",
                "context": "object",
                "created_at": "timestamp",
                "expires_at": "timestamp",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        "categories": {
            "initialized": True,
            "version": "1.0",
            "schema_version": 1,
            "description": "Product categories and taxonomy",
            "fields": {
                "name": "string (required)",
                "slug": "string (required, unique)",
                "description": "string",
                "parent_category": "string",
                "image_url": "string",
                "is_active": "boolean",
                "sort_order": "number",
                "created_at": "timestamp",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    created_collections = []
    failed_collections = []

    for collection_name, schema_data in collections.items():
        try:
            logger.info(f"Creating collection: {collection_name}")

            # Create the schema document
            doc_id = firebase.create_document(collection_name, schema_data)

            if doc_id:
                logger.info(
                    f"✅ Collection '{collection_name}' initialized with schema"
                )
                created_collections.append(collection_name)
            else:
                logger.error(f"❌ Failed to create collection: {collection_name}")
                failed_collections.append(collection_name)

        except Exception as e:
            logger.error(f"❌ Error creating collection {collection_name}: {str(e)}")
            failed_collections.append(collection_name)

    # Create migration log
    migration_log = {
        "migration_id": "v1_initial_schema",
        "version": "1.0",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "created_collections": created_collections,
        "failed_collections": failed_collections,
        "total_collections": len(collections),
        "success_count": len(created_collections),
        "failure_count": len(failed_collections),
        "status": "completed" if not failed_collections else "partial_failure",
    }

    try:
        firebase.create_document("_migrations", migration_log)
        logger.info("Migration log saved successfully")
    except Exception as e:
        logger.error(f"Failed to save migration log: {str(e)}")

    # Summary
    logger.info(
        f"""
    🎯 Migration Summary:
    ✅ Successfully created: {len(created_collections)} collections
    ❌ Failed: {len(failed_collections)} collections
    📊 Total: {len(collections)} collections

    Created collections: {', '.join(created_collections) if created_collections else 'None'}
    Failed collections: {', '.join(failed_collections) if failed_collections else 'None'}
    """
    )

    return len(failed_collections) == 0


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
        print("⚠️ Migration completed with errors. Check logs for details.")
        exit(1)
