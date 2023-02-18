import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import json
import time
import datetime
from functools import wraps

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///game.db")

# Global correct option
correct_option = db.execute('SELECT * FROM players ORDER BY RANDOM() LIMIT 1')

# FOR TESTING PURPOSES ONLY
# correct_option = db.execute('SELECT * FROM players where id = 1 ORDER BY RANDOM() LIMIT 1')

# Every 24hrs change the block to false and delete the user guess table
activate_block = False  # Default value

# Executing this lines for the first time ONLY
db.execute(' DROP TABLE user_guess')
db.execute('CREATE TABLE user_guess(try_number INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,guess_id INTEGER NOT NULL,guess_full_name TEXT NOT NULL,guess_nation TEXT NOT NULL,guess_continent TEXT NOT NULL,guess_wc_group TEXT NOT NULL,guess_age INTEGER NOT NULL,guess_position TEXT NOT NULL,guess_shirt_number INTEGER NOT NULL,time text NOT NULL,user_id INTEGER NOT NULL,FOREIGN KEY(user_id) REFERENCES user(id))')


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Function previously used for cs50's finance problem


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/search")
def search():
    q = request.args.get('q')
    if q:
        players = db.execute('SELECT * FROM players WHERE full_name LIKE ? LIMIT 7', '%' + q + '%')
    else:
        players = []
    return jsonify(players)


@app.route("/")
@login_required
def index():
    global correct_option
    user_guess = db.execute('SELECT * FROM user_guess where user_id = ?', session["user_id"])
    attempts = len(user_guess)
    user_info = db.execute('SELECT * FROM user where id = ?', session["user_id"])
    if attempts == 0:
        return render_template("index.html", correct_option=correct_option, user_info=user_info)
    else:
        return redirect(url_for('table', id=user_guess[len(user_guess)-1]["guess_id"]))

# Got some help from user Randall Moore (from StackOverFlow)
# Official site where i've got the information: https://stackoverflow.com/questions/14343812/redirecting-to-url-in-flask


@app.route('/redirect', methods=['POST', 'GET'])
@login_required
def redirection():
    if request.method == 'POST':
        guessId = request.json
        return jsonify({'redirect': url_for('table', id=guessId)})


