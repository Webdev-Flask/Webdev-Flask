from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, getUserRole, login_required, confirmed_required, db, Users


# Set Blueprints
delete = Blueprint('delete', __name__,)


@delete.route("/delete", methods=["GET", "POST"])
@login_required
@confirmed_required
def emailFunction():

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variable
        user_id = session["user_id"] 


        # Delete row in DB
        Users.query.filter_by(id=user_id).delete()
        db.session.commit()


        # Clear session
        session.clear()


        # Flash result & redirect 
        flash("Account deleted", "warning")
        return redirect("/signin")


    else:

        return render_template("delete.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())