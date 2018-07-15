import os, requests

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

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

api_key = os.getenv('API_KEY')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/<zipcode>")
def api(zipcode):
    """Return details about a location."""

    # Make sure user is logged in.
    try:
        session["user_id"]
    except KeyError:
        return jsonify({"error": "User not logged in"}), 401

    # Query database for location.
    locations = db.execute("SELECT * FROM locations JOIN locationnames ON locationnames.locationname_id = locations.locationname_id WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()

    # Make sure location exists.
    if not location:
        return jsonify({"error": "Zipcode not in database"}), 404

    # Get number of checkins by counting num of matching checkins.
    numcheckins = len(db.execute("SELECT * FROM checkins WHERE location_id = :location_id", {"location_id": locations["location_id"]}).fetchall())

    return jsonify({
            "place_name": locations["city"],
            "state": locations["state"],
            "latitude": float(locations["latitude"]),
            "longitude": float(locations["longitude"]),
            "zip": locations["zipcode"],
            "population": locations["population"],
            "check_ins": numcheckins
        })

@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for locations that match query."""

    # Make sure user is logged in.
    try:
        session["user_id"]
    except KeyError:
        return redirect(url_for("login"))

    # If user visits page, render search.html
    if request.method == "GET":
        return render_template("search.html")

    query = request.form.get("query")

    if not query:
        flash("Must enter a query.")
        return render_template("search.html")

    # Change query to uppercase and add %s
    q = query.upper()
    q = "%" + q + "%"

    locations = db.execute("SELECT * FROM locations JOIN locationnames ON locationnames.locationname_id = locations.locationname_id WHERE zipcode LIKE :q OR locationnames.city LIKE :q", {"q": q}).fetchall()

    return render_template("search.html", query=query, locations=locations)

@app.route("/location", methods=["GET", "POST"])
def location():
    """Display information about a location."""

    # Make sure user is logged in.
    try:
        session["user_id"]
    except KeyError:
        return redirect(url_for("login"))

    location_id = request.args.get("location_id")

    # If form was submitted, check in.
    if request.method == "POST":
        comment = request.form.get("comment")

        db.execute("INSERT INTO checkins (time, comment, user_id, location_id) VALUES (:time, :comment, :user_id, :location_id)",
                    {"time": str(datetime.now()), "comment": comment, "user_id": int(session["user_id"]), "location_id": location_id})
        db.commit()

    # Query database for location details.
    location = db.execute("SELECT * FROM locations JOIN locationnames ON locationnames.locationname_id = locations.locationname_id WHERE location_id = :location_id", {"location_id": location_id}).fetchone()

    # Query database for checkins for this location.
    checkins = db.execute("SELECT * FROM checkins JOIN users ON users.user_id = checkins.user_id WHERE location_id = :location_id", {"location_id": location_id}).fetchall()

    # Saved number of checkins.
    numcheckins = len(checkins)

    # Format request to Dark Sky API.
    latitude, longitude = location["latitude"], location["longitude"]
    res = requests.get(f"https://api.darksky.net/forecast/{api_key}/{latitude},{longitude}")

    # Check that request worked.
    if res.status_code != 200:
        raise Exception('ERROR: API request unsuccessful.')

    # Convert request response to JSON.
    data = res.json()
    weather = data["currently"]

    # Make weather info easier to read.
    weather["time"] = datetime.fromtimestamp(int(weather["time"])).strftime('%H:%M:%S UTC')
    weather["humidity"] = int(weather["humidity"] * 100)
    weather["temperature"] = int(weather["temperature"])
    weather["dewPoint"] = int(weather["dewPoint"])

    # Render location page with info about location, checkins and weather.
    return render_template("location.html", location=location, checkins=checkins, numcheckins=numcheckins, weather=weather)

@app.route("/mycheckins", methods=["GET"])
def mycheckins():
    """Display all checkins by the logged in user"""

    # Make sure user is logged in.
    try:
        user_id = int(session["user_id"])
    except KeyError:
        return redirect(url_for("login"))

    # Query database for checkins.
    checkins = db.execute("SELECT * FROM checkins JOIN locations ON locations.location_id = checkins.location_id WHERE user_id = :user_id", {"user_id": user_id}).fetchall()

    return render_template("mycheckins.html", checkins=checkins)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # If user visits page, render login.html
    if request.method == "GET":
        return render_template("login.html")

    # Ensure username was submitted.
    username = request.form.get("username")
    if not username:
        flash("Must provide username.")
        return render_template("login.html")

    # Ensure password was submitted.
    password = request.form.get("password")
    if not password:
        flash("Must provide password.")
        return render_template("login.html")

    # Query database for username.
    rows = db.execute("SELECT * FROM users WHERE username = :username",
        {"username": username}).fetchall()

    # Ensure username exists and password is correct.
    if len(rows) != 1 or not pwd_context.verify(password, rows[0][2]):
        flash("Invalid username and/or password.")
        return render_template("login.html")

    # Remember which user has logged in.
    session["user_id"] = rows[0]

    # Redirect user to search page.
    flash("Welcome back, " + rows[0][3] + "!")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id.
    session.clear()

    # Redirect user to index form.
    flash("Successfully logged out.")
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # Forget any user_id
    session.clear()

    # If user visits page, render register.html
    if request.method == "GET":
        return render_template("register.html")

    # Ensure username was submitted.
    username = request.form.get("username")
    if not username:
        flash("Must provide username.")
        return render_template("register.html")

    # Ensure first name was submitted.
    first_name = request.form.get("first_name")
    if not first_name:
        flash("Must provide first name.")
        return render_template("register.html")

    # Ensure password was submitted.
    password_1 = request.form.get("password_1")
    if not password_1:
        flash("Must provide password.")
        return render_template("register.html")

    # Ensure confirmation password was submitted.
    password_2 = request.form.get("password_2")
    if not password_2:
        flash("Must confirm password.")
        return render_template("register.html")

    # Ensure password and confirmation password are the same.
    if password_1 != password_2:
        flash("Passwords do not match.")
        return render_template("register.html")

    # Save user credentials.
    hash = pwd_context.hash(password_1)
    result = db.execute("INSERT INTO users (username, first_name, password_hash) VALUES (:username, :first_name, :hash)",
                    {"username": username, "first_name": first_name, "hash": hash})

    # Ensure that username does not already exist.
    if not result:
        flash("Username already exists.")
        return render_template("register.html")

    # Remember which user has logged in.
    rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    session["user_id"] = rows[0]

    db.commit()

    # Redirect user to home page.
    flash("Thank you for creating an account, " + first_name + ".")
    return redirect(url_for("index"))