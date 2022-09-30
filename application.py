import os
import random
import string
import requests
import json
import base64

from flask import Flask, session, redirect, render_template, flash, request
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message, Mail
from time import time
from flask_ckeditor import CKEditor
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms


# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Set secret key for site
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") 


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure DB
databaseURI = os.environ.get("DATABASE_URL")
if databaseURI.startswith("postgres://"):
    databaseURI = databaseURI.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = databaseURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# DB Schemas
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    username = db.Column(db.String(1024), nullable=False, unique=True)
    email = db.Column(db.String(1024), nullable=False, unique=True)
    hash = db.Column(db.String(1024), nullable=False, unique=True)
    picture = db.Column(db.String(1024), nullable=False, default="/static/profile.svg")
    role = db.Column(db.String(1024), nullable=False, default="user")
    confirmed = db.Column(db.String(1024), nullable=False, default="False")
    date = db.Column(db.Integer, nullable=False, default=0)
    pin = db.Column(db.Integer, nullable=False, default=0)
    newsletter = db.Column(db.String(1024), nullable=False, default="True")
    status = db.Column(db.String(1024), nullable=False, default="False")
    timeout = db.Column(db.Integer, nullable=False, default=0)
    room = db.Column(db.String(1024), nullable=False, default="[]")

