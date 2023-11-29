import os
from flask import Flask, redirect, render_template, session, url_for, request
from flask_login import LoginManager
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_socketio import SocketIO, emit
from celery import Celery
from config import DevelopmentConfig as Config

# Import blueprints
from apps.auth.routes import blueprint as auth_bp
from apps.auth.github_connect import blueprint as ghconnect_bp

# Initialize Celery
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, result_backend=Config.RESULT_BACKEND)
# Initialize the MongoClient
mongo_client = MongoClient(Config.MONGO_URI, server_api=ServerApi('1'))
# Initialize the socket io client
socketio = SocketIO()

def create_app():
    """
    Application Factory Pattern
    """
    app = Flask(__name__)

    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(CONFIG_TYPE)

    # Configure celery
    celery.conf.update(app.config)
    
    login_manager = LoginManager(app)

    # Register blueprints
    register_blueprints(app)

    # Configure logging
    configure_logging(app)

    @app.route('/')
    def index():
        return '<a href="/authorize/github">Login to Delta Functions</a>'
    
    return app

def register_blueprints(app):
    app.register_blueprint(blueprint=auth_bp)
    app.register_blueprint(blueprint=ghconnect_bp)

def configure_logging(app):
    import logging
    from flask.logging import default_handler
    from logging.handlers import RotatingFileHandler

    # Deactivate the default flask logger so that log message don't get duplicated
    app.logger.removeHandler(default_handler)
    # create the logging file handler and set level
    file_handler = RotatingFileHandler('flaskapp.log', maxBytes=16384, backupCount=20)
    file_handler.setLevel(logging.INFO)
    # Create a file formatter
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]')
    file_handler.setFormatter(file_formatter)

    # Add file handler object to the logger
    app.logger.addHandler(file_handler)

def register_error_handlers(app):
    pass


def initialize_extensions(app):
    app.extensions['MONGODB'] = mongo_client.get_database(Config.MONGO_DBNAME)
    socketio.init_app(app)

    # send a ping to confirm successful connection
    try:
        mongo_client.admin.command('ping')
        print("Pinged the MongoDB server")
    except Exception as e:
        print(e)