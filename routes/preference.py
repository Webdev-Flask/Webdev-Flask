from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, getUserRole, login_required, confirmed_required, db, Users


# Set Blueprints
preference = Blueprint('preference', __name__,)


@preference.route("/preference", methods=["GET", "POST"])
@login_required
@confirmed_required
def preferenceFunction():   

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages() 


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variable
        user_id = session["user_id"]


        # Activate newsletter and update DB
        if request.form.get('activate'):

            newsletter = "True"
            query = Users.query.filter_by(id=user_id).first()
            query.newsletter = newsletter
            db.session.commit()


        # Deactivate newsletter and update DB
        if request.form.get('deactivate'):

            newsletter = "False"
            query = Users.query.filter_by(id=user_id).first()
            query.newsletter = newsletter
            db.session.commit()


        # Flash result & redirect    
        flash("Newsletter updated", "success")
        return redirect("/")


    else:
    
        return render_template("preference.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())