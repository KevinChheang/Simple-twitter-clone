from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):
    """Form for registering/login a user."""

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])

class TweetForm(FlaskForm):
    """Form for creating tweet."""

    tweet = TextAreaField("Tweet", validators=[InputRequired()], render_kw={"placeholder": "Tweet tweet tweet"})