"""Forms for Flask-Feedback App.""" 

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Email, Length, ValidationError, EqualTo
from models import User

class RegistrationForm(FlaskForm):
    """Form for signing up as a user."""

    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])
    img_url = StringField('(Optional) Image URL')

    def validate_username(self, username):
        """Validate username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another username.')
    
    def validate_email(self, email):
        """Validate username is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use.')
    

class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField("Username", validators=[InputRequired(), Length(max=20)])

    password = PasswordField("Password", validators=[InputRequired()])


class CommentForm(FlaskForm):
    """Form for submitting feedback."""

    content = TextAreaField("Content", validators=[InputRequired()])


class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])
    img_url = StringField('(Optional) Image URL')
    password = PasswordField('Password', render_kw={"placeholder":"Please confirm your password to submit changes"}, validators=[Length(min=6)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[Length(min=6)])
    new_password = PasswordField('New Password', validators=[Length(min=6), EqualTo('confirm_password', message="Passwords must match!")])
    confirm_password = PasswordField('Confirm New Password', validators=[Length(min=6)])