"""
User Authentication System
This module provides user registration and login functionality with secure password hashing.
"""

import re
import bcrypt
import json
import os
from typing import Dict, Tuple, Optional


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass


class ValidationError(Exception):
    """Custom exception for validation-related errors."""
    pass


class UserDatabase:
    """Simple file-based user database for demonstration purposes."""
    
    def __init__(self, db_file: str = "users.json"):
        """Initialize the user database.
        
        Args:
            db_file: Path to the JSON file storing user data
        """
        self.db_file = db_file
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create the database file if it doesn't exist."""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({}, f)
    
    def user_exists(self, email: str) -> bool:
        """Check if a user with the given email exists.
        
        Args:
            email: User's email address
            
        Returns:
            True if user exists, False otherwise
        """
        users = self._load_users()
        return email in users
    
    def save_user(self, email: str, hashed_password: bytes):
        """Save a new user to the database.
        
        Args:
            email: User's email address
            hashed_password: Bcrypt hashed password
        """
        users = self._load_users()
        users[email] = hashed_password.decode('utf-8')
        self._save_users(users)
    
    def get_user(self, email: str) -> Optional[str]:
        """Retrieve a user's hashed password.
        
        Args:
            email: User's email address
            
        Returns:
            Hashed password or None if user doesn't exist
        """
        users = self._load_users()
        return users.get(email)
    
    def _load_users(self) -> Dict[str, str]:
        """Load users from the database file."""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_users(self, users: Dict[str, str]):
        """Save users to the database file."""
        with open(self.db_file, 'w') as f:
            json.dump(users, f, indent=2)


class AuthSystem:
    """Main authentication system class."""
    
    def __init__(self, db_file: str = "users.json"):
        """Initialize the authentication system.
        
        Args:
            db_file: Path to the user database file
        """
        self.db = UserDatabase(db_file)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format using regex.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid
            
        Raises:
            ValidationError: If email format is invalid
        """
        if not email:
            raise ValidationError("Email cannot be empty")
        
        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        return True
    
    def validate_password(self, password: str) -> bool:
        """Validate password strength.
        
        Password requirements:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit
        
        Args:
            password: Password to validate
            
        Returns:
            True if password is valid
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if not password:
            raise ValidationError("Password cannot be empty")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit")
        
        return True
    
    def hash_password(self, password: str) -> bytes:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as bytes
        """
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def register(self, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate email
            self.validate_email(email)
            
            # Validate password
            self.validate_password(password)
            
            # Check if user already exists
            if self.db.user_exists(email):
                raise ValidationError("User with this email already exists")
            
            # Hash password and save user
            hashed_password = self.hash_password(password)
            self.db.save_user(email, hashed_password)
            
            return True, "User registered successfully"
            
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Authenticate a user.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate inputs
            if not email or not password:
                raise AuthenticationError("Email and password are required")
            
            # Check if user exists
            if not self.db.user_exists(email):
                raise AuthenticationError("Invalid email or password")
            
            # Get stored password hash
            stored_hash = self.db.get_user(email)
            if not stored_hash:
                raise AuthenticationError("Invalid email or password")
            
            # Verify password
            if not self.verify_password(password, stored_hash):
                raise AuthenticationError("Invalid email or password")
            
            return True, "Login successful"
            
        except AuthenticationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Login failed: {str(e)}"


# Convenience functions for easy usage
def create_auth_system(db_file: str = "users.json") -> AuthSystem:
    """Create and return an AuthSystem instance.
    
    Args:
        db_file: Path to the user database file
        
    Returns:
        AuthSystem instance
    """
    return AuthSystem(db_file)


if __name__ == "__main__":
    # Example usage
    auth = create_auth_system("test_users.json")
    
    # Register a user
    success, message = auth.register("user@example.com", "SecurePass123")
    print(f"Registration: {message}")
    
    # Try to login
    success, message = auth.login("user@example.com", "SecurePass123")
    print(f"Login: {message}")
    
    # Clean up test file
    if os.path.exists("test_users.json"):
        os.remove("test_users.json")
