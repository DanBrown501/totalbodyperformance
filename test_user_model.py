"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

# Set an environmental variable to use a different database for tests 
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

    def tearDown(self):
        """Tear down after tests are completed"""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        # Create a test user
        u = User.register("testing1", "password", "testing1@test.com", "John", "Doe", None)
        u.id = 1111

        db.session.commit()

        u1 = User.query.get(1111)

        # User should have no comments and no favorite exercises and meals.
        self.assertEqual(len(u.exercise_comments), 0)
        self.assertEqual(len(u.user_exercises), 0)

    def test_repr_method(self):
        """Does repr method work?"""

        # Create a test user
        u = User.register("testing1", "password", "testing1@test.com", "John", "Doe", None)
        u.id = 1111
         

        db.session.commit()

        u1 = User.query.get(1111)
        self.u1 = u1

        self.assertEqual(str(self.u1), f"<{self.u1.username}: {self.u1.first_name} {self.u1.last_name} - {self.u1.email}>")

    ####
    # Registration Tests
    ####
    def test_valid_registration(self):
        """Does registration work?"""
        
        u_test = User.register("testtesttest", "password", "testtest@test.com", "John", "Doe" , None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)

        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertEqual(u_test.first_name, "John")
        self.assertEqual(u_test.last_name, "Doe")
        # Test password is not actually "password"
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_registration(self):
        """ Does invalid registration return error as expected?"""

        invalid = User.register(None, "password", "test@test.com", "John", "Doe", None)
        uid = 123456789
        invalid.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_registration(self):
        """ Does invalid registration return error as expected?"""

        invalid = User.register("testtest", "password", None, "John", "Doe", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_registration(self):
        """ Does invalid registration return error as expected?"""

        with self.assertRaises(ValueError) as context:
            User.register("testtest", "", "email@email.com", "John", "Doe", None)
        
        with self.assertRaises(ValueError) as context:
            User.register("testtest", None, "email@email.com", "John", "Doe", None)

    def test_invalid_first_name_signup(self):
        """ Does invalid registration return error as expected?"""
        
        invalid = User.register("testtest", "password", "test@test.com", None, "Doe", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_last_name_signup(self):
        """ Does invalid registration return error as expected?"""
        
        invalid = User.register("testtest", "password", "test@test.com", "John", None, None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    ####
    # Authentication Tests
    ####

    def test_valid_authentication(self):
        """Does log in work?"""

        # Create a test user
        user = User.register("testing1", "password", "testing1@test.com", "John", "Doe", None)
        user.id = 1111

        db.session.commit()

        u1 = User.query.get(1111)
        self.u1 = u1

        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1.id)
    
    def test_invalid_username(self):
        """ Does invalid log in return error as expected?"""

        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        """ Does invalid log in return error as expected?"""

        # Create a test user
        user = User.register("testing1", "password", "testing1@test.com", "John", "Doe", None)
        user.id = 1111

        db.session.commit()

        u1 = User.query.get(1111)
        self.u1 = u1
        
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))




        




        