class Chats(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    name = db.Column(db.String(1024), nullable=False)
    userlist = db.Column(db.String(1024), nullable=False, default="[]")  
    text = db.Column(db.Text, nullable=False)


# Create DB
db.create_all()


# Set CKEditor
ckeditor = CKEditor(app)


# Initiate SocketIO
socketio = SocketIO(app)


# Seed DB for admin
query = Users.query.filter_by(username=os.environ.get("USERNAME")).first()
if query is None:
    db.session.add(Users(username=os.environ.get("USERNAME"), email=os.environ.get("EMAIL"), hash=generate_password_hash(os.environ.get("PASSWORD")), role=os.environ.get("ROLE"), confirmed="True", status="True"))
    db.session.commit()


# Email configuration
app.config["DEBUG"] = False
app.config["BCRYPT_LOG_ROUNDS"] = 13
app.config["WTF_CSRF_ENABLED"] = True
app.config["DEBUG_TB_ENABLED"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.environ["APP_MAIL_USERNAME"]
app.config["MAIL_PASSWORD"] = os.environ["APP_MAIL_PASSWORD"]
app.config["MAIL_DEFAULT_SENDER"] = os.environ["APP_MAIL_USERNAME"]


# Configure mail 
mail = Mail(app)


# Ensure responses aren't cached
@app.after_request
def after_request_response(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Reset counter on active users
@app.before_request
def after_before_timeout():
    now = time()

    try: 
        user_id = session["user_id"]

    except KeyError:
        pass

    try: 
        query = Users.query.filter_by(id=user_id).first()
        query.timeout = now
        db.session.commit()
        
    except UnboundLocalError:
        pass


# Log off inactive users
@app.before_request
def before_request_inactive():
    index = 0
    query = Users.query.all()

    try:
        len(query)

    except TypeError:
        pass

    else:

        while index < len(query):

            now = time()
            before = query[index].timeout
            delta = now - before
            user_id = query[index].id

            if delta > 1800 and query[index].status == "True":
                query[index].status = "False"
                db.session.commit()

            index += 1


# Decorator to ensure user must be logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:
            return redirect("/signin")

        else:
            user_id = session["user_id"]
            query = Users.query.filter_by(id=user_id).first()
            
            if query.status == "False":
                return redirect("/signin")

        return f(*args, **kwargs)

    return decorated_function


# Decorator to ensure user is confirmed via email
def confirmed_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Check who's id is logged in
        loggedId = session["user_id"]
        
        # Query database for unconfirmed user
        query = Users.query.filter_by(id=loggedId).first()

        if query.confirmed == "False":

            flash("Please enter the PIN code sent to the given email address", "success")
            return redirect("/unconfirmed")

        return f(*args, **kwargs)

    return decorated_function


# Decorator to ensure user is authorized
def role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if getUserRole() != "admin":

            flash("You are not authorized to access this page", "error")
            return redirect("/")

        return f(*args, **kwargs)

    return decorated_function


# Generate random password
def randomPassword():
    
    result = ""
    while len(result) <= 12:
        character = random.choice(string.ascii_letters)
        result += character
    
    return result


# Check if user is confirmed via email
def getUserConfirmed():

    # Check who's id is logged in
    loggedId = session["user_id"]
        
    # Query database for unconfirmed user
    query = Users.query.filter_by(id=loggedId).first()

    return query.confirmed


# Get username to be displayed 
def getUserName():

    # Check who's id is logged in
    loggedId = session["user_id"]
    
    # Query database for username
    query = Users.query.filter_by(id=loggedId).first()

    return query.username


# Get the user email address
def getUserEmail():

    # Check who's id is logged in
    loggedId = session["user_id"]
    
    # Query database for email
    query = Users.query.filter_by(id=loggedId).first()
        
    return query.email


# Get the user role
def getUserRole():

    # Check who's id is logged in
    loggedId = session["user_id"]
    
    # Query database for role
    query = Users.query.filter_by(id=loggedId).first()
        
    return query.role


# Get the user current PIN
def getUserPin():

    # Check who's id is logged in
    loggedId = session["user_id"]
    
    # Query database for PIN
    query = Users.query.filter_by(id=loggedId).first()
        
    return query.pin


# Get the user registration time
def getUserTime():

    # Check who's id is logged in
    loggedId = session["user_id"]
    
    # Query database for time
    query = Users.query.filter_by(id=loggedId).first()
        
    return query.date


# Get profile picture to be displayed 
def getUserPicture():

    # Check who's id is logged in
    loggedId = session["user_id"]
    
    # Query database for picture
    query = Users.query.filter_by(id=loggedId).first()
        
    return query.picture


# Get user IP
def getUserIp():

    # Get IP from request
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']

    # If behind proxy
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    return ip


# Get user port
def getUserPort():

    # Get port from request
    port = request.environ['REMOTE_PORT']

    return port


# Get user room list
def getUserRoom():

    # Check who's id is logged in
    loggedId = session["user_id"]
        
    # Query database for room list
    query = Users.query.filter_by(id=loggedId).first()

    return query.room


# Get all users list
def getUserRooms():

    # Check who's id is logged in
    loggedId = session["user_id"]
        
    # Query database for all room lists
    query = Users.query.filter(id!=loggedId).all()

    # Set variables
    temporary = []

    # Loop through all DB entries and append to list
    for rooms in query:
        print(rooms.room)
        temporary.append(eval(rooms.room))

    # Return a set of list
    return list(set(temporary))


# Length checker for user input
def getInputLength(input, limit, message, category, route):

    # Check type of
    if type(input) is str:

        # Set limit, flash & redirect
        if len(input) > limit:
            flash(message, category)
            return redirect(route)

    # Check type of
    if type(input) is int:

        # Set limit, flash & redirect
        if len(str(input)) > limit:
            flash(message, category)
            return redirect(route)


# Send PIN code with confirmation email and save it to database
def sendPin(email):

    # Create activation email with a random PIN
    pin = random.randint(100000,999999)
    subject = "Welcome!"
    body = render_template('activate.html', name=getUserName(), pin=pin)
    user_id = session["user_id"]
    date = int(time())

    # Send email with new PIN
    message = Message(subject=subject, recipients=[email], body=body)
    mail.send(message)    

    # Update DB
    query = Users.query.filter_by(id=user_id).first()
    query.date = date
    query.pin = pin
    db.session.commit()


# Send email
def sendMail(subject, email, body):
    messsage = Message(subject=subject, recipients=[email], body=body)
    mail.send(messsage)


# Check if captcha is valided
def is_human(captcha_response):

    secret = os.environ.get("SITE_SECRET_KEY")
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)

    return response_text['success']



# Define allowed extensions
ALLOWED_EXTENSIONS = {'jpg', 'png', 'bmp', 'gif', 'tif', 'webp', 'heic', 'pdf'}


# Define allowed file extensions for upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ImgBB API upload function
def uploadPicture(upload):

    # Contact API
    try:
                    
        with open(upload, "rb") as file:

            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": os.environ.get("IMGBB_API"),
                "image": base64.b64encode(file.read())
            }

            response = requests.post(url, payload)

    except requests.RequestException:

        return None

    # Parse response
    try:

        image = response.json()
        dbReturn =  {
            "picture": image["data"]["url"],
        }
        return dbReturn["picture"]

    except (KeyError, TypeError, ValueError):

        return None


# SocketIO event handler for checking time difference
@socketio.on("time")
def handle_time(data):

    # Convert time from Python to JS
    date = int(time() * 1000.0)

    # Create list with both times
    result = [int(data), date]

    # Emit to client
    emit("time", result, broadcast=False)


# SocketIO event handler for sending message
@socketio.on("chat")
def handle_send_message(data):

    # Get user room list
    data[1] = getUserRoom()

    # Set counter to zero
    index = 0

    # Loop through room list
    while index < len(data[1]):

        # Joining needed room
        join_room(data[1][index])

        # Emit to specific room
        emit("chat", data, to=data[1][index])

        # Increment counter
        index += 1


# SocketIO event handler for creating room
@socketio.on("create")
def handle_create_room(data):

    # Check for empty room name
    if data[0] == "":
        data[0] = "Unnamed"

    # Check who's id is logged in
    loggedId = session["user_id"]
        
    # Query database for chat rooms
    query = Users.query.filter_by(id=loggedId).first()

    # Make user room list
    data[1] = eval(query.room)

    # Make all users room list
    data[2] = getUserRooms()

    print(data[1])
    print(type(data[1]))
    print(data[2])
    print(type(data[1]))


    # Check if room name does not alreay exist
    if data[0] not in data[1] and data[0] not in data[2]:

        # Joining room
        join_room(data[0])

        # Copying list and add notification message to send to the room
        notification = data.copy()
        notification[0] = " has created and joined the " + data[0] + " room."

        # Add new room name to user room list
        data[1].append(data[0])

        # Save room list in database
        query.room = str(data[1])
        db.session.commit()

        # Emit to new room
        emit("notification", notification, to=data[0])

        # Send data to lists of all users 
        emit("create", data, to=data[0])

    # If the room name already exist
    elif data[0] not in data[1] and data[0] in data[2]:

        # Joining room
        join_room(data[0])

        # Copying list and add notification message to send to the room
        notification = data.copy()
        notification[0] = " has joined the existing " + data[0] + " room."

        # Add new room name to user room list
        data[1].append(data[0])

        # Save room list in database
        query.room = str(data[1])
        db.session.commit()

        # Emit to new room
        emit("notification", notification, to=data[0])

        # Send list name to update user list
        emit("join", data, to=data[0])

    # If the room name already exist and the user is in already
    else:

        # Joining room
        join_room(data[0])

        # Copying list and add notification message to send to the room
        notification = data.copy()
        notification[0] = " is already in the " + data[0] + " room."

        # Emit to new room
        emit("notification", notification, to=data[0])


# SocketIO event handler for leaving room
@socketio.on("join")
def handle_join_room(data):

    # Send data to lists of all users 
    emit("join", data, broadcast=True)


# SocketIO event handler for leaving room
@socketio.on("leave")
def handle_leave_room(data):

    # Check who's id is logged in
    loggedId = session["user_id"]
        
    # Query database for chat rooms
    query = Users.query.filter_by(id=loggedId).first()

    # Make user room list
    data[1] = eval(query.room)

    # Make all users room list
    data[2] = getUserRooms()


    # Check if room name exists
    if data[0] in data[1] and data[0] in data[2]:

        # Remove room name from user room list
        data[1].remove(data[0])

        # Remove room in list and commit to DB
        query.room = str(data[1])
        db.session.commit()

        # Copying list and add notification message to send to the room
        notification = data.copy()
        notification[0] = " has left the " + data[0] + " room."

        # Emit to new room
        emit("notification", notification, to=data[0])

        # Send data to lists of all users 
        emit("leave", data, broadcast=True)

    else: 

        # Copying list and add notification message to send to the room
        notification = data.copy()
        notification[0] = " is trying to leave a non existant room."

        # Emit to new room
        emit("notification", notification, broadcast=True)


# Import routes after to avoid circular import
from routes.index import index
from routes.signin import signin
from routes.signup import signup
from routes.logout import logout
from routes.unconfirmed import unconfirmed
from routes.forget import forget
from routes.username import username
from routes.password import password
from routes.email import email
from routes.newsletter import newsletter
from routes.picture import picture
from routes.delete import delete
from routes.administration import administration
from routes.communication import communication
from routes.chat import chat
from routes.server import server
from routes.clock import clock
from routes.calculator import calculator
from routes.sandbox import sandbox


# Configure Blueprints
app.register_blueprint(index)
app.register_blueprint(signin)
app.register_blueprint(signup)
app.register_blueprint(logout)
app.register_blueprint(unconfirmed)
app.register_blueprint(forget)
app.register_blueprint(username)
app.register_blueprint(password)
app.register_blueprint(email)
app.register_blueprint(newsletter)
app.register_blueprint(picture)
app.register_blueprint(delete)
app.register_blueprint(administration)
app.register_blueprint(communication)
app.register_blueprint(chat)
app.register_blueprint(server)
app.register_blueprint(clock)
app.register_blueprint(calculator)
app.register_blueprint(sandbox)