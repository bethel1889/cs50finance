import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, check

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Showing a users portfolio on the homepage
@app.route("/")
@login_required
def index():
    # Get the user's Details from the database
    id = session["user_id"]
    user_details = db.execute("SELECT * FROM users WHERE id=?", id)[0]
    username = user_details["username"]
    cash = user_details["cash"]

    raw_portfolio = db.execute('''SELECT * FROM users JOIN portfolio ON users.id=portfolio.user_id
                                JOIN stocks ON portfolio.stock_id=stocks.id WHERE users.id=?;''', id)
    portfolio = []

    stock_value = 0
    for row in raw_portfolio:
        new_row = {}
        if row["shares"] == 0:
            continue
        new_row["symbol"] = row["symbol"]
        new_row["shares"] = row["shares"]
        new_row["price"] = lookup(row["symbol"])["price"]
        new_row["value"] = new_row["shares"] * new_row["price"]
        stock_value += new_row["value"]
        portfolio.append(new_row)

    grand_total = (stock_value + cash)
    return render_template("index.html", portfolio=portfolio,
                           username=username, cash=cash, stock_value=stock_value, grand_total=grand_total)


# Buying a Stock
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # Take note of the user's id for database querying
    id = session["user_id"]

    # To get the form
    if request.method == "GET":
        symbol = request.args.get("symbol")
        if not symbol:
            return render_template("buy.html")
        return render_template("buy.html", symbol=symbol)

    # After the form has been submitted
    else:
        # Get the symbol and check validity
        symbol = request.form.get("symbol")
        stock_data = (lookup(symbol))
        if not stock_data:
            return apology("Invalid stock symbol")

        symbol = stock_data["symbol"]
        price = float(stock_data["price"])
        shares = request.form.get("shares")

        # Check if the shares input is valid
        # Check if shares is negative
        if '.' in shares:
            return apology("Invalid share value")

        try:
            shares = int(shares)
        except:
            return apology("Invalid share Value")

        if shares < 0:
            return apology("Invalid share value")

        # Get the total cost of the shares and the user's cash balance
        shares = float(shares)
        cost = shares * price
        cash = float(db.execute("SELECT * FROM users WHERE id=?", id)[0]["cash"])

        # Check if the user can afford the purchase
        if cost > cash:
            return apology("You do not have enough cash for the transaction")
        else:
            # update you cash by subtracting cost, and get the new cash
            db.execute("UPDATE users SET cash = cash - ? WHERE id=?", cost, id)
            new_cash = db.execute("SELECT * FROM users WHERE id=?", id)

            # if that particular stock symbol is not in your database, add it and get the stock id
            rows = db.execute("SELECT * FROM stocks WHERE symbol=?", symbol)
            if not rows:
                db.execute("INSERT INTO stocks(symbol) VALUES(?)", symbol)
            stock_id = db.execute("SELECT * FROM stocks WHERE symbol=?", symbol)[0]["id"]

            # check if the user already has this stock in his portfolio
            user_stocks = db.execute(
                "SELECT * FROM portfolio WHERE user_id=? AND stock_id=?", id, stock_id)

            # if he does not, add the shares, and stock to his portfolio
            if not user_stocks:
                db.execute('''INSERT INTO portfolio (shares, user_id, stock_id)
                            VALUES (?, ?, ?);''', shares, id, stock_id)

            # If he has the stock, just update the number of shares
            else:
                db.execute(
                    "UPDATE portfolio SET shares = shares + ? WHERE user_id=? AND stock_id=?", shares, id, stock_id)

            # record the order_type, shares, price, time_stamp, user_id and stock_id in history
            # NOTE 1 is for buying orders and 0 is for selling orders
            buy = 1
            sell = 0
            time_stamp = request.form.get("time_stamp")
            db.execute('''INSERT INTO history (order_type, shares, price, time_stamp, user_id, stock_id)
                       VALUES (?, ?, ?, ?, ?, ?)''', buy, shares, price, time_stamp, id, stock_id)

            return redirect("/")


