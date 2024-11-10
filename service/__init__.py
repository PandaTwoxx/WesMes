"""Chatting platform
"""

import secrets
import sys
import time
import logging

from service.routes import app, login_manager
from service.classes import LaunchError
from service.common import log_handlers

def config():
    """Configures flask app
    """
    app.config['SECRET_KEY'] = secrets.token_hex()
    app.config['LOGGING_LEVEL'] = logging.INFO
    login_manager.init_app(app)

def run():
    """Runs server initilization
    """
    with app.app_context():
        config()
        start = time.time()
        log_handlers.init_logging(app,'gunicorn.error')
        app.logger.info(70 * "*")
        app.logger.info("  S E R V I C E   R U N N I N G  ".center(70, "*"))
        app.logger.info(70 * "*")
        try:
            app.run(host='0.0.0.0', port=8080)
        except OSError as e:
            app.logger.error('OSError, failed to start app: %s', e)
            sys.exit()
        except LaunchError as e:
            app.logger.error('Error: %s', e)
            sys.exit()


    app.logger.info("Stopping App...")

    end = time.time()
    delta = end - start

    app.logger.info("Stopped. Ran for %s seconds", delta)
    app.logger.info("App Session Ended")
    sys.exit()
