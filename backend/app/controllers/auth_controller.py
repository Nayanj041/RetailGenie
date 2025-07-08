import logging
import os
from datetime import datetime, timedelta

import bcrypt
import jwt

from app.models.user_model import User
from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class AuthController:
    def __init__(self):
        self.firebase = FirebaseUtils()
        self.collection_name = "users"
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-here")

    def register_user(self, user_data):
        """
        Register a new user

        Args:
            user_data (dict): User registration data

        Returns:
            dict: User data with token
        """
        try:
            email = user_data.get("email")
            password = user_data.get("password")
            name = user_data.get("name")

            # Check if user already exists
            existing_users = self.firebase.query_documents(
                self.collection_name, "email", "==", email
            )

            if existing_users:
                raise ValueError("User with this email already exists")

            # Hash password
            hashed_password = self._hash_password(password)

            # Create user data
            user_dict = {
                "email": email,
                "name": name,
                "password": hashed_password,
                "role": "user",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            # Save to Firebase
            user_id = self.firebase.create_document(self.collection_name, user_dict)

            # Generate JWT token
            token = self._generate_token(user_id, email, user_dict.get("role", "user"))

            # Remove password from response
            user_dict.pop("password", None)
            user_dict["id"] = user_id

            return {"user": user_dict, "token": token}
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise

    def login_user(self, email, password):
        """
        User login

        Args:
            email (str): User email
            password (str): User password

        Returns:
            dict: User data with token
        """
        try:
            # Find user by email
            users = self.firebase.query_documents(
                self.collection_name, "email", "==", email
            )

            if not users:
                raise ValueError("Invalid email or password")

            user_data = users[0]

            # Verify password
            if not self._verify_password(password, user_data.get("password")):
                raise ValueError("Invalid email or password")

            # Check if user is active
            if not user_data.get("is_active", True):
                raise ValueError("Account is deactivated")

            # Generate JWT token
            token = self._generate_token(
                user_data.get("id"), email, user_data.get("role", "user")
            )

            # Remove password from response
            user_data.pop("password", None)

            # Update last login
            self.firebase.update_document(
                self.collection_name,
                user_data.get("id"),
                {"last_login": datetime.utcnow().isoformat()},
            )

            return {"user": user_data, "token": token}
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            raise

            # Generate JWT token
            token = self._generate_token(user_data["id"], email)

            # Update last login
            self.firebase.update_document(
                self.collection_name,
                user_data["id"],
                {"last_login": datetime.now().isoformat()},
            )

            # Remove password from response
            user_data.pop("password", None)

            return {"user": user_data, "token": token}
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            raise

    def logout_user(self, token):
        """
        User logout (invalidate token)

        Args:
            token (str): JWT token
        """
        try:
            # In a production system, you would maintain a blacklist of tokens
            # For now, we'll just validate the token
            self._verify_token(token)

            # Could add token to blacklist here
            logger.info("User logged out successfully")
        except Exception as e:
            logger.error(f"Error logging out user: {str(e)}")
            raise

    def get_user_profile(self, token):
        """
        Get user profile from token

        Args:
            token (str): JWT token

        Returns:
            dict: User profile data
        """
        try:
            # Verify and decode token
            payload = self._verify_token(token)
            user_id = payload.get("user_id")

            # Get user data
            user_data = self.firebase.get_document(self.collection_name, user_id)

            if not user_data:
                raise ValueError("User not found")

            # Remove sensitive data
            user_data.pop("password", None)

            return user_data
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    def update_user_profile(self, token, update_data):
        """
        Update user profile

        Args:
            token (str): JWT token
            update_data (dict): Data to update

        Returns:
            dict: Updated user profile
        """
        try:
            # Verify token and get user ID
            payload = self._verify_token(token)
            user_id = payload.get("user_id")

            # Remove sensitive fields that shouldn't be updated this way
            sensitive_fields = ["password", "email", "id", "created_at"]
            for field in sensitive_fields:
                update_data.pop(field, None)

            # Add update timestamp
            update_data["updated_at"] = datetime.now().isoformat()

            # Update user data
            success = self.firebase.update_document(
                self.collection_name, user_id, update_data
            )

            if not success:
                raise ValueError("Failed to update profile")

            # Get updated user data
            updated_user = self.firebase.get_document(self.collection_name, user_id)
            updated_user.pop("password", None)

            return updated_user
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise

    def change_password(self, token, old_password, new_password):
        """
        Change user password

        Args:
            token (str): JWT token
            old_password (str): Current password
            new_password (str): New password

        Returns:
            bool: Success status
        """
        try:
            # Verify token and get user
            payload = self._verify_token(token)
            user_id = payload.get("user_id")

            user_data = self.firebase.get_document(self.collection_name, user_id)

            if not user_data:
                raise ValueError("User not found")

            # Verify old password
            if not self._verify_password(old_password, user_data.get("password")):
                raise ValueError("Current password is incorrect")

            # Hash new password
            hashed_password = self._hash_password(new_password)

            # Update password
            success = self.firebase.update_document(
                self.collection_name,
                user_id,
                {
                    "password": hashed_password,
                    "password_updated_at": datetime.now().isoformat(),
                },
            )

            return success
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise

    def _hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def _verify_password(self, password, hashed_password):
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    def _generate_token(self, user_id, email, role="user"):
        """Generate JWT token"""
        try:
            payload = {
                "user_id": user_id,
                "email": email,
                "role": role,
                "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
                "iat": datetime.utcnow(),
            }

            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            return token
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise

    def _verify_token(self, token):
        """Verify and decode JWT token"""
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise ValueError("Token verification failed")
