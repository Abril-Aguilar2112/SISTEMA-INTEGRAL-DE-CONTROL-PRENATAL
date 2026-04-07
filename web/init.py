
from flask import Flask
from controllers.auth import auth_bp
from controllers.dashboard import dashboard_bp
from controllers.pacientes import pacientes_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(pacientes_bp, url_prefix="/gestion")

    return app
