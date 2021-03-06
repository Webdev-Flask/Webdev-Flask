import html2text
import os

from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages
from application import getUserName, getUserPicture, login_required, confirmed_required, getUserRole, getUserEmail, sendMail, db, Users
from flask_mail import Message
from flask_ckeditor import CKEditor


# Set Blueprints
communication = Blueprint('communication', __name__,)


@communication.route("/communication", methods=["GET", "POST"])
@login_required
@confirmed_required
def communicationFunction():


    # Force flash() to get the messages on the same page as the redirect.
    get_flashed_messages()


    if request.method == "POST":

        # Get variable
        subject = request.form.get("subject")
        html = request.form.get("ckeditor")
        text = html2text.html2text(html)
        address = request.form.get("address")
        newsletter = request.form.get("newsletter")
        loggedId = session["user_id"]


        # Add contact info to text if sent by a user
        query = Users.query.filter_by(id=loggedId).first()
        if query.role == "user":
            text += "\n" + getUserName() + "\n" + getUserEmail()


        # Query database for user emails for newsletter 
        query = Users.query.filter_by(newsletter="True").all()
        if query == None:
            flash("No email in DB", "warning")
            return redirect("/communication")


        # Single email from admin
        if address != "" and newsletter == None and getUserRole() == "admin":

            # Send email (subject, email, body)
            sendMail(subject, address, text)
            flash("Single email sent", "success")

        # Multiple email from admin
        elif address == "" and newsletter == newsletter and getUserRole() == "admin":

            # Loop through email list and send 
            index  = 0
            while index < len(query):
                sendMail(subject, query[index].email, text)
                index += 1
                
            # Send a copy to the admin
            sendMail(subject, os.environ["EMAIL"], text)
            flash("Group email sent", "success")

        # Single email to admin
        elif address != "" and newsletter == None and getUserRole() == "user":
            sendMail(subject, os.environ["EMAIL"], text)
            flash("Message sent", "success")

        else:

            # Flash result & redirect
            flash("Send to one address or select Send Newsletter and leave address blank", "danger")
            return redirect("/communication")


        return redirect("/")

    
    else:

        return render_template("communication.html", name=getUserName(), picture=getUserPicture(), role=getUserRole())