from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, login_required, confirmed_required, getUserRole, getUserIp, getUserPort
from pythonping import ping


# Set Blueprints
server = Blueprint('server', __name__,)


@server.route("/server", methods=["GET", "POST"])
@login_required
@confirmed_required
def serverFunction():


    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    def test():
        return ping(getUserIp(), verbose=True)

    test()


    if request.method == "POST":


        return redirect("/")

    
    else:

        return render_template("server.html", name=getUserName(), picture=getUserPicture(), role=getUserRole(), userIp=getUserIp(), userPort=getUserPort())