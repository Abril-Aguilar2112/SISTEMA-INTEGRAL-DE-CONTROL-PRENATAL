from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from pydantic import ValidationError
from services.paciente_service import get_pacientes
from services.registro_paciente_service import registrar_paciente
from models.paciente import PacienteCreate

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/pacientes', methods=['GET'])
def pacientes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] != 'director_general'	:
        return redirect(url_for('auth.login'))

    page = int(request.args.get('page', 1))
    search = request.args.get('search', '')
    riesgo = request.args.get('riesgo', '')
    semanas = request.args.get('semanas', '')

    result = get_pacientes(
        page=page,
        search=search,
        riesgo=riesgo,
        semanas=semanas
    )

    return render_template('direccion/pacientes/pacientes.html', pacientes=result)

@pacientes_bp.route("/paciente_registro", methods=["GET", "POST"])
def paciente_registro():
    if request.method == "GET":
        return render_template("direccion/pacientes/paciente_registro.html", error=None)
 
    try:
        paciente = PacienteCreate(**request.form)
        print(paciente.to_rpc())
        result   = registrar_paciente(paciente.to_rpc())
        print(result)
 
        if result and result.get("ok"):
            return redirect(url_for("pacientes.pacientes"))
 
        if result.get("error"):
            error = result.get("error", "Error al registrar")
        return render_template("direccion/pacientes/paciente_registro.html", error=error)

    except ValidationError as e:
        print("ERROR:", e)
        flash(str(e), "error")
        return render_template("direccion/pacientes/paciente_registro.html", error=str(e))