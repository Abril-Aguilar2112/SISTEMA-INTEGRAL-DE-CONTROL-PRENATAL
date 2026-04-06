
from flask import Flask
from controllers.auth_controller import auth_bp
import os

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    app.register_blueprint(auth_bp)

    return app