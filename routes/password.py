from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from werkzeug.security import check_password_hash, generate_password_hash
from application import getUserName, getUserPicture, getUserRole, login_required, confirmed_required, db, Users


# Set Blueprints
password = Blueprint('password', __name__,)


@password.route("/password", methods=["GET", "POST"])
@login_required
@confirmed_required
def passwordFunction():

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variable
        password = request.form.get("password")
        user_id = session["user_id"]


        # Ensure password was submitted
        if not password:
            flash("Must provide password", "warning")
            return redirect("/password")


        # Query database for hash if already exists
        query = Users.query.filter_by(id=user_id).first()
        if check_password_hash(query.hash, password):
            flash("Password must be new", "danger")
            return redirect("/password")


        # Update database with password hash
        query = Users.query.filter_by(id=user_id).first()
        query.hash = generate_password_hash(password)
        db.session.commit()


        # Flash result & redirect
        flash("Password updated", "success")
        return redirect("/")

    
    else:

        return render_template("password.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())