@app.route("/history")
@login_required
def history():
    def order(order_type):
        if order_type == 1:
            return "buy"
        return "sell"

    # Show history of transactions
    id = session["user_id"]
    raw_history = db.execute(''' SELECT * FROM users JOIN history ON users.id=history.user_id
                                JOIN stocks ON history.stock_id=stocks.id WHERE users.id=?;''', id)
    username = raw_history[0]["username"]
    history = []
    for row in raw_history:
        new_row = {}
        new_row["symbol"] = row["symbol"]
        new_row["order_type"] = order(row["order_type"])
        new_row["shares"] = row["shares"]
        new_row["price"] = usd(row["price"])
        new_row["time_stamp"] = row["time_stamp"]
        history.append(new_row)
    return render_template("history.html", username=username, history=history)


@app.route("/login", methods=["GET", "POST"])
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    else:
        stock_symbol = request.form.get("symbol")
        if not stock_symbol:
            return apology("No stock symbol was provided")
        stock = lookup(stock_symbol)
        if not stock:
            return apology("Error, Stock not found")
        return render_template("quoted.html", stock=stock)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        """Register user"""
        # Check if the username and password is valid
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if check(username, password) == False:
            return apology("Enter username and password to login")

        # Check if the password and confirmation are both correct
        elif password != confirmation:
            return apology("Password and confirmation password do not match")

        # Check if the username exists in the database
        details = db.execute("SELECT * FROM users WHERE username=?;", username)
        if not details:
            # Enter the user's details into the database if the username doesn't exist
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?);",
                       username, generate_password_hash(password))
            rows = db.execute("SELECT * FROM users WHERE username=?;", username)

            # Log the user in
            session["user_id"] = rows[0]["id"]
            return redirect("/")

        # if the username and password exist
        elif check_password_hash(details[0]["hash"], password) == True:
            return apology("You already have an account with CS50 finance")

        # If only the username exists
        else:
            return apology("Please choose a different username, this username has been taken")

    else:
        return render_template("register.html")


# Sell shares of stocks
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    id = session["user_id"]
    if request.method == "GET":
        symbols = db.execute(
            "SELECT symbol FROM stocks WHERE id IN (SELECT stock_id FROM portfolio WHERE user_id=?);", id)
        return render_template("sell.html", symbols=symbols)

    else:
        stock_data = (lookup(request.form.get("symbol")))
        if not stock_data:
            return apology("Invalid stock symbol")
        symbol = stock_data["symbol"]

        price = stock_data["price"]
        shares = request.form.get("shares")
        if '.' in shares:
            return apology("Invalid share value")

        try:
            shares = int(shares)
        except:
            return apology("Invalid share Value")

        if shares < 0:
            return apology("Invalid share value")

        shares = float(shares)
        cost = shares * price
        stock_id = db.execute("SELECT * FROM stocks WHERE symbol=?;", symbol)[0]["id"]
        user_shares = db.execute(
            "SELECT * FROM portfolio WHERE user_id=? AND stock_id=?;", id, stock_id)[0]["shares"]
        if user_shares < shares:
            return apology("Not enough shares for this transaction")

        # update your cash by adding the cost
        db.execute("UPDATE users SET cash = cash + ? WHERE id=?", cost, id)
        new_cash = db.execute("SELECT * FROM users WHERE id=?;", id)

        # Update the number of shares the user has by removing the number of shares he sold
        db.execute(
            "UPDATE portfolio SET shares = shares - ? WHERE user_id=? AND stock_id=?", shares, id, stock_id)

        # record the order_type, shares, price, time_stamp, user_id and stock_id in history
        # NOTE 1 is for buying orders and 0 is for selling orders
        buy = 1
        sell = 0
        time_stamp = request.form.get("time_stamp")
        db.execute('''INSERT INTO history (order_type, shares, price, time_stamp, user_id, stock_id)
                   VALUES (?, ?, ?, ?, ?, ?);''', sell, shares, price, time_stamp, id, stock_id)

        return redirect("/")


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        """Add more cash to your balance"""
        id = session["user_id"]
        extra = request.form.get("extra")
        if not extra:
            return apology("Please enter an amount")
        db.execute("UPDATE users SET cash = cash + ? WHERE id=?;", extra, id)
        return redirect("/")
    else:
        return render_template("add_cash.html")
