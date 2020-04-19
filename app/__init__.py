from flask import Flask
from flask_socketio import SocketIO

# socketio = SocketIO(ping_timeout=90, ping_interval=40, engineio_logger=True)
socketio = SocketIO(ping_timeout=90, ping_interval=40)


def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'SUPERSECRETBRAH'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)
    return app