@app.route("/table/<id>")
@login_required
def table(id):
    playersdb = db.execute('SELECT * FROM players')  # Table with all the football players and their information
    global correct_option
    global activate_block
    user_guessId = id
    player_picked = db.execute('SELECT * FROM players WHERE id = ?', user_guessId)
    # Checking if user already made a guess
    user_guess = db.execute('SELECT * FROM user_guess where user_id = ?', session["user_id"])
    if len(user_guess) == 0:
        activate_block = False
    db.execute('INSERT INTO user_guess (guess_id ,guess_full_name, guess_nation, guess_continent, guess_wc_group, guess_age, guess_position,guess_shirt_number,time,user_id) VALUES (?,?,?,?,?,?,?,?,datetime(),?)',
               player_picked[0]['id'], player_picked[0]['full_name'], player_picked[0]['nation'], player_picked[0]['continent'], player_picked[0]['wc_group'], player_picked[0]['age'], player_picked[0]['position'], player_picked[0]['shirt_number'], session["user_id"])
    user_guess = db.execute('SELECT * FROM user_guess where user_id = ?',
                            session["user_id"])  # Table with ALL user guesses (with info)
    attempts = len(user_guess)
    user_info = db.execute('SELECT * FROM user where id = ?', session["user_id"])
    if attempts == 11 or activate_block == True:
        correct_user_try_number = db.execute(
            'SELECT try_number FROM user_guess where guess_id = ? and user_id = ? ', correct_option[0]['id'], session["user_id"])
        first_try_number = db.execute('SELECT try_number from user_guess where user_id = ? LIMIT 1', session["user_id"])
        if len(correct_user_try_number) == 0:
            db.execute('DELETE FROM user_guess WHERE try_number BETWEEN ? AND (SELECT MAX(try_number) from user_guess) AND user_id = ?',
                       first_try_number[0]['try_number']+10, session["user_id"])
        elif correct_user_try_number[0]['try_number'] >= first_try_number[0]['try_number']+10:
            db.execute('DELETE FROM user_guess WHERE try_number BETWEEN ? AND (SELECT MAX(try_number) from user_guess) AND user_id = ?',
                       first_try_number[0]['try_number']+10, session["user_id"])
        else:
            db.execute('DELETE FROM user_guess WHERE try_number BETWEEN ? AND (SELECT MAX(try_number) from user_guess) AND user_id = ?',
                       correct_user_try_number[0]['try_number']+1, session["user_id"])
    user_guess = db.execute('SELECT * FROM user_guess where user_id = ?',
                            session["user_id"])  # Table with ALL user guesses (with info)
    attempts = len(user_guess)
    for n in range(attempts):
        # 1) WINNER CASE
        if user_guess[n]['guess_id'] == correct_option[0]['id']:
            correct_user_try_number = db.execute(
                'SELECT try_number FROM user_guess where guess_id = ? and user_id = ? ', correct_option[0]['id'], session["user_id"])
            points = 11 - attempts
            if activate_block == False:
                db.execute('UPDATE user SET points = ?, games_played = ?, games_won = ?  WHERE id = ?',
                           user_info[0]['points']+points, user_info[0]['games_played']+1, user_info[0]['games_won']+1, session["user_id"])
                user_info = db.execute('SELECT * FROM user where id = ?', session["user_id"])
                db.execute('UPDATE user SET win_porcentage = ? WHERE id = ?',
                           (user_info[0]['games_won']/user_info[0]['games_played'])*100, session["user_id"])
                activate_block = True
            db.execute('DELETE FROM user_guess WHERE try_number BETWEEN ? AND (SELECT MAX(try_number) from user_guess) AND user_id = ?',
                       correct_user_try_number[0]['try_number']+1, session["user_id"])
            user_info = db.execute('SELECT * FROM user where id = ?', session["user_id"])
            user_guess = db.execute('SELECT * FROM user_guess where user_id = ?', session["user_id"])
            user_tries = len(user_guess)
            last_try_time = db.execute('SELECT time FROM user_guess where guess_id = ? and user_id = ? ',
                                       correct_option[0]['id'], session["user_id"])
            return render_template("winner.html", list_of_players=playersdb, answer=correct_option, guess=user_guess, attempts=user_tries, user_info=user_info, timer=last_try_time)
        # 2) LOSER CASE OR CASE ATTEMPTS=10
        elif n == 9 and attempts == 10:
            if activate_block == False:
                db.execute('UPDATE user SET games_played = ? where id = ?', user_info[0]['games_played']+1, session["user_id"])
                activate_block = True
            user_info = db.execute('SELECT * FROM user where id = ?', session["user_id"])
            user_guess = db.execute('SELECT * FROM user_guess where user_id = ?', session["user_id"])
            user_tries = len(user_guess)
            last_try_time = db.execute('SELECT time FROM user_guess where guess_id = ? and user_id = ? ',
                                       correct_option[0]['id'], session["user_id"])
            return render_template("gameover.html", list_of_players=playersdb, answer=correct_option, guess=user_guess, attempts=attempts, user_info=user_info, timer=last_try_time)
        # 3) CASE ATTEMPTS > 10
        elif n > 10:
            user_info = db.execute('SELECT * FROM user where id = ?', session["user_id"])
            user_guess = db.execute('SELECT * FROM user_guess where user_id = ?', session["user_id"])
            user_tries = len(user_guess)
            last_try_time = db.execute('SELECT time FROM user_guess where guess_id = ? and user_id = ? ',
                                       correct_option[0]['id'], session["user_id"])
            return render_template("gameover.html", list_of_players=playersdb, answer=correct_option, guess=user_guess, attempts=attempts, user_info=user_info, timer=last_try_time)
        elif n == attempts-1:
            return render_template("guess.html", list_of_players=playersdb, answer=correct_option, guess=user_guess, attempts=attempts, user_info=user_info)

# LOGIN AND REGISTER PART OF THE CODE


@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()
    """Register user"""
    if request.method == "POST":
      # Ensure username was submitted
        if len(request.form.get('username')) == 0:
            flash("ERROR: Missing username")
            return render_template('register.html')

        # Ensure password was submitted
        if len(request.form.get('password')) == 0 or len(request.form.get('confirmation')) == 0:
            flash('ERROR: Missing password')
            return render_template('register.html')
# Ensure password and confirmation are the same
        if request.form.get('password') != request.form.get('confirmation'):
            flash('ERROR: Passwords do not match')
            return render_template('register.html')

       # Ensure that the username is not already taken
        rows = db.execute("SELECT * FROM user WHERE username = ?", request.form.get('username'))
        if len(rows) != 0:
            flash('ERROR: Username already taken')
            return render_template('register.html')

       # Every possible error checked, adding user into the database
        db.execute('INSERT INTO user (username,hash)  VALUES(?,?)', request.form.get(
            'username'), generate_password_hash(request.form.get('password')))

       # log the user in after registration
        rows = db.execute("SELECT * FROM user WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]
    # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('ERROR: Must provide username')
            return render_template('login.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('ERROR: Must provide password')
            return render_template('login.html')

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash('ERROR: Invalid username and/or password')
            return render_template('login.html')

       # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
   # Redirect user to login form
    return redirect("/")


@app.route("/cooldown", methods=['POST', 'GET'])
@login_required
def cooldown():
    value = request.json
    if request.method == 'POST':
        if value == 1:
            global activate_block
            global correct_option
            activate_block = False
            db.execute('DELETE FROM user_guess WHERE user_id = ?', session["user_id"])
            correct_option = db.execute('SELECT * FROM players ORDER BY RANDOM() LIMIT 1')
        return jsonify({'redirect': url_for('index')})