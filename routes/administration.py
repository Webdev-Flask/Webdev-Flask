import os

from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, login_required, confirmed_required, getUserRole, role_required, db, Users
from time import time


# Set Blueprints
administration = Blueprint('administration', __name__,)


@administration.route("/administration", methods=["GET", "POST"])
@login_required
@confirmed_required
@role_required
def administrationFunction():    

    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variable
        remove = request.form.get("remove")
        promote = request.form.get("promote")
        demote = request.form.get("demote")


        if request.form.get("remove"):

            # Check if field is not empty
            if remove == "":
                flash("Must provide name REMOVE", "warning")
                return redirect("/administration")


            # Check if it is root
            if remove == os.environ.get("USERNAME"):
                flash("Can't remove this user", "warning")
                return redirect("/administration")


            # Check if the name matches
            if Users.query.filter_by(username=remove).first() == None:
                flash("No matching name", "warning")
                return redirect("/administration")


            # Check if it is the user itself
            if Users.query.filter_by(username=remove).first() == getUserName():
                flash("Can't remove yourself", "warning")
                return redirect("/administration")


            # Check if it is the user is an admin
            query = Users.query.filter_by(username=remove).first()
            if query.role == "admin":
                flash("Can't remove admin", "warning")
                return redirect("/administration")


            # Update database by removing user
            else:
                Users.query.filter(Users.username == remove).delete()
                db.session.commit()
                flash("User deleted", "success")
                return redirect("/administration")



        if request.form.get("promote"):

            # Check if field is not empty
            if promote == "":
                flash("Must provide name", "warning")
                return redirect("/administration")


            # Check if the name matches
            if Users.query.filter_by(username=promote).first() == None:
                flash("No matching name", "warning")
                return redirect("/administration")


            # Check if it is the user is an admin
            query = Users.query.filter_by(username=promote).first()
            if query.role == "admin":
                flash("Already admin", "warning")
                return redirect("/administration")


            # Update database by promoting user
            else:
                query = Users.query.filter_by(username=promote).first()
                query.role = "admin"
                db.session.commit()
                flash("User promoted", "success")
                return redirect("/administration")



        if request.form.get("demote"):

            # Check if field is not empty
            if demote == "":
                flash("Must provide name", "warning")
                return redirect("/administration")


            # Check if it is root
            if demote == os.environ.get("USERNAME"):
                flash("Can't demote this user", "warning")
                return redirect("/administration")


            # Check if the name matches
            if Users.query.filter_by(username=demote).first() == None:
                flash("No matching name", "warning")
                return redirect("/administration")


            # Check if it is the user itself
            if Users.query.filter_by(username=demote).first() == getUserName():
                flash("Can't demote yourself", "warning")
                return redirect("/administration")


            # Update database by demoting user
            else:
                query = Users.query.filter_by(username=demote).first()
                query.role = "user"
                db.session.commit()
                flash("Admin demoted", "success")
                return redirect("/administration")

                
    
    else:

        # Set variable
        user = []
        admin = []
        unconfirmed = []
        logged = []
        index = 0
        now = time()
        

        # Query DB for all users
        query = Users.query.all()


        # Loop through the DB query
        while index < len(query):

            # Users list
            if query[index].role == "user":
                user.extend([[query[index].username, query[index].email, query[index].timeout - now]])


            # Admins list
            if query[index].role == "admin":
                admin.extend([query[index].username])


            # Unconfirmeds list
            if query[index].confirmed == "False":
                unconfirmed.extend([query[index].username])


            # Unconfirmeds list
            if query[index].status == "True":
                logged.extend([query[index].username])
                

            index += 1


        return render_template("administration.html", name=getUserName(), picture=getUserPicture(), role=getUserRole(), user=user, admin=admin, unconfirmed=unconfirmed, logged=logged)