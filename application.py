import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

#@app.route("/")
#@login_required
#def index():
  #  """Show portfolio of stocks"""
    # TODO
@app.route("/", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/homepage")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached the route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure the confirm_password was submitted
        elif not request.form.get("confirmpassword"):
            return apology("must provide password (again)")

        # Ensure the passwords match
        elif request.form.get("confirmpassword") != request.form.get("password"):
            return apology("passwords don't match")

        # Ensure the username is not taken
        rows = db.execute("SELECT username from users WHERE username=:username", username=request.form.get("username"))
        if rows:
            return apology("username is not available")

        # Insert the user details into users table
        db.execute("INSERT INTO users (username , hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        flash("Regsitration Successful!")

        # Redirect to index page
        return redirect("/")

    # User reached the route via GET (as by clicking on a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/homepage")
@login_required
def homepage():
    """ Show the Homepage """
    return render_template("Homepage.html")

@app.route("/aboutus")
@login_required
def aboutus():
    """ Show the about us page """
    return render_template("AboutUs.html")

@app.route("/contactus")
@login_required
def contactus():
    """ Show the contact us page """
    return render_template("ContactUs.html")

@app.route("/upcommingmovies")
@login_required
def upcommingmovies():
    """ Show the upcomming movies page """
    return render_template("UpcommingMovies.html")

@app.route("/onlinebookings", methods=["GET","POST"])
@login_required
def onlinebookings():
    """ Show the online bookings page """
    # User reached the route via POST(i.e., by submitting a form via POST)
    if request.method == "POST":

        # Ensure the name was submitted
        if not request.form.get("username"):
            return apology("Please enter the name")

        # Ensure the date of booking was submitted
        elif not request.form.get("bookingdate"):
            return apology("Please input the booking date")

        # Ensure the movie's name was submitted
        elif not request.form.get("movie"):
            return apology("Please select the movie's name")

        # Ensure the class was selected
        elif not request.form.get("RB"):
            return apology("Please select the class")

        # Ensure the number of tickets where submitted
        elif not request.form.get("num"):
            return apology("Please enter the number of tickets")

        # Update the bookings table
        db.execute("INSERT INTO bookings (id, name, date, movie, class, num) VALUES(:id, :username, :bookingdate, :movie, :RB, :num)", id=session["user_id"], username=request.form.get("username"), bookingdate=request.form.get("bookingdate"), movie=request.form.get("movie"), RB=request.form.get("RB"), num=request.form.get("num"))

        # Select the info from the bookings table
        rows=db.execute("SELECT name, date, movie, class, num FROM bookings WHERE name=:username and movie=:movie", username=request.form.get("username"), movie=request.form.get("movie"))

        return render_template("booked.html", rows=rows)

    # if the user enters the route via GET request (i.e., By clicking on a link or via redirect)
    else:
        return render_template("OnlineBookings.html")


@app.route("/check", methods=["GET"])
def check():
    # Return true if username available, else false, in JSON format
    username = request.args.get("username")

    taken_usernames = db.execute("SELECT username FROM users WHERE username=:username", username=username)

    if taken_usernames and username:
        return jsonify(False)

    elif not taken_usernames and username:
        return jsonify(True)

    else:
        return jsonify(False)



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/password", methods=["GET","POST"])
def password():
    """Change Existing Password of the user"""
    # User reached the site via POST(as by submiting the form via POST)
    if request.method == "POST":

        # Get existing hash from the users table
        hashes = db.execute("SELECT hash FROM users WHERE username=:name", name=request.form.get("username"))

        hash = hashes[0]["hash"]

        # Ensure the username was submitted
        if not request.form.get("username"):
            return apology("missing username")

        # Ensure the old password was submited
        if not request.form.get("password"):
            return apology("missing old password")

        # Ensure the new password was submitted
        elif not request.form.get("new_password"):
            return apology("missing new password")

        # Ensure the confirm_password password was submited
        elif not request.form.get("confirmpassword"):
            return apology("missing password (again)")

        # Ensure the passwords match
        elif request.form.get("new_password") != request.form.get("confirmpassword"):
            return apology("passwords dont match")

        # Ensure old passwords match
        elif not check_password_hash(hash, request.form.get("password")):
            return apology("Old Password doesn't match")

        # All else satisfied change the password
        db.execute("UPDATE users SET hash=:new_hash WHERE username=:name", new_hash=generate_password_hash(request.form.get("new_password")), name=request.form.get("username"))

        flash("Password successfully changed!")
        return redirect("/")
    # User reached the site via GET(as by clicking on a link or via redirect)
    else:
        return render_template("password.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
