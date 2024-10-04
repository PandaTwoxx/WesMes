"""The app routes"""
import logging

from flask import render_template, Flask, request
from flask_socketio import send, SocketIO

# For proxies
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    logging.info('Client %s',request.remote_addr)
    return render_template("index.html")
