from flask import Blueprint, redirect, session, flash, get_flashed_messages
from application import getUserName, db, Users

# Set Blueprints
logout = Blueprint('logout', __name__,)


@logout.route("/logout")
def logoutFunction():

    # Force flash() to get the messages on the same page as the redirect
    get_flashed_messages()


    # Get username
    username = getUserName()


    # Get username id
    query = Users.query.filter_by(username=username).first()
    user_id = query.id


    # Change user logged status in DB and commit
    query.status = "False"
    db.session.commit()


    # Clear session of user
    session.pop('user_id', None)


    # Flash result & redirect
    flash("User logged out", "warning")
    return redirect("/signin")