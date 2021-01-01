"""Exercise View tests."""

import os
from unittest import TestCase

from models import db, connect_db

# Set an environmental variable to use a different database for tests 
os.environ['DATABASE_URL'] = "postgresql:///capstone-test"

from app import app

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class ExerciseViewTestCase(TestCase):
    """Test views for exercises."""

    def setUp(self):
        """Stuff to do before every test."""

        # get real python errors instead of flask errors
        app.config['TESTING'] = True

        # don't allow debug toolbar to work during testing
        app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

    def test_exercise_categories_page(self):
        with app.test_client() as client:
            res = client.get('/exercises')
            self.assertIn(b'Exercise Categories', res.data)  
            self.assertIn(b'Abs', res.data) 
            self.assertIn(b'Arms', res.data) 
            self.assertIn(b'Shoulders', res.data) 
    
    def test_exercises_per_category_page(self):
        with app.test_client() as client:
          res = client.get('/exercises/10/')
          self.assertIn(b'Exercises For: Abs', res.data) 
          self.assertIn(b'Please Note: You need to be signed in to view exercise details.', res.data) 
          self.assertIn(b'Crunches', res.data) 
          self.assertIn(b'Full Sit Outs', res.data) 


# Only public exercise page views are tested here. Private routes are tested in user view tests file.
