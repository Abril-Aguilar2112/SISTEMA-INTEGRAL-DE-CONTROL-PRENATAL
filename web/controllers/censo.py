from flask import Blueprint, render_template

censo_bp = Blueprint("censo", __name__)

@censo_bp.route("/")
def censo():
    return render_template("direccion/censo.html")
