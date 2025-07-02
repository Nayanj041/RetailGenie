import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class FirebaseUtils:
    def __init__(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Initialize Firebase
                cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                
                if cred_path and os.path.exists(cred_path):
                    # Use service account key file
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized with service account file")
                elif os.getenv("FIREBASE_PROJECT_ID"):
                    # Use environment variables to create credentials
                    firebase_config = {
                        "type": "service_account",
                        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                        "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
                        "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
                        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
                        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                    }
                    
                    # Filter out None values
                    firebase_config = {k: v for k, v in firebase_config.items() if v is not None}
                    
                    if len(firebase_config) >= 4:  # Minimum required fields
                        cred = credentials.Certificate(firebase_config)
                        firebase_admin.initialize_app(cred)
                        logger.info("Firebase initialized with environment variables")
                    else:
                        raise ValueError("Insufficient Firebase configuration in environment variables")
                else:
                    # Try default credentials (for Google Cloud environment)
                    firebase_admin.initialize_app()
                    logger.info("Firebase initialized with default credentials")

            # Get Firestore client
            self.db = firestore.client()
            logger.info("Firestore client created successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            # Create a mock database for development/testing
            self.db = None
            self._mock_data = {}
            logger.warning("Using mock database - Firebase not available")

    def create_document(
        self,
        collection_name: str,
        data: Dict[str, Any],
        document_id: Optional[str] = None,
    ) -> str:
        """
        Create a new document in Firestore

        Args:
            collection_name (str): Name of the collection
            data (Dict[str, Any]): Document data
            document_id (str, optional): Custom document ID

        Returns:
            str: Document ID
        """
        try:
            if self.db:
                # Use Firestore
                if document_id:
                    doc_ref = self.db.collection(collection_name).document(document_id)
                    doc_ref.set(data)
                    return document_id
                else:
                    doc_ref = self.db.collection(collection_name).add(data)
                    if isinstance(doc_ref, tuple):
                        return doc_ref[1].id
                    return doc_ref.id
            else:
                # Use mock database
                import uuid

                doc_id = document_id or str(uuid.uuid4())

                if collection_name not in self._mock_data:
                    self._mock_data[collection_name] = {}

                data_with_id = data.copy()
                data_with_id["id"] = doc_id
                self._mock_data[collection_name][doc_id] = data_with_id

                return doc_id

        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise

    def get_document(
        self, collection_name: str, document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID

        Args:
            collection_name (str): Name of the collection
            document_id (str): Document ID

        Returns:
            Optional[Dict[str, Any]]: Document data or None if not found
        """
        try:
            if self.db:
                # Use Firestore
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc = doc_ref.get()

                if doc.exists:
                    data = doc.to_dict()
                    data["id"] = doc.id
                    return data
                return None
            else:
                # Use mock database
                if collection_name in self._mock_data:
                    return self._mock_data[collection_name].get(document_id)
                return None

        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise

    def get_documents(
        self,
        collection_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get documents from a collection with optional filters

        Args:
            collection_name (str): Name of the collection
            filters (Dict[str, Any], optional): Filters to apply
            limit (int, optional): Maximum number of documents to return
            order_by (str, optional): Field to order by

        Returns:
            List[Dict[str, Any]]: List of documents
        """
        try:
            if self.db:
                # Use Firestore
                query = self.db.collection(collection_name)

                # Apply filters
                if filters:
                    for field, value in filters.items():
                        query = query.where(field, "==", value)

                # Apply ordering
                if order_by:
                    query = query.order_by(order_by)

                # Apply limit
                if limit:
                    query = query.limit(limit)

                docs = query.stream()
                result = []

                for doc in docs:
                    data = doc.to_dict()
                    data["id"] = doc.id
                    result.append(data)

                return result
            else:
                # Use mock database
                if collection_name not in self._mock_data:
                    return []

                documents = list(self._mock_data[collection_name].values())

                # Apply filters
                if filters:
                    filtered_docs = []
                    for doc in documents:
                        match = True
                        for field, value in filters.items():
                            if doc.get(field) != value:
                                match = False
                                break
                        if match:
                            filtered_docs.append(doc)
                    documents = filtered_docs

                # Apply ordering (simple implementation)
                if order_by:
                    documents.sort(key=lambda x: x.get(order_by, ""))

                # Apply limit
                if limit:
                    documents = documents[:limit]

                return documents

        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            raise

    def update_document(
        self, collection_name: str, document_id: str, data: Dict[str, Any]
    ) -> bool:
        """
        Update a document

        Args:
            collection_name (str): Name of the collection
            document_id (str): Document ID
            data (Dict[str, Any]): Data to update

        Returns:
            bool: Success status
        """
        try:
            if self.db:
                # Use Firestore
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc_ref.update(data)
                return True
            else:
                # Use mock database
                if (
                    collection_name in self._mock_data
                    and document_id in self._mock_data[collection_name]
                ):
                    self._mock_data[collection_name][document_id].update(data)
                    return True
                return False

        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False

    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """
        Delete a document

        Args:
            collection_name (str): Name of the collection
            document_id (str): Document ID

        Returns:
            bool: Success status
        """
        try:
            if self.db:
                # Use Firestore
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc_ref.delete()
                return True
            else:
                # Use mock database
                if (
                    collection_name in self._mock_data
                    and document_id in self._mock_data[collection_name]
                ):
                    del self._mock_data[collection_name][document_id]
                    return True
                return False

        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False

    def query_documents(
        self,
        collection_name: str,
        field: str,
        operator: str,
        value: Any,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query documents with specific conditions

        Args:
            collection_name (str): Name of the collection
            field (str): Field to query
            operator (str): Query operator ('==', '>', '<', '>=', '<=', '!=', 'in', 'array-contains')
            value (Any): Value to compare
            limit (int, optional): Maximum number of documents to return

        Returns:
            List[Dict[str, Any]]: List of matching documents
        """
        try:
            if self.db:
                # Use Firestore
                query = self.db.collection(collection_name).where(
                    field, operator, value
                )

                if limit:
                    query = query.limit(limit)

                docs = query.stream()
                result = []

                for doc in docs:
                    data = doc.to_dict()
                    data["id"] = doc.id
                    result.append(data)

                return result
            else:
                # Use mock database (simplified implementation)
                if collection_name not in self._mock_data:
                    return []

                documents = list(self._mock_data[collection_name].values())
                result = []

                for doc in documents:
                    field_value = doc.get(field)

                    if operator == "==" and field_value == value:
                        result.append(doc)
                    elif operator == ">" and field_value and field_value > value:
                        result.append(doc)
                    elif operator == "<" and field_value and field_value < value:
                        result.append(doc)
                    elif operator == ">=" and field_value and field_value >= value:
                        result.append(doc)
                    elif operator == "<=" and field_value and field_value <= value:
                        result.append(doc)
                    elif operator == "!=" and field_value != value:
                        result.append(doc)
                    elif operator == "in" and field_value in value:
                        result.append(doc)
                    elif (
                        operator == "array-contains"
                        and isinstance(field_value, list)
                        and value in field_value
                    ):
                        result.append(doc)

                if limit:
                    result = result[:limit]

                return result

        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            raise

    def batch_write(self, operations: List[Dict[str, Any]]) -> bool:
        """
        Perform batch write operations

        Args:
            operations (List[Dict[str, Any]]): List of operations
                Each operation should have:
                - 'type': 'create', 'update', or 'delete'
                - 'collection': collection name
                - 'document_id': document ID
                - 'data': data (for create/update operations)

        Returns:
            bool: Success status
        """
        try:
            if self.db:
                # Use Firestore batch
                batch = self.db.batch()

                for operation in operations:
                    op_type = operation.get("type")
                    collection = operation.get("collection")
                    doc_id = operation.get("document_id")
                    data = operation.get("data", {})

                    doc_ref = self.db.collection(collection).document(doc_id)

                    if op_type == "create":
                        batch.set(doc_ref, data)
                    elif op_type == "update":
                        batch.update(doc_ref, data)
                    elif op_type == "delete":
                        batch.delete(doc_ref)

                batch.commit()
                return True
            else:
                # Use mock database
                for operation in operations:
                    op_type = operation.get("type")
                    collection = operation.get("collection")
                    doc_id = operation.get("document_id")
                    data = operation.get("data", {})

                    if op_type == "create":
                        self.create_document(collection, data, doc_id)
                    elif op_type == "update":
                        self.update_document(collection, doc_id, data)
                    elif op_type == "delete":
                        self.delete_document(collection, doc_id)

                return True

        except Exception as e:
            logger.error(f"Error in batch write: {str(e)}")
            return False

    def get_documents_paginated(
        self,
        collection_name: str,
        page: int = 1,
        per_page: int = 20,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get documents with pagination support

        Args:
            collection_name (str): Name of the collection
            page (int): Page number (1-based)
            per_page (int): Number of documents per page
            order_by (str, optional): Field to order by
            filters (Dict[str, Any], optional): Filters to apply

        Returns:
            Dict containing documents, pagination info, and metadata
        """
        try:
            if self.db:
                query = self.db.collection(collection_name)

                # Apply filters
                if filters:
                    for field, value in filters.items():
                        query = query.where(field, "==", value)

                # Apply ordering
                if order_by:
                    query = query.order_by(order_by)

                # Get total count (for pagination metadata)
                total_docs = len(list(query.stream()))

                # Apply pagination
                offset = (page - 1) * per_page
                query = query.offset(offset).limit(per_page)

                # Execute query
                docs = query.stream()
                documents = []
                for doc in docs:
                    doc_dict = doc.to_dict()
                    doc_dict["id"] = doc.id
                    documents.append(doc_dict)

                total_pages = (total_docs + per_page - 1) // per_page

                return {
                    "documents": documents,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_documents": total_docs,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_prev": page > 1,
                    },
                }
            else:
                # Mock implementation
                mock_data = self._mock_data.get(collection_name, [])
                offset = (page - 1) * per_page
                paginated_data = mock_data[offset : offset + per_page]

                return {
                    "documents": paginated_data,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_documents": len(mock_data),
                        "total_pages": (len(mock_data) + per_page - 1) // per_page,
                        "has_next": offset + per_page < len(mock_data),
                        "has_prev": page > 1,
                    },
                }
        except Exception as e:
            logger.error(f"Error getting paginated documents: {e}")
            return {
                "documents": [],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_documents": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False,
                },
            }

    def search_documents(
        self,
        collection_name: str,
        search_field: str,
        search_value: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search documents by field value

        Args:
            collection_name (str): Name of the collection
            search_field (str): Field to search in
            search_value (str): Value to search for
            limit (int): Maximum number of results

        Returns:
            List of matching documents
        """
        try:
            if self.db:
                # Note: Firestore doesn't support full-text search natively
                # This is a simple field match search
                docs = (
                    self.db.collection(collection_name)
                    .where(search_field, ">=", search_value)
                    .where(search_field, "<=", search_value + "\uf8ff")
                    .limit(limit)
                    .stream()
                )

                documents = []
                for doc in docs:
                    doc_dict = doc.to_dict()
                    doc_dict["id"] = doc.id
                    documents.append(doc_dict)

                return documents
            else:
                # Mock implementation
                mock_data = self._mock_data.get(collection_name, [])
                return [
                    doc
                    for doc in mock_data
                    if search_value.lower() in str(doc.get(search_field, "")).lower()
                ][:limit]

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a collection

        Args:
            collection_name (str): Name of the collection

        Returns:
            Dict containing collection statistics
        """
        try:
            if self.db:
                docs = list(self.db.collection(collection_name).stream())

                return {
                    "total_documents": len(docs),
                    "collection_name": collection_name,
                    "last_updated": datetime.now().isoformat(),
                }
            else:
                mock_data = self._mock_data.get(collection_name, [])
                return {
                    "total_documents": len(mock_data),
                    "collection_name": collection_name,
                    "last_updated": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "collection_name": collection_name,
                "error": str(e),
            }

    def batch_create_documents(
        self, collection_name: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple documents in a batch operation

        Args:
            collection_name (str): Name of the collection
            documents (List[Dict[str, Any]]): List of documents to create

        Returns:
            Dict containing batch operation results
        """
        try:
            if self.db:
                batch = self.db.batch()
                doc_ids = []

                for doc_data in documents:
                    doc_ref = self.db.collection(collection_name).document()
                    batch.set(doc_ref, doc_data)
                    doc_ids.append(doc_ref.id)

                batch.commit()

                return {
                    "success": True,
                    "created_count": len(doc_ids),
                    "document_ids": doc_ids,
                }
            else:
                # Mock implementation
                if collection_name not in self._mock_data:
                    self._mock_data[collection_name] = []

                doc_ids = []
                for doc_data in documents:
                    doc_id = f"mock-{len(self._mock_data[collection_name])}"
                    doc_data["id"] = doc_id
                    self._mock_data[collection_name].append(doc_data)
                    doc_ids.append(doc_id)

                return {
                    "success": True,
                    "created_count": len(doc_ids),
                    "document_ids": doc_ids,
                }
        except Exception as e:
            logger.error(f"Error in batch create: {e}")
            return {"success": False, "error": str(e), "created_count": 0}

    def test_connection(self) -> bool:
        """
        Test the Firebase connection

        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            if self.db:
                # Try to read from a test collection
                list(self.db.collection("connection_test").limit(1).stream())
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    @property
    def project_id(self) -> Optional[str]:
        """Get the Firebase project ID"""
        try:
            if firebase_admin._apps:
                app = firebase_admin.get_app()
                return app.project_id
            return None
        except Exception:
            return None
