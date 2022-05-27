from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, getUserRole, login_required, confirmed_required, db, Users


# Set Blueprints
chat = Blueprint('chat', __name__,)


@chat.route("/chat", methods=["GET", "POST"])
@login_required
@confirmed_required
def chatFunction():

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        return redirect("/")


    else:

        return render_template("chat.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())