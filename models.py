"""SQLAlchemy models for """

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()



class User(db.Model):
    """User model."""

    __tablename__ = "users"

    #set table columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    img_url = db.Column(db.Text, default="/static/images/default-pic.png")

    exercise_comments = db.relationship("ExerciseComment", backref="user", cascade="all,delete")

    user_exercises = db.relationship("UserExercise", backref="user", cascade="all, delete") 


    @classmethod
    def register(cls, username, password, email, first_name, last_name, img_url):
        """Register user with hashed password and return user."""

        hashed_password = bcrypt.generate_password_hash(password)

        # turn bytestring into normal (unicode utf8) string
        hashed_password_utf8 = hashed_password.decode("utf8")

        user = User(username=username, password=hashed_password_utf8, email=email, first_name=first_name, last_name=last_name, img_url=img_url)

        db.session.add(user)
        
        return user
 
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    @classmethod
    def change_password(cls, id, current_password, new_password):

        # get user
        user = cls.query.get_or_404(id)

        if user:
            # check if user's current password is correct
            is_auth = bcrypt.check_password_hash(user.password, current_password)

            if is_auth:
                # hash new_password and set it as user's password
                hashed_pwd = bcrypt.generate_password_hash(new_password).decode('UTF-8')
                user.password = hashed_pwd
                db.session.commit()
                return True
            else:
                return False
    
    def __repr__(self):
        """Show info about user."""
        u = self
        return f"<{u.username}: {u.first_name} {u.last_name} - {u.email}>"

class ExerciseCategory(db.Model):
    __tablename__ = "exercise_categories"

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)

class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.ForeignKey("exercise_categories.id", ondelete="CASCADE"), nullable=False)

    category = db.relationship('ExerciseCategory', backref='exercise')

class ExerciseComment(db.Model):
    """Comment model for exercises."""

    __tablename__ = "exercise_comments"

    id = id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = db.Column(db.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)

    exercise = db.relationship("Exercise")

class UserExercise(db.Model):
    """Model for users' exercises."""

    __tablename__ = "user_exercises"

    id = id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = db.Column(db.ForeignKey("exercises.id", ondelete="CASCADE"), unique=True, nullable=False)

    exercise = db.relationship("Exercise") 


def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)