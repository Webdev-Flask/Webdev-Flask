from flask import Blueprint, render_template, redirect, session, request
from application import login_required, confirmed_required, getUserName, getUserPicture, getUserRole


# Set Blueprints
index = Blueprint('index', __name__,)


@index.route("/", methods=["GET", "POST"])
@login_required
@confirmed_required
def indexFunction():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

 
        return redirect("/")


    else:

        return render_template("index.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())