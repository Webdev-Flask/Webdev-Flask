from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, getUserRole, getUserRoom, login_required, confirmed_required, db, Users


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

        # Set variables
        index = 0
        roomLists = []
        rooms = []


        # Query DB for all users
        query = Users.query.all()


        # Loop through the DB query
        while index < len(query):

            # Chat room list
            roomLists.extend([(query[index].chat)])
            index += 1


        # Make a unique list 
        for items in roomLists:
            items = eval(items)
            for item in items:
                rooms.append(item)


        return render_template("chat.html", name=getUserName(), picture=getUserPicture(), role=getUserRole(), room=eval(getUserRoom()), rooms=rooms) 