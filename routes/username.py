import re

from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, getUserRole, login_required, confirmed_required, db, Users


# Set Blueprints
username = Blueprint('username', __name__,)


@username.route("/username", methods=["GET", "POST"])
@login_required
@confirmed_required
def usernameFunction():

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variable
        username = request.form.get("username")
        user_id = session["user_id"]


        # Ensure username was submitted
        if not username:
            flash("Must provide username", "warning")
            return redirect("/username")


        # Ensure username fits server-side
        if not re.search("^[a-zA-Z0-9]{2,20}$", username):
            flash("Invalid username", "danger")
            return redirect("/username")


        # Query database for username if already exists
        query = Users.query.filter_by(username=username).all()
        if len(query) != 0:
            flash("Username already taken", "danger")
            return redirect("/username")


        # Update database with username
        query = Users.query.filter_by(id=user_id).first()
        query.username = username
        db.session.commit()


        # Flash result & redirect
        flash("Username updated", "success")
        return redirect("/")

    
    else:

        return render_template("username.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())