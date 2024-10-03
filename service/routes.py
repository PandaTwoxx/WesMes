"""The app routes"""
from flask import render_template
from flask_socketio import send

from service import app, socketio

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
    return render_template("index.html")
