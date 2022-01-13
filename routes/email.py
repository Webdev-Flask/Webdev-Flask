import re

from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, getUserRole, login_required, confirmed_required, db, Users

# Set Blueprints
email = Blueprint('email', __name__,)


@email.route("/email", methods=["GET", "POST"])
@login_required
@confirmed_required
def emailFunction():

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variable
        email = request.form.get("email")
        user_id = session["user_id"]


        # Ensure email was submitted
        if not email:
            flash("Must provide email", "warning")
            return redirect("/email")


        # Ensure email fits server-side
        if not re.search(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email", "danger")
            return redirect("/email")



        # Query database for email if already exists
        query = Users.query.filter_by(email=email).all()
        if len(query) != 0:
            flash("Email already taken", "warning")
            return redirect("/username")


        # Update database with email
        query = Users.query.filter_by(id=user_id).first()
        query.email = email
        db.session.commit()


        # Flash result & redirect
        flash("Email address updated", "success")
        return redirect("/")


    else:

        return render_template("email.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())