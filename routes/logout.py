from flask import Blueprint, redirect, session, flash, get_flashed_messages


# Set Blueprints
logout = Blueprint('logout', __name__,)


@logout.route("/logout")
def logoutFunction():

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # Clear session
    session.clear()


    # Flash result & redirect
    flash("User logged out", "warning")
    return redirect("/signin")