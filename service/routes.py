"""The app routes"""
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
from service.classes import User, Chat, Message

# Redis object
from service.common.redis_data import r

# Global/Enivironment variables
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()

# Login-Manager init
login_manager.login_view = "login_page"
login_manager.login_message = "You need to login to access this page."
login_manager.login_message_category = "error"
login_manager.refresh_view = "login_page"
login_manager.needs_refresh_message = (
    "To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"
login_manager.session_protection = "strong"


# For proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


def get_user_from_handle(handle: str) -> User:
    """Pulls user with a handle

    Args:
        handle (str): The username

    Returns:
        User: The found user
    """
    user_id = r.hget('usernames', key=handle)
    return User().pull_from_redis(user_id)

def send_message(chat_id: str, content: str, user: str):
    """Sends the message to all the users in the chat"""
    updated_chat = Chat([],"",[])
    updated_chat.pull_from_redis(chat_id)
    updated_chat.messages.append(Message(user,content))

@socketio.on("message")
def share_message(message: str) -> None:
    """Broadcasts message to all users

    Args:
        message (str): Message
    Returns:
        None: nothing
    """
    send(message, broadcast=True)
    # send() function will emit a message vent by default


@app.errorhandler(404)
def not_found(error):
    """The 404 response"""
    app.logger.warning(
        'Client %s connected to %s using method %s but recieved 404 error: %s',
        request.remote_addr,
        request.path,
        request.method,
        str(error)
    )
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(error):
    """The 500 response"""
    app.logger.warning(
        'Client %s connected to %s using method %s but recieved 500 error: %s',
        request.remote_addr,
        request.path,
        request.method,
        str(error)
    )
    return render_template("500.html"),500

@app.get("/")
def index():
    """The root html response
    """
    app.logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    return render_template("index.html", current_user=current_user)


@app.get('/signup')
def signup():
    """The signup page
    """
    app.logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    if current_user.is_authenticated:
        return redirect(url_for('home')),302
    next_arg = request.args.get('next')
    return render_template("signup.html", next = next_arg or url_for('home'),
                           back = '/signup', current_user=current_user)


@app.get('/home')
@login_required
def home():
    """Home page"""
    return render_template('home.html', current_user = current_user)


@app.get('/login_page')
def login_page():
    """Login Page"""
    if current_user.is_authenticated:
        return redirect(url_for('home')),302
    next_arg = request.args.get('next')
    return render_template('login.html', next = next_arg or url_for('home'),
                           back = '/login_page', current_user=current_user)

@login_required
@app.get('/chats')
def chats():
    """Chat page"""
    return render_template('chat.html')


@login_required
@app.get('/new_chat')
def new_chat():
    """Endpoint for creating a new chat"""
    return render_template('new_chat.html')


@app.post('/create_chat')
def create_chat():
    """Creates a new chat
    """
    if 'handle' in request.form:
        handle = request.form['handle']
        user_obj = get_user_from_handle(handle)
        nbew_chat = Chat(
            members=[user_obj,current_user],
            chat_name=current_user.username+" and "+user_obj.username,
            messages=[],
        )
        user_obj.chats.append(nbew_chat.get_id())
        current_user.chats.append(nbew_chat.get_id())

        # Add updated user to the database
        user_obj.push_to_redis()
        current_user.push_to_redis()

        # Add chat to hashmap
        nbew_chat.push_to_redis()
        flash("Chat created", category="success")
        return redirect(url_for('chat', chat=nbew_chat.get_id()))
    flash('Unable to find user', category="error")
    return redirect(url_for('home'))


@app.post("/create_user")
def create_user():
    """The create user response
    """
    app.logger.info(
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
        if r.hexists('usernames', new_user.username) == 1:
            flash('User already exsists', category="error")
            return redirect(url_for('signup')), 302

        # Added user to redis
        new_user.push_to_redis()

        r.hset(name='usernames',key=new_user.username, value=new_user.get_id())

        # Logs in user
        login_user(new_user)

        return redirect(next_arg or url_for('index')), 302
    back_ref = request.form.get('back-ref')
    return redirect(back_ref or url_for('signup'))


@app.post('/login')
def login():
    """Logs in user"""
    app.logger.info(
        'Client %s connected to %s using method %s',
        request.remote_addr,
        request.path,
        request.method
    )
    if 'username' in request.form and 'password' in request.form:

        # User info
        username = request.form.get('username')
        password = request.form.get('password')

        # User id
        user_id = r.hget(name='usernames', key=username)

        # Check if user exsists
        if user_id is None:
            back_ref = request.form.get('back-ref')
            flash('Username or Password is incorrect.', category='error')
            return redirect(back_ref or url_for('login_page'))

        # Gets user object
        user = User()
        user.pull_from_redis(user_id)


        # Checks if passwords match
        if not user.check_password(password):
            flash('Username or Password is incorrect.', category='error')
            return redirect('/login_page'), 302



        # Login user
        login_user(user)

        # Sends user to next page
        next_arg = request.form.get('next')
        return redirect(next_arg or url_for('home'))
    back_ref = request.form.get('back-ref')
    flash('Username or Password is incorrect.', category='error')
    return redirect(back_ref or url_for('login_page'))


@app.get('/logout')
def logout():
    """Logs out user

    Returns:
        Response: 302
    """
    app.logger.info(
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

    # Empty user object
    user = User()

    user.pull_from_redis(user_id)

    return user
