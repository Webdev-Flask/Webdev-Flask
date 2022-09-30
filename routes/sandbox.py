from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, getUserRole, login_required, confirmed_required, db, Users


# Set Blueprints
sandbox = Blueprint('sandbox', __name__,)


@sandbox.route("/sandbox", methods=["GET", "POST"])
@login_required
@confirmed_required
def sandboxFunction():

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        return redirect("/")

    else:

        return render_template("sandbox.html", name=getUserName(), picture=getUserPicture(), role=getUserRole()) 