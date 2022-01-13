from flask import Blueprint, render_template, redirect, request, flash, get_flashed_messages
from werkzeug.security import generate_password_hash
from application import randomPassword, getUserName, mail, db, Users
from flask_mail import Message


# Set Blueprints
forget = Blueprint('forget', __name__,)


@forget.route("/forget", methods=["GET", "POST"])
def forgetFunction():

    # Force flash() to get the messages on the same page as the redirect.
    flash("Please enter your username, press reset and we will send you a new password", "warning")
    get_flashed_messages()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variable
        username = request.form.get("username")
        password = randomPassword()

        
        # Query database for existing username
        query = Users.query.filter_by(username=username).all()
        if len(query) == 0:
            flash("Username does not exist", "warning")
            return redirect("/forget")


        # Update database with new password
        query = Users.query.filter_by(username=username).first()
        query.hash = generate_password_hash(password)
        db.session.commit()


        # Get the user email address
        query = Users.query.filter_by(username=username).first()
        email = query.email


        # Send new password to user
        subject = "New password!"
        body = render_template('reset.html', name=username, password=password)
        messsage = Message(subject=subject, recipients=[email], body=body)
        mail.send(messsage)    

        
        # Flash result & redirect
        flash("New password sent", "success")
        return redirect("/signin")


    else:

        return render_template("forget.html")





    
    