import os

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable.
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database.
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for locations that match query."""

    # If user visits page, render search.html
    if request.method == "GET":
        return render_template("search.html")

    query = request.form.get("query")

    return render_template("search.html", query=query)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # If user visits page, render login.html
    if request.method == "GET":
        return render_template("login.html")

    error = None

    # Ensure username was submitted.
    username = request.form.get("username")
    if not username:
        error = "Must provide username."
        return render_template("login.html", error=error)

    # Ensure password was submitted.
    password = request.form.get("password")
    if not password:
        error = "Must provide password."
        return render_template("login.html", error=error)

    # Query database for username.
    rows = db.execute("SELECT * FROM users WHERE username = :username",
        {"username": username}).fetchall()

    # Ensure username exists and password is correct.
    if len(rows) != 1 or not pwd_context.verify(password, rows[0][2]):
        error = "Invalid username and/or password"
        return render_template("login.html", error=error)

    # Remember which user has logged in.
    session["user_id"] = rows[0]

    # Redirect user to home page.
    flash("Welcome back, " + rows[0][3] + "!")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id.
    session.clear()

    # Redirect user to index form.
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    error = None

    # If user visits page, render register.html
    if request.method == "GET":
        return render_template("register.html")

    # Ensure username was submitted.
    username = request.form.get("username")
    if not username:
        error = "Must provide username."
        return render_template("register.html", error=error)

    # Ensure first name was submitted.
    first_name = request.form.get("first_name")
    if not first_name:
        error = "Must provide first name."
        return render_template("register.html", error=error)

    # Ensure password was submitted.
    password_1 = request.form.get("password_1")
    if not password_1:
        error = "Must provide password."
        return render_template("register.html", error=error)

    # Ensure confirmation password was submitted.
    password_2 = request.form.get("password_2")
    if not password_2:
        error = "Must confirm password."
        return render_template("register.html", error=error)

    # Ensure password and confirmation password are the same.
    if password_1 != password_2:
        error = "Passwords do not match."
        return render_template("register.html", error=error)

    # Save user credentials.
    hash = pwd_context.hash(password_1)
    result = db.execute("INSERT INTO users (username, first_name, password_hash) VALUES (:username, :first_name, :hash)",
                    {"username": username, "first_name": first_name, "hash": hash})

    # Ensure that username does not already exist.
    if not result:
        error = "Username already exists."
        return render_template("register.html", error=error)

    # Remember which user has logged in.
    rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    session["user_id"] = rows[0]

    db.commit()

    # Redirect user to home page.
    flash("Thank you for creating an account, " + first_name + ".")
    return redirect(url_for("index"))