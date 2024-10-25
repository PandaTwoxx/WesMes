"""The app routes"""
import logging
import json
import redis

from flask import render_template, Flask, request, flash, redirect, url_for
from flask_socketio import send, SocketIO
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
    logout_user,
)

# For proxies
from werkzeug.middleware.proxy_fix import ProxyFix

# User Class
from service.classes import User


# Global/Enivironment variables
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
logger = logging.getLogger('messanger')
login_manager = LoginManager()
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


# For proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@socketio.on("message")
def send_message(message: str) -> None:
    """Broadcasts message to all users

    Args:
        message (str): Message
    Returns:
        None: nothing
    """
    send(message, broadcast=True)
    # send() function will emit a message vent by default


@app.get("/")
def index():
    """The root html response
    """
    logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    return render_template("index.html")


@app.get('/signup')
def signup():
    """The signup page
    """
    logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    next_arg = request.args.get('next')
    return render_template("signup.html", next = next_arg or url_for('home'), back = '/signup')


@app.get('/home')
@login_required
def home():
    """Home page"""
    return render_template('home.html', current_user = current_user)


@app.get('/login_page')
def login_page():
    """Login Page"""
    next_arg = request.args.get('next')
    return render_template('login.html', next = next_arg or url_for('home'), back = '/login_page')


@app.post("/create_user")
def create_user():
    """The create user response
    """
    logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    if 'name' in request.form and 'email' in request.form and\
          'username' in request.form and 'password' in request.form:
        # New User
        new_user = User(
            name = request.form.get('name'),
            email = request.form.get('email'),
            username = request.form.get('username'),
            password = request.form.get('password'),
        )

        # Next redirect
        next_arg = request.form.get('next')

        # Checks if user exists
        if r.hexists('usernames', new_user.username) == 1 or \
        r.hexists('emails', new_user.email) == 1:
            flash('User already exsists', category="error")
            return redirect(url_for('signup')), 302

        # Added user to redis
        r.hset(name='users', key=new_user.get_id(), value=json.dumps(new_user.serialize()))

        r.hset(name='usernames',key=new_user.username, value=new_user.get_id())
        r.hset(name='emails',key=new_user.email, value=new_user.get_id())

        # Logs in user
        login_user(new_user)

        return redirect(next_arg or url_for('index')), 302
    back_ref = request.form.get('back_ref')
    return redirect(back_ref or url_for('signup'))


@app.post('/login')
def login():
    """Logs in user"""
    logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    if 'username' in request.form and 'password' in request.form:

        # User info
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if exsists

        # User id
        user_id = r.hget(name='usernames', key=username)

        # Gets user dict
        user_dict = json.loads(r.hget('users', user_id))


        # Gets user object from dict
        user = User()
        user.deserialize(user_dict)


        # Checks if passwords match
        if not user.check_password(password):
            flash('Username or Password is incorrect.', category='error')
            return redirect('/login_page'), 302



        # Login user
        login_user(user)

        # Sends user to next page
        next_arg = request.form.get('next')
        return redirect(next_arg or url_for('home'))
    if 'email' in request.form and 'password' in request.form:

        # User info
        email = request.form.get('email')
        password = request.form.get('password')

        # User id
        user_id = r.hget(name='emails', key=email)

        # Gets user dict
        user_dict = r.hget('users', user_id)


        # Gets user object from dict
        user = User()
        user.deserialize(user_dict)


        # Checks if passwords match
        if not user.check_password(password):
            flash('Username or Password is incorrect.', category='error')
            return redirect('/login_page'), 302



        # Login user
        login_user(user)

        # Sends user to next page
        next_arg = request.form.get('next')
        return redirect(next_arg or url_for('home'))
    back_ref = request.form.get('back_ref')
    flash('Username or Password is incorrect.', category='error')
    return redirect(back_ref or url_for('login_page'))


@app.get('/logout')
def logout():
    """Logs out user

    Returns:
        Response: 302
    """
    logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    logout_user()
    return redirect(url_for('index')), 302

@login_manager.user_loader
def load_user_from_id(user_id):
    """Loads user from id for login_manager"""

    # List of usernames
    usernames = list(r.smembers(user_id))

    # Empty user object
    user = User()

    for i in usernames:
        user.deserialize(r.hget('users', i))
        if user.get_id() == user_id:
            return user
    return User()
