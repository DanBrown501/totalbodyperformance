"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, User

# Set an environmental variable to use a different database for tests 
os.environ['DATABASE_URL'] = "postgresql:///capstone-test"

from app import app

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for meals."""

    def setUp(self):
        """Stuff to do before every test."""

        # get real python errors instead of flask errors
        app.config['TESTING'] = True

        # don't allow debug toolbar to work during testing
        app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

        # create a test user
        u = User.register("testing", "password", "testing@test.com", "John", "Doe", None)
        u.id = 888
        db.session.commit()

    def test_exercise_page(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'testing'

            res = client.get('/exercises/10/91')
            self.assertIn(b'Crunches', res.data) 
            self.assertIn(b'Add a Comment', res.data) 
            self.assertIn(b'Comments', res.data)

    def test_exercise_page_invalid_user(self):
        with app.test_client() as client:
            res = client.get('/exercises/10/91')
            self.assertIn(b'not authorized', res.data) 

    
    
    def test_exercise_comment(self):
        with client.session_transaction() as sess:
                sess['username'] = 'testing'