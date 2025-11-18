"""
Unit tests for the authentication system.
Run with: python -m pytest test_auth.py -v
or: python test_auth.py
"""

import unittest
import os
import tempfile
import json
from auth import (
    AuthSystem, 
    UserDatabase, 
    AuthenticationError, 
    ValidationError,
    create_auth_system
)


class TestUserDatabase(unittest.TestCase):
    """Test cases for UserDatabase class."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a temporary file for testing
        self.test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        self.db = UserDatabase(self.test_db_path)
    
    def tearDown(self):
        """Clean up test fixtures after each test."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_db_initialization(self):
        """Test that database is properly initialized."""
        self.assertTrue(os.path.exists(self.test_db_path))
        with open(self.test_db_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, {})
    
    def test_user_exists_false(self):
        """Test user_exists returns False for non-existent user."""
        self.assertFalse(self.db.user_exists("test@example.com"))
    
    def test_save_and_retrieve_user(self):
        """Test saving and retrieving a user."""
        email = "test@example.com"
        password_hash = b"$2b$12$hashedpassword"
        
        self.db.save_user(email, password_hash)
        self.assertTrue(self.db.user_exists(email))
        
        retrieved = self.db.get_user(email)
        self.assertEqual(retrieved, password_hash.decode('utf-8'))
    
    def test_get_nonexistent_user(self):
        """Test retrieving a non-existent user returns None."""
        result = self.db.get_user("nonexistent@example.com")
        self.assertIsNone(result)


class TestEmailValidation(unittest.TestCase):
    """Test cases for email validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        self.auth = AuthSystem(self.test_db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_valid_email(self):
        """Test that valid email passes validation."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com"
        ]
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(self.auth.validate_email(email))
    
    def test_invalid_email_format(self):
        """Test that invalid email formats raise ValidationError."""
        invalid_emails = [
            "invalid",
            "invalid@",
            "@example.com",
            "user@.com",
            "user @example.com",
            "user@example",
            ""
        ]
        for email in invalid_emails:
            with self.subTest(email=email):
                with self.assertRaises(ValidationError):
                    self.auth.validate_email(email)
    
    def test_empty_email(self):
        """Test that empty email raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.auth.validate_email("")
        self.assertIn("cannot be empty", str(context.exception))


class TestPasswordValidation(unittest.TestCase):
    """Test cases for password validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        self.auth = AuthSystem(self.test_db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_valid_password(self):
        """Test that valid passwords pass validation."""
        valid_passwords = [
            "Password123",
            "SecureP@ss1",
            "MyP4ssw0rd!",
            "Test1234Pass"
        ]
        for password in valid_passwords:
            with self.subTest(password=password):
                self.assertTrue(self.auth.validate_password(password))
    
    def test_password_too_short(self):
        """Test that short passwords raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.auth.validate_password("Pass1")
        self.assertIn("at least 8 characters", str(context.exception))
    
    def test_password_no_uppercase(self):
        """Test that passwords without uppercase raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.auth.validate_password("password123")
        self.assertIn("uppercase letter", str(context.exception))
    
    def test_password_no_lowercase(self):
        """Test that passwords without lowercase raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.auth.validate_password("PASSWORD123")
        self.assertIn("lowercase letter", str(context.exception))
    
    def test_password_no_digit(self):
        """Test that passwords without digits raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.auth.validate_password("PasswordOnly")
        self.assertIn("digit", str(context.exception))
    
    def test_empty_password(self):
        """Test that empty password raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.auth.validate_password("")
        self.assertIn("cannot be empty", str(context.exception))


class TestPasswordHashing(unittest.TestCase):
    """Test cases for password hashing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        self.auth = AuthSystem(self.test_db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_hash_password(self):
        """Test that password hashing produces a hash."""
        password = "TestPassword123"
        hashed = self.auth.hash_password(password)
        
        self.assertIsInstance(hashed, bytes)
        self.assertNotEqual(password.encode('utf-8'), hashed)
        self.assertTrue(hashed.startswith(b'$2b$'))
    
    def test_hash_different_each_time(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "TestPassword123"
        hash1 = self.auth.hash_password(password)
        hash2 = self.auth.hash_password(password)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_verify_correct_password(self):
        """Test that correct password verification works."""
        password = "TestPassword123"
        hashed = self.auth.hash_password(password)
        
        self.assertTrue(self.auth.verify_password(password, hashed.decode('utf-8')))
    
    def test_verify_incorrect_password(self):
        """Test that incorrect password verification fails."""
        password = "TestPassword123"
        wrong_password = "WrongPassword123"
        hashed = self.auth.hash_password(password)
        
        self.assertFalse(self.auth.verify_password(wrong_password, hashed.decode('utf-8')))


class TestUserRegistration(unittest.TestCase):
    """Test cases for user registration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        self.auth = AuthSystem(self.test_db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_successful_registration(self):
        """Test successful user registration."""
        success, message = self.auth.register("test@example.com", "Password123")
        
        self.assertTrue(success)
        self.assertEqual(message, "User registered successfully")
        self.assertTrue(self.auth.db.user_exists("test@example.com"))
    
    def test_duplicate_registration(self):
        """Test that registering same email twice fails."""
        email = "test@example.com"
        password = "Password123"
        
        # First registration should succeed
        success1, _ = self.auth.register(email, password)
        self.assertTrue(success1)
        
        # Second registration should fail
        success2, message2 = self.auth.register(email, password)
        self.assertFalse(success2)
        self.assertIn("already exists", message2)
    
    def test_registration_invalid_email(self):
        """Test registration with invalid email fails."""
        success, message = self.auth.register("invalid-email", "Password123")
        
        self.assertFalse(success)
        self.assertIn("email", message.lower())
    
    def test_registration_weak_password(self):
        """Test registration with weak password fails."""
        success, message = self.auth.register("test@example.com", "weak")
        
        self.assertFalse(success)
        self.assertIn("password", message.lower())


class TestUserLogin(unittest.TestCase):
    """Test cases for user login."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        self.auth = AuthSystem(self.test_db_path)
        
        # Register a test user
        self.test_email = "test@example.com"
        self.test_password = "Password123"
        self.auth.register(self.test_email, self.test_password)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_successful_login(self):
        """Test successful login with correct credentials."""
        success, message = self.auth.login(self.test_email, self.test_password)
        
        self.assertTrue(success)
        self.assertEqual(message, "Login successful")
    
    def test_login_wrong_password(self):
        """Test login with wrong password fails."""
        success, message = self.auth.login(self.test_email, "WrongPassword123")
        
        self.assertFalse(success)
        self.assertIn("Invalid", message)
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email fails."""
        success, message = self.auth.login("nonexistent@example.com", "Password123")
        
        self.assertFalse(success)
        self.assertIn("Invalid", message)
    
    def test_login_empty_email(self):
        """Test login with empty email fails."""
        success, message = self.auth.login("", self.test_password)
        
        self.assertFalse(success)
        self.assertIn("required", message.lower())
    
    def test_login_empty_password(self):
        """Test login with empty password fails."""
        success, message = self.auth.login(self.test_email, "")
        
        self.assertFalse(success)
        self.assertIn("required", message.lower())


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def test_create_auth_system(self):
        """Test that create_auth_system returns AuthSystem instance."""
        test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        test_db_path = test_db.name
        test_db.close()
        
        try:
            auth = create_auth_system(test_db_path)
            self.assertIsInstance(auth, AuthSystem)
        finally:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
