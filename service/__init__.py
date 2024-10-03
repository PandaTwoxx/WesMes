"""Chatting platform
"""

import os
import sys
import time
import uuid
import threading

from flask import Flask
from waitress import serve
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def config():
    """Configures flask app
    """
    app.config['SECRET_KEY'] = os.urandom(24).hex()


def run_thread():
    """Starts thread
    """
    print(f"ID of sub-thread: {os.getpid()}")
    print(f"Sub thread name: {threading.current_thread().name}")
    serve(app, host='0.0.0.0', port=5001, _quiet=True)

def begin_server():
    """Runs server initilization
    """
    print(f"ID of main thread: {os.getpid()}")
    print(f"Main thread name: {threading.current_thread().name}")

    start = time.time()
    print('Creating new task')
    print('Waiting for task to attach')
    t1 = threading.Thread(target=run_thread, name=str(uuid.uuid4()), daemon=True)
    t1.start()

    print("Task running")
    while True:
        if input("Enter \"Stop\" to terminate: ").lower() == "stop":
            break

    print("Stopping server...")
    # No need to join since the thread is a daemon
    print("Task ended")

    end = time.time()
    delta = end - start

    print(f"Thread stopped. Ran for {delta} seconds")
    print("Server Session Ended")
    print('Killing task')
    sys.exit()


def run():
    """Begins the Flask application
    """
    config()
    # Begin the server here
    print('Starting application')
    app.run('0.0.0.0', port=8080)
