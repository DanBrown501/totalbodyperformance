"""Exercise model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, ExerciseCategory, Exercise, UserExercise, ExerciseComment

# Set an environmental variable to use a different database for tests 
os.environ['DATABASE_URL'] = "postgresql:///capstone-test"

from app import app

db.create_all()

class ExerciseModelTestCase(TestCase):
    """Test exercise models."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()

        # Create test exercise categories
        c1 = ExerciseCategory(name="Chest")
        c1.id = 10
        c2 = ExerciseCategory(name="Triceps")
        c2.id = 11

        db.session.add_all([c1,c2])
        
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Tear down after tests are completed"""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_exercise_category(self):
        """Test basic exercise category model."""

        # Create test exercise categories
        c3 = ExerciseCategory(name="Biceps")
        c3.id = 12
        c4 = ExerciseCategory(name="Back")
        c4.id = 13

        db.session.add_all([c3,c4])
        
        db.session.commit()

        ec = ExerciseCategory.query.all()

        self.assertEqual(len(ec), 4) # 2 categories were created in setUp() and we created 2 more here.
        self.assertEqual(ec[0].id, 10)
        self.assertEqual(ec[0].name, "Chest")
        self.assertEqual(ec[1].id, 11)
        self.assertEqual(ec[1].name, "Triceps")
        self.assertEqual(ec[2].id, c3.id)
        self.assertEqual(ec[2].name, "Biceps")
        self.assertEqual(ec[3].id, c4.id)
        self.assertEqual(ec[3].name, "Back")

    def test_exercise_model(self):
        """Test basic exercise model."""

        # Create test exercises
        e1 = Exercise(name="Bench Press", description="Chest exercise", category_id=10)
        e1.id = 500
        e2 = Exercise(name="Triceps Pushdown", description="Triceps exercise", category_id=11)
        e2.id = 501

        db.session.add_all([e1, e2])

        db.session.commit()

        e = Exercise.query.all()

        self.assertEqual(len(e), 2)
        self.assertEqual(e[0].id, e1.id)
        self.assertEqual(e[0].name, "Bench Press")
        self.assertEqual(e[0].description, "Chest exercise")
        self.assertEqual(e[1].id, e2.id)
        self.assertEqual(e[1].name, "Triceps Pushdown")
        self.assertEqual(e[1].description, "Triceps exercise")
        

    def test_user_exercise_model(self):
        """Test adding exercises to a user's exercises functionality."""

        # Create test exercises
        e1 = Exercise(name="Bench Press", description="Chest exercise", category_id=10)
        e1.id = 500
        e2 = Exercise(name="Triceps Pushdown", description="Triceps exercise", category_id=11)
        e2.id = 501
        
        # Create test user
        u = User.register("testing1", "password", "testing@test.com", "John", "Doe", None)
        u.id = 777

        db.session.add_all([e1, e2])

        ue1 = UserExercise(user_id=u.id, exercise_id=e1.id)
        ue2 = UserExercise(user_id=u.id, exercise_id=e2.id)

        db.session.add_all([ue1, ue2])

        db.session.commit()

        exc = UserExercise.query.filter_by(user_id=u.id)

        self.assertEqual(exc.count(), 2)
        self.assertEqual(exc[0].exercise_id, e1.id)
        self.assertEqual(exc[1].exercise_id, e2.id)

        
    def test_exercise_comment_model(self):
        """Test user commentting functionality on an exercise."""

        # Create test exercises
        e1 = Exercise(name="Bench Press", description="Chest exercise", category_id=10)
        e1.id = 500
        e2 = Exercise(name="Triceps Pushdown", description="Triceps exercise", category_id=11)
        e2.id = 501
        
        # Create test user
        u = User.register("testing1", "password", "testing@test.com", "John", "Doe", None)
        u.id = 777

        db.session.add_all([e1, e2])

        uc1 = ExerciseComment(content="Test1", user_id=u.id, exercise_id=e1.id)
        uc2 = ExerciseComment(content="Test2", user_id=u.id, exercise_id=e2.id)

        db.session.add_all([uc1, uc2])

        db.session.commit()

        ucs = ExerciseComment.query.filter_by(user_id=u.id)

        self.assertEqual(ucs.count(), 2)
        self.assertEqual(ucs[0].exercise_id, e1.id)
        self.assertEqual(ucs[0].user_id, u.id)
        self.assertEqual(ucs[1].exercise_id, e2.id)
        self.assertEqual(ucs[1].user_id, u.id)