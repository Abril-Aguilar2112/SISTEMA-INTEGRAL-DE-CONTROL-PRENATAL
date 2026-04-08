
from flask import Flask
from controllers.auth import auth_bp
from controllers.dashboard import dashboard_bp
from controllers.pacientes import pacientes_bp
from controllers.citas import citas_bp
from controllers.inasistencias import inasistencias_bp
from controllers.censo import censo_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(pacientes_bp, url_prefix="/gestion")
    app.register_blueprint(citas_bp, url_prefix="/gestion")
    app.register_blueprint(inasistencias_bp, url_prefix="/gestion")
    app.register_blueprint(censo_bp, url_prefix="/gestion")

    return app
