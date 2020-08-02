from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///auth_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """Show homepage with links to site areas."""
    if "user_id" not in session:
        flash("Signup/Login to unlock features", "danger")

    tweets = Tweet.query.all()

    return render_template("index.html", tweets=tweets)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        new_user = User.register(username, password)
        db.session.add(new_user)
        try:
            db.session.commit()
            session["user_id"] = new_user.id
            session["username"] = new_user.username
            return redirect("/")
        except IntegrityError:
            form.username.errors.append("Username taken")
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, password)

        if user:
            session["user_id"] = user.id
            session["username"] = user.username

            flash(f"Welcome {user.username}", "success")

            return redirect("/")
        else:
            form.username.errors = ["Bad name/password"]
    
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user_id")
    session.pop("username")
    flash("Logout successful.", "success")

    return redirect("/")

@app.route("/tweets", methods=["Get", "POST"])
def tweet():
    if "user_id" not in session:
        return redirect("/")

    form = TweetForm()

    if form.validate_on_submit():
        tweet = form.tweet.data

        new_tweet = Tweet(tweet=tweet, user_id=session["user_id"])

        db.session.add(new_tweet)
        db.session.commit()

        flash("Tweet created", "success")

        return redirect("/")

    return render_template("tweets.html", form=form)

@app.route("/tweets/delete/<int:tweet_id>", methods=["POST"])
def delete_tweet(tweet_id):
    # redirect to home if not logged in
    if "user_id" not in session:
        flash("Please login first", "danger")
        return redirect("/login")
    
    tweet = Tweet.query.get_or_404(tweet_id)

    # make sure user can't delete other's tweet
    # by type in path into URL
    if tweet.user.id == session["user_id"]:
        db.session.delete(tweet)
        db.session.commit()

        flash("Tweet deleted", "info")
        return redirect("/")

    return redirect("/")