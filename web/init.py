
from flask import Flask
from controllers.auth import auth_bp
from controllers.director_general import director_general_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(director_general_bp, url_prefix="/direccion")
    return app