from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import db, Users, login_required, sendPin, getUserEmail, getUserTime, getUserPin
from time import time
from flask_sqlalchemy import SQLAlchemy


# Set Blueprints
unconfirmed = Blueprint('unconfirmed', __name__,)


@unconfirmed.route("/unconfirmed", methods=["GET", "POST"])
@login_required
def unconfirmedFunction():


    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # Get variable
    email = getUserEmail()
    now = int(time())
    date = getUserTime()
    pin = getUserPin()
    sample = request.form.get("pin")
    user_id = session["user_id"]


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # User is confirming
        if request.form.get("confirm"):

            # Check if PIN has less than 10min
            if int(sample) == int(pin) and int(now - date) < 600:

                # Update database with confirmation
                query = Users.query.filter_by(id=user_id).first()
                query.confirmed = "True"
                db.session.commit()

                # Change user logged status in DB and commit
                query.status = "True"
                db.session.commit()

                # Flash result & redirect
                flash("You are now confirmed", "success")
                return redirect("/")
                
                
            else:

                # Flash result & redirect
                flash("Wrong PIN entered and/or PIN timed out. (10min)", "danger")
                return redirect("/unconfirmed")


        # User is requesting a new PIN     
        if request.form.get("send"):
            
            # Send new PIN
            sendPin(email)

            # Flash result & redirect
            flash("An new activation PIN has been sent to your email", "success")
            return redirect("/unconfirmed")


    else:

        return render_template("unconfirmed.html")