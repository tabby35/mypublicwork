import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
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


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks = db.execute( "SELECT symbol,SUM(Number_of_shares) AS Totalshares,price FROM 'transaction' WHERE user_id=:user_id GROUP BY symbol", user_id=session["user_id"])
    row = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    cashathand = row[0]["cash"]
    return render_template("index.html", stocks=stocks, cashathand=cashathand)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        """require stock symbol"""
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("must provide symbol", 403)
        """require user input number of shares"""
        Number_of_shares = request.form.get("shares")
        if (Number_of_shares.isdigit() <= 0):
            return apology("give a positive valid number", 403)
        """check how much cash user has in users"""
        row = db.execute("SELECT cash FROM users WHERE id=:user_id",user_id=session["user_id"])
        cashathand = row[0]["cash"]
        """lookup for stock current price"""
        price = stock["price"]
        """total price of shares"""
        Totalprice = Number_of_shares*price
        """decline to buy the shares if less fund"""
        if Totalprice > cashathand:
            return apology("insufficient fund")
        """buy the shares"""
        db.execute( "INSERT INTO  transaction(user_id, symbol, Number_of_shares, price) VALUES(:user_id, :symbol, :Number_of_shares, :price",user_id=session["user_id"], symbol=request.form.get("symbol"), Number_of_shares=Number_of_shares, price=price)
        """update user table"""
        db.execute("UPDATE users SET cash = cash-:price WHERE id = :user_id", price = price, user_id = session["user_id"])
        return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    row = db.execute("SELECT Symbol, Number_of_shares, price, sharetosell, Total_sell FROM 'transaction' WHERE user_id = :user_id GROUP BY symbol", user_id=session["user_id"])
    return render_template("hist.html",row=row)


@app.route("/login", methods = ["GET", "POST"])
def login():
    """Log user in"""

     #Forget any user_id
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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        flash("successfully logged in")
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
    flash("successfully log out")
    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("indicate the symbol", 403)
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("the stock not available", 403)
        else:
            return redirect("/")
    else:
        return render_template("quote.html")


@app.route("/register", methods = ["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        #ensure password match
        if request.form.get("password") == request.form.get("confirmation"):
            #hash password and username
            generated_hash = generate_password_hash(request.form.get("password"))
            username = request.form.get("username")
            #add user if user not already in database
            result = db.execute("INSERT INTO users(username,hash) VALUES(?,? )",username, generated_hash)
            if not result:
                  return apology("username exist", 409)
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                            username=request.form.get("username"))

            #log user automatically
            session["user_id"]= rows[0]["id"]
            flash("successfully register")
            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods = ["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        #stocks = db.execute("SELECT symbol,SUM(Number_of_shares) AS Totalshares,price FROM 'transaction' WHERE user_id=:user_id GROUP BY symbol", user_id=session["user_id"])
        row= db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        cashathand = row[0]["cash"]
        symboltosell = lookup(request.form.get("symbol"))
        if not symboltosell:
            return apology("there is no such symbol",403)
        pricetosell = symboltosell["pricetosell"]
        sharetosell = request.form.get("shares")
        if sharetosell <= 0:
            return apology("enter valid shares",403)
        Total_sell = sharetosell*pricetosell
        #sell the shares:
        db.execute("UPDATE user SET cash = :cash+Total_sell WHERE id = :user_id", user_id=session["user_id"])
        db.execute("INSERT INTO transaction(sharetosell, Total_sell)VALUE(:sharetosell, :Total_sell", sharetosell=sharetosell, Total_sell = Total_sell)
        return redirect("/")
    else:
        stocks = db.execute("SELECT symbol, SUM(Number_of_shares) AS Totalshares, price FROM 'transaction' WHERE user_id = :user_id GROUP BY symbol", user_id=session["user_id"])
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
