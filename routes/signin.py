import re

from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from application import db, Users
from time import time


# Set Blueprints
signin = Blueprint('signin', __name__,)


@signin.route("/signin", methods=["GET", "POST"])
def signinFunction():


    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        timeout = time()


        # Ensure username was submitted
        if not username:
            flash("must provide username", "warning")
            return redirect("/signin")


        # Ensure username fits server-side
        if not re.search("^[a-zA-Z0-9]{2,20}$", username):
            flash("Invalid username", "danger")
            return redirect("/signin")


        # Ensure password was submitted
        if not password:
            flash("must provide password", "warning")
            return redirect("/signin")


        # Query database for username
        query = Users.query.filter_by(username=username).all()
        if len(query) != 1:
            flash("Invalid username", "danger")
            return redirect("/signin")


        # Ensure username exists and password is correct
        query = Users.query.filter_by(username=username).first()
        if not check_password_hash(query.hash, password):
            flash("Invalid password", "danger")
            return redirect("/signin")


        # Change user logged status in DB and commit
        query.status = "True"
        query.timeout = timeout
        db.session.commit()


        # Remember which user has logged in
        session["user_id"] = query.id


        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signin.html")
