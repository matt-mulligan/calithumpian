import logging
from app import create_app, socketio

app = create_app()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == '__main__':
    logger.info("Starting Calithumpian socketIO App")
    socketio.run(app, host="0.0.0.0")
    logger.info("App Running")
