"""Chatting platform
"""

import secrets
import sys
import time
import logging
import logging.config

from waitress import serve
from service.routes import app


def config():
    """Configures flask app
    """
    logging.config.fileConfig('logger.conf')
    app.config['SECRET_KEY'] = secrets.token_hex()

def run():
    """Runs server initilization
    """
    config()
    logger = logging.getLogger('messanger')
    start = time.time()
    logger.info("App running")
    try:
        serve(app, host='0.0.0.0', port=8080)
    except OSError as e:
        logger.error('OSError, failed to start app: %s', e)
        sys.exit()
    except e:
        logger.error('Error: %s', e)
        sys.exit()


    logger.info("Stopping App...")

    end = time.time()
    delta = end - start

    logger.info("Stopped. Ran for %s seconds", delta)
    logger.info("App Session Ended")
    sys.exit()
