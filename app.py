import os

from flask import Flask, redirect, render_template, session, flash, request
import requests
import json
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Exercise, ExerciseCategory, ExerciseComment, UserExercise
from forms import RegistrationForm, LoginForm, CommentForm, UserEditForm, ChangePasswordForm
import pdb
from werkzeug.exceptions import Unauthorized, NotFound

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URI', 'postgres:///capstone')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

app.config['SECRET_KEY'] = "SECRET!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.before_first_request
def populate_database():
    """ Run helper functions to populate database if needed."""    

    # These helper functions check if APIs return any new meal or exercise data. If so, they take that data and add it to the database.

    get_exercise_categories()
    get_exercises()

@app.route('/')
def homepage():


###
# User Routes
###

    return render_template("homepage.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Show a registeration form and handle form submission."""

    # If user is already logged in, don't allow them to see this page.
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegistrationForm()

    if form.validate_on_submit():

        # No need for a try - except block because form validation is handled by WTForms.

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        img_url = form.img_url.data or None

        user = User.register(username, password, email, first_name, last_name, img_url)

        db.session.commit()

        # add username to session
        session['username'] = user.username

        flash(f"Welcome {username}!", "success")
        return redirect(f"/users/{user.username}")
    else:
        return render_template("user/register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Show a login form and handle form submission."""

    # If user is already logged in, don't allow them to see this page.
    if "username" in session:
        return redirect(f"/users/{session['username']}")
        
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            flash(f"Welcome back {username}!", "success")
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username or password!"]
    
    return render_template("user/login.html", form=form)

@app.route("/logout")
def logout():
    """Log user out and redirect to /login."""

    session.pop("username")

    flash(f"Goodbye!", "info")

    return redirect("/")

@app.route("/users/<username>")
def user_info(username):
    """Show user info and user's feedbacks."""
    
    # Make sure the logged in user is the authorized user to view this page.
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    username = session['username']

    user = User.query.filter_by(username=username).first()

    user_exercises = UserExercise.query.filter_by(user_id=user.id).all()

    user_exercise_comments = ExerciseComment.query.filter_by(user_id=user.id).all()

    return render_template("user/user.html", user=user, user_exercises=user_exercises, user_exercise_comments=user_exercise_comments)

@app.route("/users/<username>/settings", methods=["GET", "POST"])
def change_user_settings(username):
    """Handle user settings change."""

    # Make sure the logged in user is the authorized user to view this page.
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()

    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        user_auth = User.authenticate(form.username.data, form.password.data)

        if user_auth:
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data 
            user.img_url = form.img_url.data or None

            db.session.commit()

            flash("Update Successful.", "success")
            return redirect(f'/users/{user.username}')

        else:
            flash("Incorrect password.", "danger")
            return redirect(f'/users/{user.username}/settings')

    return render_template('/user/settings.html', form=form)

@app.route('/users/<username>/change-password', methods=["GET", "POST"])
def change_password(username):

    # Make sure the logged in user is the authorized user to view this page.
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()

    user_id = user.id

    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data 

        # If user's current password is true, update password.   
        if User.change_password(user_id, current_password, new_password):
            User.change_password(user_id, current_password, new_password)
            flash("Password updated.", "success")
            return redirect('/')
        else:
            flash("Incorrect Password.", "danger")
            return render_template('/user/change_password.html', form=form)
    else:
        return render_template('/user/change_password.html', form=form)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Delete existing user."""

    # Make sure the logged in user is the authorized user.
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()

    db.session.delete(user)

    db.session.commit()

    session.pop("username")

    flash("Account Deleted", "success")

    return redirect("/")


@app.route("/users/<username>/exercises/add", methods=["POST"])
def favorite_exercise(username):
    """Handle favoriting an exercise."""
    
    # Make sure the logged in user is the authorized user.
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.filter_by(username=username).first()

    # Get the exercise id from the form.
    exercise_id = request.form['data']
    
    # Create a UserExercise instance
    user_exercise = UserExercise(user_id=user.id, exercise_id=exercise_id)

    db.session.add(user_exercise)

    db.session.commit()

    return redirect(request.referrer)

@app.route("/users/<username>/exercises/remove", methods=["POST"])
def unfavorite_exercise(username):
    """Handle unfavoriting an exercise."""
    
    # Make sure the logged in user is the authorized user.
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    # Get the exercise id from the form
    exercise_id = request.form['data']

    user = User.query.filter_by(username=username).first()
    
    # Find user's exercise to remove from the database
    user_exercise = UserExercise.query.filter_by(user_id=user.id, exercise_id=exercise_id).first()

    db.session.delete(user_exercise)

    db.session.commit()

    return redirect(request.referrer)

@app.route('/exercise-comments/<int:comment_id>/delete', methods=["POST"])
def delete_exercise_comment(comment_id):
    """Delete an exercise comment."""

    # Find user's exercise comment to delete from the database
    comment = ExerciseComment.query.get_or_404(comment_id)

    # Make sure the logged in user is the authorized user.
    if "username" not in session or comment.user.username != session['username']:
        raise Unauthorized()

    db.session.delete(comment)

    db.session.commit()

    return redirect(request.referrer)


###
# Exercise Routes
###

@app.route('/exercises')
def display_workout_categories():
    """Display exercise categories."""

    categories = ExerciseCategory.query.all()
    
    return render_template("/exercise/exercise_categories.html", categories=categories)

@app.route('/exercises/<int:category_id>/')
def display_exercises(category_id):
    """Display exercises for a specific category."""

    exercises = Exercise.query.filter(Exercise.category_id==category_id)

    # Make sure category exists, otherwise return 404 error.
    if exercises.count() > 0:
        return render_template("/exercise/category.html", exercises=exercises)
    else:
        raise NotFound()

@app.route('/exercises/<int:category_id>/<int:exercise_id>')
def display_exercise(category_id, exercise_id):
    """Display info on a single exercise."""

    # This is a private endpoint, check if user is logged in
    if "username" not in session:
        raise Unauthorized()

    exercise = Exercise.query.get_or_404(exercise_id)

    comments = ExerciseComment.query.filter_by(exercise_id=exercise_id)

    comment_count = comments.count()

    user = User.query.filter_by(username=session['username']).first()

    user_exercise = UserExercise.query.filter_by(user_id=user.id, exercise_id=exercise_id).first()

    form = CommentForm()
    
    return render_template("exercise/exercise.html", exercise=exercise, comments=comments, form=form, user=user, user_exercise=user_exercise, comment_count=comment_count)

@app.route('/exercises/<int:category_id>/<int:exercise_id>/comment', methods=["POST"])
def add_exercise_comment(category_id, exercise_id):
    """Handle comment for an exercise."""
    
    # This is a private endpoint, check if user is logged in
    if "username" not in session:
        raise Unauthorized()

    form = CommentForm()

    username = session['username']

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        content = form.content.data
        
        exercise_comment = ExerciseComment(exercise_id=exercise_id, user_id=user.id, content = content)

        db.session.add(exercise_comment)

        db.session.commit()

    return redirect(f"/exercises/{category_id}/{exercise_id}")

###
# Meal Routes
###



@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(401)
def not_authorized(e):
    return render_template("401.html"), 401

###
# Helper functions to check if APIs have any new meal or exercise results. 
###

def get_exercise_categories():
    """Get muscle groups from API and place them in db."""
    request = requests.get('https://wger.de/api/v2/exercisecategory/')

    result = request.json()

    # Find all exercise categories currently stored in database
    exercise_categories = ExerciseCategory.query.all()

    category_ids = []

    # Push current exercise category ids into a list
    for category in exercise_categories:
        category_ids.append(category.id)    

    # If there is a new category in API result that doesn't exist in database, store it in database.
    for item in result['results']:
        if item['id'] not in category_ids:
            exercise_category = ExerciseCategory(id=item['id'], name=item['name'])

            db.session.add(exercise_category)
    
            db.session.commit()

def get_exercises():
    """Get exercises from API and place them in db."""
    request = requests.get('https://wger.de/api/v2/exercise?language=2&limit=250')

    result = request.json()

    # Find all exercises currently stored in database
    exercises = Exercise.query.all()

    exercise_ids = []

    for exercise in exercises:
        exercise_ids.append(exercise.id)


    for item in result['results']:
        if item['id'] not in exercise_ids:
            exercise = Exercise(id=item['id'], name=item['name'], description=item['description'], category_id=item['category'])
        
            db.session.add(exercise)

            db.session.commit()


